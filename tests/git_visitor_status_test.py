#!/usr/bin/env python3

import sys
import os
import shutil
import unittest

import git_test_fixture
import mvtools_test_fixture

import git_visitor_status

class GitVisitorStatusTest(unittest.TestCase):

    def makeFilename(self):
        self.internal_counter += 1
        filename = "testfile_%s.txt" % self.internal_counter
        return filename

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        self.internal_counter = 0

        v, r = mvtools_test_fixture.makeAndGetTestFolder("git_visitor_status_test_base")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # test repos paths
        self.first_repo = os.path.join(self.test_dir, "first")
        self.second_repo = os.path.join(self.test_dir, "second")
        self.third_repo = os.path.join(self.test_dir, "third")

        # creates test repos
        v, r = git_test_fixture.git_initRepo(self.test_dir, "first", False)
        if not v:
            return v, r

        v, r = git_test_fixture.git_initRepo(self.test_dir, "second", False)
        if not v:
            return v, r

        v, r = git_test_fixture.git_initRepo(self.test_dir, "third", False)
        if not v:
            return v, r

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testVisitorStatus(self):

        repos = [self.first_repo, self.second_repo, self.third_repo]
        opts = {}

        r = git_visitor_status.visitor_status(repos, opts)
        self.assertTrue(r)

if __name__ == '__main__':
    unittest.main()
