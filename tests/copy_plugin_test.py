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

import copy_plugin

class CopyPluginTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("copy_plugin_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # the test task
        self.copy_task = copy_plugin.CustomTask()

        # existent path 1
        self.existent_path1 = path_utils.concat_path(self.test_dir, "existent_path1")
        os.mkdir(self.existent_path1)

        # existent path 2
        self.existent_path2 = path_utils.concat_path(self.test_dir, "existent_path2")
        os.mkdir(self.existent_path2)

        # existent path 3
        self.existent_path3 = path_utils.concat_path(self.test_dir, "existent_path3")
        os.mkdir(self.existent_path3)

        # nonexistent path
        self.nonexistent_path = path_utils.concat_path(self.test_dir, "nonexistent_path1")

        # existent file 1
        self.existent_file1 = path_utils.concat_path(self.test_dir, "existent_file1.txt")
        create_and_write_file.create_file_contents(self.existent_file1, "test contents")

        # nonexistent file 1
        self.nonexistent_file = path_utils.concat_path(self.test_dir, "nonexistent_file1.txt")

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testCopyPluginReadParams1(self):

        local_params = {}
        self.copy_task.params = local_params

        v, r = self.copy_task._read_params()
        self.assertFalse(v)

    def testCopyPluginReadParams2(self):

        local_params = {}
        local_params["source_path"] = "dummy_value1"
        self.copy_task.params = local_params

        v, r = self.copy_task._read_params()
        self.assertFalse(v)

    def testCopyPluginReadParams3(self):

        local_params = {}
        local_params["source_path"] = "dummy_value1"
        local_params["target_path"] = "dummy_value2"
        self.copy_task.params = local_params

        v, r = self.copy_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, (["dummy_value1"], "dummy_value2", None) )

    def testCopyPluginReadParams4(self):

        local_params = {}
        local_params["source_path"] = "dummy_value1"
        local_params["target_path"] = "dummy_value2"
        local_params["rename_to"] = "dummy_value3"
        self.copy_task.params = local_params

        v, r = self.copy_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, (["dummy_value1"], "dummy_value2", "dummy_value3") )

    def testCopyPluginReadParams5(self):

        local_params = {}
        local_params["source_path"] = ["dummy_value1", "dummy_value2"]
        local_params["target_path"] = "dummy_value3"
        local_params["rename_to"] = "dummy_value4"
        self.copy_task.params = local_params

        v, r = self.copy_task._read_params()
        self.assertFalse(v)
        self.assertNotEqual( r, (["dummy_value1", "dummy_value2"], "dummy_value3", "dummy_value4") )

    def testCopyPluginRunTask1(self):

        local_params = {}
        local_params["source_path"] = self.nonexistent_path
        local_params["target_path"] = self.existent_path2
        self.copy_task.params = local_params

        with mock.patch("path_utils.copy_to", return_value=(True, None)) as dummy:
            v, r = self.copy_task.run_task(print, "exe_name")
            self.assertFalse(v)

    def testCopyPluginRunTask2(self):

        local_params = {}
        local_params["source_path"] = self.existent_path1
        local_params["target_path"] = self.nonexistent_path
        self.copy_task.params = local_params

        with mock.patch("path_utils.copy_to", return_value=(True, None)) as dummy:
            v, r = self.copy_task.run_task(print, "exe_name")
            self.assertFalse(v)

    def testCopyPluginRunTask3(self):

        local_params = {}
        local_params["source_path"] = self.existent_path1
        local_params["target_path"] = self.existent_path2
        local_params["rename_to"] = "renamed.txt"
        self.copy_task.params = local_params

        final_path_created = path_utils.concat_path(self.existent_path2, "renamed.txt")
        self.assertFalse(os.path.exists(final_path_created))
        create_and_write_file.create_file_contents(final_path_created, "test contents")
        self.assertTrue(os.path.exists(final_path_created))

        with mock.patch("path_utils.copy_to_and_rename", return_value=(True, None)) as dummy:
            v, r = self.copy_task.run_task(print, "exe_name")
            self.assertFalse(v)

    def testCopyPluginRunTask4(self):

        local_params = {}
        local_params["source_path"] = self.existent_path1
        local_params["target_path"] = self.existent_path2
        self.copy_task.params = local_params

        with mock.patch("path_utils.copy_to", return_value=(True, None)) as dummy:
            v, r = self.copy_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(self.existent_path1, self.existent_path2)

    def testCopyPluginRunTask5(self):

        local_params = {}
        local_params["source_path"] = self.existent_path1
        local_params["target_path"] = self.existent_path2
        local_params["rename_to"] = "renamed.txt"
        self.copy_task.params = local_params

        with mock.patch("path_utils.copy_to_and_rename", return_value=(True, None)) as dummy:
            v, r = self.copy_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(self.existent_path1, self.existent_path2, "renamed.txt")

    def testCopyPluginRunTask6(self):

        local_params = {}
        local_params["source_path"] = [self.existent_path1, self.existent_path2]
        local_params["target_path"] = self.existent_path3
        self.copy_task.params = local_params

        with mock.patch("path_utils.copy_to", return_value=(True, None)) as dummy:
            v, r = self.copy_task.run_task(print, "exe_name")
            self.assertTrue(v)
            self.assertEqual( dummy.mock_calls, [ mock.call(self.existent_path1, self.existent_path3), mock.call(self.existent_path2, self.existent_path3) ] )

    def testCopyPluginRunTask7(self):

        local_params = {}
        local_params["source_path"] = [self.existent_path1, self.existent_path2]
        local_params["target_path"] = self.existent_path3
        local_params["rename_to"] = "renamed.txt"
        self.copy_task.params = local_params

        with mock.patch("path_utils.copy_to", return_value=(True, None)) as dummy:
            v, r = self.copy_task.run_task(print, "exe_name")
            self.assertFalse(v)
            self.assertNotEqual( dummy.mock_calls, [ mock.call(self.existent_path1, self.existent_path3), mock.call(self.existent_path2, self.existent_path3) ] )

    def testCopyPluginRunTask8(self):

        local_params = {}
        local_params["source_path"] = [self.existent_path1, self.nonexistent_path]
        local_params["target_path"] = self.existent_path3
        self.copy_task.params = local_params

        with mock.patch("path_utils.copy_to", return_value=(True, None)) as dummy:
            v, r = self.copy_task.run_task(print, "exe_name")
            self.assertFalse(v)
            self.assertNotEqual( dummy.mock_calls, [ mock.call(self.existent_path1, self.existent_path3), mock.call(self.nonexistent_path, self.existent_path3) ] )

if __name__ == '__main__':
    unittest.main()
