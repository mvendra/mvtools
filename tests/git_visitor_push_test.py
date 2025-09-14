#!/usr/bin/env python

import sys
import os
import shutil
import unittest

import git_test_fixture
import git_wrapper
import mvtools_test_fixture
import path_utils

import git_visitor_push

class GitVisitorPushTest(unittest.TestCase):

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

        v, r = mvtools_test_fixture.makeAndGetTestFolder("git_visitor_push_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # test repos paths
        self.first_repo = path_utils.concat_path(self.test_dir, "first")
        self.second_repo = path_utils.concat_path(self.test_dir, "second")

        # creates test repos
        v, r = git_wrapper.init(self.test_dir, "first", True)
        if not v:
            return v, r

        # creates test repos
        v, r = git_wrapper.init(self.test_dir, "second", True)
        if not v:
            return v, r

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testVisitorPush(self):

        # clone first and second into third and fourth, respectively
        third_repo = path_utils.concat_path(self.test_dir, "third")
        v, r = git_wrapper.clone(self.first_repo, third_repo, "origin")
        if not v:
            self.fail(r)

        fourth_repo = path_utils.concat_path(self.test_dir, "fourth")
        v, r = git_wrapper.clone(self.second_repo, fourth_repo, "origin")
        if not v:
            self.fail(r)

        # commit new file onto third
        file1 = self.makeFilename()
        v, r = git_test_fixture.git_createAndCommit(third_repo, file1, self.makeContent(), "commit_msg")
        if not v:
            self.fail(r)

        # commit new file onto fourth
        file2 = self.makeFilename()
        v, r = git_test_fixture.git_createAndCommit(fourth_repo, file2, self.makeContent(), "commit_msg")
        if not v:
            self.fail(r)

        # call visitor_push on third and fourth
        repos = [third_repo, fourth_repo]
        opts = {"xor-remotename": "origin"}

        r = git_visitor_push.visitor_push(repos, opts)

        self.assertTrue(r)

        # checkout fifth and sixth, from first and second, and check if newfiles were pushed (from 3rd and 4th)
        fifth_repo = path_utils.concat_path(self.test_dir, "fifth")
        fifth_file1 = path_utils.concat_path(fifth_repo, file1)
        v, r = git_wrapper.clone(self.first_repo, fifth_repo, "origin")
        if not v:
            self.fail(r)

        sixth_repo = path_utils.concat_path(self.test_dir, "sixth")
        sixth_file2 = path_utils.concat_path(sixth_repo, file2)
        v, r = git_wrapper.clone(self.second_repo, sixth_repo, "origin")
        if not v:
            self.fail(r)

        self.assertTrue(os.path.exists(fifth_file1))
        self.assertTrue(os.path.exists(sixth_file2))

if __name__ == "__main__":
    unittest.main()
