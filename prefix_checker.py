#!/usr/bin/env python

import os
import sys

import path_utils
import fsquery
import mvtools_exception

def prefix_checker(target_dir, prefix_size):

    v, r = fsquery.makecontentlist(target_dir, False, False, True, True, False, False, True, None)
    if not v:
        raise mvtools_exception.mvtools_exception(r)
    dirs = r
    dirs.sort()
    c=0
    r=0
    for d in dirs:
        c += 1
        base = path_utils.dirname_filtered(d)
        subject = path_utils.basename_filtered(d)
        pref = subject[0:prefix_size]
        if int(pref) != c:
            print("%s does not pass the prefix checker at %s" % (target_dir, d))
            r += 1

    if (r > 0):
        print("%s - erros detected" % target_dir)
        return False
    else:
        print("%s - all good" % target_dir)
        return True

def puaq(selfhelp):
    print("Usage: %s prefix_size [target-dir]" % path_utils.basename_filtered(__file__))
    if selfhelp:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":

    """
    given a path:
    [/some/path/] -> optional, if not provided, will use cwd

    this tool:
    prefix_checker 3 [/some/path]

    will check if everything inside /some/path is prefixed numerically: 001~xxx
    for example:
    /some/path/001_whatever
    /some/path/002_whatever
    /some/path/003_whatever

    is valid, whereas:
    /some/path/001_whatever
    /some/path/003_whatever
    /some/path/004_whatever

    is not
    """

    td = os.getcwd()
    ps = ""

    if len(sys.argv) < 2:
        puaq(False)

    ps = sys.argv[1]

    if len(sys.argv) > 2:
        td = sys.argv[2]

    if prefix_checker(td, int(ps)):
        sys.exit(0)
    else:
        sys.exit(1)
