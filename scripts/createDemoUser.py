#!/usr/bin/env python

from django.contrib.auth.models import User

def doit(opts, args):
    for arg in args:
        username = 'phone_'+arg
        numMatches = User.objects.filter(username=username).count()
        if numMatches:
            print 'skipping %s, user exists' % arg
        user = User.objects.create_user(username,
                                        '%s@example.com' % arg,
                                        opts.password)
        user.first_name = 'Phone ' + arg.upper()
        user.last_name = 'group'
        user.save()

def main():
    import optparse
    parser = optparse.OptionParser()
    parser.add_option('-p', '--password',
                      help='password to use for new accounts')
    opts, args = parser.parse_args()
    doit(opts, args)

if __name__ == '__main__':
    main()
