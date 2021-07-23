#!/usr/bin/env python3

import sys
import os
import shutil

import mvtools_exception
import mvtools_envvars
import path_utils

import detect_repo_type
import svn_wrapper
import svn_lib

import delayed_file_backup
import maketimestamp

def make_patch_filename(path, index):
    return "%s_reset_svn_repo_%s.patch" % (str(index), path_utils.basename_filtered(path))

def _report_patch(patch_filename):
    return "generated backup patch: [%s]" % patch_filename

def _test_repo_path(path):

    v, r = detect_repo_type.detect_repo_type(path)
    if not v:
        return False, r
    if r is None:
        return False, "Path [%s] does not point to a supported repository." % path
    return True, r

def reset_svn_repo_file(target_repo, revert_file, patch_index, backup_obj):

    # check if the requested file exists
    if not os.path.exists(revert_file):
        return False, "reset_svn_repo_file: File [%s] does not exist" % revert_file

    # check if the requested file has been newly added in the repo
    v, r = svn_lib.get_added_files(target_repo)
    if not v:
        return False, "reset_svn_repo_file: Unable to retrieve list of added files: [%s]" % r
    added_files = r

    if revert_file in added_files:
        v, r = svn_wrapper.revert(target_repo, [revert_file])
        if not v:
            return False, "reset_svn_repo_file: Failed attempting to un-add files: [%s]" % r
        return True, "File [%s] was un-added" % revert_file

    # check if the requested file is modified in the repo
    v, r = svn_lib.get_modified_files(target_repo)
    if not v:
        return False, "reset_svn_repo_file: [%s]" % r
    mod_files = r

    if not revert_file in mod_files:
        return False, "reset_svn_repo_file: File [%s] is not modified in the repo" % revert_file

    # generate the backup patch
    backup_filename = make_patch_filename(revert_file, patch_index)
    backup_contents = ""
    v, r = svn_wrapper.diff(target_repo, [revert_file])
    if not v:
        return False, "reset_svn_repo_file: [%s]" % r
    backup_contents = r

    # make the backup patch
    v, r = backup_obj.make_backup(backup_filename, backup_contents)
    gen_patch = r
    if not v:
        return False, "reset_svn_repo_file: failed because [%s] already exists." % gen_patch

    # revert file changes
    v, r = svn_wrapper.revert(target_repo, [revert_file])
    if not v:
        return False, "reset_svn_repo_file: [%s] patch was generated but reverting failed: [%s]" % (gen_patch, r)

    return True, _report_patch(gen_patch)

def reset_svn_repo(target_repo, files):

    target_repo = path_utils.filter_remove_trailing_sep(target_repo)
    target_repo = os.path.abspath(target_repo)

    if not os.path.exists(target_repo):
        return False, ["Target repository %s does not exist" % target_repo]

    v, r = _test_repo_path(target_repo)
    if not v:
        return False, r
    detected_repo_type = r
    if detected_repo_type != detect_repo_type.REPO_TYPE_SVN:
        return False, ["Unsupported repository type: [%s] and [%s]." % (target_repo, detected_repo_type)]

    v, r = mvtools_envvars.mvtools_envvar_read_temp_path()
    if not v:
        return False, r
    temp_path = r
    if not os.path.exists(temp_path):
        return False, ["Can't reset svn repo. MVTOOLS_TEMP_PATH envvar is not defined or the path does not exist."]

    timestamp_now = maketimestamp.get_timestamp_now_compact()
    backup_patches_folder = "%s_reset_svn_repo_backup_%s" % (path_utils.basename_filtered(target_repo), timestamp_now)
    backup_patches_folder_fullpath = path_utils.concat_path(temp_path, backup_patches_folder)

    try:
        backup_obj = delayed_file_backup.delayed_file_backup(backup_patches_folder_fullpath)
    except mvtools_exception.mvtools_exception as mvtex:
        return False, [mvtex.message]

    has_any_failed = False
    report = []

    # get modified files
    if files is None:

        v, r = svn_lib.get_modified_files(target_repo)
        if not v:
            return False, [r]
        files = r

        # get new+added files
        v, r = svn_lib.get_added_files(target_repo)
        if not v:
            return False, ["Unable to retrieve list of added files: [%s]" % r]
        added_files = r

        # un-add new+added files (will be left as unversioned in the repo)
        if len(added_files) > 0:
            v, r = svn_wrapper.revert(target_repo, added_files)
            if not v:
                return False, ["Failed attempting to un-add files: [%s]" % r]
            for af in added_files:
                report.append("File [%s] was un-added" % af)

    # reset file by file
    c = 0
    for i in files:
        c += 1
        v, r = reset_svn_repo_file(target_repo, i, c, backup_obj)
        has_any_failed |= (not v)
        report.append(r)
    return (not has_any_failed), report

def puaq():
    print("Usage: %s target_repo [--file filepath]" % os.path.basename(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    target_repo = sys.argv[1]
    params = sys.argv[2:]

    files = []
    files_parse_next = False

    for p in params:

        if files_parse_next:
            files.append(p)
            files_parse_next = False
            continue

        if p == "--file":
            files_parse_next = True

    if len(files) == 0:
        files = None
    v, r = reset_svn_repo(target_repo, files)
    for i in r:
        print(i)
    if not v:
        print("Not everything succeeded.")
        sys.exit(1)
    print("All succeeded.")
