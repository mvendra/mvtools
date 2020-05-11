#!/usr/bin/env python3

import sys
import os

import generic_run

def status(repo):

    if not os.path.exists(repo):
        return False, "%s does not exist." % repo

    v, r = generic_run.run_cmd_simple(["svn", "status"], use_cwd=repo)
    if not v:
        return False, "Failed calling svn-status command: %s." % r

    return v, r

def info(repo):

    if not os.path.exists(repo):
        return False, "%s does not exist." % repo

    v, r = generic_run.run_cmd_simple(["svn", "info"], use_cwd=repo)
    if not v:
        return False, "Failed calling svn-info command: %s." % r

    return v, r

def log(repo, limit=None):

    if not os.path.exists(repo):
        return False, "%s does not exist." % repo

    cmd = ["svn", "log"]
    if limit is not None:
        cmd.append("--limit")
        cmd.append(limit)

    v, r = generic_run.run_cmd_simple(cmd, use_cwd=repo)
    if not v:
        return False, "Failed calling svn-log command: %s." % r

    return v, r

def diff(repo, rev=None):

    if not os.path.exists(repo):
        return False, "%s does not exist." % repo

    cmd = ["svn", "diff", "--internal-diff"]
    if rev is not None:
        cmd.append("-c")
        cmd.append(rev)

    v, r = generic_run.run_cmd_simple(cmd, use_cwd=repo)
    if not v:
        return False, "Failed calling svn-diff command: %s." % r

    return v, r

def puaq():
    print("Hello from %s" % os.path.basename(__file__))
    sys.exit(1)

if __name__ == "__main__":
    puaq()
