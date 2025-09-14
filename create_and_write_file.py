#!/usr/bin/env python

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

def puaq(selfhelp):
    print("Usage: %s file contents" % path_utils.basename_filtered(__file__))
    if selfhelp:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 3:
        puaq(False)

    filename = sys.argv[1]
    contents = sys.argv[2]

    try:
        create_file_contents(filename, contents)
    except mvtools_exception.mvtools_exception as ex:
        print(ex)
        sys.exit(1)
