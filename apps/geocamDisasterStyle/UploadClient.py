# __BEGIN_LICENSE__
# Copyright (C) 2008-2010 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# __END_LICENSE__

import os
import urllib2
import tempfile
import re
import base64

import PIL.Image

from geocamUtil import MimeMultipartFormData

class UploadClient:
    def __init__(self, url, userName='root', password=''):
        self.url = url
        self.userName = userName
        self.password = password

        self.imageName = None
        self.im = None

    def addAuthentication(self, headers, url):
        '''update headers and return transformed url to support share
        basic authentication.'''
        if self.password:
            # ensure https so we don't send password unencrypted
            assert url.startswith('http')
            url = re.sub(r'^http:', 'https:', url)
            # new-style url which does not include userName
            url = '%s/upload-m/' % url
            # add pre-emptive basic authentication
            auth = base64.encodestring('%s:%s' % (self.userName, self.password))[:-1]
            headers['Authorization'] = 'Basic %s' % auth
        else:
            # no password means use old-style upload
            url = '%s/upload/%s/' % (url, self.userName)
        return url

    def uploadImage(self, imageName, attributes, downsampleFactor=1):
        if downsampleFactor != 1:
            im = PIL.Image.open(imageName)
            w, h = im.size
            thRes = (w//downsampleFactor, h//downsampleFactor)
            im.thumbnail(thRes, PIL.Image.ANTIALIAS)
            fd, tmpName = tempfile.mkstemp('uploadImageThumb.jpg')
            os.close(fd)
            im.save(tmpName)
            del im
            imageData = file(tmpName, 'r').read()
            os.unlink(tmpName)
        else:
            imageData = file(imageName, 'r').read()

        #cookieProcessor = urllib2.HTTPCookieProcessor()
        opener = urllib2.build_opener() # (cookieProcessor)
        headers = {'User-Agent': 'GeoCam Upload Tester'}

        multipart = MimeMultipartFormData.MimeMultipartFormData()
        for k, v in attributes.iteritems():
            multipart[k] = v
        multipart.addFile(name='photo',
                          filename=os.path.basename(imageName),
                          data=imageData,
                          contentType='image/jpeg')

        h2 = headers.copy()
        h2.update(multipart.getHeaders())
        url = self.addAuthentication(h2, self.url)
        req = urllib2.Request(url=url,
                              data=multipart.getPostData(),
                              headers=h2)
        resp = opener.open(req)
        return resp

    def uploadTrack(self, url, trackName, attributes=None):
        trackData = file(trackName, 'r').read()

        if attributes == None:
            attributes = dict(trackUploadProtocolVersion='1.0')

        #cookieProcessor = urllib2.HTTPCookieProcessor()
        opener = urllib2.build_opener() # (cookieProcessor)
        headers = {'User-Agent': 'GeoCam Upload Tester'}
        url = '%s/track' % self.url

        multipart = MimeMultipartFormData.MimeMultipartFormData()
        for k, v in attributes.iteritems():
            multipart[k] = v
        multipart.addFile(name='gpxFile',
                          filename=os.path.basename(trackName),
                          data=trackData,
                          contentType='text/xml')

        h2 = headers.copy()
        h2.update(multipart.getHeaders())
        url = self.addAuthentication(h2, url)
        req = urllib2.Request(url=url,
                              data=multipart.getPostData(),
                              headers=h2)
        resp = opener.open(req)
        return resp
