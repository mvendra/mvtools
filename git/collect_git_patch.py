#!/usr/bin/env python3

import sys
import os

import git_lib
import path_utils
import fsquery_adv_filter

ERRMSG_EMPTY = "Empty contents"

def _known_states():

    st = ["??", "R ", "D ", "A ", "M ", " M", " D", "UU", "MM", "AM", "DD", "UA", "UD", "DU", "AA", "AU", "RM"]

    return st

def _test_repo_status(repo_path):

    # mvtodo: supporting exotic statuses (such as merge conflicts and etc) bears complexity that does not justify the gains. the git backend
    # also has segfault issues when trying to diff / deal with some of these states. it's best to avoid automating the handling of these
    # status with policy / workflow awareness instead.

    forbidden_items = []
    unexpected_items = []
    funcs = [git_lib.get_head_deleted_deleted_files, git_lib.get_head_updated_added_files, git_lib.get_head_updated_deleted_files, git_lib.get_head_deleted_updated_files, git_lib.get_head_added_added_files, git_lib.get_head_added_updated_files, git_lib.get_head_renamed_modified_files]

    for f in funcs:
        v, r = f(repo_path)
        if not v:
            return False, "Unable to probe for illegal statuses on repo [%s]: [%s]" % (repo_path, r)
        forbidden_items += r

    if len(forbidden_items) > 0:
        return False, "The repo [%s] has invalid statuses" % repo_path

    v, r = git_lib.repo_has_any_not_of_states(repo_path, _known_states())
    if not v:
        return False, "Unable to probe known states on repo: [%s]" % repo_path
    unexpected_items = r

    if len(unexpected_items) > 0:
        opened_list_as_string = ""
        for x in unexpected_items:
            opened_list_as_string += "[%s] - " % x
        if opened_list_as_string != "":
            opened_list_as_string = opened_list_as_string[:len(opened_list_as_string)-3]
        return False, "Repo [%s] has unknown states: %s" % (repo_path, opened_list_as_string)

    return True, None

def _make_list_tuplelistadapter(list_of_tuples):

    assembled_list = []

    for it in list_of_tuples:
        first, second = it
        assembled_list.append(first)
        assembled_list.append(second)

    return assembled_list

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

def _assemble_list_from_functions(repo, func_list):

    total_items = []
    for f in func_list:
        v, r = f(repo)
        if not v:
            return False, "Failed retrieving listing: [%s]" % r
        total_items += r

    return True, total_items

def collect_git_patch_cmd_generic(repo, storage_path, output_filename, log_title, content):

    if len(content) == 0:
        return False, ERRMSG_EMPTY

    fullbasepath = path_utils.concat_path(storage_path, repo)
    output_filename_full = path_utils.concat_path(fullbasepath, output_filename)

    if not path_utils.guaranteefolder(fullbasepath):
        return False, "Can't collect patch for [%s]: Failed guaranteeing folder [%s]." % (log_title, fullbasepath)

    if os.path.exists(output_filename_full):
        return False, "Can't collect patch for [%s]: [%s] already exists." % (log_title, output_filename_full)

    with open(output_filename_full, "w") as f:
        f.write(content)

    return True, output_filename_full

def collect_git_patch_head(repo, storage_path, default_filter, include_list, exclude_list):

    head_items_final = []

    head_items = []
    funcs = [git_lib.get_head_modified_files, git_lib.get_head_deleted_files, git_lib.get_head_updated_files, git_lib.get_head_modified_modified_files, git_lib.get_head_added_modified_files]
    v, r = _assemble_list_from_functions(repo, funcs)
    if not v:
        return False, "Unable to assemble list of head items on repo [%s]: [%s]" % (repo, r)
    head_items = r

    head_items_filtered = _apply_filters(head_items.copy(), default_filter, include_list, exclude_list)
    if head_items_filtered is None:
        return False, "Unable to apply filters (head operation). Target repo: [%s]" % repo
    head_items_final += head_items_filtered.copy()

    head_patch_contents = ""
    if len(head_items_final) > 0:
        v, r = git_lib.diff_indexed(repo, head_items_final)
        if not v:
            return False, "Failed calling git command for head: [%s]. Repository: [%s]." % (r, repo)
        head_patch_contents = r

    return collect_git_patch_cmd_generic(repo, storage_path, "head.patch", "head", head_patch_contents)

def collect_git_patch_head_id(repo, storage_path):
    v, r = git_lib.rev_parse_head(repo)
    if not v:
        return False, "Failed calling git command for head-id: [%s]. Repository: [%s]." % (r, repo)
    return collect_git_patch_cmd_generic(repo, storage_path, "head_id.txt", "head-id", r)

def collect_git_patch_staged(repo, storage_path, default_filter, include_list, exclude_list):

    final_file_list = []

    # get staged-modified files
    v, r = git_lib.get_staged_modified_files(repo)
    if not v:
        return False, "Unable to retrieve staged-modified files on repo [%s]: [%s]" % (repo, r)
    staged_modified_files = r

    # filter staged-modified files
    staged_modified_files_filtered = _apply_filters(staged_modified_files.copy(), default_filter, include_list, exclude_list)
    if staged_modified_files_filtered is None:
        return False, "Unable to apply filters (staged-modified operation). Target repo: [%s]" % repo
    final_file_list += staged_modified_files_filtered.copy()

    # get staged-added files
    v, r = git_lib.get_staged_added_files(repo)
    if not v:
        return False, "Unable to retrieve staged-added files on repo [%s]: [%s]" % (repo, r)
    staged_added_files = r

    # filter staged-added files
    staged_added_files_filtered = _apply_filters(staged_added_files.copy(), default_filter, include_list, exclude_list)
    if staged_added_files_filtered is None:
        return False, "Unable to apply filters (staged-added operation). Target repo: [%s]" % repo
    final_file_list += staged_added_files_filtered.copy()

    # get staged-deleted files
    v, r = git_lib.get_staged_deleted_files(repo)
    if not v:
        return False, "Unable to retrieve staged-deleted files on repo [%s]: [%s]" % (repo, r)
    staged_deleted_files = r

    # filter staged-deleted files
    staged_deleted_files_filtered = _apply_filters(staged_deleted_files.copy(), default_filter, include_list, exclude_list)
    if staged_deleted_files_filtered is None:
        return False, "Unable to apply filters (staged-deleted operation). Target repo: [%s]" % repo
    final_file_list += staged_deleted_files_filtered.copy()

    # get staged-renamed files
    v, r = git_lib.get_staged_renamed_files(repo)
    if not v:
        return False, "Unable to retrieve staged-renamed files on repo [%s]: [%s]" % (repo, r)
    staged_renamed_files = r

    # filter staged-renamed files
    staged_renamed_files_filtered = _apply_filters_tuplelistadapter(staged_renamed_files.copy(), default_filter, include_list, exclude_list)
    if staged_renamed_files_filtered is None:
        return False, "Unable to apply filters (staged-renamed operation). Target repo: [%s]" % repo
    final_file_list += _make_list_tuplelistadapter(staged_renamed_files_filtered.copy())

    staged_patch_contents = ""
    if len(final_file_list) > 0:
        v, r = git_lib.diff_cached_indexed(repo, final_file_list)
        if not v:
            return False, "Failed calling git command for staged: [%s]. Repository: [%s]." % (r, repo)
        staged_patch_contents = r

    return collect_git_patch_cmd_generic(repo, storage_path, "staged.patch", "staged", staged_patch_contents)

def collect_git_patch_unversioned(repo, storage_path, default_filter, include_list, exclude_list):

    written_file_list = []

    v, r = git_lib.get_unversioned_files(repo)
    if not v:
        return False, "Failed calling git command for unversioned: [%s]. Repository: [%s]." % (r, repo)
    unversioned_files = r

    # filter unversioned files
    unversioned_files_filtered = _apply_filters(unversioned_files.copy(), default_filter, include_list, exclude_list)
    if unversioned_files_filtered is None:
        return False, "Unable to apply filters (unversioned operation). Target repo: [%s]" % repo
    unversioned_files_final = unversioned_files_filtered.copy()

    target_base = path_utils.concat_path(storage_path, repo, "unversioned")
    if os.path.exists(target_base):
        return False, "Can't collect patch for unversioned: [%s] already exists." % target_base

    if not path_utils.guaranteefolder(target_base):
        return False, "Can't collect patch for unversioned: Failed guaranteeing folder: [%s]." % target_base

    for uf in unversioned_files_final:

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

def collect_git_patch_stash(repo, storage_path, stash):

    if stash is None:
        return False, "Stash is unspecified"

    v, r = git_lib.get_stash_list(repo)
    if not v:
        return False, "Failed calling git command for stash: [%s]. Repository: [%s]." % (r, repo)
    stash_list = r
    written_file_list = []

    if len(stash_list) == 0:
        return False, "Can't collect patch for stash: stash is empty. Repository: [%s]" % repo

    c = 0
    for si in stash_list:
        c += 1

        if stash != -1:
            if c > stash:
                break

        v, r = git_lib.stash_show_diff(repo, si)
        if not v:
            return False, "Failed calling git command for stash: [%s]. Repository: [%s]. Stash name: [%s]." % (r, repo, si)

        stash_current_contents = r
        stash_current_file_name = path_utils.concat_path(storage_path, repo, "%s.patch" % si)

        if not path_utils.guaranteefolder( path_utils.dirname_filtered(stash_current_file_name) ):
            return False, "Can't collect patch for stash: Failed guaranteeing folder [%s]." % path_utils.dirname_filtered(stash_current_file_name)

        if os.path.exists(stash_current_file_name):
            return False, "Can't collect patch for stash: [%s] already exists." % stash_current_file_name
        with open(stash_current_file_name, "w") as f:
            f.write(stash_current_contents)
        written_file_list.append(stash_current_file_name)

    return True, written_file_list

def collect_git_patch_previous(repo, storage_path, previous_number):

    if not previous_number > 0:
        return False, "Can't collect patch for previous: nothing to format."

    v, r = git_lib.get_previous_hash_list(repo, previous_number)
    if not v:
        return False, "Failed calling git command for previous: [%s]. Repository: [%s]." % (r, repo)
    prev_list = r
    written_file_list = []

    if previous_number > len(prev_list):
        return False, "Can't collect patch for previous: requested [%d] commits, but there are only [%d] in total." % (previous_number, len(prev_list))

    for i in range(previous_number):
        v, r = git_lib.show(repo, prev_list[i])
        if not v:
            return False, "Failed calling git command for previous: [%s]. Repository: [%s]. Commit id: [%s]." % (r, repo, prev_list[i])

        previous_file_content = r
        previous_file_name = path_utils.concat_path(storage_path, repo, "previous_%d_%s.patch" % ((i+1), prev_list[i]))

        if not path_utils.guaranteefolder( path_utils.dirname_filtered(previous_file_name) ):
            return False, "Can't collect patch for previous: Failed guaranteeing folder [%s]." % path_utils.dirname_filtered(previous_file_name)

        if os.path.exists(previous_file_name):
            return False, "Can't collect patch for previous: [%s] already exists." % previous_file_name
        with open(previous_file_name, "w") as f:
            f.write(previous_file_content)
        written_file_list.append(previous_file_name)

    return True, written_file_list

def collect_git_patch_cherry_pick_previous(repo, storage_path, cherry_pick_previous):

    v, r = git_lib.show(repo, cherry_pick_previous)
    if not v:
        return False, "Failed calling git command for cherry-pick-previous: [%s]. Repository: [%s]." % (r, repo)
    previous_cherry_picked_contents = r

    return collect_git_patch_cmd_generic(repo, storage_path, "cherry_picked_previous_%s.patch" % cherry_pick_previous, "cherry-picked-previous", previous_cherry_picked_contents)

def collect_git_patch(repo, storage_path, default_filter, include_list, exclude_list, head, head_id, staged, unversioned, stash, previous, cherry_pick_previous):

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
        v, r = collect_git_patch_head(repo, storage_path, default_filter, include_list, exclude_list)
        if not v:
            has_any_failed = True
            report.append("collect_git_patch_head: [%s]." % r)
        else:
            report.append(r)

    # head-id
    if head_id:
        v, r = collect_git_patch_head_id(repo, storage_path)
        if not v:
            has_any_failed = True
            report.append("collect_git_patch_head_id: [%s]." % r)
        else:
            report.append(r)

    # staged
    if staged:
        v, r = collect_git_patch_staged(repo, storage_path, default_filter, include_list, exclude_list)
        if not v:
            has_any_failed = True
            report.append("collect_git_patch_staged: [%s]." % r)
        else:
            report.append(r)

    # unversioned
    if unversioned:
        v, r = collect_git_patch_unversioned(repo, storage_path, default_filter, include_list, exclude_list)
        if not v:
            has_any_failed = True
            report.append("collect_git_patch_unversioned: [%s]." % r)
        else:
            report += r

    # stash
    if stash != 0:
        v, r = collect_git_patch_stash(repo, storage_path, stash)
        if not v:
            has_any_failed = True
            report.append("collect_git_patch_stash: [%s]." % r)
        else:
            report += r

    # previous
    if previous > 0:
        v, r = collect_git_patch_previous(repo, storage_path, previous)
        if not v:
            has_any_failed = True
            report.append("collect_git_patch_previous: [%s]." % r)
        else:
            report += r

    # cherry pick previous
    if cherry_pick_previous is not None:
        v, r = collect_git_patch_cherry_pick_previous(repo, storage_path, cherry_pick_previous)
        if not v:
            has_any_failed = True
            report.append("collect_git_patch_cherry_pick_previous: [%s]." % r)
        else:
            report.append(r)

    return (not has_any_failed), report

def puaq():
    print("Usage: %s repo [--storage-path the_storage_path] [--default-filter-include | --default-filter-exclude] [--include repo_basename] [--exclude repo_basename] [--head] [--head-id] [--staged] [--unversioned] [--stash X (use \"-1\" to collect the entire stash)] [--previous X] [--cherry-pick-previous HASH]" % path_utils.basename_filtered(__file__))
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
    staged = False
    unversioned = False
    stash = 0
    stash_parse_next = False
    previous = 0
    previous_parse_next = False
    cherry_pick_previous = None
    cherry_pick_previous_parse_next = False

    for p in params:

        if storage_path_parse_next:
            storage_path = p
            storage_path_parse_next = False
            continue

        if stash_parse_next:
            stash = int(p)
            stash_parse_next = False
            continue

        if previous_parse_next:
            previous = int(p)
            previous_parse_next = False
            continue

        if cherry_pick_previous_parse_next:
            cherry_pick_previous = p
            cherry_pick_previous_parse_next = False
            continue

        if include_parse_next:
            include_list.append(p)
            include_parse_next = False
            continue

        if exclude_parse_next:
            exclude_list.append(p)
            exclude_parse_next = False
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
        elif p == "--staged":
            staged = True
        elif p == "--unversioned":
            unversioned = True
        elif p == "--stash":
            stash_parse_next = True
        elif p == "--previous":
            previous_parse_next = True
        elif p == "--cherry-pick-previous":
            cherry_pick_previous_parse_next = True

    if storage_path is None:
        storage_path = os.getcwd()

    v, r = collect_git_patch(repo, storage_path, default_filter, include_list, exclude_list, head, head_id, staged, unversioned, stash, previous, cherry_pick_previous)
    for i in r:
        print(i)
    if not v:
        print("Not everything succeeded.")
        sys.exit(1)
    print("All succeeded.")
