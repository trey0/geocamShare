# Create your views here.

import math
import sys
import datetime
import os

import PIL.Image
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.utils.safestring import mark_safe
from django.template import RequestContext
from django.utils import simplejson
from django.conf import settings
from django.contrib.auth.models import User

from share2.shareCore.utils import makeUuid, mkdirP
from share2.shareCore.Pager import Pager
from share2.shareCore.models import Image
from share2.shareCore.forms import UploadFileForm

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
        return simplejson.dumps([f.getShortDict() for f in features],
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
            form = UploadFileForm(request.POST, request.FILES)
            print >>sys.stderr, 'FILES:', request.FILES.keys()
            if form.is_valid():
                # create Image db record and fill in most fields
                incoming = request.FILES['photo']
                lat = self.checkMissing(form.cleaned_data['latitude'])
                lon = self.checkMissing(form.cleaned_data['longitude'])
                img = Image(name=incoming.name,
                            owner=owner,
                            timestamp=form.cleaned_data['cameraTime'] or datetime.datetime.now(),
                            minLat=lat,
                            minLon=lon,
                            maxLat=lat,
                            maxLon=lon,
                            yaw=self.checkMissing(form.cleaned_data['yaw']),
                            notes=form.cleaned_data['notes'],
                            tags=form.cleaned_data['tags'],
                            uuid=form.cleaned_data['uuid'] or makeUuid(),
                            status=settings.STATUS_PENDING,
                            version=0, # FIX!
                            )

                # save the image data
                storePath = img.getImagePath()
                storeDir = os.path.dirname(storePath)
                mkdirP(storeDir)
                storeFile = file(storePath, 'wb')
                for chunk in incoming.chunks():
                    storeFile.write(chunk)
                storeFile.close()
                print >>sys.stderr, 'saved image data to:', storePath

                # access the image file on disk to fill in the dimensions
                # and save
                im = PIL.Image.open(storePath, 'r')
                img.widthPixels, img.heightPixels = im.size
                del im
                img.save()

                # generate thumbnails and any other processing (better to
                # do this part in the background, but not set up yet)
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
            form = UploadFileForm()
            #print 'form:', form
        resp = render_to_response('upload.html',
                                  dict(form=form,
                                       owner=owner,
                                       ),
                                  context_instance=RequestContext(request))
        print >>sys.stderr, 'upload photo end'
        return resp

