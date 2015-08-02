#!/usr/bin/env python

import sys
import os
import fsquery
import path_utils

def puaq():
    print("Usage: %s base_path." % os.path.basename(__file__))
    sys.exit(1)

def __filter_git_only(thelist):
    ret = []
    for d in thelist:
        if d.endswith(".git") or d.endswith(".git" + os.sep):
            ret.append(d)
    return ret

def make_paths_list(argv):

    """ make_paths_list
    returns a list of paths, based on argv or envvars
    """

    paths = []
    if len(argv) > 1:
        # paths specified by cmdline arg. use it.
        paths = argv[1:]
    else:
        # no paths specified. try to get paths from envvars
        try:
            paths.append(os.environ["MVBASE"])
        except KeyError:
            print("No paths specified by argv, and MVBASE is undefined.")
            return None

    paths = path_utils.filter_path_list_no_same_branch(paths) # sanitises paths list
    return paths

def make_repo_list(path):

    """ make_repo_list
    returns a list of git repositories found in the given base path
    """

    if path is None:
        return None

    ret_list = fsquery.makecontentlist(path, True, False, True, False, True, [])
    ret_list = __filter_git_only(ret_list)
    if len(ret_list) > 0:
        return ret_list
    else:
        return None

def do_visit(argv, func):

    paths = make_paths_list(argv)
    if paths is None:
        print("No paths to visit.")
        return

    for p in paths:
        repos = make_repo_list(p)
        if repos is None:
            print("Warning: %s has no repositories." % p)
            continue
        func(repos)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    basepath = sys.argv[1]
    if not os.path.exists(basepath):
        print("%s does not exist. Aborting." % basepath)
        sys.exit(1)

    for r in make_repo_list(basepath):
        print("repo: %s" % r)

