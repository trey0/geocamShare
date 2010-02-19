import os
import sys
import glob
import shutil

from PIL import Image
from django.db import models
from django.utils.safestring import mark_safe
from tagging.fields import TagField
from django.contrib.auth.models import User
from django.conf import settings

from share2.shareCore.utils import mkdirP, makeUuid

class Feature(models.Model):
    name = models.CharField(max_length=80)
    owner = models.ForeignKey(User)
    timestamp = models.DateTimeField()
    lat = models.FloatField() # WGS84 degrees
    lon = models.FloatField() # WGS84 degrees
    yaw = models.FloatField() # compass degrees, 0 = north, increase clockwise
    notes = models.CharField(max_length=2048)
    tags = TagField()
    uuid = models.CharField(max_length=48, default=makeUuid,
                            help_text="Universally unique id used to identify this db record across servers.")

    # these fields help us handle changes to data products
    status = models.CharField(max_length=1, choices=settings.STATUS_CHOICES,
                              default=settings.STATUS_CHOICES[0][0])
    version = models.PositiveIntegerField(default=0)
    purgeTime = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return 'Feature %s %s %s %s' % (self.name, self.getDateText(), self.owner.username, self.uuid)

    def getDateText(self):
        return self.timestamp.strftime('%Y%m%d')

    def getDirSuffix(self):
        return (self.getDateText(), self.owner.username, self.uuid, str(self.version))

    def getDir(self):
        return os.path.join(settings.DATA_DIR, *self.getDirSuffix())

    def getThumbnailPath(self, width):
        return os.path.join(self.getDir(), 'th%d.jpg' % width)

    def getThumbSize(self, width):
        if os.path.exists(self.getThumbnailPath(width)):
            im = Image.open(self.getThumbnailPath(width))
            return im.size
        else:
            return (width, width*3/4)

    def getShortDict(self):
        w, h = self.getThumbSize(settings.GALLERY_THUMB_SIZE[0])
        return dict(id=self.uuid,
                    version=self.version,
                    lat=self.lat,
                    lon=self.lon,
                    yaw=self.yaw,
                    w = w,
                    h = h,
                    icon = self.getIconPrefix(),
                    timestamp = self.timestamp.strftime('%Y-%m-%d %H:%M'),
                    owner = self.owner.username,
                    dateText = self.getDateText(),
                    )

    def getDirUrl(self):
        return '/'.join(settings.DATA_URL, *self.getDirSuffix())

    def getThumbnailUrl(self, width):
        return '%s/th%d.jpg' % (self.getDirUrl(), width)

    def makeThumbnail(self, thumbSize):
        previewOriginalPath = self.getImagePath()
        thumbWidth = thumbSize[0]
        if previewOriginalPath is not None and not os.path.exists(self.getThumbnailPath(thumbWidth)):
            im = Image.open(previewOriginalPath)
            im.thumbnail(thumbSize, Image.ANTIALIAS)
            mkdirP(self.getDir())
            im.save(self.getThumbnailPath(thumbWidth))

    def galleryThumb(self):
        w0, h0 = settings.GALLERY_THUMB_SIZE
        w, h = self.getThumbSize(w0)
        return mark_safe('<td style="vertical-align: top; width: %dpx; height: %dpx;"><img src="%s" width="%d" height="%d"/></td>' % (w0, h0, self.getThumbnailUrl(w0), w, h))

    def getIconPrefix(self):
        return 'camera'

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

    class Meta:
        ordering = ('-timestamp',)

class Photo(Feature):
    fname = models.CharField(max_length=80)

    def __unicode__(self):
        return 'Photo %s %s %s %s' % (self.name, self.getDateText(), self.owner.username, self.uuid)

    def getImagePath(self):
        return os.path.join(self.getDir(), 'full.jpg')

    def process(self, importFile=None):
        self.status = settings.STATUS_ACTIVE
        if importFile and not os.path.exists(self.getImagePath()):
            if not os.path.exists(self.getDir()):
                mkdirP(self.getDir())
            shutil.copy(importFile, self.getImagePath())
        self.makeThumbnail(settings.GALLERY_THUMB_SIZE)
        self.makeThumbnail(settings.DESC_THUMB_SIZE)
