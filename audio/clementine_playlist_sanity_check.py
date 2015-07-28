#!/usr/bin/env python

import sys
import os
import fsquery

def puaq(): # print usage and quit
    print("Usage: %s path_with_playlists" % os.path.basename(__file__))
    sys.exit(1)

def getcontents(thefile):
    contents = ""
    with open(thefile, "r") as f:
        contents = f.read()
    return contents

def convert_clementine_playlist_to_python_list(filename):

    contents = getcontents(filename)
    if len(contents) == 0:
        print("%s is empty! Aborting." % filename)
        sys.exit(1)

    tracks = []

    ls = 0
    le = 0
    while True:
        ls = contents.find("<location>", ls)
        if ls == -1:
            # we are done
            break

        le = contents.find("</location>", ls+1)
        if le == -1:
            print("Malformatted playlist contents detected. Check starting at offset %s, playlist %s." % (filename, ls))

        location = contents[ls+len("<location>"):le]
        tracks.append(location)

        ls = le # advance to the next location

    return tracks

def proc(plfile):
    tracks = convert_clementine_playlist_to_python_list(plfile)
    print(tracks)

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
 
