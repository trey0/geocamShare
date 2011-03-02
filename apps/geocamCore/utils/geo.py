# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

import sys
import math
from math import sqrt, sin, cos, tan, atan, atan2

DATUMS = dict(WGS84 = dict(a=6378137.0,
                           f=1.0/298.257223563))

RAD_TO_DEG_CONSTANT = (180.0/math.pi)
DEG_TO_RAD_CONSTANT = (math.pi/180.0)

def getEcefFromLonLatAlt(lla, datum='WGS84'):
    dat = DATUMS[datum]
    a = dat['a']
    f = dat['f']
    e2 = 2*f - f**2
    lonDeg, latDeg, h = lla
    lon = lonDeg * DEG_TO_RAD_CONSTANT
    lat = latDeg * DEG_TO_RAD_CONSTANT
    chi = sqrt(1-e2*sin(lat)**2)
    q = (a/chi + h) * cos(lat)
    return (q * cos(lon), q * sin(lon), ((a*(1-e2) / chi) + h) * sin(lat))

def dist(x, y):
    sum = 0
    for i in xrange(0, len(x)):
        sum += (x[i] - y[i])**2
    return sqrt(sum)

def distLla(lla1, lla2):
    return dist(getEcefFromLonLatAlt(lla1),
                getEcefFromLonLatAlt(lla2))
