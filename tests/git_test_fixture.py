#!/usr/bin/env python3

import os
import generic_run

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

def git_createAndCommit(repo, filename, content, commitmsg):
    if not generic_run.run_cmd("create_and_write_file.py %s %s" % (os.path.join(repo, filename), content) ):
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

def gv_makeAndGetTestFolder(additional_folder):

    nuke_dir = os.path.expanduser("~/nuke")
    # must have a $home/nuke folder, for creating test repos
    if not os.path.exists(nuke_dir):
        return False, "[%s] doesn't exist. Can't proceed." % nuke_dir

    # general layer for git_visitor tests
    test_dir_pre = os.path.join(nuke_dir, "git_visitor_tests")
    if os.path.exists(test_dir_pre):
        return False, "[%s] already exists. Can't proceed." % test_dir_pre
    os.mkdir(test_dir_pre)

    # optionally add another layer (specific layer for each test case)
    final_dir = test_dir_pre
    if additional_folder is not None:
        final_dir = os.path.join(test_dir_pre, additional_folder)
        os.mkdir(final_dir)

    return True, (test_dir_pre, final_dir)
