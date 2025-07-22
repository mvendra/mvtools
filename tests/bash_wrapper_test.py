#!/usr/bin/env python3

import sys
import os
import shutil
import unittest
from unittest import mock
from unittest.mock import patch

import mvtools_test_fixture

import bash_wrapper
import generic_run

class BashWrapperTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("bash_wrapper_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        self.result_obj = generic_run.run_cmd_result(None, None, None, None)

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testExec1(self):
        with mock.patch("generic_run.run_cmd", return_value=(True, self.result_obj)) as dummy:
            v, r = bash_wrapper.exec(None, None, [])
            self.assertFalse(v)
            dummy.assert_not_called()

    def testExec2(self):
        with mock.patch("generic_run.run_cmd", return_value=(True, self.result_obj)) as dummy:
            v, r = bash_wrapper.exec([], None, [])
            self.assertFalse(v)
            dummy.assert_not_called()

    def testExec3(self):
        with mock.patch("generic_run.run_cmd", return_value=(True, self.result_obj)) as dummy:
            v, r = bash_wrapper.exec("test-script.sh", None, None)
            self.assertFalse(v)
            dummy.assert_not_called()

    def testExec4(self):
        with mock.patch("generic_run.run_cmd", return_value=(True, self.result_obj)) as dummy:
            v, r = bash_wrapper.exec("test-script.sh", None, [])
            self.assertTrue(v)
            dummy.assert_called_with(["bash", "test-script.sh"])

    def testExec5(self):
        with mock.patch("generic_run.run_cmd", return_value=(True, self.result_obj)) as dummy:
            v, r = bash_wrapper.exec("test-script.sh", "test-cwd", [])
            self.assertTrue(v)
            dummy.assert_called_with(["bash", "test-script.sh"], use_cwd="test-cwd")

    def testExec6(self):
        with mock.patch("generic_run.run_cmd", return_value=(True, self.result_obj)) as dummy:
            v, r = bash_wrapper.exec("test-script.sh", "test-cwd", ["param1", "param2"])
            self.assertTrue(v)
            dummy.assert_called_with(["bash", "test-script.sh", "param1", "param2"], use_cwd="test-cwd")

if __name__ == "__main__":
    unittest.main()
