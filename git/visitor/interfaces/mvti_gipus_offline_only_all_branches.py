#!/usr/bin/env python3

import sys
import os

import path_utils
import git_visitor_push

def puaq(): # print usage and quit
    print("Usage: %s repo_path." % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    options = {}
    repos = []

    repos += [sys.argv[1]]
    options["xor-remotename"] = "offline"

    if not git_visitor_push.visitor_push(repos, options):
        sys.exit(1)

