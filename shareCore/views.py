# Create your views here.

import math
import sys
import datetime
import os
import shutil

import PIL.Image
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

from share2.shareCore.utils import makeUuid, mkdirP
from share2.shareCore.Pager import Pager
from share2.shareCore.models import Image, Track
from share2.shareCore.forms import UploadImageForm, UploadTrackForm

class ViewCore:
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
        features = [f.asLeafClass() for f in self.getMatchingFeatures(request)]
        return json.dumps([f.getShortDict() for f in features],
                          separators=(',',':') # omit spaces
                          )

    def galleryJson(self, request):
        return HttpResponse(self.getGalleryJsonText(request), mimetype='application/json')

    def galleryJsonJs(self, request):
        return render_to_response('galleryJson.js',
                                  dict(galleryJsonText = self.getGalleryJsonText(request)),
                                  mimetype='application/json')

    def main(self, request):
        pager, pageData = self.getGalleryData(request, '1')
        return render_to_response('main.html',
                                  dict(pager = pager,
                                       data = pageData),
                                  context_instance=RequestContext(request))

    def kml(request):
        kml = self.getKml(request)
        return HttpResponse(kml, mimetype='application/vnd.google-earth.kml+xml')

    def checkMissing(self, num):
        if num in (0, -999):
            return None
        else:
            return num

    def uploadImage(self, request, userName):
        owner = User.objects.get(username=userName)
        if request.method == 'POST':
            print >>sys.stderr, 'upload image start'
            form = UploadImageForm(request.POST, request.FILES)
            print >>sys.stderr, 'FILES:', request.FILES.keys()
            if form.is_valid():
                incoming = request.FILES['photo']
                uuid = form.cleaned_data['uuid'] or makeUuid()
                uuidMatches = Image.objects.filter(uuid=uuid)
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
                    # create Image db record and fill in most fields
                    lat = self.checkMissing(form.cleaned_data['latitude'])
                    lon = self.checkMissing(form.cleaned_data['longitude'])
                    timestamp = form.cleaned_data['cameraTime'] or datetime.datetime.now()
                    img = Image(name=incoming.name,
                                owner=owner,
                                minTime=timestamp,
                                maxTime=timestamp,
                                minLat=lat,
                                minLon=lon,
                                maxLat=lat,
                                maxLon=lon,
                                yaw=self.checkMissing(form.cleaned_data['yaw']),
                                notes=form.cleaned_data['notes'],
                                tags=form.cleaned_data['tags'],
                                uuid=uuid,
                                status=settings.STATUS_PENDING,
                                version=0
                                )
                    newVersion = 0

                # store the image data on disk
                storePath = img.getImagePath(version=newVersion)
                storeDir = os.path.dirname(storePath)
                mkdirP(storeDir)
                storeFile = file(storePath, 'wb')
                for chunk in incoming.chunks():
                    storeFile.write(chunk)
                storeFile.close()
                print >>sys.stderr, 'upload: saved image data to:', storePath

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
                        print >>sys.stderr, 'upload: ignoring dupe, but telling the client it worked so it stops trying'
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
                                       owner=owner,
                                       ),
                                  context_instance=RequestContext(request))
        print >>sys.stderr, 'upload image end'
        return resp

    def uploadTrack(self, request, authorName):
        owner = User.objects.get(username=authorName)
        if request.method == 'POST':
            print >>sys.stderr, 'upload track start'
            form = UploadTrackForm(request.POST, request.FILES)
            print >>sys.stderr, 'FILES:', request.FILES.keys()
            if form.is_valid():
                uuid = form.cleaned_data['uuid'] or makeUuid()
                if Track.objects.filter(uuid=uuid).count():
                    print >>sys.stderr, 'upload: track with same uuid %s posted' % img.uuid
                    print >>sys.stderr, 'upload: ignoring dupe, but telling the client it worked so it stops trying'
                else:
                    track = form.save(commit=False)
                    track.uuid = uuid
                    track.gpx = request.FILES['gpxFile'].read()
                    track.owner = owner
                    track.process()
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

    def viewTrack(self, request, uuid):
        track = Track.objects.get(uuid=uuid)
        return HttpResponse(track.json, mimetype='application/json')

