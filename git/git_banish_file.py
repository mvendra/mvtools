#!/usr/bin/env python3

import sys
import os

import git_lib

def runcmd(cmd):
    if os.system(cmd) != 0:
        raise BaseException("%s failed!" % cmd)

def git_banish_file(repo, fname):

    # check if fname exists
    if not os.path.exists(fname):
        print("%s does not exist" % fname)
        exit(1)

    # check if repo is indeed a repo
    if not git_lib.is_git_work_tree(repo):
        print("You are supposed to point the repo to its base tree - where the .git folder is located at")
        exit(1)

    answer = input("Are you sure you want to proceed? This change is irreversible (type in \"yes\" to proceed): ")
    if answer != "yes":
        print("Aborted")
        exit(1)

    runcmd("git filter-branch --index-filter \ 'git rm --ignore-unmatch --cached %s' -- HEAD" % fname)

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

    git_banish_file(repo, filename)
