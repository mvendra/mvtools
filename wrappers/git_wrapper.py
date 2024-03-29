#!/usr/bin/env python3

import sys
import os

import path_utils
import generic_run

def git_wrapper_standard_command(cmd, cmd_name="git_wrapper_standard_command"):
    v, r = generic_run.run_cmd_simple(cmd)
    if not v:
        return False, "Failed calling %s: %s" % (cmd_name, r)
    return v, r

def git_wrapper_extended_command(cmd, cmd_name="git_wrapper_extended_command"):
    v, r = generic_run.run_cmd(cmd)
    if not v:
        return False, "Failed calling %s: %s" % (cmd_name, r)
    return True, (r.success, r.stdout, r.stderr)

def config(key, value=None, global_cfg=True):

    cmd = ["git", "config"]
    if global_cfg:
        cmd.append("--global")
    cmd.append(key)
    if value is not None:
        cmd.append(value)

    return git_wrapper_standard_command(cmd, "config")

def apply(repo, source_file):
    cmd = ["git", "-C", repo, "apply", source_file]
    return git_wrapper_standard_command(cmd, "apply")

def commit_direct(repo, params):
    if not isinstance(params, list):
        return False, "git_wrapper.commit_direct: params must be a list"
    if len(params) == 0:
        return False, "git_wrapper.commit_direct: nothing to do"
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

def clone_ext(repo_source, repo_target, remotename=None):
    cmd = ["git", "clone", repo_source, repo_target]
    if remotename is not None:
        cmd.append("-o")
        cmd.append(remotename)
    return git_wrapper_extended_command(cmd, "clone-ext")

def clone_bare(repo_source, repo_target):
    cmd = ["git", "clone", "--bare", repo_source, repo_target]
    return git_wrapper_standard_command(cmd, "clone-bare")

def stage(repo, file_list=None):

    add_list = []
    if file_list is None:
        add_list.append(".")
    else:
        if not isinstance(file_list, list):
            return False, "git_wrapper.stage: file_list must be a list"
        add_list = file_list

    for f in add_list:
        cmd = ["git", "-C", repo, "add", f]
        v, r = git_wrapper_standard_command(cmd, "stage")
        if not v:
            return v, r

    return True, "git_wrapper.stage: Al OK."

def diff(repo, file_list=None):
    cmd = ["git", "-C", repo, "diff", "--no-ext-diff"]
    if file_list is not None:
        if not isinstance(file_list, list):
            return False, "git_wrapper.diff: file_list must be a list"
        for f in file_list:
            cmd.append(f)
    return git_wrapper_standard_command(cmd, "diff")

def diff_indexed(repo, file_list):
    if file_list is None:
        return False, "git_wrapper.diff_indexed: file_list can't be None"
    if not isinstance(file_list, list):
        return False, "git_wrapper.diff_indexed: file_list must be a list"
    cmd = ["git", "-C", repo, "diff", "--no-ext-diff", "--"]
    for f in file_list:
        cmd.append(f)
    return git_wrapper_standard_command(cmd, "diff-indexed")

def diff_cached(repo, file_list=None):
    cmd = ["git", "-C", repo, "diff", "--no-ext-diff", "--cached"]
    if file_list is not None:
        if not isinstance(file_list, list):
            return False, "git_wrapper.diff_cached: file_list must be a list"
        for f in file_list:
            cmd.append(f)
    return git_wrapper_standard_command(cmd, "diff-cached")

def diff_cached_indexed(repo, file_list):
    if file_list is None:
        return False, "git_wrapper.diff_cached_indexed: file_list can't be None"
    if not isinstance(file_list, list):
        return False, "git_wrapper.diff_cached_indexed: file_list must be a list"
    cmd = ["git", "-C", repo, "diff", "--no-ext-diff", "--cached", "--"]
    for f in file_list:
        cmd.append(f)
    return git_wrapper_standard_command(cmd, "diff-cached-indexed")

def rev_parse_head(repo):
    cmd = ["git", "-C", repo, "rev-parse", "HEAD"]
    return git_wrapper_standard_command(cmd, "rev-parse-head")

def rev_parse_is_bare_repo(repo):
    cmd = ["git", "-C", repo, "rev-parse", "--is-bare-repository"]
    return git_wrapper_standard_command(cmd, "rev-parse")

def rev_parse_is_inside_work_tree(repo):
    cmd = ["git", "-C", repo, "rev-parse", "--is-inside-work-tree"]
    return git_wrapper_standard_command(cmd, "rev-parse")

def rev_parse_absolute_git_dir(repo):
    cmd = ["git", "-C", repo, "rev-parse", "--absolute-git-dir"]
    v, r = git_wrapper_standard_command(cmd, "rev-parse")
    if not v:
        return False, r
    return True, r.rstrip(os.linesep)

def ls_files(repo):
    cmd = ["git", "-C", repo, "ls-files", "--exclude-standard", "--others"]
    return git_wrapper_standard_command(cmd, "ls-files")

def ls_files_nullterm(repo):
    cmd = ["git", "-C", repo, "ls-files", "-z", "--exclude-standard", "--others"]
    return git_wrapper_standard_command(cmd, "ls-files-nullterm")

def stash(repo):
    cmd = ["git", "-C", repo, "stash"]
    return git_wrapper_standard_command(cmd, "stash")

def stash_list(repo):
    cmd = ["git", "-C", repo, "stash", "list"]
    return git_wrapper_standard_command(cmd, "stash-list")

def stash_show(repo, stash_name):
    cmd = ["git", "-C", repo, "stash", "show", stash_name]
    return git_wrapper_standard_command(cmd, "stash-show")

def stash_show_diff(repo, stash_name):
    cmd = ["git", "-C", repo, "stash", "show", "-p", "--no-ext-diff", stash_name]
    return git_wrapper_standard_command(cmd, "stash-show-diff")

def stash_clear(repo):
    cmd = ["git", "-C", repo, "stash", "clear"]
    return git_wrapper_standard_command(cmd, "stash-clear")

def stash_drop(repo, stash_name = None):
    cmd = ["git", "-C", repo, "stash", "drop"]
    if stash_name is not None:
        cmd.append(stash_name)
    return git_wrapper_standard_command(cmd, "stash-drop")

def stash_pop(repo):
    cmd = ["git", "-C", repo, "stash", "pop"]
    return git_wrapper_standard_command(cmd, "stash-pop")

def log_oneline(repo, limit=None):
    cmd = ["git", "-C", repo, "log", "--oneline"]
    if limit is not None:
        cmd.append("-n")
        cmd.append(str(limit))
    return git_wrapper_standard_command(cmd, "log-oneline")

def log(repo, limit=None):
    cmd = ["git", "-C", repo, "log"]
    if limit is not None:
        cmd.append("-n")
        cmd.append(str(limit))
    return git_wrapper_standard_command(cmd, "log")

def show(repo, params=[]):
    cmd = ["git", "-C", repo, "show"]
    for p in params:
        cmd.append(p)
    return git_wrapper_standard_command(cmd, "show")

def status(repo):
    cmd = ["git", "-C", repo, "status", "--porcelain=v1"]
    return git_wrapper_standard_command(cmd, "status")

def status_simple(repo):
    cmd = ["git", "-C", repo, "status", "-s"]
    return git_wrapper_standard_command(cmd, "status-simple")

def status_nullterm_porcelain_v1(repo):
    cmd = ["git", "-C", repo, "status", "-z", "--porcelain=v1"]
    return git_wrapper_standard_command(cmd, "porcelain-v1")

def remote_list(repo):
    cmd = ["git", "-C", repo, "remote", "-v"]
    return git_wrapper_standard_command(cmd, "remote-list")

def remote_add(repo, remotename, remotepath):
    cmd = ["git", "-C", repo, "remote", "add", remotename, remotepath]
    return git_wrapper_standard_command(cmd, "remote-add")

def remote_change_url(repo, remote, new_url):
    cmd = ["git", "-C", repo, "remote", "set-url", remote, new_url]
    return git_wrapper_standard_command(cmd, "remote-change-url")

def branch(repo, params=[]):
    if not isinstance(params, list):
        return False, "git_wrapper.branch: params must be a list"
    cmd = ["git", "-C", repo, "branch"]
    for p in params:
        cmd.append(p)
    return git_wrapper_standard_command(cmd, "branch")

def branch_create_and_switch(repo, branchname):
    cmd = ["git", "-C", repo, "checkout", "-B", branchname]
    return git_wrapper_standard_command(cmd, "branch-create-and-switch")

def checkout(repo, file_list=None):
    cmd = ["git", "-C", repo, "checkout"]
    if file_list is None:
        cmd.append(repo)
    else:
        for fl in file_list:
            cmd.append(fl)
    return git_wrapper_standard_command(cmd, "checkout")

def pull(repo, remote, branch):
    cmd = ["git", "-C", repo, "pull", "--ff-only", remote, branch]
    return git_wrapper_standard_command(cmd, "pull")

def pull_default(repo):
    cmd = ["git", "-C", repo, "pull", "--ff-only"]
    return git_wrapper_standard_command(cmd, "pull-default")

def push(repo, remote, branch):
    cmd = ["git", "-C", repo, "push", remote, branch]
    return git_wrapper_standard_command(cmd, "push")

def push_default(repo):
    cmd = ["git", "-C", repo, "push"]
    return git_wrapper_standard_command(cmd, "push-default")

def fetch_all(repo):
    cmd = ["git", "-C", repo, "fetch", "--all"]
    return git_wrapper_standard_command(cmd, "fetch-all")

def fetch_multiple(repo, remotes):
    if remotes is None:
        return False, "git_wrapper.fetch_multiple: remotes can't be None"
    if not isinstance(remotes, list):
        return False, "git_wrapper.fetch_multiple: remotes must be a list"
    cmd = ["git", "-C", repo, "fetch", "--multiple"] + remotes
    return git_wrapper_standard_command(cmd, "fetch-multiple")

def merge(repo, remotename, branchname):
    cmd = ["git", "-C", repo, "merge", "%s/%s" % (remotename, branchname)]
    return git_wrapper_standard_command(cmd, "merge")

def submodule_add(repo_sub, repo_target):
    cmd = ["git", "-C", repo_target, "submodule", "add", repo_sub]
    return git_wrapper_standard_command(cmd, "submodule-add")

def reset_head(repo, files=None):
    cmd = ["git", "-C", repo, "reset", "HEAD"]
    if files is not None:
        if not isinstance(files, list):
            return False, "git_wrapper.reset_head: files must be a list"
        for f in files:
            cmd.append(f)
    return git_wrapper_standard_command(cmd, "reset-head")

def reset_hard_head(repo, reset_range):
    cmd = ["git", "-C", repo, "reset", "--hard", ("HEAD~%d" % reset_range)]
    return git_wrapper_standard_command(cmd, "reset-hard-head")

def reset_soft_head(repo, reset_range):
    cmd = ["git", "-C", repo, "reset", "--soft", ("HEAD~%d" % reset_range)]
    return git_wrapper_standard_command(cmd, "reset-soft-head")

def puaq():
    print("Hello from %s" % path_utils.basename_filtered(__file__))

if __name__ == "__main__":
    puaq()
