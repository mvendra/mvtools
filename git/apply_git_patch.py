#!/usr/bin/env python3

import sys
import os
import shutil

import mvtools_envvars
import path_utils
import detect_repo_type
import collect_git_patch
import git_lib

def _test_repo_path(path):

    v, r = detect_repo_type.detect_repo_type(path)
    if not v:
        return False, r
    if r is None:
        return False, "Path [%s] does not point to a supported repository." % path
    return True, None

def apply_git_patch_stash(temp_path, source_repo, target_repo):

    stash_files = None
    v, r = collect_git_patch.collect_git_patch_stash(source_repo, temp_path)
    if not v:
        return False, r
    stash_files = r

    for sf in reversed(stash_files):
        v, r = git_lib.patch_as_stash(target_repo, sf, True, True)
        if not v:
            return False, r

    return True, None

def apply_git_patch_previous(temp_path, source_repo, target_repo, previous_count):

    previous_files = None
    v, r = collect_git_patch.collect_git_patch_previous(source_repo, temp_path, previous_count)
    if not v:
        return False, r
    previous_files = r

    # previous commits will be stacked up ontop of head - no autocommitting is available (on purpose)
    for pf in reversed(previous_files):
        v, r = git_lib.patch_as_head(target_repo, pf, True)
        if not v:
            return False, r

    return True, None

def apply_git_patch_staged(temp_path, source_repo, target_repo):

    staged_file = None
    v, r = collect_git_patch.collect_git_patch_staged(source_repo, temp_path)
    if not v:
        return False, r
    staged_file = r

    v, r = git_lib.patch_as_staged(target_repo, staged_file, True)
    if not v:
        return False, r

    return True, None

def apply_git_patch_head(temp_path, source_repo, target_repo):

    head_file = None
    v, r = collect_git_patch.collect_git_patch_head(source_repo, temp_path)
    if not v:
        return False, r
    head_file = r

    v, r = git_lib.patch_as_head(target_repo, head_file, True)
    if not v:
        return False, r

    return True, None

def apply_git_patch_unversioned(source_repo, target_repo):
    return False, "mvtodo"

def apply_git_patch(source_repo, target_repo, head, staged, stash, unversioned, previous):

    v, r = mvtools_envvars.mvtools_envvar_read_temp_path()
    if not v:
        return False, r
    temp_path = r
    if not os.path.exists(temp_path):
        return False, ["Can't apply patches. MVTOOLS_TEMP_PATH envvar is not defined or the path does not exist."]

    temp_path_patches = path_utils.concat_path(temp_path, "temp_path_patches")
    if os.path.exists(temp_path_patches):
        return False, ["Can't apply patches. Temporary path [%s] already exists." % temp_path_patches]
    os.mkdir(temp_path_patches)

    v, r = _apply_git_patch_delegate(temp_path_patches, source_repo, target_repo, head, staged, stash, unversioned, previous)
    shutil.rmtree(temp_path_patches)
    return v, r

def _apply_git_patch_delegate(temp_path, source_repo, target_repo, head, staged, stash, unversioned, previous):

    source_repo = path_utils.filter_remove_trailing_sep(source_repo)
    source_repo = os.path.abspath(source_repo)
    target_repo = path_utils.filter_remove_trailing_sep(target_repo)
    target_repo = os.path.abspath(target_repo)

    if not os.path.exists(source_repo):
        return False, ["Source repository %s does not exist" % source_repo]

    if not os.path.exists(target_repo):
        return False, ["Target repository %s does not exist" % target_repo]

    v, r = _test_repo_path(source_repo)
    if not v:
        return False, r

    v, r = _test_repo_path(target_repo)
    if not v:
        return False, r

    report = []
    has_any_failed = False

    # stash
    if stash:
        v, r = apply_git_patch_stash(temp_path, source_repo, target_repo)
        if not v:
            has_any_failed = True
            report.append("apply_git_patch_stash: [%s]" % r)

    # previous
    if previous > 0:
        v, r = apply_git_patch_previous(temp_path, source_repo, target_repo, previous)
        if not v:
            has_any_failed = True
            report.append("apply_git_patch_previous: [%s]" % r)

    # staged
    if staged:
        v, r = apply_git_patch_staged(temp_path, source_repo, target_repo)
        if not v:
            has_any_failed = True
            report.append("apply_git_patch_staged: [%s]" % r)

    # head
    if head:
        v, r = apply_git_patch_head(temp_path, source_repo, target_repo)
        if not v:
            has_any_failed = True
            report.append("apply_git_patch_head: [%s]" % r)

    # unversioned
    if unversioned:
        v, r = apply_git_patch_unversioned(source_repo, target_repo)
        if not v:
            has_any_failed = True
            report.append("apply_git_patch_unversioned: [%s]" % r)

    return (not has_any_failed), report

def puaq():
    print("Usage: %s source_repo target_repo [--head] [--staged] [--stash] [--unversioned] [--previous]" % os.path.basename(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 3:
        puaq()

    source_repo = sys.argv[1]
    target_repo = sys.argv[2]
    params = sys.argv[3:]

    head = False
    staged = False
    stash = False
    unversioned = False
    previous = 0
    previous_parse_next = False

    for p in params:

        if previous_parse_next:
            previous = int(p)
            previous_parse_next = False
            continue

        if p == "--head":
            head = True
        elif p == "--staged":
            staged = True
        elif p == "--stash":
            stash = True
        elif p == "--unversioned":
            unversioned = True
        elif p == "--previous":
            previous_parse_next = True

    v, r = apply_git_patch(source_repo, target_repo, head, staged, stash, unversioned, previous)
    if not v:
        for i in r:
            print("Failed: %s" % i)
        sys.exit(1)
    else:
        print("All succeeded")
