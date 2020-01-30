#!/usr/bin/env python3

import sys
import os

import generic_run

def make_pack(file_to_create, incl_list, excl_list=None):

    # file_to_create: tar file to create
    # incl_list: list of files or folders to include
    # excl_list: list of files or folders to exclude

    # prechecks
    if incl_list is None:
        return False, "No files to add"
    if len(incl_list) == 0:
        return False, "No files to add"
    if os.path.exists(file_to_create):
        return False, "%s already exists." % file_to_create
    for f in incl_list:
        if not os.path.exists(f):
            return False, "%s does not exist." % f
    if excl_list is not None:
        for f in excl_list:
            if not os.path.exists(f):
                return False, "%s does not exist." % f

    # actual command
    tar_cmd = "tar"

    # exclude files
    # disabled for now. too much trouble.
    """
    if excl_list is not None:
        for s in excl_list:
            tar_cmd += " --exclude=\"%s\"" % s
    tar_cmd = tar_cmd.strip()
    """

    # main option
    tar_cmd += " -cf %s" % file_to_create
    tar_cmd = tar_cmd.strip()

    # include files
    for s in incl_list:
        tar_cmd += " %s " % s
    tar_cmd = tar_cmd.strip()

    v, r = generic_run.run_cmd(tar_cmd)
    return v, None

def extract(file_to_extract, target_folder):

    # file_to_extract: tar file to extract from
    # target_folder: target folder to extract to

    # prechecks
    if not os.path.exists(file_to_extract):
        return False, "%s does not exist." % file_to_extract
    if not os.path.exists(target_folder):
        return False, "%s does not exist." % target_folder

    # actual command
    tar_cmd = "tar -xf %s -C %s" % (file_to_extract, target_folder)
    tar_cmd = tar_cmd.strip()
    v, r = generic_run.run_cmd(tar_cmd)
    return v, None

def puaq():
    print("Usage: %s file_to_create.tar (inclusion_list)" % os.path.basename(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 3:
        puaq()

    file_to_create = sys.argv[1]
    incl_list = sys.argv[2:]

    make_pack(file_to_create, incl_list)
