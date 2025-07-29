#!/usr/bin/env python3

import sys
import os

import path_utils
import git_visitor_fetch

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
    options["xor-remotename"] = "offline"

    if not git_visitor_fetch.visitor_fetch(repos, options):
        sys.exit(1)

