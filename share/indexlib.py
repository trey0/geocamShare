#!/usr/bin/env python

import sys
import os

from django.conf import settings

from share2.share.utils import getIdSuffix
from share2.share.models import LidarScan, LidarPano, Mic, PancamPano, ALL_TASKS_DICT

class RequestIdPath:
    def __init__(self, robot, date, requestId, path=None):
        self.robot = robot
        self.date = date
        self.requestId = requestId
        self.path = path or '/irg/data/%s/%s/%s' % (settings.ROBOT_HOST_MAP[robot], date, requestId)

    @staticmethod
    def fromPath(path):
        path = path.rstrip('/')
        elts = path.split(os.path.sep)
        robotHost, date, requestId = elts[-3:]
        robot = settings.HOST_ROBOT_MAP[robotHost]
        return RequestIdPath(robot, date, requestId, path)

def nukeDb():
    for dpType in ALL_TASKS_DICT.values():
        dpType.objects.all().delete()

def processReqPath(reqPath):
    for pat in settings.SKIP_PATTERNS:
        if pat in reqPath.requestId:
            return # no processing needed
    idSuffix = getIdSuffix(reqPath.requestId)
    if idSuffix.startswith('LS'):
        td = LidarScan()
    elif idSuffix.startswith('LP'):
        td = LidarPano()
    elif idSuffix.startswith('P'):
        td = PancamPano()
    elif idSuffix.startswith('MIC'):
        td = Mic()
    else:
        print >>sys.stderr, 'skipping requestId with unknown suffix %s' % idSuffix
        return
    td.process(reqPath)
    td.save()

