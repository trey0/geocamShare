
import os
import glob
import re
from cStringIO import StringIO
import errno

import rdflib
from rdflib.Graph import Graph
import iso8601

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

    def get(self, field):
        subject = rdflib.URIRef('')
        predicate = self._getPredicate(field)
        value = self.graph.value(subject, predicate, None)
        if value == None:
            raise KeyError(field)
        else:
            return value

    def getDegMin(self, field, dirValues):
        val = self.get(field)
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
        yaw = float(self.get('exif:GPSImgDirection'))
        if yaw < 0:
            yaw = yaw + 360
        elif yaw > 360:
            yaw = yaw - 360
        return yaw

    def copyToTaskData(self, td):
        td.timestamp = iso8601.parse_date(self.get('exif:DateTimeOriginal'))
        td.minLat = self.getDegMin('exif:GPSLatitude', 'NS')
        td.maxLat = td.minLat
        td.minLon = self.getDegMin('exif:GPSLongitude', 'EW')
        td.maxLon = td.minLon
        td.yaw = self.getYaw()

def getMiddleXmpFile(reqPath):
    allXmps = glob.glob('%s/*.xmp' % reqPath.path)
    allXmps = [x for x in allXmps
               if not x.startswith('thumbnail')]
    allXmps.sort()
    assert len(allXmps) > 0
    return allXmps[len(allXmps)//2]
    
def getIdSuffix(requestId):
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
