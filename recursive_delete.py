#!/usr/bin/env python3

import sys
import os

import fsquery
import path_utils

def recursive_delete(path, filename):

    all_files = fsquery.makecontentlist(path, True, False, True, False, True, False, True, None)
    for f in all_files:
        bn = path_utils.basename_filtered(f)
        if bn == filename:
            os.unlink(f)

def puaq():
    print("Usage: %s file-to-delete" % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    path = os.getcwd()
    filename = (sys.argv[1])
    recursive_delete(path, filename)
