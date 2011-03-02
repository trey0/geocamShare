#!/usr/bin/env python
# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from math import sqrt, sin, cos, floor, log
import random
import uuid
import time
import datetime
import sys
import base64
import getpass

from django.conf import settings
import pyproj
import urllib2

from geocamShare.shareCore.utils import anyjson as json

geodG = pyproj.Geod(ellps='WGS84')
rndG = random.Random()
verbosityG = 0

def addVector(lonLat, radiusMeters, thetaDegrees):
    lon, lat, backAz = geodG.fwd(lonLat[0], lonLat[1], thetaDegrees, radiusMeters)
    return (lon, lat)

def getDistanceBearing(lonLat0, lonLat1):
    az, backAz, radiusMeters = geodG.inv(lonLat0[0], lonLat0[1], lonLat1[0], lonLat1[1])
    return radiusMeters, az

def getDistance(lonLat0, lonLat1):
    return getDistanceBearing(lonLat0, lonLat1)[0]

def dumps(obj):
    if settings.DEBUG:
        return json.dumps(obj, indent=4, sort_keys=True) # pretty print
    else:
        return json.dumps(obj, separators=(',',':')) # compact

def getBogusUuid(name):
    return str(uuid.uuid3(uuid.NAMESPACE_DNS, name))

def getPoissonSample(c):
    '''Get a sample from the Poisson distribution with density c'''
    x = 0
    t = 0
    while 1:
        t -= log(rndG.uniform(0, 1)) / c
        if t > 1:
            break
        x += 1
    return x

class Disc(object):
    def __init__(self, opts):
        self.center = (opts.longitude, opts.latitude)
        self.radiusMeters = opts.radius * 1000

    def getRandomPos(self):
        r = self.radiusMeters * sqrt(rndG.uniform(0, 1))
        theta = rndG.uniform(0, 360)
        return addVector(self.center, r, theta)

    def containsPos(self, pos):
        return getDistance(self.center, pos) < self.radiusMeters

class ResourceClient(object):
    def __init__(self, opts, i):
        self.disc = Disc(opts)
        self.altitude = opts.altitude
        self.speedMetersPerSecond = opts.speed * 1000.0 / 3600
        self.minPeriodSeconds = opts.period
        self.turnDistanceMeters = opts.turnDistance * 1000.0
        self.url = opts.url
        if self.url != '' and not self.url.endswith('/'):
            self.url += '/'

        self.userName = 'nasa%02d' % (i+1)
        if opts.userName:
            self.userName = opts.userName;

        self.authUser = opts.user
        self.authPassword = opts.password
        self.uuid = getBogusUuid(self.userName)

        now = time.time()
        self.lastUpdated = now
        self.driveDirection = rndG.uniform(0, 360)
        self.nextPostTime = now + rndG.uniform(0, self.minPeriodSeconds)
        self.pos = self.disc.getRandomPos()

    def __str__(self):
        return '%s %s %s %s' % (self.__class__.__name__, self.userName, self.pos[0], self.pos[1])

    def randomMove(self, dt):
        numTurns = getPoissonSample((dt * self.speedMetersPerSecond) / self.turnDistanceMeters)
        if numTurns > 0:
            # (ignore multiple turns in one time step and arbitrarily put the turn at the current position)
            randomSign = 1 - 2*rndG.randint(0, 1)
            newDirection = self.driveDirection + randomSign * rndG.uniform(60, 120)
            newDirection = 360.0 * ((newDirection / 360.0) - floor(newDirection / 360.0))
            self.driveDirection = newDirection
        
        # tryPos is the result of driving in the current direction at the current speed for time dt
        tryPos = addVector(self.pos, dt * self.speedMetersPerSecond, self.driveDirection)

        # the actual position we move to is the closest point to tryPos that is inside the disc
        r, theta = getDistanceBearing(self.disc.center, tryPos)
        if r > self.disc.radiusMeters:
            r = self.disc.radiusMeters
            self.pos = addVector(self.disc.center, r, theta)
        else:
            self.pos = tryPos
        
    def getGeometry(self):
        if self.altitude == None:
            coordinates = self.pos
        else:
            coordinates = (self.pos[0], self.pos[1], self.altitude)
        return dict(type='Point',
                    coordinates=coordinates)

    def getProperties(self):
        return dict(userName=self.userName,
                    timestamp=datetime.datetime.now().replace(microsecond=0).isoformat() + 'Z')

    def getGeoJsonDict(self):
        return dict(type='Feature',
                    id=self.uuid,
                    geometry=self.getGeometry(),
                    properties=self.getProperties())

    def post(self):
        now = time.time()

        data = dumps(self.getGeoJsonDict())
        if verbosityG >= 2:
            print data
        elif verbosityG >= 1:
            sys.stdout.write('.')
            sys.stdout.flush()
        opener = urllib2.build_opener()
        headers = {'User-Agent': 'GeoCam Tracking Client Simulator',
                   'Content-Type': 'application/json'}
        if self.authPassword:
            auth = base64.encodestring('%s:%s' % (self.authUser, self.authPassword))[:-1]
            headers['Authorization'] = 'Basic %s' % auth
        req = urllib2.Request(url=self.url + 'tracking/post/',
                              headers=headers,
                              data=data)
        resp = opener.open(req)

        self.nextPostTime = now + rndG.uniform(self.minPeriodSeconds, 1.1 * self.minPeriodSeconds)

    def update(self):
        now = time.time()
        dt = now - self.lastUpdated
        self.randomMove(dt)
        if now >= self.nextPostTime:
            self.post()
        self.lastUpdated = now

def doit(opts):
    global verbosityG
    verbosityG = opts.verbosity
    
    if opts.user and not opts.noSSL:
        if not opts.url.startswith('https'):
            opts.url = 'https:' + opts.url[5:]
    if opts.user and not opts.password:
        opts.password = getpass.getpass('password for %s at %s: ' % (opts.user, opts.url))

    resourceClients = [];
    if opts.namesFile:
        try:
            f = open(opts.namesFile, "r")
            for line in f:
                opts.userName = line.strip()
                resourceClients.append(ResourceClient(opts, 1))
        except IOError:
            print "Unable to open %s. Aborting."
            return
        finally:
            f.close()
    else:
        opts.userName = None
        resourceClients = [ResourceClient(opts, i) for i in xrange(0, opts.numResources)]

    while True:
        for rc in resourceClients:
            rc.update()
        time.sleep(0.1)

def getParser():
    import optparse
    parser = optparse.OptionParser("""usage: clientSim.py

Simulates a number of moving resources posting their position to GeoCam
Share.  Each resource drives around randomly and all are constrained to
stay within a disc you define.  All the clients post updates to the
server at the same rate which you specify, but their heartbeats are
tracked independently, and a small stochastic delay is added so that
they tend to go in and out of sync with each other over time.  This
simulator is single-threaded and blocks waiting for HTTP POST responses,
so it's not good for finding race conditions involving multiple
simultaneous posts.
""")
    parser.add_option('-n', '--numResources',
                      type='int', default=5,
                      help='Number of moving resources to simulate [%default]')
    parser.add_option('--latitude',
                      type='float', default=37.385715,
                      help='Center latitude of disc to move around in [%default]')
    parser.add_option('--longitude',
                      type='float', default=-122.083986,
                      help='Center longitude of disc to move around in [%default]')
    parser.add_option('--altitude',
                      type='float', default=None,
                      help='Constant altitude to use [%default]')
    parser.add_option('-r', '--radius',
                      type='float', default=2,
                      help='Radius of disc to move around in (km) [%default]')
    parser.add_option('-s', '--speed',
                      type='float', default=30,
                      help='Speed to move at (km/h) [%default]')
    parser.add_option('-t', '--turnDistance',
                      type='float', default=1,
                      help='Mean distance between turns (km) [%default]')
    parser.add_option('-p', '--period',
                      type='float', default=1,
                      help='Minimum period between updates sent to server from each resource (seconds) [%default]')
    parser.add_option('-u', '--url',
                      default='http://localhost:8000' + settings.SCRIPT_NAME,
                      help='Base url of GeoCam Share server to post updates to [%default]')
    parser.add_option('-v', '--verbosity',
                      action='count',
                      help='Make simulator more verbose; can specify -v multiple times')
    parser.add_option('--user',
                      default=getpass.getuser(),
                      help='Username for server authentication [%default]')
    parser.add_option('--password',
                      default=None,
                      help='Password for server authentication.')
    parser.add_option('--noSSL', 
                      dest='noSSL', action='store_true', default=False,
                      help='Do not force SSL for authentication.')
    parser.add_option('--namesFile', 
                      dest="namesFile", default=None,
                      help='File with usernames for the resources.')
    return parser

def main():
    parser = getParser()
    opts, args = parser.parse_args()
    doit(opts)

if __name__ == '__main__':
    main()
