#!/usr/bin/env python3

import sys
import os
import shutil
import unittest

import mvtools_test_fixture

import svn_lib

class SvnLibTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("svn_lib_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testIsNonNumber(self):

        self.assertTrue(svn_lib.is_nonnumber("a"))
        self.assertTrue(svn_lib.is_nonnumber("!"))
        self.assertFalse(svn_lib.is_nonnumber("1"))

    def testIsNonSpaceOrTabs(self):

        self.assertTrue(svn_lib.is_nonspaceortabs("a"))
        self.assertFalse(svn_lib.is_nonspaceortabs(" "))
        self.assertFalse(svn_lib.is_nonspaceortabs("\t"))

if __name__ == '__main__':
    unittest.main()
