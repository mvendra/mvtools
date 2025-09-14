#!/usr/bin/env python

import sys
import os

import path_utils
import git_lib

def puaq(selfhelp): # print usage and quit
    print("Usage: %s repo_path." % path_utils.basename_filtered(__file__))
    if selfhelp:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq(False)

    repo_path = sys.argv[1]
    print("Fetching %s..." % repo_path)

    v, r = git_lib.fetch_all(repo_path)
    if v:
        out = "Done with success."
    else:
        out = "Failed: %s" % r

    print("\n%s" % out)
