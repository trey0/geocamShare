# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

import re
import sys
import traceback
import base64

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect, get_host
from django.core.urlresolvers import resolve
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.utils.http import urlquote

def requestIsSecure(request):
    if request.is_secure():
        return True
    
    # Handle forwarded SSL (used at Webfaction)
    if 'HTTP_X_FORWARDED_SSL' in request.META:
        return request.META['HTTP_X_FORWARDED_SSL'] == 'on'

    if 'HTTP_X_SSL_REQUEST' in request.META:
        return request.META['HTTP_X_SSL_REQUEST'] == '1'

    return False

# http://stackoverflow.com/questions/2164069/best-way-to-make-djangos-login-required-the-default
# http://stackoverflow.com/questions/1548210/how-to-force-the-use-of-ssl-for-some-url-of-my-django-application
class SecurityRedirectMiddleware(object):
    # can override these built-in defaults with same-name variables in your Django settings
    SECURITY_REDIRECT_ENABLED = True
    SECURITY_REDIRECT_SSL_REQUIRED_BY_DEFAULT = True
    SECURITY_REDIRECT_TURN_OFF_SSL_WHEN_NOT_REQUIRED = False

    # can specify True, False, or 'write'.  if 'write', login is required to access urls that
    # don't have the 'readOnly' flag.  (but the 'loginRequired' flag always takes precedence.)
    SECURITY_REDIRECT_LOGIN_REQUIRED_BY_DEFAULT = True

    SECURITY_REDIRECT_DEFAULT_CHALLENGE = 'django'
    # 'django' auth type always accepted -- leave it out of the list
    SECURITY_REDIRECT_ACCEPT_AUTH_TYPES = ['digest', 'basic']
    SECURITY_REDIRECT_REQUIRE_SSL_FOR_CREDENTIALS = True

    def __init__(self):
        if 'digest' in self._getSetting('SECURITY_REDIRECT_ACCEPT_AUTH_TYPES'):
            import django_digest
            self._digestAuthenticator = django_digest.HttpDigestAuthenticator()

    def _getSetting(self, name):
        if hasattr(settings, name):
            return getattr(settings, name)
        else:
            return getattr(self, name)

    # http://djangosnippets.org/snippets/243/
    def _basicAuthenticate(self, request):
        # require SSL for basic auth -- avoid clients sending passwords in cleartext
        if not requestIsSecure(request) and self._getSetting('SECURITY_REDIRECT_REQUIRE_SSL_FOR_CREDENTIALS'):
            return False
        
        if 'HTTP_AUTHORIZATION' not in request.META:
            return False

        auth = request.META['HTTP_AUTHORIZATION'].split()
        if len(auth) != 2:
            return False

        if auth[0].lower() != "basic":
            return False

        uname, passwd = base64.b64decode(auth[1]).split(':')
        user = authenticate(username=uname, password=passwd)
        if user == None:
            return False

        if not user.is_active:
            return False

        request.user = user
        return True

    def _basicChallenge(self, request):
        response = HttpResponse()
        response.status_code = 401
        response['WWW-Authenticate'] = 'Basic realm="%s"' % settings.DIGEST_REALM
        return response

    def _djangoAuthenticate(self, request):
        return request.user.is_authenticated()
    
    def _djangoChallenge(self, request):
        loginUrlWithoutScriptName = '/' + settings.LOGIN_URL[len(settings.SCRIPT_NAME):]
        loginTuple = resolve(loginUrlWithoutScriptName)
        loginViewKwargs = loginTuple[2]
        sslRequired = loginViewKwargs.get('sslRequired', self._getSetting('SECURITY_REDIRECT_REQUIRE_SSL_FOR_CREDENTIALS'))
        if sslRequired and not requestIsSecure(request):
            # ssl required for login -- redirect to https and then back
            loginUrl = re.sub('^http:', 'https:', request.build_absolute_uri(settings.LOGIN_URL))
            path = request.get_full_path() + '?protocol=http'
        else:
            # default -- don't bother with protocol and hostname
            loginUrl = settings.LOGIN_URL
            path = request.get_full_path()
        url = '%s?%s=%s' % (loginUrl, REDIRECT_FIELD_NAME, urlquote(path))
        return HttpResponseRedirect(url)

    def _digestAuthenticate(self, request):
        return self._digestAuthenticator.authenticate(request)
    
    def _digestChallenge(self, request):
        return self._digestAuthenticator.build_challenge_response()

    def process_view(self, request, viewFunc, viewArgs, viewKwargs):
        readOnly = viewKwargs.pop('readOnly', False)
        sslRequired = viewKwargs.pop('sslRequired', self._getSetting('SECURITY_REDIRECT_SSL_REQUIRED_BY_DEFAULT'))
        loginRequiredByDefault = self._getSetting('SECURITY_REDIRECT_LOGIN_REQUIRED_BY_DEFAULT')
        if loginRequiredByDefault == 'write':
            loginRequiredByDefault = not readOnly
        loginRequired = viewKwargs.pop('loginRequired', loginRequiredByDefault)
        challenge = viewKwargs.pop('challenge', self._getSetting('SECURITY_REDIRECT_DEFAULT_CHALLENGE'))
        acceptAuthTypes = viewKwargs.pop('acceptAuthTypes', self._getSetting('SECURITY_REDIRECT_ACCEPT_AUTH_TYPES'))

        # must put this after the pop() calls above, otherwise get errors due to unknown viewKwargs
        if not self._getSetting('SECURITY_REDIRECT_ENABLED'):
            return None

        isSecure = requestIsSecure(request)
        if sslRequired and not isSecure:
            return self._redirect(request, sslRequired)

        if isSecure and not sslRequired and self._getSetting('SECURITY_REDIRECT_TURN_OFF_SSL_WHEN_NOT_REQUIRED'):
            return self._redirect(request, sslRequired)

        if loginRequired:
            authenticated = False
            for authType in ['django'] + acceptAuthTypes:
                if getattr(self, '_%sAuthenticate' % authType)(request):
                    authenticated = True
                    #print >>sys.stderr, 'authenticated via %s' % authType
                    break

            if not authenticated:
                return getattr(self, '_%sChallenge' % challenge)(request)

        return None

    def process_response(self, request, response):
        '''Patch the response from contrib.auth.views.login to redirect back to http
        if needed.  Note "?protocol=http" added in _djangoChallenge().'''
        if isinstance(response, HttpResponseRedirect) and request.method == "POST":
            try:
                redirectTo = request.POST.get('next', None)
            except:
                # probably badly formed request content -- log error and don't worry about it
                errClass, errObject, errTB = sys.exc_info()[:3]
                traceback.print_tb(errTB)
                print >>sys.stderr, '%s.%s: %s' % (errClass.__module__,
                                                   errClass.__name__,
                                                   str(errObject))
                return response
            if (redirectTo and redirectTo.endswith('?protocol=http')):
                initUrl = response['Location']
                url = request.build_absolute_uri(initUrl)
                url = re.sub(r'^https:', 'http:', url)
                url = re.sub(r'\?protocol=http$', '', url)
                response['Location'] = url
                print >>sys.stderr, 'process_response: redirectTo=%s initUrl=%s url=%s' % (redirectTo, initUrl, url)
        return response

    def _redirect(self, request, secure):
        if settings.DEBUG and request.method == 'POST':
            raise RuntimeError(
                """Django can't perform a SSL redirect while maintaining POST data.
                Please structure your views so that redirects only occur during GETs.""")
        
        protocol = secure and "https" or "http"
        
        newurl = "%s://%s%s" % (protocol, get_host(request), request.get_full_path())
        return HttpResponsePermanentRedirect(newurl)
