# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.conf.urls.defaults import *
from django.conf import settings

from geocamShare.shareGeocam.views import viewSingleton as views

urlpatterns = patterns(
    '',

    (r'^photo/(?P<id>[^/]+)/(?:[^/]+)?$', views.viewPhoto,
     {'readOnly': True}),
    (r'^track/(?P<id>[^/]+)/(?:[^/]+)?$', views.viewTrack,
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

    (r'^edit/photo/(?P<uuid>[^/]+)/$', views.editImageWrapper),
    (r'^editWidget/photo/(?P<uuid>[^/]+)/$', views.editImage),

    # legacy URLs, compatible with the old version of GeoCam
    # Mobile *if* user authentication is off (not recommended!).
    (r'^upload/(?P<userName>[^/]+)/$', views.uploadImage),
    (r'^track/upload/(?P<authorName>[^/]+)/$', views.uploadTrack),

    )
