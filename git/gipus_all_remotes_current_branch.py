#!/usr/bin/env python

import sys
import os
import git_repo_query

import git_visitor_push

def puaq(): # print usage and quit
    print("Usage: %s repo_path." % os.path.basename(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    options = {}
    repos = []

    repos += [sys.argv[1]]

    current_branch = git_repo_query.get_current_branch(repos[0])
    if current_branch is None:
        print("No branches detected in %s. Aborting." % repo_path)
        sys.exit(1)
    options["xor-branch"] = current_branch

    git_visitor_push.visitor_push(repos, options)

