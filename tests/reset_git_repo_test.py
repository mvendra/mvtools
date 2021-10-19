#!/usr/bin/env python3

import sys
import os
import shutil
import unittest
from unittest import mock
from unittest.mock import patch

import mvtools_test_fixture
import git_test_fixture
import create_and_write_file
import path_utils
import mvtools_exception
import delayed_file_backup
import fsquery

import git_wrapper
import git_lib
import reset_git_repo

class ResetGitRepoTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("reset_git_repo_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        self.nonexistent = path_utils.concat_path(self.test_dir, "nonexistent")

        self.nonrepo = path_utils.concat_path(self.test_dir, "nonrepo")
        os.mkdir(self.nonrepo)

        # first repo
        self.first_repo = path_utils.concat_path(self.test_dir, "first")
        v, r = git_wrapper.init(self.test_dir, "first", False)
        if not v:
            return v, r

        self.first_file1 = path_utils.concat_path(self.first_repo, "file1.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file1.txt", "first-file1-content", "first-file1-msg")
        if not v:
            return v, r

        self.first_file2 = path_utils.concat_path(self.first_repo, "file2.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file2.txt", "first-file2-content", "first-file2-msg")
        if not v:
            return v, r

        # backup object (rdb: reset delayed backup)
        self.rdb_storage = path_utils.concat_path(self.test_dir, "rdb_storage")
        self.rdb = delayed_file_backup.delayed_file_backup(self.rdb_storage)

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    # mvtodo: disabled
    """
    def testResetGitRepo_ResetGitRepoFile_Fail1(self):

        v, r = reset_git_repo.reset_git_repo_file(self.nonrepo, self.first_file1, 1, self.rdb)
        self.assertFalse(v)

    def testResetGitRepo_ResetGitRepoFile_Fail2(self):

        v, r = reset_git_repo.reset_git_repo_file(self.first_repo, self.first_file1, 1, self.rdb)
        self.assertFalse(v)

    def testResetGitRepo_ResetGitRepoFile_Fail3(self):

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "w") as f:
            f.write("extra stuff")

        v, r = git_lib.get_head_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        patch_file_filename = "1_reset_git_repo_head_%s.patch" % (path_utils.basename_filtered(self.first_file1))
        test_patch_file = path_utils.concat_path(self.rdb_storage, "head", patch_file_filename)
        self.assertFalse(os.path.exists(test_patch_file))

        os.mkdir(self.rdb_storage)
        self.assertTrue(create_and_write_file.create_file_contents(test_patch_file, "dummy contents"))

        v, r = reset_git_repo.reset_git_repo_file(self.first_repo, self.first_file1, 1, self.rdb)
        self.assertFalse(v)

        v, r = git_lib.get_head_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

    def testResetGitRepo_ResetGitRepoFile_Fail4(self):

        self.second_repo = path_utils.concat_path(self.test_dir, "second")
        v, r = git_wrapper.init(self.test_dir, "second", False)
        self.assertTrue(v)

        self.second_file1 = path_utils.concat_path(self.second_repo, "file1.txt")
        v, r = git_test_fixture.git_createAndCommit(self.second_repo, "file1.txt", "second-file1-content", "second-file1-msg")
        self.assertTrue(v)

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "w") as f:
            f.write("extra stuff")

        v, r = git_lib.get_head_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        patch_file_filename = "1_reset_git_repo_head_%s.patch" % (path_utils.basename_filtered(self.first_file1))
        test_patch_file = path_utils.concat_path(self.rdb_storage, "head", patch_file_filename)
        self.assertFalse(os.path.exists(test_patch_file))

        os.mkdir(self.rdb_storage)
        self.assertTrue(create_and_write_file.create_file_contents(test_patch_file, "dummy contents"))

        v, r = reset_git_repo.reset_git_repo_file(self.first_repo, self.second_file1, 1, self.rdb)
        self.assertFalse(v)

        v, r = git_lib.get_head_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

    def testResetGitRepo_ResetGitRepoFile_Fail5(self):

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        first_file3 = path_utils.concat_path(self.first_repo, "file3.txt")
        self.assertFalse(os.path.exists(first_file3))
        self.assertTrue(create_and_write_file.create_file_contents(first_file3, "first-file3-content"))

        v, r = git_wrapper.stage(self.first_repo, [first_file3])
        self.assertTrue(v)

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        patch_file_filename = "1_reset_git_repo_head_%s.patch" % (path_utils.basename_filtered(first_file3))
        test_patch_file = path_utils.concat_path(self.rdb_storage, "head", patch_file_filename)
        self.assertFalse(os.path.exists(test_patch_file))

        v, r = reset_git_repo.reset_git_repo_file(self.first_repo, first_file3, 1, self.rdb)
        self.assertFalse(v)

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

    def testResetGitRepo_ResetGitRepoFile_Fail6(self):

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "w") as f:
            f.write("extra stuff file1")

        first_file3 = path_utils.concat_path(self.first_repo, "file3.txt")
        self.assertFalse(os.path.exists(first_file3))
        self.assertTrue(create_and_write_file.create_file_contents(first_file3, "dummy contents"))
        self.assertTrue(os.path.exists(first_file3))

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertTrue(first_file3 in r)

        patch_file_filename3 = "3_reset_git_repo_head_%s.patch" % (path_utils.basename_filtered(first_file3))
        test_patch_file3 = path_utils.concat_path(self.rdb_storage, "head", patch_file_filename3)
        self.assertFalse(os.path.exists(test_patch_file3))

        v, r = reset_git_repo.reset_git_repo_file(self.first_repo, first_file3, 3, self.rdb)
        self.assertFalse(v)
        self.assertFalse(os.path.exists(test_patch_file3))

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertTrue(self.first_file1 in r)
        self.assertFalse(first_file3 in r)
        self.assertTrue(os.path.exists(first_file3))

    def testResetGitRepo_ResetGitRepoFile1(self):

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "w") as f:
            f.write("extra stuff")

        v, r = git_lib.get_head_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        patch_file_filename = "1_reset_git_repo_head_%s.patch" % (path_utils.basename_filtered(self.first_file1))
        test_patch_file = path_utils.concat_path(self.rdb_storage, "head", patch_file_filename)
        self.assertFalse(os.path.exists(test_patch_file))

        v, r = reset_git_repo.reset_git_repo_file(self.first_repo, self.first_file1, 1, self.rdb)
        self.assertTrue(v)
        self.assertTrue(os.path.exists(test_patch_file))

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

    def testResetGitRepo_ResetGitRepoFile2(self):

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "w") as f:
            f.write("extra stuff file1")

        with open(self.first_file2, "w") as f:
            f.write("extra stuff file2")

        v, r = git_lib.get_head_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)

        patch_file_filename = "1_reset_git_repo_head_%s.patch" % (path_utils.basename_filtered(self.first_file1))
        test_patch_file = path_utils.concat_path(self.rdb_storage, "head", patch_file_filename)
        self.assertFalse(os.path.exists(test_patch_file))

        v, r = reset_git_repo.reset_git_repo_file(self.first_repo, self.first_file1, 1, self.rdb)
        self.assertTrue(v)
        self.assertTrue(os.path.exists(test_patch_file))

        v, r = git_lib.get_head_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

    def testResetGitRepo_ResetGitRepoFile3(self):

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "w") as f:
            f.write("extra stuff file1")

        with open(self.first_file2, "w") as f:
            f.write("extra stuff file2")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        patch_file_filename1 = "1_reset_git_repo_head_%s.patch" % (path_utils.basename_filtered(self.first_file1))
        test_patch_file1 = path_utils.concat_path(self.rdb_storage, "head", patch_file_filename1)
        self.assertFalse(os.path.exists(test_patch_file1))

        patch_file_filename2 = "2_reset_git_repo_head_%s.patch" % (path_utils.basename_filtered(self.first_file2))
        test_patch_file2 = path_utils.concat_path(self.rdb_storage, "head", patch_file_filename2)
        self.assertFalse(os.path.exists(test_patch_file2))

        v, r = reset_git_repo.reset_git_repo_file(self.first_repo, self.first_file1, 1, self.rdb)
        self.assertTrue(v)
        self.assertTrue(os.path.exists(test_patch_file1))
        self.assertFalse(os.path.exists(patch_file_filename2))

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertTrue(self.first_file2 in r)

    def testResetGitRepo_ResetGitRepoFile4(self):

        sub1 = path_utils.concat_path(self.first_repo, "sub1")
        os.mkdir(sub1)

        sub2 = path_utils.concat_path(sub1, "sub2")
        os.mkdir(sub2)

        sub1_sub2_file3 = path_utils.concat_path(sub2, "file3.txt")
        self.assertTrue(create_and_write_file.create_file_contents(sub1_sub2_file3, "dummy contents"))

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.first_repo, "more")
        self.assertTrue(v)

        self.assertTrue(os.path.exists(sub1_sub2_file3))

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(sub1_sub2_file3, "w") as f:
            f.write("extra stuff")

        v, r = git_lib.get_head_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        patch_file_filename = "1_reset_git_repo_head_%s.patch" % (path_utils.basename_filtered(sub1_sub2_file3))
        test_patch_file = path_utils.concat_path(self.rdb_storage, "head", "sub1", "sub2", patch_file_filename)
        self.assertFalse(os.path.exists(test_patch_file))

        v, r = reset_git_repo.reset_git_repo_file(self.first_repo, sub1_sub2_file3, 1, self.rdb)
        self.assertTrue(v)
        self.assertTrue(os.path.exists(test_patch_file))

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

    def testResetGitRepo_ResetGitRepoFile5(self):

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        os.unlink(self.first_file1)
        self.assertFalse(os.path.exists(self.first_file1))

        v, r = git_lib.get_head_deleted_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        v, r = reset_git_repo.reset_git_repo_file(self.first_repo, self.first_file1, 1, self.rdb)
        self.assertTrue(v)
        self.assertTrue(self.first_file1 in r)

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

    def testResetGitRepo_ResetGitRepoFile6(self):

        sub1 = path_utils.concat_path(self.first_repo, "sub1")
        os.mkdir(sub1)

        sub2 = path_utils.concat_path(sub1, "sub2")
        os.mkdir(sub2)

        sub1_sub2_file3 = path_utils.concat_path(sub2, "file3.txt")
        self.assertTrue(create_and_write_file.create_file_contents(sub1_sub2_file3, "dummy contents"))

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.first_repo, "more")
        self.assertTrue(v)

        self.assertTrue(os.path.exists(sub1_sub2_file3))

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        os.unlink(sub1_sub2_file3)
        self.assertFalse(os.path.exists(sub1_sub2_file3))

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        v, r = reset_git_repo.reset_git_repo_file(self.first_repo, sub1_sub2_file3, 1, self.rdb)
        self.assertTrue(v)
        self.assertTrue(sub1_sub2_file3 in r)

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

    def testResetGitRepo_ResetGitRepoFile7(self):

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        os.unlink(self.first_file1)
        self.assertFalse(os.path.exists(self.first_file1))

        v, r = git_lib.get_head_deleted_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_head_deleted_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = reset_git_repo.reset_git_repo_file(self.first_repo, self.first_file1, 1, self.rdb)
        self.assertTrue(v)
        self.assertTrue(self.first_file1 in r)

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        self.assertTrue(os.path.exists(self.first_file1))
    """

    def testResetGitRepo_ResetGitRepoHead_Fail1(self):

        v, r = reset_git_repo.reset_git_repo_head(self.nonrepo, self.rdb)
        self.assertFalse(v)

    def testResetGitRepo_ResetGitRepoHead1(self):

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "w") as f:
            f.write("extra stuff")

        v, r = git_lib.get_head_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        patch_file_filename = "1_reset_git_repo_head_%s.patch" % (path_utils.basename_filtered(self.first_file1))
        test_patch_file = path_utils.concat_path(self.rdb_storage, "head", patch_file_filename)
        self.assertFalse(os.path.exists(test_patch_file))

        v, r = reset_git_repo.reset_git_repo_head(self.first_repo, self.rdb)
        self.assertTrue(v)
        self.assertTrue(os.path.exists(test_patch_file))

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

    def testResetGitRepo_ResetGitRepoHead2(self):

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "w") as f:
            f.write("extra stuff")

        with open(self.first_file2, "w") as f:
            f.write("extra stuff")

        v, r = git_lib.get_head_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)

        patch_file1_filename = "1_reset_git_repo_head_%s.patch" % (path_utils.basename_filtered(self.first_file1))
        test_patch_file1 = path_utils.concat_path(self.rdb_storage, "head",patch_file1_filename)
        self.assertFalse(os.path.exists(test_patch_file1))

        patch_file2_filename = "2_reset_git_repo_head_%s.patch" % (path_utils.basename_filtered(self.first_file2))
        test_patch_file2 = path_utils.concat_path(self.rdb_storage, "head", patch_file2_filename)
        self.assertFalse(os.path.exists(test_patch_file2))

        v, r = reset_git_repo.reset_git_repo_head(self.first_repo, self.rdb)
        self.assertTrue(v)
        self.assertTrue(os.path.exists(test_patch_file1))
        self.assertTrue(os.path.exists(test_patch_file2))

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

    def testResetGitRepo_ResetGitRepoHead3(self):

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = reset_git_repo.reset_git_repo_head(self.first_repo, self.rdb)
        self.assertTrue(v)

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

    def testResetGitRepo_ResetGitRepoHead4(self):

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "w") as f:
            f.write("extra stuff")

        with open(self.first_file2, "w") as f:
            f.write("extra stuff")

        v, r = git_wrapper.stage(self.first_repo, [self.first_file2])
        self.assertTrue(v)

        v, r = git_lib.get_head_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        patch_file1_filename = "1_reset_git_repo_head_%s.patch" % (path_utils.basename_filtered(self.first_file1))
        test_patch_file1 = path_utils.concat_path(self.rdb_storage, "head", patch_file1_filename)
        self.assertFalse(os.path.exists(test_patch_file1))

        patch_file2_filename = "2_reset_git_repo_head_%s.patch" % (path_utils.basename_filtered(self.first_file2))
        test_patch_file2 = path_utils.concat_path(self.rdb_storage, "head", patch_file2_filename)
        self.assertFalse(os.path.exists(test_patch_file2))

        v, r = reset_git_repo.reset_git_repo_head(self.first_repo, self.rdb)
        self.assertTrue(v)
        self.assertTrue(os.path.exists(test_patch_file1))
        self.assertFalse(os.path.exists(test_patch_file2))

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

    def testResetGitRepo_ResetGitRepoHead5(self):

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "w") as f:
            f.write("extra stuff")

        first_file3 = path_utils.concat_path(self.first_repo, "file3.txt")
        self.assertFalse(os.path.exists(first_file3))
        self.assertTrue(create_and_write_file.create_file_contents(first_file3, "dummy contents"))
        self.assertTrue(os.path.exists(first_file3))

        v, r = git_lib.get_unversioned_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_unversioned_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)

        patch_file1_filename = "1_reset_git_repo_head_%s.patch" % (path_utils.basename_filtered(self.first_file1))
        test_patch_file1 = path_utils.concat_path(self.rdb_storage, "head", patch_file1_filename)
        self.assertFalse(os.path.exists(test_patch_file1))

        patch_file3_filename = "2_reset_git_repo_head_%s.patch" % (path_utils.basename_filtered(first_file3))
        test_patch_file3 = path_utils.concat_path(self.rdb_storage, "head", patch_file3_filename)
        self.assertFalse(os.path.exists(test_patch_file3))

        v, r = reset_git_repo.reset_git_repo_head(self.first_repo, self.rdb)
        self.assertTrue(v)
        self.assertFalse(os.path.exists(test_patch_file1))
        self.assertFalse(os.path.exists(test_patch_file3))

        v, r = git_lib.get_unversioned_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

    def testResetGitRepo_ResetGitRepoHead6(self):

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        sub1 = path_utils.concat_path(self.first_repo, "sub1")
        os.mkdir(sub1)

        sub2 = path_utils.concat_path(sub1, "sub2")
        os.mkdir(sub2)

        sub1_sub2_file3 = path_utils.concat_path(sub2, "file3.txt")
        self.assertTrue(create_and_write_file.create_file_contents(sub1_sub2_file3, "dummy contents"))

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.first_repo, "more")
        self.assertTrue(v)

        self.assertTrue(os.path.exists(sub1_sub2_file3))

        with open(sub1_sub2_file3, "w") as f:
            f.write("extra stuff")

        v, r = git_lib.get_head_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        patch_file_filename = "1_reset_git_repo_head_%s.patch" % (path_utils.basename_filtered(sub1_sub2_file3))
        test_patch_file = path_utils.concat_path(self.rdb_storage, "head", "sub1", "sub2", patch_file_filename)
        self.assertFalse(os.path.exists(test_patch_file))

        v, r = reset_git_repo.reset_git_repo_head(self.first_repo, self.rdb)
        self.assertTrue(v)
        self.assertTrue(os.path.exists(test_patch_file))

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

    def testResetGitRepo_ResetGitRepoHead7(self):

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        os.unlink(self.first_file1)
        self.assertFalse(os.path.exists(self.first_file1))

        v, r = git_lib.get_head_deleted_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        with open(self.first_file2, "w") as f:
            f.write("extra stuff")

        v, r = reset_git_repo.reset_git_repo_head(self.first_repo, self.rdb)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertTrue(any(self.first_file1 in s for s in r))

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        self.assertTrue(os.path.exists(self.first_file1))

    def testResetGitRepo_ResetGitRepoHead8(self):

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        os.unlink(self.first_file1)
        self.assertFalse(os.path.exists(self.first_file1))

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        with open(self.first_file2, "w") as f:
            f.write("extra stuff")

        v, r = reset_git_repo.reset_git_repo_head(self.first_repo, self.rdb)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertFalse(any(self.first_file1 in s for s in r))

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        self.assertFalse(os.path.exists(self.first_file1))

    def testResetGitRepo_ResetGitRepoStaged_Fail1(self):

        v, r = reset_git_repo.reset_git_repo_staged(self.nonrepo, self.rdb)
        self.assertFalse(v)

    def testResetGitRepo_ResetGitRepoStaged1(self):

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "w") as f:
            f.write("extra stuff")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        patch_file_filename = "1_reset_git_repo_staged_%s.patch" % (path_utils.basename_filtered(self.first_file1))
        test_patch_file = path_utils.concat_path(self.rdb_storage, "staged", patch_file_filename)
        self.assertFalse(os.path.exists(test_patch_file))

        v, r = reset_git_repo.reset_git_repo_staged(self.first_repo, self.rdb)
        self.assertTrue(v)
        self.assertTrue(os.path.exists(test_patch_file))

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

    def testResetGitRepo_ResetGitRepoStaged2(self):

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "w") as f:
            f.write("extra stuff")

        with open(self.first_file2, "w") as f:
            f.write("extra stuff")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)

        patch_file1_filename = "1_reset_git_repo_staged_%s.patch" % (path_utils.basename_filtered(self.first_file1))
        test_patch_file1 = path_utils.concat_path(self.rdb_storage, "staged", patch_file1_filename)
        self.assertFalse(os.path.exists(test_patch_file1))

        patch_file2_filename = "2_reset_git_repo_staged_%s.patch" % (path_utils.basename_filtered(self.first_file2))
        test_patch_file2 = path_utils.concat_path(self.rdb_storage, "staged", patch_file2_filename)
        self.assertFalse(os.path.exists(test_patch_file2))

        v, r = reset_git_repo.reset_git_repo_staged(self.first_repo, self.rdb)
        self.assertTrue(v)
        self.assertTrue(os.path.exists(test_patch_file1))
        self.assertTrue(os.path.exists(test_patch_file2))

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)

    def testResetGitRepo_ResetGitRepoStaged3(self):

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = reset_git_repo.reset_git_repo_staged(self.first_repo, self.rdb)
        self.assertTrue(v)

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

    def testResetGitRepo_ResetGitRepoStaged4(self):

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "w") as f:
            f.write("extra stuff")

        with open(self.first_file2, "w") as f:
            f.write("extra stuff")

        v, r = git_wrapper.stage(self.first_repo, [self.first_file2])
        self.assertTrue(v)

        v, r = git_lib.get_head_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        patch_file1_filename = "1_reset_git_repo_head_%s.patch" % (path_utils.basename_filtered(self.first_file1))
        test_patch_file1 = path_utils.concat_path(self.rdb_storage, "head", patch_file1_filename)
        self.assertFalse(os.path.exists(test_patch_file1))

        patch_file2_filename = "1_reset_git_repo_staged_%s.patch" % (path_utils.basename_filtered(self.first_file2))
        test_patch_file2 = path_utils.concat_path(self.rdb_storage, "staged", patch_file2_filename)
        self.assertFalse(os.path.exists(test_patch_file2))

        v, r = reset_git_repo.reset_git_repo_staged(self.first_repo, self.rdb)
        self.assertTrue(v)
        self.assertFalse(os.path.exists(test_patch_file1))
        self.assertTrue(os.path.exists(test_patch_file2))

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)

    def testResetGitRepo_ResetGitRepoStaged5(self):

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "w") as f:
            f.write("extra stuff")

        first_file3 = path_utils.concat_path(self.first_repo, "file3.txt")
        self.assertFalse(os.path.exists(first_file3))
        self.assertTrue(create_and_write_file.create_file_contents(first_file3, "dummy contents"))
        self.assertTrue(os.path.exists(first_file3))

        v, r = git_lib.get_unversioned_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_unversioned_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)

        patch_file1_filename = "1_reset_git_repo_staged_%s.patch" % (path_utils.basename_filtered(self.first_file1))
        test_patch_file1 = path_utils.concat_path(self.rdb_storage, "staged", patch_file1_filename)
        self.assertFalse(os.path.exists(test_patch_file1))

        patch_file3_filename = "2_reset_git_repo_staged_%s.patch" % (path_utils.basename_filtered(first_file3))
        test_patch_file3 = path_utils.concat_path(self.rdb_storage, "staged", patch_file3_filename)
        self.assertFalse(os.path.exists(test_patch_file3))

        v, r = reset_git_repo.reset_git_repo_staged(self.first_repo, self.rdb)
        self.assertTrue(v)
        self.assertTrue(os.path.exists(test_patch_file1))
        self.assertTrue(os.path.exists(test_patch_file3))

        v, r = git_lib.get_unversioned_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

    def testResetGitRepo_ResetGitRepoStaged6(self):

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        sub1 = path_utils.concat_path(self.first_repo, "sub1")
        os.mkdir(sub1)

        sub2 = path_utils.concat_path(sub1, "sub2")
        os.mkdir(sub2)

        sub1_sub2_file3 = path_utils.concat_path(sub2, "file3.txt")
        self.assertTrue(create_and_write_file.create_file_contents(sub1_sub2_file3, "dummy contents"))

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.first_repo, "more")
        self.assertTrue(v)

        self.assertTrue(os.path.exists(sub1_sub2_file3))

        with open(sub1_sub2_file3, "w") as f:
            f.write("extra stuff")

        v, r = git_wrapper.stage(self.first_repo,[sub1_sub2_file3])
        self.assertTrue(v)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        patch_file_filename = "1_reset_git_repo_staged_%s.patch" % (path_utils.basename_filtered(sub1_sub2_file3))
        test_patch_file = path_utils.concat_path(self.rdb_storage, "staged", "sub1", "sub2", patch_file_filename)
        self.assertFalse(os.path.exists(test_patch_file))

        v, r = reset_git_repo.reset_git_repo_staged(self.first_repo, self.rdb)
        self.assertTrue(v)
        self.assertTrue(os.path.exists(test_patch_file))

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

    def testResetGitRepo_ResetGitRepoStaged7(self):

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        os.unlink(self.first_file1)
        self.assertFalse(os.path.exists(self.first_file1))

        v, r = git_lib.get_head_deleted_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        with open(self.first_file2, "w") as f:
            f.write("extra stuff")

        v, r = reset_git_repo.reset_git_repo_staged(self.first_repo, self.rdb)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)
        self.assertFalse(any(self.first_file1 in s for s in r))

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)

        self.assertFalse(os.path.exists(self.first_file1))

    def testResetGitRepo_ResetGitRepoStaged8(self):

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        os.unlink(self.first_file1)
        self.assertFalse(os.path.exists(self.first_file1))

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        with open(self.first_file2, "w") as f:
            f.write("extra stuff")

        v, r = reset_git_repo.reset_git_repo_staged(self.first_repo, self.rdb)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertTrue(any(self.first_file1 in s for s in r))

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)

        self.assertFalse(os.path.exists(self.first_file1))

    def testResetGitRepo_ResetGitRepoStaged9(self):

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        os.unlink(self.first_file1)
        self.assertFalse(os.path.exists(self.first_file1))

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        with open(self.first_file2, "w") as f:
            f.write("extra stuff")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        patch_second_fn = "1_reset_git_repo_staged_%s.patch" % path_utils.basename_filtered(self.first_file2)
        patch_file_second = path_utils.concat_path(self.rdb_storage, "staged", patch_second_fn)
        self.assertFalse(os.path.exists(patch_file_second))

        v, r = reset_git_repo.reset_git_repo_staged(self.first_repo, self.rdb)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertTrue(any(self.first_file1 in s for s in r))
        self.assertTrue(os.path.exists(patch_file_second))

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)

        self.assertFalse(os.path.exists(self.first_file1))

    def testResetGitRepo_ResetGitRepoStaged10(self):

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        renamed_file = path_utils.concat_path(self.first_repo, "renamed.txt")
        self.assertFalse(os.path.exists(renamed_file))
        self.assertTrue(path_utils.copy_to_and_rename(self.first_file1, self.first_repo, "renamed.txt"))
        self.assertTrue(os.path.exists(renamed_file))
        os.unlink(self.first_file1)
        self.assertFalse(os.path.exists(self.first_file1))

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        with open(self.first_file2, "w") as f:
            f.write("extra stuff")

        v, r = reset_git_repo.reset_git_repo_staged(self.first_repo, self.rdb)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertTrue(any(renamed_file in s for s in r))

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)

        self.assertFalse(os.path.exists(self.first_file1))

    def testResetGitRepo_ResetGitRepoStash_Fail1(self):

        v, r = reset_git_repo.reset_git_repo_stash(self.nonrepo, self.rdb, -1)
        self.assertFalse(v)

    def testResetGitRepo_ResetGitRepoStash_Fail2(self):

        v, r = reset_git_repo.reset_git_repo_stash(self.first_repo, self.rdb, None)
        self.assertFalse(v)

    def testResetGitRepo_ResetGitRepoStash1(self):

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "w") as f:
            f.write("extra stuff")

        v, r = git_lib.get_head_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        v, r = git_wrapper.stash(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_head_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        patch_file_filename = "1_reset_git_repo_stash@{0}.patch"
        test_patch_file = path_utils.concat_path(self.rdb_storage, "stash", patch_file_filename)
        self.assertFalse(os.path.exists(test_patch_file))

        v, r = reset_git_repo.reset_git_repo_stash(self.first_repo, self.rdb, 1)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertTrue(patch_file_filename in r[0])
        self.assertTrue(os.path.exists(test_patch_file))
        with open(test_patch_file, "r") as f:
            self.assertTrue("extra stuff" in f.read())

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

    def testResetGitRepo_ResetGitRepoStash2(self):

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "w") as f:
            f.write("extra stuff")

        v, r = git_lib.get_head_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        v, r = git_wrapper.stash(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_head_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        patch_file_filename = "1_reset_git_repo_stash@{0}.patch"
        test_patch_file = path_utils.concat_path(self.rdb_storage, "stash", patch_file_filename)
        self.assertFalse(os.path.exists(test_patch_file))

        v, r = reset_git_repo.reset_git_repo_stash(self.first_repo, self.rdb, 0)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)
        self.assertFalse(os.path.exists(test_patch_file))

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

    def testResetGitRepo_ResetGitRepoStash3(self):

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "w") as f:
            f.write("extra stuff")

        v, r = git_lib.get_head_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        v, r = git_wrapper.stash(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_head_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        patch_file_filename = "1_reset_git_repo_stash@{0}.patch"
        test_patch_file = path_utils.concat_path(self.rdb_storage, "stash", patch_file_filename)
        self.assertFalse(os.path.exists(test_patch_file))

        v, r = reset_git_repo.reset_git_repo_stash(self.first_repo, self.rdb, 5)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertTrue(patch_file_filename in r[0])
        self.assertTrue(os.path.exists(test_patch_file))
        with open(test_patch_file, "r") as f:
            self.assertTrue("extra stuff" in f.read())

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

    def testResetGitRepo_ResetGitRepoStash4(self):

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "w") as f:
            f.write("extra stuff")

        v, r = git_lib.get_head_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        v, r = git_wrapper.stash(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_head_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        patch_file_filename = "1_reset_git_repo_stash@{0}.patch"
        test_patch_file = path_utils.concat_path(self.rdb_storage, "stash", patch_file_filename)
        self.assertFalse(os.path.exists(test_patch_file))

        v, r = reset_git_repo.reset_git_repo_stash(self.first_repo, self.rdb, 2)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertTrue(patch_file_filename in r[0])
        self.assertTrue(os.path.exists(test_patch_file))
        with open(test_patch_file, "r") as f:
            self.assertTrue("extra stuff" in f.read())

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

    def testResetGitRepo_ResetGitRepoStash5(self):

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "w") as f:
            f.write("extra stuff")

        v, r = git_lib.get_head_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        v, r = git_wrapper.stash(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_head_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        patch_file_filename = "1_reset_git_repo_stash@{0}.patch"
        test_patch_file = path_utils.concat_path(self.rdb_storage, "stash", patch_file_filename)
        self.assertFalse(os.path.exists(test_patch_file))

        v, r = reset_git_repo.reset_git_repo_stash(self.first_repo, self.rdb, -1)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertTrue(patch_file_filename in r[0])
        self.assertTrue(os.path.exists(test_patch_file))
        with open(test_patch_file, "r") as f:
            self.assertTrue("extra stuff" in f.read())

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

    def testResetGitRepo_ResetGitRepoStash6(self):

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "w") as f:
            f.write("extra stuff1")

        v, r = git_wrapper.stash(self.first_repo)
        self.assertTrue(v)

        with open(self.first_file2, "w") as f:
            f.write("extra stuff2")

        v, r = git_wrapper.stash(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_head_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        patch_file_filename1 = "1_reset_git_repo_stash@{0}.patch"
        test_patch_file1 = path_utils.concat_path(self.rdb_storage, "stash", patch_file_filename1)
        self.assertFalse(os.path.exists(test_patch_file1))

        patch_file_filename2 = "2_reset_git_repo_stash@{1}.patch"
        test_patch_file2 = path_utils.concat_path(self.rdb_storage, "stash", patch_file_filename2)
        self.assertFalse(os.path.exists(test_patch_file2))

        v, r = reset_git_repo.reset_git_repo_stash(self.first_repo, self.rdb, 2)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertTrue(patch_file_filename1 in r[0])
        self.assertTrue(patch_file_filename2 in r[1])
        self.assertTrue(os.path.exists(test_patch_file1))
        self.assertTrue(os.path.exists(test_patch_file2))
        with open(test_patch_file1, "r") as f:
            self.assertTrue("extra stuff2" in f.read())
        with open(test_patch_file2, "r") as f:
            self.assertTrue("extra stuff1" in f.read())

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

    def testResetGitRepo_ResetGitRepoStash7(self):

        first_file3 = path_utils.concat_path(self.first_repo, "file3.txt")
        self.assertFalse(os.path.exists(first_file3))
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file3.txt", "first-file3-content", "first-file3-msg")
        self.assertTrue(v)
        self.assertTrue(os.path.exists(first_file3))

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "w") as f:
            f.write("extra stuff1")

        v, r = git_wrapper.stash(self.first_repo)
        self.assertTrue(v)

        with open(self.first_file2, "w") as f:
            f.write("extra stuff2")

        v, r = git_wrapper.stash(self.first_repo)
        self.assertTrue(v)

        with open(first_file3, "w") as f:
            f.write("extra stuff3")

        v, r = git_wrapper.stash(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_head_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        patch_file_filename1 = "1_reset_git_repo_stash@{0}.patch"
        test_patch_file1 = path_utils.concat_path(self.rdb_storage, "stash", patch_file_filename1)
        self.assertFalse(os.path.exists(test_patch_file1))

        patch_file_filename2 = "2_reset_git_repo_stash@{1}.patch"
        test_patch_file2 = path_utils.concat_path(self.rdb_storage, "stash", patch_file_filename2)
        self.assertFalse(os.path.exists(test_patch_file2))

        v, r = reset_git_repo.reset_git_repo_stash(self.first_repo, self.rdb, 2)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertTrue(patch_file_filename1 in r[0])
        self.assertTrue(patch_file_filename2 in r[1])
        self.assertTrue(os.path.exists(test_patch_file1))
        self.assertTrue(os.path.exists(test_patch_file2))
        with open(test_patch_file1, "r") as f:
            self.assertTrue("extra stuff3" in f.read())
        with open(test_patch_file2, "r") as f:
            self.assertTrue("extra stuff2" in f.read())

        v, r = reset_git_repo.reset_git_repo_stash(self.first_repo, self.rdb, 2)
        self.assertFalse(v) # patch_file_filename1's pre-existence should prevent the operation from finishing successfully

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = git_lib.get_stash_list(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

    def testResetGitRepo_ResetGitRepoStash8(self):

        first_file3 = path_utils.concat_path(self.first_repo, "file3.txt")
        self.assertFalse(os.path.exists(first_file3))
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file3.txt", "first-file3-content", "first-file3-msg")
        self.assertTrue(v)
        self.assertTrue(os.path.exists(first_file3))

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "w") as f:
            f.write("extra stuff1")

        v, r = git_wrapper.stash(self.first_repo)
        self.assertTrue(v)

        with open(self.first_file2, "w") as f:
            f.write("extra stuff2")

        v, r = git_wrapper.stash(self.first_repo)
        self.assertTrue(v)

        with open(first_file3, "w") as f:
            f.write("extra stuff3")

        v, r = git_wrapper.stash(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_head_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        patch_file_filename1 = "1_reset_git_repo_stash@{0}.patch"
        test_patch_file1 = path_utils.concat_path(self.rdb_storage, "stash", patch_file_filename1)
        self.assertFalse(os.path.exists(test_patch_file1))

        patch_file_filename2 = "2_reset_git_repo_stash@{1}.patch"
        test_patch_file2 = path_utils.concat_path(self.rdb_storage, "stash", patch_file_filename2)
        self.assertFalse(os.path.exists(test_patch_file2))

        v, r = reset_git_repo.reset_git_repo_stash(self.first_repo, self.rdb, 2)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertTrue(patch_file_filename1 in r[0])
        self.assertTrue(patch_file_filename2 in r[1])
        self.assertTrue(os.path.exists(test_patch_file1))
        self.assertTrue(os.path.exists(test_patch_file2))
        with open(test_patch_file1, "r") as f:
            self.assertTrue("extra stuff3" in f.read())
        with open(test_patch_file2, "r") as f:
            self.assertTrue("extra stuff2" in f.read())

        v, r = git_lib.get_stash_list(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        os.unlink(test_patch_file1)
        self.assertFalse(os.path.exists(test_patch_file1))
        v, r = reset_git_repo.reset_git_repo_stash(self.first_repo, self.rdb, 2)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertTrue(patch_file_filename1 in r[0]) # has been recreated with the same name
        self.assertTrue(os.path.exists(test_patch_file1))
        with open(test_patch_file1, "r") as f:
            self.assertTrue("extra stuff1" in f.read())

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = git_lib.get_stash_list(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

    def testResetGitRepo_ResetGitRepoStash9(self):

        first_file3 = path_utils.concat_path(self.first_repo, "file3.txt")
        self.assertFalse(os.path.exists(first_file3))
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file3.txt", "first-file3-content", "first-file3-msg")
        self.assertTrue(v)
        self.assertTrue(os.path.exists(first_file3))

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "w") as f:
            f.write("extra stuff1")

        v, r = git_wrapper.stash(self.first_repo)
        self.assertTrue(v)

        with open(self.first_file2, "w") as f:
            f.write("extra stuff2")

        v, r = git_wrapper.stash(self.first_repo)
        self.assertTrue(v)

        with open(first_file3, "w") as f:
            f.write("extra stuff3")

        v, r = git_wrapper.stash(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_head_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        patch_file_filename1 = "1_reset_git_repo_stash@{0}.patch"
        test_patch_file1 = path_utils.concat_path(self.rdb_storage, "stash", patch_file_filename1)
        self.assertFalse(os.path.exists(test_patch_file1))

        patch_file_filename2 = "2_reset_git_repo_stash@{1}.patch"
        test_patch_file2 = path_utils.concat_path(self.rdb_storage, "stash", patch_file_filename2)
        self.assertFalse(os.path.exists(test_patch_file2))

        patch_file_filename3 = "3_reset_git_repo_stash@{2}.patch"
        test_patch_file3 = path_utils.concat_path(self.rdb_storage, "stash", patch_file_filename3)
        self.assertFalse(os.path.exists(test_patch_file3))

        v, r = reset_git_repo.reset_git_repo_stash(self.first_repo, self.rdb, -1)
        self.assertTrue(v)
        self.assertEqual(len(r), 3)
        self.assertTrue(patch_file_filename1 in r[0])
        self.assertTrue(patch_file_filename2 in r[1])
        self.assertTrue(patch_file_filename3 in r[2])
        self.assertTrue(os.path.exists(test_patch_file1))
        self.assertTrue(os.path.exists(test_patch_file2))
        self.assertTrue(os.path.exists(test_patch_file3))
        with open(test_patch_file1, "r") as f:
            self.assertTrue("extra stuff3" in f.read())
        with open(test_patch_file2, "r") as f:
            self.assertTrue("extra stuff2" in f.read())
        with open(test_patch_file3, "r") as f:
            self.assertTrue("extra stuff1" in f.read())

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

    def testResetGitRepo_ResetGitRepoStash10(self):

        first_file3 = path_utils.concat_path(self.first_repo, "file3.txt")
        self.assertFalse(os.path.exists(first_file3))
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file3.txt", "first-file3-content", "first-file3-msg")
        self.assertTrue(v)
        self.assertTrue(os.path.exists(first_file3))

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "w") as f:
            f.write("extra stuff")

        with open(self.first_file2, "w") as f:
            f.write("extra stuff2")

        with open(first_file3, "w") as f:
            f.write("extra stuff3")

        v, r = git_lib.get_head_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 3)

        v, r = reset_git_repo.reset_git_repo_stash(self.first_repo, self.rdb, -1)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 3)

    def testResetGitRepo_ResetGitRepoPrevious_Fail1(self):

        v, r = reset_git_repo.reset_git_repo_previous(self.nonrepo, self.rdb, 1)
        self.assertFalse(v)

    def testResetGitRepo_ResetGitRepoPrevious_Fail2(self):

        v, r = reset_git_repo.reset_git_repo_previous(self.first_repo, self.rdb, None)
        self.assertFalse(v)

    def testResetGitRepo_ResetGitRepoPrevious1(self):

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "w") as f:
            f.write("extra stuff1")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.first_repo, "commit-msg-2")
        self.assertTrue(v)

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = git_lib.get_previous_hash_list(self.first_repo, 1)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        hash_list = r

        patch_file_filename = "1_reset_git_repo_previous_%s.patch" % hash_list[0]
        test_patch_file = path_utils.concat_path(self.rdb_storage, "previous", patch_file_filename)
        self.assertFalse(os.path.exists(test_patch_file))

        v, r = reset_git_repo.reset_git_repo_previous(self.first_repo, self.rdb, 1)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertTrue(patch_file_filename in r[0])
        self.assertTrue(os.path.exists(test_patch_file))
        with open(test_patch_file, "r") as f:
            self.assertTrue("extra stuff1" in f.read())

    def testResetGitRepo_ResetGitRepoPrevious2(self):

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "w") as f:
            f.write("extra stuff1")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.first_repo, "commit-msg-2")
        self.assertTrue(v)

        with open(self.first_file2, "w") as f:
            f.write("extra stuff2")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.first_repo, "commit-msg-3")
        self.assertTrue(v)

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = git_lib.get_previous_hash_list(self.first_repo, 2)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        hash_list = r

        patch_file_filename1 = "1_reset_git_repo_previous_%s.patch" % hash_list[0]
        test_patch_file1 = path_utils.concat_path(self.rdb_storage, "previous", patch_file_filename1)
        self.assertFalse(os.path.exists(test_patch_file1))

        patch_file_filename2 = "2_reset_git_repo_previous_%s.patch" % hash_list[1]
        test_patch_file2 = path_utils.concat_path(self.rdb_storage, "previous", patch_file_filename2)
        self.assertFalse(os.path.exists(test_patch_file2))

        v, r = reset_git_repo.reset_git_repo_previous(self.first_repo, self.rdb, 2)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertTrue(patch_file_filename1 in r[0])
        self.assertTrue(os.path.exists(test_patch_file1))
        with open(test_patch_file1, "r") as f:
            self.assertTrue("extra stuff2" in f.read())
        self.assertTrue(patch_file_filename2 in r[1])
        self.assertTrue(os.path.exists(test_patch_file2))
        with open(test_patch_file2, "r") as f:
            self.assertTrue("extra stuff1" in f.read())

    def testResetGitRepo_ResetGitRepoPrevious3(self):

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = git_lib.get_previous_hash_list(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        hash_list = r

        patch_file_filename = "1_reset_git_repo_previous_%s.patch" % hash_list[0]
        test_patch_file = path_utils.concat_path(self.rdb_storage, "previous", patch_file_filename)
        self.assertFalse(os.path.exists(test_patch_file))

        v, r = reset_git_repo.reset_git_repo_previous(self.first_repo, self.rdb, 1)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertTrue(patch_file_filename in r[0])
        self.assertTrue(os.path.exists(test_patch_file))
        with open(test_patch_file, "r") as f:
            self.assertTrue("first-file2-content" in f.read())

    def testResetGitRepo_ResetGitRepoPrevious4(self):

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = git_lib.get_previous_hash_list(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        hash_list = r

        v, r = reset_git_repo.reset_git_repo_previous(self.first_repo, self.rdb, 2)
        self.assertFalse(v)

    def testResetGitRepo_ResetGitRepoUnversioned_Fail1(self):

        v, r = reset_git_repo.reset_git_repo_unversioned(self.nonrepo, self.rdb)
        self.assertFalse(v)

    def testResetGitRepo_ResetGitRepoUnversioned1(self):

        v, r = git_lib.get_unversioned_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        first_repo_unvfile73 = path_utils.concat_path(self.first_repo, "unvfile73.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_repo_unvfile73, "dummy contents, file73"))
        self.assertTrue(os.path.exists(first_repo_unvfile73))

        first_repo_sub = path_utils.concat_path(self.first_repo, "sub")
        self.assertFalse(os.path.exists(first_repo_sub))
        os.mkdir(first_repo_sub)
        self.assertTrue(os.path.exists(first_repo_sub))

        first_repo_sub_committed_file = path_utils.concat_path(first_repo_sub, "committed_file.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, path_utils.concat_path(path_utils.basename_filtered(first_repo_sub), path_utils.basename_filtered(first_repo_sub_committed_file)), "committed-file-content", "commit msg, keep subfolder")
        self.assertTrue(v)
        self.assertTrue(os.path.exists(first_repo_sub_committed_file))

        first_repo_sub_unvfile715 = path_utils.concat_path(first_repo_sub, "unvfile715.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_repo_sub_unvfile715, "dummy contents, file715"))
        self.assertTrue(os.path.exists(first_repo_sub_unvfile715))

        first_repo_anothersub = path_utils.concat_path(self.first_repo, "anothersub")
        self.assertFalse(os.path.exists(first_repo_anothersub))
        os.mkdir(first_repo_anothersub)
        self.assertTrue(os.path.exists(first_repo_anothersub))

        first_repo_anothersub_unvfile99 = path_utils.concat_path(first_repo_anothersub, "unvfile99.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_repo_anothersub_unvfile99, "dummy contents, file99"))
        self.assertTrue(os.path.exists(first_repo_anothersub_unvfile99))

        first_repo_anothersub_unvfile47 = path_utils.concat_path(first_repo_anothersub, "unvfile47.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_repo_anothersub_unvfile47, "dummy contents, file47"))
        self.assertTrue(os.path.exists(first_repo_anothersub_unvfile47))

        first_repo_unvfile73_backup_fn = "_%s_bk" % (path_utils.basename_filtered(first_repo_unvfile73))
        first_repo_sub_unvfile715_backup_fn = "_%s_bk" % (path_utils.basename_filtered(first_repo_sub_unvfile715))
        first_repo_anothersub_unvfile99_backup_fn = "_%s_bk" % (path_utils.basename_filtered(first_repo_anothersub_unvfile99))
        first_repo_anothersub_unvfile47_backup_fn = "_%s_bk" % (path_utils.basename_filtered(first_repo_anothersub_unvfile47))

        bk_items = fsquery.makecontentlist(self.rdb_storage, True, True, True, True, True, True, None)
        self.assertFalse(any(first_repo_unvfile73_backup_fn in s for s in bk_items))
        self.assertFalse(any(first_repo_sub_unvfile715_backup_fn in s for s in bk_items))
        self.assertFalse(any(first_repo_anothersub_unvfile99_backup_fn in s for s in bk_items))
        self.assertFalse(any(first_repo_anothersub_unvfile47_backup_fn in s for s in bk_items))

        v, r = git_lib.get_unversioned_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 4)

        v, r = reset_git_repo.reset_git_repo_unversioned(self.first_repo, self.rdb)
        self.assertTrue(v)
        self.assertTrue(any(first_repo_unvfile73_backup_fn in s for s in r))
        self.assertTrue(any(first_repo_sub_unvfile715_backup_fn in s for s in r))
        self.assertTrue(any(first_repo_anothersub_unvfile99_backup_fn in s for s in r))
        self.assertTrue(any(first_repo_anothersub_unvfile47_backup_fn in s for s in r))

        bk_items = fsquery.makecontentlist(self.rdb_storage, True, True, True, True, True, True, None)
        self.assertTrue(any(first_repo_unvfile73_backup_fn in s for s in bk_items))
        self.assertTrue(any(first_repo_sub_unvfile715_backup_fn in s for s in bk_items))
        self.assertTrue(any(first_repo_anothersub_unvfile99_backup_fn in s for s in bk_items))
        self.assertTrue(any(first_repo_anothersub_unvfile47_backup_fn in s for s in bk_items))

        v, r = git_lib.get_unversioned_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        self.assertTrue(os.path.exists(first_repo_sub))
        self.assertFalse(os.path.exists(first_repo_anothersub))

    def testResetGitRepo_ResetGitRepoUnversioned2(self):

        v, r = git_lib.get_unversioned_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        first_repo_unvfile73 = path_utils.concat_path(self.first_repo, "unvfile73.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_repo_unvfile73, "dummy contents, file73"))
        self.assertTrue(os.path.exists(first_repo_unvfile73))

        first_repo_sub = path_utils.concat_path(self.first_repo, "sub")
        self.assertFalse(os.path.exists(first_repo_sub))
        os.mkdir(first_repo_sub)
        self.assertTrue(os.path.exists(first_repo_sub))

        first_repo_sub_committed_file = path_utils.concat_path(first_repo_sub, "committed_file.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, path_utils.concat_path(path_utils.basename_filtered(first_repo_sub), path_utils.basename_filtered(first_repo_sub_committed_file)), "committed-file-content", "commit msg, keep subfolder")
        self.assertTrue(v)
        self.assertTrue(os.path.exists(first_repo_sub_committed_file))

        first_repo_sub_unvfile715 = path_utils.concat_path(first_repo_sub, "unvfile715.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_repo_sub_unvfile715, "dummy contents, file715"))
        self.assertTrue(os.path.exists(first_repo_sub_unvfile715))

        first_repo_anothersub = path_utils.concat_path(self.first_repo, "anothersub")
        self.assertFalse(os.path.exists(first_repo_anothersub))
        os.mkdir(first_repo_anothersub)
        self.assertTrue(os.path.exists(first_repo_anothersub))

        first_repo_anothersub_unvfile99 = path_utils.concat_path(first_repo_anothersub, "unvfile99.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_repo_anothersub_unvfile99, "dummy contents, file99"))
        self.assertTrue(os.path.exists(first_repo_anothersub_unvfile99))

        first_repo_anothersub_unvfile47 = path_utils.concat_path(first_repo_anothersub, "unvfile47.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_repo_anothersub_unvfile47, "dummy contents, file47"))
        self.assertTrue(os.path.exists(first_repo_anothersub_unvfile47))

        first_repo_unvfile73_backup_fn = "_%s_bk" % (path_utils.basename_filtered(first_repo_unvfile73))
        first_repo_sub_unvfile715_backup_fn = "_%s_bk" % (path_utils.basename_filtered(first_repo_sub_unvfile715))
        first_repo_anothersub_unvfile99_backup_fn = "_%s_bk" % (path_utils.basename_filtered(first_repo_anothersub_unvfile99))
        first_repo_anothersub_unvfile47_backup_fn = "_%s_bk" % (path_utils.basename_filtered(first_repo_anothersub_unvfile47))

        bk_items = fsquery.makecontentlist(self.rdb_storage, True, True, True, True, True, True, None)
        self.assertFalse(any(first_repo_unvfile73_backup_fn in s for s in bk_items))
        self.assertFalse(any(first_repo_sub_unvfile715_backup_fn in s for s in bk_items))
        self.assertFalse(any(first_repo_anothersub_unvfile99_backup_fn in s for s in bk_items))
        self.assertFalse(any(first_repo_anothersub_unvfile47_backup_fn in s for s in bk_items))

        v, r = git_lib.get_unversioned_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 4)

        v, r = git_wrapper.stage(self.first_repo, [first_repo_anothersub_unvfile47])
        self.assertTrue(v)

        v, r = reset_git_repo.reset_git_repo_unversioned(self.first_repo, self.rdb)
        self.assertTrue(v)
        self.assertTrue(any(first_repo_unvfile73_backup_fn in s for s in r))
        self.assertTrue(any(first_repo_sub_unvfile715_backup_fn in s for s in r))
        self.assertTrue(any(first_repo_anothersub_unvfile99_backup_fn in s for s in r))
        self.assertFalse(any(first_repo_anothersub_unvfile47_backup_fn in s for s in r))

        bk_items = fsquery.makecontentlist(self.rdb_storage, True, True, True, True, True, True, None)
        self.assertTrue(any(first_repo_unvfile73_backup_fn in s for s in bk_items))
        self.assertTrue(any(first_repo_sub_unvfile715_backup_fn in s for s in bk_items))
        self.assertTrue(any(first_repo_anothersub_unvfile99_backup_fn in s for s in bk_items))
        self.assertFalse(any(first_repo_anothersub_unvfile47_backup_fn in s for s in bk_items))

        v, r = git_lib.get_unversioned_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        self.assertTrue(os.path.exists(first_repo_sub))
        self.assertTrue(os.path.exists(first_repo_anothersub))

    def testResetGitRepo_ResetGitRepo_Fail1(self):

        v, r = reset_git_repo.reset_git_repo(self.nonrepo, None, False, 0, False, 0)
        self.assertFalse(v)

    def testResetGitRepo_ResetGitRepo_Fail2(self):

        test_bare_repo = path_utils.concat_path(self.test_dir, "test_bare")
        v, r = git_wrapper.init(self.test_dir, "test_bare", True)
        self.assertTrue(v)

        v, r = reset_git_repo.reset_git_repo(test_bare_repo, None, False, 0, False, 0)
        self.assertFalse(v)

    def testResetGitRepo_ResetGitRepo_Fail3(self):

        base_patch_backup_folder = path_utils.concat_path(self.test_dir, "base_patch_backup_folder")
        with mock.patch("mvtools_envvars.mvtools_envvar_read_temp_path", return_value=(True, base_patch_backup_folder)):
            v, r = reset_git_repo.reset_git_repo(self.first_repo, False, False, 0, False, 0)
            self.assertFalse(v)

    def testResetGitRepo_ResetGitRepo_Fail4(self):

        base_patch_backup_folder = path_utils.concat_path(self.test_dir, "base_patch_backup_folder")
        os.mkdir(base_patch_backup_folder)
        fixed_timestamp = "fixed_timestamp"
        dirname_patch_backup_folder = "%s_reset_git_repo_backup_%s" % (path_utils.basename_filtered(self.first_repo), fixed_timestamp)
        final_patch_backup_folder = path_utils.concat_path(base_patch_backup_folder, dirname_patch_backup_folder)
        os.mkdir(final_patch_backup_folder)

        with mock.patch("mvtools_envvars.mvtools_envvar_read_temp_path", return_value=(True, base_patch_backup_folder)):
            with mock.patch("maketimestamp.get_timestamp_now_compact", return_value=fixed_timestamp):
                v, r = reset_git_repo.reset_git_repo(self.first_repo, False, False, 0, False, 0)
                self.assertFalse(v)

    def testResetGitRepo_ResetGitRepo1(self):

        base_patch_backup_folder = path_utils.concat_path(self.test_dir, "base_patch_backup_folder")
        os.mkdir(base_patch_backup_folder)
        fixed_timestamp = "fixed_timestamp"
        dirname_patch_backup_folder = "%s_reset_git_repo_backup_%s" % (path_utils.basename_filtered(self.first_repo), fixed_timestamp)
        final_patch_backup_folder = path_utils.concat_path(base_patch_backup_folder, dirname_patch_backup_folder)

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with mock.patch("mvtools_envvars.mvtools_envvar_read_temp_path", return_value=(True, base_patch_backup_folder)):
            with mock.patch("maketimestamp.get_timestamp_now_compact", return_value=fixed_timestamp):
                v, r = reset_git_repo.reset_git_repo(self.first_repo, False, False, 0, False, 0)
                self.assertTrue(v)
                self.assertEqual(len(r), 0)

    def testResetGitRepo_ResetGitRepo2(self):

        base_patch_backup_folder = path_utils.concat_path(self.test_dir, "base_patch_backup_folder")
        os.mkdir(base_patch_backup_folder)
        fixed_timestamp = "fixed_timestamp"
        dirname_patch_backup_folder = "%s_reset_git_repo_backup_%s" % (path_utils.basename_filtered(self.first_repo), fixed_timestamp)
        final_patch_backup_folder = path_utils.concat_path(base_patch_backup_folder, dirname_patch_backup_folder)

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "w") as f:
            f.write("extra stuff")

        v, r = git_lib.get_head_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        file1_patch_filename = path_utils.concat_path(final_patch_backup_folder, "head", "1_reset_git_repo_head_file1.txt.patch")
        self.assertFalse(os.path.exists(file1_patch_filename))

        with mock.patch("mvtools_envvars.mvtools_envvar_read_temp_path", return_value=(True, base_patch_backup_folder)):
            with mock.patch("maketimestamp.get_timestamp_now_compact", return_value=fixed_timestamp):
                v, r = reset_git_repo.reset_git_repo(self.first_repo, True, False, 0, False, 0)
                self.assertTrue(v)
                self.assertEqual(len(r), 1)
                self.assertTrue(file1_patch_filename in r[0])

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)
        self.assertTrue(os.path.exists(file1_patch_filename))

    def testResetGitRepo_ResetGitRepo3(self):

        base_patch_backup_folder = path_utils.concat_path(self.test_dir, "base_patch_backup_folder")
        os.mkdir(base_patch_backup_folder)
        fixed_timestamp = "fixed_timestamp"
        dirname_patch_backup_folder = "%s_reset_git_repo_backup_%s" % (path_utils.basename_filtered(self.first_repo), fixed_timestamp)
        final_patch_backup_folder = path_utils.concat_path(base_patch_backup_folder, dirname_patch_backup_folder)

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "w") as f:
            f.write("extra stuff")

        with open(self.first_file2, "w") as f:
            f.write("extra stuff")

        v, r = git_lib.get_head_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)

        file1_patch_filename = path_utils.concat_path(final_patch_backup_folder, "head", "1_reset_git_repo_head_file1.txt.patch")
        file2_patch_filename = path_utils.concat_path(final_patch_backup_folder, "head", "2_reset_git_repo_head_file2.txt.patch")
        self.assertFalse(os.path.exists(file1_patch_filename))
        self.assertFalse(os.path.exists(file2_patch_filename))

        with mock.patch("mvtools_envvars.mvtools_envvar_read_temp_path", return_value=(True, base_patch_backup_folder)):
            with mock.patch("maketimestamp.get_timestamp_now_compact", return_value=fixed_timestamp):
                v, r = reset_git_repo.reset_git_repo(self.first_repo, True, False, 0, False, 0)
                self.assertTrue(v)
                self.assertEqual(len(r), 2)
                self.assertTrue(file1_patch_filename in r[0])
                self.assertTrue(file2_patch_filename in r[1])

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        self.assertTrue(os.path.exists(file1_patch_filename))
        self.assertTrue(os.path.exists(file2_patch_filename))

    def testResetGitRepo_ResetGitRepo4(self):

        base_patch_backup_folder = path_utils.concat_path(self.test_dir, "base_patch_backup_folder")
        os.mkdir(base_patch_backup_folder)
        fixed_timestamp = "fixed_timestamp"
        dirname_patch_backup_folder = "%s_reset_git_repo_backup_%s" % (path_utils.basename_filtered(self.first_repo), fixed_timestamp)
        final_patch_backup_folder = path_utils.concat_path(base_patch_backup_folder, dirname_patch_backup_folder)

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        self.assertTrue(os.path.exists(self.first_file1))
        os.unlink(self.first_file1)
        self.assertFalse(os.path.exists(self.first_file1))

        v, r = git_lib.get_head_deleted_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        with mock.patch("mvtools_envvars.mvtools_envvar_read_temp_path", return_value=(True, base_patch_backup_folder)):
            with mock.patch("maketimestamp.get_timestamp_now_compact", return_value=fixed_timestamp):
                v, r = reset_git_repo.reset_git_repo(self.first_repo, True, False, 0, False, 0)
                self.assertTrue(v)
                self.assertTrue(any(self.first_file1 in s for s in r))

        v, r = git_lib.get_head_deleted_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        file1_patch_filename = path_utils.concat_path(final_patch_backup_folder, "head", "1_reset_git_repo_head_file1.txt.patch")
        self.assertFalse(os.path.exists(file1_patch_filename))

    # mvtodo: disabled
    """
    def testResetGitRepo_ResetGitRepo5(self):

        base_patch_backup_folder = path_utils.concat_path(self.test_dir, "base_patch_backup_folder")
        os.mkdir(base_patch_backup_folder)
        fixed_timestamp = "fixed_timestamp"
        dirname_patch_backup_folder = "%s_reset_git_repo_backup_%s" % (path_utils.basename_filtered(self.first_repo), fixed_timestamp)
        final_patch_backup_folder = path_utils.concat_path(base_patch_backup_folder, dirname_patch_backup_folder)

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "w") as f:
            f.write("extra stuff")

        v, r = git_lib.get_head_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        with mock.patch("mvtools_envvars.mvtools_envvar_read_temp_path", return_value=(True, base_patch_backup_folder)):
            with mock.patch("maketimestamp.get_timestamp_now_compact", return_value=fixed_timestamp):
                v, r = reset_git_repo.reset_git_repo(self.first_repo, [self.first_file1])
                self.assertTrue(v)
                # mvtodo: check r too

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        file1_patch_filename = path_utils.concat_path(final_patch_backup_folder, "head", "1_reset_git_repo_head_file1.txt.patch")
        self.assertTrue(os.path.exists(file1_patch_filename))

    def testResetGitRepo_ResetGitRepo6(self):

        base_patch_backup_folder = path_utils.concat_path(self.test_dir, "base_patch_backup_folder")
        os.mkdir(base_patch_backup_folder)
        fixed_timestamp = "fixed_timestamp"
        dirname_patch_backup_folder = "%s_reset_git_repo_backup_%s" % (path_utils.basename_filtered(self.first_repo), fixed_timestamp)
        final_patch_backup_folder = path_utils.concat_path(base_patch_backup_folder, dirname_patch_backup_folder)

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "w") as f:
            f.write("extra stuff")

        with open(self.first_file2, "w") as f:
            f.write("extra stuff")

        v, r = git_lib.get_head_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)

        with mock.patch("mvtools_envvars.mvtools_envvar_read_temp_path", return_value=(True, base_patch_backup_folder)):
            with mock.patch("maketimestamp.get_timestamp_now_compact", return_value=fixed_timestamp):
                v, r = reset_git_repo.reset_git_repo(self.first_repo, [self.first_file1, self.first_file2])
                self.assertTrue(v)
                # mvtodo: check r too

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        file1_patch_filename = path_utils.concat_path(final_patch_backup_folder, "head", "1_reset_git_repo_head_file1.txt.patch")
        file2_patch_filename = path_utils.concat_path(final_patch_backup_folder, "head", "2_reset_git_repo_head_file2.txt.patch")
        self.assertTrue(os.path.exists(file1_patch_filename))
        self.assertTrue(os.path.exists(file2_patch_filename))

    def testResetGitRepo_ResetGitRepo7(self):

        base_patch_backup_folder = path_utils.concat_path(self.test_dir, "base_patch_backup_folder")
        os.mkdir(base_patch_backup_folder)
        fixed_timestamp = "fixed_timestamp"
        dirname_patch_backup_folder = "%s_reset_git_repo_backup_%s" % (path_utils.basename_filtered(self.first_repo), fixed_timestamp)
        final_patch_backup_folder = path_utils.concat_path(base_patch_backup_folder, dirname_patch_backup_folder)

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "w") as f:
            f.write("extra stuff")

        v, r = git_wrapper.stage(self.first_repo, [self.first_file1])
        self.assertTrue(v)

        with open(self.first_file2, "w") as f:
            f.write("extra stuff")

        v, r = git_lib.get_head_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        with mock.patch("mvtools_envvars.mvtools_envvar_read_temp_path", return_value=(True, base_patch_backup_folder)):
            with mock.patch("maketimestamp.get_timestamp_now_compact", return_value=fixed_timestamp):
                v, r = reset_git_repo.reset_git_repo(self.first_repo, [self.first_file1, self.first_file2])
                self.assertTrue(v)
                # mvtodo: check r too

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        file1_patch_filename = path_utils.concat_path(final_patch_backup_folder, "head", "1_reset_git_repo_head_file1.txt.patch")
        file2_patch_filename = path_utils.concat_path(final_patch_backup_folder, "head", "2_reset_git_repo_head_file2.txt.patch")
        self.assertTrue(os.path.exists(file1_patch_filename))
        self.assertTrue(os.path.exists(file2_patch_filename))
    """

    def testResetGitRepo_ResetGitRepo8(self):

        base_patch_backup_folder = path_utils.concat_path(self.test_dir, "base_patch_backup_folder")
        os.mkdir(base_patch_backup_folder)
        fixed_timestamp = "fixed_timestamp"
        dirname_patch_backup_folder = "%s_reset_git_repo_backup_%s" % (path_utils.basename_filtered(self.first_repo), fixed_timestamp)
        final_patch_backup_folder = path_utils.concat_path(base_patch_backup_folder, dirname_patch_backup_folder)

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "w") as f:
            f.write("extra stuff")

        first_file3 = path_utils.concat_path(self.first_repo, "file3.txt")
        self.assertFalse(os.path.exists(first_file3))
        self.assertTrue(create_and_write_file.create_file_contents(first_file3, "dummy contents"))
        self.assertTrue(os.path.exists(first_file3))

        v, r = git_lib.get_unversioned_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        v, r = git_lib.get_head_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_unversioned_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)

        with mock.patch("mvtools_envvars.mvtools_envvar_read_temp_path", return_value=(True, base_patch_backup_folder)):
            with mock.patch("maketimestamp.get_timestamp_now_compact", return_value=fixed_timestamp):
                v, r = reset_git_repo.reset_git_repo(self.first_repo, True, False, 0, False, 0)
                self.assertTrue(v)
                self.assertEqual(len(r), 0)

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = git_lib.get_unversioned_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        file1_patch_filename = path_utils.concat_path(final_patch_backup_folder, "head", "1_reset_git_repo_head_file1.txt.patch")
        file3_patch_filename = path_utils.concat_path(final_patch_backup_folder, "head", "2_reset_git_repo_head_file3.txt.patch")
        self.assertFalse(os.path.exists(file1_patch_filename))
        self.assertFalse(os.path.exists(file3_patch_filename))

    def testResetGitRepo_ResetGitRepo9(self):

        base_patch_backup_folder = path_utils.concat_path(self.test_dir, "base_patch_backup_folder")
        os.mkdir(base_patch_backup_folder)
        fixed_timestamp = "fixed_timestamp"
        dirname_patch_backup_folder = "%s_reset_git_repo_backup_%s" % (path_utils.basename_filtered(self.first_repo), fixed_timestamp)
        final_patch_backup_folder = path_utils.concat_path(base_patch_backup_folder, dirname_patch_backup_folder)

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "w") as f:
            f.write("extra stuff")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        file1_patch_filename = path_utils.concat_path(final_patch_backup_folder, "staged", "1_reset_git_repo_staged_file1.txt.patch")
        self.assertFalse(os.path.exists(file1_patch_filename))

        with mock.patch("mvtools_envvars.mvtools_envvar_read_temp_path", return_value=(True, base_patch_backup_folder)):
            with mock.patch("maketimestamp.get_timestamp_now_compact", return_value=fixed_timestamp):
                v, r = reset_git_repo.reset_git_repo(self.first_repo, False, True, 0, False, 0)
                self.assertTrue(v)
                self.assertEqual(len(r), 1)
                self.assertTrue(file1_patch_filename in r[0])

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertTrue(os.path.exists(file1_patch_filename))

    def testResetGitRepo_ResetGitRepo10(self):

        base_patch_backup_folder = path_utils.concat_path(self.test_dir, "base_patch_backup_folder")
        os.mkdir(base_patch_backup_folder)
        fixed_timestamp = "fixed_timestamp"
        dirname_patch_backup_folder = "%s_reset_git_repo_backup_%s" % (path_utils.basename_filtered(self.first_repo), fixed_timestamp)
        final_patch_backup_folder = path_utils.concat_path(base_patch_backup_folder, dirname_patch_backup_folder)

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "w") as f:
            f.write("extra stuff")

        with open(self.first_file2, "w") as f:
            f.write("extra stuff")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)

        file1_patch_filename = path_utils.concat_path(final_patch_backup_folder, "staged", "1_reset_git_repo_staged_file1.txt.patch")
        file2_patch_filename = path_utils.concat_path(final_patch_backup_folder, "staged", "2_reset_git_repo_staged_file2.txt.patch")
        self.assertFalse(os.path.exists(file1_patch_filename))
        self.assertFalse(os.path.exists(file2_patch_filename))

        with mock.patch("mvtools_envvars.mvtools_envvar_read_temp_path", return_value=(True, base_patch_backup_folder)):
            with mock.patch("maketimestamp.get_timestamp_now_compact", return_value=fixed_timestamp):
                v, r = reset_git_repo.reset_git_repo(self.first_repo, False, True, 0, False, 0)
                self.assertTrue(v)
                self.assertEqual(len(r), 2)
                self.assertTrue(file1_patch_filename in r[0])
                self.assertTrue(file2_patch_filename in r[1])

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)

        self.assertTrue(os.path.exists(file1_patch_filename))
        self.assertTrue(os.path.exists(file2_patch_filename))

    # mvtodo: disabled
    """
    def testResetGitRepo_ResetGitRepo11(self):

        base_patch_backup_folder = path_utils.concat_path(self.test_dir, "base_patch_backup_folder")
        os.mkdir(base_patch_backup_folder)
        fixed_timestamp = "fixed_timestamp"
        dirname_patch_backup_folder = "%s_reset_git_repo_backup_%s" % (path_utils.basename_filtered(self.first_repo), fixed_timestamp)
        final_patch_backup_folder = path_utils.concat_path(base_patch_backup_folder, dirname_patch_backup_folder)

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "w") as f:
            f.write("extra stuff")

        v, r = git_lib.get_head_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        with mock.patch("mvtools_envvars.mvtools_envvar_read_temp_path", return_value=(True, base_patch_backup_folder)):
            with mock.patch("maketimestamp.get_timestamp_now_compact", return_value=fixed_timestamp):
                v, r = reset_git_repo.reset_git_repo(self.first_repo, [self.first_file1])
                self.assertTrue(v)
                # mvtodo: check r too

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        file1_patch_filename = path_utils.concat_path(final_patch_backup_folder, "head", "1_reset_git_repo_head_file1.txt.patch")
        self.assertTrue(os.path.exists(file1_patch_filename))

    def testResetGitRepo_ResetGitRepo12(self):

        base_patch_backup_folder = path_utils.concat_path(self.test_dir, "base_patch_backup_folder")
        os.mkdir(base_patch_backup_folder)
        fixed_timestamp = "fixed_timestamp"
        dirname_patch_backup_folder = "%s_reset_git_repo_backup_%s" % (path_utils.basename_filtered(self.first_repo), fixed_timestamp)
        final_patch_backup_folder = path_utils.concat_path(base_patch_backup_folder, dirname_patch_backup_folder)

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "w") as f:
            f.write("extra stuff")

        with open(self.first_file2, "w") as f:
            f.write("extra stuff")

        v, r = git_lib.get_head_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)

        with mock.patch("mvtools_envvars.mvtools_envvar_read_temp_path", return_value=(True, base_patch_backup_folder)):
            with mock.patch("maketimestamp.get_timestamp_now_compact", return_value=fixed_timestamp):
                v, r = reset_git_repo.reset_git_repo(self.first_repo, [self.first_file1, self.first_file2])
                self.assertTrue(v)
                # mvtodo: check r too

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        file1_patch_filename = path_utils.concat_path(final_patch_backup_folder, "head", "1_reset_git_repo_head_file1.txt.patch")
        file2_patch_filename = path_utils.concat_path(final_patch_backup_folder, "head", "2_reset_git_repo_head_file2.txt.patch")
        self.assertTrue(os.path.exists(file1_patch_filename))
        self.assertTrue(os.path.exists(file2_patch_filename))

    def testResetGitRepo_ResetGitRepo13(self):

        base_patch_backup_folder = path_utils.concat_path(self.test_dir, "base_patch_backup_folder")
        os.mkdir(base_patch_backup_folder)
        fixed_timestamp = "fixed_timestamp"
        dirname_patch_backup_folder = "%s_reset_git_repo_backup_%s" % (path_utils.basename_filtered(self.first_repo), fixed_timestamp)
        final_patch_backup_folder = path_utils.concat_path(base_patch_backup_folder, dirname_patch_backup_folder)

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "w") as f:
            f.write("extra stuff")

        v, r = git_wrapper.stage(self.first_repo, [self.first_file1])
        self.assertTrue(v)

        with open(self.first_file2, "w") as f:
            f.write("extra stuff")

        v, r = git_lib.get_head_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        with mock.patch("mvtools_envvars.mvtools_envvar_read_temp_path", return_value=(True, base_patch_backup_folder)):
            with mock.patch("maketimestamp.get_timestamp_now_compact", return_value=fixed_timestamp):
                v, r = reset_git_repo.reset_git_repo(self.first_repo, [self.first_file1, self.first_file2])
                self.assertTrue(v)
                # mvtodo: check r too

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        file1_patch_filename = path_utils.concat_path(final_patch_backup_folder, "head", "1_reset_git_repo_head_file1.txt.patch")
        file2_patch_filename = path_utils.concat_path(final_patch_backup_folder, "head", "2_reset_git_repo_head_file2.txt.patch")
        self.assertTrue(os.path.exists(file1_patch_filename))
        self.assertTrue(os.path.exists(file2_patch_filename))
    """

    def testResetGitRepo_ResetGitRepo14(self):

        base_patch_backup_folder = path_utils.concat_path(self.test_dir, "base_patch_backup_folder")
        os.mkdir(base_patch_backup_folder)
        fixed_timestamp = "fixed_timestamp"
        dirname_patch_backup_folder = "%s_reset_git_repo_backup_%s" % (path_utils.basename_filtered(self.first_repo), fixed_timestamp)
        final_patch_backup_folder = path_utils.concat_path(base_patch_backup_folder, dirname_patch_backup_folder)

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "w") as f:
            f.write("extra stuff")

        first_file3 = path_utils.concat_path(self.first_repo, "file3.txt")
        self.assertFalse(os.path.exists(first_file3))
        self.assertTrue(create_and_write_file.create_file_contents(first_file3, "dummy contents"))
        self.assertTrue(os.path.exists(first_file3))

        v, r = git_lib.get_unversioned_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        v, r = git_lib.get_head_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        v, r = git_wrapper.stage(self.first_repo, [self.first_file1, first_file3])
        self.assertTrue(v)

        v, r = git_lib.get_unversioned_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)

        file1_patch_filename = path_utils.concat_path(final_patch_backup_folder, "staged", "1_reset_git_repo_staged_file1.txt.patch")
        file3_patch_filename = path_utils.concat_path(final_patch_backup_folder, "staged", "2_reset_git_repo_staged_file3.txt.patch")
        self.assertFalse(os.path.exists(file1_patch_filename))
        self.assertFalse(os.path.exists(file3_patch_filename))

        with mock.patch("mvtools_envvars.mvtools_envvar_read_temp_path", return_value=(True, base_patch_backup_folder)):
            with mock.patch("maketimestamp.get_timestamp_now_compact", return_value=fixed_timestamp):
                v, r = reset_git_repo.reset_git_repo(self.first_repo, False, True, 0, False, 0)
                self.assertTrue(v)
                self.assertEqual(len(r), 2)
                self.assertTrue(file1_patch_filename in r[0])
                self.assertTrue(file3_patch_filename in r[1])

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        v, r = git_lib.get_unversioned_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        self.assertTrue(os.path.exists(file1_patch_filename))
        self.assertTrue(os.path.exists(file3_patch_filename))

    def testResetGitRepo_ResetGitRepo15(self):

        base_patch_backup_folder = path_utils.concat_path(self.test_dir, "base_patch_backup_folder")
        os.mkdir(base_patch_backup_folder)
        fixed_timestamp = "fixed_timestamp"
        dirname_patch_backup_folder = "%s_reset_git_repo_backup_%s" % (path_utils.basename_filtered(self.first_repo), fixed_timestamp)
        final_patch_backup_folder = path_utils.concat_path(base_patch_backup_folder, dirname_patch_backup_folder)

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        self.assertTrue(os.path.exists(self.first_file1))
        os.unlink(self.first_file1)
        self.assertFalse(os.path.exists(self.first_file1))

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_staged_deleted_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        with mock.patch("mvtools_envvars.mvtools_envvar_read_temp_path", return_value=(True, base_patch_backup_folder)):
            with mock.patch("maketimestamp.get_timestamp_now_compact", return_value=fixed_timestamp):
                v, r = reset_git_repo.reset_git_repo(self.first_repo, False, True, 0, False, 0)
                self.assertTrue(v)
                self.assertEqual(len(r), 1)
                self.assertTrue(self.first_file1 in r[0])

        v, r = git_lib.get_staged_deleted_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = git_lib.get_head_deleted_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        file1_patch_filename = path_utils.concat_path(final_patch_backup_folder, "staged", "1_reset_git_repo_staged_file1.txt.patch")
        self.assertFalse(os.path.exists(file1_patch_filename))

    def testResetGitRepo_ResetGitRepo16(self):

        base_patch_backup_folder = path_utils.concat_path(self.test_dir, "base_patch_backup_folder")
        os.mkdir(base_patch_backup_folder)
        fixed_timestamp = "fixed_timestamp"
        dirname_patch_backup_folder = "%s_reset_git_repo_backup_%s" % (path_utils.basename_filtered(self.first_repo), fixed_timestamp)
        final_patch_backup_folder = path_utils.concat_path(base_patch_backup_folder, dirname_patch_backup_folder)

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        first_file1_renamed = path_utils.concat_path(self.first_repo, "file1_renamed.txt")
        self.assertTrue(os.path.exists(self.first_file1))
        self.assertFalse(os.path.exists(first_file1_renamed))
        self.assertTrue(path_utils.copy_to_and_rename(self.first_file1, path_utils.dirname_filtered(self.first_file1), path_utils.basename_filtered(first_file1_renamed)))
        os.unlink(self.first_file1)
        self.assertFalse(os.path.exists(self.first_file1))
        self.assertTrue(os.path.exists(first_file1_renamed))

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_staged_renamed_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertEqual(first_file1_renamed, r[0][1])

        with mock.patch("mvtools_envvars.mvtools_envvar_read_temp_path", return_value=(True, base_patch_backup_folder)):
            with mock.patch("maketimestamp.get_timestamp_now_compact", return_value=fixed_timestamp):
                v, r = reset_git_repo.reset_git_repo(self.first_repo, False, True, 0, False, 0)
                self.assertTrue(v)
                self.assertEqual(len(r), 1)
                self.assertTrue(first_file1_renamed in r[0])

        v, r = git_lib.get_staged_renamed_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = git_lib.get_staged_deleted_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = git_lib.get_head_deleted_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertTrue(self.first_file1 in r)

        file1_patch_filename = path_utils.concat_path(final_patch_backup_folder, "staged", "1_reset_git_repo_staged_file1.txt.patch")
        self.assertFalse(os.path.exists(file1_patch_filename))

    def testResetGitRepo_ResetGitRepo17(self):

        base_patch_backup_folder = path_utils.concat_path(self.test_dir, "base_patch_backup_folder")
        os.mkdir(base_patch_backup_folder)
        fixed_timestamp = "fixed_timestamp"
        dirname_patch_backup_folder = "%s_reset_git_repo_backup_%s" % (path_utils.basename_filtered(self.first_repo), fixed_timestamp)
        final_patch_backup_folder = path_utils.concat_path(base_patch_backup_folder, dirname_patch_backup_folder)

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "w") as f:
            f.write("extra stuff")

        v, r = git_lib.get_head_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        v, r = git_wrapper.stash(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_stash_list(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        file1_patch_filename = path_utils.concat_path(final_patch_backup_folder, "stash", "1_reset_git_repo_stash@{0}.patch")
        self.assertFalse(os.path.exists(file1_patch_filename))

        with mock.patch("mvtools_envvars.mvtools_envvar_read_temp_path", return_value=(True, base_patch_backup_folder)):
            with mock.patch("maketimestamp.get_timestamp_now_compact", return_value=fixed_timestamp):
                v, r = reset_git_repo.reset_git_repo(self.first_repo, False, False, 1, False, 0)
                self.assertTrue(v)
                self.assertEqual(len(r), 1)
                self.assertTrue(file1_patch_filename in r[0])

        v, r = git_lib.get_stash_list(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        self.assertTrue(os.path.exists(file1_patch_filename))
        with open(file1_patch_filename, "r") as f:
            self.assertTrue("extra stuff" in f.read())

    def testResetGitRepo_ResetGitRepo18(self):

        base_patch_backup_folder = path_utils.concat_path(self.test_dir, "base_patch_backup_folder")
        os.mkdir(base_patch_backup_folder)
        fixed_timestamp = "fixed_timestamp"
        dirname_patch_backup_folder = "%s_reset_git_repo_backup_%s" % (path_utils.basename_filtered(self.first_repo), fixed_timestamp)
        final_patch_backup_folder = path_utils.concat_path(base_patch_backup_folder, dirname_patch_backup_folder)

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "w") as f:
            f.write("extra stuff")

        v, r = git_lib.get_head_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        v, r = git_wrapper.stash(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_stash_list(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        with mock.patch("mvtools_envvars.mvtools_envvar_read_temp_path", return_value=(True, base_patch_backup_folder)):
            with mock.patch("maketimestamp.get_timestamp_now_compact", return_value=fixed_timestamp):
                v, r = reset_git_repo.reset_git_repo(self.first_repo, False, False, 0, False, 0)
                self.assertTrue(v)
                self.assertEqual(len(r), 0)

        v, r = git_lib.get_stash_list(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        file1_patch_filename = path_utils.concat_path(final_patch_backup_folder, "stash", "1_reset_git_repo_stash@{0}.patch")
        self.assertFalse(os.path.exists(file1_patch_filename))

    def testResetGitRepo_ResetGitRepo19(self):

        base_patch_backup_folder = path_utils.concat_path(self.test_dir, "base_patch_backup_folder")
        os.mkdir(base_patch_backup_folder)
        fixed_timestamp = "fixed_timestamp"
        dirname_patch_backup_folder = "%s_reset_git_repo_backup_%s" % (path_utils.basename_filtered(self.first_repo), fixed_timestamp)
        final_patch_backup_folder = path_utils.concat_path(base_patch_backup_folder, dirname_patch_backup_folder)

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "w") as f:
            f.write("extra stuff1")

        v, r = git_lib.get_head_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        v, r = git_wrapper.stash(self.first_repo)
        self.assertTrue(v)

        with open(self.first_file2, "w") as f:
            f.write("extra stuff2")

        v, r = git_lib.get_head_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        v, r = git_wrapper.stash(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_stash_list(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)

        file1_patch_filename = path_utils.concat_path(final_patch_backup_folder, "stash", "1_reset_git_repo_stash@{0}.patch")
        file2_patch_filename = path_utils.concat_path(final_patch_backup_folder, "stash", "2_reset_git_repo_stash@{1}.patch")
        self.assertFalse(os.path.exists(file1_patch_filename))
        self.assertFalse(os.path.exists(file2_patch_filename))

        with mock.patch("mvtools_envvars.mvtools_envvar_read_temp_path", return_value=(True, base_patch_backup_folder)):
            with mock.patch("maketimestamp.get_timestamp_now_compact", return_value=fixed_timestamp):
                v, r = reset_git_repo.reset_git_repo(self.first_repo, False, False, -1, False, 0)
                self.assertTrue(v)
                self.assertEqual(len(r), 2)
                self.assertTrue(file1_patch_filename in r[0])
                self.assertTrue(file2_patch_filename in r[1])

        v, r = git_lib.get_stash_list(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        self.assertTrue(os.path.exists(file1_patch_filename))
        self.assertTrue(os.path.exists(file2_patch_filename))

        with open(file1_patch_filename, "r") as f:
            self.assertTrue("extra stuff2" in f.read())
        with open(file2_patch_filename, "r") as f:
            self.assertTrue("extra stuff1" in f.read())

    def testResetGitRepo_ResetGitRepo20(self):

        base_patch_backup_folder = path_utils.concat_path(self.test_dir, "base_patch_backup_folder")
        os.mkdir(base_patch_backup_folder)
        fixed_timestamp = "fixed_timestamp"
        dirname_patch_backup_folder = "%s_reset_git_repo_backup_%s" % (path_utils.basename_filtered(self.first_repo), fixed_timestamp)
        final_patch_backup_folder = path_utils.concat_path(base_patch_backup_folder, dirname_patch_backup_folder)

        v, r = git_lib.get_previous_hash_list(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)

        with mock.patch("mvtools_envvars.mvtools_envvar_read_temp_path", return_value=(True, base_patch_backup_folder)):
            with mock.patch("maketimestamp.get_timestamp_now_compact", return_value=fixed_timestamp):
                v, r = reset_git_repo.reset_git_repo(self.first_repo, False, False, 0, False, 0)
                self.assertTrue(v)

        v, r = git_lib.get_previous_hash_list(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)

    def testResetGitRepo_ResetGitRepo21(self):

        base_patch_backup_folder = path_utils.concat_path(self.test_dir, "base_patch_backup_folder")
        os.mkdir(base_patch_backup_folder)
        fixed_timestamp = "fixed_timestamp"
        dirname_patch_backup_folder = "%s_reset_git_repo_backup_%s" % (path_utils.basename_filtered(self.first_repo), fixed_timestamp)
        final_patch_backup_folder = path_utils.concat_path(base_patch_backup_folder, dirname_patch_backup_folder)

        v, r = git_lib.get_previous_hash_list(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        hash_list = r

        file1_patch_filename = path_utils.concat_path(final_patch_backup_folder, "previous", "1_reset_git_repo_previous_%s.patch" % hash_list[0])
        self.assertFalse(os.path.exists(file1_patch_filename))

        with mock.patch("mvtools_envvars.mvtools_envvar_read_temp_path", return_value=(True, base_patch_backup_folder)):
            with mock.patch("maketimestamp.get_timestamp_now_compact", return_value=fixed_timestamp):
                v, r = reset_git_repo.reset_git_repo(self.first_repo, False, False, 0, False, 1)
                self.assertTrue(v)
                self.assertEqual(len(r), 1)
                self.assertTrue(file1_patch_filename in r[0])

        v, r = git_lib.get_previous_hash_list(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        self.assertTrue(os.path.exists(file1_patch_filename))
        with open(file1_patch_filename, "r") as f:
            self.assertTrue("first-file2-content" in f.read())

    def testResetGitRepo_ResetGitRepo22(self):

        base_patch_backup_folder = path_utils.concat_path(self.test_dir, "base_patch_backup_folder")
        os.mkdir(base_patch_backup_folder)
        fixed_timestamp = "fixed_timestamp"
        dirname_patch_backup_folder = "%s_reset_git_repo_backup_%s" % (path_utils.basename_filtered(self.first_repo), fixed_timestamp)
        final_patch_backup_folder = path_utils.concat_path(base_patch_backup_folder, dirname_patch_backup_folder)

        with open(self.first_file1, "w") as f:
            f.write("extra stuff1")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.first_repo, "commit-msg-2")
        self.assertTrue(v)

        v, r = git_lib.get_previous_hash_list(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 3)
        hash_list = r

        file1_patch_filename = path_utils.concat_path(final_patch_backup_folder, "previous", "1_reset_git_repo_previous_%s.patch" % hash_list[0])
        file2_patch_filename = path_utils.concat_path(final_patch_backup_folder, "previous", "2_reset_git_repo_previous_%s.patch" % hash_list[1])
        self.assertFalse(os.path.exists(file1_patch_filename))
        self.assertFalse(os.path.exists(file2_patch_filename))

        with mock.patch("mvtools_envvars.mvtools_envvar_read_temp_path", return_value=(True, base_patch_backup_folder)):
            with mock.patch("maketimestamp.get_timestamp_now_compact", return_value=fixed_timestamp):
                v, r = reset_git_repo.reset_git_repo(self.first_repo, False, False, 0, False, 2)
                self.assertTrue(v)
                self.assertEqual(len(r), 2)
                self.assertTrue(file1_patch_filename in r[0])
                self.assertTrue(file2_patch_filename in r[1])

        v, r = git_lib.get_previous_hash_list(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        self.assertTrue(os.path.exists(file1_patch_filename))
        with open(file1_patch_filename, "r") as f:
            self.assertTrue("extra stuff1" in f.read())

        self.assertTrue(os.path.exists(file2_patch_filename))
        with open(file2_patch_filename, "r") as f:
            self.assertTrue("first-file2-content" in f.read())

    def testResetGitRepo_ResetGitRepo23(self):

        base_patch_backup_folder = path_utils.concat_path(self.test_dir, "base_patch_backup_folder")
        os.mkdir(base_patch_backup_folder)
        fixed_timestamp = "fixed_timestamp"
        dirname_patch_backup_folder = "%s_reset_git_repo_backup_%s" % (path_utils.basename_filtered(self.first_repo), fixed_timestamp)
        final_patch_backup_folder = path_utils.concat_path(base_patch_backup_folder, dirname_patch_backup_folder)

        v, r = git_lib.get_unversioned_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        first_repo_unvfile73 = path_utils.concat_path(self.first_repo, "unvfile73.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_repo_unvfile73, "dummy contents, file73"))
        self.assertTrue(os.path.exists(first_repo_unvfile73))

        first_repo_sub = path_utils.concat_path(self.first_repo, "sub")
        self.assertFalse(os.path.exists(first_repo_sub))
        os.mkdir(first_repo_sub)
        self.assertTrue(os.path.exists(first_repo_sub))

        first_repo_sub_committed_file = path_utils.concat_path(first_repo_sub, "committed_file.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, path_utils.concat_path(path_utils.basename_filtered(first_repo_sub), path_utils.basename_filtered(first_repo_sub_committed_file)), "committed-file-content", "commit msg, keep subfolder")
        self.assertTrue(v)
        self.assertTrue(os.path.exists(first_repo_sub_committed_file))

        first_repo_sub_unvfile715 = path_utils.concat_path(first_repo_sub, "unvfile715.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_repo_sub_unvfile715, "dummy contents, file715"))
        self.assertTrue(os.path.exists(first_repo_sub_unvfile715))

        first_repo_anothersub = path_utils.concat_path(self.first_repo, "anothersub")
        self.assertFalse(os.path.exists(first_repo_anothersub))
        os.mkdir(first_repo_anothersub)
        self.assertTrue(os.path.exists(first_repo_anothersub))

        first_repo_anothersub_unvfile99 = path_utils.concat_path(first_repo_anothersub, "unvfile99.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_repo_anothersub_unvfile99, "dummy contents, file99"))
        self.assertTrue(os.path.exists(first_repo_anothersub_unvfile99))

        first_repo_anothersub_unvfile47 = path_utils.concat_path(first_repo_anothersub, "unvfile47.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_repo_anothersub_unvfile47, "dummy contents, file47"))
        self.assertTrue(os.path.exists(first_repo_anothersub_unvfile47))

        first_repo_unvfile73_backup_fn = "_%s_bk" % (path_utils.basename_filtered(first_repo_unvfile73))
        first_repo_sub_unvfile715_backup_fn = "_%s_bk" % (path_utils.basename_filtered(first_repo_sub_unvfile715))
        first_repo_anothersub_unvfile99_backup_fn = "_%s_bk" % (path_utils.basename_filtered(first_repo_anothersub_unvfile99))
        first_repo_anothersub_unvfile47_backup_fn = "_%s_bk" % (path_utils.basename_filtered(first_repo_anothersub_unvfile47))

        bk_items = fsquery.makecontentlist(self.rdb_storage, True, True, True, True, True, True, None)
        self.assertFalse(any(first_repo_unvfile73_backup_fn in s for s in bk_items))
        self.assertFalse(any(first_repo_sub_unvfile715_backup_fn in s for s in bk_items))
        self.assertFalse(any(first_repo_anothersub_unvfile99_backup_fn in s for s in bk_items))
        self.assertFalse(any(first_repo_anothersub_unvfile47_backup_fn in s for s in bk_items))

        v, r = git_lib.get_unversioned_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 4)

        with mock.patch("mvtools_envvars.mvtools_envvar_read_temp_path", return_value=(True, base_patch_backup_folder)):
            with mock.patch("maketimestamp.get_timestamp_now_compact", return_value=fixed_timestamp):
                v, r = reset_git_repo.reset_git_repo(self.first_repo, False, False, 0, True, 0)
                self.assertTrue(v)
                self.assertEqual(len(r), 4)
                self.assertTrue(any(first_repo_unvfile73_backup_fn in s for s in r))
                self.assertTrue(any(first_repo_sub_unvfile715_backup_fn in s for s in r))
                self.assertTrue(any(first_repo_anothersub_unvfile99_backup_fn in s for s in r))
                self.assertTrue(any(first_repo_anothersub_unvfile47_backup_fn in s for s in r))

        bk_items = fsquery.makecontentlist(base_patch_backup_folder, True, True, True, True, True, True, None)
        self.assertTrue(any(first_repo_unvfile73_backup_fn in s for s in bk_items))
        self.assertTrue(any(first_repo_sub_unvfile715_backup_fn in s for s in bk_items))
        self.assertTrue(any(first_repo_anothersub_unvfile99_backup_fn in s for s in bk_items))
        self.assertTrue(any(first_repo_anothersub_unvfile47_backup_fn in s for s in bk_items))

        v, r = git_lib.get_unversioned_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)
        self.assertTrue(os.path.exists(first_repo_sub))

if __name__ == '__main__':
    unittest.main()
