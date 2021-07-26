#!/usr/bin/env python3

import sys
import os

import path_utils
import generic_run

def hash_sha_512_app_content(content):
    # returns: tuple (Boolean, String or None)
    v, r = generic_run.run_cmd_simple(["sha512sum"], use_input=content)
    if not v:
        return False, r
    return True, r[0:128]

def hash_sha_512_app_file(filename):
    # returns: tuple (Boolean, String or None)
    v, r = generic_run.run_cmd_simple(["sha512sum", filename])
    if not v:
        return False, r
    return True, r[0:128]

def puaq():
    print("Usage: %s (--file|--contents) (file|contents)" % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 3:
        puaq()

    opt = sys.argv[1]
    target = sys.argv[2]

    if opt == "--file":
        v, r = hash_sha_512_app_file(target)
        if v:
            print(r)
        else:
            print("Failed generating hash")
    elif opt == "--contents":
        v, r = hash_sha_512_app_content(target)
        if v:
            print(r)
        else:
            print("Failed generating hash")
    else:
        print("Unsupported algorithm: %s" % algo)
        puaq()
