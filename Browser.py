#!/usr/bin/env python
import os, sys, re
import urllib
import urllib2
from BeautifulSoup import BeautifulSoup, Tag

class Browser(object):
    def __init__(self, ua = None):
        self.headers = { 
            'User-Agent' : ua or 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)',
        }
        
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        urllib2.install_opener(self.opener)

    def addHeader(self, name, value):
        self.headers.update({name: value})
        return self.headers

    def removeHeader(self, name):
        return self.headers.pop(name)
        
    def forms(self, page, exclude = 'srch'):
        return BeautifulSoup(page).findAll(
            name = 'form',
            action = lambda value: exclude == None or not re.search(exclude, value, re.IGNORECASE)
        )

    def links(self, page, exclude = None, require = None):
        def href_predicate(href):
            reply = True
            if not href: return False
            if type(exclude) == list:
                reply &= reduce(lambda a, b: a & b,
                                [bool(not re.search(case, href)) for case in exclude])
            else:
                if exclude: reply &= bool(not re.search(exclude, href))
            
            if type(require) == list: 
                reply &= reduce(lambda a, b: a & b,
                                [bool(not re.search(case, href)) for case in require])
            else:
                if require: reply &= bool(re.search(require, href))
            return reply
        
        return BeautifulSoup(page).findAll(
            name = 'a',
            href = href_predicate)

    def formInputs(self, page, form_index = 0, exclude = 'srch'):
        if page.__class__ == Tag: form = page
        else: form = self.forms(page, exclude)[form_index]
        return tuple([(i.get('name') or '', i.get('value') or '') for i in form('input')]) or ()

    def request(self, url, params = None):
        if params: params = urllib.urlencode(params)
        req = urllib2.Request(url, params, self.headers)
        return self.opener.open(req).read()
