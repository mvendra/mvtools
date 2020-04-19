#!/usr/bin/env python3

import sys
import os

import generic_run

def decompress(file_to_decompress):

    # file_to_decompress: file to decompress

    # prechecks
    if not os.path.exists(file_to_decompress):
        return False, "%s does not exist." % file_to_decompress

    # actual command
    cmd = ["bunzip2", file_to_decompress]
    v, r = generic_run.run_cmd_simple(cmd)
    return v, None

def puaq():
    print("Usage: %s file_to_decompress.bz2" % os.path.basename(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    file_to_decompress = sys.argv[1]
    decompress(file_to_decompress)
