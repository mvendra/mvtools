#!/usr/bin/env python3

import sys
import os

import path_utils
import svn_lib

ERRMSG_EMPTY = "Empty contents"

def collect_svn_patch_cmd_generic(repo, storage_path, output_filename, log_title, content):

    if len(content) == 0:
        return False, ERRMSG_EMPTY

    fullbasepath = path_utils.concat_path(storage_path, repo)
    output_filename_full = path_utils.concat_path(fullbasepath, output_filename)

    if not path_utils.guaranteefolder(fullbasepath):
        return False, "Can't collect patch for [%s]: Failed guaranteeing folder [%s]." % (log_title, fullbasepath)

    if os.path.exists(output_filename_full):
        return False, "Can't collect patch for [%s]: [%s] already exists." % (log_title, output_filename_full)

    with open(output_filename_full, "wb") as f:
        f.write(content)

    return True, output_filename_full

def collect_svn_patch_head(repo, storage_path):
    v, r = svn_lib.diff(repo)
    if not v:
        return False, "Failed calling svn command for head: [%s]. Repository: [%s]." % (r, repo)
    return collect_svn_patch_cmd_generic(repo, storage_path, "head.patch", "head", r)

def collect_svn_patch_head_id(repo, storage_path):
    v, r = svn_lib.get_head_revision(repo)
    if not v:
        return False, "Failed calling svn command for head-id: [%s]. Repository: [%s]." % (r, repo)
    return collect_svn_patch_cmd_generic(repo, storage_path, "head_id.txt", "head-id", r.encode("utf8"))

def collect_svn_patch_unversioned(repo, storage_path):

    v, r = svn_lib.get_list_unversioned(repo)
    if not v:
        return False, "Failed calling svn command for unversioned: [%s]. Repository: [%s]." % (r, repo)
    unversioned_items = r
    written_file_list = []

    target_base = path_utils.concat_path(storage_path, repo, "unversioned")
    if os.path.exists(target_base):
        return False, "Can't collect patch for unversioned: [%s] already exists." % target_base

    if not path_utils.guaranteefolder(target_base):
        return False, "Can't collect patch for unversioned: Failed guaranteeing folder: [%s]." % target_base

    for uf in unversioned_items:

        v, r = path_utils.based_path_find_outstanding_path(repo, uf)
        if not v:
            return False, "Can't collect patch for unversioned: Failed separating [%s]'s path from its base path [%s]" % (repo, uf)
        item_remaining_path = r

        target_final_path = path_utils.concat_path(target_base, item_remaining_path)

        if os.path.exists(target_final_path):
            return False, "Can't collect patch for unversioned: [%s] already exists" % target_final_path
        if not path_utils.based_copy_to( repo, uf, target_base ):
            return False, "Can't collect patch for unversioned: Cant copy [%s] to [%s]" % (uf, target_base)
        written_file_list.append(target_final_path)

    return True, written_file_list

def collect_svn_patch_previous(repo, storage_path, previous_number):

    if not previous_number > 0:
        return False, "Can't collect patch for previous: nothing to format."

    v, r = svn_lib.get_previous_list(repo, previous_number)
    if not v:
        return False, "Failed calling svn command for previous: [%s]. Repository: [%s]." % (r, repo)
    prev_list = r
    written_file_list = []

    if previous_number > len(prev_list):
        return False, "Can't collect patch for previous: requested [%d] commits, but there are only [%d] in total." % (previous_number, len(prev_list))

    for i in range(previous_number):
        v, r = svn_lib.diff(repo, None, prev_list[i])
        if not v:
            return False, "Failed calling svn command for previous: [%s]. Repository: [%s]. Revision: [%s]." % (r, repo, prev_list[i])

        previous_file_content = r
        previous_file_name = path_utils.concat_path(storage_path, repo, "previous_%d_%s.patch" % ((i+1), prev_list[i]))

        if not path_utils.guaranteefolder( path_utils.dirname_filtered(previous_file_name) ):
            return False, "Can't collect patch for previous: Failed guaranteeing folder [%s]." % path_utils.dirname_filtered(previous_file_name)

        if os.path.exists(previous_file_name):
            return False, "Can't collect patch for previous: [%s] already exists." % previous_file_name
        with open(previous_file_name, "wb") as f:
            f.write(previous_file_content)
        written_file_list.append(previous_file_name)

    return True, written_file_list

def collect_svn_patch(repo, storage_path, head, head_id, unversioned, previous):

    repo = path_utils.filter_remove_trailing_sep(repo)
    repo = os.path.abspath(repo)
    storage_path = path_utils.filter_remove_trailing_sep(storage_path)
    storage_path = os.path.abspath(storage_path)

    if not os.path.exists(repo):
        return False, ["Repository [%s] does not exist." % repo]

    if not os.path.exists(storage_path):
        return False, ["Storage path [%s] does not exist." % storage_path]

    report = []
    has_any_failed = False

    # head
    if head:
        v, r = collect_svn_patch_head(repo, storage_path)
        if not v:
            has_any_failed = True
            report.append("collect_svn_patch_head: [%s]." % r)
        else:
            report.append(r)

    # head-id
    if head_id:
        v, r = collect_svn_patch_head_id(repo, storage_path)
        if not v:
            has_any_failed = True
            report.append("collect_svn_patch_head_id: [%s]." % r)
        else:
            report.append(r)

    # unversioned
    if unversioned:
        v, r = collect_svn_patch_unversioned(repo, storage_path)
        if not v:
            has_any_failed = True
            report.append("collect_svn_patch_unversioned: [%s]." % r)
        else:
            report.append(r)

    # previous
    if previous > 0:
        v, r = collect_svn_patch_previous(repo, storage_path, previous)
        if not v:
            has_any_failed = True
            report.append("collect_svn_patch_previous: [%s]." % r)
        else:
            report.append(r)

    return (not has_any_failed), report

def puaq():
    print("Usage: %s repo [--storage-path the_storage_path] [--head] [--head-id] [--unversioned] [--previous X]" % path_utils.basename_filtered(__file__))
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
    unversioned = False
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
        elif p == "--unversioned":
            unversioned = True
        elif p == "--previous":
            previous_parse_next = True

    if storage_path is None:
        storage_path = os.getcwd()

    v, r = collect_svn_patch(repo, storage_path, head, head_id, unversioned, previous)
    if not v:
        for i in r:
            print("Failed: [%s]." % i)
        sys.exit(1)
    else:
        print("All succeeded.")
