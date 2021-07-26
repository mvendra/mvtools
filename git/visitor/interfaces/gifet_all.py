#!/usr/bin/env python3

import sys
import os

import path_utils
import git_wrapper

def puaq(): # print usage and quit
    print("Usage: %s repo_path." % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    repo_path = sys.argv[1]
    print("Fetching %s..." % repo_path)

    v, r = git_wrapper.fetch_all(repo_path)
    if v:
        out = "Done with success."
    else:
        out = "Failed: %s" % r

    print("\n%s" % out)
