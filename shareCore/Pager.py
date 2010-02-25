
import math

from django.utils.safestring import mark_safe

class Pager:
    def __init__(self, baseUrl, items, pageSize, pageNum):
        self.baseUrl = baseUrl
        self.items = items
        self.pageSize = pageSize
        self.pageNum = pageNum
        self.numPages = math.ceil(float(len(items)) / pageSize)
    def slice(self):
        return self.items[(self.pageSize*(self.pageNum-1)):(self.pageSize*self.pageNum)]
    def pager(self):
        ret = []
        if self.pageNum > 1:
            ret.append('<a href="%s/%d/">&laquo; previous</a>' % (self.baseUrl, self.pageNum-1))
            ret.append('<a href="%s/1/">1</a>' % (self.baseUrl))
        if self.pageNum > 2:
            if self.pageNum > 3:
                ret.append('...')
            ret.append('<a href="%s/%d/">%d</a>' % (self.baseUrl, self.pageNum-1, self.pageNum-1))
        if self.numPages > 1:
            ret.append('%d' % self.pageNum)
        if self.pageNum < self.numPages-1:
            ret.append('<a href="%s/%d/">%d</a>' % (self.baseUrl, self.pageNum+1, self.pageNum+1))
            if self.pageNum < self.numPages-2:
                ret.append('...')
        if self.pageNum < self.numPages:
            ret.append('<a href="%s/%d/">%d</a>' % (self.baseUrl, self.numPages, self.numPages))
            ret.append('<a href="%s/%d/">next &raquo;</a>' % (self.baseUrl, self.pageNum+1))
        if ret:
            return mark_safe('pages:&nbsp;' + '&nbsp;'.join(ret))
        else:
            return ''
