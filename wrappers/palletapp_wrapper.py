#!/usr/bin/env python

import sys
import os

import path_utils
import generic_run

def init(target_archive):

    # target_archive: path to the resulting archive to be initialized. should not pre-exist.

    target_archive_filtered = path_utils.filter_remove_trailing_sep(target_archive)

    # prechecks
    if target_archive_filtered is None:
        return False, "Invalid target archive path"
    if os.path.exists(target_archive_filtered):
        return False, "[%s] already exists." % target_archive_filtered

    # actual command
    plt_cmd = ["palletapp", "--init", target_archive_filtered]
    v, r = generic_run.run_cmd_simple(plt_cmd)
    if not v:
        return False, "Failed running palletapp init command: [%s]" % r

    return True, None

def create(target_archive, source_path):

    # target_archive: path to the resulting archive to be created. should not pre-exist.
    # source_path: path to the input. either a file or a folder containing whatever.

    target_archive_filtered = path_utils.filter_remove_trailing_sep(target_archive)
    source_path_filtered = path_utils.filter_remove_trailing_sep(source_path)

    # prechecks
    if target_archive_filtered is None:
        return False, "Invalid target archive path"
    if os.path.exists(target_archive_filtered):
        return False, "[%s] already exists." % target_archive_filtered
    if source_path_filtered is None:
        return False, "Invalid source path"
    if not os.path.exists(source_path_filtered):
        return False, "[%s] does not exist." % source_path_filtered

    # actual command
    plt_cmd = ["palletapp", "--create", target_archive_filtered, source_path_filtered]
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
    if not os.path.exists(source_archive_filtered):
        return False, "[%s] does not exist." % source_archive_filtered
    if target_path_filtered is None:
        return False, "Invalid target path"
    if not os.path.exists(target_path_filtered):
        return False, "[%s] does not exist." % target_path_filtered
    if not os.path.isdir(target_path_filtered):
        return False, "[%s] is not a folder." % target_path_filtered

    # actual command
    plt_cmd = ["palletapp", "--extract", source_archive_filtered, target_path_filtered]
    v, r = generic_run.run_cmd_simple(plt_cmd)
    if not v:
        return False, "Failed running palletapp extract command: [%s]" % r

    return True, None

def load(target_archive, source_path):

    # target_archive: path to the pre-existing archive to be loaded onto.
    # source_path: path to the input. either a file or a folder containing whatever.

    target_archive_filtered = path_utils.filter_remove_trailing_sep(target_archive)
    source_path_filtered = path_utils.filter_remove_trailing_sep(source_path)

    # prechecks
    if target_archive_filtered is None:
        return False, "Invalid target archive path"
    if not os.path.exists(target_archive_filtered):
        return False, "[%s] does not exist." % target_archive_filtered
    if source_path_filtered is None:
        return False, "Invalid source path"
    if not os.path.exists(source_path_filtered):
        return False, "[%s] does not exist." % source_path_filtered

    # actual command
    plt_cmd = ["palletapp", "--load", target_archive_filtered, source_path_filtered]
    v, r = generic_run.run_cmd_simple(plt_cmd)
    if not v:
        return False, "Failed running palletapp load command: [%s]" % r

    return True, None

def ditch(target_archive, target_route):

    # target_archive: path to the target archive to ditch a route from.
    # target_route: the route to ditch from the target archive.

    target_archive_filtered = path_utils.filter_remove_trailing_sep(target_archive)

    # prechecks
    if target_archive_filtered is None:
        return False, "Invalid source archive"
    if not os.path.exists(target_archive_filtered):
        return False, "[%s] does not exist." % target_archive_filtered
    if target_route is None:
        return False, "Invalid target route"

    # actual command
    plt_cmd = ["palletapp", "--ditch", target_archive_filtered, target_route]
    v, r = generic_run.run_cmd_simple(plt_cmd)
    if not v:
        return False, "Failed running palletapp ditch command: [%s]" % r

    return True, None

def export(source_archive, target_route, target_path):

    # source_archive: path to the source archive to be exported from.
    # target_route: the route to export from the target archive.
    # target_path: path to where the archive's contents are to be exported to.

    source_archive_filtered = path_utils.filter_remove_trailing_sep(source_archive)
    target_path_filtered = path_utils.filter_remove_trailing_sep(target_path)

    # prechecks
    if source_archive_filtered is None:
        return False, "Invalid source archive"
    if not os.path.exists(source_archive_filtered):
        return False, "[%s] does not exist." % source_archive_filtered
    if target_route is None:
        return False, "Invalid target route"
    if target_path_filtered is None:
        return False, "Invalid target path"
    if not os.path.exists(target_path_filtered):
        return False, "[%s] does not exist." % target_path_filtered
    if not os.path.isdir(target_path_filtered):
        return False, "[%s] is not a folder." % target_path_filtered

    # actual command
    plt_cmd = ["palletapp", "--export", source_archive_filtered, target_route, target_path_filtered]
    v, r = generic_run.run_cmd_simple(plt_cmd)
    if not v:
        return False, "Failed running palletapp export command: [%s]" % r

    return True, None

def list(source_archive):

    # source_archive: path to the input archive to be listed from.

    source_archive_filtered = path_utils.filter_remove_trailing_sep(source_archive)

    # prechecks
    if source_archive_filtered is None:
        return False, "Invalid source archive path"
    if not os.path.exists(source_archive_filtered):
        return False, "[%s] does not exist." % source_archive_filtered

    # actual command
    plt_cmd = ["palletapp", "--list", source_archive_filtered]
    v, r = generic_run.run_cmd_simple(plt_cmd)
    if not v:
        return False, "Failed running palletapp list command: [%s]" % r

    return True, r

def puaq(selfhelp):
    print("Usage: %s source_path target_archive.plt" % path_utils.basename_filtered(__file__))
    if selfhelp:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 3:
        puaq(False)

    source_path = sys.argv[1]
    target_archive = sys.argv[2]

    v, r = create(source_path, target_archive)
    if not v:
        print(r)
        sys.exit(1)
