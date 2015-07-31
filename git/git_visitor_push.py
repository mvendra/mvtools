#!/usr/bin/env python

import sys
import os
import git_visitor_base
from subprocess import check_output

def puaq():
    print("Usage: %s base_path." % os.path.basename(__file__))
    sys.exit(1)

def run_visitor_push(list_repos):
    for r in list_repos:
        out = check_output(["git", "--git-dir=%s" % r, "--work-tree=%s" % os.path.dirname(r), "push"])

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    basepath = sys.argv[1]
    if not os.path.exists(basepath):
        print("%s does not exist. Aborting." % basepath)
        sys.exit(1)

    repos = git_visitor_base.make_repo_list(basepath)
    run_visitor_push(repos)

