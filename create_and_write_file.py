#!/usr/bin/env python3

import sys
import os
import binascii

import mvtools_exception
import path_utils

def create_file_contents(filename, contents):

    if os.path.exists(filename):
        raise mvtools_exception.mvtools_exception("[%s] already exists. Will not proceed." % filename)

    with open(filename, "w+") as f:
        f.write(contents)

def create_file_contents_hex(filename, contents):

    if os.path.exists(filename):
        raise mvtools_exception.mvtools_exception("[%s] already exists. Will not proceed." % filename)

    with open(filename, "wb+") as f:
        f.write(binascii.unhexlify(contents))

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
