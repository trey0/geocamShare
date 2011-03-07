# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.db import models
from django.contrib.auth.models import User

class LatitudeProfile(models.Model):
    user = models.ForeignKey(User)
    oauthToken = models.CharField(max_length=200, blank=True)
    oauthSecret = models.CharField(max_length=200, blank=True)
    mtime = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'geocamTrack'
