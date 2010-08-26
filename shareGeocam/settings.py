
import os

from share2.base_settings import *

# django settings overrides for shareGeocam
INSTALLED_APPS = INSTALLED_APPS + (
    'share2.shareGeocam',
    )

######################################################################
# settings specific to share app, not Django-related
######################################################################

# nothing here yet
