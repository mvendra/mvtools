#!/usr/bin/env python3

import sys
import os
import shutil
import unittest

import mvtools_test_fixture
import create_and_write_file
import path_utils

import ag_wrapper

class AgWrapperTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("ag_wrapper_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # prepare test content
        self.file1 = "file1.txt"
        self.file1_full = path_utils.concat_path(self.test_dir, self.file1)

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testSilversearch1(self):

        v, r = ag_wrapper.silversearch(self.file1_full, "abc")
        self.assertFalse(v)
        self.assertTrue("does not exist" in r)

    def testSilversearch2(self):

        os.mkdir(self.file1_full)

        v, r = ag_wrapper.silversearch(self.file1_full, "abc")
        self.assertFalse(v)
        self.assertTrue("is a directory" in r)

    def testSilversearch3(self):

        create_and_write_file.create_file_contents(self.file1_full, "abcdefxyz")

        v, r = ag_wrapper.silversearch(self.file1_full, "qwe")
        self.assertTrue(v)
        self.assertEqual(r, "")

    def testSilversearch4(self):

        create_and_write_file.create_file_contents(self.file1_full, "abcdefxyz")

        v, r = ag_wrapper.silversearch(self.file1_full, "abc")
        self.assertTrue(v)
        self.assertEqual(r, "1:abcdefxyz%s" % os.linesep)

if __name__ == "__main__":
    unittest.main()
