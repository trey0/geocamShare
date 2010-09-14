# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

# Create your views here.

import math
import sys
import datetime
import os
import shutil
import urllib
import tempfile
import shutil

import PIL.Image
import tagging
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.utils.safestring import mark_safe
from django.template import RequestContext
try:
    import json
except ImportError:
    from django.utils import simplejson as json
from django.conf import settings
from django.contrib.auth.models import User

from share2.shareCore.utils import makeUuid, mkdirP, Xmp
from share2.shareCore.Pager import Pager
from share2.shareCore.models import Image, Track, EmptyTrackError
from share2.shareCore.forms import UploadImageForm, UploadTrackForm
from share2.shareCore.utils.icons import cacheIconSize
from share2.shareCore.kml.ViewKml import ViewKml
from share2.shareCore.middleware import requestIsSecure

cacheIconSize(os.path.join(settings.MEDIA_ROOT, 'share', 'map'))
cacheIconSize(os.path.join(settings.MEDIA_ROOT, 'share', 'mapr'))

class ViewCore(ViewKml):
    # override in derived classes
    search = None
    uploadImageModel = None

    def getMatchingFeaturesForQuery(self, query):
        features = self.search.getAllFeatures()
        if query:
            features = self.search.searchFeatures(features, query)
        return features

    def getMatchingFeatures(self, request):
        query = request.REQUEST.get('q', '')
        return self.getMatchingFeaturesForQuery(query)

    def getGalleryData(self, request, page):
        pager = Pager(baseUrl=request.build_absolute_uri('..').rstrip('/'),
                      items=self.getMatchingFeatures(request),
                      pageSize=settings.GALLERY_PAGE_ROWS*settings.GALLERY_PAGE_COLS,
                      pageNum=int(page))
        pageData = pager.slice()
        for i, item in enumerate(pageData):
            item.row = i // settings.GALLERY_PAGE_COLS
        return pager, pageData

    def gallery(self, request, page):
        pager, pageData = self.getGalleryData(request, page)
        return render_to_response('gallery.html',
                                  dict(pager = pager,
                                       data = pageData),
                                  context_instance=RequestContext(request))
    
    def getGalleryJsonText(self, request):
        obj = [f.getShortDict() for f in self.getMatchingFeatures(request)]
        if 1:
            return json.dumps(obj, indent=4, sort_keys=True) # pretty print for debugging
        else:
            return json.dumps(obj, separators=(',',':')) # compact

    def galleryJson(self, request):
        return HttpResponse(self.getGalleryJsonText(request), mimetype='application/json')

    def galleryJsonJs(self, request):
        return render_to_response('galleryJson.js',
                                  dict(galleryJsonText=self.getGalleryJsonText(request)),
                                  mimetype='text/javascript')

    def galleryDebug(self, request):
        return HttpResponse('<body><pre>%s</pre></body>' % self.getGalleryJsonText(request))

    def main(self, request):
        if request.user.is_authenticated():
            accountWidget = ('<b>%(username)s</b> <a href="%(SCRIPT_NAME)saccounts/logout/">logout</a>'
                             % dict(username=request.user.username,
                                    SCRIPT_NAME=settings.SCRIPT_NAME))
        else:
            path = request.get_full_path()
            if not requestIsSecure(request):
                path += '?protocol=http' # redirect back to http after login
            accountWidget = ('<b>guest</b> <a href="%(SCRIPT_NAME)saccounts/login/?next=%(path)s">login</a>'
                             % dict(SCRIPT_NAME=settings.SCRIPT_NAME,
                                    path=urllib.quote(path)))
        return render_to_response('main.html',
                                  dict(query=request.session.get('q', ''),
                                       viewport=request.session.get('v', ''),
                                       accountWidget=accountWidget),
                                  context_instance=RequestContext(request))

    def uploadImageAuth(self, request):
        return self.uploadImage(request, request.user.username)

    def uploadImage(self, request, userName):
        author = User.objects.get(username=userName)
        if request.method == 'POST':
            print >>sys.stderr, 'upload image start'
            form = UploadImageForm(request.POST, request.FILES)
            print >>sys.stderr, 'FILES:', request.FILES.keys()
            if form.is_valid():
                incoming = request.FILES['photo']

                # store image data in temp file
                fd, tempStorePath = tempfile.mkstemp('-uploadImage.jpg')
                os.close(fd)
                storeFile = file(tempStorePath, 'wb')
                for chunk in incoming.chunks():
                    storeFile.write(chunk)
                storeFile.close()
                print >>sys.stderr, 'upload: saved image data to temp file:', tempStorePath

                # create image db record
                uuid = form.cleaned_data['uuid'] or makeUuid()
                uuidMatches = self.uploadImageModel.objects.filter(uuid=uuid)
                sameUuid = (uuidMatches.count() > 0)
                if sameUuid:
                    # if the incoming uuid matches an existing uuid, this is
                    # either (1) a duplicate upload of the same image or (2)
                    # the next higher resolution level in an incremental
                    # upload.
                    img = uuidMatches.get()
                    print >>sys.stderr, 'upload: photo %s with same uuid %s posted' % (img.name, img.uuid)
                    newVersion = img.version + 1
                else:
                    # create Image db record
                    img = self.uploadImageModel(status=settings.STATUS_PENDING,
                                                version=0
                                                )

                    # defaults
                    timestamp = datetime.datetime.now()
                    vals = dict(minTime=timestamp,
                                maxTime=timestamp)

                    # extract fields from exif or xmp headers
                    xmp = Xmp(tempStorePath)
                    xmpVals = xmp.getDict()
                    print >>sys.stderr, 'upload: exif/xmp data:', xmpVals
                    vals.update(xmpVals)
                    
                    # extract fields from http post
                    lat = Xmp.checkMissing(form.cleaned_data['latitude'])
                    lon = Xmp.checkMissing(form.cleaned_data['longitude'])
                    timestamp = form.cleaned_data['cameraTime']
                    yaw, yawRef = Xmp.normalizeYaw(form.cleaned_data['yaw'],
                                                   form.cleaned_data['yawRef'])
                    httpVals0 = dict(name=incoming.name,
                                     author=author,
                                     notes=form.cleaned_data['notes'],
                                     tags=form.cleaned_data['tags'],
                                     uuid=uuid,
                                     minLat=lat,
                                     maxLat=lat,
                                     minLon=lon,
                                     maxLon=lon,
                                     minTime=timestamp,
                                     maxTime=timestamp,
                                     yaw=yaw,
                                     yawRef=yawRef)
                    httpVals = dict([(k, v) for k, v in httpVals0.iteritems()
                                     if Xmp.checkMissing(v) != None])
                    print >>sys.stderr, 'upload: form data:', httpVals
                    vals.update(httpVals)

                    # post process some fields
                    icon = settings.ICONS[0] # default
                    tags = tagging.utils.parse_tag_input(vals['tags'])
                    for t in tags:
                        if t in settings.ICONS_DICT:
                            icon = t
                            break
                    vals['icon'] = icon

                    # copy extracted fields to img
                    for k, v in vals.iteritems():
                        setattr(img, k, v)

                    # set version
                    newVersion = 0

                # move the image data to its permanent location
                storePath = img.getImagePath(version=newVersion)
                storeDir = os.path.dirname(storePath)
                mkdirP(storeDir)
                shutil.move(tempStorePath, storePath)
                print >>sys.stderr, 'upload: moved image data to:', storePath

                # check the new image file on disk to get the dimensions
                im = PIL.Image.open(storePath, 'r')
                newRes = im.size
                del im
                    
                if sameUuid:
                    oldRes = (img.widthPixels, img.heightPixels)
                    if newRes > oldRes:
                        print >>sys.stderr, 'upload: resolution increased from %d to %d' % (oldRes[0], newRes[0])
                        img.widthPixels, img.heightPixels = newRes
                        img.processed = False
                    else:
                        print >>sys.stderr, 'upload: ignoring dupe, but telling the client it was received so it stops trying'
                        # delete dupe data
                        shutil.rmtree(storeDir)
                else:
                    img.widthPixels, img.heightPixels = newRes

                if not img.processed:
                    # generate thumbnails and any other processing
                    # (better to do this part in the background, but we
                    # don't have that set up yet)
                    img.version = newVersion
                    img.process()
                    img.save()

                print >>sys.stderr, 'upload image end'

                # swfupload requires non-empty response text.
                # also added a text pattern (in html comment) for clients to check against to make sure
                # photo has actually arrived in share.  we also put a matching line in the error log so we
                # never again run into the issue that the phone thinks it successfully uploaded but there
                # is no record of the http post on the server.
                print >>sys.stderr, 'GEOCAM_SHARE_POSTED %s' % img.name
                return HttpResponse('file posted <!--\nGEOCAM_SHARE_POSTED %s\n-->' % img.name)

            else:
                print >>sys.stderr, "form is invalid"
                print >>sys.stderr, "form errors: ", form._errors
                userAgent = request.META.get('HTTP_USER_AGENT', '')
                # swfupload user can't see errors in form response, best return an error code
                if 'Flash' in userAgent:
                    return http.HttpResponseBadRequest('<h1>400 Bad Request</h1>')
        else:
            form = UploadImageForm()
            #print 'form:', form
        resp = render_to_response('upload.html',
                                  dict(form=form,
                                       author=author,
                                       ),
                                  context_instance=RequestContext(request))
        print >>sys.stderr, 'upload image end'
        return resp

    def uploadTrackAuth(self, request):
        return self.uploadTrack(request, request.user.username)

    def uploadTrack(self, request, authorName):
        author = User.objects.get(username=authorName)
        if request.method == 'POST':
            print >>sys.stderr, 'upload track start'
            form = UploadTrackForm(request.POST, request.FILES)
            print >>sys.stderr, 'FILES:', request.FILES.keys()
            if form.is_valid():
                uuid = form.cleaned_data['uuid'] or makeUuid()
                if Track.objects.filter(uuid=uuid).count():
                    print >>sys.stderr, 'upload: track with same uuid %s posted' % img.uuid
                    print >>sys.stderr, 'upload: ignoring dupe, but telling the client it was received so it stops trying'
                else:
                    track = form.save(commit=False)
                    track.uuid = uuid
                    track.gpx = request.FILES['gpxFile'].read()
                    track.author = author
                    if track.icon == '':
                        track.icon = Track._meta.get_field('icon').default
                    try:
                        track.process()
                    except EmptyTrackError:
                        print >>sys.stderr, 'upload: ignoring empty track, but telling the client it was received so it stops trying'
                    else:
                        track.save()

                # return a pattern for clients to check for to ensure
                # the data was actually posted.  in bad network conditions
                # we've seen clients get back bogus empty '200 ok' responses
                # so this check is important to make sure they keep trying.
                posted = 'GEOCAM_SHARE_POSTED %s' % track.uuid
                print >>sys.stderr, posted
                continueUrl = form.cleaned_data['referrer'] or settings.SCRIPT_NAME
                result = render_to_response('trackUploadDone.html',
                                            dict(posted=posted,
                                                 continueUrl=continueUrl),
                                            context_instance=RequestContext(request))
                print >>sys.stderr, 'upload track end'
                return result
            else:
                print >>sys.stderr, "form errors: ", form._errors
                userAgent = request.META.get('HTTP_USER_AGENT', '')
                # swfupload user can't see errors in form response, best return an error code
                if 'Flash' in userAgent:
                    return http.HttpResponseBadRequest('<h1>400 Bad Request</h1>')
        else:
            form = UploadTrackForm(initial=dict(referrer=request.META.get('HTTP_REFERER'),
                                                uuid=''))
            #print 'form:', form
        resp = render_to_response('trackUpload.html',
                                  dict(form=form,
                                       authorName=authorName),
                                  context_instance=RequestContext(request))
        print >>sys.stderr, 'upload image end'
        return resp

    def viewTrack(self, request, uuid, version):
        track = Track.objects.get(uuid=uuid)
        return HttpResponse(track.json, mimetype='application/json')

    def viewPhoto(self, request, uuid, version):
        # this is not very efficient
        img = Image.objects.get(uuid=uuid)
        imgData = file(img.getImagePath(), 'r').read()
        return HttpResponse(imgData, mimetype='image/jpeg')

    def setVars(self, request):
        for var in ('v', 'q'):
            if var in request.GET:
                request.session[var] = request.GET[var]
        return HttpResponse('ok')
