# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

import os
import stat
import errno
import traceback

class Builder:
    def __init__(self, verbose=0):
        self.numMade = 0
        self.numRules = 0
        self.verbose = verbose

    def applyRule(self, dst, srcs, func):
        self.numRules += 1
        try:
            dstTime = os.stat(dst)[stat.ST_MTIME]
        except OSError, e:
            if e.errno == errno.ENOENT:
                dstTime = 0
            else:
                raise
        maxSrcTime = 0
        for src in srcs:
            try:
                srcTime = os.stat(src)[stat.ST_MTIME]
            except OSError, e:
                traceback.print_exc()
                print ('[could not stat source file %s in rule to generate %s]'
                       % (src, dst))
                sys.exit(1)
            maxSrcTime = max(maxSrcTime, srcTime)
        if maxSrcTime > dstTime:
            if self.verbose > 1:
                print '[building: %s]' % dst
            func()
            self.numMade += 1
        else:
            if self.verbose > 0:
                print '[up to date: %s]' % dst

    def finish(self):
        print 'builder: %d of %d files were up to date' % (self.numRules - self.numMade, self.numRules)
