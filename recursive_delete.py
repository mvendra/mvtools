#!/usr/bin/env python3

import sys
import os

import path_utils
import fsquery
import mvtools_exception

def recursive_delete(path, filename):

    v, r = fsquery.makecontentlist(path, True, False, True, False, True, False, True, None)
    if not v:
        raise mvtools_exception.mvtools_exception(r)
    all_files = r
    for f in all_files:
        bn = path_utils.basename_filtered(f)
        if bn == filename:
            os.unlink(f)

def puaq(selfhelp):
    print("Usage: %s file-to-delete" % path_utils.basename_filtered(__file__))
    if selfhelp:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq(False)

    path = os.getcwd()
    filename = (sys.argv[1])
    recursive_delete(path, filename)
