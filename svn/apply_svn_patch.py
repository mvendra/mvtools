#!/usr/bin/env python3

import sys
import os
import shutil

import path_utils
import detect_repo_type
import get_platform
import svn_lib
import fsquery

def _test_repo_path(path):

    v, r = detect_repo_type.detect_repo_type(path)
    if not v:
        return False, r
    if r is None:
        return False, "Path [%s] does not point to a supported repository." % path
    return True, None

def apply_svn_patch_head(target_repo, source_files):

    report = []

    if not isinstance(source_files, list):
        return False, "source_files must be a list"

    for sf in source_files:
        v, r = svn_lib.patch_as_head(target_repo, sf, True)
        if not v:
            return False, "Failed patching [%s] into repo [%s]: [%s]" % (sf, target_repo, r)

    return True, report

def apply_svn_patch_unversioned(target_repo, source_files):

    report = []

    if not isinstance(source_files, list):
        return False, "source_files must be a list"

    for sf in source_files:

        sf_base = sf[0]
        sf_file = sf[1]

        if not path_utils.based_copy_to(sf_base, sf_file, target_repo):
            return False, "Failed copying [%s] to [%s]" % (sf, target_repo)

    return True, report

def apply_svn_patch(target_repo, head_patches, unversioned_patches):

    if not isinstance(unversioned_patches, list):
        return False, ["source_files must be a list"]

    target_repo = path_utils.filter_remove_trailing_sep(target_repo)
    target_repo = os.path.abspath(target_repo)

    if not os.path.exists(target_repo):
        return False, ["Target repository %s does not exist" % target_repo]

    v, r = _test_repo_path(target_repo)
    if not v:
        return False, [r]

    report = []
    has_any_failed = False

    # head
    if len(head_patches) > 0:
        v, r = apply_svn_patch_head(target_repo, head_patches)
        if not v:
            has_any_failed = True
            report.append("apply_svn_patch_head: [%s]" % r)
        else:
            report += r

    # unversioned
    if len(unversioned_patches) > 0:
        v, r = apply_svn_patch_unversioned(target_repo, unversioned_patches)
        if not v:
            has_any_failed = True
            report.append("apply_svn_patch_unversioned: [%s]" % r)
        else:
            report += r

    return (not has_any_failed), report

def _assemble_unversioned_all(unversioned_all):

    all_assembled_pairs = []

    for ua in unversioned_all:

        if not os.path.exists(ua):
            return False, "Path [%s] does not exist" % ua

        latest_assembled_pairs = []
        v, r = fsquery.makecontentlist(ua, True, False, True, False, True, False, True, None)
        if not v:
            return False, r
        found_files = r
        for ff in found_files:
            latest_assembled_pairs.append((ua, os.path.abspath(ff)))

        all_assembled_pairs += latest_assembled_pairs

    return True, all_assembled_pairs

def puaq():
    print("Usage: %s target_repo [--head patch-file] [--unversioned file-base patch-file] [--unversioned-all file-base]" % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 4:
        puaq()

    target_repo = sys.argv[1]
    params = sys.argv[2:]

    head = []
    unversioned = []
    unversioned_all = []

    head_parse_next = False
    unversioned_parse_next = 0
    unversioned_base_buffer = None
    unversioned_all_parse_next = False

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

        if unversioned_all_parse_next:
            unversioned_all_parse_next = False
            unversioned_all.append(os.path.abspath(p))
            continue

        if p == "--head":
            head_parse_next = True
        elif p == "--unversioned":
            unversioned_parse_next = 1
        elif p == "--unversioned-all":
            unversioned_all_parse_next = True

    v, r = _assemble_unversioned_all(unversioned_all)
    if not v:
        print(r)
        sys.exit(1)
    unversioned += r

    # pre-filter for dupes
    all_unv_files_sentinel = []
    for uv in unversioned:
        v, r = path_utils.based_path_find_outstanding_path(uv[0], uv[1])
        if not v:
            print(r)
            sys.exit(1)
        file_based_target = r
        if file_based_target in all_unv_files_sentinel:
            print("Duplicated target for unversioned patching detected: [%s]" % file_based_target)
            sys.exit(1)
        all_unv_files_sentinel.append(file_based_target)

    v, r = apply_svn_patch(target_repo, head, unversioned)
    for i in r:
        print(i)
    if not v:
        print("Not everything succeeded.")
        sys.exit(1)
    print("All succeeded.")
