#!/usr/bin/env python

import sys
import os

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
    options["not-remote"] = ["offline"]

    git_visitor_push.visitor_push(repos, options)

