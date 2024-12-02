#!/usr/bin/env python3

import sys
import os

import path_utils
import generic_run

def make_pack(file_to_create, incl_list):

    file_to_create = path_utils.filter_remove_trailing_sep(file_to_create)

    if incl_list is None:
        return False, "No files to add"
    if len(incl_list) == 0:
        return False, "No files to add"
    if os.path.exists(file_to_create):
        return False, "[%s] already exists." % file_to_create

    for fi in range(len(incl_list)):
        incl_list[fi] = path_utils.filter_remove_trailing_sep(incl_list[fi])
        if not os.path.exists( incl_list[fi] ) and not path_utils.is_path_broken_symlink(incl_list[fi]):
            return False, "[%s] does not exist." % incl_list[fi]

    full_cmd = ["7z", "a", file_to_create] + incl_list
    v, r = generic_run.run_cmd_simple(full_cmd)
    return v, r

def extract(file_to_extract, target_path):

    file_to_extract = path_utils.filter_remove_trailing_sep(file_to_extract)
    file_to_extract = os.path.abspath(file_to_extract)
    target_path = path_utils.filter_remove_trailing_sep(target_path)
    target_path = os.path.abspath(target_path)

    if not os.path.exists(file_to_extract):
        return False, "[%s] does not exist." % file_to_extract
    if not os.path.exists(target_path):
        return False, "[%s] does not exist." % target_path

    full_cmd = ["7z", "x", file_to_extract]
    v, r = generic_run.run_cmd_simple(full_cmd, use_cwd=target_path)
    return v, r

def puaq():
    print("Usage: %s file_to_create.7z (inclusion_list)" % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 3:
        puaq()

    file_to_create = sys.argv[1]
    incl_list = sys.argv[2:]

    v, r = make_pack(file_to_create, incl_list)
    if not v:
        print(r)
        sys.exit(1)
