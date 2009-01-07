#!/usr/bin/env python
from Browser import Browser

class Crawler(Browser):
    def __init__(self, seed):
        super(Crawler, self).__init__()
        self.addHeader("Host", "www.google.com")
        self.addHeader("Accept", "text/html")
        self.addHeader("Referer", "http://www.google.com")

        self.request("http://www.google.com") #TODO: Extract from seed
        self.seed = seed

    def crawl(self):
        return self.links(self.request(self.seed),
                          exclude = 'google\.com',
                          require = '^http')
        
def main():
    crawl = Crawler('http://www.google.com/search?hl=en&q=submit+comment&btnG=Google+Search&aq=f&oq=')
    print crawl.crawl()
if __name__ == '__main__': main()
