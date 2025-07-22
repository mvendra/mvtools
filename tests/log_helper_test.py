#!/usr/bin/env python3

import sys
import os
import shutil
import unittest
from unittest import mock
from unittest.mock import patch

import mvtools_test_fixture

import log_helper

class LogHelperTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("log_helper_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        self.warnings = None

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testAddToWarnings1(self):

        self.warnings = log_helper.add_to_warnings(self.warnings, None)
        self.assertEqual(self.warnings, None)

    def testAddToWarnings2(self):

        self.warnings = log_helper.add_to_warnings(self.warnings, "first warning")
        self.assertEqual(self.warnings, "first warning")

    def testAddToWarnings3(self):

        self.warnings = log_helper.add_to_warnings(self.warnings, "first warning")
        self.warnings = log_helper.add_to_warnings(self.warnings, "second warning")
        self.assertEqual(self.warnings, "first warning%ssecond warning" % os.linesep)

    def testAddToWarnings4(self):

        self.warnings = log_helper.add_to_warnings(self.warnings, "first warning")
        self.warnings = log_helper.add_to_warnings(self.warnings, None)
        self.assertEqual(self.warnings, "first warning")

if __name__ == "__main__":
    unittest.main()
