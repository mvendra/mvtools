#!/usr/bin/env python3

import sys
import os

import path_utils
import generic_run

def umount(target_path):

    if target_path is None:
        return False, "target_path is mandatory"

    full_cmd = ["umount", target_path]

    v, r = generic_run.run_cmd_simple(full_cmd)
    if not v:
        return False, "Failed running umount command: [%s]" % r

    return True, None

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

    v, r = umount(target_path)
    if not v:
        print(r)
        sys.exit(1)
