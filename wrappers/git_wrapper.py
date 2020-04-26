#!/usr/bin/env python3

import sys
import os

from subprocess import check_output
from subprocess import call
from subprocess import CalledProcessError

import generic_run

def puaq():
    print("Usage: %s repo [--commit]" % os.path.basename(__file__)) # mvtodo
    sys.exit(1)

def commit_editor(repo):

    retcode = call("git -C %s commit" % repo, shell=True) # mvtodo: still not supported by generic_run
    return (retcode==0), "git_wrapper.commit_editor"

def commit_direct(repo, params):

    cmd = ["git",  "-C", repo, "commit"]
    for p in params:
        cmd.append(p)

    v, r = generic_run.run_cmd_simple(cmd)
    if not v:
        return False, "Failed calling git-commit (direct) command."
    return v, r

def commit(repo, msg):

    cmd = ["git", "-C", repo, "commit", "-m", msg]
    v, r = generic_run.run_cmd_simple(cmd)
    if not v:
        return False, "Failed calling git-commit command."
    return v, r

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    repo = sys.argv[1]
    options = sys.argv[2:]

    print(options) # mvtodo: implement
