#!/usr/bin/env python3

import sys
import os

import path_utils
import fsquery
import mvtools_exception
import prefix_checker

def prefix_checker_onelevel_caller(path, prefix_size):
    v, r = fsquery.makecontentlist(path, False, False, False, True, False, False, True, None)
    if not v:
        raise mvtools_exception.mvtools_exception(r)
    if not v:
        print(r)
        return False
    subcats = r
    calls = True
    for c in subcats:
        calls &= prefix_checker.prefix_checker(c, prefix_size)
    return calls

def puaq(selfhelp):
    print("Usage: %s prefix_size [target-dir]" % path_utils.basename_filtered(__file__))
    if selfhelp:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":

    td = os.getcwd()
    ps = ""

    if len(sys.argv) < 2:
        puaq(False)

    ps = sys.argv[1]

    if len(sys.argv) > 2:
        td = sys.argv[2]

    if prefix_checker_onelevel_caller(td, int(ps)):
        sys.exit(0)
    else:
        sys.exit(1)
