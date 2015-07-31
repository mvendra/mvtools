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
        if os.path.basename(d) == ".git":
            ret.append(d)
    return ret

def make_repo_list(path):
    ret = fsquery.makecontentlist(path, True, False, True, False, True, [])
    ret = __filter_git_only(ret)
    return ret

def get_remotes(repo):
    out = check_output(["git", "--git-dir=%s" % repo, "--work-tree=%s" % os.path.dirname(repo), "remote"])
    ret_list = out.split()
    return ret_list

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    basepath = sys.argv[1]
    if not os.path.exists(basepath):
        print("%s does not exist. Aborting." % basepath)
        sys.exit(1)

    for r in make_repo_list(basepath):
        print(r)

