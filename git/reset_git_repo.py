#!/usr/bin/env python3

import sys
import os
import shutil

import mvtools_exception
import mvtools_envvars
import path_utils

import detect_repo_type
import git_lib

import delayed_file_backup
import maketimestamp
import fsquery_adv_filter

def make_patch_filename(path, operation, index):
    if operation is None:
        return "%s_reset_git_repo_%s.patch" % (str(index), path_utils.basename_filtered(path))
    else:
        return "%s_reset_git_repo_%s_%s.patch" % (str(index), operation, path_utils.basename_filtered(path))

def _report_patch(patch_filename):
    return "generated backup patch: [%s]" % patch_filename

def _test_repo_status(repo_path):

    # mvtodo: supporting exotic statuses (such as merge conflicts and etc) bears complexity that does not justify the gains. the git backend
    # also has segfault issues when trying to diff / deal with some of these states. it's best to avoid automating the handling of these
    # status with policy / workflow awareness instead.

    items = []
    funcs = [git_lib.get_head_deleted_deleted_files, git_lib.get_head_updated_added_files, git_lib.get_head_updated_deleted_files, git_lib.get_head_deleted_updated_files, git_lib.get_head_added_added_files, git_lib.get_head_added_updated_files, git_lib.get_head_renamed_modified_files]

    for f in funcs:
        v, r = f(repo_path)
        if not v:
            return False, "Unable to probe for illegal statuses on repo [%s]: [%s]" % (repo_path, r)
        items += r

    if len(items) > 0:
        return False, "The repo [%s] has invalid statuses" % repo_path
    return True, None

def _test_repo_path(path):

    v, r = detect_repo_type.detect_repo_type(path)
    if not v:
        return False, r
    if r is None:
        return False, "Path [%s] does not point to a supported repository." % path
    return True, r

def _apply_filters_tuplelistadapter(items_input, default_filter, include_list, exclude_list):

    assembled_tuple_list = []

    for items in items_input:

        first, second = items
        partial_step = _apply_filters([second], default_filter, include_list, exclude_list)
        if partial_step is None:
            return None
        if len(partial_step) > 0:
            assembled_tuple_list.append((first, second))

    return assembled_tuple_list

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

def reset_git_repo_unversioned(target_repo, backup_obj, default_filter, include_list, exclude_list):

    report = []
    has_any_failed = False

    v, r = git_lib.get_unversioned_files(target_repo)
    if not v:
        return False, "Unable to retrieve unversioned (files only) on repo [%s]: [%s]" % (target_repo, r)
    unversioned_list = r

    unversioned_list_filtered = _apply_filters(unversioned_list.copy(), default_filter, include_list, exclude_list)
    if unversioned_list_filtered is None:
        return False, "Unable to apply filters (unversioned operation). Target repo: [%s]" % target_repo
    unversioned_list_final = unversioned_list_filtered.copy()

    # remove unversioned files while backing them up first
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

        if not path_utils.remove_path(ui):
            return False, "Unable to remove path [%s] from repo [%s]" % (ui, target_repo)

    return (not has_any_failed), report

def reset_git_repo_previous(target_repo, backup_obj, previous):

    report = []
    has_any_failed = False

    if previous is None:
        return False, "Previous is unspecified"

    v, r = git_lib.is_head_clear(target_repo)
    if not v:
        return False, "Unable to reset to previous on repo [%s]: unable to probe for head clearance: [%s]" % (target_repo, r)

    if not r:
        return False, "Unable to reset to previous on repo [%s]: head is not clear." % target_repo

    v, r = git_lib.get_previous_hash_list(target_repo, previous)
    if not v:
        return False, "Unable to retrieve previous hash list on repo [%s]: [%s]" % (target_repo, r)
    previous_hash_list = r

    c = 0
    for phi in previous_hash_list:
        c += 1

        if c > previous:
            break

        # generate the backup patch
        backup_filename = make_patch_filename(phi, "previous", c)
        backup_contents = ""
        v, r = git_lib.show(target_repo, phi)
        if not v:
            return False, "Unable to do git-show on repo [%s]: [%s]" % (target_repo, r)
        backup_contents = r

        # make the backup patch
        v, r = backup_obj.make_backup("previous", backup_filename, backup_contents)
        gen_patch = r
        if not v:
            return False, "Failed because [%s] already exists." % gen_patch
        report.append(_report_patch(gen_patch))

    if previous > c:
        report.append("WARNING: more indices were requested to be reset than there were previous commits (repo: [%s], requested previous reset counts: [%d], total previous entries reset: [%d])" % (target_repo, previous, (c)))

    v, r = git_lib.kill_previous(target_repo, previous)
    if not v:
        return False, "Unable to rewind to previous commit on repo [%s]: [%s]" % (target_repo, r)

    return (not has_any_failed), report

def reset_git_repo_stash(target_repo, backup_obj, stash):

    report = []
    has_any_failed = False

    if stash is None:
        return False, "Stash is unspecified"

    c = 0
    while True:
        c += 1

        if stash != -1: # "-1" means "reset whole stash"
            if c > stash: # done
                break

        v, r = git_lib.get_stash_list(target_repo)
        if not v:
            return False, "Unable to retrieve the stash list on repo [%s]: [%s]" % (target_repo, r)
        stash_list = r

        if stash == -1:
            if c > len(stash_list):
                break
            si = stash_list[c-1]
        else:
            if len(stash_list) == 0:
                if stash >= c:
                    report.append("WARNING: more indices were requested to be reset than there were stash entries (repo: [%s], requested stash reset counts: [%d], total stash entries reset: [%d])" % (target_repo, stash, (c-1)))
                break
            si = stash_list[0]

        # generate the backup patch
        stash_name_to_use = si
        if stash != -1: # artificially adjust the stash name's index when doing a ranged / partial stash reset (otherwise all backup patches would have the index 0)
            stash_name_to_use = git_lib.change_stash_index(si, c-1)
        backup_filename = make_patch_filename(stash_name_to_use, None, c)
        backup_contents = ""
        v, r = git_lib.stash_show_diff(target_repo, si)
        if not v:
            return False, "Unable to stash-show on repo [%s]: [%s]" % (target_repo, r)
        backup_contents = r

        # make the backup patch
        v, r = backup_obj.make_backup("stash", backup_filename, backup_contents)
        gen_patch = r
        if not v:
            return False, "Failed because [%s] already exists." % gen_patch
        report.append(_report_patch(gen_patch))

        if stash != -1:
            v, r = git_lib.stash_drop(target_repo)
            if not v:
                return False, "Unable to stash-drop on repo [%s]: [%s]" % (target_repo, r)

    if stash == -1:
        v, r = git_lib.stash_clear(target_repo)
        if not v:
            return False, "Unable to clear the stash on repo [%s]: [%s]" % (target_repo, r)

    return (not has_any_failed), report

def reset_git_repo_staged(target_repo, backup_obj, default_filter, include_list, exclude_list):

    report = []
    has_any_failed = False

    # get staged renamed files
    v, r = git_lib.get_staged_renamed_files(target_repo)
    if not v:
        return False, "Unable to retrieve staged-renamed files on repo [%s]: [%s]" % (target_repo, r)
    staged_renamed_files = r

    # filter staged renamed files
    staged_renamed_files_filtered = _apply_filters_tuplelistadapter(staged_renamed_files.copy(), default_filter, include_list, exclude_list)
    if staged_renamed_files_filtered is None:
        return False, "Unable to apply filters (staged-renamed operation). Target repo: [%s]" % target_repo
    staged_renamed_files_final = staged_renamed_files_filtered.copy()

    for srf in staged_renamed_files_final:
        oldname, newname = srf
        report.append("file [%s] is going to be unstaged (was renamed)" % newname)
        v, r = git_lib.unstage(target_repo, [newname])
        if not v:
            return False, "Unable to unstage file [%s] on repo [%s]: [%s]" % (srf, target_repo, r)
        report.append("file [%s] is going to be deleted (was unversioned-leftover from the un-renaming)" % newname)

        subfolder = "staged"
        dn = path_utils.dirname_filtered(newname)
        if dn is None:
            return False, "Failed because [%s]'s dirname can't be resolved." % newname
        v, r = path_utils.based_path_find_outstanding_path(target_repo, dn)
        if v:
            subfolder = path_utils.concat_path(subfolder, r)

        # make the backup patch
        v, r = backup_obj.make_backup_frompath(subfolder, path_utils.basename_filtered(newname), newname)
        gen_patch = r
        if not v:
            return False, "Failed because [%s] already exists." % gen_patch
        report.append(_report_patch(gen_patch))

        if not path_utils.remove_path(newname): # cleanup the now-leftover resulting unversioned
            return False, "Unable to remove leftover unversioned file [%s] on repo [%s]" % (newname, target_repo)

    # get staged deleted files
    v, r = git_lib.get_staged_deleted_files(target_repo)
    if not v:
        return False, "Unable to retrieve staged-deleted files on repo [%s]: [%s]" % (target_repo, r)
    staged_deleted_files = r

    # filter staged deleted files
    staged_deleted_files_filtered = _apply_filters(staged_deleted_files.copy(), default_filter, include_list, exclude_list)
    if staged_deleted_files_filtered is None:
        return False, "Unable to apply filters (staged-deleted operation). Target repo: [%s]" % target_repo
    staged_deleted_files_final = staged_deleted_files_filtered.copy()

    for sdf in staged_deleted_files_final:
        report.append("file [%s] is going to be unstaged (was deleted)" % sdf)
        v, r = git_lib.unstage(target_repo, [sdf])
        if not v:
            return False, "Unable to unstage file [%s] on repo [%s]: [%s]" % (sdf, target_repo, r)

    # get staged files
    v, r = git_lib.get_staged_files(target_repo)
    if not v:
        return False, "Unable to retrieve staged files on repo [%s]: [%s]" % (target_repo, r)
    staged_files = r

    # filter staged files
    staged_files_filtered = _apply_filters(staged_files.copy(), default_filter, include_list, exclude_list)
    if staged_files_filtered is None:
        return False, "Unable to apply filters (staged operation). Target repo: [%s]" % target_repo
    staged_files_final = staged_files_filtered.copy()

    c = 0
    for sf in staged_files_final:
        c += 1

        # generate the backup patch
        backup_filename = make_patch_filename(sf, "staged", c)
        backup_contents = ""
        v, r = git_lib.diff_cached(target_repo, [sf])
        if not v:
            return False, "Unable to retrieve cached diff on repo [%s]: [%s]" % (target_repo, r)
        backup_contents = r

        subfolder = "staged"
        dn = path_utils.dirname_filtered(sf)
        if dn is None:
            return False, "Failed because [%s]'s dirname can't be resolved." % sf
        v, r = path_utils.based_path_find_outstanding_path(target_repo, dn)
        if v:
            subfolder = path_utils.concat_path(subfolder, r)

        # make the backup patch
        v, r = backup_obj.make_backup(subfolder, backup_filename, backup_contents)
        gen_patch = r
        if not v:
            return False, "Failed because [%s] already exists." % gen_patch
        report.append(_report_patch(gen_patch))

        # unstage file
        v, r = git_lib.unstage(target_repo, [sf])
        if not v:
            return False, "Unable to unstage file [%s] on repo [%s]: [%s]" % (sf, target_repo, r)

    return (not has_any_failed), report

def reset_git_repo_head(target_repo, backup_obj, default_filter, include_list, exclude_list):

    report = []
    has_any_failed = False

    # get updated files
    v, r = git_lib.get_head_updated_files(target_repo)
    if not v:
        return False, "Unable to retrieve head-updated files on repo [%s]: [%s]" % (target_repo, r)
    upd_files = r

    # filter updated files
    upd_files_filtered = _apply_filters(upd_files.copy(), default_filter, include_list, exclude_list)
    if upd_files_filtered is None:
        return False, "Unable to apply filters (head-updated operation). Target repo: [%s]" % target_repo
    upd_files_final = upd_files_filtered.copy()

    # get modified files
    v, r = git_lib.get_head_modified_files(target_repo)
    if not v:
        return False, "Unable to retrieve head-modified files on repo [%s]: [%s]" % (target_repo, r)
    mod_files = r

    # filter modified files
    mod_files_filtered = _apply_filters(mod_files.copy(), default_filter, include_list, exclude_list)
    if mod_files_filtered is None:
        return False, "Unable to apply filters (head-modified operation). Target repo: [%s]" % target_repo
    mod_files_final = mod_files_filtered.copy()

    # get deleted files
    v, r = git_lib.get_head_deleted_files(target_repo)
    if not v:
        return False, "Unable to retrieve head-deleted files on repo [%s]: [%s]" % (target_repo, r)
    deleted_files = r

    # filter deleted files
    deleted_files_filtered = _apply_filters(deleted_files.copy(), default_filter, include_list, exclude_list)
    if deleted_files_filtered is None:
        return False, "Unable to apply filters (head-deleted operation). Target repo: [%s]" % target_repo
    deleted_files_final = deleted_files_filtered.copy()

    # get modified-modified files
    v, r = git_lib.get_head_modified_modified_files(target_repo)
    if not v:
        return False, "Unable to retrieve head-modified-modified files on repo [%s]: [%s]" % (target_repo, r)
    mod_mod_files = r

    # filter modified-modified files
    mod_mod_files_filtered = _apply_filters(mod_mod_files.copy(), default_filter, include_list, exclude_list)
    if mod_mod_files_filtered is None:
        return False, "Unable to apply filters (head-modified-modified operation). Target repo: [%s]" % target_repo
    mod_mod_files_final = mod_mod_files_filtered.copy()

    # get added-modified files
    v, r = git_lib.get_head_added_modified_files(target_repo)
    if not v:
        return False, "Unable to retrieve head-added-modified files on repo [%s]: [%s]" % (target_repo, r)
    add_mod_files = r

    # filter added-modified files
    add_mod_files_filtered = _apply_filters(add_mod_files.copy(), default_filter, include_list, exclude_list)
    if add_mod_files_filtered is None:
        return False, "Unable to apply filters (head-added-modified operation). Target repo: [%s]" % target_repo
    add_mod_files_final = add_mod_files_filtered.copy()

    # get renamed-modified files
    v, r = git_lib.get_head_renamed_modified_files(target_repo)
    if not v:
        return False, "Unable to retrieve head-renamed-modified files on repo [%s]: [%s]" % (target_repo, r)
    ren_mod_files = r

    # filter renamed-modified files
    ren_mod_files_filtered = _apply_filters_tuplelistadapter(ren_mod_files.copy(), default_filter, include_list, exclude_list)
    if ren_mod_files_filtered is None:
        return False, "Unable to apply filters (renamed-modified operation). Target repo: [%s]" % target_repo
    ren_mod_files_final = ren_mod_files_filtered.copy()

    files_to_backup = []
    files_to_backup += mod_files_final.copy()
    files_to_backup += upd_files_final.copy()
    files_to_backup += mod_mod_files_final.copy()
    files_to_backup += add_mod_files_final.copy()

    for rmf in ren_mod_files_final:
        oldname, newname = rmf
        files_to_backup.append(newname)

    c = 0
    for mf in files_to_backup:
        c += 1

        # generate the backup patch
        backup_filename = make_patch_filename(mf, "head", c)
        backup_contents = ""
        v, r = git_lib.diff(target_repo, [mf])
        if not v:
            return False, "Unable to retrieve diff on repo [%s]: [%s]" % (target_repo, r)
        backup_contents = r

        subfolder = "head"
        dn = path_utils.dirname_filtered(mf)
        if dn is None:
            return False, "Failed because [%s]'s dirname can't be resolved." % mf
        v, r = path_utils.based_path_find_outstanding_path(target_repo, dn)
        if v:
            subfolder = path_utils.concat_path(subfolder, r)

        # make the backup patch
        v, r = backup_obj.make_backup(subfolder, backup_filename, backup_contents)
        gen_patch = r
        if not v:
            return False, "Failed because [%s] already exists." % gen_patch
        report.append(_report_patch(gen_patch))

    # log undeleted files
    for df in deleted_files_final:
        report.append("file [%s] is going to be undeleted" % df)

    files_to_reset = []
    files_to_reset += upd_files_final.copy()
    files_to_reset += mod_mod_files_final.copy()
    files_to_reset += add_mod_files_final.copy()

    for rmf in ren_mod_files_final:
        oldname, newname = rmf
        files_to_reset.append(newname)

    # log and reset mixed states
    for ftr in files_to_reset:
        v, r = git_lib.soft_reset(target_repo, [ftr])
        if not v:
            return False, "Unable to reset file [%s] on repo [%s]: [%s]" % (ftr, target_repo, r)
        report.append("file [%s] was head-reset (soft)" % ftr)

    files_to_checkout = []
    files_to_checkout += mod_files_final.copy()
    files_to_checkout += deleted_files_final.copy()
    files_to_checkout += upd_files_final.copy()
    files_to_checkout += mod_mod_files_final.copy()

    # revert changes to head
    for fc in files_to_checkout:
        v, r = git_lib.checkout(target_repo, [fc])
        if not v:
            return False, "Unable to checkout file [%s] from repo [%s]: [%s]" % (fc, target_repo, r)

    return (not has_any_failed), report

def reset_git_repo(target_repo, default_filter, include_list, exclude_list, head, staged, stash, unversioned, previous):

    target_repo = path_utils.filter_remove_trailing_sep(target_repo)
    target_repo = os.path.abspath(target_repo)

    if not os.path.exists(target_repo):
        return False, ["Target repository %s does not exist" % target_repo]

    v, r = _test_repo_path(target_repo)
    if not v:
        return False, [r]
    detected_repo_type = r
    if detected_repo_type != detect_repo_type.REPO_TYPE_GIT_STD:
        return False, ["Unsupported repository type: [%s] and [%s]." % (target_repo, detected_repo_type)]

    v, r = _test_repo_status(target_repo)
    if not v:
        return False, [r]

    v, r = mvtools_envvars.mvtools_envvar_read_temp_path()
    if not v:
        return False, [r]
    temp_path = r
    if not os.path.exists(temp_path):
        return False, ["Can't reset git repo. MVTOOLS_TEMP_PATH envvar is not defined or the path does not exist."]

    timestamp_now = maketimestamp.get_timestamp_now_compact()
    backup_patches_folder = "%s_reset_git_repo_backup_%s" % (path_utils.basename_filtered(target_repo), timestamp_now)
    backup_patches_folder_fullpath = path_utils.concat_path(temp_path, backup_patches_folder)

    try:
        backup_obj = delayed_file_backup.delayed_file_backup(backup_patches_folder_fullpath)
    except mvtools_exception.mvtools_exception as mvtex:
        return False, [mvtex.message]

    has_any_failed = False
    report = []

    # staged
    if staged:
        v, r = reset_git_repo_staged(target_repo, backup_obj, default_filter, include_list, exclude_list)
        if not v:
            has_any_failed = True
            report.append("reset_git_repo_staged: [%s]." % r)
        else:
            report += r

    # head
    if head:
        v, r = reset_git_repo_head(target_repo, backup_obj, default_filter, include_list, exclude_list)
        if not v:
            has_any_failed = True
            report.append("reset_git_repo_head: [%s]." % r)
        else:
            report += r

    # stash
    if stash != 0:
        v, r = reset_git_repo_stash(target_repo, backup_obj, stash)
        if not v:
            has_any_failed = True
            report.append("reset_git_repo_stash: [%s]." % r)
        else:
            report += r

    # unversioned
    if unversioned:
        v, r = reset_git_repo_unversioned(target_repo, backup_obj, default_filter, include_list, exclude_list)
        if not v:
            has_any_failed = True
            report.append("reset_git_repo_unversioned: [%s]." % r)
        else:
            report += r

    # previous
    if previous > 0:
        v, r = reset_git_repo_previous(target_repo, backup_obj, previous)
        if not v:
            has_any_failed = True
            report.append("reset_git_repo_previous: [%s]." % r)
        else:
            report += r

    return (not has_any_failed), report

def puaq():
    print("Usage: %s target_repo [--default-filter-include | --default-filter-exclude] [--include repo_basename] [--exclude repo_basename] [--head] [--staged] [--stash X (use \"-1\" to reset the entire stash)] [--unversioned] [--previous X]" % path_utils.basename_filtered(__file__))
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
    staged = False
    stash = 0
    stash_parse_next = False
    unversioned = False
    previous = 0
    previous_parse_next = False

    for p in params:

        if stash_parse_next:
            stash = int(p)
            stash_parse_next = False
            continue

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
        elif p == "--staged":
            staged = True
        elif p == "--stash":
            stash_parse_next = True
        elif p == "--unversioned":
            unversioned = True
        elif p == "--previous":
            previous_parse_next = True

    v, r = reset_git_repo(target_repo, default_filter, include_list, exclude_list, head, staged, stash, unversioned, previous)
    for i in r:
        print(i)
    if not v:
        print("Not everything succeeded.")
        sys.exit(1)
    print("All succeeded.")
