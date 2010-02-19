
from django.conf.urls.defaults import *
from django.conf import settings

from share2.shareGeocam import views

urlpatterns = patterns(
    '',

    (r'^gallery/(?P<page>\d+)/$', views.gallery),
    (r'^gallery.json$', views.galleryJson),
    (r'^galleryJson.js', views.galleryJsonJs),
    (r'^main/$', views.main),
    (r'^data.kml$', views.kml),

    )

if settings.USE_STATIC_SERVE:
    urlpatterns += patterns(
        (r'^data/(?P<path>.*)$', 'django.views.static.serve',
         dict(document_root=settings.PROCESSED_DIR,
              show_indexes=True)),
        )
