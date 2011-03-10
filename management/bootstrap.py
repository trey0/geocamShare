#!/usr/bin/env python
# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

"""
This bootstrap script does the first stage of prep work for a Django
site that consists of multiple apps pulled in from separate repos via
git submodules.  The script does just enough so that our subsequent
Django management commands will work -- they need Django to be installed
and minimally configured, and they need the apps to be present
and linked into the right place relative to the PYTHONPATH.

This script is intended to be generic across sites.  Please don't put
any site-specific customizations in here.  If you need to modify it,
please check your changes into
geocamDjangoSiteSkeleton/skel/bin/bootstrap.py so other sites can
benefit.  Normally we would put code like this in geocamUtil, but the
whole reason we need a bootstrap step is to make sure things like
geocamUtil are available...
"""

import os
import sys
from glob import glob
import logging
from random import choice

DEFAULT_SITE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SOURCEME_NAME = 'sourceme.sh'
SETTINGS_NAME = 'settings.py'
STATUS_PATH_TEMPLATE = 'build/management/bootstrap/%sStatus.txt'

ACTIONS = (dict(name='gitInitSubmodules',
                desc="init and update submodules",
                confirm=True),
           dict(name='linkSubmodules',
                desc='link submodules into apps directory',
                confirm=True),
           dict(name='installDjango',
                desc='install Django',
                confirm=True,
                needed='needDjango'),
           dict(name='genSourceme',
                needed='needSourceme'),
           dict(name='genSettings',
                needed='needSettings'),
           )
ACTION_DICT = dict([(a['name'], a) for a in ACTIONS])

def getConfirmation(opts, actionStr):
    if opts.yes:
        sys.stdout.write(actionStr+'? [Y/n] ')
        print 'y'
        return True
    else:
        while 1:
            sys.stdout.write(actionStr+'? [Y/n] ')
            response = raw_input().strip().lower()
            if not response:
                return True
            elif response == 'y':
                return True
            elif response == 'n':
                return False

def dosys(cmd, continueOnError=False):
    if cmd.startswith('sudo'):
        # force print before user gets password prompt
        print 'running: ' + cmd
    else:
        logging.info('running: ' + cmd)
    ret = os.system(cmd)
    if ret != 0:
        if continueOnError:
            logging.warning('warning: command returned non-zero return value %d' % ret)
        else:
            logging.error('error: command returned non-zero return value %d' % ret)
            sys.exit(1)

def writeFileMakeDir(path, text):
    dir = os.path.dirname(path)
    if not os.path.exists(dir):
        os.makedirs(dir)
    f = file(path, 'w')
    f.write(text+'\n')
    f.close()

def fillTemplate(inputFile, outputFile, context):
    from django.template import Template, Context
    from django.conf import settings
    if not settings.configured:
        settings.configure()
    tmpl = Template(file(inputFile, 'r').read())
    text = tmpl.render(Context(context))
    file(outputFile, 'w').write(text)

######################################################################
# ACTION DEFINITIONS

def gitInitSubmodules(opts):
    dosys('git submodule init')
    dosys('git submodule update')

def linkSubmodules(opts):
    # assumes each submodule app has a models dir or a models.py file
    if not os.path.exists('apps'):
        os.mkdir('apps')
    submoduleAppDirs = [os.path.dirname(d) for d in glob('submodules/*/*/models*')]
    for src in submoduleAppDirs:
        appName = os.path.basename(src)
        relativeSrc = '../%s' % src
        dst = 'apps/%s' % appName
        if os.path.lexists(dst):
            logging.debug('  %s -> %s skipped (already exists)' % (dst, relativeSrc))
        else:
            logging.debug('  %s -> %s' % (dst, relativeSrc))
            os.symlink(relativeSrc, dst)

def needDjango(opts):
    try:
        import django
    except ImportError:
        return True
    return False

def installDjango(opts):
    needSudo = not os.environ.has_key('VIRTUALENV')
    if needSudo:
        sudoStr = 'sudo '
    else:
        sudoStr = ''
    dosys('%spip install django' % sudoStr)

def needSourceme(opts):
    return not os.path.exists(SOURCEME_NAME)

def genSourceme(opts):
    logging.info('generating %s' % SOURCEME_NAME)

    fillTemplate('management/templates/%s' % SOURCEME_NAME,
                 SOURCEME_NAME,
                 dict(virtualEnvDir=os.environ.get('VIRTUALENV', None),
                      parentDir=os.path.dirname(os.path.abspath(os.getcwd())),
                      appsDir=os.path.abspath('apps')
                      ))

def needSettings(opts):
    return not os.path.exists(SETTINGS_NAME)

def genSettings(opts):
    logging.info('generating %s' % SETTINGS_NAME)

    secretKey = ''.join([choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)])

    fillTemplate('management/templates/%s' % SETTINGS_NAME,
                 SETTINGS_NAME,
                 dict(secretKey=secretKey))

def needAction(opts, action):
    statusFile = STATUS_PATH_TEMPLATE % action['name']
    if os.path.exists(statusFile):
        return file(statusFile, 'r').read().strip()
    else:
        return False

######################################################################
# TOP-LEVEL CODE

def doAction(opts, action):
    # check if we need to do the action
    neededName = action.get('needed', None)
    if neededName:
        # special check function defined for this action
        neededFunc = globals()[neededName]
        actionIsNeeded = neededFunc(opts)
        if not actionIsNeeded:
            logging.info('skipping step %s, not needed' % action['name'])
            return
    else:
        # standard check function
        status = needAction(opts, action)
        if status:
            logging.info('skipping step %s, status is %s' % (action['name'], status))
            return
    
    # confirm with user
    if action.has_key('confirm') and not getConfirmation(opts, action['desc']):
        writeFileMakeDir(STATUS_PATH_TEMPLATE % action['name'], 'UNWANTED')
        return
            
    # do the action
    actionFunc = globals()[action['name']]
    actionFunc(opts)

    # mark completion (unless special check function is defined)
    if not neededName:
        writeFileMakeDir(STATUS_PATH_TEMPLATE % action['name'], 'DONE')

def doit(opts, args):
    os.chdir(opts.siteDir)
    if os.path.exists('build/management/bootstrap/bootstrapStatus.txt'):
        sys.exit(0)
    print 'bootstrapping...'

    logging.basicConfig(level=(logging.WARNING - opts.verbose * 10),
                        format='%(message)s')
    
    if args:
        for arg in args:
            if arg not in ACTION_DICT:
                print >>sys.stderr, 'ERROR: there is no action %s' % arg
                print >>sys.stderr, 'available actions are: %s' % (' '.join([a['name'] for a in ACTIONS]))
                sys.exit(1)
        actions = [ACTION_DICT[arg] for arg in args]
    else:
        actions = ACTIONS
    
    logging.info('working in %s' % os.getcwd())
    for action in ACTIONS:
        doAction(opts, action)

    # mark overall completion
    writeFileMakeDir(STATUS_PATH_TEMPLATE % 'bootstrap', 'DONE')

    print '\nnow "source sourceme.sh" before running manage.py again'
    sys.exit(1)

def main():
    import optparse
    parser = optparse.OptionParser('usage: %prog [action1 action2 ...]')
    parser.add_option('-y', '--yes',
                      action='store_true', default=False,
                      help='Automatically answer yes to all confirmation questions')
    parser.add_option('-s', '--siteDir',
                      default=DEFAULT_SITE_DIR,
                      help='Site directory to work in [%default]')
    parser.add_option('-v', '--verbose',
                      action='count', default=0,
                      help='Increase verbosity, can specify multiple times')
    opts, args = parser.parse_args()
    doit(opts, args)

if __name__ == '__main__':
    main()
