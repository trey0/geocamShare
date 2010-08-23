
import re
import sys
import traceback

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect, get_host

class LogErrorsMiddleware(object):
    """Makes exceptions thrown within the django app print debug information
    to stderr so that it shows up in the Apache error log."""
    def process_exception(self, req, exception):
        errClass, errObject, errTB = sys.exc_info()[:3]
        traceback.print_tb(errTB)
        print >>sys.stderr, '%s.%s: %s' % (errClass.__module__,
                                           errClass.__name__,
                                           str(errObject))

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
    SECURITY_REDIRECT_SSL_REQUIRED_BY_DEFAULT = False
    SECURITY_REDIRECT_LOGIN_REQUIRED_BY_DEFAULT = True
    SECURITY_REDIRECT_USE_DIGEST_CHALLENGE_BY_DEFAULT = False
    SECURITY_REDIRECT_TURN_OFF_SSL_WHEN_NOT_REQUIRED = True
    SECURITY_REDIRECT_ACCEPT_DIGEST_AUTH = True

    def __init__(self):
        if self._getSetting('SECURITY_REDIRECT_ACCEPT_DIGEST_AUTH'):
            import django_digest
            self._digestAuthenticator = django_digest.HttpDigestAuthenticator()

    def _digestAuthenticate(self, request):
        if self._getSetting('SECURITY_REDIRECT_ACCEPT_DIGEST_AUTH'):
            return self._digestAuthenticator.authenticate(request)
        else:
            return False

    def _getSetting(self, name):
        if hasattr(settings, name):
            return getattr(settings, name)
        else:
            return getattr(self, name)
    
    def process_view(self, request, viewFunc, viewArgs, viewKwargs):
        sslRequired = viewKwargs.pop('sslRequired', self._getSetting('SECURITY_REDIRECT_SSL_REQUIRED_BY_DEFAULT'))
        loginRequired = viewKwargs.pop('loginRequired', self._getSetting('SECURITY_REDIRECT_LOGIN_REQUIRED_BY_DEFAULT'))
        useDigestChallenge = viewKwargs.pop('useDigestChallenge',
                                            self._getSetting('SECURITY_REDIRECT_USE_DIGEST_CHALLENGE_BY_DEFAULT'))

        # must put this after the pop() calls above, otherwise get errors due to unknown viewKwargs
        if not self._getSetting('SECURITY_REDIRECT_ENABLED'):
            return None

        # todo: optimize to avoid multiple redirects when login requires SSL?

        if (loginRequired and
            not (request.user.is_authenticated()
                 or self._digestAuthenticate(request))):
            if useDigestChallenge:
                return self._digestAuthenticator.build_challenge_response()
            else:
                return login_required(viewFunc)(request, *viewArgs, **viewKwargs)

        isSecure = requestIsSecure(request)
        if sslRequired and not isSecure:
            return self._redirect(request, sslRequired)

        if isSecure and not sslRequired and self._getSetting('SECURITY_REDIRECT_TURN_OFF_SSL_WHEN_NOT_REQUIRED'):
            return self._redirect(request, sslRequired)

        return None

    def _redirect(self, request, secure):
        if settings.DEBUG and request.method == 'POST':
            raise RuntimeError(
                """Django can't perform a SSL redirect while maintaining POST data.
                Please structure your views so that redirects only occur during GETs.""")
        
        protocol = secure and "https" or "http"
        
        newurl = "%s://%s%s" % (protocol, get_host(request), request.get_full_path())
        return HttpResponsePermanentRedirect(newurl)
