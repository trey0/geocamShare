# emacs, please use -*- python -*- mode

import os
import sys
from django.core.handlers.wsgi import WSGIHandler

_up = os.path.dirname
checkoutParentDir = _up(_up(os.path.realpath(__file__)))
sys.path.insert(0, checkoutParentDir)
os.environ['DJANGO_SETTINGS_MODULE'] = 'share2.settings'
os.environ['DJANGO_SCRIPT_NAME'] = '/shareGeocam'
application = WSGIHandler()
