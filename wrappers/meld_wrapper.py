#!/usr/bin/env python3

import sys
import os

import path_utils
import generic_run

def meld(left_path, right_path):

    v, r = generic_run.run_cmd_simple(["meld", left_path, right_path])
    if not v:
        return False, "Failed running meld command: [%s]" % r

    return True, None

def puaq(selfhelp):
    print("Usage: %s target_path pattern" % path_utils.basename_filtered(__file__))
    if selfhelp:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 3:
        puaq(False)

    left_path = sys.argv[1]
    right_path = sys.argv[2]

    v, r = meld(left_path, right_path)
    if not v:
        print(r)
        sys.exit(1)
