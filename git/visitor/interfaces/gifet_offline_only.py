#!/usr/bin/env python

import sys
import os

import git_visitor_fetch

def puaq(): # print usage and quit
    print("Usage: %s repo_path." % os.path.basename(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    options = {}
    repos = []

    repos += [sys.argv[1]]
    options["xor-remotename"] = "offline"

    if not git_visitor_fetch.visitor_fetch(repos, options):
        sys.exit(1)

