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

    paths = git_visitor_base.make_paths_list(sys.argv)
    if paths is None:
        print("No paths to visit. Aborting.")
        sys.exit(1)

    for p in paths:
        repos = git_visitor_base.make_repo_list(p)
        if repos is None:
            print("Warning: %s has no repositories." % p)
            continue
        run_visitor_status(repos)

