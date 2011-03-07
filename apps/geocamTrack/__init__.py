# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

"""
geocamTrackWeb
"""

import django.conf

from geocamUtil.MultiSettings import MultiSettings
from geocamTrack import defaultSettings

__version_info__ = {
    'major': 0,
    'minor': 1,
    'micro': 0,
    'releaselevel': 'final',
    'serial': 1
}

def get_version():
    """
    Return the formatted version information
    """
    vers = ["%(major)i.%(minor)i" % __version_info__, ]
    
    if __version_info__['micro']:
        vers.append(".%(micro)i" % __version_info__)
    if __version_info__['releaselevel'] != 'final':
        vers.append('%(releaselevel)s%(serial)i' % __version_info__)
    return ''.join(vers)

__version__ = get_version()

settings = MultiSettings(django.conf.settings, defaultSettings)
