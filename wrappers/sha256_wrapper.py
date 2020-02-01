#!/usr/bin/env python3

import sys
import os

import generic_run

def hash_sha_256_app_content(content):
    # returns: tuple (Boolean, String or None)
    v, r = generic_run.run_cmd("sha256sum", content)
    if not v:
        return False, None
    return True, r[0:64]

def hash_sha_256_app_file(filename):
    # returns: tuple (Boolean, String or None)
    v, r = generic_run.run_cmd_l(["sha256sum", filename])
    if not v:
        return False, None
    return True, r[0:64]

def puaq():
    print("Usage: %s (--file|--contents) (file|contents)" % os.path.basename(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 3:
        puaq()

    opt = sys.argv[1]
    target = sys.argv[2]

    if opt == "--file":
        v, r = hash_sha_256_app_file(target)
        if v:
            print(r)
        else:
            print("Failed generating hash")
    elif opt == "--contents":
        v, r = hash_sha_256_app_content(target)
        if v:
            print(r)
        else:
            print("Failed generating hash")
    else:
        print("Unsupported algorithm: %s" % algo)
        puaq()
