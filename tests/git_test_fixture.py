#!/usr/bin/env python3

import os
import generic_run
import path_utils

def git_initRepo(repo_base, repo_name, bare):
    cmd = ["git", "-C", repo_base, "init", repo_name]
    if bare:
        cmd.append("--bare")
    v, r = generic_run.run_cmd_simple(cmd)
    if not v:
        return False, "Git command failed. Can't proceed: %s" % r
    return True, ""

def git_cloneRepo(repo_source, repo_target, remotename):
    v, r = generic_run.run_cmd_simple(["git", "clone", repo_source, repo_target, "-o", remotename])
    if not v:
        return False, "Git command failed. Can't proceed: %s" % r
    return True, ""

def git_addSubmodule(repo_sub, repo_target):
    v, r = generic_run.run_cmd_simple(["git", "-C", repo_target, "submodule", "add", repo_sub])
    if not v:
        return False, "Git command failed. Can't proceed: %s" % r
    return True, ""

def git_createAndCommit(repo, filename, content, commitmsg):
    v, r = generic_run.run_cmd_simple(["create_and_write_file.py", path_utils.concat_path(repo, filename), content])
    if not v:
        return False, "create_and_write_file command failed. Can't proceed: %s" % r

    v, r = git_stage(repo) # mvtodo: use git_wrapper
    if not v:
        return v, r

    return git_commit(repo, commitmsg) # mvtodo: use git_wrapper

def git_stage(repo, file_list=None):

    add_list = []
    if file_list is None:
        add_list.append(".")
    else:
        add_list = file_list

    for f in add_list:
        v, r = generic_run.run_cmd_simple(["git", "-C", repo, "add", f])
        if not v:
            return False, "Git command failed. Can't proceed: %s" % r

    return True, ""

def git_commit(repo, commitmsg):
    v, r = generic_run.run_cmd_simple(["git", "-C", repo, "commit", "-m", commitmsg])
    if not v:
        return False, "Git command failed. Can't proceed: %s" % r
    return True, ""

def git_stash(repo):
    v, r = generic_run.run_cmd_simple(["git", "-C", repo, "stash"])
    if not v:
        return False, "Git command failed. Can't proceed: %s" % r
    return True, ""

def git_addRemote(repo, remotename, remotepath):
    v, r = generic_run.run_cmd_simple(["git", "-C", repo, "remote", "add", remotename, remotepath])
    if not v:
        return False, "Git command failed. Can't proceed: %s" % r
    return True, ""

def git_createAndSwitchBranch(repo, branchname):
    v, r = generic_run.run_cmd_simple(["git", "-C", repo, "checkout", "-B", branchname])
    if not v:
        return False, "Git command failed. Can't proceed: %s" % r
    return True, ""

def git_pushToRemote(repo, remotename, branchname):
    v, r = generic_run.run_cmd_simple(["git", "-C", repo, "push", remotename, branchname])
    if not v:
        return False, "Git command failed. Can't proceed: %s" % r
    return True, ""

def git_pullFromRemote(repo, remotename, branchname):
    v, r = generic_run.run_cmd_simple(["git", "-C", repo, "pull", remotename, branchname])
    if not v:
        return False, "Git command failed. Can't proceed: %s" % r
    return True, ""

def git_mergeWithRemote(repo, remotename, branchname):
    v, r = generic_run.run_cmd_simple(["git", "-C", repo, "merge", "%s/%s" % (remotename, branchname)])
    if not v:
        return False, "Git command failed. Can't proceed: %s" % r
    return True, ""
