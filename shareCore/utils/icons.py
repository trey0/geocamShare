#!/usr/bin/env python

import PIL.Image as Image
import os
import re
from glob import glob

ICON_SIZE = {}

def rotateAntialias(im, angle, outSize=(32, 32)):
    '''x = rotateAntialias(im, angle) is like x = im.rotate(angle) but
    rotates at twice the resolution of the output image, then rescales
    to get the best quality.  note that the output image will generally
    not have exactly the requested outSize; instead, all the rotations
    of the same image will be at the same scale.'''
    s = outSize
    if im.size[0] > s[0]*2:
        filter = Image.ANTIALIAS
    else:
        filter = Image.BICUBIC
    r = im.resize((s[0]*2, s[1]*2), filter)
    r = r.rotate(angle, Image.BICUBIC, expand=1)
    s = r.size
    r = r.resize((s[0]//2, s[1]//2), Image.ANTIALIAS)
    return r

def copyThumbnails(inDir, outDir, nameTransform=None):
    icons = glob('%s/*.png' % inDir) + glob('%s/*.jpg' % inDir)
    for p in icons:
        im = Image.open(p)
        im.thumbnail((32, 32), Image.ANTIALIAS)
        base, ext = os.path.splitext(os.path.basename(p))
        if nameTransform != None:
            base = nameTransform(base)
        im.save('%s/%s%s' % (outDir, base, ext))

def generateAllDirections(imPath, outputDir):
    im = Image.open(imPath)
    base, ext = os.path.splitext(os.path.basename(imPath))
    base = re.sub(r'Point$', '', base)
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)
    for angle in xrange(0, 360, 10):
        outPath = os.path.join(outputDir, '%s%03d%s' % (base, angle, ext))
        rotateAntialias(im, angle).save(outPath)

def cacheIconSize(dir):
    paths = glob('%s/*' % dir)
    for p in paths:
        iconPrefix = os.path.splitext(os.path.basename(p))[0]
        im = Image.open(p)
        ICON_SIZE[iconPrefix] = list(im.size)

def getIconSize(iconPrefix):
    return ICON_SIZE[iconPrefix]
