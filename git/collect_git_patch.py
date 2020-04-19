#!/usr/bin/env python3

import sys
import os

import generic_run
import path_utils

def generic_parse(str_line, separator):
    if str_line is None:
        return None
    n = str_line.find(separator)
    if n == -1:
        return None
    return str_line[:n]

def get_stash_name(str_line):
    return generic_parse(str_line, ":")

def get_prev_hash(str_line):
    return generic_parse(str_line, " ")

def collect_git_patch_cmd_generic(repo, storage_path, output_filename, log_title, cmd):

    fullbasepath = path_utils.concat_path(storage_path, repo)
    output_filename_full = path_utils.concat_path(fullbasepath, output_filename)

    try:
        path_utils.guaranteefolder(fullbasepath)
    except path_utils.PathUtilsException as puex:
        return False, "Can't collect patch for %s: Failed guaranteeing folder [%s]" % (log_title, fullbasepath)

    if os.path.exists(output_filename_full):
        return False, "Can't collect patch for %s: %s already exists" % (log_title, output_filename_full)

    v, r = generic_run.run_cmd_simple(cmd)
    if not v:
        return False, "Failed calling git command"

    with open(output_filename_full, "w") as f:
        f.write(r)

    return True, ""

def collect_git_patch_head(repo, storage_path):
    return collect_git_patch_cmd_generic(repo, storage_path, "head.patch", "head", ["git", "-C", repo, "diff", "--no-ext-diff"])

def collect_git_patch_head_id(repo, storage_path):
    return collect_git_patch_cmd_generic(repo, storage_path, "head_id.txt", "head-id", ["git", "-C", repo, "rev-parse", "HEAD"])

def collect_git_patch_head_staged(repo, storage_path):
    return collect_git_patch_cmd_generic(repo, storage_path, "head_staged.patch", "head-staged", ["git", "-C", repo, "diff", "--cached", "--no-ext-diff"])

def collect_git_patch_head_unversioned(repo, storage_path):
    v, r = generic_run.run_cmd_simple(["git", "-C", repo, "ls-files", "--exclude-standard", "--others"])
    if not v:
        return False, "Failed calling git command"

    unversioned_files = [x for x in r.split(os.linesep) if x != ""]
    for uf in unversioned_files:
        target_file = path_utils.concat_path(storage_path, repo, "head_unversioned", uf)
        source_file = path_utils.concat_path(repo, uf)
        try:
            path_utils.guaranteefolder( os.path.dirname(target_file) )
        except path_utils.PathUtilsException as puex:
            return False, "Can't collect patch for head-unversioned: Failed guaranteeing folder [%s]" % os.path.dirname(target_file)
        if os.path.exists(target_file):
            return False, "Can't collect patch for head-unversioned: %s already exists" % target_file
        if not path_utils.copy_to( source_file, target_file ):
            return False, "Can't collect patch for head-unversioned: Cant copy %s to %s" % (source_file, target_file)

    return True, ""

def collect_git_patch_stash(repo, storage_path):

    v, r = generic_run.run_cmd_simple(["git", "-C", repo, "stash", "list"])
    if not v:
        return False, "Failed calling git command"

    stash_list = [get_stash_name(x) for x in r.split(os.linesep) if x != ""]
    for si in stash_list:

        v, r = generic_run.run_cmd_simple(["git", "-C", repo, "stash", "show", "-p", "--no-ext-diff", si])
        if not v:
            return False, "Failed calling git command"

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

    return True, ""

def collect_git_patch_previous(repo, storage_path, previous_number):

    if not previous_number > 0:
        return False, "Can't collect patch for previous: nothing to format"

    v, r = generic_run.run_cmd_simple(["git", "-C", repo, "log", "--oneline"])
    if not v:
        return False, "Failed calling git command"

    prev_list = [get_prev_hash(x) for x in r.split(os.linesep) if x != ""]

    if previous_number > len(prev_list):
        return False, "Can't collect patch for previous: requested %d commits, but there are only %d in total" % (previous_number, len(prev_list))

    for i in range(previous_number):
        v, r = generic_run.run_cmd_simple(["git", "-C", repo, "show", prev_list[i]])
        if not v:
            return False, "Failed calling git command"

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

    return True, ""

def collect_git_patch(repo, storage_path, head, head_id, head_staged, head_unversioned, stash, previous):

    repo = path_utils.filter_remove_trailing_sep(repo)
    repo = os.path.abspath(repo)
    storage_path = path_utils.filter_remove_trailing_sep(storage_path)
    storage_path = os.path.abspath(storage_path)

    if not os.path.exists(repo):
        return False, "Repository %s does not exist" % repo

    if not os.path.exists(storage_path):
        return False, "Storage path %s does not exist" % storage_path

    report = []

    # head
    if head:
        v, r = collect_git_patch_head(repo, storage_path)
        if not v:
            report.append(r)

    # head-id
    if head_id:
        v, r = collect_git_patch_head_id(repo, storage_path)
        if not v:
            report.append(r)

    # head_staged
    if head_staged:
        v, r = collect_git_patch_head_staged(repo, storage_path)
        if not v:
            report.append(r)

    # head_unversioned
    if head_unversioned:
        v, r = collect_git_patch_head_unversioned(repo, storage_path)
        if not v:
            report.append(r)

    # stash
    if stash:
        v, r = collect_git_patch_stash(repo, storage_path)
        if not v:
            report.append(r)

    # previous
    if previous > 0:
        v, r = collect_git_patch_previous(repo, storage_path, previous)
        if not v:
            report.append(r)

    return (len(report)==0), report

def puaq():
    print("Usage: %s repo [--storage-path the_storage_path] [--head] [--head-id] [--head-staged] [--head-unversioned] [--stash] [--previous X]" % os.path.basename(__file__))
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
    head_staged = False
    head_unversioned = False
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
        elif p == "--head-staged":
            head_staged = True
        elif p == "--head-unversioned":
            head_unversioned = True
        elif p == "--stash":
            stash = True
        elif p == "--previous":
            previous_parse_next = True

    if storage_path is None:
        storage_path = os.getcwd()

    v, r = collect_git_patch(repo, storage_path, head, head_id, head_staged, head_unversioned, stash, previous)
    if not v:
        for i in r:
            print("Failed: %s" % i)
        sys.exit(1)
    else:
        print("All succeeded")
