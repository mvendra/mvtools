#!/usr/bin/env python3

import sys
import os

import generic_run

def shred_target(path):

    the_cmd = []
    if os.path.isdir(path):
        # path points to a folder. shred and delete folder using secure-delete
        # this is NOT supported on cygwin / windows
        the_cmd = ["srm", "-rfll", path + os.sep]
    else:
        # path points to a file. shred and delete folder using shred
        the_cmd = ["shred", "-z", "-u", path]

    v, r = generic_run.run_cmd_l_asc(the_cmd)
    return v, r

def puaq():
    print("Usage: %s target_to_shred" % os.path.basename(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    target_to_shred = sys.argv[1]

    v, r = shred_target(target_to_shred)
    if v:
        print("Shredded target [%s]" % target_to_shred)
    else:
        print("Failed shredding taget [%s]" % target_to_shred)
        sys.exit(1)
