#!/usr/bin/env python3

import sys
import os
import shutil

import mvtools_envvars
import path_utils
import detect_repo_type
import git_lib

def _test_repo_path(path):

    v, r = detect_repo_type.detect_repo_type(path)
    if not v:
        return False, r
    if r is None:
        return False, "Path [%s] does not point to a supported repository." % path
    return True, None

def apply_git_patch(source_repo, target_repo, head, staged, stash, unversioned, previous):

    v, r = mvtools_envvars.mvtools_envvar_read_temp_path()
    if not v:
        return False, r
    temp_path = r
    if not os.path.exists(temp_path):
        return False, "Can't apply patches. MVTOOLS_TEMP_PATH envvar is not defined or the path does not exist."

    temp_path_patches = path_utils.concat_path(temp_path, "temp_path_patches")
    if os.path.exists(temp_path_patches):
        return False, "Can't apply patches. Temporary path [%s] already exists." % temp_path_patches
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

    # mvtodo: stash
    # mvtodo: previous
    # mvtodo: staged
    # mvtodo: head
    # mvtodo: unversioned

    if stash:
        pass # mvtodo

    # head
    """
    if head:
        v, r = collect_git_patch_head(source_repo, temp_path)
        has_any_failed |= (not v)
        # mvtodo: read written patch file from r
        report.append(r)
    """

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
