# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.conf.urls.defaults import *

from geocamShare.base_urls import urlpatterns as basePatterns
from geocamCore.urls import urlpatterns as corePatterns
from geocamDisasterStyle.urls import urlpatterns as geocamPatterns

urlpatterns = (basePatterns
               + corePatterns
               + geocamPatterns
               + patterns(
    '',

    (r'^geocamTrack/', include('geocamTrack.urls')),
))
