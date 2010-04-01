import os
import sys
import glob
import shutil

import PIL.Image
from django.db import models
from django.utils.safestring import mark_safe
from tagging.fields import TagField
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from share2.shareCore.utils import mkdirP, makeUuid

class Feature(models.Model):
    name = models.CharField(max_length=80, blank=True, default='')
    owner = models.ForeignKey(User, related_name='owned_set')
    timestamp = models.DateTimeField()
    # a word about how we encode geometry:
    # * for a feature with unknown position, we set all lat/lon fields to None.
    # * for a point feature at lat/lon, we set minLat=maxLat=lat, minLon=maxLon=lon.
    # * for a feature with spatial extent, like a GPS track, specify its bounding box
    #   using these lat/lon fields and put any other geometry info in a derived model.
    minLat = models.FloatField(blank=True, null=True) # WGS84 degrees
    minLon = models.FloatField(blank=True, null=True) # WGS84 degrees
    maxLat = models.FloatField(blank=True, null=True) # WGS84 degrees
    maxLon = models.FloatField(blank=True, null=True) # WGS84 degrees
    notes = models.CharField(max_length=2048)
    tags = TagField()
    uuid = models.CharField(max_length=48, default=makeUuid,
                            help_text="Universally unique id used to identify this db record across servers.")
    contentType = models.ForeignKey(ContentType, editable=False, null=True)

    # these fields help us handle changes to data products
    status = models.CharField(max_length=1, choices=settings.STATUS_CHOICES,
                              default=settings.STATUS_CHOICES[0][0])
    version = models.PositiveIntegerField(default=0)
    purgeTime = models.DateTimeField(null=True, blank=True)

    def save(self, force_insert=False, force_update=False):
        if self.contentType == None:
            self.contentType = ContentType.objects.get_for_model(self.__class__)
        super(Feature, self).save(force_insert, force_update)

    def deleteFiles(self):
        shutil.rmtree(self.getDir(), ignore_errors=True)

    def asLeafClass(self):
        '''If self is the parent-class portion of a derived class instance, this returns the
        full derived class instance. See http://www.djangosnippets.org/snippets/1031/'''
        leafModel = self.contentType.model_class()
        if leafModel == Feature:
            return self
        else:
            return leafModel.objects.get(id=self.id)

    def hasPosition(self):
        return self.minLat != None

    def __unicode__(self):
        return 'Feature %s %s %s %s' % (self.name, self.getDateText(), self.owner.username, self.uuid)

    def getDateText(self):
        return self.timestamp.strftime('%Y%m%d')

    def getDirSuffix(self):
        return (self.getDateText(), self.owner.username, self.uuid, str(self.version))

    def getDir(self):
        return os.path.join(settings.DATA_DIR, *self.getDirSuffix())

    def getShortDict(self):
        return dict(name=self.name,
                    uuid=self.uuid,
                    version=self.version,
                    minLat=self.minLat,
                    minLon=self.minLon,
                    maxLat=self.maxLat,
                    maxLon=self.maxLon,
                    icon=self.getIconPrefix(),
                    timestamp=self.timestamp.strftime('%Y-%m-%d %H:%M'),
                    owner=self.owner.username,
                    dateText=self.getDateText(),
                    notes=self.notes,
                    tags=self.tags,
                    type=self.__class__.__name__
                    )

    def getDirUrl(self):
        return '/'.join(settings.DATA_URL, *self.getDirSuffix())

    def getIconPrefix(self):
        return 'camera'

    class Meta:
        ordering = ('-timestamp',)

class Image(Feature):
    roll = models.FloatField(blank=True, null=True) # degrees, 0 is level, right-hand rotation about x in NED frame
    pitch = models.FloatField(blank=True, null=True) # degrees, 0 is level, right-hand rotation about y in NED frame
    yaw = models.FloatField(blank=True, null=True) # compass degrees, 0 = north, increase clockwise
    widthPixels = models.PositiveIntegerField()
    heightPixels = models.PositiveIntegerField()

    def __unicode__(self):
        return 'Image %s %s %s %s' % (self.name, self.getDateText(), self.owner.username, self.uuid)

    # with point geometry, the position of the object is equal to the southwest
    # corner of the bounding box.
    def getLat(self):
        return self.minLat
    lat = property(getLat)

    def getLon(self):
        return self.minLon
    lon = property(getLon)
    
    def getThumbnailPath(self, width):
        return os.path.join(self.getDir(), 'th%d.jpg' % width)

    def getThumbSize(self, width):
        if os.path.exists(self.getThumbnailPath(width)):
            im = PIL.Image.open(self.getThumbnailPath(width))
            return im.size
        else:
            return (width, width*3/4)

    def getImagePath(self):
        return os.path.join(self.getDir(), 'full.jpg')

    def getThumbnailUrl(self, width):
        return '%s/th%d.jpg' % (self.getDirUrl(), width)

    def makeThumbnail(self, thumbSize):
        previewOriginalPath = self.getImagePath()
        thumbWidth = thumbSize[0]
        if previewOriginalPath is not None and not os.path.exists(self.getThumbnailPath(thumbWidth)):
            im = PIL.Image.open(previewOriginalPath)
            im.thumbnail(thumbSize, PIL.Image.ANTIALIAS)
            mkdirP(self.getDir())
            im.save(self.getThumbnailPath(thumbWidth))

    def galleryThumb(self):
        w0, h0 = settings.GALLERY_THUMB_SIZE
        w, h = self.getThumbSize(w0)
        return mark_safe('<td style="vertical-align: top; width: %dpx; height: %dpx;"><img src="%s" width="%d" height="%d"/></td>' % (w0, h0, self.getThumbnailUrl(w0), w, h))

    def getShortDict(self):
        w, h = self.getThumbSize(settings.GALLERY_THUMB_SIZE[0])
        dct = super(Image, self).getShortDict()
        dct.update(lat=self.lat,
                   lon=self.lon,
                   yaw=self.yaw,
                   w=w,
                   h=h)
        return dct

    def process(self, importFile=None):
        self.status = settings.STATUS_ACTIVE
        if importFile and not os.path.exists(self.getImagePath()):
            if not os.path.exists(self.getDir()):
                mkdirP(self.getDir())
            shutil.copy(importFile, self.getImagePath())
        self.makeThumbnail(settings.GALLERY_THUMB_SIZE)
        self.makeThumbnail(settings.DESC_THUMB_SIZE)
        # remember to call save() after process()

    def getPlacemark(self, request):
        iconUrl = request.build_absolute_uri('%s/share/%s.png' % (settings.MEDIA_URL, self.getIconPrefix()))
        return """
<Placemark>
  <Style>
    <IconStyle>
      <Icon>
        <href>%s</href>
      </Icon>
      <heading>%s</heading>
    </IconStyle>
  </Style>
  <Point>
    <coordinates>%s,%s</coordinates>
  </Point>
</Placemark>
""" % (iconUrl, self.yaw, self.lon, self.lat)
