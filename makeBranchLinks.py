#!/usr/bin/env python

import os
from glob import glob
import gds.setup

THIS_DIR = os.path.dirname(os.path.realpath(__file__))
GDS_DIR = gds.setup.THIS_DIR
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
        dosys('ln %s %s' % (targ, src))

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
    os.chdir(THIS_DIR)
    links = []

    # gds symlinks in top-level dir
    for p in matchFiles(GDS_DIR, EXTENSIONS, nlevels=0):
        stem, ext = os.path.splitext(p)
        links.append(('%s/%s' % (GDS_DIR, p), '%s--gds%s' % (stem, ext)))

    # geocam symlinks in shareCore
    for p in matchFiles('shareGeocam', EXTENSIONS):
        stem, ext = os.path.splitext(p)
        links.append(('shareGeocam/%s' % p, 'shareCore/%s--geocam%s' % (stem, ext)))
    
    # gds symlinks in shareCore
    for p in matchFiles('%s/shareGds' % GDS_DIR, EXTENSIONS):
        stem, ext = os.path.splitext(p)
        links.append(('%s/shareGds/%s' % (GDS_DIR, p), 'shareCore/%s--gds%s' % (stem, ext)))

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
    opts, args = parser.parse_args()
    if args:
        parser.error('expected no arguments')
    doit(opts)

if __name__ == '__main__':
    main()
