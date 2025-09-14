#!/usr/bin/env python

import sys
import os
from subprocess import call

import path_utils
import fsquery
import mvtools_exception

def proc(plfile, str_find, str_rep):

    str_find = str_find.replace("/", "\\/")
    str_rep = str_rep.replace("/", "\\/")
    sed_opts = "s/%s/%s/g" % (str_find, str_rep)
    the_cmd = ["sed", "-i", sed_opts, plfile]

    call(the_cmd)

def puaq(selfhelp): # print usage and quit
    print("Usage: %s path_with_playlists string_to_find string_to_replace_with" % path_utils.basename_filtered(__file__))
    if selfhelp:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 4:
        puaq(False)

    path_playlists = os.path.abspath(sys.argv[1])
    if not os.path.exists(path_playlists):
        print("%s does not exist." % path_playlists)
        sys.exit(1)
    str_find = sys.argv[2]
    str_rep = sys.argv[3]
    
    v, r = fsquery.makecontentlist(path_playlists, False, False, True, False, False, False, True, "xspf")
    if not v:
        raise mvtools_exception.mvtools_exception(r)
    playlists = r
    for p in playlists:
        print("Processing %s..." % p)
        proc(p, str_find, str_rep)
 