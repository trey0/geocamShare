
from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urltuple = (
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^comments/', include('django.contrib.comments.urls')),
)

if settings.USE_STATIC_SERVE:
    urltuple += (
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
         dict(document_root=settings.MEDIA_ROOT,
              show_indexes=True)),
        )
