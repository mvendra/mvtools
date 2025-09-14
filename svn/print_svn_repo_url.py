#!/usr/bin/env python

import sys
import os

import svn_lib

def find_and_print_svn_repo_remote_link(local_repo):

    v, r = svn_lib.get_remote_link(local_repo)
    if not v:
        print("Failed: [%s]" % r)
    print(r)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        local_repo = os.getcwd()
    else:
        local_repo = sys.argv[1]

    find_and_print_svn_repo_remote_link(local_repo)
