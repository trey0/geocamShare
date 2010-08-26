
from django.conf.urls.defaults import *
from django.conf import settings

from share2.shareGeocam.views import viewSingleton as views

urlpatterns = patterns(
    '',

    (r'^accounts/login/$', 'django.contrib.auth.views.login',
     {'loginRequired': False, # avoid redirect loop
      'sslRequired': True
      }),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout',
     {'loginRequired': False, # show logout page instead of redirecting to log in again
      'template_name': 'registration/logged_out.html'}),

    (r'^gallery/(?P<page>\d+)/$', views.gallery),
    (r'^gallery.json', views.galleryJson),
    (r'^galleryJson.js', views.galleryJsonJs),
    (r'^galleryDebug.html', views.galleryDebug),

    (r'^$', views.main),
    (r'^upload/(?P<userName>[^/]+)/$', views.uploadImage),

    (r'^track/upload/(?P<authorName>[^/]+)/$', views.uploadTrack),
    (r'^track/view/(?P<uuid>[^/]+)/?$', views.viewTrack),

    (r'^setVars(?:\?[^/]*)?$', views.setVars),

    (r'^kml/startSession.kml(?:\?[^/]*)?$', views.kmlStartSession),
    (r'^kml/([^/]+)/([^/]+)\.kml$', views.kmlGetSessionResponse,
     {'useDigestChallenge': True # google earth can use digest auth but not django standard auth
      }),

    )

if settings.USE_STATIC_SERVE:
    urlpatterns += patterns(
        (r'^data/(?P<path>.*)$', 'django.views.static.serve',
         dict(document_root=settings.PROCESSED_DIR,
              show_indexes=True)),
        )
