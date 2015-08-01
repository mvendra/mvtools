#!/usr/bin/env python

import sys
import os
import fsquery

def puaq():
    print("Usage: %s base_path." % os.path.basename(__file__))
    sys.exit(1)

def __filter_git_only(thelist):
    ret = []
    for d in thelist:
        if d.endswith(".git") or d.endswith(".git" + os.sep):
            ret.append(d)
    return ret

def make_repo_list(path):

    """ make_repo_list
    returns a list of git repositories found in the given base path
    """

    ret_list = fsquery.makecontentlist(path, True, False, True, False, True, [])
    ret_list = __filter_git_only(ret_list)
    if len(ret_list) > 0:
        return ret_list
    else:
        return None

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    basepath = sys.argv[1]
    if not os.path.exists(basepath):
        print("%s does not exist. Aborting." % basepath)
        sys.exit(1)

    for r in make_repo_list(basepath):
        print("repo: %s" % r)

