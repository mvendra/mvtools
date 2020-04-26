#!/usr/bin/env python3

import sys
import os

from subprocess import call

import generic_run

def git_wrapper_standard_command(cmd, cmd_name):
    v, r = generic_run.run_cmd_simple(cmd)
    if not v:
        return False, "Failed calling %s: %s" % (cmd_name, r)
    return v, r

def config(key, value, global_cfg=True):

    cmd = ["git", "config"]
    if global_cfg:
        cmd.append("--global")
    cmd.append(key)
    cmd.append(value)

    return git_wrapper_standard_command(cmd, "git-config")

def commit_editor(repo):
    retcode = call("git -C %s commit" % repo, shell=True) # mvtodo: still not supported by generic_run
    return (retcode==0), "git_wrapper.commit_editor"

def commit_direct(repo, params):

    cmd = ["git",  "-C", repo, "commit"]
    for p in params:
        cmd.append(p)

    return git_wrapper_standard_command(cmd, "git-commit (direct)")

def commit(repo, msg):
    cmd = ["git", "-C", repo, "commit", "-m", msg]
    return git_wrapper_standard_command(cmd, "git-commit")

def diff(repo, cached=False, specific_file=None):

    cmd = ["git", "-C", repo, "diff", "--no-ext-diff"]
    if cached:
        cmd.append("--cached")
    if specific_file is not None:
        cmd.append(specific_file)

    return git_wrapper_standard_command(cmd, "git-diff")

def rev_parse(repo):
    cmd = ["git", "-C", repo, "rev-parse", "HEAD"]
    return git_wrapper_standard_command(cmd, "rev-parse")

def ls_files(repo):
    cmd = ["git", "-C", repo, "ls-files", "--exclude-standard", "--others"]
    return git_wrapper_standard_command(cmd, "ls-files")

def stash_list(repo):
    cmd = ["git", "-C", repo, "stash", "list"]
    return git_wrapper_standard_command(cmd, "stash-list")

def stash_show(repo, stash_name):
    cmd = ["git", "-C", repo, "stash", "show", "-p", "--no-ext-diff", stash_name]
    return git_wrapper_standard_command(cmd, "stash-show")

def log(repo):
    cmd = ["git", "-C", repo, "log", "--oneline"]
    return git_wrapper_standard_command(cmd, "log")

def show(repo, commit_id):
    cmd = ["git", "-C", repo, "show", commit_id]
    return git_wrapper_standard_command(cmd, "show")

def puaq():
    print("Usage: %s repo [--commit]" % os.path.basename(__file__)) # mvtodo
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    repo = sys.argv[1]
    options = sys.argv[2:]

    print(options) # mvtodo: implement
