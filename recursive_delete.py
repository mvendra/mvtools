#!/usr/bin/env python3

import sys
import os

import fsquery

def recursive_delete(path, filename):

    all_files = fsquery.makecontentlist(path, True, True, False, True, False, True, None)
    for f in all_files:
        bn = os.path.basename(f)
        if bn == filename:
            os.unlink(f)

def puaq():
    print("Usage: %s file-to-delete" % os.path.basename(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    path = os.getcwd()
    filename = (sys.argv[1])
    recursive_delete(path, filename)
