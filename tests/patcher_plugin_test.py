#!/usr/bin/env python

import sys
import os
import shutil
import unittest
from unittest import mock
from unittest.mock import patch

import mvtools_test_fixture
import create_and_write_file
import path_utils

import patcher_plugin

def is_file_contents(target_path, contents):

    local_contents = ""
    with open(target_path, "r") as f:
        local_contents = f.read()
    return local_contents == contents

class PatcherPluginTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("patcher_plugin_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # the test task
        self.patcher_task = patcher_plugin.CustomTask()

        # test target file
        self.target_file = path_utils.concat_path(self.test_dir, "target_file.txt")

        # test target folder
        self.target_folder = path_utils.concat_path(self.test_dir, "test_folder")
        os.mkdir(self.target_folder)

        # nonexistent path
        self.nonexistent_path = path_utils.concat_path(self.test_dir, "nonexistent_path")

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testPatcherPluginReadParams1(self):

        local_params = {}
        self.patcher_task.params = local_params

        v, r = self.patcher_task._read_params()
        self.assertFalse(v)

    def testPatcherPluginReadParams2(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        self.patcher_task.params = local_params

        v, r = self.patcher_task._read_params()
        self.assertFalse(v)

    def testPatcherPluginReadParams3(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["target_index"] = "dummy_value2"
        self.patcher_task.params = local_params

        v, r = self.patcher_task._read_params()
        self.assertFalse(v)

    def testPatcherPluginReadParams4(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["target_index"] = "dummy_value2"
        local_params["target_len"] = "dummy_value3"
        self.patcher_task.params = local_params

        v, r = self.patcher_task._read_params()
        self.assertFalse(v)

    def testPatcherPluginReadParams5(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["target_index"] = "dummy_value2"
        local_params["target_len"] = "dummy_value3"
        local_params["source"] = "dummy_value4"
        self.patcher_task.params = local_params

        v, r = self.patcher_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4") )

    def testPatcherPluginRunTask1(self):

        local_params = {}
        local_params["target_path"] = self.nonexistent_path
        local_params["target_index"] = "0"
        local_params["target_len"] = "1"
        local_params["source"] = "2"
        self.patcher_task.params = local_params

        create_and_write_file.create_file_contents(self.target_file, "1")

        v, r = self.patcher_task.run_task(print, "exe_name")
        self.assertFalse(v)

    def testPatcherPluginRunTask2(self):

        local_params = {}
        local_params["target_path"] = self.target_folder
        local_params["target_index"] = "0"
        local_params["target_len"] = "1"
        local_params["source"] = "2"
        self.patcher_task.params = local_params

        create_and_write_file.create_file_contents(self.target_file, "1")

        v, r = self.patcher_task.run_task(print, "exe_name")
        self.assertFalse(v)

    def testPatcherPluginRunTask3(self):

        local_params = {}
        local_params["target_path"] = self.target_file
        local_params["target_index"] = "0"
        local_params["target_len"] = "2"
        local_params["source"] = "2"
        self.patcher_task.params = local_params

        create_and_write_file.create_file_contents(self.target_file, "1")

        v, r = self.patcher_task.run_task(print, "exe_name")
        self.assertFalse(v)

    def testPatcherPluginRunTask4(self):

        local_params = {}
        local_params["target_path"] = self.target_file
        local_params["target_index"] = "1"
        local_params["target_len"] = "1"
        local_params["source"] = "2"
        self.patcher_task.params = local_params

        create_and_write_file.create_file_contents(self.target_file, "1")

        v, r = self.patcher_task.run_task(print, "exe_name")
        self.assertFalse(v)

    def testPatcherPluginRunTask5(self):

        local_params = {}
        local_params["target_path"] = self.target_file
        local_params["target_index"] = "0"
        local_params["target_len"] = "0"
        local_params["source"] = "2"
        self.patcher_task.params = local_params

        create_and_write_file.create_file_contents(self.target_file, "1")

        v, r = self.patcher_task.run_task(print, "exe_name")
        self.assertFalse(v)

    def testPatcherPluginRunTask6(self):

        local_params = {}
        local_params["target_path"] = self.target_file
        local_params["target_index"] = "0"
        local_params["target_len"] = "1"
        local_params["source"] = "2"
        self.patcher_task.params = local_params

        create_and_write_file.create_file_contents(self.target_file, "1")

        v, r = self.patcher_task.run_task(print, "exe_name")
        self.assertTrue(v)

        self.assertTrue(is_file_contents(self.target_file, "2"))

    def testPatcherPluginRunTask7(self):

        local_params = {}
        local_params["target_path"] = self.target_file
        local_params["target_index"] = "1"
        local_params["target_len"] = "1"
        local_params["source"] = ""
        self.patcher_task.params = local_params

        create_and_write_file.create_file_contents(self.target_file, "abc")

        v, r = self.patcher_task.run_task(print, "exe_name")
        self.assertTrue(v)

        self.assertTrue(is_file_contents(self.target_file, "ac"))

if __name__ == "__main__":
    unittest.main()
