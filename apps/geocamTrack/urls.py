# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.conf.urls.defaults import *

from geocamTrack import settings
from geocamTrack import views

urlpatterns = patterns(
    '',

    (r'^$', views.getIndex,
     {'readOnly': True}),

    (r'^resources.json$', views.getResourcesJson,
     {'readOnly': True}),
    (r'^icon/(\S+)', views.getIcon,
     {'readOnly': True}),
    (r'^liveMap/$', views.getLiveMap,
     {'readOnly': True}),
    (r'^liveMap.kml$', views.getKmlNetworkLink,
     {'readOnly': True,
      'challenge': 'digest' # Google Earth can't handle django challenge
      }),
    (r'^latest.kml$', views.getKmlLatest,
     {'readOnly': True,
      'challenge': 'digest' # Google Earth can't handle django challenge
      }),

    (r'^post/$', views.postPosition,
     {'challenge': 'digest' # for best support of future mobile apps
      }),

)

if settings.GEOCAM_TRACK_LATITUDE_ENABLED:
    # make latitude-related urls available
    urlpatterns += patterns([(r'^latitude/', include('geocamTrack.latitude.urls'))])
