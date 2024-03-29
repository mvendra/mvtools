#!/usr/bin/env python3

import sys
import os

import git_lib
import test_mvtags_in_git_cache
import inline_echo

def gicom(repo, params):

    if len(params) == 0:
        return False, "editor invocation is no longer supported here"
    return git_lib.commit_direct(repo, params)

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
        v, r = gicom(repo, params)
        if v:
            inline_echo.inline_echo(r)
        else:
            print(r)
            exit(1)
    else:
        # violations detected. report and abort.
        for c in check:
            print("%s has pre-commit violations." % c)
        exit(1)
