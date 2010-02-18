
from django.conf.urls.defaults import *
from django.contrib import admin

from share2 import settings
from share2.shareCore import views

admin.autodiscover()

urlpatterns = patterns(
    '',
    (r'^comments/', include('django.contrib.comments.urls')),

    (r'^gallery/(?P<page>\d+)/$', views.gallery),
    (r'^gallery.json$', views.galleryJson),
    (r'^main/$', views.main),
    (r'^data.kml$', views.kml),

    )

if settings.USE_STATIC_SERVE:
    urlpatterns += patterns(
        (r'^data/(?P<path>.*)$', 'django.views.static.serve',
         dict(document_root=settings.PROCESSED_DIR,
              show_indexes=True)),
        )
