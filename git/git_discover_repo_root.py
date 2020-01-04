#!/usr/bin/env python3

import os
import sys
import path_utils

def is_repo_root(path):
    if path is None:
        return False
    if not os.path.exists(path):
        return False
    if path.endswith(".git") or path.endswith(".git" + os.sep):
        return True

def git_discover_repo_root(repo_path):
    curpath = repo_path
    while not is_repo_root(os.path.join(curpath, ".git")):
        curpath = path_utils.backpedal_path(curpath)
        if curpath is None:
            return None
    return curpath

if __name__ == "__main__":

    startpath = os.getcwd() # uses current working dir by default
    if len(sys.argv) > 1:
        # override with cmdline arg
        startpath = sys.argv[1]

    r = git_discover_repo_root(startpath)
    if r is None:
        print("Failed getting root directory for [%s]." % startpath)
        sys.exit(1)
    print(r)
