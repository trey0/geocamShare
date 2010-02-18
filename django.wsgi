# emacs, please use -*- python -*- mode

import os, sys
_up = os.path.dirname
share2ParentDir = _up(_up(__file__))
sys.path.insert(0, share2ParentDir)
os.environ['DJANGO_SETTINGS_MODULE'] = 'share2.settings'
os.environ['SHARE2_SCRIPT_NAME'] = '/shareGeocam'
os.environ['PATH'] = ('%s/packages/bin:%s'
                      % (share2ParentDir, os.environ['PATH']))
print >>sys.stderr, 'PATH=', os.environ['PATH']

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
