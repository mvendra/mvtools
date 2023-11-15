#!/usr/bin/env python3

import sys
import os
import shutil
import unittest
from unittest import mock
from unittest.mock import patch
from unittest.mock import call

import mvtools_test_fixture
import create_and_write_file
import path_utils
import output_backup_helper

import python_plugin

def FileHasContents(filename, contents):
    if not os.path.exists(filename):
        return False
    local_contents = ""
    with open(filename, "r") as f:
        local_contents = f.read()
    if local_contents == contents:
        return True
    return False

class PythonPluginTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("python_plugin_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # the test task
        self.python_task = python_plugin.CustomTask()

        # existent path 1
        self.existent_path1 = path_utils.concat_path(self.test_dir, "existent_path1")
        os.mkdir(self.existent_path1)

        # existent path 2
        self.existent_path2 = path_utils.concat_path(self.test_dir, "existent_path2")
        os.mkdir(self.existent_path2)

        # nonexistent path 1
        self.nonexistent_path1 = path_utils.concat_path(self.test_dir, "nonexistent_path1")

        # dumped_stdout_file
        self.dumped_stdout_file = path_utils.concat_path(self.test_dir, "dumped_stdout_file")

        # dumped_stderr_file
        self.dumped_stderr_file = path_utils.concat_path(self.test_dir, "dumped_stderr_file")

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testPythonPluginReadParams1(self):

        local_params = {}
        self.python_task.params = local_params

        v, r = self.python_task._read_params()
        self.assertFalse(v)

    def testPythonPluginReadParams2(self):

        local_params = {}
        local_params["script"] = self.nonexistent_path1
        self.python_task.params = local_params

        v, r = self.python_task._read_params()
        self.assertFalse(v)

    def testPythonPluginReadParams3(self):

        local_params = {}
        local_params["script"] = self.existent_path1
        self.python_task.params = local_params

        v, r = self.python_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, (self.existent_path1, None, [], None, None, False) )

    def testPythonPluginReadParams4(self):

        local_params = {}
        local_params["script"] = self.existent_path1
        local_params["cwd"] = self.nonexistent_path1
        self.python_task.params = local_params

        v, r = self.python_task._read_params()
        self.assertFalse(v)

    def testPythonPluginReadParams5(self):

        local_params = {}
        local_params["script"] = self.existent_path1
        local_params["cwd"] = self.existent_path2
        self.python_task.params = local_params

        v, r = self.python_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, (self.existent_path1, self.existent_path2, [], None, None, False) )

    def testPythonPluginReadParams6(self):

        local_params = {}
        local_params["script"] = self.existent_path1
        local_params["cwd"] = self.existent_path2
        local_params["args"] = "dummy_value1"
        self.python_task.params = local_params

        v, r = self.python_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, (self.existent_path1, self.existent_path2, ["dummy_value1"], None, None, False) )

    def testPythonPluginReadParams7(self):

        local_params = {}
        local_params["script"] = self.existent_path1
        local_params["cwd"] = self.existent_path2
        local_params["args"] = ["dummy_value1", "dummy_value2"]
        self.python_task.params = local_params

        v, r = self.python_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, (self.existent_path1, self.existent_path2, ["dummy_value1", "dummy_value2"], None, None, False) )

    def testPythonPluginReadParams8(self):

        local_params = {}
        local_params["script"] = self.existent_path1
        local_params["cwd"] = self.existent_path2
        local_params["args"] = "dummy_value1"
        local_params["save_output"] = "dummy_value2"
        self.python_task.params = local_params

        v, r = self.python_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, (self.existent_path1, self.existent_path2, ["dummy_value1"], "dummy_value2", None, False) )

    def testPythonPluginReadParams9(self):

        local_params = {}
        local_params["script"] = self.existent_path1
        local_params["cwd"] = self.existent_path2
        local_params["args"] = "dummy_value1"
        local_params["save_output"] = "dummy_value2"
        local_params["save_error_output"] = "dummy_value3"
        self.python_task.params = local_params

        v, r = self.python_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, (self.existent_path1, self.existent_path2, ["dummy_value1"], "dummy_value2", "dummy_value3", False) )

    def testPythonPluginReadParams10(self):

        local_params = {}
        local_params["script"] = self.existent_path1
        local_params["cwd"] = self.existent_path2
        local_params["args"] = "dummy_value1"
        local_params["save_output"] = "dummy_value2"
        local_params["save_error_output"] = "dummy_value3"
        local_params["suppress_stderr_warnings"] = "dummy_value4"
        self.python_task.params = local_params

        v, r = self.python_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, (self.existent_path1, self.existent_path2, ["dummy_value1"], "dummy_value2", "dummy_value3", True) )

if __name__ == '__main__':
    unittest.main()
