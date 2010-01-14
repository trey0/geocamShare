
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
        td.lat = self.getDegMin('exif:GPSLatitude', 'NS')
        td.lon = self.getDegMin('exif:GPSLongitude', 'EW')
        td.yaw = self.getYaw()

def getMiddleXmpFile(reqPath):
    allXmps = glob.glob('%s/*.xmp' % reqPath.path)
    return allXmps[len(allXmps)//2]
    
def getIdSuffix(requestId):
    return requestId.split('_')[-1]

def mkdirP(dir):
    try:
        os.makedirs(dir)
    except OSError, err:
        if err.errno != errno.EEXIST:
            raise

