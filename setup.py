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
from django.template import Template, Context

THIS_DIR = os.path.dirname(os.path.realpath(__file__))
DJANGO_DIR = os.path.dirname(os.path.realpath(django.__file__))
LOCAL_SETTINGS = 'local_settings.py'
LOCAL_SOURCEME = 'sourceme.sh'
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

def dosys(cmd):
    print cmd
    ret = os.system(cmd)
    if ret != 0:
        print '[command exited with non-zero return value %d]' % ret

def findDirContaining(f, dirs, envVar, warnOnFailure=False):
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
        if warnOnFailure:
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

def installDir0(builder, src, dst):
    for f in getFiles(src):
        #print 'src=%s f=%s' % (src, f)
        dst1 = joinNoTrailingSlash(dst, f)
        src1 = joinNoTrailingSlash(src, f)
        #print 'dst1=%s src1=%s' % (dst1, src1)
        builder.applyRule(dst1, [src1],
                          lambda: installFile(src1, dst1))

def installDir(builder, src, dst):
    print 'installDir %s %s' % (src, dst)
    installDir0(builder, src, dst)

def installDirs0(builder, srcs, dst):
    for src in srcs:
        installDir0(builder, src, os.path.join(dst, os.path.basename(src)))

def installDirs(builder, pat, dst):
    print 'installDirs %s %s' % (pat, dst)
    installDirs0(builder, glob(pat), dst)

def svgIcons(builder, pat, outputDir):
    print 'svgIcons %s %s' % (pat, outputDir)
    for imPath in glob(pat):
        svg.buildIcon(builder, imPath, outputDir=outputDir)

def fillTemplate(builder, inputFile, outputFile, context):
    tmpl = Template(file(inputFile, 'r').read())
    text = tmpl.render(context)
    file(outputFile, 'w').write(text)

def fillTemplates(builder, pat, outputDir, context):
    print 'fillTemplates %s %s' % (pat, outputDir)
    if not os.path.exists(outputDir):
        dosys('mkdir -p %s' % outputDir)
    for inputFile in glob(pat):
        outputFile = os.path.join(outputDir, os.path.basename(inputFile))
        builder.applyRule(outputFile, [inputFile, LOCAL_SOURCEME, LOCAL_SETTINGS],
                          lambda: fillTemplate(builder, inputFile, outputFile, context))

class AppSetupCore(object):
    def __init__(self, opts, workingDir):
        self.workingDir = workingDir
        self.builder = utils.Builder(verbose=opts.verbose)

    def collectMedia(self):
        if not os.path.exists('build/s/tmp'):
            dosys('mkdir -p build/s/tmp')
        installFile('%s/make/templates/tmp/README.txt' % THIS_DIR,
                    'build/s/tmp')
        dosys('chmod go+rw build/s/tmp')
        installDirs(self.builder,
                    '%s/shareCore/media/static/*' % THIS_DIR,
                    'build/media/')
        installDir(self.builder,
                   '%s/contrib/admin/media' % DJANGO_DIR,
                   'build/media/admin')
        gigapanSearchDirs = ('%s/gigapan' % self.workingDir,
                             '/Library/WebServer/Documents/gigapan')
        gigapanMediaDir = findDirContaining('PanoramaViewer.swf',
                                            gigapanSearchDirs,
                                            'GIGAPAN_MEDIA_DIR')
        if gigapanMediaDir:
            installDir(self.builder, gigapanMediaDir, 'build/media/gigapan')

    def renderIcons(self):
        svgIcons(self.builder,
                 '%s/shareCore/media/svgIcons/*.svg' % THIS_DIR,
                 'build/media/share/map/')

    def rotateIcons(self):
        rotGlob = 'build/media/share/map/*Point.png'
        rotOutput = 'build/media/share/mapr'
        print 'rotateIcons %s %s' % (rotGlob, rotOutput)
        for imPath in glob(rotGlob):
            rotate.buildAllDirections(self.builder, imPath, outputDir=rotOutput)

    def makeLocalSourceme(self):
        if not os.path.exists(LOCAL_SOURCEME):
            print 'writing template %s' % LOCAL_SOURCEME
            parentDir = os.path.dirname(self.workingDir)
            text = """
# Set DJANGO_SCRIPT_NAME to the URL prefix for Django on your web server (with leading slash
# and trailing slash).  This setting is ignored if using the built-in Django development web
# server.
export DJANGO_SCRIPT_NAME='/share/'

# The auto-generated PYTHONPATH usually works, but you might need to add more directories
# depending on how you installed everything.
export PYTHONPATH=%s:$PYTHONPATH

# You should not need to change this.
export DJANGO_SETTINGS_MODULE='share2.settings'
""" % parentDir
            file(LOCAL_SOURCEME, 'w').write(text)

    def makeLocalSettings(self):
        if not os.path.exists(LOCAL_SETTINGS):
            print 'writing template %s' % LOCAL_SETTINGS
            print 'generating a unique secret key for your server'
            secretKey = ''.join([choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)])
            text = """
import sys

USING_DJANGO_DEV_SERVER = (sys.argv[-1] == 'runserver')

ADMINS = (
    ('Example', 'root@example.com'),
)
MANAGERS = ADMINS

# SECURITY_REDIRECT_* -- settings for SecurityRedirectMiddleware; see shareCore/middleware.py
if USING_DJANGO_DEV_SERVER:
    # The built-in Django dev server does not support Share's
    # authentication strategy.
    SECURITY_REDIRECT_ENABLED = False
else:
    # If your web server does not support SSL you may need to set this to its
    # INSECURE False setting.
    SECURITY_REDIRECT_ENABLED = True

# Make this unique, and don't share it with anybody.  Used by Django's
# cookie-based authentication mechanism.
SECRET_KEY = '%s'

# Normally you don't need to set MAPS_API_KEY, but it is required if
# you're using the alternate mapping backend based on the Google Earth
# API.
MAPS_API_KEY = 'fill in key for your domain here -- get from http://code.google.com/apis/maps/signup.html'
""".lstrip() % secretKey
            file(LOCAL_SETTINGS, 'w').write(text)

    def fillConfigTemplates(self):
        try:
            from share2.djangoWsgi import getEnvironmentFromSourceMe
            getEnvironmentFromSourceMe()
            from django.conf import settings
        except ImportError:
            print >>sys.stderr, '*** warning: can\'t fill config templates, error importing settings'
            return
        user = os.environ['USER']
        context = Context(dict(CHECKOUT_DIR=settings.CHECKOUT_DIR,
                               SCRIPT_NAME=settings.SCRIPT_NAME,
                               MEDIA_DIR=settings.MEDIA_ROOT,
                               DATA_DIR=settings.DATA_DIR,
                               WSGI_USER=user,
                               WSGI_PROCESS_GROUP='share'+user.capitalize()))
        fillTemplates(self.builder,
                      '%s/make/templates/*.conf' % THIS_DIR,
                      'build/apache2/',
                      context)

    def install(self):
        os.chdir(self.workingDir)
        if not os.path.exists('build'):
            dosys('mkdir -p build')
            dosys('touch build/__init__.py')
        self.collectMedia()
        self.renderIcons()
        self.rotateIcons()
        self.makeLocalSourceme()
        self.makeLocalSettings()
        self.fillConfigTemplates()
        dosys('touch djangoWsgi.py')
        self.builder.finish()

class AppSetupGeoCam(AppSetupCore):
    def collectMedia(self):
        super(AppSetupGeoCam, self).collectMedia()
        installDirs(self.builder,
                    '%s/shareGeocam/media/static/*' % THIS_DIR,
                    'build/media/')
        installDirs(self.builder,
                    '%s/shareTracking/media/static/*' % THIS_DIR,
                    'build/media/')

    def renderIcons(self):
        super(AppSetupGeoCam, self).renderIcons()
        svgIcons(self.builder,
                 '%s/shareGeocam/media/svgIcons/*.svg' % THIS_DIR,
                 'build/media/share/map/')

def main():
    import optparse
    parser = optparse.OptionParser('usage: %prog <install>')
    parser.add_option('-v', '--verbose',
                      action='count',
                      help='Increase verbosity.  Can specify -v multiple times.')
    opts, args = parser.parse_args()
    if not (len(args) == 1 and args[0] == 'install'):
        parser.error('expected install command')
    appSetup = AppSetupGeoCam(opts, THIS_DIR)
    appSetup.install()

if __name__ == '__main__':
    main()
