#!/usr/bin/env python3

import sys
import os

import path_utils
import generic_run

def mount(target_path):

    full_cmd = ["mount"]
    if target_path is not None:
        full_cmd.append(target_path)

    v, r = generic_run.run_cmd_simple(full_cmd)
    if not v:
        return False, "Failed running mount command: [%s]" % r

    return True, r

def puaq(selfhelp):
    print("Usage: %s target_path" % path_utils.basename_filtered(__file__))
    if selfhelp:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq(False)

    target_path = sys.argv[1]

    v, r = mount(target_path)
    if not v:
        print(r)
        sys.exit(1)
