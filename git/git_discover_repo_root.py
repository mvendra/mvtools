#!/usr/bin/env python

import os
import path_utils

def is_repo_root(path):
    if not os.path.exists(path):
        return False
    if path.endswith(".git") or path.endswith(".git" + os.sep):
        return True

if __name__ == "__main__":

    curpath = os.getcwd()
    while not is_repo_root(os.path.join(curpath, ".git")):
        curpath = path_utils.backpedal_path(curpath)
        if curpath is None:
            break
    print(os.path.join(curpath, ".git"))

