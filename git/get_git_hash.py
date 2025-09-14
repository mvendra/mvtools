#!/usr/bin/env python

import sys
import os

import path_utils
import git_lib

def get_git_hash(target_repo):
    return git_lib.get_head_hash(target_repo)

if __name__ == "__main__":

    target_repo = os.getcwd()
    v, r = get_git_hash(target_repo)
    print(r)
    if not v:
        sys.exit(1)
