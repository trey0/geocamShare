# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

import random, StringIO

class MimeMultipartFormData:
    def __init__(self, **kwargs):
        self._boundary = '%032x' % random.getrandbits(128)
        self._fields = kwargs.get('fields', {})
        self._files = kwargs.get('files', [])
    def __getitem__(self, k):
        return self._fields[k]
    def __setitem__(self, k, v):
        self._fields[k] = v
    def getHeaders(self):
        return {'Content-Type': 'multipart/form-data; boundary=%s' % self._boundary}
    def addFile(self, name, filename, data, contentType='text/plain'):
        self._files.append((name, filename, data, contentType))
    def writePostData(self, stream):
        for k, v in self._fields.iteritems():
            stream.write('\r\n--%s\r\n' % self._boundary)
            stream.write('Content-Disposition: form-data; name="%s"\r\n' % k)
            stream.write('Content-Type: text/plain\r\n')
            stream.write('\r\n')
            stream.write(v)
        for name, filename, data, contentType in self._files:
            stream.write('\r\n--%s\r\n' % self._boundary)
            stream.write('Content-Disposition: form-data; name="%s"; filename="%s"\r\n'
                         % (name, filename))
            stream.write('Content-Type: %s\r\n' % contentType)
            stream.write('\r\n')
            stream.write(data)
        stream.write('\r\n--%s--\r\n' % self._boundary)
    def getPostData(self):
        stream = StringIO.StringIO()
        self.writePostData(stream)
        return stream.getvalue()
