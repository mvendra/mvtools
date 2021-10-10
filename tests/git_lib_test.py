#!/usr/bin/env python3

import sys
import os
import shutil
import unittest

import mvtools_test_fixture
import git_test_fixture
import create_and_write_file
import path_utils

import git_wrapper
import collect_git_patch
import git_lib

class GitLibTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("git_lib_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # test repos paths
        self.first_repo = path_utils.concat_path(self.test_dir, "first")
        self.second_repo = path_utils.concat_path(self.test_dir, "second")
        self.third_repo = path_utils.concat_path(self.test_dir, "third")

        self.nonexistent_repo = path_utils.concat_path(self.test_dir, "nonexistent")

        self.fourth_notrepo = path_utils.concat_path(self.test_dir, "fourth")
        os.mkdir(self.fourth_notrepo)

        self.fifth_repo = path_utils.concat_path(self.test_dir, "fifth")

        self.storage_path = path_utils.concat_path(self.test_dir, "storage_path")
        os.mkdir(self.storage_path)

        # creates test repos
        v, r = git_wrapper.init(self.test_dir, "second", True)
        if not v:
            return v, r

        v, r = git_wrapper.clone(self.second_repo, self.first_repo, "origin")
        if not v:
            return v, r

        v, r = git_wrapper.clone(self.second_repo, self.third_repo, "origin")
        if not v:
            return v, r

        v, r = git_wrapper.init(self.test_dir, "fifth", False)
        if not v:
            return v, r

        # create a file with rubbish on first, and push it to its remote (second)
        self.first_file1 = path_utils.concat_path(self.first_repo, "file1.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, path_utils.basename_filtered(self.first_file1), "file1-content1", "commit_msg_file1")
        if not v:
            return v, r

        v, r = git_wrapper.push(self.first_repo, "origin", "master")
        if not v:
            return v, r

        # pull changes from first into third, through second
        v, r = git_wrapper.pull(self.third_repo, "origin", "master")
        if not v:
            return v, r

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testHelperFunctions(self):
        self.assertEqual(git_lib.get_stash_name("stash@{0}: WIP on master: a44cc87 upd"), "stash@{0}")
        self.assertEqual(git_lib.get_stash_name(""), None)
        self.assertEqual(git_lib.get_stash_name(None), None)

        self.assertEqual(git_lib.get_prev_hash("a44cc87 (HEAD -> master) upd"), "a44cc87")
        self.assertEqual(git_lib.get_prev_hash(""), None)
        self.assertEqual(git_lib.get_prev_hash(None), None)

    def testGetRemotes(self):

        v, r = git_lib.get_remotes(self.fourth_notrepo)
        self.assertFalse(v)

        v, r = git_wrapper.remote_add(self.first_repo, "latest-addition", self.third_repo)
        self.assertTrue(v)

        v, r = git_lib.get_remotes(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(self.second_repo, r["origin"]["fetch"])
        self.assertEqual(self.third_repo, r["latest-addition"]["fetch"])

        v, r = git_wrapper.remote_add(self.first_repo, "latest-addition", self.third_repo)
        self.assertFalse(v) # disallow duplicates

        v, r = git_wrapper.remote_add(self.first_repo, "リモート", self.third_repo)
        self.assertTrue(v)

        v, r = git_lib.get_remotes(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(self.third_repo, r["リモート"]["fetch"])

    def testGetRemotesRelativePath(self):

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)

            v, r = git_lib.get_remotes("./fourth")
            self.assertFalse(v)

            v, r = git_wrapper.remote_add(self.first_repo, "latest-addition", self.third_repo)
            self.assertTrue(v)

            v, r = git_lib.get_remotes("./first")
            self.assertTrue(v)
            self.assertEqual(self.second_repo, r["origin"]["fetch"])
            self.assertEqual(self.third_repo, r["latest-addition"]["fetch"])

            v, r = git_wrapper.remote_add(self.first_repo, "latest-addition", self.third_repo)
            self.assertFalse(v) # disallow duplicates

            v, r = git_wrapper.remote_add(self.first_repo, "リモート", self.third_repo)
            self.assertTrue(v)

            v, r = git_lib.get_remotes("./first")
            self.assertTrue(v)
            self.assertEqual(self.third_repo, r["リモート"]["fetch"])

        finally:
            os.chdir(saved_wd)

    def testGetBranches(self):

        v, r = git_lib.get_branches(self.fifth_repo)
        self.assertTrue(v)
        self.assertEqual(r, [])
        v, r = git_lib.get_branches(self.fourth_notrepo)
        self.assertFalse(v)

        v, r = git_lib.get_branches(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0], "master")

        v, r = git_wrapper.branch_create_and_switch(self.first_repo, "new-branch")
        self.assertTrue(v)

        v, r = git_lib.get_branches(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertTrue("master" in r)
        self.assertTrue("new-branch" in r)

        v, r = git_wrapper.branch_create_and_switch(self.first_repo, "ブランチ")
        self.assertTrue(v)

        v, r = git_lib.get_branches(self.first_repo)
        self.assertTrue(v)
        self.assertTrue("ブランチ" in r)

    def testGetBranchesRelativePath(self):

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)

            v, r = git_lib.get_branches("./fifth")
            self.assertTrue(v)
            self.assertEqual(r, [])
            v, r = git_lib.get_branches("./fourth")
            self.assertFalse(v)

            v, r = git_lib.get_branches("./first")
            self.assertTrue(v)
            self.assertEqual(len(r), 1)
            self.assertEqual(r[0], "master")

            v, r = git_wrapper.branch_create_and_switch(self.first_repo, "new-branch")
            self.assertTrue(v)

            v, r = git_lib.get_branches("./first")
            self.assertTrue(v)
            self.assertEqual(len(r), 2)
            self.assertTrue("master" in r)
            self.assertTrue("new-branch" in r)

            v, r = git_wrapper.branch_create_and_switch(self.first_repo, "ブランチ")
            self.assertTrue(v)

            v, r = git_lib.get_branches("./first")
            self.assertTrue(v)
            self.assertTrue("ブランチ" in r)

        finally:
            os.chdir(saved_wd)

    def testGetCurrentBranch(self):

        v, r = git_lib.get_current_branch(self.fifth_repo)
        self.assertTrue(v)
        self.assertEqual(r, None)

        v, r = git_lib.get_current_branch(self.fourth_notrepo)
        self.assertFalse(v)
        self.assertNotEqual(r, None)

        v, r = git_lib.get_current_branch(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(r, "master")

        v, r = git_wrapper.branch_create_and_switch(self.first_repo, "another-branch")
        self.assertTrue(v)

        v, r = git_lib.get_current_branch(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(r, "another-branch")

    def testGetCurrentBranchRelativePath(self):

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)

            v, r = git_lib.get_current_branch("./fifth")
            self.assertTrue(v)
            self.assertEqual(r, None)

            v, r = git_lib.get_current_branch("./fourth")
            self.assertFalse(v)
            self.assertNotEqual(r, None)

            v, r = git_lib.get_current_branch("./first")
            self.assertTrue(v)
            self.assertEqual(r, "master")

            v, r = git_wrapper.branch_create_and_switch(self.first_repo, "another-branch")
            self.assertTrue(v)

            v, r = git_lib.get_current_branch("./first")
            self.assertTrue(v)
            self.assertEqual(r, "another-branch")

        finally:
            os.chdir(saved_wd)

    def testGetModifiedFiles(self):

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v and r)

        first_more1 = path_utils.concat_path(self.first_repo, "more1.txt")
        if not create_and_write_file.create_file_contents(first_more1, "more1-contents"):
            self.fail("Failed creating file %s" % first_more1)

        first_more2 = path_utils.concat_path(self.first_repo, "more2.txt")
        if not create_and_write_file.create_file_contents(first_more2, "more2-contents"):
            self.fail("Failed creating file %s" % first_more2)

        first_more3 = path_utils.concat_path(self.first_repo, "more3.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, path_utils.basename_filtered(first_more3), "file3-content3", "commit_msg_file3")
        self.assertTrue(v)

        v, r = git_wrapper.stage(self.first_repo, [first_more1])
        if not v:
            self.fail(r)

        with open(self.first_file1, "a") as f:
            f.write("actual modification")

        v, r = git_wrapper.stage(self.first_repo, [self.first_file1])
        if not v:
            self.fail(r)

        with open(first_more3, "a") as f:
            f.write("actual modification, again")

        v, r = git_lib.get_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(r, [first_more3])

    def testGetModifiedFilesRelativePath(self):

        sub1 = path_utils.concat_path(self.test_dir, "sub1")
        self.assertFalse(os.path.exists(sub1))
        os.mkdir(sub1)
        self.assertTrue(os.path.exists(sub1))

        sub1_testrepo = path_utils.concat_path(sub1, "testrepo")
        v, r = git_wrapper.init(sub1, "testrepo", False)
        self.assertTrue(v)
        self.assertTrue(os.path.exists(sub1_testrepo))

        testrepo_file1 = path_utils.concat_path(sub1_testrepo, "file1.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file1), "file1-content1", "commit_msg_file1")
        self.assertTrue(v)

        testrepo_file2 = path_utils.concat_path(sub1_testrepo, "file2.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file2), "file2-content1", "commit_msg_file2")
        self.assertTrue(v)

        testrepo_file3 = path_utils.concat_path(sub1_testrepo, "file3.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file3), "file3-content1", "commit_msg_file3")
        self.assertTrue(v)

        sub1_testrepo_sub2 = path_utils.concat_path(sub1_testrepo, "sub2")
        os.mkdir(sub1_testrepo_sub2)
        sub1_testrepo_sub3 = path_utils.concat_path(sub1_testrepo, "sub3")
        os.symlink(sub1_testrepo_sub2, sub1_testrepo_sub3)

        sub1_testrepo_sub2_file4 = path_utils.concat_path(sub1_testrepo_sub2, "file4.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo_sub2, path_utils.basename_filtered(sub1_testrepo_sub2_file4), "file4-content1", "commit_msg_file4")
        self.assertTrue(v)
        sub1_testrepo_sub3_file4 = path_utils.concat_path(sub1_testrepo_sub3, "file4.txt")

        self.assertTrue(os.path.exists(sub1_testrepo_sub2_file4))
        self.assertTrue(os.path.exists(sub1_testrepo_sub3_file4))

        with open(testrepo_file1, "a") as f:
            f.write("additional content f1")

        with open(testrepo_file3, "a") as f:
            f.write("additional content f3")

        with open(sub1_testrepo_sub3_file4, "a") as f:
            f.write("additional content f4")

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            v, r = git_lib.get_modified_files("./sub1/testrepo")
            self.assertTrue(v)
            self.assertTrue(testrepo_file1 in r)
            self.assertFalse(testrepo_file2 in r)
            self.assertTrue(testrepo_file3 in r)
            self.assertTrue(sub1_testrepo_sub2_file4 in r)
            self.assertFalse(sub1_testrepo_sub3_file4 in r) # git resolves symlinks
        finally:
            os.chdir(saved_wd)

    def testGetModifiedFilesRelativePathSymlinkRepo(self):

        sub2 = path_utils.concat_path(self.test_dir, "sub2")
        self.assertFalse(os.path.exists(sub2))
        os.mkdir(sub2)
        self.assertTrue(os.path.exists(sub2))

        sub1 = path_utils.concat_path(self.test_dir, "sub1")
        self.assertFalse(os.path.exists(sub1))
        os.symlink(sub2, sub1)
        self.assertTrue(os.path.exists(sub1))

        sub1_testrepo = path_utils.concat_path(sub1, "testrepo")
        v, r = git_wrapper.init(sub1, "testrepo", False)
        self.assertTrue(v)
        self.assertTrue(os.path.exists(sub1_testrepo))

        testrepo_file1 = path_utils.concat_path(sub1_testrepo, "file1.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file1), "file1-content1", "commit_msg_file1")
        self.assertTrue(v)

        testrepo_file2 = path_utils.concat_path(sub1_testrepo, "file2.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file2), "file2-content1", "commit_msg_file2")
        self.assertTrue(v)

        testrepo_file3 = path_utils.concat_path(sub1_testrepo, "file3.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file3), "file3-content1", "commit_msg_file3")
        self.assertTrue(v)

        sub1_testrepo_sub2 = path_utils.concat_path(sub1_testrepo, "sub2")
        os.mkdir(sub1_testrepo_sub2)
        sub1_testrepo_sub3 = path_utils.concat_path(sub1_testrepo, "sub3")
        os.symlink(sub1_testrepo_sub2, sub1_testrepo_sub3)

        sub1_testrepo_sub2_file4 = path_utils.concat_path(sub1_testrepo_sub2, "file4.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo_sub2, path_utils.basename_filtered(sub1_testrepo_sub2_file4), "file4-content1", "commit_msg_file4")
        self.assertTrue(v)
        sub1_testrepo_sub3_file4 = path_utils.concat_path(sub1_testrepo_sub3, "file4.txt")

        self.assertTrue(os.path.exists(sub1_testrepo_sub2_file4))
        self.assertTrue(os.path.exists(sub1_testrepo_sub3_file4))

        with open(testrepo_file1, "a") as f:
            f.write("additional content f1")

        with open(testrepo_file3, "a") as f:
            f.write("additional content f3")

        with open(sub1_testrepo_sub3_file4, "a") as f:
            f.write("additional content f4")

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            v, r = git_lib.get_modified_files("./sub1/testrepo")
            self.assertTrue(v)
            self.assertTrue(testrepo_file1 in r)
            self.assertFalse(testrepo_file2 in r)
            self.assertTrue(testrepo_file3 in r)
            self.assertTrue(sub1_testrepo_sub2_file4 in r)
            self.assertFalse(sub1_testrepo_sub3_file4 in r) # git resolves symlinks
        finally:
            os.chdir(saved_wd)

    def testGetStagedFiles(self):

        v, r = git_lib.get_staged_files(self.fourth_notrepo)
        self.assertFalse(v)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(r, [])

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

        first_more5 = path_utils.concat_path(self.first_repo, "アーカイブ.txt")
        if not create_and_write_file.create_file_contents(first_more5, "アーカイブ-contents"):
            self.fail("Failed creating file %s" % first_more5)

        v, r = git_wrapper.stage(self.first_repo, [first_more1])
        self.assertTrue(v)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(r, [first_more1])

        v, r = git_wrapper.stage(self.first_repo, [first_more2, first_more3])
        self.assertTrue(v)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 3)
        self.assertTrue(first_more1 in r)
        self.assertTrue(first_more2 in r)
        self.assertTrue(first_more3 in r)

        with open(self.first_file1, "a") as f:
            f.write("additional contents")

        v, r = git_wrapper.stage(self.first_repo, None)
        self.assertTrue(v)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)

        self.assertEqual(len(r), 6)
        self.assertTrue(self.first_file1 in r)
        self.assertTrue(first_more1 in r)
        self.assertTrue(first_more2 in r)
        self.assertTrue(first_more3 in r)
        self.assertTrue(first_more4 in r)
        #self.assertTrue(first_more5 in r) # mvtodo: might require extra system config or ...

    def testGetStagedFilesRelativePath(self):

        sub1 = path_utils.concat_path(self.test_dir, "sub1")
        self.assertFalse(os.path.exists(sub1))
        os.mkdir(sub1)
        self.assertTrue(os.path.exists(sub1))

        sub1_testrepo = path_utils.concat_path(sub1, "testrepo")
        v, r = git_wrapper.init(sub1, "testrepo", False)
        self.assertTrue(v)
        self.assertTrue(os.path.exists(sub1_testrepo))

        testrepo_file1 = path_utils.concat_path(sub1_testrepo, "file1.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file1), "file1-content1", "commit_msg_file1")
        self.assertTrue(v)

        testrepo_file2 = path_utils.concat_path(sub1_testrepo, "file2.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file2), "file2-content1", "commit_msg_file2")
        self.assertTrue(v)

        testrepo_file3 = path_utils.concat_path(sub1_testrepo, "file3.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file3), "file3-content1", "commit_msg_file3")
        self.assertTrue(v)

        sub1_testrepo_sub2 = path_utils.concat_path(sub1_testrepo, "sub2")
        os.mkdir(sub1_testrepo_sub2)
        sub1_testrepo_sub3 = path_utils.concat_path(sub1_testrepo, "sub3")
        os.symlink(sub1_testrepo_sub2, sub1_testrepo_sub3)

        sub1_testrepo_sub2_file4 = path_utils.concat_path(sub1_testrepo_sub2, "file4.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo_sub2, path_utils.basename_filtered(sub1_testrepo_sub2_file4), "file4-content1", "commit_msg_file4")
        self.assertTrue(v)
        sub1_testrepo_sub3_file4 = path_utils.concat_path(sub1_testrepo_sub3, "file4.txt")

        self.assertTrue(os.path.exists(sub1_testrepo_sub2_file4))
        self.assertTrue(os.path.exists(sub1_testrepo_sub3_file4))

        with open(testrepo_file1, "a") as f:
            f.write("additional content f1")

        with open(testrepo_file3, "a") as f:
            f.write("additional content f3")

        with open(sub1_testrepo_sub3_file4, "a") as f:
            f.write("additional content f4")

        v, r = git_wrapper.stage(sub1_testrepo)
        self.assertTrue(v)

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            v, r = git_lib.get_staged_files("./sub1/testrepo")
            self.assertTrue(v)
            self.assertTrue(testrepo_file1 in r)
            self.assertFalse(testrepo_file2 in r)
            self.assertTrue(testrepo_file3 in r)
            self.assertTrue(sub1_testrepo_sub2_file4 in r)
            self.assertFalse(sub1_testrepo_sub3_file4 in r) # git resolves symlinks
        finally:
            os.chdir(saved_wd)

    def testGetStagedFilesRelativePathSymlinkRepo(self):

        sub2 = path_utils.concat_path(self.test_dir, "sub2")
        self.assertFalse(os.path.exists(sub2))
        os.mkdir(sub2)
        self.assertTrue(os.path.exists(sub2))

        sub1 = path_utils.concat_path(self.test_dir, "sub1")
        self.assertFalse(os.path.exists(sub1))
        os.symlink(sub2, sub1)
        self.assertTrue(os.path.exists(sub1))

        sub1_testrepo = path_utils.concat_path(sub1, "testrepo")
        v, r = git_wrapper.init(sub1, "testrepo", False)
        self.assertTrue(v)
        self.assertTrue(os.path.exists(sub1_testrepo))

        testrepo_file1 = path_utils.concat_path(sub1_testrepo, "file1.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file1), "file1-content1", "commit_msg_file1")
        self.assertTrue(v)

        testrepo_file2 = path_utils.concat_path(sub1_testrepo, "file2.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file2), "file2-content1", "commit_msg_file2")
        self.assertTrue(v)

        testrepo_file3 = path_utils.concat_path(sub1_testrepo, "file3.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file3), "file3-content1", "commit_msg_file3")
        self.assertTrue(v)

        sub1_testrepo_sub2 = path_utils.concat_path(sub1_testrepo, "sub2")
        os.mkdir(sub1_testrepo_sub2)
        sub1_testrepo_sub3 = path_utils.concat_path(sub1_testrepo, "sub3")
        os.symlink(sub1_testrepo_sub2, sub1_testrepo_sub3)

        sub1_testrepo_sub2_file4 = path_utils.concat_path(sub1_testrepo_sub2, "file4.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo_sub2, path_utils.basename_filtered(sub1_testrepo_sub2_file4), "file4-content1", "commit_msg_file4")
        self.assertTrue(v)
        sub1_testrepo_sub3_file4 = path_utils.concat_path(sub1_testrepo_sub3, "file4.txt")

        self.assertTrue(os.path.exists(sub1_testrepo_sub2_file4))
        self.assertTrue(os.path.exists(sub1_testrepo_sub3_file4))

        with open(testrepo_file1, "a") as f:
            f.write("additional content f1")

        with open(testrepo_file3, "a") as f:
            f.write("additional content f3")

        with open(sub1_testrepo_sub3_file4, "a") as f:
            f.write("additional content f4")

        v, r = git_wrapper.stage(sub1_testrepo)
        self.assertTrue(v)

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            v, r = git_lib.get_staged_files("./sub1/testrepo")
            self.assertTrue(v)
            self.assertTrue(testrepo_file1 in r)
            self.assertFalse(testrepo_file2 in r)
            self.assertTrue(testrepo_file3 in r)
            self.assertTrue(sub1_testrepo_sub2_file4 in r)
            self.assertFalse(sub1_testrepo_sub3_file4 in r) # git resolves symlinks
        finally:
            os.chdir(saved_wd)

    def testGetUnversionedFiles(self):

        v, r = git_lib.get_unversioned_files(self.fourth_notrepo)
        self.assertFalse(v)

        v, r = git_lib.get_unversioned_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(r, [])

        first_more1 = path_utils.concat_path(self.first_repo, "more1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_more1, "more1-contents"))
        first_more2 = path_utils.concat_path(self.first_repo, "more2.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_more2, "more2-contents"))
        first_more3 = path_utils.concat_path(self.first_repo, "アーカイブ.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_more3, "more3-contents"))

        first_sub = path_utils.concat_path(self.first_repo, "subfolder")
        os.mkdir(first_sub)
        self.assertTrue(os.path.exists(first_sub))
        first_sub_more4 = path_utils.concat_path(first_sub, "more4.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_sub_more4, "more4-contents"))

        v, r = git_lib.get_unversioned_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 4)
        self.assertTrue(first_more1 in r)
        self.assertTrue(first_more2 in r)
        #self.assertTrue(first_more3 in r) # mvtodo: might require extra system config or ...
        self.assertTrue(first_sub_more4 in r)

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_unversioned_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

    def testGetUnversionedFilesRelativePath(self):

        sub1 = path_utils.concat_path(self.test_dir, "sub1")
        self.assertFalse(os.path.exists(sub1))
        os.mkdir(sub1)
        self.assertTrue(os.path.exists(sub1))

        sub1_testrepo = path_utils.concat_path(sub1, "testrepo")
        v, r = git_wrapper.init(sub1, "testrepo", False)
        self.assertTrue(v)
        self.assertTrue(os.path.exists(sub1_testrepo))

        testrepo_file1 = path_utils.concat_path(sub1_testrepo, "file1.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file1), "file1-content1", "commit_msg_file1")
        self.assertTrue(v)

        v, r = git_wrapper.stage(sub1_testrepo)
        self.assertTrue(v)

        testrepo_file2 = path_utils.concat_path(sub1_testrepo, "file2.txt")
        self.assertTrue(create_and_write_file.create_file_contents(testrepo_file2, "file2-content1"))

        testrepo_file3 = path_utils.concat_path(sub1_testrepo, "file3.txt")
        self.assertTrue(create_and_write_file.create_file_contents(testrepo_file3, "file3-content1"))

        sub1_testrepo_sub2 = path_utils.concat_path(sub1_testrepo, "sub2")
        os.mkdir(sub1_testrepo_sub2)
        sub1_testrepo_sub3 = path_utils.concat_path(sub1_testrepo, "sub3")
        os.symlink(sub1_testrepo_sub2, sub1_testrepo_sub3)

        sub1_testrepo_sub2_file4 = path_utils.concat_path(sub1_testrepo_sub2, "file4.txt")
        self.assertTrue(create_and_write_file.create_file_contents(sub1_testrepo_sub2_file4, "file4-content1"))
        self.assertTrue(v)
        sub1_testrepo_sub3_file4 = path_utils.concat_path(sub1_testrepo_sub3, "file4.txt")

        self.assertTrue(os.path.exists(sub1_testrepo_sub2_file4))
        self.assertTrue(os.path.exists(sub1_testrepo_sub3_file4))

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            v, r = git_lib.get_unversioned_files("./sub1/testrepo")
            self.assertTrue(v)
            self.assertFalse(testrepo_file1 in r)
            self.assertTrue(testrepo_file2 in r)
            self.assertTrue(testrepo_file3 in r)
            self.assertTrue(sub1_testrepo_sub2_file4 in r)
            self.assertTrue(path_utils.dirname_filtered(sub1_testrepo_sub3_file4) in r) # git will return a single entry for a symlink that points to a folder
        finally:
            os.chdir(saved_wd)

    def testGetUnversionedFilesRelativePathSymlinkRepo(self):

        sub2 = path_utils.concat_path(self.test_dir, "sub2")
        self.assertFalse(os.path.exists(sub2))
        os.mkdir(sub2)
        self.assertTrue(os.path.exists(sub2))

        sub1 = path_utils.concat_path(self.test_dir, "sub1")
        self.assertFalse(os.path.exists(sub1))
        os.symlink(sub2, sub1)
        self.assertTrue(os.path.exists(sub1))

        sub1_testrepo = path_utils.concat_path(sub1, "testrepo")
        v, r = git_wrapper.init(sub1, "testrepo", False)
        self.assertTrue(v)
        self.assertTrue(os.path.exists(sub1_testrepo))

        testrepo_file1 = path_utils.concat_path(sub1_testrepo, "file1.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file1), "file1-content1", "commit_msg_file1")
        self.assertTrue(v)

        v, r = git_wrapper.stage(sub1_testrepo)
        self.assertTrue(v)

        testrepo_file2 = path_utils.concat_path(sub1_testrepo, "file2.txt")
        self.assertTrue(create_and_write_file.create_file_contents(testrepo_file2, "file2-content1"))

        testrepo_file3 = path_utils.concat_path(sub1_testrepo, "file3.txt")
        self.assertTrue(create_and_write_file.create_file_contents(testrepo_file3, "file3-content1"))

        sub1_testrepo_sub2 = path_utils.concat_path(sub1_testrepo, "sub2")
        os.mkdir(sub1_testrepo_sub2)
        sub1_testrepo_sub3 = path_utils.concat_path(sub1_testrepo, "sub3")
        os.symlink(sub1_testrepo_sub2, sub1_testrepo_sub3)

        sub1_testrepo_sub2_file4 = path_utils.concat_path(sub1_testrepo_sub2, "file4.txt")
        self.assertTrue(create_and_write_file.create_file_contents(sub1_testrepo_sub2_file4, "file4-content1"))
        self.assertTrue(v)
        sub1_testrepo_sub3_file4 = path_utils.concat_path(sub1_testrepo_sub3, "file4.txt")

        self.assertTrue(os.path.exists(sub1_testrepo_sub2_file4))
        self.assertTrue(os.path.exists(sub1_testrepo_sub3_file4))

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            v, r = git_lib.get_unversioned_files("./sub1/testrepo")
            self.assertTrue(v)
            self.assertFalse(testrepo_file1 in r)
            self.assertTrue(testrepo_file2 in r)
            self.assertTrue(testrepo_file3 in r)
            self.assertTrue(sub1_testrepo_sub2_file4 in r)
            self.assertTrue(path_utils.dirname_filtered(sub1_testrepo_sub3_file4) in r) # git resolves symlinks
        finally:
            os.chdir(saved_wd)

    def testRemoveGitlogDecorations(self):

        self.first_file = path_utils.concat_path(self.first_repo, "file.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, path_utils.basename_filtered(self.first_file), "file1-content", "commit_msg_file")
        if not v:
            self.fail(r)

        v, r = git_wrapper.log(self.first_repo, 1)
        self.assertTrue(v)

        self.assertEqual( len(r.strip().split(os.linesep)), 5 )
        self.assertTrue("commit_msg_file" in r)
        commit_msg_oneliner = git_lib.remove_gitlog_decorations(r)
        self.assertEqual( len(commit_msg_oneliner.strip().split(os.linesep)), 1 )
        self.assertEqual("commit_msg_file", commit_msg_oneliner)

    def testIsRepoRoot(self):
        self.assertTrue(git_lib.is_repo_root(path_utils.concat_path(self.first_repo, ".git")))
        self.assertFalse(git_lib.is_repo_root(path_utils.concat_path(self.first_repo, ".anythingelse")))
        self.assertFalse(git_lib.is_repo_root(None))
        self.assertFalse(git_lib.is_repo_root(self.nonexistent_repo))

    def testIsRepoRootRelativePath(self):

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            self.assertTrue(git_lib.is_repo_root(path_utils.concat_path("./first", ".git")))
            self.assertFalse(git_lib.is_repo_root(path_utils.concat_path("./first", ".anythingelse")))
            self.assertFalse(git_lib.is_repo_root(None))
            self.assertFalse(git_lib.is_repo_root("./nonexistent"))
        finally:
            os.chdir(saved_wd)

    def testDiscoverRepoRoot(self):

        folder1 = path_utils.concat_path(self.first_repo, "folder1")
        os.mkdir(folder1)

        self.first_folder1_file2 = path_utils.concat_path(folder1, "file2.txt")
        v, r = git_test_fixture.git_createAndCommit(folder1, path_utils.basename_filtered(self.first_folder1_file2), "file2-content", "commit_msg_file-2")
        if not v:
            self.fail(r)

        folder2 = path_utils.concat_path(folder1, "folder2")
        os.mkdir(folder2)

        folder3 = path_utils.concat_path(self.first_repo, "one", "two", "three")
        path_utils.guaranteefolder(folder3)

        self.assertEqual(git_lib.discover_repo_root(self.first_repo), self.first_repo)
        self.assertEqual(git_lib.discover_repo_root(self.nonexistent_repo), None)
        self.assertEqual(git_lib.discover_repo_root(folder1), self.first_repo)
        self.assertEqual(git_lib.discover_repo_root(folder2), self.first_repo)
        self.assertEqual(git_lib.discover_repo_root(folder3), self.first_repo)

    def testDiscoverRepoRootRelativePath(self):

        folder1 = path_utils.concat_path(self.first_repo, "folder1")
        os.mkdir(folder1)

        self.first_folder1_file2 = path_utils.concat_path(folder1, "file2.txt")
        v, r = git_test_fixture.git_createAndCommit(folder1, path_utils.basename_filtered(self.first_folder1_file2), "file2-content", "commit_msg_file-2")
        if not v:
            self.fail(r)

        folder2 = path_utils.concat_path(folder1, "folder2")
        os.mkdir(folder2)

        folder3 = path_utils.concat_path(self.first_repo, "one", "two", "three")
        path_utils.guaranteefolder(folder3)

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            self.assertEqual(git_lib.discover_repo_root("./first"), self.first_repo)
            self.assertEqual(git_lib.discover_repo_root("./nonexistent"), None)
            self.assertEqual(git_lib.discover_repo_root("./first/folder1"), self.first_repo)
            self.assertEqual(git_lib.discover_repo_root("./first/folder2"), self.first_repo)
            self.assertEqual(git_lib.discover_repo_root("./first/folder3"), self.first_repo)
        finally:
            os.chdir(saved_wd)

    def testIsRepoWorkingTree(self):

        v, r = git_lib.is_repo_working_tree(self.first_repo)
        self.assertTrue(v)
        self.assertTrue(r)

        first_git_folder = path_utils.concat_path(self.first_repo, ".git")
        self.assertTrue(os.path.exists(first_git_folder))
        v, r = git_lib.is_repo_working_tree(first_git_folder)
        self.assertTrue(v)
        self.assertFalse(r)

        folder = path_utils.concat_path(self.first_repo, "one", "two", "three")
        path_utils.guaranteefolder(folder)

        v, r = git_lib.is_repo_working_tree(folder)
        self.assertTrue(v)
        self.assertTrue(r)

        # bare repos are not working trees
        v, r = git_lib.is_repo_working_tree(self.second_repo)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = git_lib.is_repo_working_tree(self.nonexistent_repo)
        self.assertFalse(v)

        v, r = git_lib.is_repo_working_tree(self.fourth_notrepo)
        self.assertTrue(v)
        self.assertFalse(r)

    def testIsRepoWorkingTreeRelativePath(self):

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)

            v, r = git_lib.is_repo_working_tree("./first")
            self.assertTrue(v)
            self.assertTrue(r)

            v, r = git_lib.is_repo_working_tree("./first/.git")
            self.assertTrue(v)
            self.assertFalse(r)

            folder = path_utils.concat_path("./first", "one", "two", "three")
            path_utils.guaranteefolder(folder)

            v, r = git_lib.is_repo_working_tree(folder)
            self.assertTrue(v)
            self.assertTrue(r)

            # bare repos are not working trees
            v, r = git_lib.is_repo_working_tree("./second")
            self.assertTrue(v)
            self.assertFalse(r)

            v, r = git_lib.is_repo_working_tree("./nonexistent")
            self.assertFalse(v)

            v, r = git_lib.is_repo_working_tree("./fourth")
            self.assertTrue(v)
            self.assertFalse(r)

        finally:
            os.chdir(saved_wd)

    def testIsRepoBare(self):

        v, r = git_lib.is_repo_bare(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(r)

        second_repo_objects = os.path.join(self.second_repo, "objects")
        v, r = git_lib.is_repo_bare(second_repo_objects)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = git_lib.is_repo_bare(self.first_repo)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = git_lib.is_repo_bare(self.nonexistent_repo)
        self.assertFalse(v)

    def testIsRepoBareRelativePath(self):

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)

            v, r = git_lib.is_repo_bare("./second")
            self.assertTrue(v)
            self.assertTrue(r)

            second_repo_objects = os.path.join("./second", "objects")
            v, r = git_lib.is_repo_bare(second_repo_objects)
            self.assertTrue(v)
            self.assertFalse(r)

            v, r = git_lib.is_repo_bare("./first")
            self.assertTrue(v)
            self.assertFalse(r)

            v, r = git_lib.is_repo_bare("./nonexistent")
            self.assertFalse(v)

        finally:
            os.chdir(saved_wd)

    def testIsRepoStandard(self):

        v, r = git_lib.is_repo_standard(self.first_repo)
        self.assertTrue(v)
        self.assertTrue(r)

        v, r = git_lib.is_repo_standard(self.second_repo)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = git_lib.is_repo_standard(self.nonexistent_repo)
        self.assertFalse(v)

        v, r = git_lib.is_repo_standard(self.fourth_notrepo)
        self.assertTrue(v)
        self.assertFalse(r)

        sub_repo = path_utils.concat_path(self.first_repo, "third")
        v, r = git_wrapper.submodule_add(self.third_repo, self.first_repo)
        self.assertTrue(v)
        self.assertTrue(os.path.exists(sub_repo))

        v, r = git_lib.is_repo_standard(sub_repo)
        self.assertTrue(v)
        self.assertFalse(r)

    def testIsRepoStandardRelativePath(self):

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)

            v, r = git_lib.is_repo_standard("./first")
            self.assertTrue(v)
            self.assertTrue(r)

            v, r = git_lib.is_repo_standard("./second")
            self.assertTrue(v)
            self.assertFalse(r)

            v, r = git_lib.is_repo_standard("./nonexistent")
            self.assertFalse(v)

            v, r = git_lib.is_repo_standard("./fourth")
            self.assertTrue(v)
            self.assertFalse(r)

            sub_repo = path_utils.concat_path("./first", "third")
            v, r = git_wrapper.submodule_add(self.third_repo, self.first_repo)
            self.assertTrue(v)
            self.assertTrue(os.path.exists(os.path.abspath(sub_repo)))

            v, r = git_lib.is_repo_standard(sub_repo)
            self.assertTrue(v)
            self.assertFalse(r)

        finally:
            os.chdir(saved_wd)

    def testIsRepoSubmodule(self):

        v, r = git_lib.is_repo_submodule(self.first_repo)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = git_lib.is_repo_submodule(self.second_repo)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = git_lib.is_repo_submodule(self.nonexistent_repo)
        self.assertFalse(v)

        v, r = git_lib.is_repo_submodule(self.fourth_notrepo)
        self.assertTrue(v)
        self.assertFalse(r)

        sub_repo = path_utils.concat_path(self.first_repo, "third")
        v, r = git_wrapper.submodule_add(self.third_repo, self.first_repo)
        self.assertTrue(v)
        self.assertTrue(os.path.exists(sub_repo))

        v, r = git_lib.is_repo_submodule(sub_repo)
        self.assertTrue(v)
        self.assertTrue(r)

    def testIsRepoSubmoduleRelativePath(self):

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)

            v, r = git_lib.is_repo_submodule("./first")
            self.assertTrue(v)
            self.assertFalse(r)

            v, r = git_lib.is_repo_submodule("./second")
            self.assertTrue(v)
            self.assertFalse(r)

            v, r = git_lib.is_repo_submodule("./nonexistent")
            self.assertFalse(v)

            v, r = git_lib.is_repo_submodule("./fourth")
            self.assertTrue(v)
            self.assertFalse(r)

            sub_repo = path_utils.concat_path("./first", "third")
            v, r = git_wrapper.submodule_add(self.third_repo, self.first_repo)
            self.assertTrue(v)
            self.assertTrue(os.path.exists(os.path.abspath(sub_repo)))

            v, r = git_lib.is_repo_submodule(sub_repo)
            self.assertTrue(v)
            self.assertTrue(r)

        finally:
            os.chdir(saved_wd)

    def testIsHeadClear(self):

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertTrue(r)

        with open(self.first_file1, "a") as f:
            f.write("extra content")

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertFalse(r)

    def testIsHeadClearRelativePath(self):

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)

            v, r = git_lib.is_head_clear("./first")
            self.assertTrue(v)
            self.assertTrue(r)

            with open(self.first_file1, "a") as f:
                f.write("extra content")

            v, r = git_lib.is_head_clear("./first")
            self.assertTrue(v)
            self.assertFalse(r)

        finally:
            os.chdir(saved_wd)

    def testIsHeadClearFail1(self):

        with open(self.first_file1, "a") as f:
            f.write("extra content")

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertFalse(r)

    def testIsHeadClearFail2(self):

        with open(self.first_file1, "a") as f:
            f.write("extra content")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertFalse(r)

    def testIsHeadClearFail3(self):

        first_file2 = path_utils.concat_path(self.first_repo, "file2.txt")
        with open(first_file2, "a") as f:
            f.write("latest file")

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertFalse(r)

    def testIsHeadClearStashed(self):

        with open(self.first_file1, "a") as f:
            f.write("extra content")

        v, r = git_wrapper.stash(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertTrue(r)

    def testPatchAsHead(self):

        first_mirror = path_utils.concat_path(self.test_dir, "first_mirror")
        v, r = git_wrapper.clone(self.first_repo, first_mirror, "origin")
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v and r)
        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v and r)

        with open(self.first_file1, "a") as f:
            f.write("changes")

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path)
        self.assertTrue(v)
        generated_patch_file = r
        self.assertTrue(os.path.exists(generated_patch_file))

        v, r = git_lib.patch_as_head(first_mirror, generated_patch_file, False)
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = git_lib.get_modified_files(self.first_repo)
        self.assertTrue(v)
        mod_first = r

        v, r = git_lib.get_modified_files(first_mirror)
        self.assertTrue(v)
        mod_first_mirror = r

        self.assertEqual(path_utils.basename_filtered(mod_first[0]), path_utils.basename_filtered(mod_first_mirror[0]))

    def testPatchAsHeadRelativePath(self):

        first_mirror = path_utils.concat_path(self.test_dir, "first_mirror")
        v, r = git_wrapper.clone(self.first_repo, first_mirror, "origin")
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v and r)
        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v and r)

        with open(self.first_file1, "a") as f:
            f.write("changes")

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path)
        self.assertTrue(v)
        generated_patch_file = r
        self.assertTrue(os.path.exists(generated_patch_file))
        generated_patch_file_rel_path = path_utils.concat_path("./", path_utils.basename_filtered(self.storage_path), self.first_repo, path_utils.basename_filtered(generated_patch_file))

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            self.assertTrue(os.path.exists(generated_patch_file_rel_path))
            v, r = git_lib.patch_as_head("./first_mirror", generated_patch_file_rel_path, False)
            self.assertTrue(v)
        finally:
            os.chdir(saved_wd)

        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = git_lib.get_modified_files(self.first_repo)
        self.assertTrue(v)
        mod_first = r

        v, r = git_lib.get_modified_files(first_mirror)
        self.assertTrue(v)
        mod_first_mirror = r

        self.assertEqual(path_utils.basename_filtered(mod_first[0]), path_utils.basename_filtered(mod_first_mirror[0]))

    def testPatchAsHeadFail1(self):

        first_mirror = path_utils.concat_path(self.test_dir, "first_mirror")
        v, r = git_wrapper.clone(self.first_repo, first_mirror, "origin")
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v and r)
        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v and r)

        with open(self.first_file1, "a") as f:
            f.write("changes")

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path)
        self.assertTrue(v)
        generated_patch_file = r
        self.assertTrue(os.path.exists(generated_patch_file))

        first_mirror_more1 = path_utils.concat_path(first_mirror, "more1.txt")
        if not create_and_write_file.create_file_contents(first_mirror_more1, "more1-contents"):
            self.fail("Failed creating file %s" % first_mirror_more1)

        v, r = git_lib.patch_as_head(first_mirror, generated_patch_file, False)
        self.assertFalse(v)

        v, r = git_lib.get_modified_files(first_mirror)
        self.assertTrue(v)
        self.assertEqual(r, [])

        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v)
        self.assertFalse(r)

    def testPatchAsHeadFail2(self):

        first_mirror = path_utils.concat_path(self.test_dir, "first_mirror")
        v, r = git_wrapper.clone(self.first_repo, first_mirror, "origin")
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v and r)
        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v and r)

        with open(self.first_file1, "a") as f:
            f.write("changes")

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path)
        self.assertTrue(v)
        generated_patch_file = r
        self.assertTrue(os.path.exists(generated_patch_file))

        first_mirror_more1 = path_utils.concat_path(first_mirror, "more1.txt")
        if not create_and_write_file.create_file_contents(first_mirror_more1, "more1-contents"):
            self.fail("Failed creating file %s" % first_mirror_more1)

        v, r = git_wrapper.stage(first_mirror, [first_mirror_more1])
        self.assertTrue(v)

        v, r = git_lib.patch_as_head(first_mirror, generated_patch_file, False)
        self.assertFalse(v)

        v, r = git_lib.get_modified_files(first_mirror)
        self.assertTrue(v)
        self.assertEqual(r, [])

        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v)
        self.assertFalse(r)

    def testPatchAsHeadOverrideFail1(self):

        first_mirror = path_utils.concat_path(self.test_dir, "first_mirror")
        v, r = git_wrapper.clone(self.first_repo, first_mirror, "origin")
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v and r)
        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v and r)

        with open(self.first_file1, "a") as f:
            f.write("changes")

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path)
        self.assertTrue(v)
        generated_patch_file = r
        self.assertTrue(os.path.exists(generated_patch_file))

        first_mirror_more1 = path_utils.concat_path(first_mirror, "more1.txt")
        if not create_and_write_file.create_file_contents(first_mirror_more1, "more1-contents"):
            self.fail("Failed creating file %s" % first_mirror_more1)

        v, r = git_lib.patch_as_head(first_mirror, generated_patch_file, True)
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = git_lib.get_modified_files(self.first_repo)
        self.assertTrue(v)
        mod_first = r

        v, r = git_lib.get_modified_files(first_mirror)
        self.assertTrue(v)
        mod_first_mirror = r

        self.assertEqual(path_utils.basename_filtered(mod_first[0]), path_utils.basename_filtered(mod_first_mirror[0]))

    def testPatchAsHeadOverrideFail2(self):

        first_mirror = path_utils.concat_path(self.test_dir, "first_mirror")
        v, r = git_wrapper.clone(self.first_repo, first_mirror, "origin")
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v and r)
        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v and r)

        with open(self.first_file1, "a") as f:
            f.write("changes")

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path)
        self.assertTrue(v)
        generated_patch_file = r
        self.assertTrue(os.path.exists(generated_patch_file))

        first_mirror_more1 = path_utils.concat_path(first_mirror, "more1.txt")
        if not create_and_write_file.create_file_contents(first_mirror_more1, "more1-contents"):
            self.fail("Failed creating file %s" % first_mirror_more1)

        v, r = git_wrapper.stage(first_mirror, [first_mirror_more1])
        self.assertTrue(v)

        v, r = git_lib.patch_as_head(first_mirror, generated_patch_file, True)
        self.assertTrue(v)

        v, r = git_lib.get_modified_files(self.first_repo)
        self.assertTrue(v)
        mod_first = r

        v, r = git_lib.get_modified_files(first_mirror)
        self.assertTrue(v)
        mod_first_mirror = r

        self.assertEqual(path_utils.basename_filtered(mod_first[0]), path_utils.basename_filtered(mod_first_mirror[0]))

    def testPatchAsStaged(self):

        first_mirror = path_utils.concat_path(self.test_dir, "first_mirror")
        v, r = git_wrapper.clone(self.first_repo, first_mirror, "origin")
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v and r)
        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v and r)

        with open(self.first_file1, "a") as f:
            f.write("changes")

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path)
        self.assertTrue(v)
        generated_patch_file = r
        self.assertTrue(os.path.exists(generated_patch_file))

        v, r = git_lib.patch_as_staged(first_mirror, generated_patch_file, False)
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = git_lib.get_modified_files(self.first_repo)
        self.assertTrue(v)
        mod_first = r

        v, r = git_lib.get_staged_files(first_mirror)
        self.assertTrue(v)
        mod_first_mirror = r

        self.assertEqual(path_utils.basename_filtered(mod_first[0]), path_utils.basename_filtered(mod_first_mirror[0]))

    def testPatchAsStagedRelativePath(self):

        first_mirror = path_utils.concat_path(self.test_dir, "first_mirror")
        v, r = git_wrapper.clone(self.first_repo, first_mirror, "origin")
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v and r)
        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v and r)

        with open(self.first_file1, "a") as f:
            f.write("changes")

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path)
        self.assertTrue(v)
        generated_patch_file = r
        self.assertTrue(os.path.exists(generated_patch_file))
        generated_patch_file_rel_path = path_utils.concat_path("./", path_utils.basename_filtered(self.storage_path), self.first_repo, path_utils.basename_filtered(generated_patch_file))

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            self.assertTrue(os.path.exists(generated_patch_file_rel_path))

            v, r = git_lib.patch_as_staged("./first_mirror", generated_patch_file_rel_path, False)
            self.assertTrue(v)

        finally:
            os.chdir(saved_wd)

        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = git_lib.get_modified_files(self.first_repo)
        self.assertTrue(v)
        mod_first = r

        v, r = git_lib.get_staged_files(first_mirror)
        self.assertTrue(v)
        mod_first_mirror = r

        self.assertEqual(path_utils.basename_filtered(mod_first[0]), path_utils.basename_filtered(mod_first_mirror[0]))

    def testPatchAsStagedFail1(self):

        first_mirror = path_utils.concat_path(self.test_dir, "first_mirror")
        v, r = git_wrapper.clone(self.first_repo, first_mirror, "origin")
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v and r)
        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v and r)

        with open(self.first_file1, "a") as f:
            f.write("changes")

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path)
        self.assertTrue(v)
        generated_patch_file = r
        self.assertTrue(os.path.exists(generated_patch_file))

        first_mirror_more1 = path_utils.concat_path(first_mirror, "more1.txt")
        if not create_and_write_file.create_file_contents(first_mirror_more1, "more1-contents"):
            self.fail("Failed creating file %s" % first_mirror_more1)

        v, r = git_lib.patch_as_staged(first_mirror, generated_patch_file, False)
        self.assertFalse(v)

        v, r = git_lib.get_staged_files(first_mirror)
        self.assertTrue(v)
        self.assertEqual(r, [])

        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v)
        self.assertFalse(r)

    def testPatchAsStagedFail2(self):

        first_mirror = path_utils.concat_path(self.test_dir, "first_mirror")
        v, r = git_wrapper.clone(self.first_repo, first_mirror, "origin")
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v and r)
        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v and r)

        with open(self.first_file1, "a") as f:
            f.write("changes")

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path)
        self.assertTrue(v)
        generated_patch_file = r
        self.assertTrue(os.path.exists(generated_patch_file))

        first_mirror_more1 = path_utils.concat_path(first_mirror, "more1.txt")
        if not create_and_write_file.create_file_contents(first_mirror_more1, "more1-contents"):
            self.fail("Failed creating file %s" % first_mirror_more1)

        v, r = git_wrapper.stage(first_mirror, [first_mirror_more1])
        self.assertTrue(v)

        v, r = git_lib.patch_as_staged(first_mirror, generated_patch_file, False)
        self.assertFalse(v)

        v, r = git_lib.get_staged_files(first_mirror)
        self.assertTrue(v)
        staged_list_first_mirror = r
        self.assertEqual(path_utils.basename_filtered(staged_list_first_mirror[0]), path_utils.basename_filtered(first_mirror_more1))

        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v)
        self.assertFalse(r)

    def testPatchAsStagedOverrideFail1(self):

        first_mirror = path_utils.concat_path(self.test_dir, "first_mirror")
        v, r = git_wrapper.clone(self.first_repo, first_mirror, "origin")
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v and r)
        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v and r)

        with open(self.first_file1, "a") as f:
            f.write("changes")

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path)
        self.assertTrue(v)
        generated_patch_file = r
        self.assertTrue(os.path.exists(generated_patch_file))

        first_mirror_more1 = path_utils.concat_path(first_mirror, "more1.txt")
        if not create_and_write_file.create_file_contents(first_mirror_more1, "more1-contents"):
            self.fail("Failed creating file %s" % first_mirror_more1)

        v, r = git_lib.patch_as_staged(first_mirror, generated_patch_file, True)
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = git_lib.get_modified_files(self.first_repo)
        self.assertTrue(v)
        mod_first = r

        v, r = git_lib.get_staged_files(first_mirror)
        self.assertTrue(v)
        mod_first_mirror = r

        self.assertEqual(path_utils.basename_filtered(mod_first[0]), path_utils.basename_filtered(mod_first_mirror[0]))

    def testPatchAsStagedOverrideFail2(self):

        first_mirror = path_utils.concat_path(self.test_dir, "first_mirror")
        v, r = git_wrapper.clone(self.first_repo, first_mirror, "origin")
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v and r)
        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v and r)

        with open(self.first_file1, "a") as f:
            f.write("changes")

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path)
        self.assertTrue(v)
        generated_patch_file = r
        self.assertTrue(os.path.exists(generated_patch_file))

        first_mirror_more1 = path_utils.concat_path(first_mirror, "more1.txt")
        if not create_and_write_file.create_file_contents(first_mirror_more1, "more1-contents"):
            self.fail("Failed creating file %s" % first_mirror_more1)

        v, r = git_wrapper.stage(first_mirror, [first_mirror_more1])
        self.assertTrue(v)

        v, r = git_lib.patch_as_staged(first_mirror, generated_patch_file, True)
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = git_lib.get_modified_files(self.first_repo)
        self.assertTrue(v)
        mod_first = r

        v, r = git_lib.get_staged_files(first_mirror)
        self.assertTrue(v)
        mod_first_mirror = r

        self.assertEqual(path_utils.basename_filtered(mod_first[0]), path_utils.basename_filtered(mod_first_mirror[0]))

    def testPatchAsStash(self):

        first_mirror = path_utils.concat_path(self.test_dir, "first_mirror")
        v, r = git_wrapper.clone(self.first_repo, first_mirror, "origin")
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v and r)
        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v and r)

        with open(self.first_file1, "a") as f:
            f.write("changes")

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path)
        self.assertTrue(v)
        generated_patch_file = r
        self.assertTrue(os.path.exists(generated_patch_file))

        v, r = git_lib.patch_as_stash(first_mirror, generated_patch_file, False, False)
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v)
        self.assertTrue(r)

        v, r = git_lib.get_stash_list(first_mirror)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

    def testPatchAsStashRelativePath(self):

        first_mirror = path_utils.concat_path(self.test_dir, "first_mirror")
        v, r = git_wrapper.clone(self.first_repo, first_mirror, "origin")
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v and r)
        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v and r)

        with open(self.first_file1, "a") as f:
            f.write("changes")

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path)
        self.assertTrue(v)
        generated_patch_file = r
        self.assertTrue(os.path.exists(generated_patch_file))
        generated_patch_file_rel_path = path_utils.concat_path("./", path_utils.basename_filtered(self.storage_path), self.first_repo, path_utils.basename_filtered(generated_patch_file))

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            self.assertTrue(os.path.exists(generated_patch_file_rel_path))

            v, r = git_lib.patch_as_stash("./first_mirror", generated_patch_file_rel_path, False, False)
            self.assertTrue(v)

            v, r = git_lib.is_head_clear(first_mirror)
            self.assertTrue(v)
            self.assertTrue(r)

            v, r = git_lib.get_stash_list("./first_mirror")
            self.assertTrue(v)
            self.assertEqual(len(r), 1)

        finally:
            os.chdir(saved_wd)

    def testPatchAsStashFail1(self):

        first_mirror = path_utils.concat_path(self.test_dir, "first_mirror")
        v, r = git_wrapper.clone(self.first_repo, first_mirror, "origin")
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v and r)
        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v and r)

        with open(self.first_file1, "a") as f:
            f.write("changes")

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path)
        self.assertTrue(v)
        generated_patch_file = r
        self.assertTrue(os.path.exists(generated_patch_file))

        first_mirror_more1 = path_utils.concat_path(first_mirror, "more1.txt")
        if not create_and_write_file.create_file_contents(first_mirror_more1, "more1-contents"):
            self.fail("Failed creating file %s" % first_mirror_more1)

        v, r = git_lib.patch_as_stash(first_mirror, generated_patch_file, False, False)
        self.assertFalse(v)

        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v)
        self.assertFalse(r)

    def testPatchAsStashFail2(self):

        first_mirror = path_utils.concat_path(self.test_dir, "first_mirror")
        v, r = git_wrapper.clone(self.first_repo, first_mirror, "origin")
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v and r)
        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v and r)

        with open(self.first_file1, "a") as f:
            f.write("changes")

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path)
        self.assertTrue(v)
        generated_patch_file = r
        self.assertTrue(os.path.exists(generated_patch_file))

        self.first_mirror_file1 = path_utils.concat_path(first_mirror, "file1.txt")
        with open(self.first_mirror_file1, "a") as f:
            f.write("additional content")

        v, r = git_lib.patch_as_stash(first_mirror, generated_patch_file, False, False)
        self.assertFalse(v)

        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = git_lib.get_stash_list(first_mirror)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

    def testPatchAsStashFail3(self):

        first_mirror = path_utils.concat_path(self.test_dir, "first_mirror")
        v, r = git_wrapper.clone(self.first_repo, first_mirror, "origin")
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v and r)
        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v and r)

        with open(self.first_file1, "a") as f:
            f.write("changes")

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path)
        self.assertTrue(v)
        generated_patch_file = r
        self.assertTrue(os.path.exists(generated_patch_file))

        self.first_mirror_file1 = path_utils.concat_path(first_mirror, "file1.txt")
        with open(self.first_mirror_file1, "a") as f:
            f.write("additional content")

        v, r = git_wrapper.stash(first_mirror)
        self.assertTrue(v)

        v, r = git_lib.patch_as_stash(first_mirror, generated_patch_file, False, False)
        self.assertFalse(v)

        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v)
        self.assertTrue(r)

        v, r = git_lib.get_stash_list(first_mirror)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

    def testPatchAsStashOverrideFail1(self):

        first_mirror = path_utils.concat_path(self.test_dir, "first_mirror")
        v, r = git_wrapper.clone(self.first_repo, first_mirror, "origin")
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v and r)
        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v and r)

        with open(self.first_file1, "a") as f:
            f.write("changes")

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path)
        self.assertTrue(v)
        generated_patch_file = r
        self.assertTrue(os.path.exists(generated_patch_file))

        first_mirror_more1 = path_utils.concat_path(first_mirror, "more1.txt")
        if not create_and_write_file.create_file_contents(first_mirror_more1, "more1-contents"):
            self.fail("Failed creating file %s" % first_mirror_more1)

        v, r = git_lib.patch_as_stash(first_mirror, generated_patch_file, True, True)
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v)
        self.assertFalse(r)

    def testPatchAsStashOverrideFail2(self):

        first_mirror = path_utils.concat_path(self.test_dir, "first_mirror")
        v, r = git_wrapper.clone(self.first_repo, first_mirror, "origin")
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v and r)
        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v and r)

        with open(self.first_file1, "a") as f:
            f.write("changes")

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path)
        self.assertTrue(v)
        generated_patch_file = r
        self.assertTrue(os.path.exists(generated_patch_file))

        self.first_mirror_file1 = path_utils.concat_path(first_mirror, "file1.txt")
        with open(self.first_mirror_file1, "a") as f:
            f.write("additional content")

        v, r = git_wrapper.stash(first_mirror)
        self.assertTrue(v)

        v, r = git_lib.patch_as_stash(first_mirror, generated_patch_file, True, True)
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v)
        self.assertTrue(r)

        v, r = git_lib.get_stash_list(first_mirror)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)

    def testUnstageFail1(self):

        first_file2 = path_utils.concat_path(self.first_repo, "file2.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, path_utils.basename_filtered(first_file2), "file2-content1", "commit_msg_file2")
        self.assertTrue(v)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "a") as f:
            f.write("smore")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        v, r = git_lib.unstage(self.first_repo, [first_file2])
        self.assertFalse(v)

        v, r = git_lib.unstage(self.first_repo, [self.first_file1, first_file2])
        self.assertFalse(v)

    def testUnstageFail2(self):

        first_file2 = path_utils.concat_path(self.first_repo, "file2.txt")

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "a") as f:
            f.write("smore")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        v, r = git_lib.unstage(self.first_repo, [first_file2])
        self.assertFalse(v)

    def testUnstageFail3(self):

        first_file2 = path_utils.concat_path(self.first_repo, "file2.txt")

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "a") as f:
            f.write("smore")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        self.assertTrue(create_and_write_file.create_file_contents(first_file2, "more1-contents"))

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        v, r = git_lib.unstage(self.first_repo, [first_file2])
        self.assertFalse(v)

    def testUnstage1(self):

        first_file2 = path_utils.concat_path(self.first_repo, "file2.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, path_utils.basename_filtered(first_file2), "file2-content1", "commit_msg_file2")
        self.assertTrue(v)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "a") as f:
            f.write("smore")

        with open(first_file2, "a") as f:
            f.write("smore")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)

        v, r = git_lib.unstage(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

    def testUnstage2(self):

        first_file2 = path_utils.concat_path(self.first_repo, "file2.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, path_utils.basename_filtered(first_file2), "file2-content1", "commit_msg_file2")
        self.assertTrue(v)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "a") as f:
            f.write("smore")

        with open(first_file2, "a") as f:
            f.write("smore")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)

        v, r = git_lib.unstage(self.first_repo, [self.first_file1])
        self.assertTrue(v)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertFalse(self.first_file1 in r)
        self.assertTrue(first_file2 in r)

    def testUnstageRelativePath1(self):

        first_file2 = path_utils.concat_path(self.first_repo, "file2.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, path_utils.basename_filtered(first_file2), "file2-content1", "commit_msg_file2")
        self.assertTrue(v)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "a") as f:
            f.write("smore")

        with open(first_file2, "a") as f:
            f.write("smore")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            v, r = git_lib.unstage("./first")
            self.assertTrue(v)
        finally:
            os.chdir(saved_wd)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

    def testUnstageRelativePath2(self):

        first_file2 = path_utils.concat_path(self.first_repo, "file2.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, path_utils.basename_filtered(first_file2), "file2-content1", "commit_msg_file2")
        self.assertTrue(v)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "a") as f:
            f.write("smore")

        with open(first_file2, "a") as f:
            f.write("smore")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            first_file_rel_path = path_utils.concat_path("./", path_utils.basename_filtered(self.first_repo), path_utils.basename_filtered(self.first_file1))
            self.assertTrue(os.path.exists(first_file_rel_path))

            v, r = git_lib.unstage("./first", [first_file_rel_path])
            self.assertTrue(v)
        finally:
            os.chdir(saved_wd)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertFalse(self.first_file1 in r)
        self.assertTrue(first_file2 in r)

if __name__ == '__main__':
    unittest.main()
