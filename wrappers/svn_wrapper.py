#!/usr/bin/env python3

import sys
import os

import path_utils
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

def diff(repo, file_list=None, rev=None):

    if not os.path.exists(repo):
        return False, "%s does not exist." % repo

    cmd = ["svn", "diff", "--internal-diff"]
    if rev is not None:
        cmd.append("-c")
        cmd.append(rev)

    if file_list is not None:
        for fl in file_list:
            cmd.append(fl)

    v, r = generic_run.run_cmd_simple(cmd, use_cwd=repo)
    if not v:
        return False, "Failed calling svn-diff command: %s." % r

    return v, r

def checkout(remote_link, local_repo):

    if os.path.exists(local_repo):
        return False, "%s already exists." % local_repo

    base_path = os.path.dirname(local_repo)
    if base_path == local_repo:
        return False, "Target path [%s] is invalid." % local_repo
    local_target_name = os.path.basename(local_repo)

    v, r = generic_run.run_cmd_simple(["svn", "checkout", remote_link, local_target_name], use_cwd=base_path)
    if not v:
        return False, "Failed calling svn-checkout command: %s." % r

    return v, r

def cleanup(local_repo):

    if not os.path.exists(local_repo):
        return False, "%s does not exist." % local_repo

    v, r = generic_run.run_cmd_simple(["svn", "cleanup"], use_cwd=local_repo)
    if not v:
        return False, "Failed calling svn-cleanup command: %s." % r

    return v, r

def update(local_repo):

    if not os.path.exists(local_repo):
        return False, "%s does not exist." % local_repo

    v, r = generic_run.run_cmd_simple(["svn", "update"], use_cwd=local_repo)
    if not v:
        return False, "Failed calling svn-update command: %s." % r

    return v, r

def revert(local_repo, repo_items):

    if not os.path.exists(local_repo):
        return False, "Base repo [%s] does not exist." % local_repo

    the_cmd = ["svn", "revert"]
    the_cmd += repo_items

    v, r = generic_run.run_cmd_simple(the_cmd, use_cwd=local_repo)
    if not v:
        return False, "Failed calling svn-revert command: %s." % r

    return True, None

def patch(repo, source_file):

    if not os.path.exists(repo):
        return False, "%s does not exist." % repo

    v, r = generic_run.run_cmd_simple(["svn", "patch", source_file], use_cwd=repo)
    if not v:
        return False, "Failed calling svn-patch command: %s." % r

    return v, r

def puaq():
    print("Hello from %s" % os.path.basename(__file__))
    sys.exit(1)

if __name__ == "__main__":
    puaq()
