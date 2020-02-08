#!/usr/bin/env python3

import sys
import os
import shutil
import unittest

import git_test_fixture
import mvtools_test_fixture
import path_utils

import git_visitor_fetch

class GitVisitorFetchTest(unittest.TestCase):

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

        v, r = mvtools_test_fixture.makeAndGetTestFolder("git_visitor_fetch_test_base")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # test repos paths
        self.first_repo = path_utils.concat_path(self.test_dir, "first")
        self.second_repo = path_utils.concat_path(self.test_dir, "second")
        self.third_repo = path_utils.concat_path(self.test_dir, "third")

        # creates test repos
        v, r = git_test_fixture.git_initRepo(self.test_dir, "third", True)
        if not v:
            return v, r

        # clone third into second
        v, r = git_test_fixture.git_cloneRepo(self.third_repo, self.second_repo, "origin")
        if not v:
            return v, r

        # commit something onto second
        self.file1 = self.makeFilename()
        self.second_file1 = path_utils.concat_path(self.second_repo, self.file1)
        v, r = git_test_fixture.git_createAndCommit(self.second_repo, self.file1, self.makeContent(), "commit_msg")
        if not v:
            return v, r

        # clone third into first
        v, r = git_test_fixture.git_cloneRepo(self.third_repo, self.first_repo, "origin")
        if not v:
            return v, r

        # commit something onto first
        self.file2 = self.makeFilename()
        self.first_file2 = path_utils.concat_path(self.first_repo, self.file2)
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, self.file2, self.makeContent(), "commit_msg")
        if not v:
            return v, r

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testVisitorFetch(self):

        # create fourth  and fifth repos - clones of second and first, respectively
        fourth_repo = path_utils.concat_path(self.test_dir, "fourth")
        v, r = git_test_fixture.git_cloneRepo(self.second_repo, fourth_repo, "origin")
        if not v:
            self.fail(r)

        fifth_repo = path_utils.concat_path(self.test_dir, "fifth")
        v, r = git_test_fixture.git_cloneRepo(self.first_repo, fifth_repo, "origin")
        if not v:
            self.fail(r)

        # commit something else onto second
        file3 = self.makeFilename()
        v, r = git_test_fixture.git_createAndCommit(self.second_repo, file3, self.makeContent(), "commit_msg")
        if not v:
            self.fail(r)

        # commit something else onto first
        file4 = self.makeFilename()
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, file4, self.makeContent(), "commit_msg")
        if not v:
            self.fail(r)

        # call visitor_fetch on fourth and fifth
        repos = [fourth_repo, fifth_repo]
        opts = {"xor-remotename": "origin"}

        r = git_visitor_fetch.visitor_fetch(repos, opts)

        # validate it
        self.assertTrue(r)

        # merges after the fetch
        v, r = git_test_fixture.git_mergeWithRemote(fourth_repo, "origin", "master")
        if not v:
            self.fail(r)

        v, r = git_test_fixture.git_mergeWithRemote(fifth_repo, "origin", "master")
        if not v:
            self.fail(r)

        self.assertTrue(path_utils.concat_path(fourth_repo, file3) )
        self.assertTrue(path_utils.concat_path(fifth_repo, file4) )

if __name__ == '__main__':
    unittest.main()
