# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

import os
import sys
from StringIO import StringIO

from django.http import HttpResponse, HttpResponseNotAllowed
import iso8601
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.models import User

from geocamUtil import anyjson as json
from geocamTrack.models import Resource, ResourcePosition, PastResourcePosition
from geocamTrack.avatar import renderAvatar
from geocamTrack import settings

class ExampleError(Exception):
    pass

def getIndex(request):
    return render_to_response('trackingIndex.html',
                              {},
                              context_instance=RequestContext(request))

def getGeoJsonDict():
    return dict(type='FeatureCollection',
                crs=dict(type='name',
                         properties=dict(name='urn:ogc:def:crs:OGC:1.3:CRS84')),
                features=[r.getGeoJson() for r in ResourcePosition.objects.all()])

def getGeoJsonDictWithErrorHandling():
    try:
        result = getGeoJsonDict()
    except ExampleError:
        return dict(error=dict(code=-32099,
                               message='This is how we would signal an err'))
    return dict(result=result)

def wrapKml(text):
    # xmlns:gx="http://www.google.com/kml/ext/2.2"
    return '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2"
     xmlns:kml="http://www.opengis.net/kml/2.2"
     xmlns:atom="http://www.w3.org/2005/Atom">
%s
</kml>
''' % text

def getKmlResponse(text):
    return HttpResponse(wrapKml(text),
                        mimetype='application/vnd.google-earth.kml+xml')

def getKmlNetworkLink(request):
    url = request.build_absolute_uri(settings.SCRIPT_NAME + 'geocamTrack/latest.kml')
    return getKmlResponse('''
<NetworkLink>
  <name>GeoCam Track</name>
  <Link>
    <href>%(url)s</href>
    <refreshMode>onInterval</refreshMode>
    <refreshInterval>5</refreshInterval>
  </Link>
</NetworkLink>
''' % dict(url=url))

def getKmlLatest(request):
    text = '<Document>\n'
    text += '  <name>GeoCam Track</name>\n'
    positions = ResourcePosition.objects.all().order_by('resource__user__username')
    for i, pos in enumerate(positions):
        text += pos.getKml(i)
    text += '</Document>\n'
    return getKmlResponse(text)

def dumps(obj):
    if settings.DEBUG:
        return json.dumps(obj, indent=4, sort_keys=True) # pretty print
    else:
        return json.dumps(obj, separators=(',',':')) # compact

def getResourcesJson(request):
    return HttpResponse(dumps(getGeoJsonDictWithErrorHandling()),
                        mimetype='application/json')

def postPosition(request):
    if request.method == 'GET':
        return HttpResponseNotAllowed('Please post a resource position as a GeoJSON Feature.')
    else:
        try:
            featureDict = json.loads(request.raw_post_data)
        except ValueError:
            return HttpResponse('Malformed request, expected resources position as a GeoJSON Feature',
                                status=400)

        # create or update Resource
        properties = featureDict['properties']
        featureUserName = properties['userName']
        matchingUsers = User.objects.filter(username=featureUserName)
        if matchingUsers:
            user = matchingUsers[0]
        else:
            user = User.objects.create_user(featureUserName, '%s@example.com' % featureUserName, '12345')
            user.first_name = featureUserName
            user.is_active = False
            user.save()
        resource, created = Resource.objects.get_or_create(uuid=featureDict['id'],
                                                           defaults=dict(user=user))
        if resource.user.username != featureUserName:
            resource.user = user
            resource.save()

        # create or update ResourcePosition
        coordinates = featureDict['geometry']['coordinates']
        timestamp = iso8601.parse_date(properties['timestamp']).replace(tzinfo=None)
        attrs = dict(timestamp=timestamp,
                     longitude=coordinates[0],
                     latitude=coordinates[1])
        if len(coordinates) >= 3:
            attrs['altitude'] = coordinates[2]
        rp, created = ResourcePosition.objects.get_or_create(resource=resource,
                                                             defaults=attrs)
        if not created:
            for field, val in attrs.iteritems():
                setattr(rp, field, val)
            rp.save()

        # add a PastResourcePosition historical entry
        PastResourcePosition(resource=resource, **attrs).save()

        return HttpResponse(dumps(dict(result='ok')),
                            mimetype='application/json')

def getLiveMap(request):
    userData = { 'loggedIn': False }
    if request.user.is_authenticated():
        userData['loggedIn'] = True
        userData['userName'] = request.user.username

    return render_to_response('liveMap.html',
                              { 'userData': dumps(userData) },
                              context_instance=RequestContext(request))

def getIcon(request, userName):
    return HttpResponse(renderAvatar(request, userName),
                        mimetype='image/png')
