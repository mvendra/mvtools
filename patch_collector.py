#!/usr/bin/env python3

import sys
import os

import fsquery
import detect_repo_type
import collect_git_patch
import collect_svn_patch

def collect_patches(path, storage_path, head, head_id, head_staged, head_unversioned, stash, previous, repotype):

    if repotype != "svn" and repotype != "git" and repotype != "both":
        return False, ["Invalid repository type: %s" % repotype]

    if not os.path.exists(storage_path):
        return False, ["Storage path [%s] does not exist."  % storage_path]

    items = fsquery.makecontentlist(path, True, False, True, False, True, True, None)

    report = []

    for it in items:
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
    print("Usage: %s path [--storage-path the_storage_path] [--head] [--head-id] [--head-staged] [--head-unversioned] [--stash] [--previous X] [--repo-type git|svn|both]" % os.path.basename(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    path = sys.argv[1]
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
        elif p == "--repo-type":
            repotype_parse_next = True

    if storage_path is None:
        storage_path = os.getcwd()

    v, r = collect_patches(path, storage_path, head, head_id, head_staged, head_unversioned, stash, previous, repotype)

    if not v:
        for i in r:
            print("Failed: %s" % i)
        sys.exit(1)
    else:
        print("All passed")
        sys.exit(0)
