# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

import os
import re
import sys
from glob import glob

# can override CHECKOUT_DIR by setting the environment variable before
# importing base_settings
DEFAULT_CHECKOUT_DIR = os.path.dirname(os.path.realpath(__file__))
CHECKOUT_DIR = os.environ.get('CHECKOUT_DIR', DEFAULT_CHECKOUT_DIR)

SCRIPT_NAME = os.environ['DJANGO_SCRIPT_NAME']
if not SCRIPT_NAME.endswith('/'):
    SCRIPT_NAME += '/'

USING_DJANGO_DEV_SERVER = ('runserver' in sys.argv)

if USING_DJANGO_DEV_SERVER:
    # django dev server deployment won't work with other SCRIPT_NAME settings
    SCRIPT_NAME = '/'

DEBUG = USING_DJANGO_DEV_SERVER
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'sqlite3',
        'NAME': '%s/sqlite3.db' % CHECKOUT_DIR,
    }
}

#DATABASE_ENGINE = 'sqlite3'
#DATABASE_NAME = '%s/sqlite3.db' % CHECKOUT_DIR
#DATABASE_USER = ''             # Not used with sqlite3.
#DATABASE_PASSWORD = ''         # Not used with sqlite3.
#DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
#DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Los_Angeles'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = '%s/build/media/' % CHECKOUT_DIR

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = SCRIPT_NAME + 'media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.  Must not be the same as MEDIA_URL!
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = SCRIPT_NAME + 'media/admin/'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    "geocamCore.context_processors.serverRoot",
    "geocamCore.context_processors.settings",
)

MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
#    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'geocamCore.middleware.SecurityRedirectMiddleware',
    'geocamCore.middleware.LogErrorsMiddleware',
)

ROOT_URLCONF = 'geocamShare.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'geocamCore',
    'geocamTrack',
    'geocamLatitude',
    'geocamUtil',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.comments',
    'tagging',
    'django_digest',
)

AUTH_PROFILE_MODULE = 'geocamCore.UserProfile'

LOGIN_URL = SCRIPT_NAME + 'accounts/login/'

CACHE_BACKEND = 'locmem://?timeout=30'

# time out sessions after 30 minutes of inactivity
SESSION_COOKIE_AGE = 30*60
SESSION_SAVE_EVERY_REQUEST = True

# DIGEST_* -- settings for django_digest HTTP digest authentication

DIGEST_REALM = 'geocamshare.org'

# Nonce count is a security feature that makes replay attacks more
# difficult.  However, it apparently causes problems when browsers with
# cached credentials make several simultaneous connections to the
# server, so it's recommended to turn it off.
# See http://bitbucket.org/akoha/django-digest/wiki/Home
DIGEST_ENFORCE_NONCE_COUNT = False

#DEBUG_TOOLBAR_CONFIG = {
#    'INTERCEPT_REDIRECTS': False,
#    'SHOW_TOOLBAR_CALLBACK': lambda request: True,
#    #'EXTRA_SIGNALS': ['myproject.signals.MySignal'],
#    'HIDE_DJANGO_SQL': False,
#}

######################################################################

USE_STATIC_SERVE = USING_DJANGO_DEV_SERVER

DATA_DIR = '%s/data/' % CHECKOUT_DIR
DATA_URL = '%sdata/' % SCRIPT_NAME

ICON_PATTERN = MEDIA_ROOT + 'share/map/*Point.png'
ICONS_RAW = [re.sub(r'Point\.png$', '', os.path.basename(i))
             for i in glob(ICON_PATTERN)]
# put 'camera' first, indicating the default
ICONS = ['camera'] + [i for i in ICONS_RAW if i != 'camera']
ICONS_DICT = dict.fromkeys(ICONS)

BASE_LINE_STYLES = ('solid',)
LINE_STYLES = BASE_LINE_STYLES

STATIC_DIR = '%s/build/s/' % CHECKOUT_DIR
TMP_DIR = '%stmp/' % STATIC_DIR

STATIC_URL = '%ss/' % SCRIPT_NAME
TMP_URL = '%stmp/' % STATIC_URL

DELETE_TMP_FILE_WAIT_SECONDS = 60*60

SITE_TITLE = 'GeoCam Share'
KML_FLY_TO_VIEW = True

STATUS_CHOICES = (('p', 'pending'), # in db but not fully processed yet
                  ('a', 'active'),  # active, display this to user
                  ('d', 'deleted'), # deleted but not purged yet
                  )
# define constants like STATUS_PENDING based on above choices
for code, label in STATUS_CHOICES:
    globals()['STATUS_' + label.upper()] = code

GALLERY_PAGE_COLS = 3
GALLERY_PAGE_ROWS = 3

# for multiple thumbnails in sidebar gallery
GALLERY_THUMB_SIZE = [160, 120]
# for single thumbnail in sidebar gallery
DESC_THUMB_SIZE = [480, 360]

THUMB_SIZES = [GALLERY_THUMB_SIZE, DESC_THUMB_SIZE]

# MAP_BACKEND possible values: 'earth', 'maps', 'none'.
MAP_BACKEND = 'maps'

# enable/disable clustering of markers (if supported by the current MAP_BACKEND)
USE_MARKER_CLUSTERING = False

USE_TRACKING = False
