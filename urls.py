# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.conf.urls.defaults import *

from geocamShare.base_urls import urlpatterns as basePatterns
from geocamShare.shareCore.urls import urlpatterns as corePatterns
from geocamShare.shareGeocam.urls import urlpatterns as geocamPatterns

urlpatterns = (basePatterns
               + corePatterns
               + geocamPatterns
               + patterns(
    '',

    (r'^tracking/', include('geocamShare.shareTracking.urls')),
    (r'^latitude/', include('geocamShare.shareLatitude.urls')),
))
