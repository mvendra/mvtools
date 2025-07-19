#!/usr/bin/env python3

import sys
import os
import shutil
import unittest

import mvtools_test_fixture
import mvtools_exception
import create_and_write_file
import path_utils

import getcontents

class GetContentsTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("getcontents_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # source files
        self.content_file = path_utils.concat_path(self.test_dir, "test_contents.txt")
        self.nonexistent_file = path_utils.concat_path(self.test_dir, "nonexistent")
        create_and_write_file.create_file_contents(self.content_file, "abcdef123456")

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testNonExistent(self):

        self.assertTrue(mvtools_test_fixture.throwsExcept(getcontents.getcontents, self.nonexistent_file, mvtools_exception.mvtools_exception))

    def testVanilla(self):

        self.assertEqual(getcontents.getcontents(self.content_file), "abcdef123456")

if __name__ == '__main__':
    unittest.main()
