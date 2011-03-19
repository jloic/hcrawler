#!/usr/bin/env python
# -*- coding: utf8 -*-


import urllib2
imporm urllib
import cookielib
import re
import datetime
import simplejson

from pyquery import PyQuery 
import mimetools, mimetypes

url_re = re.compile(r'http://.[^/]*')

class HTTPCrawler():
    def __init__(self, base_url):
        self.base_url = base_url

        self.cookie_jar = cookielib.LWPCookieJar()
        cj = self.cookie_jar

        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

        #usefull for django
        self.add_trailing_slash = True
        
        self.start_timer = datetime.datetime.now()
        self.duration = datetime.timedelta(0,0)
        
    def soup_post(self, url, args= {}):
        return self.soup(url, args, True)

    def soup_get(self, url, args = {}):
        return self.soup(url, args, False)
    
    def json_post(self, url, args = {}, files = {}):
        c = self.soup(url, args, True, False, files)
        return simplejson.loads(c)

    def soup(self, url, args = {}, POST = True, to_soup = True, files = {}):
        self.start_timer = datetime.datetime.now()

        data = urllib.urlencode(args)
        
        #take the http://.*/ part off
        url = url_re.sub('', url) 

        if self.add_trailing_slash and url[-1] != '/':
                url += '/'

        if files:
            req = self.post_multipart(self.base_url, url, args, files)
        else:
            if POST:   
                if data:
                    req = urllib2.Request(self.base_url + url, data)
                else:
                    req = urllib2.Request(self.base_url + url)
            else:
                #GET

                req = urllib2.Request(self.base_url + url + '?' + urllib.urlencode(args))

        r = self.opener.open(req)

        content = r.read()
        content = unicode(content.decode('utf-8'))
        content = content.replace('xmlns="http://www.w3.org/1999/xhtml"', '')

        self.duration = datetime.datetime.now() - self.start_timer

        if to_soup:
            return PyQuery(content)
        else:
            return content

    def post_multipart(self, host, selector, fields, files):
        content_type, body = self.encode_multipart_formdata(fields, files)
        headers = {'Content-Type': content_type,
                   'Content-Length': str(len(body))}
        r = urllib2.Request("%s%s" % (host, selector), body, headers)
        return r

    def encode_multipart_formdata(self, fields, files):
        boundary = mimetools.choose_boundary()
        crlf = '\r\n'

        encoded_data = []

        for key, value in fields.items():
            encoded_data.append('--' + boundary)
            encoded_data.append('Content-Disposition: form-data; name="%s"' % key)
            encoded_data.append('')
            encoded_data.append(value)

        for (key, filename, value) in files:
            encoded_data.append('--' + boundary)
            encoded_data.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
            encoded_data.append('Content-Type: %s' % self.get_content_type(filename))
            encoded_data.append('')
            encoded_data.append(value)

        encoded_data.append('--' + boundary + '--')
        encoded_data.append('')

        body = crlf.join(encoded_data)
        content_type = 'multipart/form-data; boundary=%s' % boundary

        return content_type, body

    def get_content_type(self, filename):
        return mimetypes.guess_type(filename)[0] or 'application/octet-stream'


if __name__ == '__main__':
    c = HTTPCrawler('http://vflow.com.br')
    s = c.soup('/') 
    for i in s('.headlink > a'):
        print 'Menu ', i.text
