#!/usr/bin/env python3

import sys
import os
import shutil
import unittest

import mvtools_test_fixture
import mvtools_exception
import getcontents
import path_utils

import create_and_write_file
import open_and_update_file

class OpenAndUpdateFileTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("open_and_update_file_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # source files
        self.content_file = path_utils.concat_path(self.test_dir, "test_contents.txt")

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testUpdateFileContentsDoesntExist(self):

        self.assertFalse(os.path.exists(self.content_file))
        self.assertTrue(mvtools_test_fixture.throwsExcept2(mvtools_exception.mvtools_exception, open_and_update_file.update_file_contents, self.content_file, "andthensomemore"))
        self.assertFalse(os.path.exists(self.content_file))

    def testUpdateFileContentsVanilla(self):

        self.assertFalse(os.path.exists(self.content_file))
        create_and_write_file.create_file_contents(self.content_file, "abcdef123456")
        self.assertTrue(os.path.exists(self.content_file))
        self.assertEqual(getcontents.getcontents(self.content_file), "abcdef123456")
        open_and_update_file.update_file_contents(self.content_file, "andthensomemore")
        self.assertEqual(getcontents.getcontents(self.content_file), "abcdef123456andthensomemore")

if __name__ == '__main__':
    unittest.main()
