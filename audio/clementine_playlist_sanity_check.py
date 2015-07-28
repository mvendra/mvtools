#!/usr/bin/env python

import sys
import os
import fsquery

def puaq(): # print usage and quit
    print("Usage: %s path_with_playlists" % os.path.basename(__file__))
    sys.exit(1)

def proc(plfile):
    pass

if __name__ == "__main__":
    if len(sys.argv) < 2:
        puaq()

    path_playlists = os.path.abspath(sys.argv[1])
    if not os.path.exists(path_playlists):
        print("%s does not exist." % path_playlists)
        sys.exit(1)
    
    playlists = fsquery.makecontentlist(path_playlists, False, True, False, False, False, "xspf")
    for p in playlists:
        print("Processing %s..." % p)
        proc(p)
 
