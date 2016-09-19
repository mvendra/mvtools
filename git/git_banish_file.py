#!/usr/bin/env python

import sys
import os

from subprocess import check_output

import git_repo_query

def git_banish_file(fname, repo):

    # check if fname exists
    if not os.path.exists(fname):
        print("%s does not exist" % fname)
        exit(1)

    # check if repo is indeed a repo
    if not git_repo_query.is_git_work_tree(repo):
        print("You are supposed to point the repo to its base tree - where the .git folder is located at")
        exit(1)

    os.system("git filter-branch --index-filter \ 'git rm --ignore-unmatch --cached %s' -- HEAD" % fname)

def puaq():
    print("Usage: %s file [repo, or I will assume the current working dir]" % os.path.basename(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    filename = sys.argv[1]
    repo = None
    if len(sys.argv) > 2:
        repo = sys.argv[2]
    else:
        repo = os.getcwd()

    git_banish_file(filename, repo)

