#!/usr/bin/env python

import os
from glob import glob

GDS = '%s/k' % os.environ['HOME']
EXTENSIONS = ['py', 'js', 'html']

def dosys(cmd):
    print cmd
    os.system(cmd)

def makeLink(targ, src):
    if os.path.islink(src):
        dosys('rm -f %s' % src)
    dosys('ln %s %s' % (targ, src))

def matchFiles(dir, recurse=False):
    old = os.getcwd()
    os.chdir(dir)
    matches = []
    for ext in EXTENSIONS:
        matches += glob('*.%s' % ext)
        if recurse:
            matches += glob('*/*.%s' % ext)
    os.chdir(old)
    return matches

thisDir = os.path.dirname(os.path.realpath(__file__))
os.chdir(thisDir)

# make gds symlinks in top-level dir
for p in matchFiles(GDS):
    stem, ext = os.path.splitext(p)
    makeLink('%s/%s' % (GDS, p), '%s--gds%s' % (stem, ext))

# make geocam symlinks in shareCore
for p in matchFiles('shareGeocam', True):
    stem, ext = os.path.splitext(p)
    makeLink('shareGeocam/%s' % p, 'shareCore/%s--geocam%s' % (stem, ext))
    
# make gds symlinks in shareCore
for p in matchFiles('%s/shareGds' % GDS, True):
    stem, ext = os.path.splitext(p)
    makeLink('%s/shareGds/%s' % (GDS, p), 'shareCore/%s--gds%s' % (stem, ext))
