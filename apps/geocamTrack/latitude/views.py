# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

import os
import sys
import urllib
import urlparse

import oauth2 as oauth
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

from geocamUtil import anyjson as json
from geocamTrack.latitude.models import LatitudeProfile
from geocamTrack.latitude import LatitudeClient
from geocamTrack.latitude import settings

def getIndex(request):
    return render_to_response('latitudeIndex.html',
                              {},
                              context_instance=RequestContext(request))

REQUEST_TOKEN_URL = 'https://www.google.com/accounts/OAuthGetRequestToken'
REQUEST_TOKEN_PARAMS = dict(scope='https://www.googleapis.com/auth/latitude')
                            

AUTHORIZE_URL = 'https://www.google.com/latitude/apps/OAuthAuthorizeToken'
AUTHORIZE_PARAMS = dict(location='all',
                        granularity='best')

ACCESS_TOKEN_URL = 'https://www.google.com/accounts/OAuthGetAccessToken'

@login_required
def signup(request):
    profile, created = LatitudeProfile.objects.get_or_create(user=request.user)
    next = request.GET.get('next', '%slatitude/' % settings.SCRIPT_NAME)
    request.session['next'] = next
    return render_to_response('latitudeSignup.html',
                              dict(profile=profile),
                              context_instance=RequestContext(request))

def getConsumer():
    return oauth.Consumer(settings.GEOCAM_TRACK_LATITUDE_CONSUMER_KEY, settings.GEOCAM_TRACK_LATITUDE_CONSUMER_SECRET)

@login_required
def signup2(request):
    fullUrl = '%s?%s' % (REQUEST_TOKEN_URL, urllib.urlencode(REQUEST_TOKEN_PARAMS))
    consumer = getConsumer()
    client = oauth.Client(consumer)
    resp, content = client.request(fullUrl, "GET")
    if resp['status'] != '200':
        raise Exception("Couldn't get request token; Latitude server returned HTTP error code %s" % resp['status'])
    requestToken = dict(urlparse.parse_qsl(content))
    if not requestToken:
        print >>sys.stderr, 'content:', content
        raise Exception("Couldn't parse request token returned by Latitude server")
    request.session['requestToken'] = requestToken
    
    params = AUTHORIZE_PARAMS.copy()
    params.update(dict(domain=settings.GEOCAM_TRACK_LATITUDE_CONSUMER_KEY,
                       oauth_callback=request.build_absolute_uri('../signupCallback/'),
                       oauth_token=requestToken['oauth_token']))
    authorizeUrl = '%s?%s' % (AUTHORIZE_URL, urllib.urlencode(params))
    
    return HttpResponseRedirect(authorizeUrl)

@login_required
def signupCallback(request):
    request_token = request.session['requestToken']
    oauth_verifier = request.GET['oauth_token']

    token = oauth.Token(request_token['oauth_token'],
                        request_token['oauth_token_secret'])
    token.set_verifier(oauth_verifier)

    consumer = getConsumer()
    client = oauth.Client(consumer, token)
    resp, content = client.request(ACCESS_TOKEN_URL, "POST")
    if resp['status'] != '200':
        raise Exception("Couldn't get access token; Latitude server returned HTTP error code %s" % resp['status'])
    accessToken = dict(urlparse.parse_qsl(content))
    if not accessToken:
        print >>sys.stderr, 'content:', content
        raise Exception("Couldn't parse access token returned by Latitude server")

    profile, created = LatitudeProfile.objects.get_or_create(user=request.user)
    profile.oauthToken = accessToken['oauth_token']
    profile.oauthSecret = accessToken['oauth_token_secret']
    profile.save()

    return render_to_response('latitudeSignupComplete.html',
                              dict(next=request.session['next']),
                              context_instance=RequestContext(request))


def getLatitudeClient(request):
    profile = None
    try:
        profile = LatitudeProfile.objects.get(user=request.user)
    except ObjectDoesNotExist:
        pass # catch this below
    if not profile or not profile.oauthToken:
        raise Exception("You have not authorized Share to monitor your position in Latitude")

    return LatitudeClient(settings.GEOCAM_TRACK_LATITUDE_CONSUMER_KEY, settings.GEOCAM_TRACK_LATITUDE_CONSUMER_SECRET,
                          profile.oauthToken, profile.oauthSecret)

@login_required
def currentPosition(request):
    c = getLatitudeClient(request)
    try:
        loc = c.getCurrentLocation()
    except LatitudeClient.LatitudeError, e:
        raise Exception("Error trying to get current location from Latitude server: %s" % e)
    return HttpResponse('<pre>%s</pre>' % json.dumps(loc, indent=4))

@login_required
def locationList(request):
    c = getLatitudeClient(request)
    try:
        loc = c.getLocationList()
    except LatitudeClient.LatitudeError, e:
        raise Exception("Error trying to get current location from Latitude server: %s" % e)
    return HttpResponse('<pre>%s</pre>' % json.dumps(loc, indent=4))
