
# inherit some views from shareCore and override as needed
from share2.shareCore.views import *

from share2.shareGeocam.models import Photo

def getGalleryData(request, page):
    pager = Pager(baseUrl=request.build_absolute_uri('..').rstrip('/'),
                  items=Photo.objects.all(),
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

def getGalleryJsonText():
    return simplejson.dumps([p.getShortDict() for p in Photo.objects.all()],
                            separators=(',',':') # omit spaces
                            )

def galleryJson(request):
    return HttpResponse(getGalleryJsonText(), mimetype='application/json')

def galleryJsonJs(request):
    return render_to_response('galleryJson.js',
                              dict(galleryJsonText = getGalleryJsonText()),
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

