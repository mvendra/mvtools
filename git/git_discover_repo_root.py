#!/usr/bin/env python3

import os
import sys
import path_utils

import git_lib

if __name__ == "__main__":

    startpath = os.getcwd() # uses current working dir by default
    if len(sys.argv) > 1:
        # override with cmdline arg
        startpath = sys.argv[1]

    r = git_lib.discover_repo_root(startpath)
    if r is None:
        print("Failed getting root directory for [%s]." % startpath)
        sys.exit(1)
    print(r)
