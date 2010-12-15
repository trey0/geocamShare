# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.conf.urls.defaults import *

from base_urls import urlpatterns

from share2.shareCore.base_urls import urlpatterns as basePatterns
from share2.shareCore.urls import urlpatterns as corePatterns
from share2.shareGeocam.urls import urlpatterns as geocamPatterns

urlpatterns = (basePatterns
               + corePatterns
               + geocamPatterns
               + patterns(
    '',

    (r'^tracking/', include('share2.shareTracking.urls')),
))
