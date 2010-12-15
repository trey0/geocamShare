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
import PIL

from django.conf import settings

IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png')

def findImageName(xmpName):
    base = os.path.splitext(xmpName)[0]
    for ext in IMAGE_EXTENSIONS:
        if os.path.exists(base + ext):
            return base + ext
    raise Exception('no image corresponding to xmp file %s' % xmpName)

class Xmp:
    def __init__(self, fname):
        self.graph = Graph()
        if os.path.splitext(fname)[1].lower() in IMAGE_EXTENSIONS:
            self.parseImageHeader(fname)
        else:
            self.parseXmp(fname)
            self.xmpName = fname
            
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
        nsuri = self.graph.namespace_manager.store.namespace(prefix)
        if nsuri == None:
            return None
        else:
            return rdflib.URIRef(nsuri + attr)

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
    def normalizeAltitude(altitude, altitudeRef):
        '''Assumes yaw is a float, a string representation of a float, or None.
        Values 0 and -999 get mapped to None.'''

        if altitude != None and not isinstance(altitude, float):
            altitude = Xmp.getRational(altitude)
        altitude = Xmp.checkMissing(altitude)

        altitudeRef = Xmp.checkMissing(altitudeRef)

        if altitude != None and abs(altitude) > 20000:
            # Ricoh Caplio sometimes outputs huge bogus altitude values
            altitude = None

        if altitude == None:
            return (altitude, '')

        # to do: possible transforms here

        return (altitude, altitudeRef)

    def getAltitude(self):
        altitudeStr = self.get('exif:GPSAltitude', None)
        altitudeRefStr = 'S' # EXIF always uses sea-level as reference
        return self.normalizeAltitude(altitudeStr, altitudeRefStr)

    @staticmethod
    def checkMissing(val):
        if val in (0, -999, ''):
            return None
        else:
            return val

    def getTime(self, field):
        timeStr = self.get('exif:DateTimeOriginal', None)
        if timeStr == None:
            return None
        t = iso8601.parse_date(timeStr,
                               default_timezone=pytz.timezone(settings.TIME_ZONE))
        return t.replace(tzinfo=None) - t.utcoffset() # normalize to utc
        
    def getDict(self):
        timestamp = self.getTime('exif:DateTimeOriginal')
        lat = self.checkMissing(self.getDegMin('exif:GPSLatitude', 'NS'))
        lon = self.checkMissing(self.getDegMin('exif:GPSLongitude', 'EW'))
        yaw, yawRef = self.getYaw()
        altitude, altitudeRef = self.getAltitude()

        widthStr = self.get('tiff:ImageWidth', None)
        heightStr = self.get('tiff:ImageLength', None)
        if widthStr != None and heightStr != None:
            widthPixels, heightPixels = int(widthStr), int(heightStr)
        else:
            im = PIL.Image.open(findImageName(self.xmpName))
            widthPixels, heightPixels = im.size
            del im

        vals0 = dict(timestamp=timestamp,
                     latitude=lat,
                     longitude=lon,
                     yaw=yaw,
                     yawRef=yawRef,
                     altitude=altitude,
                     altitudeRef=altitudeRef,
                     widthPixels=widthPixels,
                     heightPixels=heightPixels)

        return dict([(k,v) for k, v in vals0.iteritems()
                     if self.checkMissing(v) != None])

    def copyToPlacemark(self, td):
        vals = self.getDict()
        for k, v in vals.iteritems():
            setattr(td, k, v)

