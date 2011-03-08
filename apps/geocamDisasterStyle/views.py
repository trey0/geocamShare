# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

import os

from geocamCore.views import ViewCore
from geocamUtil.icons import cacheIcons

from geocamDisasterStyle.models import Photo
from geocamDisasterStyle.search import SearchGeocam
from geocamDisasterStyle import settings

cacheIcons(os.path.join(settings.MEDIA_ROOT, 'geocamDisasterStyle', 'icons', 'map'))
cacheIcons(os.path.join(settings.MEDIA_ROOT, 'geocamDisasterStyle', 'icons', 'mapr'))

class ViewGeocam(ViewCore):
    search = SearchGeocam()
    defaultImageModel = Photo

viewSingleton = ViewGeocam()
