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
import fsquery_adv_filter

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

def _apply_filters(items_input, default_filter, include_list, exclude_list):

    filtering_required = (((default_filter == "include") and (len(exclude_list) > 0)) or (default_filter == "exclude"))

    if not filtering_required:
        return items_input

    filters = []
    items_filtered = []
    if default_filter == "include":
        filters.append( (fsquery_adv_filter.filter_all_positive, "not-used") )
        for ei in exclude_list:
            filters.append( (fsquery_adv_filter.filter_has_not_middle_pieces, path_utils.splitpath(ei, "auto")) )
        items_filtered = fsquery_adv_filter.filter_path_list_and(items_input, filters)

    elif default_filter == "exclude":
        filters.append( (fsquery_adv_filter.filter_all_negative, "not-used") )
        for ii in include_list:
            filters.append( (fsquery_adv_filter.filter_has_middle_pieces, path_utils.splitpath(ii, "auto")) )
        items_filtered = fsquery_adv_filter.filter_path_list_or(items_input, filters)
    else:
        return None

    return items_filtered

def reset_svn_repo_previous(target_repo, backup_obj, previous):

    report = []
    has_any_failed = False

    if previous is None:
        return False, "Previous is unspecified"

    v, r = svn_lib.is_head_clear(target_repo, False, False)
    if not v:
        return False, "Unable to reset to previous on repo [%s]: unable to probe for head clearance: [%s]" % (target_repo, r)

    if not r:
        return False, "Unable to reset to previous on repo [%s]: head is not clear." % target_repo

    v, r = svn_lib.get_previous_list(target_repo, previous)
    if not v:
        return False, "Unable to retrieve list of previous for repo [%s]: [%s]" % (target_repo, r)
    prev_list = r

    if previous > len(prev_list):
        return False, "A higher quantity of previous has been requested than there are available previous revisions (repo [%s])" % target_repo

    c = 0
    for pl in prev_list:
        c += 1

        if c > previous:
            break

        # generate the backup patch
        backup_filename = make_patch_filename(pl, "previous", c)
        backup_contents = ""
        v, r = svn_lib.diff(target_repo, None, pl)
        if not v:
            return False, "Unable to retrieve diff of previous for repo [%s]: [%s]" % (target_repo, r)
        backup_contents = r

        # make the backup patch
        v, r = backup_obj.make_backup("previous", backup_filename, backup_contents)
        gen_patch = r
        if not v:
            return False, "Failed because [%s] already exists." % gen_patch
        report.append(_report_patch(gen_patch))

    if previous > c:
        report.append("WARNING: more indices were requested to be reset than there were previous commits (repo: [%s], requested previous reset counts: [%d], total previous entries reset: [%d])" % (target_repo, previous, (c)))

    v, r = svn_lib.kill_previous(target_repo, previous)
    if not v:
        return False, "Unable to rewind to previous for repo [%s]: [%s]" % (target_repo, r)

    return (not has_any_failed), report

def reset_svn_repo_unversioned(target_repo, backup_obj, default_filter, include_list, exclude_list):

    # unversioned filtering, on SVN, has a considerable limitation:
    # it's not possible to filter out unversioned files or folder if they themselves are inside
    # an unversioned base tree. for example:
    # the_repo/sub/folder/some/domain/component
    # if "sub" itself is unversioned, then it's not possible to deal with unversioned files
    # that reside (for example) inside "domain", using something like: --default-filter-exclude --include '*/domain/*'
    # this could possibly be solved by manually traversing (eg. with fsquery) each entry in order to assemble
    # a full listing, and then processing that instead - and only then filtering the result of that - but that
    # may come with some extra complications and corner cases.

    report = []
    has_any_failed = False

    v, r = svn_lib.get_list_unversioned(target_repo)
    if not v:
        return False, "Unable to retrieve list of unversioned for repo [%s]: [%s]" % (target_repo, r)
    unversioned_list = r

    unversioned_list_filtered = _apply_filters(unversioned_list.copy(), default_filter, include_list, exclude_list)
    if unversioned_list_filtered is None:
        return False, "Unable to apply filters (unversioned operation). Target repo: [%s]" % target_repo
    unversioned_list_final = unversioned_list_filtered.copy()

    # make backups first
    for ui in unversioned_list_final:

        subfolder = "unversioned"
        dn = path_utils.dirname_filtered(ui)
        if dn is None:
            return False, "Failed because [%s]'s dirname can't be resolved." % ui
        v, r = path_utils.based_path_find_outstanding_path(target_repo, dn)
        if v:
            subfolder = path_utils.concat_path(subfolder, r)

        # make the backup patch
        v, r = backup_obj.make_backup_frompath(subfolder, path_utils.basename_filtered(ui), ui)
        gen_patch = r
        if not v:
            return False, "Failed because [%s] already exists." % gen_patch
        report.append(_report_patch(gen_patch))

    # then delete all unversioned, files and folders (that contain unversioned files *only*)
    for ui in unversioned_list_final:
        if not path_utils.remove_path(ui):
            return False, "Failed removing path [%s]" % ui

    return (not has_any_failed), report

def reset_svn_repo_head(target_repo, backup_obj, default_filter, include_list, exclude_list):

    report = []
    has_any_failed = False

    # get new+added files
    v, r = svn_lib.get_head_added_files(target_repo)
    if not v:
        return False, "Unable to retrieve list of added files: [%s]" % r
    added_files = r

    added_files_filtered = _apply_filters(added_files.copy(), default_filter, include_list, exclude_list)
    if added_files_filtered is None:
        return False, "Unable to apply filters (head-added operation). Target repo: [%s]" % target_repo
    added_files_final = added_files_filtered.copy()

    # get versioned+delete-scheduled files
    v, r = svn_lib.get_head_deleted_files(target_repo)
    if not v:
        return False, "Unable to retrieve list of to-be-deleted files: [%s]" % r
    to_be_deleted_files = r

    to_be_deleted_files_filtered = _apply_filters(to_be_deleted_files.copy(), default_filter, include_list, exclude_list)
    if to_be_deleted_files_filtered is None:
        return False, "Unable to apply filters (head-deleted operation). Target repo: [%s]" % target_repo
    to_be_deleted_files_final = to_be_deleted_files_filtered.copy()

    # get versioned+replace-scheduled files
    v, r = svn_lib.get_head_replaced_files(target_repo)
    if not v:
        return False, "Unable to retrieve list of replaced files: [%s]" % r
    replaced_files = r

    replaced_files_filtered = _apply_filters(replaced_files.copy(), default_filter, include_list, exclude_list)
    if replaced_files_filtered is None:
        return False, "Unable to apply filters (head-replaced operation). Target repo: [%s]" % target_repo
    replaced_files_final = replaced_files_filtered.copy()

    # get missing files
    v, r = svn_lib.get_head_missing_files(target_repo)
    if not v:
        return False, "Unable to retrieve list of missing files: [%s]" % r
    missing_files = r

    missing_files_filtered = _apply_filters(missing_files.copy(), default_filter, include_list, exclude_list)
    if missing_files_filtered is None:
        return False, "Unable to apply filters (head-missing operation). Target repo: [%s]" % target_repo
    missing_files_final = missing_files_filtered.copy()

    # get modified files
    v, r = svn_lib.get_head_modified_files(target_repo)
    if not v:
        return False, "Unable to retrieve list of modified files: [%s]" % r
    modified_files = r

    modified_files_filtered = _apply_filters(modified_files.copy(), default_filter, include_list, exclude_list)
    if modified_files_filtered is None:
        return False, "Unable to apply filters (head-modified operation). Target repo: [%s]" % target_repo
    modified_files_final = modified_files_filtered.copy()

    # get conflicted files
    v, r = svn_lib.get_head_conflicted_files(target_repo)
    if not v:
        return False, "Unable to retrieve list of conflicted files: [%s]" % r
    conflicted_files = r

    conflicted_files_filtered = _apply_filters(conflicted_files.copy(), default_filter, include_list, exclude_list)
    if conflicted_files_filtered is None:
        return False, "Unable to apply filters (head-conflicted operation). Target repo: [%s]" % target_repo
    conflicted_files_final = conflicted_files_filtered.copy()

    # un-add new+added files (will be left as unversioned in the repo)
    if len(added_files_final) > 0:
        v, r = svn_lib.revert(target_repo, added_files_final)
        if not v:
            return False, "Failed attempting to un-add files: [%s]" % r
        for af in added_files_final:
            report.append("file [%s] was un-added" % af)

    # un-delete files
    if len(to_be_deleted_files_final) > 0:
        v, r = svn_lib.revert(target_repo, to_be_deleted_files_final)
        if not v:
            return False, "Failed attempting to un-delete files: [%s]" % r
        for df in to_be_deleted_files_final:
            report.append("file [%s] was un-deleted" % df)

    # un-replace files
    if len(replaced_files_final) > 0:
        v, r = svn_lib.revert(target_repo, replaced_files_final)
        if not v:
            return False, "Failed attempting to un-replace files: [%s]" % r
        for rf in replaced_files_final:
            report.append("file [%s] was un-replaced" % rf)

    # restore missing
    for mf in missing_files_final:
        v, r = svn_lib.restore_subpath(target_repo, mf)
        if not v:
            return False, "Failed attempting to restore missing file [%s]: [%s]" % (mf, r)
        report.append("file [%s] has been restored" % mf)

    all_relevant_files_for_bk = []
    all_relevant_files_for_bk += modified_files_final.copy()
    all_relevant_files_for_bk += conflicted_files_final.copy()

    # revert files, backing them up first
    c = 0
    for mf in all_relevant_files_for_bk:
        c += 1

        # generate the backup patch
        backup_filename = make_patch_filename(mf, "head", c)
        backup_contents = ""
        v, r = svn_lib.diff(target_repo, [mf])
        if not v:
            return False, "Failed retrieving diff for [%s]: [%s]" % (mf, r)
        backup_contents = r

        subfolder = "head"
        dn = path_utils.dirname_filtered(mf)
        if dn is None:
            return False, "Unable to resolve [%s]'s dirname." % mf
        v, r = path_utils.based_path_find_outstanding_path(target_repo, dn)
        if v:
            subfolder = path_utils.concat_path(subfolder, r)

        # make the backup patch
        v, r = backup_obj.make_backup(subfolder, backup_filename, backup_contents)
        gen_patch = r
        if not v:
            return False, "Failed because [%s] already exists." % gen_patch

        # revert file changes
        v, r = svn_lib.revert(target_repo, [mf])
        if not v:
            return False, "[%s] patch was generated but reverting failed: [%s]" % (gen_patch, r)
        report.append(_report_patch(gen_patch))

    return (not has_any_failed), report

def reset_svn_repo(target_repo, default_filter, include_list, exclude_list, head, unversioned, previous):

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
        v, r = reset_svn_repo_head(target_repo, backup_obj, default_filter, include_list, exclude_list)
        if not v:
            has_any_failed = True
            report.append("reset_svn_repo_head: [%s]." % r)
        else:
            report += r

    # unversioned
    if unversioned:
        v, r = reset_svn_repo_unversioned(target_repo, backup_obj, default_filter, include_list, exclude_list)
        if not v:
            has_any_failed = True
            report.append("reset_svn_repo_unversioned: [%s]." % r)
        else:
            report += r

    # previous
    if previous > 0:
        v, r = reset_svn_repo_previous(target_repo, backup_obj, previous)
        if not v:
            has_any_failed = True
            report.append("reset_svn_repo_previous: [%s]." % r)
        else:
            report += r

    return (not has_any_failed), report

def puaq():
    print("Usage: %s target_repo [--default-filter-include | --default-filter-exclude] [--include repo_basename] [--exclude repo_basename] [--head] [--unversioned] [--previous X]" % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    target_repo = sys.argv[1]
    params = sys.argv[2:]

    default_filter = "include"
    include_list = []
    exclude_list = []
    include_parse_next = False
    exclude_parse_next = False
    head = False
    unversioned = False
    previous = 0
    previous_parse_next = False

    for p in params:

        if previous_parse_next:
            previous = int(p)
            previous_parse_next = False
            continue

        if include_parse_next:
            include_list.append(p)
            include_parse_next = False
            continue

        if exclude_parse_next:
            exclude_list.append(p)
            exclude_parse_next = False
            continue

        if p == "--default-filter-include":
            default_filter = "include"
        elif p == "--default-filter-exclude":
            default_filter = "exclude"
        elif p == "--include":
            include_parse_next = True
        elif p == "--exclude":
            exclude_parse_next = True
        elif p == "--head":
            head = True
        elif p == "--unversioned":
            unversioned = True
        elif p == "--previous":
            previous_parse_next = True

    v, r = reset_svn_repo(target_repo, default_filter, include_list, exclude_list, head, unversioned, previous)
    for i in r:
        print(i)
    if not v:
        print("Not everything succeeded.")
        sys.exit(1)
    print("All succeeded.")
