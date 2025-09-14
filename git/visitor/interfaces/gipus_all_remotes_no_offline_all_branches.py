#!/usr/bin/env python

import sys
import os

import path_utils
import git_visitor_push

def puaq(selfhelp): # print usage and quit
    print("Usage: %s repo_path." % path_utils.basename_filtered(__file__))
    if selfhelp:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq(False)

    options = {}
    repos = []

    repos += [sys.argv[1]]
    options["not-remotename"] = ["offline"]

    if not git_visitor_push.visitor_push(repos, options):
        sys.exit(1)

