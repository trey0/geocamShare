
import sys

from django.http import HttpResponse, HttpResponseNotAllowed
from django.conf import settings
import iso8601
from django.shortcuts import render_to_response
from django.template import RequestContext

from share2.shareTracking.models import Resource, ResourcePosition

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
        featureName = properties['name']
        resource, created = Resource.objects.get_or_create(uuid=featureDict['id'],
                                                           defaults=dict(name=featureName))
        if resource.name != featureName:
            resource.name = featureName
            resource.save()

        # create or update ResourcePosition
        coordinates = featureDict['geometry']['coordinates']
        timestamp = iso8601.parse_date(properties['timestamp']).replace(tzinfo=None)
        attrs = dict(timestamp=timestamp,
                     longitude=coordinates[0],
                     latitude=coordinates[1])
        rp, created = ResourcePosition.objects.get_or_create(resource=resource,
                                                             defaults=attrs)
        if not created:
            for field, val in attrs.iteritems():
                setattr(rp, field, val)
            rp.save()

        return HttpResponse(dumps(dict(result='ok')),
                            mimetype='application/json')

def getLiveMap(request):
    return render_to_response('liveMap.html',
                              dict(),
                              context_instance=RequestContext(request))
