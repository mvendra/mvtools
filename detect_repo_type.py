#!/usr/bin/env python3

import sys
import os

import path_utils
import git_lib
import svn_lib

def detect_repo_type(path):

    if not os.path.exists(path):
        return False, "Path %s doesn't exist." % path

    v, r = git_lib.is_repo_bare(path)
    if v and r:
        return True, "git/bare"

    v, r = git_lib.is_repo_standard(path)
    if v and r:
        return True, "git/std"

    v, r = git_lib.is_repo_submodule(path)
    if v and r:
        return True, "git/sub"

    v, r = svn_lib.is_svn_repo(path)
    if v and r:
        return True, "svn"

    return False, "Nothing detected"

def puaq():
    print("Usage: %s path" % os.path.basename(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    path = sys.argv[1]
    v, r = detect_repo_type(path)
    print(r)

    if not v:
        sys.exit(1)
