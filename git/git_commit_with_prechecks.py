#!/usr/bin/env python

import sys
import os

from subprocess import check_output
from subprocess import call
from subprocess import CalledProcessError

import test_mvtags_in_git_cache

def gicom(repo, params):

    if len(params) == 0:
        # special case. we will call git differently
        # because here we want the $EDITOR to be able to more easily
        # integrate with the calling terminal
        retcode = call("git -C %s commit" % repo, shell=True)
        exit(retcode)

    cmd = ["git",  "-C", repo, "commit"]
    for p in params:
        cmd.append(p)

    try:
        out = check_output(cmd)
        print(out.strip())
    except CalledProcessError as cpe:
        print(cpe.output.strip())
        exit(cpe.returncode) 

if __name__ == "__main__":

    params = sys.argv[1:]
    repo = os.getcwd()

    try:
        repo = check_output(["git_discover_repo_root.py", repo])
    except CalledProcessError as cpe:
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

