#!/usr/bin/env python3

import sys
import os

import fsquery_adv_filter
import path_utils
import svn_lib

ERRMSG_EMPTY = "Empty contents"

def _known_states():

    st = ["C", "M", "!", "R", "D", "A", "?", "X"]

    return st

def _test_repo_status(repo_path):

    v, r = svn_lib.repo_has_any_not_of_states(repo_path, _known_states())
    if not v:
        return False, "Unable to probe known states on repo: [%s]" % repo_path
    if len(r) > 0:
        opened_list_as_string = ""
        for x in r:
            opened_list_as_string += "[%s] - " % x
        if opened_list_as_string != "":
            opened_list_as_string = opened_list_as_string[:len(opened_list_as_string)-3]
        return False, "Repo [%s] has unknown states: %s" % (repo_path, opened_list_as_string)

    return True, None

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

def collect_svn_patch_head(repo, storage_path, default_filter, include_list, exclude_list):

    final_diff_files = []

    # get head-modified files
    v, r = svn_lib.get_head_modified_files(repo)
    if not v:
        return False, "Unable to retrieve list of head-modified files on repo [%s]: [%s]" % (repo, r)
    mod_files = r

    # filter head-modified files
    mod_files_filtered = _apply_filters(mod_files.copy(), default_filter, include_list, exclude_list)
    if mod_files_filtered is None:
        return False, "Unable to apply filters (head-modified operation). Target repo: [%s]" % target_repo
    mod_files_final = mod_files_filtered.copy()

    # get head-added files
    v, r = svn_lib.get_head_added_files(repo)
    if not v:
        return False, "Unable to retrieve list of head-added files on repo [%s]: [%s]" % (repo, r)
    add_files = r

    # filter head-added files
    add_files_filtered = _apply_filters(add_files.copy(), default_filter, include_list, exclude_list)
    if add_files_filtered is None:
        return False, "Unable to apply filters (head-added operation). Target repo: [%s]" % target_repo
    add_files_final = add_files_filtered.copy()

    # get head-deleted files
    v, r = svn_lib.get_head_deleted_files(repo)
    if not v:
        return False, "Unable to retrieve list of head-deleted files on repo [%s]: [%s]" % (repo, r)
    rem_files = r

    # filter head-deleted files
    rem_files_filtered = _apply_filters(rem_files.copy(), default_filter, include_list, exclude_list)
    if rem_files_filtered is None:
        return False, "Unable to apply filters (head-deleted operation). Target repo: [%s]" % target_repo
    rem_files_final = rem_files_filtered.copy()

    # get head-replaced files
    v, r = svn_lib.get_head_replaced_files(repo)
    if not v:
        return False, "Unable to retrieve list of head-replaced files on repo [%s]: [%s]" % (repo, r)
    rep_files = r

    # filter head-replaced files
    rep_files_filtered = _apply_filters(rep_files.copy(), default_filter, include_list, exclude_list)
    if rep_files_filtered is None:
        return False, "Unable to apply filters (head-replaced operation). Target repo: [%s]" % target_repo
    rep_files_final = rep_files_filtered.copy()

    # get head-conflicted files
    v, r = svn_lib.get_head_conflicted_files(repo)
    if not v:
        return False, "Unable to retrieve list of head-conflicted files on repo [%s]: [%s]" % (repo, r)
    con_files = r

    # filter head-conflicted files
    con_files_filtered = _apply_filters(con_files.copy(), default_filter, include_list, exclude_list)
    if con_files_filtered is None:
        return False, "Unable to apply filters (head-conflicted operation). Target repo: [%s]" % target_repo
    con_files_final = con_files_filtered.copy()

    final_diff_files += mod_files_final
    final_diff_files += add_files_final
    final_diff_files += rem_files_final
    final_diff_files += rep_files_final
    final_diff_files += con_files_final

    v, r = svn_lib.diff(repo, final_diff_files)
    if not v:
        return False, "Failed calling svn command for head: [%s]. Repository: [%s]." % (r, repo)

    return collect_svn_patch_cmd_generic(repo, storage_path, "head.patch", "head", r)

def collect_svn_patch_head_id(repo, storage_path):
    v, r = svn_lib.get_head_revision(repo)
    if not v:
        return False, "Failed calling svn command for head-id: [%s]. Repository: [%s]." % (r, repo)
    return collect_svn_patch_cmd_generic(repo, storage_path, "head_id.txt", "head-id", r.encode("utf8"))

def collect_svn_patch_unversioned(repo, storage_path, default_filter, include_list, exclude_list):

    # mvtodo: unversioned filtering, on SVN, has a considerable limitation:
    # it's not possible to filter out unversioned files or folders if they themselves are inside
    # an unversioned base tree. for example:
    # the_repo/sub/folder/some/domain/component
    # if "sub" itself is unversioned, then it's not possible to deal with unversioned files
    # that reside (for example) inside "domain", using something like: --default-filter-exclude --include '*/domain/*'
    # this could possibly be solved by manually traversing (eg. with fsquery) each entry in order to assemble
    # a full listing, and then processing that instead - and only then filtering the result of that - but that
    # may come with some extra complications and corner cases.

    written_file_list = []

    # get unversioned files
    v, r = svn_lib.get_list_unversioned(repo)
    if not v:
        return False, "Failed calling svn command for unversioned: [%s]. Repository: [%s]." % (r, repo)
    unversioned_items = r

    # filter unversioned files
    unversioned_items_filtered = _apply_filters(unversioned_items.copy(), default_filter, include_list, exclude_list)
    if unversioned_items_filtered is None:
        return False, "Unable to apply filters (unversioned operation). Target repo: [%s]" % target_repo
    unversioned_items_final = unversioned_items_filtered.copy()

    target_base = path_utils.concat_path(storage_path, repo, "unversioned")
    if os.path.exists(target_base):
        return False, "Can't collect patch for unversioned: [%s] already exists." % target_base

    if not path_utils.guaranteefolder(target_base):
        return False, "Can't collect patch for unversioned: Failed guaranteeing folder: [%s]." % target_base

    for uf in unversioned_items_final:

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

def collect_svn_patch(repo, storage_path, default_filter, include_list, exclude_list, head, head_id, unversioned, previous):

    repo = path_utils.filter_remove_trailing_sep(repo)
    repo = os.path.abspath(repo)
    storage_path = path_utils.filter_remove_trailing_sep(storage_path)
    storage_path = os.path.abspath(storage_path)

    if not os.path.exists(repo):
        return False, ["Repository [%s] does not exist." % repo]

    if not os.path.exists(storage_path):
        return False, ["Storage path [%s] does not exist." % storage_path]

    v, r = _test_repo_status(repo)
    if not v:
        return False, [r]

    report = []
    has_any_failed = False

    # head
    if head:
        v, r = collect_svn_patch_head(repo, storage_path, default_filter, include_list, exclude_list)
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
        v, r = collect_svn_patch_unversioned(repo, storage_path, default_filter, include_list, exclude_list)
        if not v:
            has_any_failed = True
            report.append("collect_svn_patch_unversioned: [%s]." % r)
        else:
            report += r

    # previous
    if previous > 0:
        v, r = collect_svn_patch_previous(repo, storage_path, previous)
        if not v:
            has_any_failed = True
            report.append("collect_svn_patch_previous: [%s]." % r)
        else:
            report += r

    return (not has_any_failed), report

def puaq():
    print("Usage: %s repo [--storage-path the_storage_path] [--default-filter-include | --default-filter-exclude] [--include repo_basename] [--exclude repo_basename] [--head] [--head-id] [--unversioned] [--previous X]" % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    repo = sys.argv[1]
    storage_path = None
    params = sys.argv[2:]

    # parse options
    storage_path_parse_next = False
    default_filter = "include"
    include_list = []
    exclude_list = []
    include_parse_next = False
    exclude_parse_next = False
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

        if include_parse_next:
            include_list.append(p)
            include_parse_next = False
            continue

        if exclude_parse_next:
            exclude_list.append(p)
            exclude_parse_next = False
            continue

        if previous_parse_next:
            previous = int(p)
            previous_parse_next = False
            continue

        if p == "--storage-path":
            storage_path_parse_next = True
        elif p == "--default-filter-include":
            default_filter = "include"
        elif p == "--default-filter-exclude":
            default_filter = "exclude"
        elif p == "--include":
            include_parse_next = True
        elif p == "--exclude":
            exclude_parse_next = True
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

    v, r = collect_svn_patch(repo, storage_path, default_filter, include_list, exclude_list, head, head_id, unversioned, previous)
    for i in r:
        print(i)
    if not v:
        print("Not everything succeeded.")
        sys.exit(1)
    print("All succeeded.")
