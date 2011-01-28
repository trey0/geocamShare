# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

import os
import sys
import tempfile
import re
from django.core.handlers.wsgi import WSGIHandler

def getEnvironmentFromSourceMe(thisDir):
    # pick up environment variables from sourceme
    fd, tmp = tempfile.mkstemp('djangoWsgiSourceMe.txt')
    os.close(fd)
    os.system('bash -c "(source %s/sourceme.sh && printenv > %s)"' % (thisDir, tmp))
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

def sendError(start_response, text):
    start_response(text, [('Content-type', 'text/html')])
    return ["""<html>
  <head><title>%s</title></head>
  <body><h1>%s</h1></body>
</html>
    """ % (text, text)]

def downForMaintenance(environ, start_response):
    import stat
    import time
    thisDir = os.path.dirname(os.path.realpath(__file__))
    downFile = os.path.join(thisDir, 'DOWN_FOR_MAINTENANCE')
    downMtime = os.stat(downFile)[stat.ST_MTIME]
    downTimeString = time.strftime('%Y-%m-%d %H:%M %Z', time.localtime(downMtime))
    return sendError(start_response, '503 Down for maintenance since %s' % downTimeString)

thisDir = os.path.dirname(os.path.realpath(__file__))
getEnvironmentFromSourceMe(thisDir)
if os.path.exists(os.path.join(thisDir, 'DOWN_FOR_MAINTENANCE')):
    application = downForMaintenance
else:
    application = WSGIHandler()
