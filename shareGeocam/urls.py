# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.conf.urls.defaults import *
from django.conf import settings

from share2.shareGeocam.views import viewSingleton as views

urlpatterns = patterns(
    '',

    (r'^accounts/login/$', 'django.contrib.auth.views.login',
     {'loginRequired': False, # avoid redirect loop
      }),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout',
     # show logout page instead of redirecting to log in again
     {'loginRequired': False}),

    (r'^features.json', views.featuresJson, {'readOnly': True}),
    (r'^featuresJson.js', views.featuresJsonJs, {'readOnly': True}),
    (r'^galleryDebug.html', views.galleryDebug, {'readOnly': True}),

    (r'^$', views.main, {'readOnly': True}),

    (r'^photo/(?P<uuid>[^/]+)/(?P<version>[\d+])/(?:[^/]+)$', views.viewPhoto,
     {'readOnly': True}),
    (r'^track/(?P<uuid>[^/]+)/(?P<version>[\d+])/(?:[^/]+)$', views.viewTrack,
     {'readOnly': True}),

    (r'^upload/$', views.uploadImageAuth),
    # alternate URL that accepts http basic authentication, used by newer versions of GeoCam Mobile
    (r'^upload-m/$', views.uploadImageAuth,
     {'challenge': 'basic'}),

    (r'^track/upload/$', views.uploadTrackAuth),
    # alternate URL that accepts http basic authentication, used by newer versions of GeoCam Mobile
    (r'^track/upload-m/$', views.uploadTrackAuth,
     {'challenge': 'basic'}),

    (r'^track/view/(?P<uuid>[^/]+)/?$', views.viewTrack, {'readOnly': True}),

    (r'^setVars(?:\?[^/]*)?$', views.setVars, {'readOnly': True}),

    (r'^kml/startSession.kml(?:\?[^/]*)?$', views.kmlStartSession,
     {'readOnly': True}),
    (r'^kml/([^/]+)/([^/]+)\.kml$', views.kmlGetSessionResponse,
     # google earth can't handle django challenge
     {'challenge': 'digest',
      'readOnly': True}),

    (r'^edit/photo/(?P<uuid>[^/]+)/$', views.editImageWrapper),
    (r'^editWidget/photo/(?P<uuid>[^/]+)/$', views.editImage),

    # legacy URLs, compatible with the old version of GeoCam
    # Mobile *if* user authentication is off (not recommended!).
    (r'^upload/(?P<userName>[^/]+)/$', views.uploadImage),
    (r'^track/upload/(?P<authorName>[^/]+)/$', views.uploadTrack),

    )

if settings.USE_STATIC_SERVE:
    urlpatterns += patterns('',
        (r'^data/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root':settings.DATA_DIR,
          'show_indexes':True,
          'readOnly': True}),
        (r'^favicon.ico$', 'django.views.generic.simple.redirect_to',
         {'url': settings.MEDIA_URL + 'share/camera.ico',
          'readOnly': True}
         ),
        )
