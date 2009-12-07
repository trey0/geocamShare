
import os

from django.conf import settings

from share2.share.models import LidarScan, LidarPano, Mic, PancamPano, ALL_TASKS_DICT
from share2.share.indexlib import RequestIdPath, getIdSuffix

def doit(opts):
    if opts.clean:
        print 'got -c option, deleting old data before indexing'
        for dpType in ALL_TASKS_DICT.values():
            dpType.objects.all().delete()
    requestIds = os.listdir(settings.DATA_DIR)
    reqPaths = [RequestIdPath('k10black', '20090626', id) for id in requestIds]
    for pat in settings.SKIP_PATTERNS:
        reqPaths = [p for p in reqPaths if pat not in p.requestId]
    for p in reqPaths:
        idSuffix = getIdSuffix(p.requestId)
        if idSuffix.startswith('LS'):
            td = LidarScan()
        elif idSuffix.startswith('LP'):
            td = LidarPano()
        elif idSuffix.startswith('P'):
            td = PancamPano()
        elif idSuffix.startswith('MIC'):
            td = Mic()
        else:
            print 'skipping requestId with unknown suffix %s' % idSuffix
            continue
        td.process(p)
        td.save()

def main():
    import optparse
    parser = optparse.OptionParser('usage: %prog')
    parser.add_option('-c', '--clean',
                      default=False, action='store_true',
                      help='Clean tables before indexing')
    opts, args = parser.parse_args()
    doit(opts)

if __name__ == '__main__':
    main()
