# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

import sys

from django.http import HttpResponse, HttpResponseNotAllowed
from django.conf import settings
import iso8601
from django.shortcuts import render_to_response
from django.template import RequestContext

from share2.shareTracking.models import Resource, ResourcePosition, PastResourcePosition

try:
    import json
except ImportError:
    from django.utils import simplejson as json

class ExampleError(Exception):
    pass

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
        resource, created = Resource.objects.get_or_create(uuid=featureDict['id'],
                                                           defaults=dict(userName=featureUserName))
        if resource.userName != featureUserName:
            resource.userName = featureUserName
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
    return render_to_response('liveMap.html',
                              dict(),
                              context_instance=RequestContext(request))

from StringIO import StringIO
import Image, ImageDraw, ImageFont

import os
import os.path as op

AVATAR_DIR = 'shareTracking/media/avatars'
PLACARD_FRESH = 'shareTracking/media/mapIcons/placard.png'

def getIcon(request, userName):
    placard = Image.open(PLACARD_FRESH)

    avatar = None
    avatar_file = op.join(AVATAR_DIR, "%s.png" % userName)
    if op.exists(avatar_file):
        avatar = Image.open(avatar_file)
    else:
        avatar = Image.new("RGB", (8, 8), "#FFFFFF")
        font = ImageFont.load_default()
        draw  = ImageDraw.Draw(avatar)
        draw.text((1, -2), userName.upper()[0], font=font, fill=0)
        del draw

    avatar = avatar.resize((36,36))
    placard.paste(avatar, (10, 8))

    if ("scale" in request.REQUEST):
        scale = float(request.REQUEST['scale'])
        new_size = (int(placard.size[0] * scale),
                    int(placard.size[1] * scale))
        placard = placard.resize(new_size)

    strio = StringIO()
    placard.save(strio, "PNG")
    return HttpResponse(strio.getvalue(),
                        mimetype='image/png')
