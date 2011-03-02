# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from geocamShare.shareCore.views import ViewCore
from geocamShare.shareGeocam.models import Photo
from geocamShare.shareGeocam.search import SearchGeocam

class ViewGeocam(ViewCore):
    search = SearchGeocam()
    defaultImageModel = Photo

viewSingleton = ViewGeocam()
