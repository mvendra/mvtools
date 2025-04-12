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

import tree_plugin

class TreePluginTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("tree_plugin_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # the test task
        self.tree_task = tree_plugin.CustomTask()

        # source path
        self.source_path = "source_path"
        self.source_path_full = path_utils.concat_path(self.test_dir, self.source_path)
        os.mkdir(self.source_path_full)

        # target path
        self.target_path = "target_path"
        self.target_path_full = path_utils.concat_path(self.test_dir, self.target_path)

        # nonexistent path
        self.nonexistent_path = path_utils.concat_path(self.test_dir, "nonexistent_path")

        # file1
        self.file1 = "file1.txt"
        self.file1_full = path_utils.concat_path(self.test_dir, self.source_path, self.file1)
        create_and_write_file.create_file_contents(self.file1_full, "test contents")

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testTreePluginReadParams1(self):

        local_params = {}
        local_params["target_path"] = self.target_path_full
        self.tree_task.params = local_params

        v, r = self.tree_task._read_params()
        self.assertFalse(v)

    def testTreePluginReadParams2(self):

        local_params = {}
        local_params["source_path"] = self.source_path_full
        self.tree_task.params = local_params

        v, r = self.tree_task._read_params()
        self.assertFalse(v)

    def testTreePluginReadParams3(self):

        local_params = {}
        local_params["source_path"] = self.nonexistent_path
        local_params["target_path"] = self.target_path_full
        self.tree_task.params = local_params

        v, r = self.tree_task._read_params()
        self.assertFalse(v)

    def testTreePluginReadParams4(self):

        local_params = {}
        local_params["source_path"] = self.source_path_full
        os.mkdir(self.target_path_full)
        local_params["target_path"] = self.target_path_full
        self.tree_task.params = local_params

        v, r = self.tree_task._read_params()
        self.assertFalse(v)

    def testTreePluginReadParams5(self):

        local_params = {}
        local_params["source_path"] = self.source_path_full
        local_params["target_path"] = self.target_path_full
        self.tree_task.params = local_params

        v, r = self.tree_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, (self.source_path_full, self.target_path_full))

    def testTreePluginRunTask1(self):

        local_params = {}
        local_params["source_path"] = self.source_path_full
        local_params["target_path"] = self.target_path_full
        self.tree_task.params = local_params

        with mock.patch("tree_wrapper.make_tree", return_value=(True, "mocked contents")) as dummy:
            v, r = self.tree_task.run_task(print, "exe_name")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(self.source_path_full)

        self.assertTrue(os.path.exists(self.target_path_full))

        contents = ""
        with open(self.target_path_full, "r") as f:
            contents = f.read()

        self.assertEqual(contents, "mocked contents")

if __name__ == '__main__':
    unittest.main()
