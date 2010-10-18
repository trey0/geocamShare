#!/usr/bin/env python

import re
import sys

from share2.shareTracking.models import Resource

def doit(opts, args):
    for fname in args:
        f = file(fname, 'r')
        for line in f:
            # remove comments
            line = re.sub(r'\s*\#.*$', '', line)
            # skip blank lines
            if line == '':
                continue
            # userName, displayName in format: 'jdoe:John Doe'
            userName, displayName = [s.strip() for s in line.split(':', 1)]
            matches = Resource.objects.filter(userName=userName)
            if matches:
                resource = matches[0]
                resource.displayName = displayName
                resource.save()
            else:
                print >>sys.stderr, 'warning: no resource with userName "%s"' % userName

def main():
    import optparse
    parser = optparse.OptionParser('''usage: %prog <names.txt> [moreNames.txt] ...

Takes a bulk file of (userName, displayName) pairs where each line is in
the format 'jdoe:John Doe, Some Unit'.  Finds the shareTracking Resource
with that userName and assigns it the specified displayName.''')
    opts, args = parser.parse_args()

    if not args:
        parser.error('expected at least one argument')
    doit(opts, args)

if __name__ == '__main__':
    main()
