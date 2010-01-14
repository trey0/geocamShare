# Create your views here.

import math
import sys

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.utils.safestring import mark_safe
from django.template import RequestContext
from django.utils import simplejson
from django.conf import settings

from share2.share.models import TaskData, ALL_TASKS_DICT

class Pager:
    def __init__(self, baseUrl, items, pageSize, pageNum):
        self.baseUrl = baseUrl
        self.items = items
        self.pageSize = pageSize
        self.pageNum = pageNum
        self.numPages = math.ceil(float(len(items)) / pageSize)
    def slice(self):
        return self.items[(self.pageSize*(self.pageNum-1)):(self.pageSize*self.pageNum)]
    def pager(self):
        ret = []
        if self.pageNum > 1:
            ret.append('<a href="%s/%d/">&lt;&lt;</a>' % (self.baseUrl, self.pageNum-1))
            ret.append('<a href="%s/1/">1</a>' % (self.baseUrl))
        if self.pageNum > 2:
            if self.pageNum > 3:
                ret.append('...')
            ret.append('<a href="%s/%d/">%d</a>' % (self.baseUrl, self.pageNum-1, self.pageNum-1))
        if self.numPages > 1:
            ret.append('%d' % self.pageNum)
        if self.pageNum < self.numPages-1:
            ret.append('<a href="%s/%d/">%d</a>' % (self.baseUrl, self.pageNum+1, self.pageNum+1))
            if self.pageNum < self.numPages-2:
                ret.append('...')
        if self.pageNum < self.numPages:
            ret.append('<a href="%s/%d/">%d</a>' % (self.baseUrl, self.numPages, self.numPages))
            ret.append('<a href="%s/%d/">&gt;&gt;</a>' % (self.baseUrl, self.pageNum+1))
        if ret:
            return mark_safe('pages:&nbsp;' + '&nbsp;'.join(ret))
        else:
            return ''

def getGalleryData(request, page):
    pager = Pager(baseUrl=request.build_absolute_uri('..').rstrip('/'),
                  items=TaskData.objects.all(),
                  pageSize=settings.GALLERY_PAGE_ROWS*settings.GALLERY_PAGE_COLS,
                  pageNum=int(page))
    pageData = pager.slice()
    for i, item in enumerate(pageData):
        item.row = i // settings.GALLERY_PAGE_COLS
    return pager, pageData

def getKml(request):
    kml = """
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
""".lstrip()
    for dptype in ALL_TASKS_DICT.values():
        for dp in dptype.objects.all():
            kml += dp.getPlacemark(request)
    kml += """
  </Document>
</kml>"""
    return kml

def gallery(request, page):
    pager, pageData = getGalleryData(request, page)
    return render_to_response('gallery.html',
                              dict(pager = pager,
                                   data = pageData),
                              context_instance=RequestContext(request))

def galleryJson(request):
    return HttpResponse(simplejson.dumps([p.getShortDict() for p in TaskData.objects.all()],
                                         separators=(',',':') # omit spaces
                                         ),
                        mimetype='application/json')

def main(request):
    pager, pageData = getGalleryData(request, '1')
    print >>sys.stderr, request
    import os
    print >>sys.stderr, os.environ
    return render_to_response('main.html',
                              dict(pager = pager,
                                   data = pageData),
                              context_instance=RequestContext(request))

def kml(request):
    kml = getKml(request)
    return HttpResponse(kml, mimetype='application/vnd.google-earth.kml+xml')
