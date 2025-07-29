#!/usr/bin/env python3

import sys
import os

import tar_wrapper
import bzip2_wrapper
import create_and_write_file
import sha512_wrapper
import path_utils

def add_str_to_report(target_string, additional_string):

    if len(additional_string) == 0:
        return target_string

    if len(target_string) == 0:
        return additional_string

    target_string += " / %s" % additional_string
    return target_string

def pakgen(filename, dohash, files):

    report = ""

    for f in files:
        if not os.path.exists( f ) and not path_utils.is_path_broken_symlink(f):
            return False, "%s does not exist." % f

    FILENAME_TAR = "%s.tar" % filename
    FILENAME_TAR_BZ2 = "%s.bz2" % FILENAME_TAR

    if os.path.exists(FILENAME_TAR):
        return False, "%s already exists." % FILENAME_TAR

    if os.path.exists(FILENAME_TAR_BZ2):
        return False, "%s already exists." % FILENAME_TAR_BZ2

    v, r = tar_wrapper.make_pack(FILENAME_TAR, files)
    if not v:
        return False, "Pakgen failed: %s" % r
    report = add_str_to_report(report, r)

    v, r = bzip2_wrapper.compress(FILENAME_TAR)
    if not v:
        return False, "Pakgen failed: %s" % r
    report = add_str_to_report(report, r)

    if dohash:
        HASH_FILENAME = "%s.sha512"  % FILENAME_TAR_BZ2
        if os.path.exists(HASH_FILENAME):
            return False, "%s already exists." % HASH_FILENAME
        v, r = sha512_wrapper.hash_sha_512_app_file(FILENAME_TAR_BZ2)
        if v:
            report = add_str_to_report(report, r)
            create_and_write_file.create_file_contents(HASH_FILENAME, r)
        else:
            return False, "Failed generating hash for %s" % FILENAME_TAR_BZ2

    return True, report

def puaq(selfhelp):
    print("Usage: %s [--file pack_filename] [--hash] (files_and_folders)" % path_utils.basename_filtered(__file__))
    if selfhelp:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq(False)

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
        puaq(False)
    elif len(files) == 1 and filename is None:
        filename = path_utils.basename_filtered(files[0])
    elif filename is None:
        filename = "newpack"

    v, r = pakgen(filename, dohash, files)
    print(r)
    if not v:
        sys.exit(1)
