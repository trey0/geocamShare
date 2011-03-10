# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.conf.urls.defaults import *

from geocamCore import settings

urlpatterns = patterns(
    '',

    # accounts
    (r'^accounts/login/$', 'django.contrib.auth.views.login',
     {'loginRequired': False, # avoid redirect loop
      }),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout',
     # show logout page instead of redirecting to log in again
     {'loginRequired': False}),

    )

if settings.USE_STATIC_SERVE:
    urlpatterns += patterns(
        '',
        
        (r'^data/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root':settings.DATA_DIR,
          'show_indexes':True,
          'readOnly': True}))
