#!/usr/bin/env python3

import sys
import os
import shutil
import unittest

import git_test_fixture
import git_wrapper
import mvtools_test_fixture
import path_utils

import git_sub_push

class GitSubPushTest(unittest.TestCase):

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

        v, r = mvtools_test_fixture.makeAndGetTestFolder("git_sub_push_test_base")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # test repos paths
        self.first_repo = path_utils.concat_path(self.test_dir, "first")
        self.second_repo = path_utils.concat_path(self.test_dir, "second")
        self.third_repo = path_utils.concat_path(self.test_dir, "third")
        self.fourth_repo = path_utils.concat_path(self.test_dir, "fourth")

        # creates test repos
        v, r = git_wrapper.init(self.test_dir, "first", True)
        if not v:
            return v, r

        v, r = git_wrapper.init(self.test_dir, "second", True)
        if not v:
            return v, r

        # clone third and fourth from first and second, respectively
        v, r = git_wrapper.clone(self.first_repo, self.third_repo, "origin")
        if not v:
            return v, r

        v, r = git_wrapper.clone(self.second_repo, self.fourth_repo, "origin")
        if not v:
            return v, r

        # commit something onto third
        self.file1 = self.makeFilename()
        v, r = git_test_fixture.git_createAndCommit(self.third_repo, self.file1, self.makeContent(), "commit_msg")
        if not v:
            return v, r

        # push third
        v, r = git_wrapper.push(self.third_repo, "origin", "master")
        if not v:
            return v, r

        # commit something onto fourth
        self.file2 = self.makeFilename()
        v, r = git_test_fixture.git_createAndCommit(self.fourth_repo, self.file2, self.makeContent(), "commit_msg")
        if not v:
            return v, r

        # push fourth
        v, r = git_wrapper.push(self.fourth_repo, "origin", "master")
        if not v:
            return v, r

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testSubPush(self):

        # add first as submodule of third
        sub3_first = path_utils.concat_path(self.third_repo, "first")
        v, r = git_wrapper.submodule_add(self.first_repo, self.third_repo)
        if not v:
            self.fail(r)

        # commit something into first (sub of third)
        file3 = self.makeFilename()
        v, r = git_test_fixture.git_createAndCommit(sub3_first, file3, self.makeContent(), "commit_msg")
        if not v:
            self.fail(r)

        # call git sub push on third (to push first-sub thru third)
        git_sub_push.push_subs(self.third_repo)

        # clone fifth from first
        fifth_repo = path_utils.concat_path(self.test_dir, "fifth")
        v, r = git_wrapper.clone(self.first_repo, fifth_repo, "origin")
        if not v:
            self.fail(r)

        # validate it
        fifth_file3 = path_utils.concat_path( fifth_repo, file3)
        self.assertTrue( os.path.exists(fifth_file3) )

if __name__ == '__main__':
    unittest.main()
