
import os
import urllib2
import tempfile

import PIL.Image

import MimeMultipartFormData

def uploadImage(url, imageName, attributes, downsampleFactor=1):
    if downsampleFactor != 1:
        im = PIL.Image.open(imageName)
        w, h = im.size
        thRes = (w//downsampleFactor, h//downsampleFactor)
        im.thumbnail(thRes, PIL.Image.ANTIALIAS)
        if 0:
            imageData = im.tostring()
        else:
            fd, tmpName = tempfile.mkstemp('uploadImageThumb.jpg')
            os.close(fd)
            im.save(tmpName)
            imageData = file(tmpName, 'r').read()
        del im
    else:
        imageData = file(imageName, 'r').read()

    #cookieProcessor = urllib2.HTTPCookieProcessor()
    opener = urllib2.build_opener() # (cookieProcessor)
    headers = {'User-Agent': 'GeoCam Mobile'}
    url = '%s/upload/%s/' % (url, attributes['userName'])
    
    multipart = MimeMultipartFormData.MimeMultipartFormData()
    for k, v in attributes.iteritems():
        multipart[k] = v
    multipart.addFile(name='photo',
                      filename=os.path.basename(imageName),
                      data=imageData,
                      contentType='image/jpeg')
    
    h2 = headers.copy()
    h2.update(multipart.getHeaders())
    req = urllib2.Request(url=url,
                          data=multipart.getPostData(),
                          headers=h2)
    resp = opener.open(req)
    return resp
