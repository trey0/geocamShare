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
import stat

import PIL
import pytz
import tagging
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from geocamUtil import TimeUtil
from geocamUtil.FileUtil import mkdirP
from geocamCore.models import Feature, Folder

from geocamLens.UploadClient import UploadClient
from geocamLens.models import Photo
from geocamLens import settings

def checkMissing(val):
    if val == -999:
        return None
    else:
        return val

def importImageDirect(imagePath, attributes):
    try:
        author = User.objects.get(username=attributes['userName'])
    except ObjectDoesNotExist:
        print 'ERROR: No Django user "%s"; specify an existing user with the --user option, or create the user' % attributes['userName']
        sys.exit(1)
    attributes['author'] = author

    name = os.path.basename(imagePath)
    attributes['name'] = name

    matchingPhotos = Photo.objects.filter(name=name,
                                          author=author)

    if matchingPhotos:
        print 'skipping already imported', unicode(matchingPhotos[0])
    else:
        photo = Photo()
        photo.readImportVals(storePath=imagePath, uploadImageFormData=attributes)
        photo.save()
        photo.process(importFile=imagePath)
        photo.save()
        print 'processed', unicode(photo)

def getBogusUuid(name, userName, timeStr):
    return str(uuid.uuid3(uuid.NAMESPACE_DNS, '%s-%s-%s' % (name, userName, timeStr)))    

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

    photosToUpload = []

    csvFiles = glob.glob('%s/*.csv' % dir)
    if csvFiles:
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
            bogusUuid = getBogusUuid(name, opts.user, timeStr)

            # map to field names in upload form
            attributes = dict(name=name,
                              userName=opts.user,
                              cameraTime=timeStr,
                              latitude=lat,
                              longitude=lon,
                              altitude=None,
                              altitudeRef=None,
                              roll=None,
                              pitch=None,
                              yaw=compass,
                              notes=notes,
                              tags=tagsDb,
                              uuid=bogusUuid,
                              folder=folderName)

            photosToUpload.append(dict(imagePath=imagePath,
                                       attributes=attributes))
            i += 1
    else:
        images = []
        for ext in ('.jpg', '.jpeg', '.JPG'):
            images += glob.glob('%s/*%s' % (dir, ext))
        if images:
            if opts.match:
                print >>sys.stderr, "warning: can't import dir %s -- can't match tags unless we have a .csv" % dir
                images = []
            if opts.number != 0:
                images = images[:opts.number]
            for img in images:
                name = os.path.basename(img)
                timeStr = os.stat(img)[stat.ST_MTIME]
                bogusUuid = getBogusUuid(name, opts.user, timeStr)

                attributes = dict(name=name,
                                  userName=opts.user,
                                  uuid=bogusUuid,
                                  folder=os.path.basename(os.path.dirname(img)))
                
                photosToUpload.append(dict(imagePath=img,
                                           attributes=attributes))
        else:
            print >>sys.stderr, "warning: can't import dir %s -- no *.csv, no images" % dir

    for p in photosToUpload:
        if uploadClient:
            print 'uploading', os.path.basename(p['imagePath'])
            uploadClient.uploadImage(p['imagePath'], p['attributes'], downsampleFactor=int(opts.downsample))
        else:
            importImageDirect(p['imagePath'], p['attributes'])

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
                      help='Import only photos with tags matching pattern')
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
                      default='http://localhost:8000' + settings.SCRIPT_NAME,
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
