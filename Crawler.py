#!/usr/bin/env python
import re
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
    if kwargs.get('merge'): merge = kwargs['merge']
    else: merge = lambda l: l
    call_chain = lambda *args, **kwargs: [f(*args, **kwargs) for f in functions]
    return lambda *args, **kwargs: merge(call_chain(*args, **kwargs))
    

class Crawler(Browser):
    class Styles:
        DEPTH_FIRST = 1
        BREADTH_FIRST = 2
        
    def __init__(self, seed):
        super(Crawler, self).__init__()
        self.addHeader("Host", "www.google.com")
        self.addHeader("Accept", "text/html")
        self.addHeader("Referer", "http://www.google.com")

        self.request("http://www.google.com") #TODO: Extract from seed
        self.seed = seed

    def crawl(self, do, depth = 1, style = Styles.BREADTH_FIRST):
        if depth <= 0:
            print "Exiting recursion with [%s]" % self.seed
            return list()
        print "crawling('%(seed)s', depth = %(depth)d, style = %(style)s)" % {
            'seed': self.seed,
            'depth': depth,
            'style': list(search_object(self.Styles, value = style).pop())[0]
        }
        do(self.seed)
        links = self.links(self.request(self.seed),
                          exclude = 'google\.com',
                          require = '^http')
            
        if style == self.Styles.BREADTH_FIRST:
            map(do, links)
            map(lambda link: Crawler(link).crawl(do, depth - 1, style), links)
        elif style == self.Styles.DEPTH_FIRST:
            def visit(link):
                do(link)
                Crawler(link).crawl(do, depth - 1, style)
            map(visit, links)
            
        return list()
        
def main():
    def doer(value):
        print "Doing [%s]" % value
    crawl = Crawler('http://www.google.com/search?hl=en&q=submit+comment&btnG=Google+Search&aq=f&oq=')
    print "Found %d links" % len(crawl.crawl(doer, style = Crawler.Styles.DEPTH_FIRST))
if __name__ == '__main__': main()
