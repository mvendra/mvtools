#!/usr/bin/env python

import sys
import os

import path_utils
import seven_z_wrapper

def extract_iso(source_file, target_folder):

    if not os.path.exists(source_file):
        return False, "Source file [%s] does not exist" % source_file

    if os.path.exists(target_folder):
        return False, "Output folder [%s] already exist" % target_folder

    os.mkdir(target_folder)

    v, r = seven_z_wrapper.extract(source_file, target_folder)
    return v, r

def puaq(selfhelp):
    print("Usage: %s source.iso target_folder" % path_utils.basename_filtered(__file__))
    if selfhelp:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 3:
        puaq(False)

    source_file = sys.argv[1]
    target_folder = sys.argv[2]

    v, r = extract_iso(source_file, target_folder)
    if not v:
        print(r)
        sys.exit(1)

    print("Extracted [%s] to [%s] successfully" % (source_file, target_folder))
