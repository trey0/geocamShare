# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

import re
from django.http import HttpResponse

def wrapKmlHttp(text):
    wrapped = wrapKml(text)
    return ("""HTTP/1.0 200 OK\r
Content-type: application/vnd.google-earth.kml+xml
Expires: -1

%s
""" % wrapped)

def wrapKmlDjango(text):
    return djangoResponse(wrapKml(text))

def djangoResponse(wrappedText):
    return HttpResponse(wrappedText, mimetype='application/vnd.google-earth.kml+xml')

def wrapKml(text, id=None):
    if id:
        text = re.sub('^<(\w+)>', '<\\1 id="%s">' % id, text)
    return ("""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://earth.google.com/kml/2.2">
  %s
</kml>
""" % text)

def wrapKmlDocument(text, id=None):
    if id:
        return wrapKml("""
  <Document id="%(id)s">
    <name>%(id)s</name>
    %(text)s
  </Document>
""" % dict(id=id, text=text))
    else:
        return wrapKml("""
  <Document>
    %s
  </Document>
""" % text)

