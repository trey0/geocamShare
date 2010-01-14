#!/usr/bin/env python

import os
import glob

from django.conf import settings

from share2.share.models import LidarScan, LidarPano, Mic, PancamPano, ALL_TASKS_DICT
from share2.share.indexlib import RequestIdPath, nukeDb, processReqPath

def doit(opts):
    if opts.clean:
        print 'got -c option, deleting old data before indexing'
        nukeDb()
    if opts.path:
        expandedPaths = []
        for p in opts.path:
            expandedPaths += glob.glob(p)
        reqPaths = [RequestIdPath.fromPath(p)
                    for p in expandedPaths]
    else:
        # default for testing
        reqPaths = [RequestIdPath('k10black', '20090626', id)
                    for id in requestIds]
    for p in reqPaths:
        processReqPath(p)

def main():
    import optparse
    parser = optparse.OptionParser('usage: %prog')
    parser.add_option('-c', '--clean',
                      default=False, action='store_true',
                      help='Clean tables before indexing')
    parser.add_option('-r', '--requestIdPath',
                      action='append', type='string',
                      dest='path',
                      help='Add a request id path (can specify multiple times)')
    opts, args = parser.parse_args()
    doit(opts)

if __name__ == '__main__':
    main()
