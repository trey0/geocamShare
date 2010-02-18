# Django settings for gds project.

from base_settings import *

INSTALLED_APPS = INSTALLED_APPS + (
    'share2.shareGeocam',
    )

from local_settings import *
