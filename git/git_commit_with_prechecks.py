#!/usr/bin/env python

import sys
import os

from subprocess import check_output
from subprocess import CalledProcessError

import test_mvtags_in_git_cache

def gicom(repo, params):

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

    check = test_mvtags_in_git_cache.check_mvtags_in_repo(repo)
    if len(check) == 0:
        # no mvtags detected. we are clear to proceed and commit
        gicom(repo, params)
    else:
        # violations detected. report and abort.
        # mvtodo: offer interactive chance to allow commit to pass
        for c in check:
            print("%s has pre-commit violations." % c)
        exit(1)

