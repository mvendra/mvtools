#!/usr/bin/env python3

import sys
import os
import shutil
import unittest

import git_test_fixture

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

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        self.internal_counter = 0

        # must have a $home/nuke folder, for creating test repos
        self.nuke_dir = os.path.expanduser("~/nuke")
        if not os.path.exists(self.nuke_dir):
            return False, "[%s] doesn't exist. Can't proceed." % self.nuke_dir

        # must *not* have a $home/nuke/git_visitor_backends_test_base so it can be created - it will
        # be deleted after each test
        self.test_dir = os.path.join(self.nuke_dir, "git_visitor_backends_test_base")
        if os.path.exists(self.test_dir):
            return False, "[%s] already exists. Can't proceed." % self.test_dir

        os.mkdir(self.test_dir)
        self.first_repo = os.path.join(self.test_dir, "first")
        self.second_repo = os.path.join(self.test_dir, "second")
        self.third_repo = os.path.join(self.test_dir, "third")

        # creates test repos
        v, r = git_test_fixture.git_initRepo(self.test_dir, "second", True)
        if not v:
            return v, r

        v, r = git_test_fixture.git_cloneRepo(self.second_repo, self.first_repo, "origin")
        if not v:
            return v, r

        v, r = git_test_fixture.git_cloneRepo(self.second_repo, self.third_repo, "origin")
        if not v:
            return v, r

        # create a file with rubbish on first, and push it to its remote (second)
        self.first_repo_first_file = self.makeFilename()
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, self.first_repo_first_file, self.makeContent(), "commit_msg")
        if not v:
            return v, r

        v, r = git_test_fixture.git_pushToRemote(self.first_repo, "origin", "master")
        if not v:
            return v, r

        # pull changes from first into third, through second
        v, r = git_test_fixture.git_pullFromRemote(self.third_repo, "origin", "master")
        if not v:
            return v, r

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def testPull(self):

        # setup
        newfile = self.makeFilename()
        newfile_r1 = os.path.join(self.first_repo, newfile)

        v, r = git_test_fixture.git_createAndCommit(self.third_repo, newfile, self.makeContent(), "commit_msg")
        if not v:
            self.fail(r)

        v, r = git_test_fixture.git_pushToRemote(self.third_repo, "origin", "master")
        if not v:
            self.fail(r)

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

        v, r = git_test_fixture.git_createAndCommit(self.third_repo, newfile, self.makeContent(), "commit_msg")
        if not v:
            self.fail(r)

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
        v, r = git_test_fixture.git_pullFromRemote(self.first_repo, "origin", "master")
        if not v:
            self.fail(r)

        # must exist now because it was just pulled
        self.assertTrue(os.path.exists( newfile_r1 ))

    def testFetch(self):

        # setup
        newfile = self.makeFilename()
        newfile_r1 = os.path.join(self.first_repo, newfile)

        v, r = git_test_fixture.git_createAndCommit(self.third_repo, newfile, self.makeContent(), "commit_msg")
        if not v:
            self.fail(r)

        v, r = git_test_fixture.git_pushToRemote(self.third_repo, "origin", "master")
        if not v:
            self.fail(r)

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
        v, r = git_test_fixture.git_mergeWithRemote(self.first_repo, "origin", "master")
        if not v:
            self.fail(r)

        # must exist now because it was just pulled
        self.assertTrue(os.path.exists( newfile_r1 ))

    def testRemote(self):

        # setup
        remote = "origin"
        operation = ""
        fourth_repo = os.path.join(self.test_dir, "fourth")
        fifth_repo = os.path.join(self.test_dir, "fifth")

        v, r = git_test_fixture.git_initRepo(self.test_dir, "fourth", True)
        if not v:
            self.fail(r)

        # fifth repo must not pre-exist
        self.assertFalse(os.path.exists(fifth_repo))

        v, r = git_remote.remote_change_url(self.first_repo, remote, operation, fourth_repo)

        # operation must have succeded without any failures
        self.assertFalse(v)

        # push to new remote
        v, r = git_test_fixture.git_pushToRemote(self.first_repo, "origin", "master")
        if not v:
            self.fail(r)

        # clone fourth into fifth to check for repo1's contents
        v, r = git_test_fixture.git_cloneRepo(fourth_repo, fifth_repo, "origin")
        if not v:
            self.fail(r)

        # file from repo1 must exist inside fifth repo
        self.assertTrue(os.path.exists( os.path.join(fifth_repo, self.first_repo_first_file) ))

if __name__ == '__main__':
    unittest.main()
