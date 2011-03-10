# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.conf.urls.defaults import *
from django.conf import settings

from geocamCore.baseUrls import urlpatterns as basePatterns
from geocamCore.urls import urlpatterns as corePatterns

urlpatterns = (basePatterns
               + corePatterns
               + patterns(
    '',

    (r'^geocamAware/', include('geocamAware.urls')),
    (r'^geocamLens/', include('geocamLens.urls')),
    (r'^geocamTrack/', include('geocamTrack.urls')),


    (r'^$', 'django.views.generic.simple.redirect_to',
     {'url': settings.SCRIPT_NAME + 'geocamAware/',
      'readOnly': True}
     ),
))
