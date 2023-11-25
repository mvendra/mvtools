#!/usr/bin/env python3

import sys
import os

import path_utils
import git_lib

def git_backup_current_branch(repo):

    if repo is None:
        return False, "No repo specified"

    repo = os.path.abspath(repo)

    t1 = git_lib.is_repo_working_tree(repo)
    if t1 is None:
        return False, "%s does not exist." % repo
    elif t1 is False:
        return False, "%s is not a git work tree." % repo

    current_branch = None
    v, r = git_lib.get_current_branch(repo)
    if not v:
        return v, r
    current_branch = r

    backup_branch = "%s_bk" % current_branch
    v, r = git_lib.create_branch(repo, backup_branch)
    if not v:
        return v, r

    return True, "Created backup of branch [%s] as [%s]" % (current_branch, backup_branch)

if __name__ == "__main__":

    repo = os.getcwd()
    if len(sys.argv) > 1:
        repo = sys.argv[1]

    v, r = git_backup_current_branch(repo)
    if v:
        print(r)
    else:
        print("Backing up current branch failed for repo [%s]: [%s]" % (repo, r))
        exit(1)
