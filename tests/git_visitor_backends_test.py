#!/usr/bin/env python3

import sys
import os
import shutil
import unittest

import generic_run

import git_pull
import git_push
import git_fetch
import git_remote

class GitVisitorBackendsTest(unittest.TestCase):

    def makeFilename(self):
        self.internal_counter += 1
        filename = "testfile_%s.txt" % self.internal_counter
        return filename

    def makeContent(self):
        self.internal_counter += 1
        content = "rubbish_content_%s" % self.internal_counter
        return content

    def git_initRepo(self, repo_base, repo_name, bare):
        bare_cmd = ""
        if bare:
            bare_cmd = " --bare"
        if not generic_run.run_cmd("git -C %s init %s%s" % (repo_base, repo_name, bare_cmd) ):
            self.fail("Git command failed. Can't proceed.")

    def git_cloneRepo(self, repo_source, repo_target, remotename):
        if not generic_run.run_cmd("git clone %s %s -o %s" % (repo_source, repo_target, remotename)):
            self.fail("Git command failed. Can't proceed.")

    def git_createAndCommit(self, repo, filename, content, commitmsg):
        if not generic_run.run_cmd("create_and_write_file.py %s %s" % (os.path.join(repo, filename), content) ):
            self.fail("create_and_write_file command failed. Can't proceed.")

        if not generic_run.run_cmd("git -C %s add ." % repo):
            self.fail("Git command failed. Can't proceed.")

        if not generic_run.run_cmd("git -C %s commit -m %s" % (repo, commitmsg) ):
            self.fail("Git command failed. Can't proceed.")

    def git_addRemote(self, repo, remotename, remotepath):
        if not generic_run.run_cmd("git -C %s remote add %s %s" % (repo, remotename, remotepath)):
            self.fail("Git command failed. Can't proceed.")

    def git_pushToRemote(self, repo, remotename, branchname):
        if not generic_run.run_cmd("git -C %s push %s %s" % (repo, remotename, branchname)):
            self.fail("Git command failed. Can't proceed.")

    def git_pullFromRemote(self, repo, remotename, branchname):
        if not generic_run.run_cmd("git -C %s pull %s %s" % (repo, remotename, branchname)):
            self.fail("Git command failed. Can't proceed.")

    def git_mergeWithRemote(self, repo, remotename, branchname):
        if not generic_run.run_cmd("git -C %s merge %s/%s" % (repo, remotename, branchname)):
            self.fail("Git command failed. Can't proceed.")

    def setUp(self):

        self.internal_counter = 0

        # must have a $home/nuke folder, for creating test repos
        self.nuke_dir = os.path.expanduser("~/nuke")
        if not os.path.exists(self.nuke_dir):
            self.fail("[%s] doesn't exist. Can't proceed." % self.nuke_dir)

        # must *not* have a $home/nuke/git_visitor_backends_test_base so it can be created - it will
        # be deleted after each test
        self.test_dir = os.path.join(self.nuke_dir, "git_visitor_backends_test_base")
        if os.path.exists(self.test_dir):
            self.fail("[%s] already exists. Can't proceed." % self.test_dir)

        os.mkdir(self.test_dir)
        self.first_repo = os.path.join(self.test_dir, "first")
        self.second_repo = os.path.join(self.test_dir, "second")
        self.third_repo = os.path.join(self.test_dir, "third")

        # creates test repos
        self.git_initRepo(self.test_dir, "second", True)
        self.git_cloneRepo(self.second_repo, self.first_repo, "origin")
        self.git_cloneRepo(self.second_repo, self.third_repo, "origin")

        # create a file with rubbish on first, and push it to its remote (second)
        self.first_repo_first_file = self.makeFilename()
        self.git_createAndCommit(self.first_repo, self.first_repo_first_file, self.makeContent(), "commit_msg")
        self.git_pushToRemote(self.first_repo, "origin", "master")

        # pull changes from first into third, through second
        self.git_pullFromRemote(self.third_repo, "origin", "master")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def testPull(self):

        # setup
        newfile = self.makeFilename()
        newfile_r1 = os.path.join(self.first_repo, newfile)
        self.git_createAndCommit(self.third_repo, newfile, self.makeContent(), "commit_msg")
        self.git_pushToRemote(self.third_repo, "origin", "master")

        # test
        remotes = {}
        remotes["origin"] = { "push": self.second_repo, "fetch": self.second_repo }
        branches = ["master"]

        # file must not pre-exist
        self.assertFalse(os.path.exists( newfile_r1 ))

        v, r = git_pull.do_pull(self.first_repo, remotes, branches)

        # must exist now because it was just pulled
        self.assertTrue(os.path.exists( newfile_r1 ))
        # operation must have succeded without any failures
        self.assertFalse(v)

    def testPush(self):

        # setup
        newfile = self.makeFilename()
        newfile_r1 = os.path.join(self.first_repo, newfile)
        self.git_createAndCommit(self.third_repo, newfile, self.makeContent(), "commit_msg")

        # test
        remotes = {}
        remotes["origin"] = { "push": self.second_repo, "fetch": self.second_repo }
        branches = ["master"]

        # file must not pre-exist
        self.assertFalse(os.path.exists( newfile_r1 ))

        v, r = git_push.do_push(self.third_repo, remotes, branches)

        # operation must have succeded without any failures
        self.assertFalse(v)
        # pull the file into first we just pushed from third
        self.git_pullFromRemote(self.first_repo, "origin", "master")
        # must exist now because it was just pulled
        self.assertTrue(os.path.exists( newfile_r1 ))

    def testFetch(self):

        # setup
        newfile = self.makeFilename()
        newfile_r1 = os.path.join(self.first_repo, newfile)
        self.git_createAndCommit(self.third_repo, newfile, self.makeContent(), "commit_msg")
        self.git_pushToRemote(self.third_repo, "origin", "master")

        # test
        remotes = {}
        remotes["origin"] = { "push": self.second_repo, "fetch": self.second_repo }
        branches = ["master"]

        # file must not pre-exist
        self.assertFalse(os.path.exists( newfile_r1 ))

        v, r = git_fetch.do_fetch(self.first_repo, remotes)

        # operation must have succeded without any failures
        self.assertFalse(v)

        # merges after the fetch
        self.git_mergeWithRemote(self.first_repo, "origin", "master")

        # must exist now because it was just pulled
        self.assertTrue(os.path.exists( newfile_r1 ))

    def testRemote(self):

        # setup
        remote = "origin"
        operation = ""
        fourth_repo = os.path.join(self.test_dir, "fourth")
        fifth_repo = os.path.join(self.test_dir, "fifth")
        self.git_initRepo(self.test_dir, "fourth", True)

        # fifth repo must not pre-exist
        self.assertFalse(os.path.exists(fifth_repo))

        v, r = git_remote.remote_change_url(self.first_repo, remote, operation, fourth_repo)

        # operation must have succeded without any failures
        self.assertFalse(v)

        # push to new remote
        self.git_pushToRemote(self.first_repo, "origin", "master")

        # clone fourth into fifth to check for repo1's contents
        self.git_cloneRepo(fourth_repo, fifth_repo, "origin")
        # file from repo1 must exist inside fifth repo
        self.assertTrue(os.path.exists( os.path.join(fifth_repo, self.first_repo_first_file) ))

if __name__ == '__main__':
    unittest.main()
