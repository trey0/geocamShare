# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.conf.urls.defaults import *
from django.contrib import admin

from geocamCore import settings

admin.autodiscover()

urlpatterns = patterns(
    '',
    
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^comments/', include('django.contrib.comments.urls')),
)

if settings.USE_STATIC_SERVE:
    urlpatterns += patterns(
        '',
        
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
         dict(document_root=settings.MEDIA_ROOT,
              show_indexes=True,
              readOnly=True)),
        (r'^favicon.ico$', 'django.views.generic.simple.redirect_to',
         {'url': settings.MEDIA_URL + 'geocamCore/icons/camera.ico',
          'readOnly': True}
         ),
        )
