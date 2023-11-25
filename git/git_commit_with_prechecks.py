#!/usr/bin/env python3

import sys
import os

import git_lib
import test_mvtags_in_git_cache
import inline_echo

def gicom(repo, params):

    if len(params) == 0:
        # special case. we will call git differently
        # because here we want the $EDITOR to be able to more easily
        # integrate with the calling terminal
        v, r = git_lib.commit_editor(repo)
    else:
        v, r = git_lib.commit_direct(repo, params)

    if not v:
        print("gicom failed: [%s]" % r)
    exit(not v)

if __name__ == "__main__":

    params = sys.argv[1:]
    repo = os.getcwd()

    repo = git_lib.discover_repo_root(repo)
    if repo is None:
        print("Failed detecting repo from %s." % repo)
        exit(1)

    check = []
    if "--ignore-mvtags" in params:
        # we will ignore the checks
        # we need to remove the --ignore-mvtags params here because it will trip git
        params_copy = params
        params = []
        for p in params_copy:
            if p != "--ignore-mvtags":
                params.append(p)
    else:
        # lets apply the pre-commit checks
        check = test_mvtags_in_git_cache.check_mvtags_in_repo(repo)

    if len(check) == 0:
        # no mvtags detected/override valve activated. we are clear to proceed and commit.
        gicom(repo, params)
    else:
        # violations detected. report and abort.
        for c in check:
            print("%s has pre-commit violations." % c)
        exit(1)
