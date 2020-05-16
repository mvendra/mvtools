#!/usr/bin/env python3

import sys
import os

import fsquery
import fsquery_adv_filter
import detect_repo_type
import collect_git_patch
import collect_svn_patch

def collect_patches(path, storage_path, default_filter, include_list, exclude_list, head, head_id, head_staged, head_unversioned, stash, previous, repotype):

    if repotype != "svn" and repotype != "git" and repotype != "both":
        return False, ["Invalid repository type: %s" % repotype]

    if not os.path.exists(storage_path):
        return False, ["Storage path [%s] does not exist."  % storage_path]

    items = fsquery.makecontentlist(path, True, False, True, False, True, True, None)

    # setup filtering
    filters = []
    if default_filter == "include":
        filters.append( (fsquery_adv_filter.filter_all_positive, "not-used") )
        for ei in exclude_list:
            filters.append( (fsquery_adv_filter.filter_is_last_not_equal_to, ei) )
        items_filtered = fsquery_adv_filter.filter_path_list_and(items, filters)
    elif default_filter == "exclude":
        filters.append( (fsquery_adv_filter.filter_all_negative, "not-used") )
        for ii in include_list:
            filters.append( (fsquery_adv_filter.filter_is_last_equal_to, ii) )
        items_filtered = fsquery_adv_filter.filter_path_list_or(items, filters)

    report = []

    for it in items_filtered:
        v, r = detect_repo_type.detect_repo_type(it)
        if v:
            repotype_detected = r
            if "git" in repotype_detected and "bare" in repotype_detected:
                continue

            if "git" in repotype_detected and (repotype == "git" or repotype == "both"):
                print("Collecting git patches: [%s]" % it)
                v, r = collect_git_patch.collect_git_patch(it, storage_path, head, head_id, head_staged, head_unversioned, stash, previous)
                if not v:
                    report.append("Failed collecting git patches: %s" % r)
            elif "svn" in repotype_detected and (repotype == "svn" or repotype == "both"):
                print("Collecting svn patches: [%s]" % it)
                v, r = collect_svn_patch.collect_svn_patch(it, storage_path, head, head_id, head_unversioned, previous)
                if not v:
                    report.append("Failed collecting svn patches: %s" % r)

    return (len(report)==0), report

def puaq():
    print("Usage: %s path [--storage-path the_storage_path] [--default-filter-include | --default-filter-exclude] [--include repo_basename] [--exclude repo_basename] [--head] [--head-id] [--head-staged] [--head-unversioned] [--stash] [--previous X] [--repo-type git|svn|both]" % os.path.basename(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    path = sys.argv[1]
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
    head_staged = False
    head_unversioned = False
    stash = False
    previous = 0
    previous_parse_next = False
    repotype = "both"
    repotype_parse_next = False

    for p in params:

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

        if p == "--default-filter-include":
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

    v, r = collect_patches(path, storage_path, default_filter, include_list, exclude_list, head, head_id, head_staged, head_unversioned, stash, previous, repotype)

    if not v:
        for i in r:
            print("Failed: %s" % i)
        sys.exit(1)
    else:
        print("All passed")
        sys.exit(0)
