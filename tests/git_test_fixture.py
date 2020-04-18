#!/usr/bin/env python3

import os
import generic_run
import path_utils

def git_initRepo(repo_base, repo_name, bare):
    cmd = ["git", "-C", repo_base, "init", repo_name]
    if bare:
        cmd.append("--bare")
    if not generic_run.run_cmd_l(cmd):
        return False, "Git command failed. Can't proceed."
    return True, ""

def git_cloneRepo(repo_source, repo_target, remotename):
    if not generic_run.run_cmd_l(["git", "clone", repo_source, repo_target, "-o", remotename]):
        return False, "Git command failed. Can't proceed."
    return True, ""

def git_addSubmodule(repo_sub, repo_target):
    if not generic_run.run_cmd_l(["git", "-C", repo_target, "submodule", "add", repo_sub]):
        return False, "Git command failed. Can't proceed."
    return True, ""

def git_createAndCommit(repo, filename, content, commitmsg):
    if not generic_run.run_cmd_l(["create_and_write_file.py", path_utils.concat_path(repo, filename), content]):
        return False, "create_and_write_file command failed. Can't proceed."

    v, r = git_stage(repo)
    if not v:
        return v, r

    return git_commit(repo, commitmsg)

def git_stage(repo, file_list=None):

    add_list = []
    if file_list is None:
        add_list.append(".")
    else:
        add_list = file_list

    for f in add_list:
        if not generic_run.run_cmd_l(["git", "-C", repo, "add", f]):
            return False, "Git command failed. Can't proceed."

    return True, ""

def git_commit(repo, commitmsg):
    if not generic_run.run_cmd_l(["git", "-C", repo, "commit", "-m", commitmsg]):
        return False, "Git command failed. Can't proceed."
    return True, ""

def git_stash(repo):
    if not generic_run.run_cmd_l(["git", "-C", repo, "stash"]):
        return False, "Git command failed. Can't proceed."
    return True, ""

def git_addRemote(repo, remotename, remotepath):
    if not generic_run.run_cmd_l(["git", "-C", repo, "remote", "add", remotename, remotepath]):
        return False, "Git command failed. Can't proceed."
    return True, ""

def git_pushToRemote(repo, remotename, branchname):
    if not generic_run.run_cmd_l(["git", "-C", repo, "push", remotename, branchname]):
        return False, "Git command failed. Can't proceed."
    return True, ""

def git_pullFromRemote(repo, remotename, branchname):
    if not generic_run.run_cmd_l(["git", "-C", repo, "pull", remotename, branchname]):
        return False, "Git command failed. Can't proceed."
    return True, ""

def git_mergeWithRemote(repo, remotename, branchname):
    if not generic_run.run_cmd_l(["git", "-C", repo, "merge", "%s/%s" % (remotename, branchname)]):
        return False, "Git command failed. Can't proceed."
    return True, ""
