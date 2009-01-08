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

    def crawl(self, depth = 1, style = Styles.BREADTH_FIRST):
        return self.links(self.request(self.seed),
                          exclude = 'google\.com',
                          require = '^http')
        
def main():
    crawl = Crawler('http://www.google.com/search?hl=en&q=submit+comment&btnG=Google+Search&aq=f&oq=')
    print crawl.crawl()
if __name__ == '__main__': main()
