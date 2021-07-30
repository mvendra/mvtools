#!/usr/bin/env python3

import sys
import os
import shutil
import unittest
from unittest import mock
from unittest.mock import patch

import mvtools_test_fixture

import cmake_wrapper
import generic_run

class CmakeWrapperTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("cmake_wrapper_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        self.result_obj = generic_run.run_cmd_result(None, None, None, None)

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testConfigureAndGenerateFail1(self):
        with mock.patch("generic_run.run_cmd", return_value=(True, self.result_obj)) as dummy:
            v, r = cmake_wrapper.configure_and_generate("test3", "test4", "test5", "test6", None)
            self.assertFalse(v)

    def testConfigureAndGenerateFail2(self):
        self.result_obj.stdout = "test1"
        self.result_obj.stderr = "test2"
        with mock.patch("generic_run.run_cmd", return_value=(False, "error message")) as dummy:
            v, r = cmake_wrapper.configure_and_generate("test3", "test4", "test5", "test6", {})
            self.assertFalse(v)
            self.assertEqual(r, "error message")

    def testConfigureAndGenerate1(self):
        self.result_obj.success = True
        self.result_obj.stdout = "test1"
        self.result_obj.stderr = "test2"
        with mock.patch("generic_run.run_cmd", return_value=(True, self.result_obj)) as dummy:
            self.assertEqual(cmake_wrapper.configure_and_generate("test3", "test4", "test5", "test6", {}), (True, (True, "test1", "test2")))
            dummy.assert_called_with(["test3", "test4", "-G", "test6"], use_cwd="test5")

    def testConfigureAndGenerate2(self):
        self.result_obj.success = True
        self.result_obj.stdout = "test1"
        self.result_obj.stderr = "test2"
        with mock.patch("generic_run.run_cmd", return_value=(True, self.result_obj)) as dummy:
            self.assertEqual(cmake_wrapper.configure_and_generate("test3", "test4", "test5", "test6", {"optname": ("opttype", "optval")}), (True, (True, "test1", "test2")))
            dummy.assert_called_with(["test3", "test4", "-G", "test6", "-Doptname:opttype=optval"], use_cwd="test5")

    def testConfigureAndGenerate3(self):
        self.result_obj.success = True
        self.result_obj.stdout = "test1"
        self.result_obj.stderr = "test2"
        with mock.patch("generic_run.run_cmd", return_value=(True, self.result_obj)) as dummy:
            self.assertEqual(cmake_wrapper.configure_and_generate(None, "test4", "test5", "test6", {}), (True, (True, "test1", "test2")))
            dummy.assert_called_with(["cmake", "test4", "-G", "test6"], use_cwd="test5")

if __name__ == '__main__':
    unittest.main()
