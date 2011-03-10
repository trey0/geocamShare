# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

import urllib
import datetime
import sys

from geocamUtil import KmlUtil
from geocamCore.models import Feature

from geocamLens.models import GoogleEarthSession
from geocamLens import settings

class BogusRequest:
    def build_absolute_uri(self, text):
        return text

class ViewKml(object):
    def kmlGetStartSessionKml(self, request, sessionId):
        quotedId = urllib.quote_plus(sessionId)
        absUrl = request.build_absolute_uri('%skml/%s/initial.kml' % (settings.SCRIPT_NAME, quotedId))
        if settings.GEOCAM_LENS_KML_FLY_TO_VIEW:
            flyToView = '<flyToView>1</flyToView>'
        else:
            flyToView = ''
        return ("""
<NetworkLink>
  <name>%(GEOCAM_CORE_SITE_TITLE)s</name>
  <Link>
    <href>%(absUrl)s</href>
  </Link>
  %(flyToView)s
</NetworkLink>
""" % dict(GEOCAM_CORE_SITE_TITLE=settings.GEOCAM_CORE_SITE_TITLE,
           absUrl=absUrl,
           flyToView=flyToView))

    def kmlStartSession(self, request):
        searchQuery = request.REQUEST.get('q', None)
        sessionId = GoogleEarthSession.getSessionId(searchQuery)
        print >>sys.stderr, "ViewKml: started session %s" % sessionId
        return KmlUtil.wrapKmlDjango(self.kmlGetStartSessionKml(request, sessionId))

    def kmlGetAllFeaturesFolder(self, request, searchQuery, newUtime):
        features = self.search.searchFeatures(Feature.objects.all(), searchQuery)
        if 0:
            # FIX: update models so this filtering statement can work
            features = features.filter(mtime__lte=newUtime,
                                       deleted=False)
        featuresKml = '\n'.join([f.getKml(request) for f in features])
        return ("""
<Folder id="allFeatures">
  <name>All features</name>
  %s
</Folder>
""" % featuresKml)

    def kmlGetInitialKml(self, request, sessionId):
        newUtime = datetime.datetime.now()
        session, created = GoogleEarthSession.objects.get_or_create(sessionId=sessionId,
                                                                    defaults=dict(utime=newUtime))
        session.utime = newUtime
        session.save()

        allFeaturesFolder = self.kmlGetAllFeaturesFolder(request,
                                                         session.getSearchQuery(),
                                                         newUtime)
        quotedId = urllib.quote_plus(sessionId)
        updateUrl = request.build_absolute_uri('%skml/%s/update.kml' % (settings.SCRIPT_NAME, quotedId))
        return ("""
<Document id="allFeatures">
  <name>%(GEOCAM_CORE_SITE_TITLE)s</name>

  <NetworkLink>
    <name>Update</name>
    <Link>
      <href>%(updateUrl)s</href>
      <refreshMode>onInterval</refreshMode>
      <refreshInterval>30</refreshInterval>
    </Link>
  </NetworkLink>

  %(allFeaturesFolder)s

</Document>
""" % dict(GEOCAM_CORE_SITE_TITLE=settings.GEOCAM_CORE_SITE_TITLE,
           updateUrl=updateUrl,
           allFeaturesFolder=allFeaturesFolder))
    
    def kmlGetUpdateKml(self, request, sessionId):
        # FIX: implement me -- can use old version of geocam for reference
        return ''

    def kmlGetSessionResponse(self, request, quotedId, method):
        sessionId = urllib.unquote_plus(quotedId)
        #print 'sessionId:', sessionId
        #print 'method:', method
        if method == 'initial':
            return KmlUtil.wrapKmlDjango(self.kmlGetInitialKml(request, sessionId))
        elif method == 'update':
            return KmlUtil.wrapKmlDjango(self.kmlGetUpdateKml(request, sessionId))
        else:
            raise Exception('method must be "initial" or "update"')
