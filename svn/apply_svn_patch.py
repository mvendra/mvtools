#!/usr/bin/env python3

import sys
import os
import shutil

import path_utils
import detect_repo_type
import get_platform
import svn_lib

def _test_repo_path(path):

    v, r = detect_repo_type.detect_repo_type(path)
    if not v:
        return False, r
    if r is None:
        return False, "Path [%s] does not point to a supported repository." % path
    return True, None

def apply_svn_patch_head(target_repo, source_files):

    if not isinstance(source_files, list):
        return False, "source_files must be a list"

    for sf in source_files:
        v, r = svn_lib.patch_as_head(target_repo, sf, True)
        if not v:
            return False, r

    return True, None

def apply_svn_patch_unversioned(target_repo, source_files):

    if not isinstance(source_files, list):
        return False, "source_files must be a list"

    for sf in source_files:

        sf_base = sf[0]
        sf_file = sf[1]

        if not path_utils.based_copy_to(sf_base, sf_file, target_repo):
            return False, "Failed copying [%s] to [%s]" % (sf, target_repo)

    return True, None

def apply_svn_patch(target_repo, head_patches, unversioned_patches):

    if not isinstance(unversioned_patches, list):
        return False, "source_files must be a list"

    target_repo = path_utils.filter_remove_trailing_sep(target_repo)
    target_repo = os.path.abspath(target_repo)

    if not os.path.exists(target_repo):
        return False, ["Target repository %s does not exist" % target_repo]

    v, r = _test_repo_path(target_repo)
    if not v:
        return False, r

    report = []
    has_any_failed = False

    # head
    if len(head_patches) > 0:
        v, r = apply_svn_patch_head(target_repo, head_patches)
        if not v:
            has_any_failed = True
            report.append("apply_svn_patch_head: [%s]" % r)

    # unversioned
    if len(unversioned_patches) > 0:
        v, r = apply_svn_patch_unversioned(target_repo, unversioned_patches)
        if not v:
            has_any_failed = True
            report.append("apply_svn_patch_unversioned: [%s]" % r)

    return (not has_any_failed), report

def puaq():
    print("Usage: %s target_repo [--head patch-file] [--unversioned file-base patch-file]" % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 4:
        puaq()

    target_repo = sys.argv[1]
    params = sys.argv[2:]

    head = []
    unversioned = []

    head_parse_next = False
    unversioned_parse_next = 0
    unversioned_base_buffer = None

    for p in params:

        if head_parse_next:
            head_parse_next = False
            head.append(os.path.abspath(p))
            continue

        if unversioned_parse_next == 1:
            unversioned_parse_next = 2
            unversioned_base_buffer = os.path.abspath(p)
            continue

        if unversioned_parse_next == 2:
            unversioned_parse_next = 0
            unversioned.append( (unversioned_base_buffer, os.path.abspath(p)) )
            unversioned_base_buffer = None
            continue

        if p == "--head":
            head_parse_next = True
        elif p == "--unversioned":
            unversioned_parse_next = 1

    v, r = apply_svn_patch(target_repo, head, unversioned)
    if not v:
        for i in r:
            print("Failed: %s" % i)
        sys.exit(1)
    else:
        print("All succeeded")
