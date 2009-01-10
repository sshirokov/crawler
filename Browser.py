#!/usr/bin/env python
import os, sys, re
import urllib
import urllib2
from BeautifulSoup import BeautifulSoup, Tag
from utils import matcher, listify, make_chain

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

    def links(self, page, exclude = False, require = None):
        exclude, require = map(lambda m: make_chain(map(matcher, listify(m)),
                                       merge = lambda returns: reduce(lambda a, b: bool(a) | bool(b), returns, True)),
                               [exclude, require])
        
        return BeautifulSoup(page).findAll(
            name = 'a',
            href = lambda value: exclude(value))#exclude(value))#require(value))# and not exclude(value))#href_predicate)

    def formInputs(self, page, form_index = 0, exclude = 'srch'):
        if page.__class__ == Tag: form = page
        else: form = self.forms(page, exclude)[form_index]
        return tuple([(i.get('name') or '', i.get('value') or '') for i in form('input')]) or ()

    def request(self, url, params = None):
        if params: params = urllib.urlencode(params)
        req = urllib2.Request(url, params, self.headers)
        return self.opener.open(req).read()
