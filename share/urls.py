
from django.conf.urls.defaults import *
from django.contrib import admin

from share2.share import views

admin.autodiscover()

urlpatterns = patterns(
    '',
    (r'^comments/', include('django.contrib.comments.urls')),
    (r'^data/(?P<path>.*)$', 'django.views.static.serve',
     dict(document_root='/home/trey/projects/gds/sw/sandbox/processed',
          show_indexes=True)),

    (r'^gallery/(?P<page>\d+)/$', views.gallery),
    (r'^gallery.json$', views.galleryJson),
    (r'^main/$', views.main),
    (r'^data.kml$', views.kml),

    )
