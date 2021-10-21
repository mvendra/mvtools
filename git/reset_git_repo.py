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

def make_patch_filename(path, operation, index):
    if operation is None:
        return "%s_reset_git_repo_%s.patch" % (str(index), path_utils.basename_filtered(path))
    else:
        return "%s_reset_git_repo_%s_%s.patch" % (str(index), operation, path_utils.basename_filtered(path))

def _report_patch(patch_filename):
    return "generated backup patch: [%s]" % patch_filename

def _test_repo_path(path):

    v, r = detect_repo_type.detect_repo_type(path)
    if not v:
        return False, r
    if r is None:
        return False, "Path [%s] does not point to a supported repository." % path
    return True, r

def _has_in_second_pos_of_list(the_list, find_obj):
    for li in the_list:
        if li[1] == find_obj:
            return True
    return False

# mvtodo: disabled
"""
def reset_git_repo_file(target_repo, revert_file, patch_index, backup_obj):

    # check if the requested file is staged in the repo - and if so, unstage it
    v, r = git_lib.get_staged_files(target_repo)
    if not v:
        return False, "reset_git_repo_file: [%s]" % r
    cached_files = r

    if revert_file in cached_files:
        v, r = git_lib.unstage(target_repo, [revert_file])
        if not v:
            return False, "reset_git_repo_file: [%s]" % r

    v, r = git_lib.get_head_deleted_files(target_repo)
    if not v:
        return False, "reset_git_repo_file: [%s]" % r
    deleted_files = r

    if revert_file in deleted_files:
        # simpler case - just undelete and bail out
        v, r = git_lib.checkout(target_repo, [revert_file])
        if not v:
            return False, "reset_git_repo_file: unable to undelete [%s]: [%s]" % (revert_file, r)
        return True, "file [%s] was undeleted" % revert_file

    # check if the requested file exists
    if not os.path.exists(revert_file):
        return False, "reset_git_repo_file: File [%s] does not exist" % revert_file

    # check if the requested file is modified in the repo
    v, r = git_lib.get_head_modified_files(target_repo)
    if not v:
        return False, "reset_git_repo_file: [%s]" % r
    mod_files = r

    if not revert_file in mod_files:
        return False, "reset_git_repo_file: File [%s] is not modified in the repo" % revert_file

    # generate the backup patch
    backup_filename = make_patch_filename(revert_file, "file", patch_index)
    backup_contents = ""
    v, r = git_lib.diff(target_repo, [revert_file])
    if not v:
        return False, "reset_git_repo_file: [%s]" % r
    backup_contents = r

    subfolder = None
    dn = path_utils.dirname_filtered(revert_file)
    if dn is None:
        return False, "reset_git_repo_file: unable to resolve [%s]'s dirname." % revert_file
    v, r = path_utils.based_path_find_outstanding_path(target_repo, dn)
    if v:
        subfolder = r

    # make the backup patch
    v, r = backup_obj.make_backup(subfolder, backup_filename, backup_contents)
    gen_patch = r
    if not v:
        return False, "reset_git_repo_file: failed because [%s] already exists." % gen_patch

    # revert file changes
    v, r = git_lib.checkout(target_repo, [revert_file])
    if not v:
        return False, "reset_git_repo_file: [%s] patch was generated but reverting failed: [%s]" % (gen_patch, r)

    return True, _report_patch(gen_patch)
"""

def reset_git_repo_unversioned(target_repo, backup_obj):

    report = []
    has_any_failed = False

    v, r = git_lib.get_unversioned_files(target_repo)
    if not v:
        return False, "Unable to retrieve unversioned (files only) on repo [%s]: [%s]" % (target_repo, r)
    unversioned_list = r

    v, r = git_lib.get_unversioned_files_and_folders(target_repo)
    if not v:
        return False, "Unable to retrieve unversioned (files and folders) on repo [%s]: [%s]" % (target_repo, r)
    unversioned_plus_folders_list = r

    # make backups first
    for ui in unversioned_list:

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
    for ui in unversioned_plus_folders_list:
        if not path_utils.remove_path(ui):
            return False, "Failed removing path [%s]" % ui

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
        v, r = git_lib.stash_show(target_repo, si)
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

def reset_git_repo_staged(target_repo, backup_obj):

    report = []
    has_any_failed = False

    # get staged files
    v, r = git_lib.get_staged_files(target_repo)
    if not v:
        return False, "Unable to retrieve staged files on repo [%s]: [%s]" % (target_repo, r)
    staged_files = r

    # get staged deleted files
    v, r = git_lib.get_staged_deleted_files(target_repo)
    if not v:
        return False, "Unable to retrieve staged-deleted files on repo [%s]: [%s]" % (target_repo, r)
    staged_deleted_files = r

    # get staged renamed files
    v, r = git_lib.get_staged_renamed_files(target_repo)
    if not v:
        return False, "Unable to retrieve staged-renamed files on repo [%s]: [%s]" % (target_repo, r)
    staged_renamed_files = r

    c = 0
    for sf in staged_files:

        if sf in staged_deleted_files:
            report.append("file [%s] is going to be unstaged (was deleted)" % sf) # just unstage - cant run diff --cached
            continue

        if _has_in_second_pos_of_list(staged_renamed_files, sf):
            report.append("file [%s] is going to be unstaged (was renamed)" % sf) # just unstage - cant run diff --cached
            continue

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

    # unstage everything
    v, r = git_lib.unstage(target_repo)
    if not v:
        return False, "Unable to unstage files on repo [%s]: [%s]" % (target_repo, r)

    return (not has_any_failed), report

def reset_git_repo_head(target_repo, backup_obj):

    report = []
    has_any_failed = False

    # get updated files
    v, r = git_lib.get_head_updated_files(target_repo)
    if not v:
        return False, "Unable to retrieve head-updated files on repo [%s]: [%s]" % (target_repo, r)
    upd_files = r

    # get modified files
    v, r = git_lib.get_head_modified_files(target_repo)
    if not v:
        return False, "Unable to retrieve head-modified files on repo [%s]: [%s]" % (target_repo, r)
    mod_files = r

    # get deleted files
    v, r = git_lib.get_head_deleted_files(target_repo)
    if not v:
        return False, "Unable to retrieve head-deleted files on repo [%s]: [%s]" % (target_repo, r)
    deleted_files = r

    files_to_backup = []
    files_to_backup += mod_files.copy()
    files_to_backup += upd_files.copy()

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
    for df in deleted_files:
        report.append("file [%s] is going to be undeleted" % df)

    # log un-updated files
    for uf in upd_files:
        v, r = git_lib.unstage(target_repo, [uf])
        if not v:
            return False, "Unable to unstage file [%s] on repo [%s]: [%s]" % (uf, target_repo, r)
        report.append("file [%s] was un-updated" % uf)

    # revert all changes
    v, r = git_lib.checkout(target_repo)
    if not v:
        return False, "Unable to checkout repo [%s]: [%s]" % (target_repo, r)

    return (not has_any_failed), report

def reset_git_repo(target_repo, head, staged, stash, unversioned, previous):

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
        v, r = reset_git_repo_staged(target_repo, backup_obj)
        if not v:
            has_any_failed = True
            report.append("reset_git_repo_staged: [%s]." % r)
        else:
            report += r

    # head
    if head:
        v, r = reset_git_repo_head(target_repo, backup_obj)
        if not v:
            has_any_failed = True
            report.append("reset_git_repo_head: [%s]." % r)
        else:
            report += r

    # mvtodo: disabled
    """
    # reset file by file
    has_any_failed = False
    report = []
    c = 0
    for i in files:
        c += 1
        v, r = reset_git_repo_file(target_repo, i, c, backup_obj)
        has_any_failed |= (not v)
        report.append(r)
    """

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
        v, r = reset_git_repo_unversioned(target_repo, backup_obj)
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
    print("Usage: %s target_repo [--head] [--staged] [--stash X (use \"-1\" to reset the entire stash)] [--unversioned] [--previous X]" % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    target_repo = sys.argv[1]
    params = sys.argv[2:]

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

        if p == "--head":
            head = True
        elif p == "--staged":
            staged = True
        elif p == "--stash":
            stash_parse_next = True
        elif p == "--unversioned":
            unversioned = True
        elif p == "--previous":
            previous_parse_next = True

    v, r = reset_git_repo(target_repo, head, staged, stash, unversioned, previous)
    for i in r:
        print(i)
    if not v:
        print("Not everything succeeded.")
        sys.exit(1)
    print("All succeeded.")
