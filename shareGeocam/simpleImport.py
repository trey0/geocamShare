#!/usr/bin/env python

"""Simplest possible import to get some data to work with.  This code
will not be used in production."""

import sys
import os
import datetime
import glob
import csv
import re

from django.contrib.auth.models import User
from django.conf import settings

from share2.shareGeocam.models import Feature, Photo
from share2.shareCore.utils import mkdirP

DEFAULT_IMPORT_DIR = os.path.join(settings.CHECKOUT_DIR, 'data', 'importData', 'guiberson')

def parseCsvTime(timeStr):
    # strip microseconds if present
    timeStr = re.sub(r'\.\d+$', '', timeStr)
    return datetime.datetime.strptime(timeStr, '%Y-%m-%d %H:%M:%S')

def importDir(opts, dir):
    owner = User.objects.get(username=opts.user)
    dir = os.path.realpath(dir)
    csvName = glob.glob('%s/*.csv' % dir)[0]
    reader = csv.reader(file(csvName, 'r'))
    firstLine = True
    i = 0
    for row in reader:
        if firstLine:
            firstLine = False
            continue
        if opts.number != 0 and i >= opts.number:
            break
        allText = ' '.join(row)
        if opts.match and not re.search(opts.match, allText):
            continue
        latStr, lonStr, compassStr, timeStr, name, notes, tagsStr, creatorName = row
        tags = [t.strip() for t in tagsStr.split(',')]
        tags = [t for t in tags if t != 'default']
        tags.append(creatorName)
        tagsDb = ', '.join(tags)
        lat, lon, compass = float(latStr), float(lonStr), float(compassStr)
        if lat == -999:
            continue
        timestamp = parseCsvTime(timeStr)
        photo, created = (Photo.objects.get_or_create
                          (name=name,
                           owner=owner,
                           timestamp=timestamp,
                           defaults=dict(lat=lat,
                                         lon=lon,
                                         yaw=compass,
                                         notes=notes,
                                         tags=tagsDb,
                                         )))
        if created:
            print 'processing', unicode(photo)
            photo.process(importFile=os.path.join(dir, 'photos', name))
            photo.save()
        else:
            print 'skipping already imported ', unicode(photo)
        i += 1

def doit(opts, importDirs):
    if opts.clean:
        print 'cleaning'
        Feature.objects.all().delete()
        Photo.objects.all().delete()
    for dir in importDirs:
        importDir(opts, dir)

def main():
    import optparse
    parser = optparse.OptionParser('usage: %prog <dir1> [dir2 ...]')
    parser.add_option('-c', '--clean',
                      action='store_true', default=False,
                      help='Clean database before import')
    parser.add_option('-u', '--user',
                      default='root',
                      help='Owner of imported photos')
    parser.add_option('-m', '--match',
                      default=None,
                      help='Import only photos matching specified pattern')
    parser.add_option('-n', '--number',
                      default=0,
                      help='Number of photos to import')
    opts, args = parser.parse_args()
    if not args:
        print >>sys.stderr, 'warning: no import dirs specified, not importing anything'
    importDirs = args
    doit(opts, importDirs)

if __name__ == '__main__':
    main()
