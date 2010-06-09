
import os
import time
import random
import shutil
from glob import glob
import traceback
import sys

from django.conf import settings

from share2.shareCore import utils

def getTempName(prefix, suffix=''):
    return '%s/%s-%s-%s%s' % (settings.TMP_DIR,
                              prefix,
                              time.strftime('%Y-%m-%d-%H%M'),
                              '%04x' % random.getrandbits(16),
                              suffix)

def deleteStaleFiles():
    files = glob('%s/*' % settings.TMP_DIR)
    now = time.time()
    for f in files:
        if (now - os.stat(f).st_ctime > settings.DELETE_TMP_FILE_WAIT_SECONDS
            and not f.endswith('/README.txt')):
            try:
                os.unlink(f)
            except OSError, e:
                traceback.print_exc()
                print >>sys.stderr, '[tempfiles.deleteStaleFiles: could not unlink %s]' % f

def initZipDir(prefix):
    deleteStaleFiles()
    zipDir = getTempName(prefix)
    utils.mkdirP(zipDir)
    return zipDir

def finishZipDir(zipDir):
    zipFile = '%s.zip' % zipDir
    oldDir = os.getcwd()
    os.chdir(os.path.dirname(settings.TMP_DIR))
    os.system('zip -r %s %s' % (zipFile, os.path.basename(zipDir)))
    os.chdir(oldDir)
    shutil.rmtree(zipDir)
    return zipFile
