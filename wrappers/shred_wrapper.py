#!/usr/bin/env python3

import sys
import os
import shutil

import path_utils
import fsquery
import mvtools_exception
import generic_run

def shred_target(path):

    if not os.path.isdir(path):
        v, r = generic_run.run_cmd_simple(["shred", "-z", "-u", path])
        if not v:
            return False, "Failed running shred (file) command: [%s]" % r

        return True, None

    v, r = fsquery.makecontentlist(path, True, False, True, False, True, False, True, [])
    if not v:
        return False, r
    targets = r

    for i in targets:
        v, r = generic_run.run_cmd_simple(["shred", "-z", "-u", i])
        if not v:
            return False, "Failed running shred (dir) command: [%s]" % r

    shutil.rmtree(path)
    return True, None

def puaq(selfhelp):
    print("Usage: %s target_to_shred" % path_utils.basename_filtered(__file__))
    if selfhelp:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq(False)

    target_to_shred = sys.argv[1]

    v, r = shred_target(target_to_shred)
    if v:
        print("Shredded target [%s]" % target_to_shred)
    else:
        print("Failed shredding taget [%s]: [%s]" % (target_to_shred, r))
        sys.exit(1)
