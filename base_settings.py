# Django settings for gds project.

import os

CHECKOUT_DIR = os.environ['CHECKOUT_DIR']
SCRIPT_NAME = os.environ['DJANGO_SCRIPT_NAME']
if not SCRIPT_NAME.endswith('/'):
    SCRIPT_NAME += '/'

DEBUG = True
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
    "share2.shareCore.context_processors.serverRoot",
    "share2.shareCore.context_processors.settings",
)

MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
#    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'share2.shareCore.middleware.LogErrorsMiddleware',
)

ROOT_URLCONF = 'share2.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.comments',
    'tagging',
    'share2.shareCore',
)

#DEBUG_TOOLBAR_CONFIG = {
#    'INTERCEPT_REDIRECTS': False,
#    'SHOW_TOOLBAR_CALLBACK': lambda request: True,
#    #'EXTRA_SIGNALS': ['myproject.signals.MySignal'],
#    'HIDE_DJANGO_SQL': False,
#}

######################################################################

USE_STATIC_SERVE = False

DATA_DIR = '%s/data/' % CHECKOUT_DIR
DATA_URL = '%sdata/' % SCRIPT_NAME

BASE_ICONS = ('camera', 'track',)
ICONS = BASE_ICONS

BASE_LINE_STYLES = ('solid',)
LINE_STYLES = BASE_LINE_STYLES

STATIC_DIR = '%s/build/s/' % CHECKOUT_DIR
TMP_DIR = '%stmp/' % STATIC_DIR

STATIC_URL = '%ss/' % SCRIPT_NAME
TMP_URL = '%stmp/' % STATIC_URL

DELETE_TMP_FILE_WAIT_SECONDS = 60*60

SITE_TITLE = 'K10 Share'

KML_FLY_TO_VIEW = True

from local_settings import *
