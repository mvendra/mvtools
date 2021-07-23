#!/usr/bin/env python3

import sys
import os
import shutil
import unittest
from unittest import mock
from unittest.mock import patch

import mvtools_test_fixture
import create_and_write_file
import path_utils

import rm_plugin

class RmPluginTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("rm_plugin_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # the test task
        self.rm_task = rm_plugin.CustomTask()

        # existent path 1
        self.existent_path1 = path_utils.concat_path(self.test_dir, "existent_path1")
        os.mkdir(self.existent_path1)

        # nonexistent path 1
        self.nonexistent_path1 = path_utils.concat_path(self.test_dir, "nonexistent_path1")

        # existent file 1
        self.existent_file1 = path_utils.concat_path(self.test_dir, "existent_file1.txt")
        create_and_write_file.create_file_contents(self.existent_file1, "dummy txt file")

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testRmPluginReadParams1(self):

        local_params = {}
        self.rm_task.params = local_params

        v, r = self.rm_task._read_params()
        self.assertFalse(v)

    def testRmPluginReadParams2(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        self.rm_task.params = local_params

        v, r = self.rm_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", False) )

    def testRmPluginReadParams3(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["ignore_non_pre_existence"] = "dummy_value2"
        self.rm_task.params = local_params

        v, r = self.rm_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", True) )

    def testRmPluginRunTask1(self):

        local_params = {}
        local_params["target_path"] = self.existent_file1
        self.rm_task.params = local_params

        self.assertTrue(os.path.exists(self.existent_file1))

        v, r = self.rm_task.run_task(print, "exe_name")
        self.assertTrue(v)

        self.assertFalse(os.path.exists(self.existent_file1))

    def testRmPluginRunTask2(self):

        local_params = {}
        local_params["target_path"] = self.nonexistent_path1
        self.rm_task.params = local_params

        self.assertFalse(os.path.exists(self.nonexistent_path1))

        v, r = self.rm_task.run_task(print, "exe_name")
        self.assertFalse(v)

    def testRmPluginRunTask3(self):

        local_params = {}
        local_params["target_path"] = self.existent_path1
        self.rm_task.params = local_params

        self.assertTrue(os.path.exists(self.existent_path1))

        v, r = self.rm_task.run_task(print, "exe_name")
        self.assertFalse(v)

    def testRmPluginRunTask4(self):

        local_params = {}
        local_params["target_path"] = self.nonexistent_path1
        local_params["ignore_non_pre_existence"] = "dummy_value1"
        self.rm_task.params = local_params

        self.assertFalse(os.path.exists(self.nonexistent_path1))

        v, r = self.rm_task.run_task(print, "exe_name")
        self.assertTrue(v)
        self.assertTrue(r is not None)

if __name__ == '__main__':
    unittest.main()
