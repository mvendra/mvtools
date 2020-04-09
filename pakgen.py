#!/usr/bin/env python3

import sys
import os

import tar_wrapper
import bzip2_wrapper
import create_and_write_file
import sha256_wrapper
import path_utils

def pakgen(filename, dohash, files):

    for f in files:
        if not os.path.exists( f ):
            print("%s does not exist." % f)
            return False

    FILENAME_TAR = "%s.tar" % filename
    FILENAME_TAR_BZ2 = "%s.bz2" % FILENAME_TAR

    if os.path.exists(FILENAME_TAR):
        print("%s already exists." % FILENAME_TAR)
        return False

    if os.path.exists(FILENAME_TAR_BZ2):
        print("%s already exists." % FILENAME_TAR_BZ2)
        return False

    v, r = tar_wrapper.make_pack(FILENAME_TAR, files)
    if not v:
        print(r)
        return False

    v, r = bzip2_wrapper.compress(FILENAME_TAR)
    if not v:
        print(r)
        return False

    if dohash:
        HASH_FILENAME = "%s.sha256"  % FILENAME_TAR_BZ2
        if os.path.exists(HASH_FILENAME):
            print("%s already exists." % HASH_FILENAME)
            return False
        v, r = sha256_wrapper.hash_sha_256_app_file(FILENAME_TAR_BZ2)
        if v:
            create_and_write_file.create_file_contents(HASH_FILENAME, r)
        else:
            print("Failed generating hash for %s" % FILENAME_TAR_BZ2)
            return False

    return True

def puaq():
    print("Usage: %s [--file pack_filename] [--hash] (files_and_folders)" % os.path.basename(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    params = sys.argv[1:]
    files = []
    filename = None
    dohash = False

    capture_next = False
    for i in params:
        if capture_next:
            capture_next = False
            filename = i
        elif i == "--hash":
            dohash = True
        elif i == "--file":
            capture_next = True
        else:
            files.append(i)

    if len(files) < 1:
        puaq
    elif len(files) == 1 and filename is None:
        filename = os.path.basename( path_utils.filter_remove_trailing_sep(files[0]) )
    elif filename is None:
        filename = "newpack"

    if not pakgen(filename, dohash, files):
        print("Generating pak failed.")
        sys.exit(1)
