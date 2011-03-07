# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.db import models
from django.contrib.auth.models import User
import pytz

from geocamTrack import settings

class Resource(models.Model):
    name = models.CharField(max_length=32)
    user = models.ForeignKey(User)
    uuid = models.CharField(max_length=128)

    def getUserNameAbbreviated(self):
        if self.user.first_name:
            if not self.user.last_name or self.user.last_name == 'group':
                abbrevName = self.user.first_name
            else:
                abbrevName = '%s. %s' % (self.user.first_name[0], self.user.last_name)
        else:
            abbrevName = self.user.username
        return abbrevName

    def __unicode__(self):
        return '%s %s' % (self.__class__.__name__, self.user.username)

class AbstractResourcePosition(models.Model):
    resource = models.ForeignKey(Resource)
    timestamp = models.DateTimeField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    altitude = models.FloatField(null=True)

    def getGeometry(self):
        return dict(type='Point',
                    coordinates=[self.longitude, self.latitude])

    def getProperties(self):
        timezone = pytz.timezone(settings.TIME_ZONE)
        localTime = timezone.localize(self.timestamp)
        props0 = dict(subtype='ResourcePosition',
                      userName=self.resource.user.username,
                      displayName=self.resource.getUserNameAbbreviated(),
                      timestamp=localTime.isoformat(),
                      unixstamp=localTime.strftime("%s"))
        props = dict(((k, v) for k, v in props0.iteritems()
                      if v not in ('', None)))
        return props

    def getGeoJson(self):
        return dict(type='Feature',
                    id=self.resource.uuid,
                    geometry=self.getGeometry(),
                    properties=self.getProperties())

    def getIconForIndex(self, index):
        if index == None or index >= 26:
            letter = ''
        else:
            letter = chr(65 + index)
        return 'http://maps.google.com/mapfiles/marker%s.png' % letter

    def getKml(self, index=None):
        coords = '%f,%f' % (self.longitude, self.latitude)
        #if self.altitude != None:
        #    coords += ',%f' % self.altitude
        return ('''
<Placemark id="%(id)s">
  <name>%(displayName)s</name>
  <description>%(displayName)s</description>
  <Point>
    <coordinates>%(coords)s</coordinates>
  </Point>
  <Style>
    <IconStyle>
      <Icon>
        <href>%(icon)s</href>
      </Icon>
    </IconStyle>
  </Style>
</Placemark>
'''
                % dict(id='resource-' + self.resource.user.username,
                       displayName=self.resource.getUserNameAbbreviated(),
                       coords=coords,
                       icon=self.getIconForIndex(index)))

    def __unicode__(self):
        return ('%s %s %s %s %s'
                % (self.__class__.__name__,
                   self.resource.user.username,
                   self.timestamp,
                   self.latitude,
                   self.longitude))

    class Meta:
        abstract = True

class ResourcePosition(AbstractResourcePosition):
    pass

class PastResourcePosition(AbstractResourcePosition):
    pass

if settings.GEOCAM_TRACK_LATITUDE_ENABLED:
    # add latitude-related models
    from geocamTrack.latitude.models import *
