#!/usr/bin/env python3

import sys
import os

import path_utils
import generic_run

def meld(left_path, right_path):

    v, r = generic_run.run_cmd(["meld", left_path, right_path])
    if not v:
        return False, r
    return True, None

def puaq():
    print("Usage: %s target_path pattern" % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 3:
        puaq()

    left_path = sys.argv[1]
    right_path = sys.argv[2]

    v, r = meld(left_path, right_path)
    if not v:
        print(r)
        sys.exit(1)
