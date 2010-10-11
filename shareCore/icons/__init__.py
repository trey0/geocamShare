# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

import os
from glob import glob

from PIL import Image

ICON_SIZE_CACHE = {}

def cacheIconSize(dir):
    paths = glob('%s/*' % dir)
    for p in paths:
        iconPrefix = os.path.splitext(os.path.basename(p))[0]
        im = Image.open(p)
        ICON_SIZE_CACHE[iconPrefix] = list(im.size)

def getIconSize(iconPrefix):
    return ICON_SIZE_CACHE[iconPrefix]

# for export
import rotate
import svg
