#!/usr/bin/env python

import PIL.Image as Image
import os
import re
from glob import glob

ICON_SIZE = {}

def rotateAntialias(im, angle, reqSize=(32, 32)):
    '''x = rotateAntialias(im, angle) is like x = im.rotate(angle) but
    gets best quality by rotating at twice the resolution of the output
    image, then downsampling with anti-aliasing.  note that the output
    image will generally not have exactly the requested reqSize;
    instead, all the rotations of the same image will be at the same
    scale.'''
    if float(reqSize[0]) / im.size[0] < float(reqSize[1]) / im.size[1]:
        outSize = (reqSize[0], int(float(reqSize[0])/im.size[0] * im.size[1]))
    else:
        outSize = (int(float(reqSize[1])/im.size[1] * im.size[0]), reqSize[1])
    if im.size[0] > outSize[0]*2:
        filter = Image.ANTIALIAS
    else:
        filter = Image.BICUBIC
    r = im.resize((outSize[0]*2, outSize[1]*2), filter)
    r = r.rotate(angle, Image.BICUBIC, expand=1)
    r = r.resize((r.size[0]//2, r.size[1]//2), Image.ANTIALIAS)
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
        # PIL rotates counter-clockwise, angle is clockwise compass direction
        rotateAntialias(im, -angle).save(outPath)

def cacheIconSize(dir):
    paths = glob('%s/*' % dir)
    for p in paths:
        iconPrefix = os.path.splitext(os.path.basename(p))[0]
        im = Image.open(p)
        ICON_SIZE[iconPrefix] = list(im.size)

def getIconSize(iconPrefix):
    return ICON_SIZE[iconPrefix]
