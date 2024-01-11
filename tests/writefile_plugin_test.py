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

import writefile_plugin

def FileHasContents(filename, contents):
    if not os.path.exists(filename):
        return False
    local_contents = ""
    with open(filename, "r") as f:
        local_contents = f.read()
    if local_contents == contents:
        return True
    return False

class WritefilePluginTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("writefile_plugin_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # the test task
        self.writefile_task = writefile_plugin.CustomTask()

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testWritefilePluginReadParams1(self):

        local_params = {}
        self.writefile_task.params = local_params

        v, r = self.writefile_task._read_params()
        self.assertFalse(v)

    def testWritefilePluginReadParams2(self):

        local_params = {}
        local_params["exec_path"] = self.existent_path1
        self.writefile_task.params = local_params

        v, r = self.writefile_task._read_params()
        self.assertFalse(v)

    def testWritefilePluginReadParams3(self):

        local_params = {}
        local_params["exec_path"] = self.nonexistent_path1
        local_params["operation"] = "dummy_value1"
        self.writefile_task.params = local_params

        v, r = self.writefile_task._read_params()
        self.assertFalse(v)

    def testWritefilePluginRunTask1(self):

        local_params = {}
        local_params["exec_path"] = self.existent_path1
        local_params["operation"] = "invalid-operation"
        self.writefile_task.params = local_params

        with mock.patch("writefile_plugin.CustomTask.task_build", return_value=(True, None)) as dummy:
            v, r = self.writefile_task.run_task(print, "exe_name")
            self.assertFalse(v)
            dummy.assert_not_called()

    def testWritefilePluginRunTask2(self):

        local_params = {}
        local_params["exec_path"] = self.existent_path1
        local_params["operation"] = "build"
        self.writefile_task.params = local_params

        with mock.patch("writefile_plugin.CustomTask.task_build", return_value=(True, None)) as dummy:
            v, r = self.writefile_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(print, self.existent_path1, None, None, None, [], None, None, False)

    def testWritefilePluginRunTask3(self):

        local_params = {}
        local_params["exec_path"] = self.existent_path1
        local_params["operation"] = "fetch"
        self.writefile_task.params = local_params

        with mock.patch("writefile_plugin.CustomTask.task_fetch", return_value=(True, None)) as dummy:
            v, r = self.writefile_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(print, self.existent_path1, None, None, None, False)

    def testWritefilePluginRunTask4(self):

        local_params = {}
        local_params["exec_path"] = self.existent_path1
        local_params["operation"] = "clean"
        self.writefile_task.params = local_params

        with mock.patch("writefile_plugin.CustomTask.task_clean", return_value=(True, None)) as dummy:
            v, r = self.writefile_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(print, self.existent_path1, False, None, None, False)

if __name__ == '__main__':
    unittest.main()
