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
        v, r = local_dfb.make_backup(test_fn, test_content)
        self.assertFalse(v)

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
        v, r = local_dfb.make_backup(test_fn, test_content)
        self.assertTrue(v)
        self.assertTrue(os.path.exists(test_patch_file_full))

if __name__ == '__main__':
    unittest.main()
