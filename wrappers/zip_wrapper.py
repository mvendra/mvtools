#!/usr/bin/env python3

import sys
import os

import generic_run
import path_utils

def make_pack(file_to_create, incl_list):

    # file_to_create: zip file to create
    # incl_list: list of files or folders to include

    file_to_create = path_utils.filter_remove_trailing_sep(file_to_create)

    # prechecks
    if incl_list is None:
        return False, "No files to add"
    if len(incl_list) == 0:
        return False, "No files to add"
    if os.path.exists(file_to_create):
        return False, "%s already exists." % file_to_create

    for fi in range(len(incl_list)):
        incl_list[fi] = path_utils.filter_remove_trailing_sep(incl_list[fi])
        if not os.path.exists( incl_list[fi] ):
            return False, "%s does not exist." % incl_list(fi)

    # main option
    zip_cmd = ["zip", file_to_create, "-r"] + incl_list
    v, r = generic_run.run_cmd_simple(zip_cmd)
    return v, r

def extract(file_to_extract, target_path):

    # file_to_extract: zip file to extract from
    # target_path: target folder to extract to

    file_to_extract = path_utils.filter_remove_trailing_sep(file_to_extract)

    # prechecks
    if not os.path.exists(file_to_extract):
        return False, "%s does not exist." % file_to_extract
    if not os.path.exists(target_path):
        return False, "%s does not exist." % target_path

    # actual command
    zip_cmd = ["unzip", file_to_extract, "-d", target_path]
    v, r = generic_run.run_cmd_simple(zip_cmd)
    return v, r

def puaq():
    print("Usage: %s file_to_create.zip (inclusion_list)" % os.path.basename(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 3:
        puaq()

    file_to_create = sys.argv[1]
    incl_list = sys.argv[2:]

    make_pack(file_to_create, incl_list)