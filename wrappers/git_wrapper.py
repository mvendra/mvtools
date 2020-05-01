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

    return git_wrapper_standard_command(cmd, "config")

def commit_editor(repo):
    retcode = call("git -C %s commit" % repo, shell=True) # mvtodo: still not supported by generic_run
    return (retcode==0), "git_wrapper.commit_editor"

def commit_direct(repo, params):
    cmd = ["git",  "-C", repo, "commit"]
    for p in params:
        cmd.append(p)
    return git_wrapper_standard_command(cmd, "commit-direct")

def commit(repo, msg):
    cmd = ["git", "-C", repo, "commit", "-m", msg]
    return git_wrapper_standard_command(cmd, "commit")

def init(repo_base, repo_name, bare):
    cmd = ["git", "-C", repo_base, "init", repo_name]
    if bare:
        cmd.append("--bare")
    return git_wrapper_standard_command(cmd, "init")

def clone(repo_source, repo_target, remotename=None):
    cmd = ["git", "clone", repo_source, repo_target]
    if remotename is not None:
        cmd.append("-o")
        cmd.append(remotename)
    return git_wrapper_standard_command(cmd, "clone")

def diff(repo, specific_file=None):
    cmd = ["git", "-C", repo, "diff", "--no-ext-diff"]
    if specific_file is not None:
        cmd.append(specific_file)
    return git_wrapper_standard_command(cmd, "diff")

def diff_cached(repo, specific_file=None):
    cmd = ["git", "-C", repo, "diff", "--no-ext-diff", "--cached"]
    if specific_file is not None:
        cmd.append(specific_file)
    return git_wrapper_standard_command(cmd, "diff-cached")

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

def log_oneline(repo):
    cmd = ["git", "-C", repo, "log", "--oneline"]
    return git_wrapper_standard_command(cmd, "log-oneline")

def log(repo):
    cmd = ["git", "-C", repo, "log"]
    return git_wrapper_standard_command(cmd, "log")

def show(repo, commit_id):
    cmd = ["git", "-C", repo, "show", commit_id]
    return git_wrapper_standard_command(cmd, "show")

def status(repo):
    cmd = ["git", "-C", repo, "status", "--porcelain"]
    return git_wrapper_standard_command(cmd, "status")

def status_simple(repo):
    cmd = ["git", "-C", repo, "status", "-s"]
    return git_wrapper_standard_command(cmd, "status-simple")

def remote_list(repo):
    cmd = ["git", "-C", repo, "remote", "-v"]
    return git_wrapper_standard_command(cmd, "remote-list")

def remote_change_url(repo, remote, new_url):
    cmd = ["git", "-C", repo, "remote", "set-url", remote, new_url]
    return git_wrapper_standard_command(cmd, "remote-change-url")

def branch(repo):
    cmd = ["git", "-C", repo, "branch"]
    return git_wrapper_standard_command(cmd, "branch")

def pull(repo, remote, branch):
    cmd = ["git", "-C", repo, "pull", "--ff-only", remote, branch]
    return git_wrapper_standard_command(cmd, "pull")

def push(repo, remote, branch):
    cmd = ["git", "-C", repo, "push", remote, branch]
    return git_wrapper_standard_command(cmd, "push")

def fetch_all(repo):
    cmd = ["git", "-C", repo, "fetch", "--all"]
    return git_wrapper_standard_command(cmd, "fetch-all")

def fetch_multiple(repo, remotes):
    cmd = ["git", "-C", repo, "fetch", "--multiple"] + remotes
    return git_wrapper_standard_command(cmd, "fetch-multiple")

def submodule_add(repo_sub, repo_target):
    cmd = ["git", "-C", repo_target, "submodule", "add", repo_sub]
    return git_wrapper_standard_command(cmd, "submodule-add")

def puaq():
    print("Usage: %s repo [--commit]" % os.path.basename(__file__)) # mvtodo
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    repo = sys.argv[1]
    options = sys.argv[2:]

    print(options) # mvtodo: implement
