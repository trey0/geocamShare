
from base_urls import *

urltuple = urltuple + (
    ('', include('share2.shareGeocam.urls')),
)
urlpatterns = patterns('', *urltuple)
