#!/usr/bin/env python3

import sys
import os
import shutil
import unittest

import git_test_fixture
import path_utils
import git_repo_query
import mvtools_test_fixture
import create_and_write_file

class GitRepoQueryTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("git_repo_query_test_base")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # test repos paths
        self.first_repo = path_utils.concat_path(self.test_dir, "first")
        self.second_repo = path_utils.concat_path(self.test_dir, "second")
        self.third_repo = path_utils.concat_path(self.test_dir, "third")

        self.fourth_notrepo = path_utils.concat_path(self.test_dir, "fourth")
        os.mkdir(self.fourth_notrepo)

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
        self.first_file1 = path_utils.concat_path(self.first_repo, "file1.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, path_utils.basename_filtered(self.first_file1), "file1-content1", "commit_msg_file1")
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
        shutil.rmtree(self.test_base_dir)

    def testIsGitWorkTree(self):
        self.assertTrue(git_repo_query.is_git_work_tree(self.first_repo))
        self.assertFalse(git_repo_query.is_git_work_tree(self.fourth_notrepo))

    def testGetRemotes(self):

        self.assertEqual(git_repo_query.get_remotes(self.fourth_notrepo), None)

        v, r = git_test_fixture.git_addRemote(self.first_repo, "latest-addition", self.third_repo)
        if not v:
            self.fail(r)

        ret = git_repo_query.get_remotes(self.first_repo)
        self.assertEqual(self.second_repo, ret["origin"]["fetch"])
        self.assertEqual(self.third_repo, ret["latest-addition"]["fetch"])

        ret = git_repo_query.get_remotes(self.fourth_notrepo)
        self.assertEqual(ret, None)

    def testGetBranches(self):

        self.assertEqual(git_repo_query.get_branches(self.fourth_notrepo), None)

        ret = git_repo_query.get_branches(self.first_repo)
        self.assertEqual(len(ret), 1)
        self.assertEqual(ret[0], "master")

        v, r = git_test_fixture.git_createAndSwitchBranch(self.first_repo, "new-branch")
        if not v:
            self.fail(r)

        ret = git_repo_query.get_branches(self.first_repo)
        self.assertEqual(len(ret), 2)
        self.assertTrue("master" in ret)
        self.assertTrue("new-branch" in ret)

    def testGetCurrentBranch(self):

        self.assertEqual(git_repo_query.get_current_branch(self.fourth_notrepo), None)

        self.assertEqual(git_repo_query.get_current_branch(self.first_repo), "master")

        v, r = git_test_fixture.git_createAndSwitchBranch(self.first_repo, "another-branch")
        if not v:
            self.fail(r)

        self.assertEqual(git_repo_query.get_current_branch(self.first_repo), "another-branch")

    def testGetStagedFiles(self):

        self.assertEqual(git_repo_query.get_staged_files(self.fourth_notrepo), None)

        self.assertEqual(git_repo_query.get_staged_files(self.first_repo), "")

        first_more1 = path_utils.concat_path(self.first_repo, "more1.txt")
        if not create_and_write_file.create_file_contents(first_more1, "more1-contents"):
            self.fail("Failed creating file %s" % first_more1)

        first_more2 = path_utils.concat_path(self.first_repo, "more2.txt")
        if not create_and_write_file.create_file_contents(first_more2, "more2-contents"):
            self.fail("Failed creating file %s" % first_more2)

        first_more3 = path_utils.concat_path(self.first_repo, "more3.txt")
        if not create_and_write_file.create_file_contents(first_more3, "more3-contents"):
            self.fail("Failed creating file %s" % first_more3)

        first_more4 = path_utils.concat_path(self.first_repo, "more4.txt")
        if not create_and_write_file.create_file_contents(first_more4, "more4-contents"):
            self.fail("Failed creating file %s" % first_more4)

        v, r = git_test_fixture.git_stage(self.first_repo, [first_more1])
        if not v:
            self.fail(r)

        self.assertEqual(git_repo_query.get_staged_files(self.first_repo), [first_more1])

        v, r = git_test_fixture.git_stage(self.first_repo, [first_more2, first_more3])
        if not v:
            self.fail(r)

        ret = git_repo_query.get_staged_files(self.first_repo)
        self.assertEqual(len(ret), 3)
        self.assertTrue(first_more1 in ret)
        self.assertTrue(first_more2 in ret)
        self.assertTrue(first_more3 in ret)

        v, r = git_test_fixture.git_stage(self.first_repo, None)
        if not v:
            self.fail(r)

        ret = git_repo_query.get_staged_files(self.first_repo)
        self.assertEqual(len(ret), 4)
        self.assertTrue(first_more1 in ret)
        self.assertTrue(first_more2 in ret)
        self.assertTrue(first_more3 in ret)
        self.assertTrue(first_more4 in ret)

    def testGetUnstagedFiles(self):

        self.assertEqual(git_repo_query.get_unstaged_files(self.fourth_notrepo), None)

        self.assertEqual(git_repo_query.get_unstaged_files(self.first_repo), "")

        first_more1 = path_utils.concat_path(self.first_repo, "more1.txt")
        if not create_and_write_file.create_file_contents(first_more1, "more1-contents"):
            self.fail("Failed creating file %s" % first_more1)

        first_more2 = path_utils.concat_path(self.first_repo, "more2.txt")
        if not create_and_write_file.create_file_contents(first_more2, "more2-contents"):
            self.fail("Failed creating file %s" % first_more2)

        ret = git_repo_query.get_unstaged_files(self.first_repo)
        self.assertEqual(len(ret), 2)
        self.assertTrue(first_more1 in ret)
        self.assertTrue(first_more2 in ret)

        v, r = git_test_fixture.git_stage(self.first_repo, [first_more1])
        if not v:
            self.fail(r)

        ret = git_repo_query.get_unstaged_files(self.first_repo)
        self.assertEqual(len(ret), 1)
        self.assertEqual(ret[0], first_more2)

if __name__ == '__main__':
    unittest.main()
