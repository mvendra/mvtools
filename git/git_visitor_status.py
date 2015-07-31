#!/usr/bin/env python

import sys
import os
import git_visitor_base
from subprocess import check_output

def run_visitor_status(list_repos):
    for r in list_repos:
        out = check_output(["git", "--git-dir=%s" % r, "--work-tree=%s" % os.path.dirname(r), "status", "-s"])
        if len(out) == 0:
            pass # clean HEAD
        else:
            print("%s is dirty." % os.path.dirname(r))

if __name__ == "__main__":

    base_paths = []
    # try to use envvar
    try:
        base_paths.append(os.environ["MVBASE"])
    except KeyError:
        pass # let it be

    base_paths += sys.argv[1:]
    print(base_paths)

    # mvtodo: dont repeat same parents (remove duplicates when they have the same parents inside base_paths

    if len(base_paths) == 0:
        print("No paths determined, either by envvar or by cmdline argument. Aborting.")
        sys.exit(1)

    basepath = sys.argv[1]
    if not os.path.exists(basepath):
        print("%s does not exist. Aborting." % basepath)
        sys.exit(1)

    repos = git_visitor_base.make_repo_list(basepath)
    run_visitor_status(repos)

