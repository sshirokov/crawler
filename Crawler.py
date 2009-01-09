#!/usr/bin/env python
import sys, re
from Browser import Browser

def search_object(object, name = None, value = None):
    def matcher(searcher):
        if callable(searcher): return searcher
        if searcher == None: return lambda value: True
        if type(searcher) == type(re.compile('')): return lambda value: re.match(searcher, value)
        if str(searcher) == searcher: return lambda value: searcher in value
        else: return lambda value: searcher == value
    if not name and not value: raise Exception("Must search by name or value")
    name, value = matcher(name), matcher(value)
    return [(i, getattr(object, i)) for i in dir(object) if name(i) and value(getattr(object, i))]

def make_chain(*functions, **kwargs):
    '''Return a function calling all the functions passed in sequence with the given params'''
    merge = kwargs.get('merge') or (lambda l: l)
    call_chain = lambda *args, **kwargs: [f(*args, **kwargs) for f in functions]
    return lambda *args, **kwargs: merge(call_chain(*args, **kwargs))
    

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
            map(do, links)
            total = sum(map(lambda link: Crawler(link, referer = self.seed).crawl(do, depth - 1, style), links))
        elif style == self.Styles.DEPTH_FIRST:
            def visit(link):
                do(link)
                return Crawler(link, referer = self.seed).crawl(do, depth - 1, style)
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
