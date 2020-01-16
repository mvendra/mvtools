#!/usr/bin/env python3

import sys
import os

import fsquery
import prefix_checker

def prefix_checker_onelevel_caller(path, prefix_size):
    r = True
    subcats = fsquery.makecontentlist(path, False, False, True, False, False, True, None)
    for c in subcats:
        r &= prefix_checker.prefix_checker(c, prefix_size)
    return r

def puaq():
    print("Usage: %s prefix_size [target-dir]" % os.path.basename(__file__))
    sys.exit(1)

if __name__ == "__main__":

    td = os.getcwd()
    ps = ""

    if len(sys.argv) < 2:
        puaq()

    ps = sys.argv[1]

    if len(sys.argv) > 2:
        td = sys.argv[2]

    if prefix_checker_onelevel_caller(td, int(ps)):
        sys.exit(0)
    else:
        sys.exit(1)
