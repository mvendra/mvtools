#!/usr/bin/env python3

import sys
import os

import path_utils
import generic_run

def compress(file_to_compress):

    # file_to_compress: file to compress

    # prechecks
    if not os.path.exists(file_to_compress) and not path_utils.is_path_broken_symlink(file_to_compress):
        return False, "%s does not exist." % file_to_compress

    # actual command
    cmd = ["bzip2", file_to_compress]
    v, r = generic_run.run_cmd_simple(cmd)
    if not v:
        return False, "Failed running bzip2 compress command: [%s]" % r

    return True, r

def decompress(file_to_decompress):

    # file_to_decompress: file to decompress

    # prechecks
    if not os.path.exists(file_to_decompress):
        return False, "%s does not exist." % file_to_decompress

    # actual command
    cmd = ["bunzip2", file_to_decompress]
    v, r = generic_run.run_cmd_simple(cmd)
    if not v:
        return False, "Failed running bunzip2 decompress command: [%s]" % r

    return True, r

def puaq():
    print("Usage: %s file_to_compress" % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    file_to_compress = sys.argv[1]
    compress(file_to_compress)
