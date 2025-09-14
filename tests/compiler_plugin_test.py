#!/usr/bin/env python

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
import clang_wrapper

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
        self.assertEqual(r, "compiler is a required parameter")

    def testCompilerPluginReadParams2(self):

        local_params = {}
        local_params["compiler"] = "gcc"
        self.compiler_task.params = local_params

        v, r = self.compiler_task._read_params()
        self.assertFalse(v)
        self.assertEqual(r, "params is a required parameter")

    def testCompilerPluginReadParams3(self):

        test_path_local = path_utils.concat_path(self.test_dir, "test_path_local")
        self.assertFalse(os.path.exists(test_path_local))

        local_params = {}
        local_params["compiler_base"] = test_path_local
        local_params["compiler"] = "gcc"
        local_params["params"] = "dummy_value2"
        self.compiler_task.params = local_params

        v, r = self.compiler_task._read_params()
        self.assertFalse(v)
        self.assertEqual(r, "compiler_base [%s] does not exist" % test_path_local)

    def testCompilerPluginReadParams4(self):

        local_params = {}
        local_params["compiler"] = "unsupported-compiler"
        local_params["params"] = "dummy_value1"
        self.compiler_task.params = local_params

        v, r = self.compiler_task._read_params()
        self.assertFalse(v)
        self.assertEqual(r, "Compiler [unsupported-compiler] is unknown/not supported")

    def testCompilerPluginReadParams5(self):

        test_path_local = path_utils.concat_path(self.test_dir, "test_path_local")
        os.mkdir(test_path_local)
        self.assertTrue(os.path.exists(test_path_local))

        local_params = {}
        local_params["compiler_base"] = test_path_local
        local_params["compiler"] = "gcc"
        local_params["params"] = "dummy_value2"
        self.compiler_task.params = local_params

        v, r = self.compiler_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, (test_path_local, gcc_wrapper, ["dummy_value2"]))

    def testCompilerPluginReadParams6(self):

        local_params = {}
        local_params["compiler"] = "gcc"
        local_params["params"] = "dummy_value1"
        self.compiler_task.params = local_params

        v, r = self.compiler_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, (None, gcc_wrapper, ["dummy_value1"]))

    def testCompilerPluginReadParams7(self):

        local_params = {}
        local_params["compiler"] = "clang"
        local_params["params"] = "dummy_value1"
        self.compiler_task.params = local_params

        v, r = self.compiler_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, (None, clang_wrapper, ["dummy_value1"]))

    def testCompilerPluginRunTask1(self):

        local_params = {}
        local_params["compiler"] = "gcc"
        local_params["params"] = "dummy_value1"
        self.compiler_task.params = local_params

        with mock.patch("gcc_wrapper.exec", return_value=(True, None)) as dummy:
            v, r = self.compiler_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(None, ["dummy_value1"])

    def testCompilerPluginRunTask2(self):

        local_params = {}
        local_params["compiler"] = "gcc"
        local_params["params"] = ["dummy_value1", "dummy_value2"]
        self.compiler_task.params = local_params

        with mock.patch("gcc_wrapper.exec", return_value=(True, None)) as dummy:
            v, r = self.compiler_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(None, ["dummy_value1", "dummy_value2"])

    def testCompilerPluginRunTask3(self):

        test_path_local = path_utils.concat_path(self.test_dir, "test_path_local")
        os.mkdir(test_path_local)
        self.assertTrue(os.path.exists(test_path_local))

        local_params = {}
        local_params["compiler_base"] = test_path_local
        local_params["compiler"] = "gcc"
        local_params["params"] = "dummy_value1"
        self.compiler_task.params = local_params

        with mock.patch("gcc_wrapper.exec", return_value=(True, None)) as dummy:
            v, r = self.compiler_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(test_path_local, ["dummy_value1"])

    def testCompilerPluginRunTask4(self):

        local_params = {}
        local_params["compiler"] = "clang"
        local_params["params"] = "dummy_value1"
        self.compiler_task.params = local_params

        with mock.patch("clang_wrapper.exec", return_value=(True, None)) as dummy:
            v, r = self.compiler_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(None, ["dummy_value1"])

    def testCompilerPluginRunTask5(self):

        local_params = {}
        local_params["compiler"] = "clang"
        local_params["params"] = ["dummy_value1", "dummy_value2"]
        self.compiler_task.params = local_params

        with mock.patch("clang_wrapper.exec", return_value=(True, None)) as dummy:
            v, r = self.compiler_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(None, ["dummy_value1", "dummy_value2"])

    def testCompilerPluginRunTask6(self):

        test_path_local = path_utils.concat_path(self.test_dir, "test_path_local")
        os.mkdir(test_path_local)
        self.assertTrue(os.path.exists(test_path_local))

        local_params = {}
        local_params["compiler_base"] = test_path_local
        local_params["compiler"] = "clang"
        local_params["params"] = "dummy_value1"
        self.compiler_task.params = local_params

        with mock.patch("clang_wrapper.exec", return_value=(True, None)) as dummy:
            v, r = self.compiler_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(test_path_local, ["dummy_value1"])

if __name__ == "__main__":
    unittest.main()
