#!/usr/bin/env python3

import sys
import os
import shutil

import mvtools_exception
import mvtools_envvars
import path_utils

import detect_repo_type
import svn_lib

import delayed_file_backup
import maketimestamp
import get_platform

def make_patch_filename(path, operation, index):
    if operation is None:
        return "%s_reset_svn_repo_%s.patch" % (str(index), path_utils.basename_filtered(path))
    else:
        return "%s_reset_svn_repo_%s_%s.patch" % (str(index), operation, path_utils.basename_filtered(path))

def _report_patch(patch_filename):
    return "generated backup patch: [%s]" % patch_filename

def _test_repo_path(path):

    v, r = detect_repo_type.detect_repo_type(path)
    if not v:
        return False, r
    if r is None:
        return False, "Path [%s] does not point to a supported repository." % path
    return True, r

def reset_svn_repo_unversioned(target_repo, backup_obj):

    report = []
    has_any_failed = False

    v, r = svn_lib.get_list_unversioned(target_repo)
    if not v:
        return False, ["reset_svn_repo_unversioned: [%s]" % r]
    unversioned_list = r

    # make backups first
    for ui in unversioned_list:

        subfolder = "unversioned"
        dn = path_utils.dirname_filtered(ui)
        if dn is None:
            return False, ["reset_svn_repo_previous: failed because [%s]'s dirname can't be resolved." % ui]
        v, r = path_utils.based_path_find_outstanding_path(target_repo, dn)
        if v:
            subfolder = path_utils.concat_path(subfolder, r)

        # make the backup patch
        v, r = backup_obj.make_backup_frompath(subfolder, path_utils.basename_filtered(ui), ui)
        gen_patch = r
        if not v:
            return False, ["reset_svn_repo_previous: failed because [%s] already exists." % gen_patch]
        report.append(_report_patch(gen_patch))

    # then delete all unversioned, files and folders (that contain unversioned files *only*)
    for ui in unversioned_list:
        if not path_utils.remove_path(ui):
            has_any_failed = True
            report.append("Failed removing path [%s]" % ui)

    return (not has_any_failed), report

def reset_svn_repo_head(target_repo, backup_obj):

    report = []
    has_any_failed = False

    # get new+added files
    v, r = svn_lib.get_head_added_files(target_repo)
    if not v:
        return False, ["Unable to retrieve list of added files: [%s]" % r]
    added_files = r

    # get versioned+delete-scheduled files
    v, r = svn_lib.get_head_deleted_files(target_repo)
    if not v:
        return False, ["Unable to retrieve list of to-be-deleted files: [%s]" % r]
    to_be_deleted_files = r

    # get versioned+replace-scheduled files
    v, r = svn_lib.get_head_replaced_files(target_repo)
    if not v:
        return False, ["Unable to retrieve list of replaced files: [%s]" % r]
    replaced_files = r

    # get missing files
    v, r = svn_lib.get_head_missing_files(target_repo)
    if not v:
        return False, ["reset_svn_repo_file: Unable to retrieve list of missing files: [%s]" % r]
    missing_files = r

    # get modified files
    v, r = svn_lib.get_head_modified_files(target_repo)
    if not v:
        return False, ["reset_svn_repo_file: Unable to retrieve list of modified files: [%s]" % r]
    modified_files = r

    # get conflicted files
    v, r = svn_lib.get_head_conflicted_files(target_repo)
    if not v:
        return False, ["reset_svn_repo_file: Unable to retrieve list of conflicted files: [%s]" % r]
    conflicted_files = r

    # un-add new+added files (will be left as unversioned in the repo)
    if len(added_files) > 0:
        v, r = svn_lib.revert(target_repo, added_files)
        if not v:
            return False, ["Failed attempting to un-add files: [%s]" % r]
        for af in added_files:
            report.append("File [%s] was un-added" % af)

    # un-delete files
    if len(to_be_deleted_files) > 0:
        v, r = svn_lib.revert(target_repo, to_be_deleted_files)
        if not v:
            return False, ["Failed attempting to un-delete files: [%s]" % r]
        for af in to_be_deleted_files:
            report.append("File [%s] was un-deleted" % af)

    # un-replace files
    if len(replaced_files) > 0:
        v, r = svn_lib.revert(target_repo, replaced_files)
        if not v:
            return False, ["Failed attempting to un-replace files: [%s]" % r]
        for rf in replaced_files:
            report.append("File [%s] was un-replaced" % rf)

    # restore missing
    for mf in missing_files:
        v, r = svn_lib.restore_subpath(target_repo, mf)
        if not v:
            return False, ["Failed attempting to restore file [%s]: [%s]" % (mf, r)]
        report.append("file [%s] has been restored" % mf)

    all_relevant_files_for_bk = []
    all_relevant_files_for_bk += modified_files.copy()
    all_relevant_files_for_bk += conflicted_files.copy()

    # revert files, backing them up first
    c = 0
    for mf in all_relevant_files_for_bk:
        c += 1

        # generate the backup patch
        backup_filename = make_patch_filename(mf, "head", c)
        backup_contents = ""
        v, r = svn_lib.diff(target_repo, [mf])
        if not v:
            return False, ["Failed retrieving diff for [%s]: [%s]" % (mf, r)]
        backup_contents = r

        subfolder = "head"
        dn = path_utils.dirname_filtered(mf)
        if dn is None:
            return False, ["Unable to resolve [%s]'s dirname." % mf]
        v, r = path_utils.based_path_find_outstanding_path(target_repo, dn)
        if v:
            subfolder = path_utils.concat_path(subfolder, r)

        # make the backup patch
        v, r = backup_obj.make_backup(subfolder, backup_filename, backup_contents)
        gen_patch = r
        if not v:
            return False, ["Failed because [%s] already exists." % gen_patch]

        # revert file changes
        v, r = svn_lib.revert(target_repo, [mf])
        if not v:
            return False, ["[%s] patch was generated but reverting failed: [%s]" % (gen_patch, r)]
        report.append(_report_patch(gen_patch))

    return (not has_any_failed), report

def reset_svn_repo(target_repo, head, unversioned, previous):

    target_repo = path_utils.filter_remove_trailing_sep(target_repo)
    target_repo = os.path.abspath(target_repo)

    if not os.path.exists(target_repo):
        return False, ["Target repository %s does not exist" % target_repo]

    v, r = _test_repo_path(target_repo)
    if not v:
        return False, [r]
    detected_repo_type = r
    if detected_repo_type != detect_repo_type.REPO_TYPE_SVN:
        return False, ["Unsupported repository type: [%s] and [%s]." % (target_repo, detected_repo_type)]

    v, r = mvtools_envvars.mvtools_envvar_read_temp_path()
    if not v:
        return False, [r]
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

    # head
    if head:
        v, r = reset_svn_repo_head(target_repo, backup_obj)
        if not v:
            has_any_failed = True
            report.append("reset_svn_repo_head: [%s]." % r)
        else:
            report += r

    # unversioned
    if unversioned:
        v, r = reset_svn_repo_unversioned(target_repo, backup_obj)
        if not v:
            has_any_failed = True
            report.append("reset_svn_repo_unversioned: [%s]." % r)
        else:
            report += r

    # mvtodo: previous

    return (not has_any_failed), report

def puaq():
    print("Usage: %s target_repo [--head] [--unversioned] [--previous X]" % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    target_repo = sys.argv[1]
    params = sys.argv[2:]

    head = False
    unversioned = False
    previous = 0
    previous_parse_next = False

    for p in params:

        if previous_parse_next:
            previous = int(p)
            previous_parse_next = False
            continue

        if p == "--head":
            head = True
        elif p == "--unversioned":
            unversioned = True
        elif p == "--previous":
            previous_parse_next = True

    v, r = reset_svn_repo(target_repo, head, unversioned, previous)
    for i in r:
        print(i)
    if not v:
        print("Not everything succeeded.")
        sys.exit(1)
    print("All succeeded.")
