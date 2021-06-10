#!/usr/bin/env python3

import sys
import os

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

def reset_repo(target_repo, files):

    if not os.path.exists(target_repo):
        return False, ["Target repo [%s] does not exist."  % target_repo]

    v, r = check_repo_type(target_repo)
    if not v:
        return False, r
    detected_repo_type = r

    if detected_repo_type == detect_repo_type.REPO_TYPE_GIT_STD:
        return reset_git_repo.reset_git_repo(target_repo, files)
    elif detected_repo_type == detect_repo_type.REPO_TYPE_SVN:
        return reset_svn_repo.reset_svn_repo(target_repo, files)

    return False, ["Resetting failed: Unsupported repo type: [%s]" % repotype]

def puaq():
    print("Usage: %s target_repo [--file filepath]" % os.path.basename(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    target_repo = sys.argv[1]
    params = sys.argv[2:]

    files = []
    files_parse_next = False

    for p in params:

        if files_parse_next:
            files.append(p)
            files_parse_next = False
            continue

        if p == "--file":
            files_parse_next = True

    if len(files) == 0:
        files = None
    v, r = reset_repo(target_repo, files)
    for i in r:
        print(i)
    if not v:
        print("Not everything succeeded.")
        sys.exit(1)
    print("All succeeded.")
