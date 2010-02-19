
from base_urls import *

urltuple = urltuple + (
    (r'^share/', include('share2.shareGeocam.urls')),
)
urlpatterns = patterns('', *urltuple)
