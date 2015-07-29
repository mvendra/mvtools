#!/usr/bin/env python

import urllib

if __name__ == "__main__":
    cont = urllib.urlopen("http://www.amazon.com/Templates-Complete-Guide-David-Vandevoorde/dp/0201734842/ref=sr_1_1?ie=UTF8&qid=1438170638&sr=8-1&keywords=c%2B%2B+templates")

    #print(cont)

    with open("/home/mateus/nuke/page.html", "w") as f:
        f.write(cont.read())
    

