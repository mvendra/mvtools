#!/usr/bin/env python3

import sys
import os

import path_utils
import fsquery
import fsquery_adv_filter
import detect_repo_type
import collect_git_patch
import collect_svn_patch

import importlib.util

def resolve_py_into_custom_pathnav_func(path_to_py_script):

    # see "MVTOOLS/collect_patches_cnav_sample.py" for an example
    # on how to implement a custom path navigator script.

    if path_to_py_script is None or not os.path.exists(path_to_py_script):
        return None

    spec = importlib.util.spec_from_file_location("", path_to_py_script)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    test_bind = None
    try:
        test_bind = mod.visit_path
    except:
        return None
    return test_bind

def collect_patch(path, storage_path, default_subfilter, subfilter_include_list, subfilter_exclude_list, head, head_id, staged, unversioned, stash, previous, repotype):

    if repotype != "svn" and repotype != "git" and repotype != "all":
        return False, ["Invalid repository type: %s" % repotype]

    if not os.path.exists(storage_path):
        return False, ["Storage path [%s] does not exist."  % storage_path]

    v, r = detect_repo_type.detect_repo_type(path)
    if not v:
        return False, "Failed collecting patches: [%s]" % r
    repotype_detected = r
    if "git" in repotype_detected and "bare" in repotype_detected: # cant collect patches for git bare repos
        return False, "Can't collect patches from git-bare repos."

    if "git" in repotype_detected and (repotype == "git" or repotype == "all"):
        v, r = collect_git_patch.collect_git_patch(path, storage_path, default_subfilter, subfilter_include_list, subfilter_exclude_list, head, head_id, staged, unversioned, stash, previous)
        if not v:
            return False, "Failed collecting git patches: %s" % r

    elif "svn" in repotype_detected and (repotype == "svn" or repotype == "all"):
        v, r = collect_svn_patch.collect_svn_patch(path, storage_path, default_subfilter, subfilter_include_list, subfilter_exclude_list, head, head_id, unversioned, previous)
        if not v:
            return False, "Failed collecting svn patches: %s" % r

    return True, None

def collect_patches_recursive(path, custom_path_navigator, storage_path, default_filter, include_list, exclude_list, default_subfilter, subfilter_include_list, subfilter_exclude_list, head, head_id, staged, unversioned, stash, previous, repotype):

    custom_path_navigator_local_copy = custom_path_navigator
    if custom_path_navigator is not None:
        custom_path_navigator = resolve_py_into_custom_pathnav_func(custom_path_navigator)
        if custom_path_navigator is None: # custom path navigator has been specified, but could not be resolved. fail.
            return False, ["Custom path navigator [%s] could not be loaded. Aborting." % custom_path_navigator_local_copy]

    items = []
    if custom_path_navigator is None:
        # automatic path traversal
        items = fsquery.makecontentlist(path, True, False, False, True, False, True, True, None)
    else:
        items = custom_path_navigator(path)

    items = fsquery_adv_filter.filter_path_list_and(items, [ (fsquery_adv_filter.filter_is_repo, "not-used") ] ) # do the pre-filtering (for repos only)

    # setup filtering
    filters = []
    if default_filter == "include":
        filters.append( (fsquery_adv_filter.filter_all_positive, "not-used") )
        for ei in exclude_list:
            filters.append( (fsquery_adv_filter.filter_has_not_middle_pieces, path_utils.splitpath(ei, "auto")) )
        items_filtered = fsquery_adv_filter.filter_path_list_and(items, filters)

    elif default_filter == "exclude":
        filters.append( (fsquery_adv_filter.filter_all_negative, "not-used") )
        for ii in include_list:
            filters.append( (fsquery_adv_filter.filter_has_middle_pieces, path_utils.splitpath(ii, "auto")) )
        items_filtered = fsquery_adv_filter.filter_path_list_or(items, filters)
    else:
        return False, ["Invalid default filter: [%s]" % default_filter]

    report = []
    for it in items_filtered:
        print("Collecting patches on repo: [%s]" % it)
        v, r = collect_patch(it, storage_path, default_subfilter, subfilter_include_list, subfilter_exclude_list, head, head_id, staged, unversioned, stash, previous, repotype)
        if not v:
            report.append("Failed collecting patches for repo: [%s]: %s" % (it, r))

    return (len(report)==0), report

def collect_patches(path, custom_path_navigator, storage_path, default_filter, include_list, exclude_list, default_subfilter, subfilter_include_list, subfilter_exclude_list, head, head_id, staged, unversioned, stash, previous, repotype):

    v, r = detect_repo_type.detect_repo_type(path)
    if not (v and (r == detect_repo_type.REPO_TYPE_GIT_STD or r == detect_repo_type.REPO_TYPE_SVN)):
        return collect_patches_recursive(path, custom_path_navigator, storage_path, default_filter, include_list, exclude_list, default_subfilter, subfilter_include_list, subfilter_exclude_list, head, head_id, staged, unversioned, stash, previous, repotype)

    v, r = collect_patch(path, storage_path, default_subfilter, subfilter_include_list, subfilter_exclude_list, head, head_id, staged, unversioned, stash, previous, repotype)
    return v, [r]

"""
a warning about the filter selectors (--include and --exclude)
they accept wildcards ("*", or asterisks) for specifying path matches
this is a word of caution when using them. wilcards in these operations
DO NOT work exactly the same as you'd expect from, say, the usual implementation
of regular expressions in programming languages (PCRE for example).
wildcards here mean "current token/path piece may be skipped until a match can be found
with the next defined token". see fsquery_adv_filter_test for many examples.
and a few handy examples below:

--include "*/folder/*" -> will match paths that have "folder" in the middle, or if the
path is simply "/folder".

--include "folder/*" -> will match paths that BEGIN with "folder" and then followed by whatever else (or nothing)

--include "*/folder" -> will match paths that END with "folder" and are preceded by whatever else (or nothing)

--include "*/folder/*/folder" -> the path "/rubbish/folder/more_rubbish/folder" will
match, whereas "/rubbish/folder/more_rubbish/folder/yetmorestuff" will NOT

for short, the matching algorithm is a greedy, left-to-right only matcher that you ought to
be cautious about when using, to avoid mismatches and misuse.
"""

def puaq():
    print("Usage: %s path [--custom-path-navigator the_custom_path_navigator] [--storage-path the_storage_path] [--default-filter-include | --default-filter-exclude] [--include repo_basename] [--exclude repo_basename] [--default-subfilter-include | --default-subfilter-exclude] [--subfilter-include repo_basename] [--subfilter-exclude repo_basename] [--head] [--head-id] [--staged] [--unversioned] [--stash X (use \"-1\" to collect the entire stash)] [--previous X] [--repo-type git|svn|all]" % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    path = sys.argv[1]
    storage_path = None
    params = sys.argv[2:]

    # parse options
    custom_path_navigator_parse_next = False
    custom_path_navigator = None
    storage_path_parse_next = False
    default_filter = "include"
    include_list = []
    exclude_list = []
    include_parse_next = False
    exclude_parse_next = False
    default_subfilter = "include"
    subfilter_include_list = []
    subfilter_exclude_list = []
    subfilter_include_parse_next = False
    subfilter_exclude_parse_next = False
    head = False
    head_id = False
    staged = False
    unversioned = False
    stash = 0
    stash_parse_next = False
    previous = 0
    previous_parse_next = False
    repotype = "all"
    repotype_parse_next = False

    for p in params:

        if custom_path_navigator_parse_next:
            custom_path_navigator = p
            custom_path_navigator_parse_next = False
            continue

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

        if repotype_parse_next:
            repotype = p
            repotype_parse_next = False
            continue

        if include_parse_next:
            include_list.append(p)
            include_parse_next = False
            continue

        if exclude_parse_next:
            exclude_list.append(p)
            exclude_parse_next = False
            continue

        if subfilter_include_parse_next:
            subfilter_include_list.append(p)
            subfilter_include_parse_next = False
            continue

        if subfilter_exclude_parse_next:
            subfilter_exclude_list.append(p)
            subfilter_exclude_parse_next = False
            continue

        if p == "--custom-path-navigator":
            custom_path_navigator_parse_next = True
        elif p == "--storage-path":
            storage_path_parse_next = True
        elif p == "--default-filter-include":
            default_filter = "include"
        elif p == "--default-filter-exclude":
            default_filter = "exclude"
        elif p == "--include":
            include_parse_next = True
        elif p == "--exclude":
            exclude_parse_next = True
        elif p == "--default-subfilter-include":
            default_subfilter = "include"
        elif p == "--default-subfilter-exclude":
            default_subfilter = "exclude"
        elif p == "--subfilter-include":
            subfilter_include_parse_next = True
        elif p == "--subfilter-exclude":
            subfilter_exclude_parse_next = True
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
        elif p == "--repo-type":
            repotype_parse_next = True

    if storage_path is None:
        storage_path = os.getcwd()

    v, r = collect_patches(path, custom_path_navigator, storage_path, default_filter, include_list, exclude_list, default_subfilter, subfilter_include_list, subfilter_exclude_list, head, head_id, staged, unversioned, stash, previous, repotype)
    if not v:
        for i in r:
            print("Failed: %s" % i)
        sys.exit(1)
    else:
        print("All passed")
        sys.exit(0)
