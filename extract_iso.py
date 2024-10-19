#!/usr/bin/env python3

import sys
import os

import path_utils
import generic_run

def extract_iso(source_file, target_folder):

    if not os.path.exists(source_file):
        return False, "Source file [%s] does not exist" % source_file

    if os.path.exists(target_folder):
        return False, "Output folder [%s] already exist" % target_folder

    os.mkdir(target_folder)

    cmd = ["7z", "x", source_file, "-o%s" % target_folder]
    v, r = generic_run.run_cmd_simple(cmd)
    return v, r

def puaq():
    print("Usage: %s source.iso target_folder" % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 3:
        puaq()

    source_file = sys.argv[1]
    target_folder = sys.argv[2]

    v, r = extract_iso(source_file, target_folder)
    if not v:
        print(r)
        sys.exit(1)

    print("Extracted [%s] to [%s] successfully" % (source_file, target_folder))
