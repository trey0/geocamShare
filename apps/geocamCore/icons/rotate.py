#!/usr/bin/env python
# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

import PIL.Image as Image
from PIL import ImageChops
import os
import re
from glob import glob

REQ_SIZE = (48, 48)

def getbbox(im, threshold):
    '''like Image.getbbox(), but instead of cropping everything that is exactly 0,
    crops everything with the alpha channel below @threshold'''
    a = im.split()[-1]
    thresholded = ImageChops.add(a, ImageChops.constant(im, 0), 1.0, -threshold)
    return a.getbbox()

def rotateAntialias(im, angle, reqSize=REQ_SIZE):
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
    r = r.crop(getbbox(r, 128))
    return r

def copyThumbnail(inPath, outPath, reqSize):
    im = Image.open(inPath)
    im.thumbnail(reqSize, Image.ANTIALIAS)
    im.save(outPath)

def copyThumbnails(builder, inDir, outDir, nameTransform=None, reqSize=REQ_SIZE):
    icons = glob('%s/*.png' % inDir) + glob('%s/*.jpg' % inDir)
    for inPath in icons:
        base, ext = os.path.splitext(os.path.basename(inPath))
        if nameTransform != None:
            base = nameTransform(base)
        outPath = '%s/%s%s' % (outDir, base, ext)
        builder.applyRule(outPath, [inPath],
                          lambda: copyThumbnail(inPath, outPath, reqSize))

def getOutPath(imPath, outputDir, angle):
    base, ext = os.path.splitext(os.path.basename(imPath))
    base = re.sub(r'Point$', '', base)
    return os.path.join(outputDir, '%s%03d%s' % (base, angle, ext))

def buildAllDirections(builder, imPath, outputDir):
    firstOutFile = getOutPath(imPath, outputDir, 0)
    builder.applyRule(firstOutFile, [imPath],
                      lambda: generateAllDirections(imPath, outputDir))

def generateAllDirections(imPath, outputDir):
    im = Image.open(imPath)
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)
    for angle in xrange(0, 360, 10):
        outPath = getOutPath(imPath, outputDir, angle)
        # PIL rotates counter-clockwise, angle is clockwise compass direction
        rotateAntialias(im, -angle).save(outPath)
