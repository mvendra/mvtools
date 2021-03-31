#!/usr/bin/env python3

import sys
import os
import shutil
import unittest

import mvtools_test_fixture
import create_and_write_file
import path_utils

import shred_wrapper

class ShredWrapperTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("shred_wrapper_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # create test content
        self.folder1 = path_utils.concat_path(self.test_dir, "folder1")
        self.folder1_file1 = path_utils.concat_path(self.folder1, "file1.txt")

        self.folder2 = path_utils.concat_path(self.folder1, "folder2")
        self.folder2_file2 = path_utils.concat_path(self.folder2, "file2.txt")

        self.file3 = path_utils.concat_path(self.test_dir, "file3.txt")

        os.mkdir(self.folder1)
        os.mkdir(self.folder2)
        create_and_write_file.create_file_contents(self.folder1_file1, "abc")
        create_and_write_file.create_file_contents(self.folder2_file2, "def")
        create_and_write_file.create_file_contents(self.file3, "ghi")

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testShredFile(self):
        self.assertTrue(os.path.exists(self.file3))
        shred_wrapper.shred_target(self.file3)
        self.assertFalse(os.path.exists(self.file3))

    def testShredFolder(self):
        self.assertTrue(os.path.exists(self.folder1))
        self.assertTrue(os.path.exists(self.folder1_file1))
        self.assertTrue(os.path.exists(self.folder2))
        self.assertTrue(os.path.exists(self.folder2_file2))
        shred_wrapper.shred_target(self.folder1)
        self.assertFalse(os.path.exists(self.folder1))
        self.assertFalse(os.path.exists(self.folder1_file1))
        self.assertFalse(os.path.exists(self.folder2))
        self.assertFalse(os.path.exists(self.folder2_file2))

if __name__ == '__main__':
    unittest.main()
