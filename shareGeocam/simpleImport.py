#!/usr/bin/env python
# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

"""Simplest possible import to get some data to work with.  This code
will not be used in production."""

import sys
import os
import datetime
import glob
import csv
import re
import uuid
import getpass

import PIL
import pytz
import tagging
from django.contrib.auth.models import User
from django.conf import settings

from share2.shareCore.models import Feature, Folder
from share2.shareGeocam.models import Photo
from share2.shareCore.utils import mkdirP, UploadClient
from share2.shareCore.TimeUtils import parseUploadTime

DEFAULT_IMPORT_DIR = os.path.join(settings.CHECKOUT_DIR, 'importData', 'guiberson')

def checkMissing(val):
    if val == -999:
        return None
    else:
        return val

def importImageDirect(imagePath, attributes):
    im = PIL.Image.open(imagePath, 'r')
    widthPixels, heightPixels = im.size
    del im

    lat = attributes['latitude']
    lon = attributes['longitude']
    folder = Folder.objects.get(name=attributes['folder'])
    tz = pytz.timezone(folder.timeZone)
    timestampLocal = parseUploadTime(attributes['cameraTime']).replace(tzinfo=tz)
    timestampUtc = timestampLocal.astimezone(pytz.utc).replace(tzinfo=None)

    tags = tagging.utils.parse_tag_input(attributes['tags'])
    icon = settings.ICONS[0] # default
    for t in tags:
        if t in settings.ICONS_DICT:
            icon = t
            break

    img, created = (Photo.objects.get_or_create
                    (name=os.path.basename(imagePath),
                     author=User.objects.get(username=attributes['userName']),
                     minTime=timestampUtc,
                     maxTime=timestampUtc,
                     defaults=dict(minLat=lat,
                                   minLon=lon,
                                   maxLat=lat,
                                   maxLon=lon,
                                   roll=attributes['roll'],
                                   pitch=attributes['pitch'],
                                   yaw=checkMissing(attributes['yaw']),
                                   notes=attributes['notes'],
                                   tags=tags,
                                   widthPixels=widthPixels,
                                   heightPixels=heightPixels,
                                   folder=folder,
                                   icon=icon,
                                   )))

    if created:
        print 'processing', unicode(img)
        img.process(importFile=imagePath)
        img.save()
    else:
        print 'skipping already imported', unicode(img)

def importDir(opts, dir, uploadClient):
    dir = os.path.realpath(dir)

    tzFile = '%s/timezone.txt' % dir
    if os.path.exists(tzFile):
        timeZone = file(tzFile, 'r').read().strip()
    else:
        timeZone = 'US/Pacific' # default

    folderName = os.path.basename(dir)
    if not opts.upload:
        folder, created = Folder.objects.get_or_create(name=folderName,
                                                       defaults=dict(timeZone=timeZone))

    csvFiles = glob.glob('%s/*.csv' % dir)
    if not csvFiles:
        print >>sys.stderr, "warning: can't import dir %s, no *.csv files found" % dir
        return
    csvName = csvFiles[0]
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
            lat, lon = None, None
        imagePath = os.path.join(dir, 'photos', name)

        # make up a consistent bogus uuid field so we can test incremental upload.
        # real clients should always make a stronger uuid to avoid collisions!
        bogusUuid = uuid.uuid3(uuid.NAMESPACE_DNS, '%s-%s-%s' % (name, opts.user, timeStr))
        
        # map to field names in upload form
        attributes = dict(name=name,
                          userName=opts.user,
                          cameraTime=timeStr,
                          latitude=lat,
                          longitude=lon,
                          roll=None,
                          pitch=None,
                          yaw=compass,
                          notes=notes,
                          tags=tagsDb,
                          uuid=bogusUuid,
                          folder=folderName)
        if uploadClient:
            print 'uploading', os.path.basename(imagePath)
            uploadClient.uploadImage(imagePath, attributes, downsampleFactor=int(opts.downsample))
        else:
            importImageDirect(imagePath, attributes)

        i += 1

def doit(opts, importDirs):
    if opts.downsample != '1':
        opts.upload = True
    if opts.password:
        opts.secure = True
    if opts.secure:
        opts.upload = True
        assert opts.url
        if opts.password == None:
            opts.password = getpass.getpass('password for %s at %s: ' % (opts.user, opts.url))
    if opts.upload:
        opts.url = opts.url.rstrip('/')
        uploadClient = UploadClient(opts.url, opts.user, opts.password)
    else:
        uploadClient = None
    if opts.clean:
        print 'cleaning'
        features = Feature.objects.all()
        for f in features:
            f.deleteFiles()
            f.delete()
    for dir in importDirs:
        importDir(opts, dir, uploadClient)

def main():
    import optparse
    parser = optparse.OptionParser('usage: %prog <dir1> [dir2 ...]')
    parser.add_option('-c', '--clean',
                      action='store_true', default=False,
                      help='Clean database before import')
    parser.add_option('-m', '--match',
                      default=None,
                      help='Import only photos matching specified pattern')
    parser.add_option('-n', '--number',
                      default=0,
                      help='Limit number of photos to import')
    parser.add_option('-u', '--upload',
                      action='store_true', default=False,
                      help='Simulate client HTTP upload rather than directly connecting to db')
    parser.add_option('-s', '--secure',
                      action='store_true', default=False,
                      help='Use share v2 secure upload. Implies -u.')
    parser.add_option('--url',
                      default='http://localhost' + settings.SCRIPT_NAME,
                      help='Server url for client upload [%default]')
    parser.add_option('--user',
                      default=getpass.getuser(),
                      help='Author of imported photos [%default]')
    parser.add_option('-p', '--password',
                      default=None,
                      help='Password to use for upload authentication. Implies -s.')
    parser.add_option('-d', '--downsample',
                      default='1',
                      help='Downsample images by specified factor before upload.  Implies -u.')
    opts, args = parser.parse_args()
    if not args:
        print >>sys.stderr, 'warning: no import dirs specified, not importing anything'
    importDirs = args
    doit(opts, importDirs)

if __name__ == '__main__':
    main()
