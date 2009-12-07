import os
import sys
import glob

from PIL import Image
from django.db import models
from django.utils.safestring import mark_safe
from tagging.fields import TagField
from django.conf import settings

from share2.share.indexlib import RequestIdPath, Xmp, getMiddleXmpFile, getIdSuffix, mkdirP

class TaskData(models.Model):
    robot = models.CharField(max_length=40, choices=settings.ROBOT_CHOICES)
    date = models.CharField(max_length=40) # date string used in path
    requestId = models.CharField(max_length=40)
    task = models.CharField(max_length=40, choices=settings.TASK_CHOICES)
    params = models.CharField(max_length=40) # params setting as shown in planner UI, e.g. 'narrow hi'
    instrument = models.CharField(max_length=40, choices=settings.INSTRUMENT_CHOICES)
    timestamp = models.DateTimeField()
    lat = models.FloatField() # WGS84 degrees
    lon = models.FloatField() # WGS84 degrees
    yaw = models.FloatField() # compass degrees, 0 = north, increase clockwise
    tags = TagField()

    # these fields help us handle changes to data products
    status = models.CharField(max_length=1, choices=settings.STATUS_CHOICES)
    version = models.PositiveIntegerField()
    purgeTime = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return self.requestId

    def getPreviewOriginalPath(self, reqPath):
        '''can override in derived classes'''
        paths = glob.glob('%s/*eff.jpg' % reqPath.path)
        if paths:
            return paths[0]
        else:
            return None

    def getReqProcessedDir(self):
        return os.path.join(settings.PROCESSED_DIR, self.requestId, str(self.version))

    def getThumbnailPath(self, width):
        return os.path.join(self.getReqProcessedDir(), 'th%d.jpg' % width)

    def getThumbSize(self, width):
        if os.path.exists(self.getThumbnailPath(width)):
            im = Image.open(self.getThumbnailPath(width))
            return im.size
        else:
            return (width, width*3/4)

    def getShortDict(self):
        w, h = self.getThumbSize(settings.GALLERY_THUMB_SIZE[0])
        return dict(requestId=self.requestId,
                    version=self.version,
                    lat=self.lat,
                    lon=self.lon,
                    yaw=self.yaw,
                    w = w,
                    h = h,
                    icon = self.getIconPrefix(),
                    task = self.task,
                    params = self.params,
                    timestamp = self.timestamp.strftime('%Y-%m-%d %H:%M'),
                    )

    def getReqProcessedUrl(self):
        return '/test1/data/%s/%s' % (self.requestId, self.version)

    def getThumbnailUrl(self, width):
        return '%s/th%d.jpg' % (self.getReqProcessedUrl(), width)

    def process0(self, reqPath):
        self.status = 'a'
        self.version = 0
        self.robot = settings.ROBOT_CODES[reqPath.robot]
        self.date = reqPath.date
        self.requestId = reqPath.requestId
        x = Xmp(getMiddleXmpFile(reqPath))
        x.copyToTaskData(self)
        self.makeThumbnail(reqPath, settings.GALLERY_THUMB_SIZE)
        self.makeThumbnail(reqPath, settings.DESC_THUMB_SIZE)

    def makeThumbnail(self, reqPath, thumbSize):
        previewOriginalPath = self.getPreviewOriginalPath(reqPath)
        if previewOriginalPath is not None and not os.path.exists(self.getThumbnailPath(thumbSize[0])):
            im = Image.open(previewOriginalPath)
            im.thumbnail(thumbSize, Image.ANTIALIAS)
            mkdirP(self.getReqProcessedDir())
            im.save(self.getThumbnailPath(thumbSize[0]))

    def galleryThumb(self):
        w0, h0 = settings.GALLERY_THUMB_SIZE
        w, h = self.getThumbSize(w0)
        return mark_safe('<td style="vertical-align: top; width: %dpx; height: %dpx;"><img src="%s" width="%d" height="%d"/></td>' % (w0, h0, self.getThumbnailUrl(w0), w, h))

    def getIconPrefix(self):
        return settings.TASK_ICONS[self.task]

    def getPlacemark(self, request):
        iconUrl = request.build_absolute_uri('/media/test1/%s.png' % self.getIconPrefix())
        return """
<Placemark id="%s">
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
""" % (self.requestId, iconUrl, self.yaw, self.lon, self.lat)

    class Meta:
        ordering = ('-requestId',)

class LidarPano(TaskData):
    def process(self, reqPath):
        print >>sys.stderr, 'lpa %s' % reqPath.requestId
        self.process0(reqPath)
        self.task = settings.TASK_LIDAR_PANO
        self.instrument = settings.INSTR_LDR
        self.params = 'standard'

class LidarScan(TaskData):
    def process(self, reqPath):
        print >>sys.stderr, 'lsc %s' % reqPath.requestId
        self.process0(reqPath)
        self.task = settings.TASK_LIDAR_SCAN
        self.instrument = settings.INSTR_LDR
        self.params = settings.LIDAR_SCAN_PARAMS[getIdSuffix(self.requestId)]

class Mic(TaskData):
    dpname = models.CharField(max_length=40)

    def process(self, reqPath):
        print >>sys.stderr, 'mic %s' % reqPath.requestId
        self.process0(reqPath)
        self.task = settings.TASK_MIC
        self.instrument = settings.INSTR_MIC
        self.params = 'standard'
        self.dpname = os.path.splitext(getMiddleXmpFile(reqPath))[0]

class PancamPano(TaskData):
    def getPreviewOriginalPath(self, reqPath):
        paths = glob.glob('%s/thumbnail_*.jpg' % reqPath.path)
        if paths:
            return paths[0]
        else:
            return None

    def process(self, reqPath):
        print >>sys.stderr, 'pan %s' % reqPath.requestId
        self.process0(reqPath)
        self.task = settings.TASK_PANCAM_PANO
        self.instrument = settings.INSTR_PAN
        self.params = settings.PANCAM_PANO_PARAMS[getIdSuffix(self.requestId)]

ALL_TASK_PAIRS = ((settings.TASK_LIDAR_PANO, LidarPano),
                  (settings.TASK_LIDAR_SCAN, LidarScan),
                  (settings.TASK_MIC, Mic),
                  (settings.TASK_PANCAM_PANO, PancamPano),
                  )
ALL_TASKS_DICT = dict(ALL_TASK_PAIRS)
