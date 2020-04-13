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

def get_prev_hash(str_line):
    return generic_parse(str_line, " ")

def is_non_generic(char_input, list_select):
    for c in list_select:
        if c == char_input:
            return False
    return True

def is_nonnumber(thechar):
    return is_non_generic(thechar, ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"])

def is_nonspaceortabs(thechar):
    return is_non_generic(thechar, [" ", "\t"])

def revision_filter_function(the_output):

    find_string = "Revision: "
    n = the_output.find(find_string)
    revision_left = the_output[n + len(find_string):]
    revision = ""
    for i in range(len(revision_left)):
        if is_nonnumber(revision_left[i]):
            revision = revision_left[0:i]
            break
    return revision

def status_filter_function(the_line):

    if the_line is None:
        return None
    if len(the_line) == 0:
        return None
    if the_line[0] != "?":
        return None
    the_line = the_line[1:]

    for i in range(len(the_line)):
        if is_nonspaceortabs(the_line[i]):
            return the_line[i:]

def detect_separator(the_string):

    if the_string is None:
        return None
    if len(the_string) == 0:
        return None

    rep_char = the_string[0]
    rep_line = ""
    for i in range(len(the_string)):
        if is_non_generic(the_string[i], [rep_char]):
            rep_line = the_string[0:i]
            return rep_line

def rev_single_entry_filter(log_entry):

    if log_entry is None:
        return None
    if len(log_entry) == 0:
        return None

    na = log_entry.find("r")
    if na == -1:
        return None
    nb = log_entry.find(" ", na)
    the_rev = log_entry[na:nb]
    return the_rev

def rev_entries_filter(log_entries_list):

    rev_list = []

    for le in log_entries_list:
        rle = rev_single_entry_filter(le)
        if rle is not None:
            rev_list.append(rle)

    return rev_list

def collect_svn_patch_cmd_generic(repo, storage_path, output_filename, log_title, cmd, filter_function=None):

    fullbasepath = path_utils.concat_path(storage_path, path_utils.basename_filtered(repo))
    output_filename_full = path_utils.concat_path(fullbasepath, output_filename)

    try:
        path_utils.guaranteefolder(fullbasepath)
    except path_utils.PathUtilsException as puex:
        return False, "Can't collect patch for %s: Failed guaranteeing folder [%s]" % (log_title, fullbasepath)

    if os.path.exists(output_filename_full):
        return False, "Can't collect patch for %s: %s already exists" % (log_title, output_filename_full)

    v, r = generic_run.run_cmd_l(cmd, use_cwd=repo)
    if not v:
        return False, "Failed calling svn command"
    if filter_function is not None:
        final_output = filter_function(r)
    else:
        final_output = r

    with open(output_filename_full, "w") as f:
        f.write(final_output)

    return True, ""

def collect_svn_patch_head(repo, storage_path):
    return collect_svn_patch_cmd_generic(repo, storage_path, "head.patch", "head", ["svn", "diff", "--internal-diff"], None)

def collect_svn_patch_head_id(repo, storage_path):
    return collect_svn_patch_cmd_generic(repo, storage_path, "head_id.txt", "head-id", ["svn", "info"], revision_filter_function)

def collect_svn_patch_head_unversioned(repo, storage_path):

    v, r = generic_run.run_cmd_l(["svn", "status"], use_cwd=repo)
    if not v:
        return False, "Failed calling svn command"

    unversioned_files = [x for x in r.split(os.linesep) if x != ""]
    for uf in unversioned_files:
        file_filtered = status_filter_function(uf)
        if file_filtered is None:
            continue
        target_file = path_utils.concat_path(storage_path, path_utils.basename_filtered(repo), "head_unversioned", file_filtered)
        source_file = path_utils.concat_path(repo, file_filtered)
        try:
            path_utils.guaranteefolder( os.path.dirname(target_file) )
        except path_utils.PathUtilsException as puex:
            return False, "Can't collect patch for head-unversioned: Failed guaranteeing folder [%s]" % os.path.dirname(target_file)
        if os.path.exists(target_file):
            return False, "Can't collect patch for head-unversioned: %s already exists" % target_file
        if not path_utils.copy_to( source_file, target_file ):
            return False, "Can't collect patch for head-unversioned: Cant copy %s to %s" % (source_file, target_file)

    return True, ""

def collect_svn_patch_previous(repo, storage_path, previous_number):

    if not previous_number > 0:
        return False, "Can't collect patch for previous: nothing to format"

    v, r = generic_run.run_cmd_l(["svn", "log", "--limit", str(previous)], use_cwd=repo)
    if not v:
        return False, "Failed calling svn command"
    log_out = r

    sep_line = detect_separator(log_out)
    log_entries_pre = log_out.split(sep_line)
    log_entries = []
    for le in log_entries_pre:
        if le != "":
            log_entries.append(le)

    prev_list = rev_entries_filter(log_entries)

    if previous_number > len(prev_list):
        return False, "Can't collect patch for previous: requested %d commits, but there are only %d in total" % (previous_number, len(prev_list))

    for i in range(previous_number):
        v, r = generic_run.run_cmd_l(["svn", "diff", "-c", prev_list[i]], use_cwd=repo)
        if not v:
            return False, "Failed calling svn command"

        previous_file_content = r
        previous_file_name = path_utils.concat_path(storage_path, path_utils.basename_filtered(repo), "previous_%d_%s.patch" % ((i+1), prev_list[i]))

        try:
            path_utils.guaranteefolder( os.path.dirname(previous_file_name) )
        except path_utils.PathUtilsException as puex:
            return False, "Can't collect patch for previous: Failed guaranteeing folder [%s]" % os.path.dirname(previous_file_name)

        if os.path.exists(previous_file_name):
            return False, "Can't collect patch for previous: %s already exists" % previous_file_name
        with open(previous_file_name, "w") as f:
            f.write(previous_file_content)

    return True, ""

def collect_svn_patch(repo, storage_path, head, head_id, head_unversioned, previous):

    repo = path_utils.filter_remove_trailing_sep(repo)
    storage_path = path_utils.filter_remove_trailing_sep(storage_path)

    if not os.path.exists(repo):
        return False, "Repository %s does not exist" % repo

    if not os.path.exists(storage_path):
        return False, "Storage path %s does not exist" % storage_path

    # head
    if head:
        v, r = collect_svn_patch_head(repo, storage_path)
        if not v:
            return v, r

    # head-id
    if head_id:
        v, r = collect_svn_patch_head_id(repo, storage_path)
        if not v:
            return v, r

    # head_unversioned
    if head_unversioned:
        v, r = collect_svn_patch_head_unversioned(repo, storage_path)
        if not v:
            return v, r

    # previous
    if previous > 0:
        v, r = collect_svn_patch_previous(repo, storage_path, previous)
        if not v:
            return v, r

    return True, "Done"

def puaq():
    print("Usage: %s repo [--storage-path the_storage_path] [--head] [--head-id] [--head-unversioned] [--previous X]" % os.path.basename(__file__))
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
    head_unversioned = False
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
        elif p == "--head-unversioned":
            head_unversioned = True
        elif p == "--previous":
            previous_parse_next = True

    if storage_path is None:
        storage_path = os.getcwd()

    v, r = collect_svn_patch(repo, storage_path, head, head_id, head_unversioned, previous)
    print(r)

    if not v:
        sys.exit(1)
