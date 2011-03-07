# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.conf.urls.defaults import *

import views

urlpatterns = patterns(
    '',

    (r'^$', views.getIndex,
     {'readOnly': True}),

    (r'^signup/$', views.signup),

    (r'^signup2/$', views.signup2),

    (r'^signupCallback/$', views.signupCallback),

    (r'^currentPosition/$', views.currentPosition,
     {'readOnly': True}),

    (r'^locationList/$', views.locationList,
     {'readOnly': True}),

)
