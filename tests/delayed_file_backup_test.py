#!/usr/bin/env python3

import sys
import os
import shutil
import unittest

import mvtools_test_fixture
import create_and_write_file
import path_utils
import mvtools_exception

import delayed_file_backup

class DelayedFileBackupTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("delayed_file_backup_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testAscertainStorageFolder1(self):

        local_dfb_storage = path_utils.concat_path(self.test_dir, "local_dfb_storage")
        local_dfb = delayed_file_backup.delayed_file_backup(local_dfb_storage)
        self.assertFalse(os.path.exists(local_dfb_storage))

        local_dfb._ascertain_storage_folder(None)

        self.assertTrue(os.path.exists(local_dfb_storage))

    def testAscertainStorageFolder2(self):

        local_dfb_storage = path_utils.concat_path(self.test_dir, "local_dfb_storage")
        local_dfb_storage_sub1_sub2 = path_utils.concat_path(local_dfb_storage, "sub1", "sub2")
        local_dfb = delayed_file_backup.delayed_file_backup(local_dfb_storage)
        self.assertFalse(os.path.exists(local_dfb_storage))
        self.assertFalse(os.path.exists(local_dfb_storage_sub1_sub2))

        local_dfb._ascertain_storage_folder("sub1/sub2")

        self.assertTrue(os.path.exists(local_dfb_storage))
        self.assertTrue(os.path.exists(local_dfb_storage_sub1_sub2))

    def testDelayedFileBackup_Fail1(self):

        local_dfb_storage = path_utils.concat_path(self.test_dir, "local_dfb_storage")
        os.mkdir(local_dfb_storage)

        ex_raised = False
        try:
            local_dfb = delayed_file_backup.delayed_file_backup(local_dfb_storage)
        except mvtools_exception.mvtools_exception as mvtex:
            ex_raised = True

        self.assertTrue(ex_raised)

    def testDelayedFileBackup_Fail2(self):

        local_dfb_storage = path_utils.concat_path(self.test_dir, "local_dfb_storage")
        local_dfb = delayed_file_backup.delayed_file_backup(local_dfb_storage)
        self.assertFalse(os.path.exists(local_dfb_storage))

        test_fn = "test.patch"
        test_content = "patched contents"
        test_patch_file_full = path_utils.concat_path(local_dfb_storage, test_fn)

        self.assertFalse(os.path.exists(test_patch_file_full))
        os.mkdir(local_dfb_storage)
        self.assertTrue(create_and_write_file.create_file_contents(test_patch_file_full, "dummy contents"))
        v, r = local_dfb.make_backup(None, test_fn, test_content)
        self.assertFalse(v)
        self.assertEqual(r, test_patch_file_full)

    def testDelayedFileBackup1(self):

        local_dfb_storage = path_utils.concat_path(self.test_dir, "local_dfb_storage")

        ex_raised = False
        try:
            local_dfb = delayed_file_backup.delayed_file_backup(local_dfb_storage)
        except mvtools_exception.mvtools_exception as mvtex:
            ex_raised = True

        self.assertFalse(ex_raised)

    def testDelayedFileBackup2(self):

        local_dfb_storage = path_utils.concat_path(self.test_dir, "local_dfb_storage")
        local_dfb = delayed_file_backup.delayed_file_backup(local_dfb_storage)
        self.assertFalse(os.path.exists(local_dfb_storage))

        test_fn = "test.patch"
        test_content = "patched contents"
        test_patch_file_full = path_utils.concat_path(local_dfb_storage, test_fn)

        self.assertFalse(os.path.exists(test_patch_file_full))
        v, r = local_dfb.make_backup(None, test_fn, test_content)
        self.assertTrue(v)
        self.assertTrue(os.path.exists(test_patch_file_full))
        self.assertEqual(r, test_patch_file_full)

    def testDelayedFileBackup3(self):

        local_dfb_storage = path_utils.concat_path(self.test_dir, "local_dfb_storage")
        local_dfb = delayed_file_backup.delayed_file_backup(local_dfb_storage)
        self.assertFalse(os.path.exists(local_dfb_storage))

        test_fn = "test.patch"
        test_content = "patched contents"
        subpath = "sub1/sub2/sub3"
        test_patch_file_full = path_utils.concat_path(local_dfb_storage, subpath, test_fn)

        self.assertFalse(os.path.exists(test_patch_file_full))
        v, r = local_dfb.make_backup(subpath, test_fn, test_content)
        self.assertTrue(v)
        self.assertTrue(os.path.exists(test_patch_file_full))
        self.assertEqual(r, test_patch_file_full)

    def testDelayedFileBackupFromPath1(self):

        # single file source, root bk folder, no renaming

        local_dfb_storage = path_utils.concat_path(self.test_dir, "local_dfb_storage")
        local_dfb = delayed_file_backup.delayed_file_backup(local_dfb_storage)
        self.assertFalse(os.path.exists(local_dfb_storage))

        test_fn = "file1.txt"
        test_content = "source file contents"
        test_source_file_full = path_utils.concat_path(self.test_dir, test_fn)
        test_backup_file_full = path_utils.concat_path(local_dfb_storage, test_fn)
        self.assertFalse(os.path.exists(test_source_file_full))
        self.assertFalse(os.path.exists(test_backup_file_full))
        with open(test_source_file_full, "w") as f:
            f.write(test_content)
        self.assertTrue(os.path.exists(test_source_file_full))

        v, r = local_dfb.make_backup_frompath(None, test_fn, test_source_file_full)
        self.assertTrue(v)
        self.assertTrue(os.path.exists(test_backup_file_full))
        self.assertEqual(r, test_backup_file_full)

    def testDelayedFileBackupFromPath2(self):

        # single file source, root bk folder, renaming

        local_dfb_storage = path_utils.concat_path(self.test_dir, "local_dfb_storage")
        local_dfb = delayed_file_backup.delayed_file_backup(local_dfb_storage)
        self.assertFalse(os.path.exists(local_dfb_storage))

        test_fn_source = "file1.txt"
        test_fn_renamed = "file1_renamed.txt"
        test_content = "source file contents"
        test_source_file_full = path_utils.concat_path(self.test_dir, test_fn_source)
        test_backup_file_full = path_utils.concat_path(local_dfb_storage, test_fn_renamed)
        self.assertFalse(os.path.exists(test_source_file_full))
        self.assertFalse(os.path.exists(test_backup_file_full))
        with open(test_source_file_full, "w") as f:
            f.write(test_content)
        self.assertTrue(os.path.exists(test_source_file_full))

        v, r = local_dfb.make_backup_frompath(None, test_fn_renamed, test_source_file_full)
        self.assertTrue(v)
        self.assertTrue(os.path.exists(test_backup_file_full))
        self.assertEqual(r, test_backup_file_full)

    def testDelayedFileBackupFromPath3(self):

        # single file source, subfoldered bk, no renaming

        local_dfb_storage = path_utils.concat_path(self.test_dir, "local_dfb_storage")
        local_dfb = delayed_file_backup.delayed_file_backup(local_dfb_storage)
        self.assertFalse(os.path.exists(local_dfb_storage))

        test_fn = "file1.txt"
        test_content = "source file contents"
        test_source_file_full = path_utils.concat_path(self.test_dir, test_fn)
        test_backup_file_full = path_utils.concat_path(local_dfb_storage, "the-subfolder", test_fn)
        self.assertFalse(os.path.exists(test_source_file_full))
        self.assertFalse(os.path.exists(test_backup_file_full))
        with open(test_source_file_full, "w") as f:
            f.write(test_content)
        self.assertTrue(os.path.exists(test_source_file_full))

        v, r = local_dfb.make_backup_frompath("the-subfolder", test_fn, test_source_file_full)
        self.assertTrue(v)
        self.assertTrue(os.path.exists(test_backup_file_full))
        self.assertEqual(r, test_backup_file_full)

    def testDelayedFileBackupFromPath4(self):

        # single file source, subfoldered bk, renaming

        local_dfb_storage = path_utils.concat_path(self.test_dir, "local_dfb_storage")
        local_dfb = delayed_file_backup.delayed_file_backup(local_dfb_storage)
        self.assertFalse(os.path.exists(local_dfb_storage))

        test_fn_source = "file1.txt"
        test_fn_renamed = "file1_renamed.txt"
        test_content = "source file contents"
        test_source_file_full = path_utils.concat_path(self.test_dir, test_fn_source)
        test_backup_file_full = path_utils.concat_path(local_dfb_storage, "the-subfolder", test_fn_renamed)
        self.assertFalse(os.path.exists(test_source_file_full))
        self.assertFalse(os.path.exists(test_backup_file_full))
        with open(test_source_file_full, "w") as f:
            f.write(test_content)
        self.assertTrue(os.path.exists(test_source_file_full))

        v, r = local_dfb.make_backup_frompath("the-subfolder", test_fn_renamed, test_source_file_full)
        self.assertTrue(v)
        self.assertTrue(os.path.exists(test_backup_file_full))
        self.assertEqual(r, test_backup_file_full)

    def testDelayedFileBackupFromPath5(self):

        # folder source, root bk folder, no renaming

        local_dfb_storage = path_utils.concat_path(self.test_dir, "local_dfb_storage")
        local_dfb = delayed_file_backup.delayed_file_backup(local_dfb_storage)
        self.assertFalse(os.path.exists(local_dfb_storage))

        test_sourcefolder = path_utils.concat_path(self.test_dir, "sourcefolder")
        self.assertFalse(os.path.exists(test_sourcefolder))
        os.mkdir(test_sourcefolder)
        self.assertTrue(os.path.exists(test_sourcefolder))

        test_sourcefolder_file1 = path_utils.concat_path(test_sourcefolder, "file1.txt")
        self.assertFalse(os.path.exists(test_sourcefolder_file1))
        with open(test_sourcefolder_file1, "w") as f:
            f.write("file1 contents")
        self.assertTrue(os.path.exists(test_sourcefolder_file1))

        test_sourcefolder_subfolder = path_utils.concat_path(test_sourcefolder, "subfolder")
        self.assertFalse(os.path.exists(test_sourcefolder_subfolder))
        os.mkdir(test_sourcefolder_subfolder)
        self.assertTrue(os.path.exists(test_sourcefolder_subfolder))

        test_sourcefolder_subfolder_file2 = path_utils.concat_path(test_sourcefolder_subfolder, "file2.txt")
        self.assertFalse(os.path.exists(test_sourcefolder_subfolder_file2))
        with open(test_sourcefolder_subfolder_file2, "w") as f:
            f.write("file2 contents")
        self.assertTrue(os.path.exists(test_sourcefolder_subfolder_file2))

        test_sourcefolder_subfolder_file3 = path_utils.concat_path(test_sourcefolder_subfolder, "file3.txt")
        self.assertFalse(os.path.exists(test_sourcefolder_subfolder_file3))
        with open(test_sourcefolder_subfolder_file3, "w") as f:
            f.write("file3 contents")
        self.assertTrue(os.path.exists(test_sourcefolder_subfolder_file3))

        test_sourcefolder_backup = path_utils.concat_path(local_dfb_storage, path_utils.basename_filtered(test_sourcefolder))
        test_sourcefolder_file1_backup = path_utils.concat_path(local_dfb_storage, path_utils.basename_filtered(test_sourcefolder), path_utils.basename_filtered(test_sourcefolder_file1))
        test_sourcefolder_subfolder_backup = path_utils.concat_path(local_dfb_storage, path_utils.basename_filtered(test_sourcefolder), path_utils.basename_filtered(test_sourcefolder_subfolder))
        test_sourcefolder_subfolder_file2_backup = path_utils.concat_path(local_dfb_storage, path_utils.basename_filtered(test_sourcefolder), path_utils.basename_filtered(test_sourcefolder_subfolder), path_utils.basename_filtered(test_sourcefolder_subfolder_file2))
        test_sourcefolder_subfolder_file3_backup = path_utils.concat_path(local_dfb_storage, path_utils.basename_filtered(test_sourcefolder), path_utils.basename_filtered(test_sourcefolder_subfolder), path_utils.basename_filtered(test_sourcefolder_subfolder_file3))

        self.assertFalse(os.path.exists(test_sourcefolder_backup))
        self.assertFalse(os.path.exists(test_sourcefolder_file1_backup))
        self.assertFalse(os.path.exists(test_sourcefolder_subfolder_backup))
        self.assertFalse(os.path.exists(test_sourcefolder_subfolder_file2_backup))
        self.assertFalse(os.path.exists(test_sourcefolder_subfolder_file3_backup))

        v, r = local_dfb.make_backup_frompath(None, path_utils.basename_filtered(test_sourcefolder), test_sourcefolder)
        self.assertTrue(v)
        self.assertEqual(r, test_sourcefolder_backup)
        self.assertTrue(os.path.exists(test_sourcefolder_backup))
        self.assertTrue(os.path.exists(test_sourcefolder_file1_backup))
        self.assertTrue(os.path.exists(test_sourcefolder_subfolder_backup))
        self.assertTrue(os.path.exists(test_sourcefolder_subfolder_file2_backup))
        self.assertTrue(os.path.exists(test_sourcefolder_subfolder_file3_backup))

    def testDelayedFileBackupFromPath6(self):

        # folder source, root bk folder, renaming

        local_dfb_storage = path_utils.concat_path(self.test_dir, "local_dfb_storage")
        local_dfb = delayed_file_backup.delayed_file_backup(local_dfb_storage)
        self.assertFalse(os.path.exists(local_dfb_storage))

        test_sourcefolder = path_utils.concat_path(self.test_dir, "sourcefolder")
        self.assertFalse(os.path.exists(test_sourcefolder))
        os.mkdir(test_sourcefolder)
        self.assertTrue(os.path.exists(test_sourcefolder))

        test_sourcefolder_file1 = path_utils.concat_path(test_sourcefolder, "file1.txt")
        self.assertFalse(os.path.exists(test_sourcefolder_file1))
        with open(test_sourcefolder_file1, "w") as f:
            f.write("file1 contents")
        self.assertTrue(os.path.exists(test_sourcefolder_file1))

        test_sourcefolder_subfolder = path_utils.concat_path(test_sourcefolder, "subfolder")
        self.assertFalse(os.path.exists(test_sourcefolder_subfolder))
        os.mkdir(test_sourcefolder_subfolder)
        self.assertTrue(os.path.exists(test_sourcefolder_subfolder))

        test_sourcefolder_subfolder_file2 = path_utils.concat_path(test_sourcefolder_subfolder, "file2.txt")
        self.assertFalse(os.path.exists(test_sourcefolder_subfolder_file2))
        with open(test_sourcefolder_subfolder_file2, "w") as f:
            f.write("file2 contents")
        self.assertTrue(os.path.exists(test_sourcefolder_subfolder_file2))

        test_sourcefolder_subfolder_file3 = path_utils.concat_path(test_sourcefolder_subfolder, "file3.txt")
        self.assertFalse(os.path.exists(test_sourcefolder_subfolder_file3))
        with open(test_sourcefolder_subfolder_file3, "w") as f:
            f.write("file3 contents")
        self.assertTrue(os.path.exists(test_sourcefolder_subfolder_file3))

        test_sourcefolder_backup = path_utils.concat_path(local_dfb_storage, "renamed_sourcefolder")
        test_sourcefolder_file1_backup = path_utils.concat_path(local_dfb_storage, "renamed_sourcefolder", path_utils.basename_filtered(test_sourcefolder_file1))
        test_sourcefolder_subfolder_backup = path_utils.concat_path(local_dfb_storage, "renamed_sourcefolder", path_utils.basename_filtered(test_sourcefolder_subfolder))
        test_sourcefolder_subfolder_file2_backup = path_utils.concat_path(local_dfb_storage, "renamed_sourcefolder", path_utils.basename_filtered(test_sourcefolder_subfolder), path_utils.basename_filtered(test_sourcefolder_subfolder_file2))
        test_sourcefolder_subfolder_file3_backup = path_utils.concat_path(local_dfb_storage, "renamed_sourcefolder", path_utils.basename_filtered(test_sourcefolder_subfolder), path_utils.basename_filtered(test_sourcefolder_subfolder_file3))

        self.assertFalse(os.path.exists(test_sourcefolder_backup))
        self.assertFalse(os.path.exists(test_sourcefolder_file1_backup))
        self.assertFalse(os.path.exists(test_sourcefolder_subfolder_backup))
        self.assertFalse(os.path.exists(test_sourcefolder_subfolder_file2_backup))
        self.assertFalse(os.path.exists(test_sourcefolder_subfolder_file3_backup))

        v, r = local_dfb.make_backup_frompath(None, "renamed_sourcefolder", test_sourcefolder)
        self.assertTrue(v)
        self.assertEqual(r, test_sourcefolder_backup)
        self.assertTrue(os.path.exists(test_sourcefolder_backup))
        self.assertTrue(os.path.exists(test_sourcefolder_file1_backup))
        self.assertTrue(os.path.exists(test_sourcefolder_subfolder_backup))
        self.assertTrue(os.path.exists(test_sourcefolder_subfolder_file2_backup))
        self.assertTrue(os.path.exists(test_sourcefolder_subfolder_file3_backup))

    def testDelayedFileBackupFromPath7(self):

        # folder source, subfoldered bk, no renaming

        local_dfb_storage = path_utils.concat_path(self.test_dir, "local_dfb_storage")
        local_dfb = delayed_file_backup.delayed_file_backup(local_dfb_storage)
        self.assertFalse(os.path.exists(local_dfb_storage))

        test_sourcefolder = path_utils.concat_path(self.test_dir, "sourcefolder")
        self.assertFalse(os.path.exists(test_sourcefolder))
        os.mkdir(test_sourcefolder)
        self.assertTrue(os.path.exists(test_sourcefolder))

        test_sourcefolder_file1 = path_utils.concat_path(test_sourcefolder, "file1.txt")
        self.assertFalse(os.path.exists(test_sourcefolder_file1))
        with open(test_sourcefolder_file1, "w") as f:
            f.write("file1 contents")
        self.assertTrue(os.path.exists(test_sourcefolder_file1))

        test_sourcefolder_subfolder = path_utils.concat_path(test_sourcefolder, "subfolder")
        self.assertFalse(os.path.exists(test_sourcefolder_subfolder))
        os.mkdir(test_sourcefolder_subfolder)
        self.assertTrue(os.path.exists(test_sourcefolder_subfolder))

        test_sourcefolder_subfolder_file2 = path_utils.concat_path(test_sourcefolder_subfolder, "file2.txt")
        self.assertFalse(os.path.exists(test_sourcefolder_subfolder_file2))
        with open(test_sourcefolder_subfolder_file2, "w") as f:
            f.write("file2 contents")
        self.assertTrue(os.path.exists(test_sourcefolder_subfolder_file2))

        test_sourcefolder_subfolder_file3 = path_utils.concat_path(test_sourcefolder_subfolder, "file3.txt")
        self.assertFalse(os.path.exists(test_sourcefolder_subfolder_file3))
        with open(test_sourcefolder_subfolder_file3, "w") as f:
            f.write("file3 contents")
        self.assertTrue(os.path.exists(test_sourcefolder_subfolder_file3))

        test_sourcefolder_backup = path_utils.concat_path(local_dfb_storage, "the-subfolder", path_utils.basename_filtered(test_sourcefolder))
        test_sourcefolder_file1_backup = path_utils.concat_path(local_dfb_storage, "the-subfolder", path_utils.basename_filtered(test_sourcefolder), path_utils.basename_filtered(test_sourcefolder_file1))
        test_sourcefolder_subfolder_backup = path_utils.concat_path(local_dfb_storage, "the-subfolder", path_utils.basename_filtered(test_sourcefolder), path_utils.basename_filtered(test_sourcefolder_subfolder))
        test_sourcefolder_subfolder_file2_backup = path_utils.concat_path(local_dfb_storage, "the-subfolder", path_utils.basename_filtered(test_sourcefolder), path_utils.basename_filtered(test_sourcefolder_subfolder), path_utils.basename_filtered(test_sourcefolder_subfolder_file2))
        test_sourcefolder_subfolder_file3_backup = path_utils.concat_path(local_dfb_storage, "the-subfolder", path_utils.basename_filtered(test_sourcefolder), path_utils.basename_filtered(test_sourcefolder_subfolder), path_utils.basename_filtered(test_sourcefolder_subfolder_file3))

        self.assertFalse(os.path.exists(test_sourcefolder_backup))
        self.assertFalse(os.path.exists(test_sourcefolder_file1_backup))
        self.assertFalse(os.path.exists(test_sourcefolder_subfolder_backup))
        self.assertFalse(os.path.exists(test_sourcefolder_subfolder_file2_backup))
        self.assertFalse(os.path.exists(test_sourcefolder_subfolder_file3_backup))

        v, r = local_dfb.make_backup_frompath("the-subfolder", path_utils.basename_filtered(test_sourcefolder), test_sourcefolder)
        self.assertTrue(v)
        self.assertEqual(r, test_sourcefolder_backup)
        self.assertTrue(os.path.exists(test_sourcefolder_backup))
        self.assertTrue(os.path.exists(test_sourcefolder_file1_backup))
        self.assertTrue(os.path.exists(test_sourcefolder_subfolder_backup))
        self.assertTrue(os.path.exists(test_sourcefolder_subfolder_file2_backup))
        self.assertTrue(os.path.exists(test_sourcefolder_subfolder_file3_backup))

    def testDelayedFileBackupFromPath8(self):

        # folder source, subfoldered bk, renaming

        local_dfb_storage = path_utils.concat_path(self.test_dir, "local_dfb_storage")
        local_dfb = delayed_file_backup.delayed_file_backup(local_dfb_storage)
        self.assertFalse(os.path.exists(local_dfb_storage))

        test_sourcefolder = path_utils.concat_path(self.test_dir, "sourcefolder")
        self.assertFalse(os.path.exists(test_sourcefolder))
        os.mkdir(test_sourcefolder)
        self.assertTrue(os.path.exists(test_sourcefolder))

        test_sourcefolder_file1 = path_utils.concat_path(test_sourcefolder, "file1.txt")
        self.assertFalse(os.path.exists(test_sourcefolder_file1))
        with open(test_sourcefolder_file1, "w") as f:
            f.write("file1 contents")
        self.assertTrue(os.path.exists(test_sourcefolder_file1))

        test_sourcefolder_subfolder = path_utils.concat_path(test_sourcefolder, "subfolder")
        self.assertFalse(os.path.exists(test_sourcefolder_subfolder))
        os.mkdir(test_sourcefolder_subfolder)
        self.assertTrue(os.path.exists(test_sourcefolder_subfolder))

        test_sourcefolder_subfolder_file2 = path_utils.concat_path(test_sourcefolder_subfolder, "file2.txt")
        self.assertFalse(os.path.exists(test_sourcefolder_subfolder_file2))
        with open(test_sourcefolder_subfolder_file2, "w") as f:
            f.write("file2 contents")
        self.assertTrue(os.path.exists(test_sourcefolder_subfolder_file2))

        test_sourcefolder_subfolder_file3 = path_utils.concat_path(test_sourcefolder_subfolder, "file3.txt")
        self.assertFalse(os.path.exists(test_sourcefolder_subfolder_file3))
        with open(test_sourcefolder_subfolder_file3, "w") as f:
            f.write("file3 contents")
        self.assertTrue(os.path.exists(test_sourcefolder_subfolder_file3))

        test_sourcefolder_backup = path_utils.concat_path(local_dfb_storage, "the-subfolder", "renamed_sourcefolder")
        test_sourcefolder_file1_backup = path_utils.concat_path(local_dfb_storage, "the-subfolder", "renamed_sourcefolder", path_utils.basename_filtered(test_sourcefolder_file1))
        test_sourcefolder_subfolder_backup = path_utils.concat_path(local_dfb_storage, "the-subfolder", "renamed_sourcefolder", path_utils.basename_filtered(test_sourcefolder_subfolder))
        test_sourcefolder_subfolder_file2_backup = path_utils.concat_path(local_dfb_storage, "the-subfolder", "renamed_sourcefolder", path_utils.basename_filtered(test_sourcefolder_subfolder), path_utils.basename_filtered(test_sourcefolder_subfolder_file2))
        test_sourcefolder_subfolder_file3_backup = path_utils.concat_path(local_dfb_storage, "the-subfolder", "renamed_sourcefolder", path_utils.basename_filtered(test_sourcefolder_subfolder), path_utils.basename_filtered(test_sourcefolder_subfolder_file3))

        self.assertFalse(os.path.exists(test_sourcefolder_backup))
        self.assertFalse(os.path.exists(test_sourcefolder_file1_backup))
        self.assertFalse(os.path.exists(test_sourcefolder_subfolder_backup))
        self.assertFalse(os.path.exists(test_sourcefolder_subfolder_file2_backup))
        self.assertFalse(os.path.exists(test_sourcefolder_subfolder_file3_backup))

        v, r = local_dfb.make_backup_frompath("the-subfolder", "renamed_sourcefolder", test_sourcefolder)
        self.assertTrue(v)
        self.assertEqual(r, test_sourcefolder_backup)
        self.assertTrue(os.path.exists(test_sourcefolder_backup))
        self.assertTrue(os.path.exists(test_sourcefolder_file1_backup))
        self.assertTrue(os.path.exists(test_sourcefolder_subfolder_backup))
        self.assertTrue(os.path.exists(test_sourcefolder_subfolder_file2_backup))
        self.assertTrue(os.path.exists(test_sourcefolder_subfolder_file3_backup))

    def testDelayedFileBackupFromPath9(self):

        # single file source (broken symlink), root bk folder, no renaming

        local_dfb_storage = path_utils.concat_path(self.test_dir, "local_dfb_storage")
        local_dfb = delayed_file_backup.delayed_file_backup(local_dfb_storage)
        self.assertFalse(os.path.exists(local_dfb_storage))

        test_fn = "file1.txt"
        test_fn_link = "file1_link.txt"
        test_content = "source file contents"
        test_source_file_full = path_utils.concat_path(self.test_dir, test_fn)
        test_source_file_link_full = path_utils.concat_path(self.test_dir, test_fn_link)
        test_backup_file_link_full = path_utils.concat_path(local_dfb_storage, test_fn_link)
        self.assertFalse(os.path.exists(test_source_file_full))
        self.assertFalse(os.path.exists(test_source_file_link_full))
        self.assertFalse(os.path.exists(test_backup_file_link_full))
        with open(test_source_file_full, "w") as f:
            f.write(test_content)
        self.assertTrue(os.path.exists(test_source_file_full))
        os.symlink(test_source_file_full, test_source_file_link_full)
        self.assertTrue(os.path.exists(test_source_file_link_full))
        os.unlink(test_source_file_full)
        self.assertFalse(os.path.exists(test_source_file_full))
        self.assertTrue(path_utils.is_path_broken_symlink(test_source_file_link_full))

        v, r = local_dfb.make_backup_frompath(None, test_fn_link, test_source_file_link_full)
        self.assertTrue(v)
        self.assertEqual(r, test_backup_file_link_full)
        self.assertTrue(path_utils.is_path_broken_symlink(test_backup_file_link_full))

    def testDelayedFileBackupFromPath10(self):

        # single file source (broken symlink), root bk folder, renaming

        local_dfb_storage = path_utils.concat_path(self.test_dir, "local_dfb_storage")
        local_dfb = delayed_file_backup.delayed_file_backup(local_dfb_storage)
        self.assertFalse(os.path.exists(local_dfb_storage))

        test_fn = "file1.txt"
        test_fn_link = "file1_link.txt"
        test_fn_link_renamed = "file1_link_renamed.txt"
        test_content = "source file contents"
        test_source_file_full = path_utils.concat_path(self.test_dir, test_fn)
        test_source_file_link_full = path_utils.concat_path(self.test_dir, test_fn_link)
        test_backup_file_link_renamed_full = path_utils.concat_path(local_dfb_storage, test_fn_link_renamed)
        self.assertFalse(os.path.exists(test_source_file_full))
        self.assertFalse(os.path.exists(test_source_file_link_full))
        self.assertFalse(os.path.exists(test_backup_file_link_renamed_full))
        with open(test_source_file_full, "w") as f:
            f.write(test_content)
        self.assertTrue(os.path.exists(test_source_file_full))
        os.symlink(test_source_file_full, test_source_file_link_full)
        self.assertTrue(os.path.exists(test_source_file_link_full))
        os.unlink(test_source_file_full)
        self.assertFalse(os.path.exists(test_source_file_full))
        self.assertTrue(path_utils.is_path_broken_symlink(test_source_file_link_full))

        v, r = local_dfb.make_backup_frompath(None, test_fn_link_renamed, test_source_file_link_full)
        self.assertTrue(v)
        self.assertEqual(r, test_backup_file_link_renamed_full)
        self.assertTrue(path_utils.is_path_broken_symlink(test_backup_file_link_renamed_full))

    def testDelayedFileBackupFromPath11(self):

        # single file source (broken symlink), subfoldered bk, no renaming

        local_dfb_storage = path_utils.concat_path(self.test_dir, "local_dfb_storage")
        local_dfb = delayed_file_backup.delayed_file_backup(local_dfb_storage)
        self.assertFalse(os.path.exists(local_dfb_storage))

        test_fn = "file1.txt"
        test_fn_link = "file1_link.txt"
        test_content = "source file contents"
        test_source_file_full = path_utils.concat_path(self.test_dir, test_fn)
        test_source_file_link_full = path_utils.concat_path(self.test_dir, test_fn_link)
        test_backup_file_link_full = path_utils.concat_path(local_dfb_storage, "the-subfolder", test_fn_link)
        self.assertFalse(os.path.exists(test_source_file_full))
        self.assertFalse(os.path.exists(test_source_file_link_full))
        self.assertFalse(os.path.exists(test_backup_file_link_full))
        with open(test_source_file_full, "w") as f:
            f.write(test_content)
        self.assertTrue(os.path.exists(test_source_file_full))
        os.symlink(test_source_file_full, test_source_file_link_full)
        self.assertTrue(os.path.exists(test_source_file_link_full))
        os.unlink(test_source_file_full)
        self.assertFalse(os.path.exists(test_source_file_full))
        self.assertTrue(path_utils.is_path_broken_symlink(test_source_file_link_full))

        v, r = local_dfb.make_backup_frompath("the-subfolder", test_fn_link, test_source_file_link_full)
        self.assertTrue(v)
        self.assertEqual(r, test_backup_file_link_full)
        self.assertTrue(path_utils.is_path_broken_symlink(test_backup_file_link_full))

    def testDelayedFileBackupFromPath12(self):

        # single file source (broken symlink), subfoldered bk, renaming

        local_dfb_storage = path_utils.concat_path(self.test_dir, "local_dfb_storage")
        local_dfb = delayed_file_backup.delayed_file_backup(local_dfb_storage)
        self.assertFalse(os.path.exists(local_dfb_storage))

        test_fn = "file1.txt"
        test_fn_link = "file1_link.txt"
        test_fn_link_renamed = "file1_link_renamed.txt"
        test_content = "source file contents"
        test_source_file_full = path_utils.concat_path(self.test_dir, test_fn)
        test_source_file_link_full = path_utils.concat_path(self.test_dir, test_fn_link)
        test_backup_file_link_renamed_full = path_utils.concat_path(local_dfb_storage, "the-subfolder", test_fn_link_renamed)
        self.assertFalse(os.path.exists(test_source_file_full))
        self.assertFalse(os.path.exists(test_source_file_link_full))
        self.assertFalse(os.path.exists(test_backup_file_link_renamed_full))
        with open(test_source_file_full, "w") as f:
            f.write(test_content)
        self.assertTrue(os.path.exists(test_source_file_full))
        os.symlink(test_source_file_full, test_source_file_link_full)
        self.assertTrue(os.path.exists(test_source_file_link_full))
        os.unlink(test_source_file_full)
        self.assertFalse(os.path.exists(test_source_file_full))
        self.assertTrue(path_utils.is_path_broken_symlink(test_source_file_link_full))

        v, r = local_dfb.make_backup_frompath("the-subfolder", test_fn_link_renamed, test_source_file_link_full)
        self.assertTrue(v)
        self.assertEqual(r, test_backup_file_link_renamed_full)
        self.assertTrue(path_utils.is_path_broken_symlink(test_backup_file_link_renamed_full))

    def testDelayedFileBackupFromPath13(self):

        # folder source (broken symlink), root bk folder, no renaming

        local_dfb_storage = path_utils.concat_path(self.test_dir, "local_dfb_storage")
        local_dfb = delayed_file_backup.delayed_file_backup(local_dfb_storage)
        self.assertFalse(os.path.exists(local_dfb_storage))

        test_sourcefolder = path_utils.concat_path(self.test_dir, "sourcefolder")
        self.assertFalse(os.path.exists(test_sourcefolder))
        os.mkdir(test_sourcefolder)
        self.assertTrue(os.path.exists(test_sourcefolder))

        test_sourcefolder_file1 = path_utils.concat_path(test_sourcefolder, "file1.txt")
        self.assertFalse(os.path.exists(test_sourcefolder_file1))
        with open(test_sourcefolder_file1, "w") as f:
            f.write("file1 contents")
        self.assertTrue(os.path.exists(test_sourcefolder_file1))

        test_sourcefolder_subfolder = path_utils.concat_path(test_sourcefolder, "subfolder")
        self.assertFalse(os.path.exists(test_sourcefolder_subfolder))
        os.mkdir(test_sourcefolder_subfolder)
        self.assertTrue(os.path.exists(test_sourcefolder_subfolder))

        test_sourcefolder_subfolder_file2 = path_utils.concat_path(test_sourcefolder_subfolder, "file2.txt")
        self.assertFalse(os.path.exists(test_sourcefolder_subfolder_file2))
        with open(test_sourcefolder_subfolder_file2, "w") as f:
            f.write("file2 contents")
        self.assertTrue(os.path.exists(test_sourcefolder_subfolder_file2))

        test_sourcefolder_subfolder_file3 = path_utils.concat_path(test_sourcefolder_subfolder, "file3.txt")
        self.assertFalse(os.path.exists(test_sourcefolder_subfolder_file3))
        with open(test_sourcefolder_subfolder_file3, "w") as f:
            f.write("file3 contents")
        self.assertTrue(os.path.exists(test_sourcefolder_subfolder_file3))

        test_sourcefolder_link = path_utils.concat_path(self.test_dir, "sourcefolder_link")
        self.assertFalse(os.path.exists(test_sourcefolder_link))
        os.symlink(test_sourcefolder, test_sourcefolder_link)
        self.assertTrue(os.path.exists(test_sourcefolder_link))
        shutil.rmtree(test_sourcefolder)
        self.assertFalse(os.path.exists(test_sourcefolder))
        self.assertTrue(path_utils.is_path_broken_symlink(test_sourcefolder_link))

        test_sourcefolder_link_backup = path_utils.concat_path(local_dfb_storage, path_utils.basename_filtered(test_sourcefolder_link))
        self.assertFalse(path_utils.is_path_broken_symlink(test_sourcefolder_link_backup))

        v, r = local_dfb.make_backup_frompath(None, path_utils.basename_filtered(test_sourcefolder_link), test_sourcefolder_link)
        self.assertTrue(v)
        self.assertEqual(r, test_sourcefolder_link_backup)
        self.assertTrue(path_utils.is_path_broken_symlink(test_sourcefolder_link_backup))

    def testDelayedFileBackupFromPath14(self):

        # folder source (broken symlink), root bk folder, renaming

        local_dfb_storage = path_utils.concat_path(self.test_dir, "local_dfb_storage")
        local_dfb = delayed_file_backup.delayed_file_backup(local_dfb_storage)
        self.assertFalse(os.path.exists(local_dfb_storage))

        test_sourcefolder = path_utils.concat_path(self.test_dir, "sourcefolder")
        self.assertFalse(os.path.exists(test_sourcefolder))
        os.mkdir(test_sourcefolder)
        self.assertTrue(os.path.exists(test_sourcefolder))

        test_sourcefolder_file1 = path_utils.concat_path(test_sourcefolder, "file1.txt")
        self.assertFalse(os.path.exists(test_sourcefolder_file1))
        with open(test_sourcefolder_file1, "w") as f:
            f.write("file1 contents")
        self.assertTrue(os.path.exists(test_sourcefolder_file1))

        test_sourcefolder_subfolder = path_utils.concat_path(test_sourcefolder, "subfolder")
        self.assertFalse(os.path.exists(test_sourcefolder_subfolder))
        os.mkdir(test_sourcefolder_subfolder)
        self.assertTrue(os.path.exists(test_sourcefolder_subfolder))

        test_sourcefolder_subfolder_file2 = path_utils.concat_path(test_sourcefolder_subfolder, "file2.txt")
        self.assertFalse(os.path.exists(test_sourcefolder_subfolder_file2))
        with open(test_sourcefolder_subfolder_file2, "w") as f:
            f.write("file2 contents")
        self.assertTrue(os.path.exists(test_sourcefolder_subfolder_file2))

        test_sourcefolder_subfolder_file3 = path_utils.concat_path(test_sourcefolder_subfolder, "file3.txt")
        self.assertFalse(os.path.exists(test_sourcefolder_subfolder_file3))
        with open(test_sourcefolder_subfolder_file3, "w") as f:
            f.write("file3 contents")
        self.assertTrue(os.path.exists(test_sourcefolder_subfolder_file3))

        test_sourcefolder_link = path_utils.concat_path(self.test_dir, "sourcefolder_link")
        self.assertFalse(os.path.exists(test_sourcefolder_link))
        os.symlink(test_sourcefolder, test_sourcefolder_link)
        self.assertTrue(os.path.exists(test_sourcefolder_link))
        shutil.rmtree(test_sourcefolder)
        self.assertFalse(os.path.exists(test_sourcefolder))
        self.assertTrue(path_utils.is_path_broken_symlink(test_sourcefolder_link))

        test_sourcefolder_link_backup = path_utils.concat_path(local_dfb_storage, "sourcefolder_link_renamed")
        self.assertFalse(path_utils.is_path_broken_symlink(test_sourcefolder_link_backup))

        v, r = local_dfb.make_backup_frompath(None, "sourcefolder_link_renamed", test_sourcefolder_link)
        self.assertTrue(v)
        self.assertEqual(r, test_sourcefolder_link_backup)
        self.assertTrue(path_utils.is_path_broken_symlink(test_sourcefolder_link_backup))

    def testDelayedFileBackupFromPath15(self):

        # folder source (broken symlink), subfoldered bk, no renaming

        local_dfb_storage = path_utils.concat_path(self.test_dir, "local_dfb_storage")
        local_dfb = delayed_file_backup.delayed_file_backup(local_dfb_storage)
        self.assertFalse(os.path.exists(local_dfb_storage))

        test_sourcefolder = path_utils.concat_path(self.test_dir, "sourcefolder")
        self.assertFalse(os.path.exists(test_sourcefolder))
        os.mkdir(test_sourcefolder)
        self.assertTrue(os.path.exists(test_sourcefolder))

        test_sourcefolder_file1 = path_utils.concat_path(test_sourcefolder, "file1.txt")
        self.assertFalse(os.path.exists(test_sourcefolder_file1))
        with open(test_sourcefolder_file1, "w") as f:
            f.write("file1 contents")
        self.assertTrue(os.path.exists(test_sourcefolder_file1))

        test_sourcefolder_subfolder = path_utils.concat_path(test_sourcefolder, "subfolder")
        self.assertFalse(os.path.exists(test_sourcefolder_subfolder))
        os.mkdir(test_sourcefolder_subfolder)
        self.assertTrue(os.path.exists(test_sourcefolder_subfolder))

        test_sourcefolder_subfolder_file2 = path_utils.concat_path(test_sourcefolder_subfolder, "file2.txt")
        self.assertFalse(os.path.exists(test_sourcefolder_subfolder_file2))
        with open(test_sourcefolder_subfolder_file2, "w") as f:
            f.write("file2 contents")
        self.assertTrue(os.path.exists(test_sourcefolder_subfolder_file2))

        test_sourcefolder_subfolder_file3 = path_utils.concat_path(test_sourcefolder_subfolder, "file3.txt")
        self.assertFalse(os.path.exists(test_sourcefolder_subfolder_file3))
        with open(test_sourcefolder_subfolder_file3, "w") as f:
            f.write("file3 contents")
        self.assertTrue(os.path.exists(test_sourcefolder_subfolder_file3))

        test_sourcefolder_link = path_utils.concat_path(self.test_dir, "sourcefolder_link")
        self.assertFalse(os.path.exists(test_sourcefolder_link))
        os.symlink(test_sourcefolder, test_sourcefolder_link)
        self.assertTrue(os.path.exists(test_sourcefolder_link))
        shutil.rmtree(test_sourcefolder)
        self.assertFalse(os.path.exists(test_sourcefolder))
        self.assertTrue(path_utils.is_path_broken_symlink(test_sourcefolder_link))

        test_sourcefolder_link_backup = path_utils.concat_path(local_dfb_storage, "the-subfolder", path_utils.basename_filtered(test_sourcefolder_link))
        self.assertFalse(path_utils.is_path_broken_symlink(test_sourcefolder_link_backup))

        v, r = local_dfb.make_backup_frompath("the-subfolder", path_utils.basename_filtered(test_sourcefolder_link), test_sourcefolder_link)
        self.assertTrue(v)
        self.assertTrue(r, test_sourcefolder_link_backup)
        self.assertTrue(path_utils.is_path_broken_symlink(test_sourcefolder_link_backup))

    def testDelayedFileBackupFromPath16(self):

        # folder source (broken symlink), subfoldered bk, renaming

        local_dfb_storage = path_utils.concat_path(self.test_dir, "local_dfb_storage")
        local_dfb = delayed_file_backup.delayed_file_backup(local_dfb_storage)
        self.assertFalse(os.path.exists(local_dfb_storage))

        test_sourcefolder = path_utils.concat_path(self.test_dir, "sourcefolder")
        self.assertFalse(os.path.exists(test_sourcefolder))
        os.mkdir(test_sourcefolder)
        self.assertTrue(os.path.exists(test_sourcefolder))

        test_sourcefolder_file1 = path_utils.concat_path(test_sourcefolder, "file1.txt")
        self.assertFalse(os.path.exists(test_sourcefolder_file1))
        with open(test_sourcefolder_file1, "w") as f:
            f.write("file1 contents")
        self.assertTrue(os.path.exists(test_sourcefolder_file1))

        test_sourcefolder_subfolder = path_utils.concat_path(test_sourcefolder, "subfolder")
        self.assertFalse(os.path.exists(test_sourcefolder_subfolder))
        os.mkdir(test_sourcefolder_subfolder)
        self.assertTrue(os.path.exists(test_sourcefolder_subfolder))

        test_sourcefolder_subfolder_file2 = path_utils.concat_path(test_sourcefolder_subfolder, "file2.txt")
        self.assertFalse(os.path.exists(test_sourcefolder_subfolder_file2))
        with open(test_sourcefolder_subfolder_file2, "w") as f:
            f.write("file2 contents")
        self.assertTrue(os.path.exists(test_sourcefolder_subfolder_file2))

        test_sourcefolder_subfolder_file3 = path_utils.concat_path(test_sourcefolder_subfolder, "file3.txt")
        self.assertFalse(os.path.exists(test_sourcefolder_subfolder_file3))
        with open(test_sourcefolder_subfolder_file3, "w") as f:
            f.write("file3 contents")
        self.assertTrue(os.path.exists(test_sourcefolder_subfolder_file3))

        test_sourcefolder_link = path_utils.concat_path(self.test_dir, "sourcefolder_link")
        self.assertFalse(os.path.exists(test_sourcefolder_link))
        os.symlink(test_sourcefolder, test_sourcefolder_link)
        self.assertTrue(os.path.exists(test_sourcefolder_link))
        shutil.rmtree(test_sourcefolder)
        self.assertFalse(os.path.exists(test_sourcefolder))
        self.assertTrue(path_utils.is_path_broken_symlink(test_sourcefolder_link))

        test_sourcefolder_link_backup = path_utils.concat_path(local_dfb_storage, "the-subfolder", "sourcefolder_link_renamed")
        self.assertFalse(path_utils.is_path_broken_symlink(test_sourcefolder_link_backup))

        v, r = local_dfb.make_backup_frompath("the-subfolder", "sourcefolder_link_renamed", test_sourcefolder_link)
        self.assertTrue(v)
        self.assertEqual(r, test_sourcefolder_link_backup)
        self.assertTrue(path_utils.is_path_broken_symlink(test_sourcefolder_link_backup))

if __name__ == '__main__':
    unittest.main()
