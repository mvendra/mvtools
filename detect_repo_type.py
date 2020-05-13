#!/usr/bin/env python3

import sys
import os

import path_utils
import git_lib

def detect_repo_type(path):

    if not os.path.exists(path):
        return False, "Path %s doesn't exist." % path

    v, r = git_lib.is_repo_bare(path)
    if v and r:
        return True, "git/bare"

    v, r = git_lib.is_repo_working_tree(path)
    if v and r:
        the_git_obj = path_utils.concat_path(path, ".git")
        if os.path.exists( the_git_obj ):
            if os.path.isdir(the_git_obj):
                return True, "git/std"
            else:
                return True, "git/sub"

    # should ideally use "svnlook info the_path" but that wouldn't work with some repositories
    the_svn_obj = path_utils.concat_path(path, ".svn")
    if os.path.exists(the_svn_obj) and os.path.isdir(the_svn_obj):
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
