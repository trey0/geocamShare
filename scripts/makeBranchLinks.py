#!/usr/bin/env python
# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

import os
import sys

_up = os.path.dirname
CHECKOUT_DIR = _up(_up(os.path.realpath(__file__)))
EXTENSIONS = ['.py', '.js', '.html']

def dosys(cmd):
    print cmd
    os.system(cmd)

def makeLink(targ, src):
    if os.path.islink(src):
        dosys('rm -f %s' % src)
    if os.path.exists(src):
        print 'makeLink: %s already exists, skipping' % src
    else:
        #dosys('ln %s %s' % (targ, src))
        dosys('ln -s %s %s' % (targ, src))

def matchFiles(root, extensions, stem='', nlevels=999):
    matches = []
    dir = os.path.join(root, stem)
    files = os.listdir(dir)
    files.sort()
    subDirs = []
    for f in files:
        fullPath = os.path.join(dir, f)
        relPath = os.path.join(stem, f)
        if os.path.isdir(fullPath):
            subDirs.append(relPath)
        else:
            if os.path.splitext(f)[1] in extensions:
                matches.append(relPath)
    if nlevels > 0:
        for subDir in subDirs:
            matches += matchFiles(root, extensions, subDir, nlevels-1)
    return matches

def doit(opts):
    os.chdir(CHECKOUT_DIR)
    links = []

    if not opts.noGds and not os.path.exists(os.path.join(opts.gdsDir, 'setup.py')):
        print >>sys.stderr, 'no setup.py found in GDS directory %s; try -g or -n option' % opts.gdsDir
        sys.exit(1)

    # gds symlinks in top-level dir
    if not opts.noGds:
        for p in matchFiles(opts.gdsDir, EXTENSIONS, nlevels=0):
            stem, ext = os.path.splitext(p)
            links.append(('%s/%s' % (opts.gdsDir, p), '%s--gds%s' % (stem, ext)))

    # gds symlinks in geocamCore
    if not opts.noGds:
        for p in matchFiles('%s/shareGds' % opts.gdsDir, EXTENSIONS):
            stem, ext = os.path.splitext(p)
            links.append(('%s/shareGds/%s' % (opts.gdsDir, p), 'geocamCore/%s--gds%s' % (stem, ext)))

    # local app symlinks in geocamCore
    for shareApp in ('geocam', 'tracking'):
        suffix = 'share' + shareApp.capitalize()
        appDir = os.path.join(CHECKOUT_DIR, suffix)
        for p in matchFiles(appDir, EXTENSIONS):
            stem, ext = os.path.splitext(p)
            links.append(('%s/%s' % (appDir, p), 'geocamCore/%s--%s%s' % (stem, shareApp, ext)))
    
    for targ, src in links:
        if opts.clean:
            dosys('rm -f %s' % src)
        else:
            makeLink(targ, src)
    
def main():
    import optparse
    parser = optparse.OptionParser('usage: %prog')
    parser.add_option('-c', '--clean',
                      action='store_true', default=False,
                      help='Clean links instead of creating them')
    parser.add_option('-g', '--gdsDir',
                      default='%s/gds' % os.path.dirname(CHECKOUT_DIR),
                      help='Directory containing setup.py for GDS [%default]')
    parser.add_option('-n', '--noGds',
                      default=False, action='store_true',
                      help='Do not make GDS links')
    opts, args = parser.parse_args()
    if args:
        parser.error('expected no arguments')
    doit(opts)

if __name__ == '__main__':
    main()
