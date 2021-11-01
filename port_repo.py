#!/usr/bin/env python3

import sys
import os

import path_utils
import detect_repo_type
import port_git_repo
import port_svn_repo

def check_repos_type(source_repo, target_repo):

    supported_repo_types = [detect_repo_type.REPO_TYPE_GIT_STD, detect_repo_type.REPO_TYPE_SVN]

    v, r = detect_repo_type.detect_repo_type(source_repo)
    if not v:
        return False, "Unable to detect source repo type [%s]" % source_repo
    detected_source_type = r

    if detected_source_type not in supported_repo_types:
        return False, "Source repo [%s] is not supported for porting." % source_repo

    v, r = detect_repo_type.detect_repo_type(target_repo)
    if not v:
        return False, "Unable to detect target repo type [%s]" % target_repo
    detected_target_type = r

    if detected_target_type not in supported_repo_types:
        return False, "Target repo [%s] is not supported for porting." % target_repo

    if detected_source_type != detected_target_type:
        return False, "Detected source repo type [%s] differs from target repo type [%s]" % (detected_source_type, detected_target_type)

    if "git" in detected_source_type and "bare" in detected_source_type: # cant collect patches for git bare repos
        return False, "Bare git repos are not portable"

    return True, detected_source_type

def port_repo(source_repo, target_repo, head, staged, stash, unversioned, previous):

    if not os.path.exists(source_repo):
        return False, "Source repo [%s] does not exist."  % source_repo

    if not os.path.exists(target_repo):
        return False, "Target repo [%s] does not exist."  % target_repo

    v, r = check_repos_type(source_repo, target_repo)
    if not v:
        return False, r
    repos_type = r

    if repos_type == detect_repo_type.REPO_TYPE_GIT_STD:
        return port_git_repo.port_git_repo(source_repo, target_repo, head, staged, stash, unversioned, previous) # mvtodo: wirings
    elif repos_type == detect_repo_type.REPO_TYPE_SVN:
        return port_svn_repo.port_svn_repo(source_repo, target_repo, head, unversioned, previous) # mvtodo: wirings

    return False, "Porting failed: Unsupported repo type: [%s]" % repos_type

def puaq():
    print("Usage: %s source_repo target_repo [--head] [--staged] [--stash X (use \"-1\" to port the entire stash)] [--unversioned] [--previous X]" % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 3:
        puaq()

    source_repo = sys.argv[1]
    target_repo = sys.argv[2]
    params = sys.argv[3:]

    head = False
    staged = False
    stash = 0
    stash_parse_next = False
    unversioned = False
    previous = 0

    previous_parse_next = False

    for p in params:

        if stash_parse_next:
            stash = int(p)
            stash_parse_next = False
            continue

        if previous_parse_next:
            previous = int(p)
            previous_parse_next = False
            continue

        if p == "--previous":
            previous_parse_next = True
        elif p == "--head":
            head = True
        elif p == "--staged":
            staged = True
        elif p == "--stash":
            stash_parse_next = True
        elif p == "--unversioned":
            unversioned = True

    v, r = port_repo(source_repo, target_repo, head, staged, stash, unversioned, previous)
    if not v:
        print("Porting repo [%s] to [%s] failed: %s" % (source_repo, target_repo, r))
        sys.exit(1)
    print("Succeeded")
