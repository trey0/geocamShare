# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import pytz

class Resource(models.Model):
    name = models.CharField(max_length=32)
    userName = models.CharField(max_length=32)
    displayName = models.CharField(max_length=80)
    uuid = models.CharField(max_length=128)

class ResourcePosition(models.Model):
    resource = models.ForeignKey(Resource)
    timestamp = models.DateTimeField()
    latitude = models.FloatField()
    longitude = models.FloatField()

    def getGeometry(self):
        return dict(type='Point',
                    coordinates=[self.longitude, self.latitude])

    def getProperties(self):
        timezone = pytz.timezone(settings.TIME_ZONE)
        localTime = timezone.localize(self.timestamp)
        props0 = dict(subtype='ResourcePosition',
                      userName=self.resource.userName,
                      displayName=self.resource.displayName,
                      timestamp=localTime.isoformat())
        props = dict(((k, v) for k, v in props0.iteritems()
                      if v not in ('', None)))
        return props

    def getGeoJson(self):
        return dict(type='Feature',
                    id=self.resource.uuid,
                    geometry=self.getGeometry(),
                    properties=self.getProperties())

    def __unicode__(self):
        return ('%s %s %s %s %s'
                % (self.__class__.__name__,
                   self.resource.userName,
                   self.timestamp,
                   self.latitude,
                   self.longitude))
