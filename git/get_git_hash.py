#!/usr/bin/env python

import sys
import os

import path_utils
import git_lib

def get_git_hash(target_repo, num_prev_hash):

    if num_prev_hash is None:

        return git_lib.get_head_hash(target_repo)

    else:

        if num_prev_hash == "0":
            return git_lib.get_head_hash(target_repo)

        v, r = git_lib.get_previous_hash_list(target_repo, int(num_prev_hash) + 1)
        if not v:
            return False, r
        return True, r[len(r) - 1]

if __name__ == "__main__":

    num_prev_hash = None
    if len(sys.argv) > 1:
        num_prev_hash = sys.argv[1]

    target_repo = os.getcwd()
    v, r = get_git_hash(target_repo, num_prev_hash)
    print(r)
    if not v:
        sys.exit(1)
