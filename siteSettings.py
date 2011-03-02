# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

import os

from geocamShare.base_settings import *

# django settings overrides for shareGeocam
INSTALLED_APPS = INSTALLED_APPS + (
    'geocamShare.shareGeocam',
    )

MAIN_APP = 'geocamShare.shareGeocam'
