#!/usr/bin/env python3

import sys
import os
from subprocess import call

import fsquery
import path_utils

def puaq(): # print usage and quit
    print("Usage: %s path_with_playlists string_to_find string_to_replace_with" % path_utils.basename_filtered(__file__))
    sys.exit(1)

def proc(plfile, str_find, str_rep):

    str_find = str_find.replace("/", "\\/")
    str_rep = str_rep.replace("/", "\\/")
    sed_opts = "s/%s/%s/g" % (str_find, str_rep)
    the_cmd = ["sed", "-i", sed_opts, plfile]

    call(the_cmd)

if __name__ == "__main__":
    if len(sys.argv) < 4:
        puaq()

    path_playlists = os.path.abspath(sys.argv[1])
    if not os.path.exists(path_playlists):
        print("%s does not exist." % path_playlists)
        sys.exit(1)
    str_find = sys.argv[2]
    str_rep = sys.argv[3]
    
    playlists = fsquery.makecontentlist(path_playlists, False, True, False, False, False, True, "xspf")
    for p in playlists:
        print("Processing %s..." % p)
        proc(p, str_find, str_rep)
 
