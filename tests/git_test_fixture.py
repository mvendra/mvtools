#!/usr/bin/env python3

import os
import generic_run
import path_utils

def git_initRepo(repo_base, repo_name, bare):
    bare_cmd = ""
    if bare:
        bare_cmd = " --bare"
    if not generic_run.run_cmd("git -C %s init %s%s" % (repo_base, repo_name, bare_cmd) ):
        return False, "Git command failed. Can't proceed."
    return True, ""

def git_cloneRepo(repo_source, repo_target, remotename):
    if not generic_run.run_cmd("git clone %s %s -o %s" % (repo_source, repo_target, remotename)):
        return False, "Git command failed. Can't proceed."
    return True, ""

def git_addSubmodule(repo_sub, repo_target):
    if not generic_run.run_cmd("git -C %s submodule add %s" % (repo_target, repo_sub) ):
        return False, "Git command failed. Can't proceed."
    return True, ""

def git_createAndCommit(repo, filename, content, commitmsg):
    if not generic_run.run_cmd("create_and_write_file.py %s %s" % (os.path.join(repo, path_utils.filter_join_abs(filename) ), content) ):
        return False, "create_and_write_file command failed. Can't proceed."

    if not generic_run.run_cmd("git -C %s add ." % repo):
        return False, "Git command failed. Can't proceed."

    if not generic_run.run_cmd("git -C %s commit -m %s" % (repo, commitmsg) ):
        return False, "Git command failed. Can't proceed."

    return True, ""

def git_addRemote(repo, remotename, remotepath):
    if not generic_run.run_cmd("git -C %s remote add %s %s" % (repo, remotename, remotepath)):
        return False, "Git command failed. Can't proceed."
    return True, ""

def git_pushToRemote(repo, remotename, branchname):
    if not generic_run.run_cmd("git -C %s push %s %s" % (repo, remotename, branchname)):
        return False, "Git command failed. Can't proceed."
    return True, ""

def git_pullFromRemote(repo, remotename, branchname):
    if not generic_run.run_cmd("git -C %s pull %s %s" % (repo, remotename, branchname)):
        return False, "Git command failed. Can't proceed."
    return True, ""

def git_mergeWithRemote(repo, remotename, branchname):
    if not generic_run.run_cmd("git -C %s merge %s/%s" % (repo, remotename, branchname)):
        return False, "Git command failed. Can't proceed."
    return True, ""
