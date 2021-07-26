#!/usr/bin/env python3

import sys
import os

import path_utils

def create_file_contents(filename, contents):

    if os.path.exists(filename):
        print("[%s] already exists. Will not proceed." % filename)
        return False

    with open(filename, "w+") as f:
        f.write(contents)
    return True

def puaq():
    print("Usage: %s file contents" % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 3:
        puaq()

    filename = sys.argv[1]
    contents = sys.argv[2]

    r = create_file_contents(filename, contents)
    if not r:
        print("Failed creating new file.")
        sys.exit(1)
