# Django settings for gds project.

import os

thisDir = os.path.realpath(os.path.dirname(__file__))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Your Name', 'root@example.com'),
)

MANAGERS = ADMINS
DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = '%s/sqlite3.db' % thisDir
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
MEDIA_ROOT = '%s/media/' % thisDir

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.  Must not be the same as MEDIA_URL!
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin_media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '@@2_ck7)x$q#$325tpaw3vq)wuqt2ch+oy77$k-&j5m^1(^f(j'

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
    "share2.context_processors.serverRoot",
    "share2.context_processors.settings",
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
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
    'share2.share',
)

######################################################################

STATUS_CHOICES = (('p', 'pending'), # in db but not fully processed yet
                  ('a', 'active'),  # active, display this to user
                  ('d', 'deleted'), # deleted but not purged yet
                  )

ROBOT_CHOICES = (('B', 'k10black'),
                 ('R', 'k10red'),
                 )

TASK_CHOICES = (('lidar_pano', 'lidar pano'),
                ('lidar_scan', 'lidar scan'),
                ('mic', 'microscopic image'),
                ('pancam_pano', 'pancam pano'),
                )
TASK_CHOICES_DICT = dict(TASK_CHOICES);

TASK_ICONS = dict((('lidar_pano', 'lpa'),
                   ('lidar_scan', 'lsc'),
                   ('mic', 'mi'),
                   ('pancam_pano', 'pc'),
                   ))

# define constants, e.g. TASK_LIDARPANO = 'lidarpano'
for code, name in TASK_CHOICES:
    globals()['TASK_'+code.upper()] = code

INSTRUMENT_CHOICES = (('mic', 'microscopic imaging camera'),
                      ('pan', 'pancam'),
                      ('ldr', 'survey lidar'),
                      )

PANCAM_PANO_PARAMS = dict((('PML', 'medium lo'),
                           ('PWL', 'wide lo'),
                           ('PNH', 'narrow hi'),
                           ('PMM', 'medium medium'),
                           ('PWM', 'wide medium'),
                           ))

LIDAR_SCAN_PARAMS = dict((('LSL', 'lo res'),
                          ('LSM', 'medium res'),
                          ('LSH', 'high res'),
                          ))

# define constants, e.g. INSTR_MIC = 'mic'
for code, name in INSTRUMENT_CHOICES:
    globals()['INSTR_'+code.upper()] = code

DATA_DIR = '/irg/data/k10brain8/20090626'
SKIP_PATTERNS = ['gdsState']
ROBOT_HOST_MAP = dict(k10black = 'k10brain8',
                      k10red = 'k10brain9',
                      )
ROBOT_CODES = dict([(name, code) for (code, name) in ROBOT_CHOICES])

PROCESSED_DIR = os.path.join(os.path.dirname(thisDir), 'processed')

GALLERY_PAGE_COLS = 3
GALLERY_PAGE_ROWS = 4

GALLERY_THUMB_SIZE = [160, 120]
DESC_THUMB_SIZE = [480, 360]
