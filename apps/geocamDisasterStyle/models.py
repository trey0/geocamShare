# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.db import models

from geocamCore.models import Image
from geocamUtil.models.managers import FinalModelManager

class Photo(Image):
    objects = FinalModelManager(parentModel=Image)
