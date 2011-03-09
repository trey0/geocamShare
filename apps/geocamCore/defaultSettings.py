# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

GEOCAM_CORE_SITE_TITLE = 'GeoCam Share'

GEOCAM_CORE_DEFAULT_ICON = 'camera'

GEOCAM_CORE_LINE_STYLES = ('solid',)
GEOCAM_CORE_DEFAULT_LINE_STYLE = GEOCAM_CORE_LINE_STYLES[0]

GEOCAM_CORE_KML_FLY_TO_VIEW = True

GEOCAM_CORE_DELETE_TMP_FILE_WAIT_SECONDS = 60*60

GEOCAM_CORE_GALLERY_PAGE_COLS = 3
GEOCAM_CORE_GALLERY_PAGE_ROWS = 3

# for multiple thumbnails in sidebar gallery
GEOCAM_CORE_GALLERY_THUMB_SIZE = [160, 120]
# for single thumbnail in sidebar gallery
GEOCAM_CORE_DESC_THUMB_SIZE = [480, 360]

# GEOCAM_CORE_MAP_BACKEND possible values: 'earth', 'maps', 'none'.
GEOCAM_CORE_MAP_BACKEND = 'maps'

# enable/disable clustering of markers (if supported by the current GEOCAM_CORE_MAP_BACKEND)
GEOCAM_CORE_USE_MARKER_CLUSTERING = False

GEOCAM_CORE_USE_TRACKING = False
