#!/usr/bin/env python3

import sys
import os

import path_utils
import fsquery
import getcontents
import mvtools_exception

def convert_clementine_playlist_to_python_list(filename):

    contents = getcontents.getcontents(filename)
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
        track_found = location # in L16, there was no 'file://'
        #track_found = location[7:] # append but also remove the 'file://'
        track_found = track_found.replace("&amp;", "&") # clementine stuff.
        tracks.append(track_found)

        ls = le # advance to the next location

    return tracks

def proc(plfile):
    tracks = convert_clementine_playlist_to_python_list(plfile)
    i=0
    for t in tracks:
        i+=1
        if not os.path.exists(t):
            print("(index %s): %s of playlist %s does not exist!" % (i, path_utils.basename_filtered(t), path_utils.basename_filtered(plfile)))
    print("\n")

def puaq(selfhelp): # print usage and quit
    print("Usage: %s path_with_playlists" % path_utils.basename_filtered(__file__))
    if selfhelp:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        puaq(False)

    path_playlists = os.path.abspath(sys.argv[1])
    if not os.path.exists(path_playlists):
        print("%s does not exist." % path_playlists)
        sys.exit(1)
    
    v, r = fsquery.makecontentlist(path_playlists, False, False, True, False, False, False, True, "xspf")
    if not v:
        raise mvtools_exception.mvtools_exception(r)
    playlists = r
    for p in playlists:
        print("Processing %s..." % p)
        proc(p)
