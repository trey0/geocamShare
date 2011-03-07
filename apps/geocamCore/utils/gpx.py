# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

import datetime
from xml.dom import minidom

import iso8601

from geocamUtil import anyjson as json

class RaiseValueError:
    pass
RAISE_VALUE_ERROR = RaiseValueError()

def getChild(node, name, dflt=RAISE_VALUE_ERROR, ns=None):
    # getElementsByTagName() returns a list of descendant nodes with
    # tags that match the specified name.  getChild() returns the first
    # such descendant that is a direct child. (e.g. it gets the <Icon>
    # that is a direct child rather than the one that is buried inside
    # the <Style>.)
    if node != None:
        if ns == None:
            children = node.getElementsByTagName(name)
        else:
            children = node.getElementsByTagNameNS(ns, name)
        for n in children:
            if n.parentNode == node:
                return n
    if dflt == RAISE_VALUE_ERROR:
        raise ValueError('no immediate child named %s' % name)
    else:
        return dflt

def getChildText(node, name, dflt=RAISE_VALUE_ERROR, ns=None):
    try:
        child = getChild(node, name, ns=ns)
    except ValueError:
        if dflt == RAISE_VALUE_ERROR:
            raise
        else:
            return dflt
    else:
        return getText(child)

def getText(node):
    rc = ""
    for node in node.childNodes:
        if node.nodeType == node.TEXT_NODE:
            rc = rc + node.data
    return rc
        
def getFloat(node):
    return float(getText(node))

def floatOrNone(str):
    if str == None:
        return None
    else:
        return float(str)

def getFloatFromAttr(node, name):
    return float(node.attributes[name].value)

class RoundingEncoder(json.JSONEncoder):
    def __init__(self, decimalPlaces=6, **kwargs):
        self.roundingFormat = '%%.%df' % decimalPlaces
        super(RoundingEncoder, self).__init__(**kwargs)
        
    def _iterencode(self, o, markers=None):
        if isinstance(o, float):
            return self.roundingFormat % o
        else:
            return super(RoundingEncoder, self)._iterencode(o, markers);

class Bbox:
    def __init__(self, dim=2):
        self.dim = dim
        self.minVal = [99e+20] * self.dim
        self.maxVal = [-99e+20] * self.dim

    def addPoint(self, v):
        for i in xrange(self.dim):
            self.minVal[i] = min(self.minVal[i], v[i])
            self.maxVal[i] = max(self.maxVal[i], v[i])

    def addBox(self, bbox):
        for i in xrange(self.dim):
            self.minVal[i] = min(self.minVal[i], bbox.minVal[i])
            self.maxVal[i] = max(self.maxVal[i], bbox.maxVal[i])

    def asList(self):
        return self.minVal + self.maxVal

class TimeRange:
    def __init__(self):
        self.minTime = datetime.datetime.max
        self.maxTime = datetime.datetime.min
        self.hasData = False

    def addTime(self, dt):
        if dt != None:
            self.minTime = min(self.minTime, dt)
            self.maxTime = max(self.maxTime, dt)
            self.hasData = True

    def addRange(self, rng):
        if rng.hasData:
            self.minTime = min(self.minTime, rng.minTime)
            self.maxTime = max(self.maxTime, rng.maxTime)
            self.hasData = True

    def asList(self):
        if self.hasData:
            return [self.minTime, self.maxTime]
        else:
            return None

class TrackLog:
    def __init__(self, tracks=None):
        self.tracks = tracks

    def getNumPoints(self):
        n = 0
        for track in self.tracks:
            n += len(track.pts)
        return n

    def geoJson(self):
        return dict(type='MultiLineString',
                    geometry=[t.geoJson() for t in self.tracks])

    def geoJsonString(self, decimalPlaces=6):
        return RoundingEncoder(decimalPlaces).encode(self.geoJson())

    def getBbox(self):
        bbox = Bbox()
        for track in self.tracks:
            bbox.addBox(track.getBbox())
        return bbox

    def getTimeRange(self):
        rng = TimeRange()
        for track in self.tracks:
            rng.addRange(track.getTimeRange())
        return rng

    def debugPrint(self):
        print 'icon=%s lineStyle=%s lineColor=%s' % (self.icon, self.lineStyle, self.lineColor)
        print 'timeRange=%s' % (self.getTimeRange().asList())
        print 'bbox=%s' % (self.getBbox().asList())
        print self.geoJsonString()

    @staticmethod
    def parseGpxString(gpxString):
        doc = minidom.parseString(gpxString)
        gpx = doc.documentElement
        log = TrackLog()
        geocamNS = 'http://geocam.arc.nasa.gov/schema/gpxExtensions/1'
        trackNodes = gpx.getElementsByTagName('trk')
        log.tracks = []
        for trackNode in trackNodes:
            pts = []
            for ptNode in trackNode.getElementsByTagName('trkpt'):
                ele = floatOrNone(getChildText(ptNode, 'ele', None))
                timestampStr = getChildText(ptNode, 'time', None)
                if timestampStr:
                    t = iso8601.parse_date(timestampStr)
                    # normalize to UTC
                    timestamp = t.replace(tzinfo=None) - t.utcoffset()
                else:
                    timestamp = None
                pts.append(TrackPoint(lat=getFloatFromAttr(ptNode, 'lat'),
                                      lon=getFloatFromAttr(ptNode, 'lon'),
                                      ele=ele,
                                      timestamp=timestamp))
            extensions = getChild(trackNode, 'extensions', None)
            track = Track(icon=getChildText(extensions, 'icon', '', ns=geocamNS),
                          lineStyle=getChildText(extensions, 'lineStyle', '', ns=geocamNS),
                          lineColor=getChildText(extensions, 'lineColor', '', ns=geocamNS),
                          pts=pts)
            log.tracks.append(track)
        return log

    @staticmethod
    def parseGpxFile(gpxPath):
        return TrackLog.parseGpxString(file(gpxPath, 'r').read())        

class Track:
    def __init__(self, icon=None, lineColor=None, lineStyle=None, pts=None):
        self.icon = icon
        self.lineColor = lineColor
        self.lineStyle = lineStyle
        self.pts = pts

    def geoJson(self):
        return [p.geoJson() for p in self.pts]

    def getBbox(self):
        bbox = Bbox()
        for p in self.pts:
            bbox.addPoint([p.lon, p.lat])
        return bbox

    def getTimeRange(self):
        rng = TimeRange()
        for p in self.pts:
            rng.addTime(p.timestamp)
        return rng

class TrackPoint:
    def __init__(self, lat=None, lon=None, ele=None, timestamp=None):
        self.lat = lat
        self.lon = lon
        self.ele = ele
        self.timestamp = timestamp

    def geoJson(self):
        return [self.lon, self.lat, self.ele]

def main():
    import optparse
    parser = optparse.OptionParser('usage: gpx <1.gpx> [2.gpx ...]')
    opts, args = parser.parse_args()
    if not args:
        parser.error('please specify a file to parse')
    for arg in args:
        TrackLog.parseGpxFile(arg).debugPrint()
        

if __name__ == '__main__':
    main()
