
import os
import sys
import glob
import shutil
import datetime
import random
import re
try:
    import json
except ImportError:
    from django.utils import simplejson as json

import PIL.Image
from django.db import models
from django.utils.safestring import mark_safe
from tagging.fields import TagField
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from share2.shareCore.utils import mkdirP, makeUuid
from share2.shareCore.utils.gpx import TrackLog
from share2.shareCore.ExtrasField import ExtrasField
from share2.shareCore.utils.icons import getIconSize

ICON_CHOICES = [(i,i) for i in settings.ICONS]
DEFAULT_ICON = settings.ICONS[0]

LINE_STYLE_CHOICES = [(c,c) for c in settings.LINE_STYLES]
DEFAULT_LINE_STYLE = settings.LINE_STYLES[0]

TIME_ZONES = None
try:
    import pytz
except ImportError:
    TIME_ZONES = ['US/Pacific'] # try to fail gracefully
else:
    TOP_TIME_ZONES = ['US/Pacific', 'US/Eastern', 'US/Central', 'US/Mountain']
    TIME_ZONES = TOP_TIME_ZONES + [tz for tz in pytz.common_timezones if tz not in TOP_TIME_ZONES]
TIME_ZONE_CHOICES = [(x,x) for x in TIME_ZONES]
DEFAULT_TIME_ZONE = TIME_ZONES[0]

PERM_VIEW = 0
PERM_POST = 1
PERM_EDIT = 2
PERM_VALIDATE = 3
PERM_ADMIN = 4

PERMISSION_CHOICES = ((PERM_VIEW, 'view'),
                      (PERM_POST, 'post'),
                      (PERM_VALIDATE, 'validate'),
                      (PERM_ADMIN, 'admin'),
                      )

YAW_REF_CHOICES = (('T', 'true'),
                   ('M', 'magnetic'),
                   )
DEFAULT_YAW_REF = YAW_REF_CHOICES[0][0]

WF_NEEDS_EDITS = 0
WF_SUBMITTED_FOR_VALIDATION = 1
WF_VALID = 2
WF_REJECTED = 3
WORKFLOW_STATUS_CHOICES = ((WF_NEEDS_EDITS, 'Needs edits'),
                           (WF_SUBMITTED_FOR_VALIDATION, 'Submitted for validation'),
                           (WF_VALID, 'Valid'),
                           (WF_REJECTED, 'Rejected'),
                           )
DEFAULT_WORKFLOW_STATUS = WF_SUBMITTED_FOR_VALIDATION

class EmptyTrackError(Exception):
    pass

class Folder(models.Model):
    """Every piece of data in Share belongs to a folder which records both the
    operation the data is associated with and who should be able to access it."""
    name = models.CharField(max_length=32)
    operation = models.ForeignKey("Operation", blank=True, null=True,
                                  related_name='activeOperation',
                                  help_text='Operation that gathered the data in this folder, if applicable.  (Once a folder has an operation and contains data, it should not be switched to a new operation; create a new folder instead.)')
    timeZone = models.CharField(max_length=32,
                                choices=TIME_ZONE_CHOICES,
                                default=DEFAULT_TIME_ZONE,
                                help_text="Time zone used to display timestamps on data in this folder.")
    isArchive = models.BooleanField(default=False,
                                    help_text='If true, disable editing data in this folder.')
    notes = models.TextField(blank=True)
    uuid = models.CharField(max_length=48, default=makeUuid,
                            help_text='Universally unique id used to identify this db record across servers.')
    extras = ExtrasField(help_text="A place to add extra fields if we need them but for some reason can't modify the table schema.  Expressed as a JSON-encoded dict.")

    def __unicode__(self):
        if self.name:
            name = self.name
        else:
            name = '[untitled]'
        return '%s id=%d' % (name, self.id)

class Permission(models.Model):
    folder = models.ForeignKey(Folder, default=1)
    accessType = models.PositiveIntegerField(choices=PERMISSION_CHOICES)

class Unit(models.Model):
    folder = models.ForeignKey(Folder, default=1)
    name = models.CharField(max_length=80)
    permissions = models.ManyToManyField(Permission)

class Operation(models.Model):
    """Represents an area where a team is operating.  Could be a regular
    station posting, an incident, an exercise, or whatever makes sense.
    For a discussion of incident file naming conventions see
    http://gis.nwcg.gov/2008_GISS_Resource/student_workbook/unit_lessons/Unit_08_File_Naming_Review.pdf"""

    folder = models.ForeignKey(Folder, related_name='owningFolder', default=1)
    name = models.CharField(max_length=32, blank=True,
                            help_text="A descriptive name for this operation.  Example: 'beaver_pond'.")
    operationId = models.CharField(max_length=32, blank=True, verbose_name='operation id',
                                   help_text="A formal id for this operation.  For incidents, use the incident number.  Example: 'PA-DEWA-0001'")
    minTime = models.DateTimeField(blank=True, null=True, verbose_name='start date')
    maxTime = models.DateTimeField(blank=True, null=True, verbose_name='end date')
    minLat = models.FloatField(blank=True, null=True, verbose_name='minimum latitude') # WGS84 degrees
    minLon = models.FloatField(blank=True, null=True, verbose_name='minimum longitude') # WGS84 degrees
    maxLat = models.FloatField(blank=True, null=True, verbose_name='maximum latitude') # WGS84 degrees
    maxLon = models.FloatField(blank=True, null=True, verbose_name='maximum longitude') # WGS84 degrees
    notes = models.TextField(blank=True)
    tags = TagField(blank=True)
    contentType = models.ForeignKey(ContentType, editable=False, null=True)
    uuid = models.CharField(max_length=48, default=makeUuid,
                            help_text="Universally unique id used to identify this db record across servers.")
    extras = ExtrasField(help_text="A place to add extra fields if we need them but for some reason can't modify the table schema.  Expressed as a JSON-encoded dict.")

    def asLeafClass(self):
        '''If self is the parent-class portion of a derived class instance, this returns the
        full derived class instance. See http://www.djangosnippets.org/snippets/1031/'''
        leafModel = self.contentType.model_class()
        if leafModel == Feature:
            return self
        else:
            return leafModel.objects.get(id=self.id)

    def __unicode__(self):
        return '%s %s %s' % (self.__class__.__name__, self.name, self.operationId)

class Assignment(models.Model):
    folder = models.ForeignKey(Folder)
    unit = models.ForeignKey(Unit,
                             help_text='The unit you are assigned to.')
    title = models.CharField(max_length=64, blank=True, help_text="Your title within unit.  Example: 'Sit Unit Leader'")
    uuid = models.CharField(max_length=48, default=makeUuid,
                            help_text='Universally unique id used to identify this db record across servers.')

class UserProfile(models.Model):
    """Adds some extended fields to the django built-in User type."""
    user = models.OneToOneField(User, help_text='Reference to corresponding User object of built-in Django authentication system.')
    displayName = models.CharField(max_length=40, blank=True,
                                   help_text="The 'uploaded by' name that will appear next to data you upload.  Defaults to 'F. Last', but if other members of your unit use your account you might want to show your unit name instead.")
    contactInfo = models.CharField(max_length=128, blank=True,
                                   help_text="Your contact info.  If at an incident, we suggest listing cell number and email address.")
    # user's overall folder permissions are the union of userPermissions and
    # the permissions granted to units the user is posted to.  if user has 'admin'
    # privileges to any folder, they can also create new folders.
    userPermissions = models.ManyToManyField(Permission)
    assignments = models.ManyToManyField(Assignment)
    homeOrganization = models.CharField(max_length=64, blank=True, help_text="The organization you normally work for.")
    homeTitle = models.CharField(max_length=64, blank=True, help_text="Your normal job title.")
    uuid = models.CharField(max_length=48, default=makeUuid,
                            help_text='Universally unique id used to identify this user across servers.')
    extras = ExtrasField(help_text="A place to add extra fields if we need them but for some reason can't modify the table schema.  Expressed as a JSON-encoded dict.")

    class Meta:
        ordering = ['user']

    def __unicode__(self):
        return u'<User %s "%s %s">' % (self.user.username, self.user.first_name, self.user.last_name)

class Sensor(models.Model):
    name = models.CharField(max_length=40, blank=True,
                            help_text='Your name for the instrument. Example: "MicroImager" or "GeoCam"')
    make = models.CharField(max_length=40, blank=True,
                            help_text='The organization that makes the sensor.  Example: "Canon"')
    model = models.CharField(max_length=40, blank=True,
                             help_text='The model of sensor.  Example: "Droid" or "PowerShot G9"')
    software = models.CharField(max_length=160, blank=True,
                                help_text='Software running on the sensor, including any known firmware and version details. Example: "GeoCam Mobile 1.0.10, Android firmware 2.1-update1 build ESE81"')
    serialNumber = models.CharField(max_length=80, blank=True,
                                    verbose_name='serial number',
                                    help_text='Information that uniquely identifies this particular sensor unit. Example: "serialNumber:HT851N002808 phoneNumber:4126573579" ')
    notes = models.TextField(blank=True)
    tags = TagField(blank=True)
    uuid = models.CharField(max_length=48, default=makeUuid, blank=True,
                            help_text="Universally unique id used to identify this db record across servers.")
    extras = ExtrasField(help_text="A place to add extra fields if we need them but for some reason can't modify the table schema.  Expressed as a JSON-encoded dict.")

class Feature(models.Model):
    folder = models.ForeignKey(Folder, default=1)
    name = models.CharField(max_length=80, blank=True, default='')
    author = models.ForeignKey(User, null=True, related_name='authoredSet',
                               help_text='The user who collected the data (when you upload data, Share tags you as the author)')
    minTime = models.DateTimeField(blank=True, verbose_name='start time')
    maxTime = models.DateTimeField(blank=True, verbose_name='end time')
    # a word about how we encode geometry:
    # * for a feature with unknown position, we set all lat/lon fields to None.
    # * for a point feature at lat/lon, we set minLat=maxLat=lat, minLon=maxLon=lon.
    # * for a feature with spatial extent, like a GPS track, specify its bounding box
    #   using these lat/lon fields and put any other geometry info in a derived model.
    minLat = models.FloatField(blank=True, null=True, verbose_name='minimum latitude') # WGS84 degrees
    minLon = models.FloatField(blank=True, null=True, verbose_name='minimum longitude') # WGS84 degrees
    maxLat = models.FloatField(blank=True, null=True, verbose_name='maximum latitude') # WGS84 degrees
    maxLon = models.FloatField(blank=True, null=True, verbose_name='maximum longitude') # WGS84 degrees
    sensor = models.ForeignKey(Sensor, blank=True, null=True)
    isAerial = models.BooleanField(default=False, blank=True, verbose_name='aerial data', help_text="True for aerial data. Generally for non-aerial data we snap to terrain in 3D visualizations so that GPS errors can't cause features to be rendered underground.")
    notes = models.TextField(blank=True)
    tags = TagField(blank=True)
    icon = models.CharField(max_length=16, choices=ICON_CHOICES, default=DEFAULT_ICON, blank=True)

    # these fields help us handle changes to data products
    status = models.CharField(max_length=1, choices=settings.STATUS_CHOICES,
                              default=settings.STATUS_CHOICES[0][0])
    processed = models.BooleanField(default=False)
    version = models.PositiveIntegerField(default=0)
    purgeTime = models.DateTimeField(null=True, blank=True)
    workflowStatus = models.PositiveIntegerField(choices=WORKFLOW_STATUS_CHOICES,
                                                 default=DEFAULT_WORKFLOW_STATUS)

    uuid = models.CharField(max_length=48, default=makeUuid, blank=True,
                            help_text="Universally unique id used to identify this db record across servers.")
    contentType = models.ForeignKey(ContentType, editable=False, null=True)
    extras = ExtrasField(help_text="A place to add extra fields if we need them but for some reason can't modify the table schema.  Expressed as a JSON-encoded dict.")

    def save(self, **kwargs):
        if self.minTime == None:
            timestamp = datetime.datetime.now()
            self.minTime = timestamp
            self.maxTime = timestamp
        if self.contentType == None:
            self.contentType = ContentType.objects.get_for_model(self.__class__)
        super(Feature, self).save(**kwargs)

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

    def utcToLocalTime(self, dtUtc0):
        dtUtc = pytz.utc.localize(dtUtc0)
        localTz = pytz.timezone(self.folder.timeZone)
        dtLocal = dtUtc.astimezone(localTz)
        return dtLocal

    def hasPosition(self):
        return self.minLat != None

    def __unicode__(self):
        return '%s %d %s %s %s %s' % (self.contentType.model_class().__name__, self.id, self.name or '[untitled]', self.minTime.strftime('%Y-%m-%d'), self.author.username, self.uuid)

    def getDateText(self):
        return self.utcToLocalTime(self.minTime).strftime('%Y%m%d')

    def getDirSuffix(self, version=None):
        if version == None:
            version = self.version
        return (self.getDateText(), self.author.username, self.uuid, str(version))

    def getDir(self, version=None):
        return os.path.join(settings.DATA_DIR, *self.getDirSuffix(version))

    def getIconDict(self):
        name = self.icon
        return dict(name=name,
                    size=getIconSize(name))

    def getShortDict(self):
        return dict(name=self.name,
                    uuid=self.uuid,
                    version=self.version,
                    minTime=self.utcToLocalTime(self.minTime).isoformat(),
                    maxTime=self.utcToLocalTime(self.maxTime).isoformat(),
                    minLat=self.minLat,
                    minLon=self.minLon,
                    maxLat=self.maxLat,
                    maxLon=self.maxLon,
                    isAerial=self.isAerial,
                    author=self.author.username,
                    notes=self.notes,
                    tags=self.tags,
                    icon=self.getIconDict(),
                    type=self.__class__.__name__
                    )

    def getDirUrl(self):
        return '/'.join([settings.DATA_URL] + list(self.getDirSuffix()))

    class Meta:
        ordering = ('-minTime',)

class Change(models.Model):
    """The concept workflow is like this: there are two roles involved,
    the author (the person who collected the data and who knows it best)
    and validators (who are responsible for signing off on it before it
    is considered 'valid' by the rest of the team).  When the author
    uploads new data, it is marked 'submitted for validation', so it
    appears in the queue of things to be validated.  Any validator
    examining the queue has three choices with each piece of data: she
    can mark it 'valid' (publishing it to the team), 'needs edits'
    (putting it on the author's queue to be fixed), or
    'rejected' (indicating it's not worth fixing, and hiding it to avoid
    confusion).  If the author fixes something on his queue to be fixed,
    he can then submit it to be validated again.  if the author notices
    a problem with the data after it is marked 'valid', he can change
    its status back to 'needs author fixes', edit, and then resubmit.
    Each status change in the workflow is recorded as a Change object."""
    timestamp = models.DateTimeField()
    feature = models.ForeignKey(Feature)
    user = models.ForeignKey(User)
    action = models.CharField(max_length=40, blank=True,
                              help_text='Brief human-readable description like "upload" or "validation check"')
    workflowStatus = models.PositiveIntegerField(choices=WORKFLOW_STATUS_CHOICES,
                                                 default=DEFAULT_WORKFLOW_STATUS)
    uuid = models.CharField(max_length=48, default=makeUuid, blank=True,
                            help_text="Universally unique id used to identify this db record across servers.")

class Placemark(Feature):
    # with point geometry, the bounding box has zero size and the
    # position of the object is equal to its southwest corner.
    def getLat(self):
        return self.minLat
    lat = property(getLat)

    def getLon(self):
        return self.minLon
    lon = property(getLon)
    
    def getTimestamp(self):
        return self.minTime
    timestamp = property(getTimestamp)

    def getLocalTime(self):
        return self.utcToLocalTime(self.minTime)
    localTime = property(getLocalTime)

    def getLocalTimeHumanReadable(self):
        return self.getLocalTime().strftime('%Y-%m-%d %H:%M:%S (%z)')

    def getShortDict(self):
        w, h = self.getThumbSize(settings.GALLERY_THUMB_SIZE[0])
        dct = super(Placemark, self).getShortDict()
        dct.update(lat=self.lat,
                   lon=self.lon,
                   timestamp=self.localTime.isoformat(),
                   dateText=self.localTime.strftime('%Y%m%d'))
        return dct

    def getBalloonHtml(self, request):
        return ''

    def getKml(self, request=None):
        if self.lon == None:
            return ''
        relIconUrl = '%sshare/map/%s.png' % (settings.MEDIA_URL, self.icon)
        iconUrl = request.build_absolute_uri(relIconUrl)
        shortReqId = re.sub('^..._', '', self.requestId)
        return ("""
<Placemark>
  <name>%(shortReqId)s</name>
  <description><![CDATA[%(balloonHtml)s]]></description>
  <Style>
    <IconStyle>
      <Icon>
        <href>%(iconUrl)s</href>
      </Icon>
      <heading>%(yaw)s</heading>
    </IconStyle>
  </Style>
  <Point>
    <coordinates>%(lon)s,%(lat)s</coordinates>
  </Point>
</Placemark>
""" % dict(shortReqId=shortReqId,
           balloonHtml=self.getBalloonHtml(request),
           iconUrl=iconUrl,
           yaw=self.yaw,
           lon=self.lon,
           lat=self.lat))

class Image(Placemark):
    roll = models.FloatField(blank=True, null=True) # degrees, 0 is level, right-hand rotation about x in NED frame
    pitch = models.FloatField(blank=True, null=True) # degrees, 0 is level, right-hand rotation about y in NED frame
    yaw = models.FloatField(blank=True, null=True) # compass degrees, 0 = north, increase clockwise as viewed from above
    yawRef = models.CharField(max_length=1, choices=YAW_REF_CHOICES, default=DEFAULT_YAW_REF)
    widthPixels = models.PositiveIntegerField()
    heightPixels = models.PositiveIntegerField()

    def getThumbnailPath(self, width):
        return os.path.join(self.getDir(), 'th%d.jpg' % width)

    def calcThumbSize(self, fullWidth, fullHeight, maxOutWidth, maxOutHeight=None):
        if maxOutHeight == None:
            maxOutHeight = (maxOutWidth * 3) // 4
        if float(maxOutWidth) / fullWidth < float(maxOutHeight) / fullHeight:
            thumbWidth = maxOutWidth
            thumbHeight = int(float(maxOutWidth)/fullWidth * fullHeight)
        else:
            thumbWidth = int(float(maxOutHeight)/fullHeight * fullWidth)
            thumbHeight = maxOutHeight
        return (thumbWidth, thumbHeight)

    def getThumbSize(self, width):
        return self.calcThumbSize(self.widthPixels, self.heightPixels, width)

    def getImagePath(self, version=None):
        return os.path.join(self.getDir(version), 'full.jpg')

    def getThumbnailUrl(self, width):
        return '%s/th%d.jpg' % (self.getDirUrl(), width)

    def makeThumbnail0(self, previewOriginalPath, thumbSize):
        maxOutWidth, maxOutHeight = thumbSize
        if previewOriginalPath is not None and not os.path.exists(self.getThumbnailPath(maxOutWidth)):
            im = PIL.Image.open(previewOriginalPath)
            fullWidth, fullHeight = im.size
            thumbWidth, thumbHeight = self.calcThumbSize(fullWidth, fullHeight, maxOutWidth, maxOutHeight)
            im.thumbnail((thumbWidth, thumbHeight), PIL.Image.ANTIALIAS)
            mkdirP(self.getDir())
            im.save(self.getThumbnailPath(maxOutWidth))

    def makeThumbnail(self, thumbSize):
        previewOriginalPath = self.getImagePath()
        self.makeThumbnail0(previewOriginalPath, thumbSize)

    def galleryThumb(self):
        w0, h0 = settings.GALLERY_THUMB_SIZE
        w, h = self.getThumbSize(w0)
        return mark_safe('<td style="vertical-align: top; width: %dpx; height: %dpx;"><img src="%s" width="%d" height="%d"/></td>' % (w0, h0, self.getThumbnailUrl(w0), w, h))

    def getIconDict(self):
        ret = super(Image, self).getIconDict()

        if self.yaw == None:
            rot = 0
        else:
            rot = self.yaw
        rotRounded = 10 * int(0.1 * rot + 0.5)
        if rotRounded == 360:
            rotRounded = 0
        name = self.icon
        rotName = '%s%03d' % (name, rotRounded)
        ret.update(dict(rotName=rotName,
                        rotSize=getIconSize(rotName)))
        return ret

    def getShortDict(self):
        w, h = self.getThumbSize(settings.GALLERY_THUMB_SIZE[0])
        dct = super(Image, self).getShortDict()
        dct.update(yaw=self.yaw,
                   w=w,
                   h=h)
        return dct

    def process(self, importFile=None):
        self.status = settings.STATUS_ACTIVE
        self.processed = True
        if importFile and not os.path.exists(self.getImagePath()):
            if not os.path.exists(self.getDir()):
                mkdirP(self.getDir())
            shutil.copy(importFile, self.getImagePath())
        self.makeThumbnail(settings.GALLERY_THUMB_SIZE)
        self.makeThumbnail(settings.DESC_THUMB_SIZE)
        # remember to call save() after process()

    def getBalloonHtml(self, request):
        dw, dh = self.getThumbSize(settings.DESC_THUMB_SIZE[0])
        viewerUrl = request.build_absolute_uri(self.getViewerUrl())
        thumbnailUrl = request.build_absolute_uri(self.getThumbnailUrl(settings.DESC_THUMB_SIZE[0]))
        captionHtml = self.getCaptionHtml()
        return ("""
<div>
  <a href="%(viewerUrl)s"
     title="Show high-res view">
    <img
     src="%(thumbnailUrl)s"
     width="%(dw)f"
     height="%(dh)f"
     border="0"
     />
  </a>
  %(captionHtml)s
</div>
""" % dict(viewerUrl=viewerUrl,
           thumbnailUrl=thumbnailUrl,
           captionHtml=captionHtml,
           dw=dw,
           dh=dh))

    def getKmlAdvanced(self):
        # FIX: fix this up and rename it to getKml()
        return ("""
<PhotoOverlay %(uuid)s>
  <name>%(requestId)s</name>
  <Style>
    <IconStyle><Icon></Icon></IconStyle>
    <BalloonStyle>
      <displayMode>hide</displayMode><!-- suppress confusing description balloon -->
    </BalloonStyle>
  </Style>
  <Camera>
    <longitude></longitude>
    <latitude></latitude>
    <altitude></altitude>
    <heading>{{ self.cameraRotation.yawDegrees }}</heading>
    <tilt>90</tilt>
    <roll>{{ self.cameraRotation.rollDegrees }}</roll>
  </Camera>
  <Icon>
    <href>{{ self.hrefBase }}s/photos/{{ self.rollName }}/{{ self.imageFile }}</href>
  </Icon>
  <Point>
    <coordinates>{{ billboardLonLatAlt.commaString }}</coordinates>
    <altitudeMode>relativeToGround</altitudeMode>
  </Point>
  <ViewVolume>
    <near>{{ settings.STYLE.billboard.photoNear }}</near>
    <leftFov>-{{ halfWidthDegrees }}</leftFov>
    <rightFov>{{ halfWidthDegrees }}</rightFov>
    <bottomFov>-{{ halfHeightDegrees }}</bottomFov>
    <topFov>{{ halfHeightDegrees }}</topFov>
  </ViewVolume>
</PhotoOverlay>
""" % dict())

class Track(Feature):
    lineColor = models.CharField(max_length=10, blank=True,
                                 default='#ff0000ff',
                                 verbose_name='line color',
                                 help_text='A color in HTML #RRGGBBAA hex format, must start with "#" character.')
    lineStyle = models.CharField(max_length=10, blank=True,
                                 choices=LINE_STYLE_CHOICES, default=DEFAULT_LINE_STYLE,
                                 verbose_name='line style',
                                 help_text='Line style for visualization')
    json = models.TextField(help_text='GeoJSON encoding exchanged with browser clients')
    gpx = models.TextField(help_text='If this track was imported as a GPX log, we keep the original GPX here in case there are important fields that are not currently captured in our GeoJSON format.')

    def getShortDict(self):
        dct = super(Track, self).getShortDict()
        dct.update(geometry=json.loads(self.json))
        return dct

    def process(self):
        self.status = settings.STATUS_ACTIVE
        self.processed = True
        data = TrackLog.parseGpxString(self.gpx)
        if not data.getNumPoints():
            raise EmptyTrackError()
        rng = data.getTimeRange()
        self.minTime, self.maxTime = rng.minTime, rng.maxTime
        self.minLon, self.minLat, self.maxLon, self.maxLat = data.getBbox().asList()
        self.json = data.geoJsonString()

class Snapshot(models.Model):
    img = models.ForeignKey(Image)
    xmin = models.FloatField()
    ymin = models.FloatField()
    xmax = models.FloatField()
    ymax = models.FloatField()
    title = models.CharField(max_length=64)
    comment = models.TextField()
    dateCreated = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return self.title

class GoogleEarthSession(models.Model):
    """Session state for a Google Earth client that is requesting periodic updates."""
    sessionId = models.CharField(max_length=256)
    query = models.CharField(max_length=128, default='', help_text="User's query when session was initiated")
    utime = models.DateTimeField(help_text="The last time we sent an update to the client.")
    extras = models.TextField(max_length=1024, default='{}', help_text="A place to add extra fields if we need them but for some reason can't modify the table schema.  Expressed as a JSON-encoded dict.")

    @staticmethod
    def getSessionId(searchQuery=None):
        randomPart = '%08x' % random.getrandbits(32)
        if searchQuery:
            MAX_SEARCH_LEN = 200
            if len(searchQuery) > MAX_SEARCH_LEN:
                raise Exception('due to limitations of current db schema, search queries are limited to %d chars' % MAX_SEARCH_LEN)
            return '%s-%s' % (randomPart, searchQuery)
        else:
            return randomPart
        
    def getSearchQuery(self):
        if '-' in self.sessionId:
            return self.sessionId.split('-', 1)[1]
        else:
            return None

    def __unicode__(self):
        return u'<Session %s (%s)>' % (self.sessionId, self.utime)
    class Meta:
        verbose_name = 'Google Earth session'
        ordering = ['utime']
