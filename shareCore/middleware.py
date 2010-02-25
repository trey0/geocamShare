
import sys
import traceback

class LogErrorsMiddleware(object):
    """Makes exceptions thrown within the django app print debug information
    to stderr so that it shows up in the Apache error log."""
    def process_exception(self, req, exception):
        errClass, errObject, errTB = sys.exc_info()[:3]
        traceback.print_tb(errTB)
        print >>sys.stderr, '%s.%s: %s' % (errClass.__module__,
                                           errClass.__name__,
                                           str(errObject))
