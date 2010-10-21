#!/usr/bin/env python
# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

import sys
import os
import stat
import itertools
import traceback
import errno
import shutil
from glob import glob
from random import choice

import django

THIS_DIR = os.path.dirname(os.path.realpath(__file__))
DJANGO_DIR = os.path.dirname(os.path.realpath(django.__file__))
LOCAL_SETTINGS = 'local_settings.py'
LOCAL_SOURCEME = 'sourceme.sh'
GIGAPAN_MEDIA_SEARCH_DIRS = ('%s/gigapan' % THIS_DIR,
                             '/Library/WebServer/Documents/gigapan')
BUILDING_FOR_GEOCAM = (__name__ == '__main__')
USE_SYMLINKS = True

# avoid obscure error message if share2 module is not found
try:
    import share2
except ImportError:
    # try adding parent directory to $PYTHONPATH
    sys.path = [os.path.dirname(THIS_DIR)] + sys.path
    import share2

from share2.shareCore import utils
from share2.shareCore.icons import rotate, svg

builderG = None
        
def dosys(cmd):
    print cmd
    ret = os.system(cmd)
    if ret != 0:
        print '[command exited with non-zero return value %d]' % ret

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
        print >>sys.stderr, ('**** warning: no file %s in search path, try setting $%s to the directory that contains it'
                             % (f, envVar))
        return None

def joinNoTrailingSlash(a, b):
    if b == '':
        return a
    else:
        return a + os.path.sep + b

def getFiles(src, suffix=''):
    #print 'getFiles: src=%s suffix=%s' % (src, suffix)
    path = joinNoTrailingSlash(src, suffix)
    pathMode = os.stat(path)[stat.ST_MODE]
    if stat.S_ISREG(pathMode):
        return [suffix]
    elif stat.S_ISDIR(pathMode):
        return itertools.chain([suffix],
                               *(getFiles(src, os.path.join(suffix, f))
                                 for f in os.listdir(path)))
    else:
        return [] # not a dir or regular file, ignore

def installFile(src, dst):
    if os.path.isdir(src):
        if os.path.exists(dst):
            if not os.path.isdir(dst):
                # replace plain file with directory
                os.unlink(dst)
                os.makedirs(dst)
        else:
            # make directory
            os.makedirs(dst)
    else:
        # install plain file
        if not os.path.exists(os.path.dirname(dst)):
            os.makedirs(os.path.dirname(dst))
        if USE_SYMLINKS:
            if os.path.isdir(dst):
                dst = os.path.join(dst, os.path.basename(src))
            if os.path.exists(dst):
                os.unlink(dst)
            os.symlink(os.path.realpath(src), dst)
        else:
            shutil.copy(src, dst)

def installDir0(src, dst):
    for f in getFiles(src):
        #print 'src=%s f=%s' % (src, f)
        dst1 = joinNoTrailingSlash(dst, f)
        src1 = joinNoTrailingSlash(src, f)
        #print 'dst1=%s src1=%s' % (dst1, src1)
        builderG.applyRule(dst1, [src1],
                           lambda: installFile(src1, dst1))

def installDir(src, dst):
    print 'installDir %s %s' % (src, dst)
    installDir0(src, dst)

def installDirs0(srcs, dst):
    for src in srcs:
        installDir0(src, os.path.join(dst, os.path.basename(src)))

def installDirs(pat, dst):
    print 'installDirs %s %s' % (pat, dst)
    installDirs0(glob(pat), dst)

def collectMedia():
    dosys('mkdir -p build/s/tmp')
    installFile('configTemplates/tmp/README.txt', 'build/s/tmp')
    dosys('chmod go+rw build/s/tmp')
    installDirs('shareCore/media/static/*', 'build/media/')
    if BUILDING_FOR_GEOCAM:
        installDirs('shareGeocam/media/static/*', 'build/media/')
        installDirs('shareTracking/media/static/*', 'build/media/')
    installDir('%s/contrib/admin/media' % DJANGO_DIR,
               'build/media/admin')
    gigapanMediaDir = findDirContaining('PanoramaViewer.swf',
                                        GIGAPAN_MEDIA_SEARCH_DIRS,
                                        'GIGAPAN_MEDIA_DIR')
    if gigapanMediaDir:
        installDir(gigapanMediaDir, 'build/media/gigapan')

def svgIcons(pat, outputDir):
    print 'svgIcons %s %s' % (pat, outputDir)
    for imPath in glob(pat):
        svg.buildIcon(builderG, imPath, outputDir=outputDir)

def generateIcons():
    svgIcons('shareCore/media/svgIcons/*.svg', 'build/media/share/map/')
    if BUILDING_FOR_GEOCAM:
        svgIcons('shareGeocam/media/svgIcons/*.svg', 'build/media/share/map/')
    rotGlob = 'build/media/share/map/*Point.png'
    rotOutput = 'build/media/share/mapr'
    print 'rotateIcons %s %s' % (rotGlob, rotOutput)
    for imPath in glob(rotGlob):
        rotate.buildAllDirections(builderG, imPath, outputDir=rotOutput)

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
    dosys('mkdir -p build')
    dosys('touch build/__init__.py')
    collectMedia()
    generateIcons()
    makeLocalSourceme()
    makeLocalSettings()
    if not os.path.exists('django.wsgi'):
        # backward compatible with older share installations
        dosys('ln -s djangoWsgi.py django.wsgi')
    dosys('touch djangoWsgi.py')
    builderG.finish()

def main():
    global builderG
    import optparse
    parser = optparse.OptionParser('usage: %prog <install>')
    parser.add_option('-v', '--verbose',
                      action='count',
                      help='Increase verbosity.  Can specify -v multiple times.')
    opts, args = parser.parse_args()
    if not (len(args) == 1 and args[0] == 'install'):
        parser.error('expected install command')
    builderG = utils.Builder(verbose=opts.verbose)
    install()

if __name__ == '__main__':
    main()
