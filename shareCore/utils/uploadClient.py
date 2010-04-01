
from share2.shareCore.util import MimeMultipartFormData

def uploadImage(self, url, imageName, attributes):
    #cookieProcessor = urllib2.HTTPCookieProcessor()
    opener = urllib2.build_opener() # (cookieProcessor)
    headers = {'User-Agent': 'GeoCam Mobile'}
    url = '%s/upload/%s/' % (url, attributes['userName'])
    
    multipart = MimeMultipartFormData.MimeMultipartFormData()
    for k, v in attributes.iteritems():
        multipart[k] = v
    multipart.addFile(name='photo',
                      filename=imageName,
                      data=file(imageName, 'r').read(),
                      contentType='image/jpeg')
    
    h2 = headers.copy()
    h2.update(multipart.getHeaders())
    req = urllib2.Request(url=url,
                          data=multipart.getPostData(),
                          headers=h2)
    resp = opener.open(req)
    return resp
