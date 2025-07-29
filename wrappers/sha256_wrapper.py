#!/usr/bin/env python3

import sys
import os

import path_utils
import generic_run

def hash_sha_256_app_content(content):

    v, r = generic_run.run_cmd_simple(["sha256sum"], use_input=content)
    if not v:
        return False, "Failed running sha256 (contents) command: [%s]" % r

    return True, r[0:64]

def hash_sha_256_app_file(filename):

    v, r = generic_run.run_cmd_simple(["sha256sum", filename])
    if not v:
        return False, "Failed running sha256 (file) command: [%s]" % r

    return True, r[0:64]

def puaq(selfhelp):
    print("Usage: %s (--file|--contents) (file|contents)" % path_utils.basename_filtered(__file__))
    if selfhelp:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 3:
        puaq(False)

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
        puaq(False)
