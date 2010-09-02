# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

from django.db import models

from share2.shareCore.models import Image
from share2.shareCore.managers import LeafClassManager

class Photo(Image):
    objects = LeafClassManager(parentModel=Image)
