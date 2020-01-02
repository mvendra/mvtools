#!/usr/bin/env python3

import os
import sys
import path_utils

import inline_echo

def is_repo_root(path):
    if path is None:
        return False
    if not os.path.exists(path):
        return False
    if path.endswith(".git") or path.endswith(".git" + os.sep):
        return True

if __name__ == "__main__":

    curpath = os.getcwd() # uses current working dir by default
    if len(sys.argv) > 1:
        # override with cmdline arg
        curpath = sys.argv[1]

    while not is_repo_root(os.path.join(curpath, ".git")):
        curpath = path_utils.backpedal_path(curpath)
        if curpath is None:
            sys.exit(1)

    inline_echo.inline_echo(curpath)
