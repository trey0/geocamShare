# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.conf.urls.defaults import *
from django.conf import settings

import views

urlpatterns = patterns(
    '',

    (r'^resources.json$', views.getResourcesJson),
    (r'^post/$', views.postPosition),
    (r'^liveMap/$', views.getLiveMap),

    )
