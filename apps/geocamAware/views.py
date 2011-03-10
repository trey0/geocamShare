# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

import urllib

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from geocamUtil import anyjson as json
from geocamUtil.middleware.SecurityMiddleware import requestIsSecure

from geocamAware import settings

def getExportSettings():
    exportedVars = ['SCRIPT_NAME',
                    'MEDIA_URL',
                    'DATA_URL',
                    'GEOCAM_CORE_GALLERY_THUMB_SIZE',
                    'GEOCAM_CORE_DESC_THUMB_SIZE',
                    'GEOCAM_AWARE_GALLERY_PAGE_COLS',
                    'GEOCAM_AWARE_GALLERY_PAGE_ROWS',
                    'GEOCAM_AWARE_MAP_BACKEND',
                    'GEOCAM_AWARE_USE_MARKER_CLUSTERING',
                    'GEOCAM_AWARE_USE_TRACKING']
    exportDict = dict(((f, getattr(settings, f))
                       for f in exportedVars))
    return json.dumps(exportDict)

def main(request):
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
                                   accountWidget=accountWidget,
                                   exportSettings=getExportSettings()),
                              context_instance=RequestContext(request))

def setVars(request):
    for var in ('v', 'q'):
        if var in request.GET:
            request.session[var] = request.GET[var]
    return HttpResponse('ok')
