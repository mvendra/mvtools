#!/usr/bin/env python3

import sys
import os

import path_utils
import git_wrapper

def detect_repo_type(path):

    if not os.path.exists(path):
        return False, "Path %s doesn't exist." % path

    v, r = git_wrapper.rev_parse_is_bare_repo(path)
    if v:
        if "true" in r:
            return True, "git/bare"

    v, r = git_wrapper.rev_parse_is_inside_work_tree(path)
    if v:
        if "true" in r:
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
