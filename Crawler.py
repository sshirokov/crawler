#!/usr/bin/env python
import sys, re
from urllib2 import HTTPError, URLError
from Browser import Browser
from utils import search_object, make_chain

class Crawler(Browser):
    class Styles:
        DEPTH_FIRST = 1
        BREADTH_FIRST = 2
        
    def __init__(self, seed, referer = None):
        super(Crawler, self).__init__()
        self.addHeader("Host", re.match('.+//([^/]+)?/{0,1}.+$', seed).group(1))
        self.addHeader("Accept", "text/html")
        if referer: self.addHeader("Referer", referer)

        self.seed = seed
        self.request = make_chain(self.request, self.update_referer, merge = lambda returns: returns[0])
        
    def update_referer(self, url, params = None):
        self.addHeader("Referer", url)

    def crawl(self, do, **kwargs):
        return len(map(do, self.generate(**kwargs)))

    def generate(self, depth = 1, style = Styles.BREADTH_FIRST, exclude = False, require = None):
        if depth == None: depth = -1
        if depth == 0: return
        
        try: links = self.links(self.request(self.seed), exclude, require)
        except URLError, e: links = []
        except HTTPError, e: links = []
            
        links = [link['href'] for link in links if link.get('href')]
            
        if style == self.Styles.BREADTH_FIRST:
            for link in links:
                yield link
            for link in links:
                for sublink in Crawler(link, referer = self.seed).generate(depth = depth - 1, style = style, exclude = exclude, require = require):
                    yield link
        elif style == self.Styles.DEPTH_FIRST:
            for link in links:
                yield link
                for sublink in Crawler(link, referer = self.seed).generate(depth = depth - 1, style = style, exclude = exclude, require = require):
                    yield sublink
        
def main():
    def doer(link):
        #print "Doing [%s]" % link
        pass
    crawler = Crawler('http://www.google.com/search?hl=en&q=submit+comment&btnG=Google+Search&aq=f&oq=')
    if len(sys.argv) > 1: limit = int(sys.argv[1])
    else: limit = 1 
    print "Found %d links" % crawler.crawl(do = doer,
                                           depth = limit,
                                           style = Crawler.Styles.BREADTH_FIRST,
                                           exclude = ['q=cache:'],
                                           require = re.compile('^http'))
    print "Generated %d links" % len([link for link in crawler.generate(depth = limit,
                                                                        style = Crawler.Styles.BREADTH_FIRST,
                                                                        exclude = ['q=cache:'],
                                                                        require = re.compile('^http'))])
if __name__ == '__main__': main()
