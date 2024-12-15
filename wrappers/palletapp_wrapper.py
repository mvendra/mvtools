#!/usr/bin/env python3

import sys
import os

import path_utils
import generic_run

def create(source_path, target_archive):

    # source_path: path to the input. either a file or a folder containing whatever.
    # target_archive: path to the resulting archive to be created. should not pre-exist.

    source_path_filtered = path_utils.filter_remove_trailing_sep(source_path)
    target_archive_filtered = path_utils.filter_remove_trailing_sep(target_archive)

    # prechecks
    if source_path_filtered is None:
        return False, "Invalid source path"
    if target_archive_filtered is None:
        return False, "Invalid target archive path"
    if os.path.exists(target_archive_filtered):
        return False, "%s already exists." % target_archive_filtered

    # actual command
    plt_cmd = ["palletapp", "--create", source_path_filtered, target_archive_filtered]
    v, r = generic_run.run_cmd_simple(plt_cmd)
    if not v:
        return False, "Failed running palletapp create command: [%s]" % r

    return True, None

def extract(source_archive, target_path):

    # source_archive: path to the input archive to be extracted.
    # target_path: path to where the archive's contents are to be extracted to.

    source_archive_filtered = path_utils.filter_remove_trailing_sep(source_archive)
    target_path_filtered = path_utils.filter_remove_trailing_sep(target_path)

    # prechecks
    if source_archive_filtered is None:
        return False, "Invalid source archive"
    if target_path_filtered is None:
        return False, "Invalid target path"
    if not os.path.exists(source_archive_filtered):
        return False, "%s does not exist." % source_archive_filtered
    if not os.path.exists(target_path_filtered):
        return False, "%s does not exist." % target_path_filtered

    # actual command
    plt_cmd = ["palletapp", "--extract", source_archive_filtered, target_path_filtered]
    v, r = generic_run.run_cmd_simple(plt_cmd)
    if not v:
        return False, "Failed running palletapp extract command: [%s]" % r

    return True, None

def puaq():
    print("Usage: %s source_path target_archive.plt" % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 3:
        puaq()

    source_path = sys.argv[1]
    target_archive = sys.argv[2]

    v, r = create(source_path, target_archive)
    if not v:
        print(r)
        sys.exit(1)
