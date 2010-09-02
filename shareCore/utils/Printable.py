# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

class Printable(object):
    """If x is an instance of a class inheriting from Printable, 'repr(x)'
    and 'print x' give useful debug output.  Idea similar to Perl Data::Dumper."""
    def getPrintable(self):
        svars = vars(self).items()
        svars.sort()
        return ('%s.%s(%s%s)' % (self.__class__.__module__,
                                 self.__class__.__name__,
                                 self.getPrefix(),
                                 ', '.join(['%s=%s' % (k, repr(v))
                                            for k, v in svars])))
    def getPrefix(self):
        return ''
    def __repr__(self):
        return self.getPrintable()
