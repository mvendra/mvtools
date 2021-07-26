#!/usr/bin/env python3

import sys
import os

import generic_run
import path_utils

def compress(target_archive):

    target_archive = path_utils.filter_remove_trailing_sep(target_archive)

    # prechecks
    if not os.path.exists(target_archive):
        return False, "%s does not exist." % target_archive

    # actual command
    gzip_cmd = ["gzip", target_archive]
    v, r = generic_run.run_cmd_simple(gzip_cmd)
    return v, r

def decompress(target_archive):

    target_archive = path_utils.filter_remove_trailing_sep(target_archive)
    target_archive_decomp = path_utils.poplastextension(target_archive)

    # prechecks
    if not os.path.exists(target_archive):
        return False, "%s does not exist." % target_archive
    if os.path.exists(target_archive_decomp):
        return False, "%s already exists." % target_archive_decomp

    # actual command
    gunzip_cmd = ["gunzip", target_archive]
    v, r = generic_run.run_cmd_simple(gunzip_cmd)
    return v, r

def puaq():
    print("Usage: %s target_archive.tar" % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    target_archive = sys.argv[1]

    v, r = compress(target_archive)
    if not v:
        print(r)
        sys.exit(1)
