# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

import os
import re
import sys
from glob import glob

from geocamUtil.management.commandUtil import getSiteDir

######################################################################
# CHECKOUT_DIR, SCRIPT_NAME, USING_DJANGO_DEV_SERVER -- these are not
# understood by Django but are used a lot below to calculate other
# settings

# can override CHECKOUT_DIR by setting the environment variable before
# importing baseSettings
DEFAULT_CHECKOUT_DIR = getSiteDir()
CHECKOUT_DIR = os.environ.get('CHECKOUT_DIR', DEFAULT_CHECKOUT_DIR)

SCRIPT_NAME = os.environ['DJANGO_SCRIPT_NAME']
if not SCRIPT_NAME.endswith('/'):
    SCRIPT_NAME += '/'

USING_DJANGO_DEV_SERVER = ('runserver' in sys.argv)

if USING_DJANGO_DEV_SERVER:
    # django dev server deployment won't work with other SCRIPT_NAME settings
    SCRIPT_NAME = '/'

######################################################################
# This section is for variables understood by Django.

DEBUG = USING_DJANGO_DEV_SERVER
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'sqlite3',
        'NAME': '%s/dev.db' % CHECKOUT_DIR,
    }
}

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
    "geocamCore.context_processors.settings",
)

MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
#    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'geocamUtil.middleware.SecurityMiddleware',
    'geocamUtil.middleware.LogErrorsMiddleware',
)

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'geocamCore',
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

######################################################################
# DIGEST_* -- settings for django_digest HTTP digest authentication

# Nonce count is a security feature that makes replay attacks more
# difficult.  However, it apparently causes problems when browsers with
# cached credentials make several simultaneous connections to the
# server, so it's recommended to turn it off.
# See http://bitbucket.org/akoha/django-digest/wiki/Home
DIGEST_ENFORCE_NONCE_COUNT = False

######################################################################
# DEBUG_* -- settings for optional debug_toolbar app

#DEBUG_TOOLBAR_CONFIG = {
#    'INTERCEPT_REDIRECTS': False,
#    'SHOW_TOOLBAR_CALLBACK': lambda request: True,
#    #'EXTRA_SIGNALS': ['myproject.signals.MySignal'],
#    'HIDE_DJANGO_SQL': False,
#}

######################################################################
# The remaining settings are ones we define that are generically
# useful across different geocam apps.  See geocamCore/defaultSettings
# for stuff that is more specific to geocamCore.

USE_STATIC_SERVE = USING_DJANGO_DEV_SERVER

GEOCAM_UTIL_SECURITY_ENABLED = not USING_DJANGO_DEV_SERVER

DATA_DIR = '%s/data/' % CHECKOUT_DIR
DATA_URL = '%sdata/' % SCRIPT_NAME

TMP_DIR = '%stmp/' % DATA_DIR
TMP_URL = '%stmp/' % DATA_URL
