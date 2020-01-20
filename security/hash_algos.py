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

def hash_sha_512_app_content(content):
    # returns: tuple (Boolean, String or None)
    v, r = generic_run.run_cmd("sha512sum", content)
    if not v:
        return False, None
    return True, r[0:128]

def hash_sha_256_app_file(filename):
    # returns: tuple (Boolean, String or None)
    v, r = generic_run.run_cmd("sha256sum %s" % filename)
    if not v:
        return False, None
    return True, r[0:64]

def hash_sha_512_app_file(filename):
    # returns: tuple (Boolean, String or None)
    v, r = generic_run.run_cmd("sha512sum %s" % filename)
    if not v:
        return False, None
    return True, r[0:128]

def puaq():
    print("Usage: %s (sha256|sha512) contents" % os.path.basename(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 3:
        puaq()

    algo = sys.argv[1]
    content = sys.argv[2]

    if algo == "sha256":
        v, r = hash_sha_256_app_content(content)
        if v:
            print(r)
        else:
            print("Failed generating hash")
    elif algo == "sha512":
        v, r = hash_sha_512_app_content(content)
        if v:
            print(r)
        else:
            print("Failed generating hash")
    else:
        print("Unsupported algorithm: %s" % algo)
        puaq()
