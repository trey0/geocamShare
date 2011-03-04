# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

import os

from geocamShare.base_settings import *

USING_DJANGO_DEV_SERVER = ('runserver' in sys.argv)

ADMINS = (
    ('Trey Smith', 'info@geocamshare.org'),
)
MANAGERS = ADMINS

# django settings overrides for geocamDisasterSkin
INSTALLED_APPS = INSTALLED_APPS + (
    'geocamDisasterSkin',
    )

MAIN_APP = 'geocamDisasterSkin'
