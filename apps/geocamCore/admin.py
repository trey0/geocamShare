# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.contrib import admin

from geocamCore.models import *

admin.site.register(Folder)
admin.site.register(Permission)
admin.site.register(Unit)
admin.site.register(Operation)
admin.site.register(Assignment)
admin.site.register(UserProfile)
admin.site.register(Sensor)
admin.site.register(Change)
