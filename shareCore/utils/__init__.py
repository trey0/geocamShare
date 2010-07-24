
import os
import glob
import re
from cStringIO import StringIO
import errno
import datetime
import time

import rdflib
from rdflib.Graph import Graph
import iso8601
import pytz

from django.conf import settings

class Xmp:
    def __init__(self, xmpFile):
        self.graph = Graph()
        xmp = file(xmpFile, 'r').read()
        match = re.search('<rdf:RDF.*</rdf:RDF>', xmp, re.DOTALL)
        xmp = match.group(0)
        self.graph.parse(StringIO(xmp))

    def _getPredicate(self, field):
        prefix, attr = field.split(':',1)
        return rdflib.URIRef(self.graph.namespace_manager.store.namespace(prefix) + attr)

    def get(self, field, dflt='ERROR'):
        subject = rdflib.URIRef('')
        predicate = self._getPredicate(field)
        value = self.graph.value(subject, predicate, None)
        if value == None:
            if dflt == 'ERROR':
                raise KeyError(field)
            else:
                return dflt
        else:
            return value

    def getDegMin(self, field, dirValues):
        val = self.get(field, None)
        if val == None:
            return None
        degMin = val[:-1]
        degS, minS = degMin.split(',')
        deg = float(degS)
        min = float(minS)
        dirS = val[-1]
        if dirS == dirValues[0]:
            sign = 1
        elif dirS == dirValues[1]:
            sign = -1
        else:
            raise ValueError('expected dir in %s, got %s' % (dirValues, dirS))
        return sign * (deg + min/60.)

    def getYaw(self):
        yawStr = self.get('exif:GPSImgDirection', None)
        if yawStr == None:
            return None
        yaw = float(yawStr)
        if yaw < 0:
            yaw = yaw + 360
        elif yaw > 360:
            yaw = yaw - 360
        return yaw

    def checkMissing(self, val):
        if val in (0, -999):
            return None
        else:
            return val

    def copyToTaskData(self, td):
        t = iso8601.parse_date(self.get('exif:DateTimeOriginal'))
        timestamp = t.replace(tzinfo=None) - t.utcoffset() # normalize to utc
        td.minTime = timestamp
        td.maxTime = timestamp
        lat = self.checkMissing(self.getDegMin('exif:GPSLatitude', 'NS'))
        lon = self.checkMissing(self.getDegMin('exif:GPSLongitude', 'EW'))
        td.minLat = lat
        td.maxLat = lat
        td.minLon = lon
        td.maxLon = lon
        td.yaw = self.getYaw()

class NoDataError(Exception):
    pass

def getMiddleFileWithExtension(ext, reqPath):
    allXmps = glob.glob('%s/*%s' % (reqPath, ext))
    allXmps = [x for x in allXmps
               if not x.startswith('thumbnail')]
    if not allXmps:
        raise NoDataError('no %s files in %s' % (ext, reqPath))
    allXmps.sort()
    assert len(allXmps) > 0
    return allXmps[len(allXmps)//2]
    
def getMiddleXmpFile(reqPath):
    return getMiddleFileWithExtension('xmp', reqPath)

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

def mkdirP(dir):
    try:
        os.makedirs(dir)
    except OSError, err:
        if err.errno != errno.EEXIST:
            raise

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

# pull in other modules in this dir so they're exported
import MimeMultipartFormData
import uploadClient
import gpx
import Printable
import geo
