#!/usr/bin/env python3

import sys
import os

import path_utils
import git_lib
import svn_lib

REPO_TYPE_GIT_BARE="git/bare"
REPO_TYPE_GIT_STD="git/std"
REPO_TYPE_GIT_SUB="git/sub"
REPO_TYPE_SVN="svn"
REPO_TYPES = [REPO_TYPE_GIT_BARE, REPO_TYPE_GIT_STD, REPO_TYPE_GIT_SUB, REPO_TYPE_SVN]

def detect_repo_type(path):

    if not os.path.exists(path):
        return False, "Path %s doesn't exist." % path

    v, r = git_lib.is_repo_bare(path)
    if v and r:
        return True, REPO_TYPE_GIT_BARE

    v, r = git_lib.is_repo_standard(path)
    if v and r:
        return True, REPO_TYPE_GIT_STD

    v, r = git_lib.is_repo_submodule(path)
    if v and r:
        return True, REPO_TYPE_GIT_SUB

    v, r = svn_lib.is_svn_repo(path)
    if v and r:
        return True, REPO_TYPE_SVN

    return True, None

def is_any_repo_type(repo_type):
    return repo_type in REPO_TYPES

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
