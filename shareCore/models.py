# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

import os
import sys
import glob
import shutil
import datetime
import random
import re

import pytz
import PIL.Image
from django.db import models
from django.utils.safestring import mark_safe
from tagging.fields import TagField
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.contrib.contenttypes import generic
import tagging

from share2.shareCore.utils import anyjson as json
from share2.shareCore.utils import mkdirP, makeUuid, Xmp
from share2.shareCore.utils.gpx import TrackLog
from share2.shareCore.ExtrasField import ExtrasField
from share2.shareCore.icons import getIconSize
from share2.shareCore.TimeUtils import parseUploadTime
from share2.shareCore.managers import AbstractClassManager, LeafClassManager

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

YAW_REF_CHOICES = (('', 'unknown'),
                   ('T', 'true'),
                   ('M', 'magnetic'),
                   )
YAW_REF_LOOKUP = dict(YAW_REF_CHOICES)
YAW_REF_LOOKUP[''] = None
DEFAULT_YAW_REF = YAW_REF_CHOICES[0][0]

ALTITUDE_REF_CHOICES = (('', 'unknown'),
                        ('S', 'sea level'),
                        ('E', 'ellipsoid wgs84'),
                        ('G', 'ground surface'),
                        )
ALTITUDE_REF_LOOKUP = dict(ALTITUDE_REF_CHOICES)
ALTITUDE_REF_LOOKUP[''] = None
DEFAULT_ALTITUDE_REF = ALTITUDE_REF_CHOICES[0][0]

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

class AbstractOperation(models.Model):
    """Represents an area where a team is operating.  Could be a regular
    station posting, an incident, an exercise, or whatever makes sense.
    For a discussion of incident file naming conventions see
    http://gis.nwcg.gov/2008_GISS_Resource/student_workbook/unit_lessons/Unit_08_File_Naming_Review.pdf"""

    folder = models.ForeignKey(Folder, related_name='%(app_label)s_%(class)s_owningFolder', default=1)
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
    objects = AbstractClassManager(parentModel=None)

    class Meta:
        abstract = True

    def __unicode__(self):
        return '%s %s %s' % (self.__class__.__name__, self.name, self.operationId)

class Operation(AbstractOperation):
    objects = LeafClassManager(parentModel=AbstractOperation)

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
    author = models.ForeignKey(User, null=True, related_name='%(app_label)s_%(class)s_authoredSet',
                               help_text='The user who collected the data (when you upload data, Share tags you as the author)')
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
    mtime = models.DateTimeField(null=True, blank=True)

    uuid = models.CharField(max_length=48, default=makeUuid, blank=True,
                            help_text="Universally unique id used to identify this db record across servers.")
    extras = ExtrasField(help_text="A place to add extra fields if we need them but for some reason can't modify the table schema.  Expressed as a JSON-encoded dict.")

    objects = AbstractClassManager(parentModel=None)

    class Meta:
        abstract = True

    def save(self, **kwargs):
        self.mtime = datetime.datetime.now()
        super(Feature, self).save(**kwargs)

    def deleteFiles(self):
        shutil.rmtree(self.getDir(), ignore_errors=True)

    def getCachedField(self, field):
        relatedId = getattr(self, '%s_id' % field)
        key = 'fieldCache-shareCore-Feature-%s-%d' % (field, relatedId)
        result = cache.get(key)
        if not result:
            result = getattr(self, field)
            cache.set(key, result)
        return result

    def getCachedFolder(self):
        return self.getCachedField('folder')

    def getCachedAuthor(self):
        return self.getCachedField('author')

    def utcToLocalTime(self, dtUtc0):
        dtUtc = pytz.utc.localize(dtUtc0)
        localTz = pytz.timezone(self.getCachedFolder().timeZone)
        dtLocal = dtUtc.astimezone(localTz)
        return dtLocal

    def hasPosition(self):
        return self.minLat != None

    def getAuthor(self):
        pass

    def __unicode__(self):
        return '%s %d %s %s %s %s' % (self.__class__.__name__, self.id, self.name or '[untitled]', self.timestamp.strftime('%Y-%m-%d'), self.author.username, self.uuid)

    def getDateText(self):
        return self.utcToLocalTime(self.timestamp).strftime('%Y%m%d')

    def getDirSuffix(self, version=None):
        if version == None:
            version = self.version
        idStr = str(self.id) + 'p'
        idList = [idStr[i:(i+2)] for i in xrange(0, len(idStr), 2)]
        return [self.__class__.__name__.lower()] + idList + [str(version)]

    def getDir(self, version=None):
        return os.path.join(settings.DATA_DIR, *self.getDirSuffix(version))

    def getIconDict(self):
        name = self.icon
        return dict(name=name,
                    size=getIconSize(name))

    def getUserDisplayName(self, user):
        if user.last_name == 'group':
            return user.first_name
        else:
            return '%s %s' % (user.first_name.capitalize(),
                              user.last_name.capitalize())
            return result

    def getProperties(self):
        tagsList = tagging.utils.parse_tag_input(self.tags)
        author = self.getCachedAuthor()
        authorDict = dict(userName=author.username,
                          displayName=self.getUserDisplayName(author))
        return dict(name=self.name,
                    version=self.version,
                    isAerial=self.isAerial,
                    author=authorDict,
                    notes=self.notes,
                    tags=tagsList,
                    icon=self.getIconDict(),
                    localId=self.id,
                    subtype=self.__class__.__name__
                    )

    def cleanDict(self, d):
        return dict(((k, v)
                     for k, v in d.iteritems()
                     if v not in (None, '')))

    def getGeoJson(self):
        return dict(type='Feature',
                    id=self.uuid,
                    geometry=self.getGeometry(),
                    properties=self.cleanDict(self.getProperties()))

    def getDirUrl(self):
        return '/'.join([settings.DATA_URL] + list(self.getDirSuffix()))

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
    featureUuid = models.CharField(max_length=48)
    user = models.ForeignKey(User)
    action = models.CharField(max_length=40, blank=True,
                              help_text='Brief human-readable description like "upload" or "validation check"')
    workflowStatus = models.PositiveIntegerField(choices=WORKFLOW_STATUS_CHOICES,
                                                 default=DEFAULT_WORKFLOW_STATUS)
    uuid = models.CharField(max_length=48, default=makeUuid, blank=True,
                            help_text="Universally unique id used to identify this db record across servers.")

class PointFeature(Feature):
    latitude = models.FloatField(blank=True, null=True) # WGS84 degrees
    longitude = models.FloatField(blank=True, null=True) # WGS84 degrees
    altitude = models.FloatField(blank=True, null=True)
    altitudeRef = models.CharField(blank=True, max_length=1,
                                   choices=ALTITUDE_REF_CHOICES, default=DEFAULT_ALTITUDE_REF,
                                   verbose_name='Altitude ref.')
    timestamp = models.DateTimeField(blank=True)
    objects = AbstractClassManager(parentModel=Feature)
    
    class Meta:
        abstract = True
        ordering = ['-timestamp']

    def save(self, **kwargs):
        if self.timestamp == None:
            self.timestamp = datetime.datetime.now()
        super(PointFeature, self).save(**kwargs)

    def getLocalTime(self):
        return self.utcToLocalTime(self.timestamp)
    localTime = property(getLocalTime)

    def getLocalTimeHumanReadable(self):
        return self.getLocalTime().strftime('%Y-%m-%d %H:%M:%S (%z)')

    def getBalloonHtml(self, request):
        return ''

    def getKml(self, request=None):
        if self.longitude == None:
            return ''
        if self.yaw == None:
            headingStr = ''
        else:
            headingStr = '<heading>%s</heading>' % self.yaw
        relIconUrl = '%sshare/map/%sPoint.png' % (settings.MEDIA_URL, self.icon)
        iconUrl = request.build_absolute_uri(relIconUrl)
        return ("""
<Placemark>
  <name>%(name)s</name>
  <description><![CDATA[%(balloonHtml)s]]></description>
  <Style>
    <IconStyle>
      <Icon>
        <href>%(iconUrl)s</href>
      </Icon>
      %(headingStr)s
    </IconStyle>
  </Style>
  <Point>
    <coordinates>%(lon)s,%(lat)s</coordinates>
  </Point>
</Placemark>
""" % dict(name=self.name,
           balloonHtml=self.getBalloonHtml(request),
           iconUrl=iconUrl,
           headingStr=headingStr,
           lon=self.longitude,
           lat=self.latitude))
    
    def getProperties(self):
        result = super(PointFeature, self).getProperties()
        result.update(timestamp=self.localTime.isoformat(),
                      dateText=self.localTime.strftime('%Y%m%d'),
                      altitude=self.altitude,
                      altitudeRef=ALTITUDE_REF_LOOKUP[self.altitudeRef])
        return result

    def getGeometry(self):
        return dict(type='Point',
                    coordinates=[self.longitude, self.latitude])

class Snapshot(models.Model):
    imgType = models.ForeignKey(ContentType, editable=False)
    imgId = models.PositiveIntegerField()
    xmin = models.FloatField()
    ymin = models.FloatField()
    xmax = models.FloatField()
    ymax = models.FloatField()
    title = models.CharField(max_length=64)
    comment = models.TextField()
    dateCreated = models.DateTimeField(null=True, blank=True)

    # img is a virtual field, not actually present in the db.  it
    # specifies which image this snapshot is associated with based on
    # imgType (which db table to look in) and imgId (which row in the
    # table).
    img = generic.GenericForeignKey('imgType', 'imgId')

    def __unicode__(self):
        return self.title

class Image(PointFeature):
    roll = models.FloatField(blank=True, null=True) # degrees, 0 is level, right-hand rotation about x in NED frame
    pitch = models.FloatField(blank=True, null=True) # degrees, 0 is level, right-hand rotation about y in NED frame
    # compass degrees, 0 = north, increase clockwise as viewed from above
    yaw = models.FloatField(blank=True, null=True,
                            verbose_name='Heading')
    yawRef = models.CharField(blank=True, max_length=1, choices=YAW_REF_CHOICES, default=DEFAULT_YAW_REF,
                              verbose_name='Heading ref.')
    widthPixels = models.PositiveIntegerField()
    heightPixels = models.PositiveIntegerField()
    objects = AbstractClassManager(parentModel=PointFeature)

    # snapshot_set is a virtual field, not actually present in the db,
    # which specifies how to look up the snapshots associated with this
    # image.
    snapshot_set = generic.GenericRelation(Snapshot,
                                           content_type_field='imgType',
                                           object_id_field='imgId')

    class Meta:
        abstract = True

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

    def getRotatedIconDict(self):
        if self.yaw == None:
            rot = 0
        else:
            rot = self.yaw
        rotRounded = 10 * int(0.1 * rot + 0.5)
        if rotRounded == 360:
            rotRounded = 0
        name = self.icon
        rotName = '%s%03d' % (name, rotRounded)
        return dict(name=rotName,
                    size=getIconSize(rotName))

    def process(self, importFile=None):
        self.status = settings.STATUS_ACTIVE
        self.processed = True
        if importFile and not os.path.exists(self.getImagePath()):
            if not os.path.exists(self.getDir()):
                mkdirP(self.getDir())
            shutil.copyfile(importFile, self.getImagePath())
        self.makeThumbnail(settings.GALLERY_THUMB_SIZE)
        self.makeThumbnail(settings.DESC_THUMB_SIZE)
        # remember to call save() after process()

    def getViewerUrl(self):
        return '%sview/%s/' % (settings.SCRIPT_NAME, self.uuid)

    def getCaptionHtml(self):
        return ''

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

    def getXmpVals(self, storePath):
        xmp = Xmp(storePath)
        xmpVals = xmp.getDict()
        return xmpVals

    def getUploadImageFormVals(self, formData):
        yaw, yawRef = Xmp.normalizeYaw(formData.get('yaw', None),
                                       formData.get('yawRef', None))
        altitude, altitudeRef = Xmp.normalizeYaw(formData.get('altitude', None),
                                                 formData.get('altitudeRef', None))

        folderName = formData.get('folder', None)
        folder = None
        if folderName:
            folderMatches = Folder.objects.filter(name=folderName)
            if folderMatches:
                folder = folderMatches[0]
        if folder == None:
            folder = Folder.objects.get(id=1)

        tz = pytz.timezone(folder.timeZone)
        timestampStr = Xmp.checkMissing(formData.get('cameraTime', None))
        if timestampStr == None:
            timestampUtc = None
        else:
            timestampLocal = parseUploadTime(timestampStr)
            if timestampLocal.tzinfo == None:
                timestampLocal = tz.localize(timestampLocal)
            timestampUtc = timestampLocal.astimezone(pytz.utc).replace(tzinfo=None)

        # special case: remove 'default' tag inserted by older versions of GeoCam Mobile
        tagsOrig = formData.get('tags', None)
        tagsList = [t for t in tagging.utils.parse_tag_input(tagsOrig)
                    if t != 'default']
        tagsStr = self.makeTagsString(tagsList)

        formVals0 = dict(uuid=formData.get('uuid', None),
                         name=formData.get('name', None),
                         author=formData.get('author', None),
                         notes=formData.get('notes', None),
                         tags=tagsStr,
                         latitude=formData.get('latitude', None),
                         longitude=formData.get('longitude', None),
                         altitude=formData.get('altitude', None),
                         altitudeRef=formData.get('altitudeRef', None),
                         timestamp=timestampUtc,
                         folder=folder,
                         yaw=yaw,
                         yawRef=yawRef)
        formVals = dict([(k, v) for k, v in formVals0.iteritems()
                         if Xmp.checkMissing(v) != None])
        return formVals

    @staticmethod
    def makeTagsString(tagsList):
        tagsList = list(set(tagsList))
        tagsList.sort()
        
        # modeled on tagging.utils.edit_string_for_tags
        names = []
        useCommas = False
        for tag in tagsList:
            if ' ' in tag:
                names.append('"%s"' % tag)
            else:
                names.append(tag)
            if ',' in tag:
                useCommas = True
        if useCommas:
            return ', '.join(names)
        else:
            return ' '.join(names)

    def processVals(self, vals):
        if vals.has_key('tags'):
            tagsList = tagging.utils.parse_tag_input(vals['tags'])
        else:
            tagsList = []

        # find any '#foo' hashtags in notes and add them to the tags field
        if vals.has_key('notes'):
            for hashtag in re.finditer('\#([\w0-9_]+)', vals['notes']):
                tagsList.append(hashtag.group(1))
            vals['tags'] = self.makeTagsString(tagsList)

        # if one of the tags is the name of an icon, use that icon
        for t in tagsList:
            if t in settings.ICONS_DICT:
                vals['icon'] = t
                break

    def getImportVals(self, storePath=None, uploadImageFormData=None):
        vals = {}

        if storePath != None:
            xmpVals = self.getXmpVals(storePath)
            print >>sys.stderr, 'getImportVals: exif/xmp data:', xmpVals
            vals.update(xmpVals)

        if uploadImageFormData != None:
            formVals = self.getUploadImageFormVals(uploadImageFormData)
            print >>sys.stderr, 'getImportVals: UploadImageForm data:', formVals
            vals.update(formVals)

        self.processVals(vals)

        return vals

    def readImportVals(self, *args, **kwargs):
        vals = self.getImportVals(*args, **kwargs)
        for k, v in vals.iteritems():
            setattr(self, k, v)

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

    def getProperties(self):
        result = super(Image, self).getProperties()
        result.update(sizePixels=[self.widthPixels, self.heightPixels],
                      rotatedIcon=self.getRotatedIconDict(),
                      roll=self.roll,
                      pitch=self.pitch,
                      yaw=self.yaw,
                      yawRef=YAW_REF_LOOKUP[self.yawRef])
        return result

class ExtentFeature(Feature):
    minTime = models.DateTimeField(blank=True, verbose_name='start time')
    maxTime = models.DateTimeField(blank=True, verbose_name='end time')
    minLat = models.FloatField(blank=True, null=True, verbose_name='minimum latitude') # WGS84 degrees
    minLon = models.FloatField(blank=True, null=True, verbose_name='minimum longitude') # WGS84 degrees
    maxLat = models.FloatField(blank=True, null=True, verbose_name='maximum latitude') # WGS84 degrees
    maxLon = models.FloatField(blank=True, null=True, verbose_name='maximum longitude') # WGS84 degrees
    objects = AbstractClassManager(parentModel=Feature)

    def save(self, **kwargs):
        if self.minTime == None:
            timestamp = datetime.datetime.now()
            self.minTime = timestamp
            self.maxTime = timestamp
        super(ExtentFeature, self).save(**kwargs)

    def getTimestamp(self):
        return self.maxTime
    timestamp = property(getTimestamp)

    def getProperties(self):
        result = super(ExtentFeature, self).getProperties()
        result.update(minTime=self.utcToLocalTime(self.minTime).isoformat(),
                      maxTime=self.utcToLocalTime(self.maxTime).isoformat())
        return result

    class Meta:
        abstract = True
        ordering = ['-maxTime']

class Track(ExtentFeature):
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
    objects = LeafClassManager(parentModel=ExtentFeature)

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

    def getGeometry(self):
        return json.loads(self.json)

    def getGeoJson(self):
        result = super(Track, self).getGeoJson()
        result['bbox'] = [self.minLon, self.minLat, self.maxLon, self.maxLat]
        return result

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
