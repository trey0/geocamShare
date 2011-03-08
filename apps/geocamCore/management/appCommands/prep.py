# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

import logging
import os
from glob import glob

from django.core.management.base import NoArgsCommand

from geocamUtil.Builder import Builder
from geocamUtil.icons import svg, rotate
from geocamUtil.Installer import Installer

class Command(NoArgsCommand):
    help = 'Prep geocamDisasterStyle app'
    
    def handle_noargs(self, **options):
        up = os.path.dirname
        appDir = up(up(up(os.path.abspath(__file__))))
        builder = Builder()

        # rotate pngs
        rotGlob = '%s/build/media/geocamCore/icons/map/*Point.png' % appDir
        rotOutput = '%s/build/media/geocamCore/icons/mapr' % appDir
        logging.debug('rotateIcons %s %s' % (rotGlob, rotOutput))
        for imPath in glob(rotGlob):
            rotate.buildAllDirections(builder, imPath, outputDir=rotOutput)

        # link static stuff into build/media
        inst = Installer(builder)
        inst.installRecurseGlob('%s/static/*' % appDir,
                                '%s/build/media' % appDir)
