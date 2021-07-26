#!/usr/bin/env python3

import sys
import os

import path_utils

import git_lib
import git_visitor_push

def puaq(): # print usage and quit
    print("Usage: %s repo_path" % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    options = {}
    repos = []

    repos += [sys.argv[1]]

    v, r = git_lib.get_current_branch(repos[0])
    if not v:
        print("Failed [%s]: [%s]." % (repos[0], r))
        sys.exit(1)
    elif v and r == None:
        print("No branches detected in %s. Aborting." % repo_path)
        sys.exit(1)
    current_branch = r
    options["xor-branch"] = current_branch

    if not git_visitor_push.visitor_push(repos, options):
        sys.exit(1)
