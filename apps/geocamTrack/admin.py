# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.contrib import admin

from geocamTrack.models import *
from geocamTrack import settings

admin.site.register(Resource)
admin.site.register(ResourcePosition)
admin.site.register(PastResourcePosition)

if settings.GEOCAM_TRACK_LATITUDE_ENABLED:
    # register latitude-related models with admin
    from geocamTrack.latitude import admin
