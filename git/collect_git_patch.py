#!/usr/bin/env python3

import sys
import os

import git_lib
import git_wrapper
import path_utils

def collect_git_patch_cmd_generic(repo, storage_path, output_filename, log_title, content):

    if len(content) == 0:
        return False, "Empty contents"

    fullbasepath = path_utils.concat_path(storage_path, repo)
    output_filename_full = path_utils.concat_path(fullbasepath, output_filename)

    try:
        path_utils.guaranteefolder(fullbasepath)
    except path_utils.PathUtilsException as puex:
        return False, "Can't collect patch for %s: Failed guaranteeing folder [%s]" % (log_title, fullbasepath)

    if os.path.exists(output_filename_full):
        return False, "Can't collect patch for %s: %s already exists" % (log_title, output_filename_full)

    with open(output_filename_full, "w") as f:
        f.write(content)

    return True, output_filename_full

def collect_git_patch_head(repo, storage_path):
    v, r = git_wrapper.diff(repo)
    if not v:
        return False, "Failed calling git command for head: %s. Repository: %s." % (r, repo)
    return collect_git_patch_cmd_generic(repo, storage_path, "head.patch", "head", r)

def collect_git_patch_head_id(repo, storage_path):
    v, r = git_wrapper.rev_parse_head(repo)
    if not v:
        return False, "Failed calling git command for head-id: %s. Repository: %s." % (r, repo)
    return collect_git_patch_cmd_generic(repo, storage_path, "head_id.txt", "head-id", r)

def collect_git_patch_staged(repo, storage_path):
    v, r = git_wrapper.diff_cached(repo)
    if not v:
        return False, "Failed calling git command for staged: %s. Repository: %s." % (r, repo)
    return collect_git_patch_cmd_generic(repo, storage_path, "staged.patch", "staged", r)

def collect_git_patch_unversioned(repo, storage_path):

    v, r = git_lib.get_list_unversioned_files(repo)
    if not v:
        return False, "Failed calling git command for unversioned: %s. Repository: %s." % (r, repo)
    unversioned_files = r
    written_file_list = []

    for uf in unversioned_files:
        target_file = path_utils.concat_path(storage_path, repo, "unversioned", uf)
        source_file = path_utils.concat_path(repo, uf)
        try:
            path_utils.guaranteefolder( os.path.dirname(target_file) )
        except path_utils.PathUtilsException as puex:
            return False, "Can't collect patch for unversioned: Failed guaranteeing folder [%s]" % os.path.dirname(target_file)
        if os.path.exists(target_file):
            return False, "Can't collect patch for unversioned: %s already exists" % target_file
        if not path_utils.copy_to( source_file, target_file ):
            return False, "Can't collect patch for unversioned: Cant copy %s to %s" % (source_file, target_file)
        written_file_list.append(target_file)

    return True, written_file_list

def collect_git_patch_stash(repo, storage_path):

    v, r = git_lib.get_stash_list(repo)
    if not v:
        return False, "Failed calling git command for stash: %s. Repository: %s." % (r, repo)
    stash_list = r
    written_file_list = []

    for si in stash_list:

        v, r = git_wrapper.stash_show(repo, si)
        if not v:
            return False, "Failed calling git command for stash: %s. Repository: %s. Stash name: %s." % (r, repo, si)

        stash_current_contents = r
        stash_current_file_name = path_utils.concat_path(storage_path, repo, "%s.patch" % si)

        try:
            path_utils.guaranteefolder( os.path.dirname(stash_current_file_name) )
        except path_utils.PathUtilsException as puex:
            return False, "Can't collect patch for stash: Failed guaranteeing folder [%s]" % os.path.dirname(stash_current_file_name)

        if os.path.exists(stash_current_file_name):
            return False, "Can't collect patch for stash: %s already exists" % stash_current_file_name
        with open(stash_current_file_name, "w") as f:
            f.write(stash_current_contents)
        written_file_list.append(stash_current_file_name)

    return True, written_file_list

def collect_git_patch_previous(repo, storage_path, previous_number):

    if not previous_number > 0:
        return False, "Can't collect patch for previous: nothing to format"

    v, r = git_lib.get_previous_hash_list(repo, previous_number)
    if not v:
        return False, "Failed calling git command for previous: %s. Repository: %s." % (r, repo)
    prev_list = r
    written_file_list = []

    if previous_number > len(prev_list):
        return False, "Can't collect patch for previous: requested %d commits, but there are only %d in total" % (previous_number, len(prev_list))

    for i in range(previous_number):
        v, r = git_wrapper.show(repo, prev_list[i])
        if not v:
            return False, "Failed calling git command for previous: %s. Repository: %s. Commit id: %s." % (r, repo, prev_list[i])

        previous_file_content = r
        previous_file_name = path_utils.concat_path(storage_path, repo, "previous_%d_%s.patch" % ((i+1), prev_list[i]))

        try:
            path_utils.guaranteefolder( os.path.dirname(previous_file_name) )
        except path_utils.PathUtilsException as puex:
            return False, "Can't collect patch for previous: Failed guaranteeing folder [%s]" % os.path.dirname(previous_file_name)

        if os.path.exists(previous_file_name):
            return False, "Can't collect patch for previous: %s already exists" % previous_file_name
        with open(previous_file_name, "w") as f:
            f.write(previous_file_content)
        written_file_list.append(previous_file_name)

    return True, written_file_list

def collect_git_patch(repo, storage_path, head, head_id, staged, unversioned, stash, previous):

    repo = path_utils.filter_remove_trailing_sep(repo)
    repo = os.path.abspath(repo)
    storage_path = path_utils.filter_remove_trailing_sep(storage_path)
    storage_path = os.path.abspath(storage_path)

    if not os.path.exists(repo):
        return False, ["Repository %s does not exist" % repo]

    if not os.path.exists(storage_path):
        return False, ["Storage path %s does not exist" % storage_path]

    report = []
    has_any_failed = False

    # head
    if head:
        v, r = collect_git_patch_head(repo, storage_path)
        if not v:
            has_any_failed = True
            report.append("collect_git_patch_head: [%s]" % r)
        else:
            report.append(r)

    # head-id
    if head_id:
        v, r = collect_git_patch_head_id(repo, storage_path)
        if not v:
            has_any_failed = True
            report.append("collect_git_patch_head_id: [%s]" % r)
        else:
            report.append(r)

    # staged
    if staged:
        v, r = collect_git_patch_staged(repo, storage_path)
        if not v:
            has_any_failed = True
            report.append("collect_git_patch_staged: [%s]" % r)
        else:
            report.append(r)

    # unversioned
    if unversioned:
        v, r = collect_git_patch_unversioned(repo, storage_path)
        if not v:
            has_any_failed = True
            report.append("collect_git_patch_unversioned: [%s]" % r)
        else:
            report.append(r)

    # stash
    if stash:
        v, r = collect_git_patch_stash(repo, storage_path)
        if not v:
            has_any_failed = True
            report.append("collect_git_patch_stash: [%s]" % r)
        else:
            report.append(r)

    # previous
    if previous > 0:
        v, r = collect_git_patch_previous(repo, storage_path, previous)
        if not v:
            has_any_failed = True
            report.append("collect_git_patch_previous: [%s]" % r)
        else:
            report.append(r)

    return (not has_any_failed), report

def puaq():
    print("Usage: %s repo [--storage-path the_storage_path] [--head] [--head-id] [--staged] [--unversioned] [--stash] [--previous X]" % os.path.basename(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    repo = sys.argv[1]
    storage_path = None
    params = sys.argv[2:]

    # parse options
    storage_path_parse_next = False
    head = False
    head_id = False
    staged = False
    unversioned = False
    stash = False
    previous = 0
    previous_parse_next = False

    for p in params:

        if storage_path_parse_next:
            storage_path = p
            storage_path_parse_next = False
            continue

        if previous_parse_next:
            previous = int(p)
            previous_parse_next = False
            continue

        if p == "--storage-path":
            storage_path_parse_next = True
        elif p == "--head":
            head = True
        elif p == "--head-id":
            head_id = True
        elif p == "--staged":
            staged = True
        elif p == "--unversioned":
            unversioned = True
        elif p == "--stash":
            stash = True
        elif p == "--previous":
            previous_parse_next = True

    if storage_path is None:
        storage_path = os.getcwd()

    v, r = collect_git_patch(repo, storage_path, head, head_id, staged, unversioned, stash, previous)
    if not v:
        for i in r:
            print("Failed: %s" % i)
        sys.exit(1)
    else:
        print("All succeeded")
