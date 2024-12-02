#!/usr/bin/env python3

import sys
import os
import shutil
import unittest
from unittest import mock
from unittest.mock import patch

import mvtools_test_fixture

import make_wrapper
import generic_run

class MakeWrapperTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("make_wrapper_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        self.result_obj = generic_run.run_cmd_result(None, None, None, None)

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testMakeFail(self):
        self.result_obj.success = False
        self.result_obj.stdout = "test1"
        self.result_obj.stderr = "test2"
        with mock.patch("generic_run.run_cmd", return_value=(False, "error message")) as dummy:
            self.assertEqual(make_wrapper.make("test3", "test4", None), (False, "Failed running make command: [error message]"))

    def testMake1(self):
        self.result_obj.success = True
        self.result_obj.stdout = "test1"
        self.result_obj.stderr = "test2"
        with mock.patch("generic_run.run_cmd", return_value=(True, self.result_obj)) as dummy:
            self.assertEqual(make_wrapper.make("test3", "test4", None), (True, (True, "test1", "test2")))
            dummy.assert_called_with(["make", "test4"], use_cwd="test3")

    def testMake2(self):
        self.result_obj.success = True
        self.result_obj.stdout = "test1"
        self.result_obj.stderr = "test2"
        with mock.patch("generic_run.run_cmd", return_value=(True, self.result_obj)) as dummy:
            self.assertEqual(make_wrapper.make("test3", "test4", "test5"), (True, (True, "test1", "test2")))
            dummy.assert_called_with(["make", "test4", "PREFIX=test5"], use_cwd="test3")

if __name__ == '__main__':
    unittest.main()
