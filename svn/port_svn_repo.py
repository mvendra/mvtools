#!/usr/bin/env python3

import sys
import os
import shutil

import mvtools_envvars
import maketimestamp
import path_utils
import detect_repo_type
import collect_svn_patch
import apply_svn_patch

def _test_repo_path(path):

    v, r = detect_repo_type.detect_repo_type(path)
    if not v:
        return False, r
    if r is None:
        return False, "Path [%s] does not point to a supported repository." % path
    return True, None

def port_svn_repo_previous(temp_path, source_repo, target_repo, previous_count):

    report = []

    previous_files = None
    v, r = collect_svn_patch.collect_svn_patch_previous(source_repo, temp_path, previous_count)
    if not v:
        return False, "Failed porting previous (during collect-previous) from [%s] to [%s]: [%s]" % (source_repo, target_repo, r)
    previous_files = reversed(r)

    # previous commits will be stacked up ontop of head - no autocommitting is available (on purpose)
    v, r = apply_svn_patch.apply_svn_patch_head(target_repo, previous_files)
    if not v:
        return False, "Failed porting previous (during head-apply) from [%s] to [%s]: [%s]" % (source_repo, target_repo, r)

    return True, report

def port_svn_repo_head(temp_path, source_repo, target_repo):

    report = []

    head_files = None
    v, r = collect_svn_patch.collect_svn_patch_head(source_repo, temp_path, "include", [], [])
    if not v:
        if r == collect_svn_patch.ERRMSG_EMPTY:
            return True, [] # ignore if target head is unmodified
        return False, "Failed collecting head from [%s] to [%s]: [%s]" % (source_repo, target_repo, r)
    head_files = [r]

    v, r = apply_svn_patch.apply_svn_patch_head(target_repo, head_files)
    if not v:
        return False, "Failed patching head from [%s] to [%s]: [%s]" % (source_repo, target_repo, r)

    return True, report

def port_svn_repo_unversioned(temp_path, source_repo, target_repo):

    report = []

    unversioned_files = None
    v, r = collect_svn_patch.collect_svn_patch_unversioned(source_repo, temp_path, "include", [], [])
    if not v:
        return False, "Failed collecting unversioned from [%s] to [%s]: [%s]" % (source_repo, target_repo, r)
    unversioned_files = r
    combined_base = path_utils.concat_path(temp_path, source_repo, "unversioned")

    uvf_param = []
    for uf in unversioned_files:
        uvf_param.append( (combined_base, uf) )

    v, r = apply_svn_patch.apply_svn_patch_unversioned(target_repo, uvf_param)
    if not v:
        return False, "Failed porting unversioned from [%s] to [%s]: [%s]" % (source_repo, target_repo, r)

    return True, report

def port_svn_repo(source_repo, target_repo, head, unversioned, previous):

    v, r = mvtools_envvars.mvtools_envvar_read_temp_path()
    if not v:
        return False, [r]
    temp_path = r
    if not os.path.exists(temp_path):
        return False, ["Can't apply patches. MVTOOLS_TEMP_PATH envvar is not defined or the path does not exist."]

    timestamp_now = maketimestamp.get_timestamp_now_compact()
    temp_path_patches = path_utils.concat_path(temp_path, ("temp_path_patches_%s" % timestamp_now))
    if os.path.exists(temp_path_patches):
        return False, ["Can't apply patches. Temporary path [%s] already exists." % temp_path_patches]
    os.mkdir(temp_path_patches)

    v, r = _port_svn_repo_delegate(temp_path_patches, source_repo, target_repo, head, unversioned, previous)
    shutil.rmtree(temp_path_patches)
    return v, r

def _port_svn_repo_delegate(temp_path, source_repo, target_repo, head, unversioned, previous):

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
        return False, [r]

    v, r = _test_repo_path(target_repo)
    if not v:
        return False, [r]

    report = []
    has_any_failed = False

    # previous
    if previous > 0:
        v, r = port_svn_repo_previous(temp_path, source_repo, target_repo, previous)
        if not v:
            has_any_failed = True
            report.append("port_svn_repo_previous: [%s]" % r)
        else:
            report += r

    # head
    if head:
        v, r = port_svn_repo_head(temp_path, source_repo, target_repo)
        if not v:
            has_any_failed = True
            report.append("port_svn_repo_head: [%s]" % r)
        else:
            report += r

    # unversioned
    if unversioned:
        v, r = port_svn_repo_unversioned(temp_path, source_repo, target_repo)
        if not v:
            has_any_failed = True
            report.append("port_svn_repo_unversioned: [%s]" % r)
        else:
            report += r

    return (not has_any_failed), report

def puaq():
    print("Usage: %s source_repo target_repo [--head] [--unversioned] [--previous]" % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 3:
        puaq()

    source_repo = sys.argv[1]
    target_repo = sys.argv[2]
    params = sys.argv[3:]

    head = False
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
        elif p == "--unversioned":
            unversioned = True
        elif p == "--previous":
            previous_parse_next = True

    v, r = port_svn_repo(source_repo, target_repo, head, unversioned, previous)
    for i in r:
        print(i)
    if not v:
        print("Not everything succeeded.")
        sys.exit(1)
    print("All succeeded.")
