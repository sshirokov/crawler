#!/usr/bin/env python
import sys, re
from urllib2 import HTTPError
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
        print "Constructed(seed = '%s', referer = '%s')" % (seed, referer or "None")
        
    def update_referer(self, url, params = None):
        self.addHeader("Referer", url)

    def crawl(self, do, depth = 1, style = Styles.BREADTH_FIRST):
        if depth <= 0:
            print "Exiting recursion with [%s]" % self.seed
            return 0
        print "crawling('%(seed)s', depth = %(depth)d, style = %(style)s)" % {
            'seed': self.seed,
            'depth': depth,
            'style': list(search_object(self.Styles, value = style).pop())[0]
        }
        links = self.links(self.request(self.seed),
                          exclude = ['google\.com',
                                     'q=cache:',],
                          require = '^http')
        links = [link['href'] for link in links if link.get('href')]
            
        if style == self.Styles.BREADTH_FIRST:
            def visit(link):
                try:
                    return Crawler(link, referer = self.seed).crawl(do, depth - 1, style)
                except HTTPError, e:
                    sys.stderr.write("Warning: Error(%s) on '%s'" % (e, link))
                    return 0
            map(do, links)
            total = sum(map(visit, links))
        elif style == self.Styles.DEPTH_FIRST:
            def visit(link):
                do(link)
                try:
                    return Crawler(link, referer = self.seed).crawl(do, depth - 1, style)
                except HTTPError, e:
                    sys.stderr.write("Warning: Error(%s) on '%s'" % (e, link))
                    return 0
            total = sum(map(visit, links))
            
        return len(links) + total
        
def main():
    def doer(value):
        print "Doing [%s]" % value
    crawler = Crawler('http://www.google.com/search?hl=en&q=submit+comment&btnG=Google+Search&aq=f&oq=')
    if len(sys.argv) > 1: limit = int(sys.argv[1])
    else: limit = 1 
    print "Found %d links" % crawler.crawl(doer, depth = limit, style = Crawler.Styles.BREADTH_FIRST)
if __name__ == '__main__': main()
