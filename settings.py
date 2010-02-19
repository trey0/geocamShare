
import os

CHECKOUT_DIR = os.path.dirname(os.path.realpath(__file__))
os.environ['CHECKOUT_DIR'] = CHECKOUT_DIR

# inherit most settings from base_settings
from base_settings import *

# django settings overrides for shareGeocam
INSTALLED_APPS = INSTALLED_APPS + (
    'share2.shareGeocam',
    )

# non-django-related app settings
from share2.shareGeocam.settings import *

# settings for this server instance
from local_settings import *
