#!/usr/bin/env python3

import sys
import os
import shutil

import fsquery
import path_utils
import generic_run

def shred_target(path):

    if os.path.isdir(path):
        v, r = fsquery.makecontentlist(path, True, False, True, False, True, False, True, [])
        ret = r
        for i in ret:
            v, r = generic_run.run_cmd_simple(["shred", "-z", "-u", i])
            if not v:
                return False, r
        shutil.rmtree(path)
        return True, None
    else:
        return generic_run.run_cmd_simple(["shred", "-z", "-u", path])

def puaq():
    print("Usage: %s target_to_shred" % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    target_to_shred = sys.argv[1]

    v, r = shred_target(target_to_shred)
    if v:
        print("Shredded target [%s]" % target_to_shred)
    else:
        print("Failed shredding taget [%s]: [%s]" % (target_to_shred, r))
        sys.exit(1)
