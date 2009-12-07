
from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # for debug only -- for production use Apache
    (r'^media/(?P<path>.*)$', 'django.views.static.serve',
     dict(document_root='/home/trey/projects/gds/sw/sandbox/share2/media', # settings.MEDIA_ROOT,
          show_indexes=True)),

    (r'^share/', include('share2.share.urls')),
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),

)
