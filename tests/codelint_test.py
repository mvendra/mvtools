#!/usr/bin/env python3

import sys
import os
import shutil
import unittest

"""
# mvtodo: needed?
from unittest import mock
from unittest.mock import patch
from unittest.mock import call
"""

import mvtools_test_fixture
import path_utils

import codelint

class CodeLintTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("codelint_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testHelperValidateMsgpatchReturn1(self):

        v, r = codelint.helper_validate_msgpatch_return(123, [])
        self.assertFalse(v)
        self.assertEqual(r, "invalid result return: msg is not a str")

    def testHelperValidateMsgpatchReturn2(self):

        v, r = codelint.helper_validate_msgpatch_return("error-msg", ())
        self.assertFalse(v)
        self.assertEqual(r, "invalid result return: patches is not a list")

    def testHelperValidateMsgpatchReturn3(self):

        v, r = codelint.helper_validate_msgpatch_return("error-msg", [123])
        self.assertFalse(v)
        self.assertEqual(r, "invalid result return: patches entry is not a tuple")

    def testHelperValidateMsgpatchReturn4(self):

        v, r = codelint.helper_validate_msgpatch_return("error-msg", [("1", "contents")])
        self.assertFalse(v)
        self.assertEqual(r, "invalid result return: patches entry, first tuple entry is not an int")

    def testHelperValidateMsgpatchReturn5(self):

        v, r = codelint.helper_validate_msgpatch_return("error-msg", [(1, 123)])
        self.assertFalse(v)
        self.assertEqual(r, "invalid result return: patches entry, second tuple entry is not a str")

    def testHelperValidateMsgpatchReturn6(self):

        v, r = codelint.helper_validate_msgpatch_return("error-msg", [])
        self.assertTrue(v)
        self.assertEqual(r, None)

    def testHelperValidateMsgpatchReturn7(self):

        v, r = codelint.helper_validate_msgpatch_return("error-msg", [(1, "contents")])
        self.assertTrue(v)
        self.assertEqual(r, None)

if __name__ == '__main__':
    unittest.main()
