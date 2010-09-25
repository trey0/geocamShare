# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

import os
import re
from cStringIO import StringIO
import tempfile

import rdflib
from rdflib.Graph import Graph
import iso8601
import pytz

from django.conf import settings

class Xmp:
    def __init__(self, fname):
        self.graph = Graph()
        if os.path.splitext(fname)[1].lower() in ('.jpg', '.jpeg', '.png'):
            self.parseImageHeader(fname)
        else:
            self.parseXmp(fname)
            
    def parseImageHeader(self, fname):
        fd, xmpFname = tempfile.mkstemp('-parseImageHeader.xmp')
        os.close(fd)
        os.system('exiftool -fast -tagsfromfile %s "-all>xmp:all" "-xmp:all>xmp:all" %s'
                  % (fname, xmpFname))
        self.parseXmp(xmpFname)
        try:
            os.unlink(xmpFname)
        except OSError, e:
            traceback.print_exc()
            print >>sys.stderr, '[parseImageHeader: could not delete %s]' % xmpFname

    def parseXmp(self, xmpFile):
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
            return str(value)

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

    @staticmethod
    def getRational(s):
        m = re.search(r'(-?\d+)/(-?\d+)', s)
        if m:
            num = int(m.group(1))
            denom = int(m.group(2))
            if denom == 0:
                return None
            else:
                return float(num)/denom
        else:
            return float(s)
            

    @staticmethod
    def normalizeYaw(yaw, yawRef):
        '''Assumes yaw is a float, a string representation of a float, or None.
        Values 0 and -999 get mapped to None.'''

        if yaw != None and not isinstance(yaw, float):
            yaw = Xmp.getRational(yaw)
        yaw = Xmp.checkMissing(yaw)

        yawRef = Xmp.checkMissing(yawRef)

        if yaw == None:
            return (None, '')

        # todo: correct for magnetic declination here
        # (if yawRef == 'M', apply correction and set
        # yawRef to 'T')

        if yaw < 0:
            yaw = yaw + 360
        elif yaw > 360:
            yaw = yaw - 360

        return (yaw, yawRef)

    def getYaw(self):
        yawStr = self.get('exif:GPSImgDirection', None)
        yawRefStr = self.get('exif:GPSImgDirectionRef', None)
        return self.normalizeYaw(yawStr, yawRefStr)

    @staticmethod
    def checkMissing(val):
        if val in (0, -999, ''):
            return None
        else:
            return val

    def getDict(self):
        t = iso8601.parse_date(self.get('exif:DateTimeOriginal'),
                               default_timezone=pytz.timezone(settings.TIME_ZONE))
        timestamp = t.replace(tzinfo=None) - t.utcoffset() # normalize to utc
        lat = self.checkMissing(self.getDegMin('exif:GPSLatitude', 'NS'))
        lon = self.checkMissing(self.getDegMin('exif:GPSLongitude', 'EW'))
        yaw, yawRef = self.getYaw()
        widthPixels = int(self.get('tiff:ImageWidth'))
        heightPixels = int(self.get('tiff:ImageLength'))

        vals0 = dict(timestamp=timestamp,
                     latitude=lat,
                     longitude=lon,
                     yaw=yaw,
                     yawRef=yawRef,
                     widthPixels=widthPixels,
                     heightPixels=heightPixels)

        return dict([(k,v) for k, v in vals0.iteritems()
                     if self.checkMissing(v) != None])

    def copyToPlacemark(self, td):
        vals = self.getDict()
        for k, v in vals.iteritems():
            setattr(td, k, v)

