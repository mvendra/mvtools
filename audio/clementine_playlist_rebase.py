#!/usr/bin/env python

import sys
import os
from subprocess import call

def puaq(): # print usage and quit
    print("Usage: %s path_with_playlists string_to_find string_to_replace_with" % os.path.basename(__file__))
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
    str_find = sys.argv[2]
    str_rep = sys.argv[3]
    
    playlists = os.listdir(path_playlists)
    for p in playlists:
        proc(os.path.join(path_playlists, p), str_find, str_rep)
 
