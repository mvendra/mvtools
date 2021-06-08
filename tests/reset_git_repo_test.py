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

        # backup object
        self.rbm_storage = path_utils.concat_path(self.test_dir, "rbm_storage")
        self.rbm = delayed_file_backup.delayed_file_backup(self.rbm_storage)

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testResetGitRepo_ResetBackupMaker_Fail1(self):

        local_rbm_storage = path_utils.concat_path(self.test_dir, "local_rbm_storage")
        os.mkdir(local_rbm_storage)

        ex_raised = False
        try:
            local_rbm = delayed_file_backup.delayed_file_backup(local_rbm_storage)
        except mvtools_exception.mvtools_exception as mvtex:
            ex_raised = True

        self.assertTrue(ex_raised)

    def testResetGitRepo_ResetBackupMaker_Fail2(self):

        local_rbm_storage = path_utils.concat_path(self.test_dir, "local_rbm_storage")
        local_rbm = delayed_file_backup.delayed_file_backup(local_rbm_storage)
        self.assertFalse(os.path.exists(local_rbm_storage))

        test_fn = "test.patch"
        test_content = "patched contents"
        test_patch_file_full = path_utils.concat_path(local_rbm_storage, test_fn)

        self.assertFalse(os.path.exists(test_patch_file_full))
        os.mkdir(local_rbm_storage)
        self.assertTrue(create_and_write_file.create_file_contents(test_patch_file_full, "dummy contents"))
        v, r = local_rbm.make_backup(test_fn, test_content)
        self.assertFalse(v)

    def testResetGitRepo_ResetBackupMaker1(self):

        local_rbm_storage = path_utils.concat_path(self.test_dir, "local_rbm_storage")

        ex_raised = False
        try:
            local_rbm = delayed_file_backup.delayed_file_backup(local_rbm_storage)
        except mvtools_exception.mvtools_exception as mvtex:
            ex_raised = True

        self.assertFalse(ex_raised)

    def testResetGitRepo_ResetBackupMaker2(self):

        local_rbm_storage = path_utils.concat_path(self.test_dir, "local_rbm_storage")
        local_rbm = delayed_file_backup.delayed_file_backup(local_rbm_storage)
        self.assertFalse(os.path.exists(local_rbm_storage))

        test_fn = "test.patch"
        test_content = "patched contents"
        test_patch_file_full = path_utils.concat_path(local_rbm_storage, test_fn)

        self.assertFalse(os.path.exists(test_patch_file_full))
        v, r = local_rbm.make_backup(test_fn, test_content)
        self.assertTrue(v)
        self.assertTrue(os.path.exists(test_patch_file_full))

    def testResetGitRepo_ResetGitRepoFile_Fail1(self):

        v, r = reset_git_repo.reset_git_repo_file(self.nonrepo, self.first_file1, 1, self.rbm)
        self.assertFalse(v)

    def testResetGitRepo_ResetGitRepoFile_Fail2(self):

        v, r = reset_git_repo.reset_git_repo_file(self.first_repo, self.first_file1, 1, self.rbm)
        self.assertFalse(v)

    def testResetGitRepo_ResetGitRepoFile_Fail3(self):

        v, r = git_lib.get_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "w") as f:
            f.write("extra stuff")

        v, r = git_lib.get_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        patch_file_filename = "1_reset_git_repo_%s.patch" % (path_utils.basename_filtered(self.first_file1))
        test_patch_file = path_utils.concat_path(self.rbm_storage, patch_file_filename)
        self.assertFalse(os.path.exists(test_patch_file))

        os.mkdir(self.rbm_storage)
        self.assertTrue(create_and_write_file.create_file_contents(test_patch_file, "dummy contents"))

        v, r = reset_git_repo.reset_git_repo_file(self.first_repo, self.first_file1, 1, self.rbm)
        self.assertFalse(v)

        v, r = git_lib.get_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

    def testResetGitRepo_ResetGitRepoFile_Fail4(self):

        self.second_repo = path_utils.concat_path(self.test_dir, "second")
        v, r = git_wrapper.init(self.test_dir, "second", False)
        self.assertTrue(v)

        self.second_file1 = path_utils.concat_path(self.second_repo, "file1.txt")
        v, r = git_test_fixture.git_createAndCommit(self.second_repo, "file1.txt", "second-file1-content", "second-file1-msg")
        self.assertTrue(v)

        v, r = git_lib.get_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "w") as f:
            f.write("extra stuff")

        v, r = git_lib.get_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        patch_file_filename = "1_%s.patch" % (path_utils.basename_filtered(self.first_file1))
        test_patch_file = path_utils.concat_path(self.rbm_storage, patch_file_filename)
        self.assertFalse(os.path.exists(test_patch_file))

        os.mkdir(self.rbm_storage)
        self.assertTrue(create_and_write_file.create_file_contents(test_patch_file, "dummy contents"))

        v, r = reset_git_repo.reset_git_repo_file(self.first_repo, self.second_file1, 1, self.rbm)
        self.assertFalse(v)

        v, r = git_lib.get_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

    def testResetGitRepo_ResetGitRepoFile1(self):

        v, r = git_lib.get_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "w") as f:
            f.write("extra stuff")

        v, r = git_lib.get_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        patch_file_filename = "1_reset_git_repo_%s.patch" % (path_utils.basename_filtered(self.first_file1))
        test_patch_file = path_utils.concat_path(self.rbm_storage, patch_file_filename)
        self.assertFalse(os.path.exists(test_patch_file))

        v, r = reset_git_repo.reset_git_repo_file(self.first_repo, self.first_file1, 1, self.rbm)
        self.assertTrue(v)
        self.assertTrue(os.path.exists(test_patch_file))

        v, r = git_lib.get_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

    def testResetGitRepo_ResetGitRepoFile2(self):

        v, r = git_lib.get_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "w") as f:
            f.write("extra stuff file1")

        with open(self.first_file2, "w") as f:
            f.write("extra stuff file2")

        v, r = git_lib.get_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)

        patch_file_filename = "1_reset_git_repo_%s.patch" % (path_utils.basename_filtered(self.first_file1))
        test_patch_file = path_utils.concat_path(self.rbm_storage, patch_file_filename)
        self.assertFalse(os.path.exists(test_patch_file))

        v, r = reset_git_repo.reset_git_repo_file(self.first_repo, self.first_file1, 1, self.rbm)
        self.assertTrue(v)
        self.assertTrue(os.path.exists(test_patch_file))

        v, r = git_lib.get_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

    def testResetGitRepo_ResetGitRepoEntire_Fail1(self):

        v, r = reset_git_repo.reset_git_repo_entire(self.nonrepo, self.rbm)
        self.assertFalse(v)

    def testResetGitRepo_ResetGitRepoEntire1(self):

        v, r = git_lib.get_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "w") as f:
            f.write("extra stuff")

        v, r = git_lib.get_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        patch_file_filename = "1_reset_git_repo_%s.patch" % (path_utils.basename_filtered(self.first_file1))
        test_patch_file = path_utils.concat_path(self.rbm_storage, patch_file_filename)
        self.assertFalse(os.path.exists(test_patch_file))

        v, r = reset_git_repo.reset_git_repo_entire(self.first_repo, self.rbm)
        self.assertTrue(v)
        self.assertTrue(os.path.exists(test_patch_file))

        v, r = git_lib.get_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

    def testResetGitRepo_ResetGitRepoEntire2(self):

        v, r = git_lib.get_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "w") as f:
            f.write("extra stuff")

        with open(self.first_file2, "w") as f:
            f.write("extra stuff")

        v, r = git_lib.get_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)

        patch_file1_filename = "1_reset_git_repo_%s.patch" % (path_utils.basename_filtered(self.first_file1))
        test_patch_file1 = path_utils.concat_path(self.rbm_storage, patch_file1_filename)
        self.assertFalse(os.path.exists(test_patch_file1))

        patch_file2_filename = "2_reset_git_repo_%s.patch" % (path_utils.basename_filtered(self.first_file2))
        test_patch_file2 = path_utils.concat_path(self.rbm_storage, patch_file2_filename)
        self.assertFalse(os.path.exists(test_patch_file2))

        v, r = reset_git_repo.reset_git_repo_entire(self.first_repo, self.rbm)
        self.assertTrue(v)
        self.assertTrue(os.path.exists(test_patch_file1))
        self.assertTrue(os.path.exists(test_patch_file2))

        v, r = git_lib.get_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

    def testResetGitRepo_ResetGitRepoEntire3(self):

        v, r = git_lib.get_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = reset_git_repo.reset_git_repo_entire(self.first_repo, self.rbm)
        self.assertTrue(v)

        v, r = git_lib.get_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

    def testResetGitRepo_ResetGitRepo_Fail1(self):

        v, r = reset_git_repo.reset_git_repo(self.nonrepo, None)
        self.assertFalse(v)

    def testResetGitRepo_ResetGitRepo_Fail2(self):

        test_bare_repo = path_utils.concat_path(self.test_dir, "test_bare")
        v, r = git_wrapper.init(self.test_dir, "test_bare", True)
        self.assertTrue(v)

        v, r = reset_git_repo.reset_git_repo(test_bare_repo, None)
        self.assertFalse(v)

    def testResetGitRepo_ResetGitRepo_Fail3(self):

        base_patch_backup_folder = path_utils.concat_path(self.test_dir, "base_patch_backup_folder")
        with mock.patch("mvtools_envvars.mvtools_envvar_read_temp_path", return_value=(True, base_patch_backup_folder)):
            v, r = reset_git_repo.reset_git_repo(self.first_repo, None)
            self.assertFalse(v)

    def testResetGitRepo_ResetGitRepo_Fail4(self):

        base_patch_backup_folder = path_utils.concat_path(self.test_dir, "base_patch_backup_folder")
        os.mkdir(base_patch_backup_folder)
        fixed_timestamp = "fixed_timestamp"
        dirname_patch_backup_folder = "%s_reset_git_repo_backup_%s" % (path_utils.basename_filtered(self.first_repo), fixed_timestamp)
        final_patch_backup_folder = path_utils.concat_path(base_patch_backup_folder, dirname_patch_backup_folder)
        os.mkdir(final_patch_backup_folder)

        with mock.patch("mvtools_envvars.mvtools_envvar_read_temp_path", return_value=(True, base_patch_backup_folder)):
            with mock.patch("reset_git_repo._get_timestamp", return_value=fixed_timestamp):
                v, r = reset_git_repo.reset_git_repo(self.first_repo, None)
                self.assertFalse(v)

    def testResetGitRepo_ResetGitRepo1(self):

        base_patch_backup_folder = path_utils.concat_path(self.test_dir, "base_patch_backup_folder")
        os.mkdir(base_patch_backup_folder)
        fixed_timestamp = "fixed_timestamp"
        dirname_patch_backup_folder = "%s_reset_git_repo_backup_%s" % (path_utils.basename_filtered(self.first_repo), fixed_timestamp)
        final_patch_backup_folder = path_utils.concat_path(base_patch_backup_folder, dirname_patch_backup_folder)

        v, r = git_lib.get_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with mock.patch("mvtools_envvars.mvtools_envvar_read_temp_path", return_value=(True, base_patch_backup_folder)):
            with mock.patch("reset_git_repo._get_timestamp", return_value=fixed_timestamp):
                v, r = reset_git_repo.reset_git_repo(self.first_repo, None)
                self.assertTrue(v)

    def testResetGitRepo_ResetGitRepo2(self):

        base_patch_backup_folder = path_utils.concat_path(self.test_dir, "base_patch_backup_folder")
        os.mkdir(base_patch_backup_folder)
        fixed_timestamp = "fixed_timestamp"
        dirname_patch_backup_folder = "%s_reset_git_repo_backup_%s" % (path_utils.basename_filtered(self.first_repo), fixed_timestamp)
        final_patch_backup_folder = path_utils.concat_path(base_patch_backup_folder, dirname_patch_backup_folder)

        v, r = git_lib.get_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "w") as f:
            f.write("extra stuff")

        v, r = git_lib.get_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        with mock.patch("mvtools_envvars.mvtools_envvar_read_temp_path", return_value=(True, base_patch_backup_folder)):
            with mock.patch("reset_git_repo._get_timestamp", return_value=fixed_timestamp):
                v, r = reset_git_repo.reset_git_repo(self.first_repo, None)
                self.assertTrue(v)

        v, r = git_lib.get_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        file1_patch_filename = path_utils.concat_path(final_patch_backup_folder, "1_reset_git_repo_file1.txt.patch")
        self.assertTrue(os.path.exists(file1_patch_filename))

    def testResetGitRepo_ResetGitRepo3(self):

        base_patch_backup_folder = path_utils.concat_path(self.test_dir, "base_patch_backup_folder")
        os.mkdir(base_patch_backup_folder)
        fixed_timestamp = "fixed_timestamp"
        dirname_patch_backup_folder = "%s_reset_git_repo_backup_%s" % (path_utils.basename_filtered(self.first_repo), fixed_timestamp)
        final_patch_backup_folder = path_utils.concat_path(base_patch_backup_folder, dirname_patch_backup_folder)

        v, r = git_lib.get_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "w") as f:
            f.write("extra stuff")

        with open(self.first_file2, "w") as f:
            f.write("extra stuff")

        v, r = git_lib.get_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)

        with mock.patch("mvtools_envvars.mvtools_envvar_read_temp_path", return_value=(True, base_patch_backup_folder)):
            with mock.patch("reset_git_repo._get_timestamp", return_value=fixed_timestamp):
                v, r = reset_git_repo.reset_git_repo(self.first_repo, None)
                self.assertTrue(v)

        v, r = git_lib.get_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        file1_patch_filename = path_utils.concat_path(final_patch_backup_folder, "1_reset_git_repo_file1.txt.patch")
        file2_patch_filename = path_utils.concat_path(final_patch_backup_folder, "2_reset_git_repo_file2.txt.patch")
        self.assertTrue(os.path.exists(file1_patch_filename))
        self.assertTrue(os.path.exists(file2_patch_filename))

    def testResetGitRepo_ResetGitRepo4(self):

        base_patch_backup_folder = path_utils.concat_path(self.test_dir, "base_patch_backup_folder")
        os.mkdir(base_patch_backup_folder)
        fixed_timestamp = "fixed_timestamp"
        dirname_patch_backup_folder = "%s_reset_git_repo_backup_%s" % (path_utils.basename_filtered(self.first_repo), fixed_timestamp)
        final_patch_backup_folder = path_utils.concat_path(base_patch_backup_folder, dirname_patch_backup_folder)

        v, r = git_lib.get_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "w") as f:
            f.write("extra stuff")

        v, r = git_lib.get_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        with mock.patch("mvtools_envvars.mvtools_envvar_read_temp_path", return_value=(True, base_patch_backup_folder)):
            with mock.patch("reset_git_repo._get_timestamp", return_value=fixed_timestamp):
                v, r = reset_git_repo.reset_git_repo(self.first_repo, [self.first_file1])
                self.assertTrue(v)

        v, r = git_lib.get_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        file1_patch_filename = path_utils.concat_path(final_patch_backup_folder, "1_reset_git_repo_file1.txt.patch")
        self.assertTrue(os.path.exists(file1_patch_filename))

    def testResetGitRepo_ResetGitRepo5(self):

        base_patch_backup_folder = path_utils.concat_path(self.test_dir, "base_patch_backup_folder")
        os.mkdir(base_patch_backup_folder)
        fixed_timestamp = "fixed_timestamp"
        dirname_patch_backup_folder = "%s_reset_git_repo_backup_%s" % (path_utils.basename_filtered(self.first_repo), fixed_timestamp)
        final_patch_backup_folder = path_utils.concat_path(base_patch_backup_folder, dirname_patch_backup_folder)

        v, r = git_lib.get_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "w") as f:
            f.write("extra stuff")

        with open(self.first_file2, "w") as f:
            f.write("extra stuff")

        v, r = git_lib.get_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)

        with mock.patch("mvtools_envvars.mvtools_envvar_read_temp_path", return_value=(True, base_patch_backup_folder)):
            with mock.patch("reset_git_repo._get_timestamp", return_value=fixed_timestamp):
                v, r = reset_git_repo.reset_git_repo(self.first_repo, [self.first_file1, self.first_file2])
                self.assertTrue(v)

        v, r = git_lib.get_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        file1_patch_filename = path_utils.concat_path(final_patch_backup_folder, "1_reset_git_repo_file1.txt.patch")
        file2_patch_filename = path_utils.concat_path(final_patch_backup_folder, "2_reset_git_repo_file2.txt.patch")
        self.assertTrue(os.path.exists(file1_patch_filename))
        self.assertTrue(os.path.exists(file2_patch_filename))

if __name__ == '__main__':
    unittest.main()
