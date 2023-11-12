#!/usr/bin/env python3

import sys
import os

import path_utils
import sha512_wrapper

def puaq():
    print("Usage: %s archive-to-check [hash-file]" % path_utils.basename_filtered(__file__))
    sys.exit(1)

def sha512sum_check(archive_file, hash_file):

    hash_file_contents = ""
    with open(hash_file, "r") as f:
        hash_file_contents = f.read()

    v, r = sha512_wrapper.hash_sha_512_app_file(archive_file)
    if not v:
        print("Failed generating hash for file %s" % archive_file)
        sys.exit(1)

    # and then compare
    if hash_file_contents[0:128] == r:
        return True
    else:
        return False

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    archive_file = sys.argv[1]
    hash_file = ""

    if len(sys.argv) > 2:
        hash_file = sys.argv[2]
    else:
        hash_file = archive_file + ".sha512"

    if not os.path.isfile(archive_file):
        print("%s does not exist. Aborting." % archive_file)
        sys.exit(1)

    if not os.path.isfile(hash_file):
        print("%s does not exist. Aborting." % hash_file)
        sys.exit(1)

    if sha512sum_check(archive_file, hash_file):
        print("Correct match")
    else:
        print("Check failed!")
        sys.exit(1)
