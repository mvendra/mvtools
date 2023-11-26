#!/usr/bin/env python3

import sys
import os

import path_utils

def git_smash(repo, num_commits):

    if repo is None:
        return False, "git_smash: repo is None"

    if not isinstance(num_commits, int):
        return False, "git_smash: number of commits is not numeric (%s)" % num_commits

    if num_commits == 1:
        return False, "git_smash: number of commits is too small"

    return False, "mvtodo"

def puaq():
    print("Usage: %s [repository] number_of_commits" % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":

    repo = None
    num_commits = None
    if len(sys.argv) < 2:
        puaq()
    elif len(sys.argv) == 2:
        num_commits = sys.argv[1]
        repo = os.getcwd()
    else:
        repo = sys.argv[1]
        num_commits = sys.argv[2]

    v, r = git_smash(repo, int(num_commits))
    print(r)
    exit(not v)
