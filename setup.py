#!/usr/bin/env python

import sys
import os
from random import choice
import django

THIS_DIR = os.path.dirname(os.path.realpath(__file__))
DJANGO_DIR = os.path.dirname(os.path.realpath(django.__file__))
LOCAL_SETTINGS = 'local_settings.py'
LOCAL_SOURCEME = 'sourceme'
GIGAPAN_MEDIA_SEARCH_DIRS = ('%s/gigapan' % THIS_DIR,
                             '/Library/WebServer/Documents/gigapan')

def dosys(cmd):
    print cmd
    os.system(cmd)

def findDirContaining(f, dirs, envVar):
    envDir = os.environ.get(envVar, None)
    if envDir:
        if os.path.exists(os.path.join(envDir, f)):
            return envDir
        else:
            raise Exception('no file %s in dir $%s=%s' % (f, envVar, envDir))
    else:
        for dir in dirs:
            if os.path.exists(os.path.join(dir, f)):
                return dir
        raise Exception('no file %s in default search path, try setting $%s to the directory that contains it'
                        % (f, envVar))

def collectMedia():
    dosys('rm -rf build/media')
    dosys('mkdir -p build/media/share')
    dosys('cp -r shareCore/media/* build/media/share/')
    if __name__ == '__main__':
        dosys('cp -r shareGeocam/media/* build/media/share/')
    dosys('cp -r %s/contrib/admin/media build/media/admin' % DJANGO_DIR)
    gigapanMediaDir = findDirContaining('PanoramaViewer.swf',
                                        GIGAPAN_MEDIA_SEARCH_DIRS,
                                        'GIGAPAN_MEDIA_DIR')
    dosys('cp -r %s build/media/gigapan' % gigapanMediaDir)

def makeLocalSourceme():
    if not os.path.exists(LOCAL_SOURCEME):
        print 'writing template %s' % LOCAL_SOURCEME
        parentDir = os.path.dirname(THIS_DIR)
        text = """
# set DJANGO_SCRIPT_NAME to the URL prefix for Django on your web server (with leading slash
# and trailing slash)
export DJANGO_SCRIPT_NAME='/share/'

# the auto-generated PYTHONPATH usually works, but you might need to add more directories
# depending on how you installed everything
export PYTHONPATH=%s:$PYTHONPATH

export DJANGO_SETTINGS_MODULE='share2.settings'
""" % parentDir
        file(LOCAL_SOURCEME, 'w').write(text)
        print
        print '**** Please set DJANGO_SCRIPT_NAME in %s according to the instructions there' % LOCAL_SOURCEME

def makeLocalSettings():
    if not os.path.exists(LOCAL_SETTINGS):
        print 'writing template %s' % LOCAL_SETTINGS
        print 'generating a unique secret key for your server'
        secretKey = ''.join([choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)])
        text = """
ADMINS = (
    ('Example', 'root@example.com'),
)
MANAGERS = ADMINS

# Make this unique, and don't share it with anybody
SECRET_KEY = '%s'

MAPS_API_KEY = 'fill in key for your domain here -- get from http://code.google.com/apis/maps/signup.html'
""".lstrip() % secretKey
        file(LOCAL_SETTINGS, 'w').write(text)
        print
        print '**** Please fill in a Google Maps API key for your domain in %s' % LOCAL_SETTINGS
        print '**** Visit http://code.google.com/apis/maps/signup.html to get one'

def install():
    os.chdir(THIS_DIR)
    dosys('touch django.wsgi')
    dosys('mkdir -p build')
    dosys('touch build/__init__.py')
    collectMedia()
    makeLocalSourceme()
    makeLocalSettings()

def main():
    import optparse
    parser = optparse.OptionParser('usage: %prog <install>')
    opts, args = parser.parse_args()
    if not (len(args) == 1 and args[0] == 'install'):
        parser.error('expected install command')
    install()

if __name__ == '__main__':
    main()
