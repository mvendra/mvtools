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

def collect_patches(path, custom_path_navigator, storage_path, default_filter, include_list, exclude_list, head, head_id, head_staged, head_unversioned, stash, previous, repotype):

    if repotype != "svn" and repotype != "git" and repotype != "all":
        return False, ["Invalid repository type: %s" % repotype]

    if not os.path.exists(storage_path):
        return False, ["Storage path [%s] does not exist."  % storage_path]

    items = []
    if custom_path_navigator is None:
        # automatic path traversal
        items = fsquery.makecontentlist(path, True, False, True, False, True, True, None)
    else:
        items = custom_path_navigator(path)

    items = fsquery_adv_filter.filter_path_list_and(items, [ (fsquery_adv_filter.filter_is_repo, "not-used") ] ) # do the pre-filtering (for repos only)

    # setup filtering
    filters = []
    if default_filter == "include":
        filters.append( (fsquery_adv_filter.filter_all_positive, "not-used") )
        for ei in exclude_list:
            filters.append( (fsquery_adv_filter.filter_has_not_middle_pieces, path_utils.splitpath(ei)) )
        items_filtered = fsquery_adv_filter.filter_path_list_and(items, filters)

    elif default_filter == "exclude":
        filters.append( (fsquery_adv_filter.filter_all_negative, "not-used") )
        for ii in include_list:
            filters.append( (fsquery_adv_filter.filter_has_middle_pieces, path_utils.splitpath(ii)) )
        items_filtered = fsquery_adv_filter.filter_path_list_or(items, filters)

    report = []
    for it in items_filtered:

        v, r = detect_repo_type.detect_repo_type(it)
        if not v:
            continue
        repotype_detected = r
        if "git" in repotype_detected and "bare" in repotype_detected: # cant collect patches for git bare repos
            continue

        if "git" in repotype_detected and (repotype == "git" or repotype == "all"):
            print("Collecting git patches: [%s]" % it)
            v, r = collect_git_patch.collect_git_patch(it, storage_path, head, head_id, head_staged, head_unversioned, stash, previous)
            if not v:
                report.append("Failed collecting git patches: %s" % r)

        elif "svn" in repotype_detected and (repotype == "svn" or repotype == "all"):
            print("Collecting svn patches: [%s]" % it)
            v, r = collect_svn_patch.collect_svn_patch(it, storage_path, head, head_id, head_unversioned, previous)
            if not v:
                report.append("Failed collecting svn patches: %s" % r)

    return (len(report)==0), report

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
    print("Usage: %s path [--custom-path-navigator the_custom_path_navigator] [--storage-path the_storage_path] [--default-filter-include | --default-filter-exclude] [--include repo_basename] [--exclude repo_basename] [--head] [--head-id] [--head-staged] [--head-unversioned] [--stash] [--previous X] [--repo-type git|svn|all]" % os.path.basename(__file__))
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
    head = False
    head_id = False
    head_staged = False
    head_unversioned = False
    stash = False
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

        if p == "--custom-path-navigator":
            custom_path_navigator_parse_next = True
        elif p == "--default-filter-include":
            default_filter = "include"
        elif p == "--default-filter-exclude":
            default_filter = "exclude"
        elif p == "--storage-path":
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
        elif p == "--repo-type":
            repotype_parse_next = True
        elif p == "--include":
            include_parse_next = True
        elif p == "--exclude":
            exclude_parse_next = True

    if storage_path is None:
        storage_path = os.getcwd()

    if custom_path_navigator is not None and not os.path.exists(custom_path_navigator):
        # custom path navigator has been specified, but does not exists. fail.
        print("Custom path navigator [%s] does not exist. Aborting." % custom_path_navigator)
        sys.exit(1)

    v, r = collect_patches(path, resolve_py_into_custom_pathnav_func(custom_path_navigator), storage_path, default_filter, include_list, exclude_list, head, head_id, head_staged, head_unversioned, stash, previous, repotype)

    if not v:
        for i in r:
            print("Failed: %s" % i)
        sys.exit(1)
    else:
        print("All passed")
        sys.exit(0)
