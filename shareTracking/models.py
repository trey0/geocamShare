
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import pytz

class Resource(models.Model):
    name = models.CharField(max_length=32)
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
        return dict(subtype='ResourcePosition',
                    name=self.resource.name,
                    timestamp=localTime.isoformat())

    def getGeoJson(self):
        return dict(type='Feature',
                    id=self.resource.uuid,
                    geometry=self.getGeometry(),
                    properties=self.getProperties())

    def __unicode__(self):
        return ('%s %s %s %s %s'
                % (self.__class__.__name__,
                   self.resource.name,
                   self.timestamp,
                   self.latitude,
                   self.longitude))
