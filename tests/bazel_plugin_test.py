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

import bazel_plugin

class BazelPluginTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("bazel_plugin_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # the test task
        self.bazel_task = bazel_plugin.CustomTask()

        # existent path 1
        self.existent_path1 = path_utils.concat_path(self.test_dir, "existent_path1")
        os.mkdir(self.existent_path1)

        # nonexistent path 1
        self.nonexistent_path1 = path_utils.concat_path(self.test_dir, "nonexistent_path1")

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testBazelPluginReadParams1(self):

        local_params = {}
        self.bazel_task.params = local_params

        v, r = self.bazel_task._read_params()
        self.assertFalse(v)

    def testBazelPluginReadParams2(self):

        local_params = {}
        local_params["exec_path"] = self.existent_path1
        self.bazel_task.params = local_params

        v, r = self.bazel_task._read_params()
        self.assertFalse(v)

    def testBazelPluginReadParams3(self):

        local_params = {}
        local_params["exec_path"] = self.nonexistent_path1
        local_params["operation"] = "dummy_value1"
        self.bazel_task.params = local_params

        v, r = self.bazel_task._read_params()
        self.assertFalse(v)

    def testBazelPluginReadParams4(self):

        local_params = {}
        local_params["exec_path"] = self.existent_path1
        local_params["operation"] = "dummy_value1"
        self.bazel_task.params = local_params

        v, r = self.bazel_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, (self.existent_path1, "dummy_value1", None, None, None, False) )

    def testBazelPluginReadParams5(self):

        local_params = {}
        local_params["exec_path"] = self.existent_path1
        local_params["operation"] = "dummy_value1"
        local_params["target"] = "dummy_value2"
        self.bazel_task.params = local_params

        v, r = self.bazel_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, (self.existent_path1, "dummy_value1", "dummy_value2", None, None, False) )

    def testBazelPluginReadParams6(self):

        local_params = {}
        local_params["exec_path"] = self.existent_path1
        local_params["operation"] = "dummy_value1"
        local_params["target"] = "dummy_value2"
        local_params["save_output"] = "dummy_value3"
        self.bazel_task.params = local_params

        v, r = self.bazel_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, (self.existent_path1, "dummy_value1", "dummy_value2", "dummy_value3", None, False) )

    def testBazelPluginReadParams7(self):

        local_params = {}
        local_params["exec_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        local_params["target"] = "dummy_value3"
        local_params["save_output"] = self.existent_path1
        self.bazel_task.params = local_params

        v, r = self.bazel_task._read_params()
        self.assertFalse(v)

    def testBazelPluginReadParams8(self):

        local_params = {}
        local_params["exec_path"] = self.existent_path1
        local_params["operation"] = "dummy_value1"
        local_params["target"] = "dummy_value2"
        local_params["save_output"] = "dummy_value3"
        local_params["save_error_output"] = "dummy_value4"
        self.bazel_task.params = local_params

        v, r = self.bazel_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, (self.existent_path1, "dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4", False) )

    def testBazelPluginReadParams9(self):

        local_params = {}
        local_params["exec_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        local_params["target"] = "dummy_value3"
        local_params["save_output"] = "dummy_value4"
        local_params["save_error_output"] = self.existent_path1
        self.bazel_task.params = local_params

        v, r = self.bazel_task._read_params()
        self.assertFalse(v)

    def testBazelPluginReadParams10(self):

        local_params = {}
        local_params["exec_path"] = self.existent_path1
        local_params["operation"] = "dummy_value1"
        local_params["target"] = "dummy_value2"
        local_params["save_output"] = "dummy_value3"
        local_params["save_error_output"] = "dummy_value4"
        local_params["suppress_stderr_warnings"] = "dummy_value5"
        self.bazel_task.params = local_params

        v, r = self.bazel_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, (self.existent_path1, "dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4", True) )

    def testBazelPluginRunTask1(self):

        local_params = {}
        local_params["exec_path"] = self.existent_path1
        local_params["operation"] = "invalid-operation"
        self.bazel_task.params = local_params

        with mock.patch("bazel_plugin.CustomTask.task_build", return_value=(True, None)) as dummy:
            v, r = self.bazel_task.run_task(print, "exe_name")
            self.assertFalse(v)
            dummy.assert_not_called()

    def testBazelPluginRunTask2(self):

        local_params = {}
        local_params["exec_path"] = self.existent_path1
        local_params["operation"] = "build"
        self.bazel_task.params = local_params

        with mock.patch("bazel_plugin.CustomTask.task_build", return_value=(True, None)) as dummy:
            v, r = self.bazel_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(print, self.existent_path1, None, None, None, False)

    def testBazelPluginRunTask3(self):

        local_params = {}
        local_params["exec_path"] = self.existent_path1
        local_params["operation"] = "fetch"
        self.bazel_task.params = local_params

        with mock.patch("bazel_plugin.CustomTask.task_fetch", return_value=(True, None)) as dummy:
            v, r = self.bazel_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(print, self.existent_path1, None, None, None, False)

    def testBazelPluginRunTask4(self):

        local_params = {}
        local_params["exec_path"] = self.existent_path1
        local_params["operation"] = "clean"
        self.bazel_task.params = local_params

        with mock.patch("bazel_plugin.CustomTask.task_clean", return_value=(True, None)) as dummy:
            v, r = self.bazel_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(print, self.existent_path1, None, None, None, False)

    def testBazelPluginRunTask5(self):

        local_params = {}
        local_params["exec_path"] = self.existent_path1
        local_params["operation"] = "test"
        self.bazel_task.params = local_params

        with mock.patch("bazel_plugin.CustomTask.task_test", return_value=(True, None)) as dummy:
            v, r = self.bazel_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(print, self.existent_path1, None, None, None, False)

    def testBazelPluginTaskBuild1(self):

        with mock.patch("bazel_wrapper.build", return_value=(False, "dummy-error")) as dummy1:
            with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value=None) as dummy2:
                v, r = self.bazel_task.task_build(print, self.existent_path1, None, None, None, False)
                self.assertFalse(v)
                dummy1.assert_called_with(self.existent_path1, None)
                dummy2.assert_not_called()

    def testBazelPluginTaskBuild2(self):

        with mock.patch("bazel_wrapper.build", return_value=(True, (True, "", ""))) as dummy1:
            with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value=None) as dummy2:
                v, r = self.bazel_task.task_build(print, self.existent_path1, None, None, None, False)
                self.assertTrue(v)
                dummy1.assert_called_with(self.existent_path1, None)
                out_list = [("bazel_plugin_stdout", "", "Bazel's stdout"), ("bazel_plugin_stderr", "", "Bazel's stderr")]
                dummy2.assert_called_with(True, print, out_list)

    def testBazelPluginTaskBuild3(self):

        with mock.patch("bazel_wrapper.build", return_value=(True, (True, "", ""))) as dummy1:
            with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value=None) as dummy2:
                v, r = self.bazel_task.task_build(print, self.existent_path1, "dummy_value1", None, None, False)
                self.assertTrue(v)
                dummy1.assert_called_with(self.existent_path1, "dummy_value1")
                out_list = [("bazel_plugin_stdout", "", "Bazel's stdout"), ("bazel_plugin_stderr", "", "Bazel's stderr")]
                dummy2.assert_called_with(True, print, out_list)

if __name__ == '__main__':
    unittest.main()
