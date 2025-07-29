#!/usr/bin/env python3

import sys
import os

import path_utils
import git_lib
import git_wrapper
import git_backup_current_branch

def git_smash(repo, num_commits):

    if repo is None:
        return False, "git_smash: repo is None"

    if not isinstance(num_commits, int):
        return False, "git_smash: number of commits is not numeric (%s)" % num_commits

    if num_commits == 1:
        return False, "git_smash: number of commits is too small"

    v, r = git_lib.is_head_clear(repo)
    if not v:
        return False, "git_smash failed - repo: [%s]: [%s]" % (repo, r)
    if not r:
        return False, "git_smash: repo [%s] is not clear" % repo

    v, r = git_lib.is_previous_commit_range_by_configured_user(repo, num_commits)
    if not v:
        return False, "git_smash: [%s]" % r

    v, r = git_backup_current_branch.git_backup_current_branch(repo)
    if not v:
        return False, "git_smash: [%s]" % r

    v, r = git_wrapper.reset_soft_head(repo, num_commits)
    if not v:
        return False, "git_smash: [%s]" % r

    return True, "git_smash: (%s) commits smashed down on repo [%s]" % (num_commits, repo)

def puaq(selfhelp):
    print("Usage: %s [repository] number_of_commits" % path_utils.basename_filtered(__file__))
    if selfhelp:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":

    repo = None
    num_commits = None
    if len(sys.argv) < 2:
        puaq(False)
    elif len(sys.argv) == 2:
        num_commits = sys.argv[1]
        repo = os.getcwd()
    else:
        repo = sys.argv[1]
        num_commits = sys.argv[2]

    v, r = git_smash(repo, int(num_commits))
    print(r)
    exit(not v)
