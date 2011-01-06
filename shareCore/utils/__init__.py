# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

import os
import glob
import re
import errno
import datetime
import time
import tempfile

import pytz

from django.conf import settings

class NoDataError(Exception):
    pass

def importModuleByName(name):
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod

def getMiddleFileWithExtension(ext, path):
    allXmps = glob.glob('%s/*%s' % (path, ext))
    allXmps = [x for x in allXmps
               if not x.startswith('thumbnail')]
    if not allXmps:
        raise NoDataError('no %s files in %s' % (ext, path))
    allXmps.sort()
    assert len(allXmps) > 0
    return allXmps[len(allXmps)//2]
    
def getMiddleXmpFile(path):
    return getMiddleFileWithExtension('xmp', path)

def getUtcTimeFromDpName(reqPath, dpname):
    dptime = os.path.basename(dpname)[:13] # extract time part of dpname
    timeNoTz = datetime.datetime(*time.strptime(dptime, '%Y%m%d_%H%M')[:6])
    deploymentPrefix = reqPath.requestId[:3]
    matchingTimeZones = [tz
                         for (dep, tz) in settings.DEPLOYMENT_TIME_ZONES
                         if deploymentPrefix.startswith(dep)]
    if len(matchingTimeZones) != 1:
        raise Exception("can't infer time zone for deployment %s; please fix gds/settings.py DEPLOYMENT_TIME_ZONES to have exactly 1 matching time zone entry" % deploymentPrefix)
    tzName = matchingTimeZones[0]
    tz = pytz.timezone(tzName)
    timeWithTz = tz.localize(timeNoTz)
    timeUtc = timeWithTz.replace(tzinfo=None) - timeWithTz.utcoffset()
    return timeUtc

def getIdSuffix(requestId):
    # ignore attempt number if it exists
    requestId = re.sub('_\d+$', '', requestId)
    return requestId.split('_')[-1]

def makeUuid():
    try:
        import uuid
    except ImportError:
        # before python 2.5
        import random
        return '%04x-%02x-%02x-%02x-%06x' % (random.getrandbits(32), random.getrandbits(8),
                                             random.getrandbits(8), random.getrandbits(8),
                                             random.getrandbits(48))
    else:
        return str(uuid.uuid4())

def mkdirP(dir):
    try:
        os.makedirs(dir)
    except OSError, err:
        if err.errno != errno.EEXIST:
            raise

# pull in other modules in this dir so they're exported
import MimeMultipartFormData
import gpx
import Printable
import geo
from UploadClient import UploadClient
from Xmp import Xmp
from Builder import Builder
