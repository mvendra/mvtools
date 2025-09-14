#!/usr/bin/env python

import sys
import os

import path_utils
import detect_repo_type
import reset_git_repo
import reset_svn_repo

def check_repo_type(target_repo):

    supported_repo_types = [detect_repo_type.REPO_TYPE_GIT_STD, detect_repo_type.REPO_TYPE_SVN]

    v, r = detect_repo_type.detect_repo_type(target_repo)
    if not v:
        return False, "Unable to detect target repo type [%s]" % target_repo
    detected_target_type = r

    if detected_target_type not in supported_repo_types:
        return False, "Target repo [%s] is not supported for resetting." % target_repo

    if "git" in detected_target_type and "bare" in detected_target_type:
        return False, "Bare git repos are not resetable"

    return True, detected_target_type

def reset_repo(target_repo, default_filter, include_list, exclude_list, head, staged, stash, unversioned, previous):

    if not os.path.exists(target_repo):
        return False, ["Target repo [%s] does not exist."  % target_repo]

    v, r = check_repo_type(target_repo)
    if not v:
        return False, r
    detected_repo_type = r

    if detected_repo_type == detect_repo_type.REPO_TYPE_GIT_STD:
        return reset_git_repo.reset_git_repo(target_repo, default_filter, include_list, exclude_list, head, staged, stash, unversioned, previous)
    elif detected_repo_type == detect_repo_type.REPO_TYPE_SVN:
        return reset_svn_repo.reset_svn_repo(target_repo, default_filter, include_list, exclude_list, head, unversioned, previous)

    return False, ["Resetting failed: Unsupported repo type: [%s]" % repotype]

def puaq(selfhelp):
    print("Usage: %s target_repo [--default-filter-include | --default-filter-exclude] [--include repo_basename] [--exclude repo_basename] [--head] [--staged] [--stash X (use \"-1\" to reset the entire stash)] [--unversioned] [--previous X]" % path_utils.basename_filtered(__file__))
    if selfhelp:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq(False)

    target_repo = sys.argv[1]
    params = sys.argv[2:]

    default_filter = "include"
    include_list = []
    exclude_list = []
    include_parse_next = False
    exclude_parse_next = False
    head = False
    staged = False
    stash = 0
    stash_parse_next = False
    unversioned = False
    previous = 0
    previous_parse_next = False

    for p in params:

        if include_parse_next:
            include_list.append(p)
            include_parse_next = False
            continue

        if exclude_parse_next:
            exclude_list.append(p)
            exclude_parse_next = False
            continue

        if stash_parse_next:
            stash = int(p)
            stash_parse_next = False
            continue

        if previous_parse_next:
            previous = int(p)
            previous_parse_next = False
            continue

        if p == "--default-filter-include":
            default_filter = "include"
        elif p == "--default-filter-exclude":
            default_filter = "exclude"
        elif p == "--include":
            include_parse_next = True
        elif p == "--exclude":
            exclude_parse_next = True
        elif p == "--head":
            head = True
        elif p == "--staged":
            staged = True
        elif p == "--stash":
            stash_parse_next = True
        elif p == "--unversioned":
            unversioned = True
        elif p == "--previous":
            previous_parse_next = True

    v, r = reset_repo(target_repo, default_filter, include_list, exclude_list, head, staged, stash, unversioned, previous)
    for i in r:
        print(i)
    if not v:
        print("Not everything succeeded.")
        sys.exit(1)
    print("All succeeded.")
