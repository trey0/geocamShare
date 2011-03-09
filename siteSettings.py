# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

import os

from geocamCore.baseSettings import *

USING_DJANGO_DEV_SERVER = ('runserver' in sys.argv)

ADMINS = (
    ('Trey Smith', 'info@geocamshare.org'),
)
MANAGERS = ADMINS

# django settings overrides for geocamDisasterStyle
INSTALLED_APPS = INSTALLED_APPS + (
    'geocamDisasterStyle',
    'geocamTrack',
    )

MAIN_APP = 'geocamDisasterStyle'

ROOT_URLCONF = 'geocamShare.urls'

# DIGEST_* -- settings for django_digest HTTP digest authentication
DIGEST_REALM = 'geocamshare.org'
