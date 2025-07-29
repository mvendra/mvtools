#!/usr/bin/env python3

import sys
import os

import path_utils
import generic_run

def make_pack(file_to_create, incl_list):

    # file_to_create: tar file to create
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
        if not os.path.exists( incl_list[fi] ) and not path_utils.is_path_broken_symlink(incl_list[fi]):
            return False, "%s does not exist." % incl_list(fi)

    # main option
    tar_cmd = ["tar", "-cf", file_to_create] + incl_list
    v, r = generic_run.run_cmd_simple(tar_cmd)
    if not v:
        return False, "Failed running tar make_pack command: [%s]" % r

    return True, r

def extract(file_to_extract, target_path):

    # file_to_extract: tar file to extract from
    # target_path: target folder to extract to

    file_to_extract = path_utils.filter_remove_trailing_sep(file_to_extract)

    # prechecks
    if not os.path.exists(file_to_extract):
        return False, "%s does not exist." % file_to_extract
    if not os.path.exists(target_path):
        return False, "%s does not exist." % target_path

    # actual command
    tar_cmd = ["tar", "-xf", file_to_extract, "-C", target_path]
    v, r = generic_run.run_cmd_simple(tar_cmd)
    if not v:
        return False, "Failed running tar extract command: [%s]" % r

    return True, r

def puaq(selfhelp):
    print("Usage: %s file_to_create.tar (inclusion_list)" % path_utils.basename_filtered(__file__))
    if selfhelp:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 3:
        puaq(False)

    file_to_create = sys.argv[1]
    incl_list = sys.argv[2:]

    make_pack(file_to_create, incl_list)
