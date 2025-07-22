#!/usr/bin/env python3

import sys
import os
import shutil
import unittest
from unittest import mock
from unittest.mock import patch
from unittest.mock import call

import mvtools_test_fixture
import path_utils
import gcc_wrapper

import compiler_plugin

class CompilerPluginTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("compiler_plugin_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # the test task
        self.compiler_task = compiler_plugin.CustomTask()

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testCompilerPluginReadParams1(self):

        local_params = {}
        local_params["params"] = "dummy_value1"
        self.compiler_task.params = local_params

        v, r = self.compiler_task._read_params()
        self.assertFalse(v)

    def testCompilerPluginReadParams2(self):

        local_params = {}
        local_params["compiler"] = "gcc"
        self.compiler_task.params = local_params

        v, r = self.compiler_task._read_params()
        self.assertFalse(v)

    def testCompilerPluginReadParams3(self):

        local_params = {}
        local_params["compiler"] = "not-supported-compiler"
        local_params["params"] = "dummy_value1"
        self.compiler_task.params = local_params

        v, r = self.compiler_task._read_params()
        self.assertFalse(v)

    def testCompilerPluginReadParams4(self):

        local_params = {}
        local_params["compiler"] = "gcc"
        local_params["params"] = "dummy_value1"
        self.compiler_task.params = local_params

        v, r = self.compiler_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, (gcc_wrapper, ["dummy_value1"]) )

    def testCompilerPluginRunTask1(self):

        local_params = {}
        local_params["compiler"] = "gcc"
        local_params["params"] = "dummy_value1"
        self.compiler_task.params = local_params

        with mock.patch("gcc_wrapper.exec", return_value=(True, None)) as dummy:
            v, r = self.compiler_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.called_with(["dummy_value1"])

    def testCompilerPluginRunTask2(self):

        local_params = {}
        local_params["compiler"] = "gcc"
        local_params["params"] = ["dummy_value1", "dummy_value2"]
        self.compiler_task.params = local_params

        with mock.patch("gcc_wrapper.exec", return_value=(True, None)) as dummy:
            v, r = self.compiler_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.called_with(["dummy_value1", "dummy_value2"])

if __name__ == "__main__":
    unittest.main()
