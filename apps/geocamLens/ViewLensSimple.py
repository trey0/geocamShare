# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

import os

from geocamUtil.icons import cacheIcons

from geocamLens.ViewLensAbstract import ViewLensAbstract
from geocamLens.models import Photo
from geocamLens.SearchSimple import SearchSimple
from geocamLens import settings

class ViewLensSimple(ViewLensAbstract):
    search = SearchSimple()
    defaultImageModel = Photo

viewSingleton = ViewLensSimple()
