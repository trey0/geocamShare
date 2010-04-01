# emacs, please use -*- python -*- mode

import os
import sys
import tempfile
import re
from django.core.handlers.wsgi import WSGIHandler

def getEnvironmentFromSourceMe():
    # pick up environment variables from sourceme
    thisDir = os.path.dirname(os.path.realpath(__file__))
    fd, tmp = tempfile.mkstemp('djangoWsgiSourceMe.txt')
    os.close(fd)
    os.system('bash -c "(source %s/sourceme && printenv > %s)"' % (thisDir, tmp))
    varsIn = file(tmp, 'r')
    for line in varsIn:
        line = line[:-1] # chop final cr
        var, val = line.split('=', 1)
        os.environ[var] = val
    varsIn.close()
    try:
        os.unlink(tmp)
    except:
        pass

    # add any new entries from PYTHONPATH to Python's sys.path
    if os.environ.has_key('PYTHONPATH'):
        envPath = re.sub(':$', '', os.environ['PYTHONPATH'])
        sys.path = envPath.split(':') + sys.path

getEnvironmentFromSourceMe()
application = WSGIHandler()
