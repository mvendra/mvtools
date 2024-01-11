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

        # nonexistent path 1
        self.nonexistent_path1 = path_utils.concat_path(self.test_dir, "nonexistent_path1")

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
        local_params["target_file"] = self.nonexistent_path1
        self.writefile_task.params = local_params

        v, r = self.writefile_task._read_params()
        self.assertFalse(v)

    def testWritefilePluginReadParams3(self):

        local_params = {}
        local_params["target_file"] = self.nonexistent_path1
        local_params["mode"] = "w"
        self.writefile_task.params = local_params

        v, r = self.writefile_task._read_params()
        self.assertFalse(v)

    def testWritefilePluginReadParams4(self):

        local_params = {}
        local_params["target_file"] = self.nonexistent_path1
        local_params["mode"] = "w"
        local_params["content"] = "dummy-content"
        self.writefile_task.params = local_params

        v, r = self.writefile_task._read_params()
        self.assertTrue(v)

    def testWritefilePluginRunTask1(self):

        local_params = {}
        local_params["target_file"] = self.nonexistent_path1
        local_params["mode"] = "w"
        local_params["content"] = "dummy-content"
        self.writefile_task.params = local_params

        self.assertFalse(os.path.exists(self.nonexistent_path1))
        v, r = self.writefile_task.run_task(print, "exe_name")
        self.assertTrue(v)
        self.assertTrue(os.path.exists(self.nonexistent_path1))
        self.assertTrue(FileHasContents(self.nonexistent_path1, "dummy-content"))

    def testWritefilePluginRunTask2(self):

        local_params = {}
        local_params["target_file"] = self.nonexistent_path1
        local_params["mode"] = "a"
        local_params["content"] = "\ndummy-content2"
        self.writefile_task.params = local_params

        self.assertFalse(os.path.exists(self.nonexistent_path1))
        with open(self.nonexistent_path1, "w") as f:
            f.write("dummy-content1")
        v, r = self.writefile_task.run_task(print, "exe_name")
        self.assertTrue(v)
        self.assertTrue(os.path.exists(self.nonexistent_path1))
        self.assertTrue(FileHasContents(self.nonexistent_path1, "dummy-content1\ndummy-content2"))

if __name__ == '__main__':
    unittest.main()
