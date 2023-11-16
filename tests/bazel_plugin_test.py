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

def FileHasContents(filename, contents):
    if not os.path.exists(filename):
        return False
    local_contents = ""
    with open(filename, "r") as f:
        local_contents = f.read()
    if local_contents == contents:
        return True
    return False

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

        # dumped_stdout_file
        self.dumped_stdout_file = path_utils.concat_path(self.test_dir, "dumped_stdout_file")

        # dumped_stderr_file
        self.dumped_stderr_file = path_utils.concat_path(self.test_dir, "dumped_stderr_file")

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
        self.assertEqual( r, (self.existent_path1, "dummy_value1", None, None, None, False, False, [], [], None, None, False) )

    def testBazelPluginReadParams5(self):

        local_params = {}
        local_params["exec_path"] = self.existent_path1
        local_params["operation"] = "dummy_value1"
        local_params["jobs"] = "dummy_value2"
        self.bazel_task.params = local_params

        v, r = self.bazel_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, (self.existent_path1, "dummy_value1", "dummy_value2", None, None, False, False, [], [], None, None, False) )

    def testBazelPluginReadParams6(self):

        local_params = {}
        local_params["exec_path"] = self.existent_path1
        local_params["operation"] = "dummy_value1"
        local_params["jobs"] = ["dummy_value2", "dummy_value3"]
        self.bazel_task.params = local_params

        v, r = self.bazel_task._read_params()
        self.assertFalse(v)

    def testBazelPluginReadParams7(self):

        local_params = {}
        local_params["exec_path"] = self.existent_path1
        local_params["operation"] = "dummy_value1"
        local_params["jobs"] = "dummy_value2"
        local_params["config"] = "dummy_value3"
        self.bazel_task.params = local_params

        v, r = self.bazel_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, (self.existent_path1, "dummy_value1", "dummy_value2", "dummy_value3", None, False, False, [], [], None, None, False) )

    def testBazelPluginReadParams8(self):

        local_params = {}
        local_params["exec_path"] = self.existent_path1
        local_params["operation"] = "dummy_value1"
        local_params["jobs"] = "dummy_value2"
        local_params["config"] = ["dummy_value3", "dummy_value4"]
        self.bazel_task.params = local_params

        v, r = self.bazel_task._read_params()
        self.assertFalse(v)

    def testBazelPluginReadParams9(self):

        local_params = {}
        local_params["exec_path"] = self.existent_path1
        local_params["operation"] = "dummy_value1"
        local_params["jobs"] = "dummy_value2"
        local_params["config"] = "dummy_value3"
        local_params["target"] = "dummy_value4"
        self.bazel_task.params = local_params

        v, r = self.bazel_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, (self.existent_path1, "dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4", False, False, [], [], None, None, False) )

    def testBazelPluginReadParams10(self):

        local_params = {}
        local_params["exec_path"] = self.existent_path1
        local_params["operation"] = "dummy_value1"
        local_params["jobs"] = "dummy_value2"
        local_params["config"] = "dummy_value3"
        local_params["target"] = "dummy_value4"
        local_params["expunge"] = "dummy_value5"
        self.bazel_task.params = local_params

        v, r = self.bazel_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, (self.existent_path1, "dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4", True, False, [], [], None, None, False) )

    def testBazelPluginReadParams11(self):

        local_params = {}
        local_params["exec_path"] = self.existent_path1
        local_params["operation"] = "dummy_value1"
        local_params["jobs"] = "dummy_value2"
        local_params["config"] = "dummy_value3"
        local_params["target"] = "dummy_value4"
        local_params["expunge"] = "dummy_value5"
        local_params["fail_test_fail_task"] = "dummy_value6"
        self.bazel_task.params = local_params

        v, r = self.bazel_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, (self.existent_path1, "dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4", True, True, [], [], None, None, False) )

    def testBazelPluginReadParams12(self):

        local_params = {}
        local_params["exec_path"] = self.existent_path1
        local_params["operation"] = "dummy_value1"
        local_params["jobs"] = "dummy_value2"
        local_params["config"] = "dummy_value3"
        local_params["target"] = "dummy_value4"
        local_params["expunge"] = "dummy_value5"
        local_params["fail_test_fail_task"] = "dummy_value6"
        local_params["opt"] = "dummy_value7"
        self.bazel_task.params = local_params

        v, r = self.bazel_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, (self.existent_path1, "dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4", True, True, ["dummy_value7"], [], None, None, False) )

    def testBazelPluginReadParams13(self):

        local_params = {}
        local_params["exec_path"] = self.existent_path1
        local_params["operation"] = "dummy_value1"
        local_params["jobs"] = "dummy_value2"
        local_params["config"] = "dummy_value3"
        local_params["target"] = "dummy_value4"
        local_params["expunge"] = "dummy_value5"
        local_params["fail_test_fail_task"] = "dummy_value6"
        local_params["opt"] = ["dummy_value7", "dummy_value8"]
        self.bazel_task.params = local_params

        v, r = self.bazel_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, (self.existent_path1, "dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4", True, True, ["dummy_value7", "dummy_value8"], [], None, None, False) )

    def testBazelPluginReadParams14(self):

        local_params = {}
        local_params["exec_path"] = self.existent_path1
        local_params["operation"] = "dummy_value1"
        local_params["jobs"] = "dummy_value2"
        local_params["config"] = "dummy_value3"
        local_params["target"] = "dummy_value4"
        local_params["expunge"] = "dummy_value5"
        local_params["fail_test_fail_task"] = "dummy_value6"
        local_params["opt"] = "dummy_value7"
        local_params["save_output"] = "dummy_value8"
        self.bazel_task.params = local_params

        v, r = self.bazel_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, (self.existent_path1, "dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4", True, True, ["dummy_value7"], [], "dummy_value8", None, False) )

    def testBazelPluginReadParams15(self):

        local_params = {}
        local_params["exec_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        local_params["jobs"] = "dummy_value3"
        local_params["config"] = "dummy_value4"
        local_params["target"] = "dummy_value5"
        local_params["expunge"] = "dummy_value6"
        local_params["fail_test_fail_task"] = "dummy_value7"
        local_params["opt"] = "dummy_value8"
        local_params["save_output"] = self.existent_path1
        self.bazel_task.params = local_params

        v, r = self.bazel_task._read_params()
        self.assertFalse(v)

    def testBazelPluginReadParams16(self):

        local_params = {}
        local_params["exec_path"] = self.existent_path1
        local_params["operation"] = "dummy_value1"
        local_params["jobs"] = "dummy_value2"
        local_params["config"] = "dummy_value3"
        local_params["target"] = "dummy_value4"
        local_params["expunge"] = "dummy_value5"
        local_params["fail_test_fail_task"] = "dummy_value6"
        local_params["opt"] = "dummy_value7"
        local_params["save_output"] = "dummy_value8"
        local_params["save_error_output"] = "dummy_value9"
        self.bazel_task.params = local_params

        v, r = self.bazel_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, (self.existent_path1, "dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4", True, True, ["dummy_value7"], [], "dummy_value8", "dummy_value9", False) )

    def testBazelPluginReadParams17(self):

        local_params = {}
        local_params["exec_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        local_params["jobs"] = "dummy_value3"
        local_params["config"] = "dummy_value4"
        local_params["target"] = "dummy_value5"
        local_params["expunge"] = "dummy_value6"
        local_params["fail_test_fail_task"] = "dummy_value7"
        local_params["opt"] = "dummy_value8"
        local_params["save_output"] = "dummy_value9"
        local_params["save_error_output"] = self.existent_path1
        self.bazel_task.params = local_params

        v, r = self.bazel_task._read_params()
        self.assertFalse(v)

    def testBazelPluginReadParams18(self):

        local_params = {}
        local_params["exec_path"] = self.existent_path1
        local_params["operation"] = "dummy_value1"
        local_params["jobs"] = "dummy_value2"
        local_params["config"] = "dummy_value3"
        local_params["target"] = "dummy_value4"
        local_params["expunge"] = "dummy_value5"
        local_params["fail_test_fail_task"] = "dummy_value6"
        local_params["opt"] = "dummy_value7"
        local_params["save_output"] = "dummy_value8"
        local_params["save_error_output"] = "dummy_value9"
        local_params["suppress_stderr_warnings"] = "dummy_value10"
        self.bazel_task.params = local_params

        v, r = self.bazel_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, (self.existent_path1, "dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4", True, True, ["dummy_value7"], [], "dummy_value8", "dummy_value9", True) )

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
            dummy.assert_called_with(print, self.existent_path1, None, None, None, [], None, None, False)

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
            dummy.assert_called_with(print, self.existent_path1, False, None, None, False)

    def testBazelPluginRunTask5(self):

        local_params = {}
        local_params["exec_path"] = self.existent_path1
        local_params["operation"] = "test"
        self.bazel_task.params = local_params

        with mock.patch("bazel_plugin.CustomTask.task_test", return_value=(True, None)) as dummy:
            v, r = self.bazel_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(print, self.existent_path1, None, None, None, False, [], None, None, False)

    def testBazelPluginTaskBuild1(self):

        with mock.patch("bazel_wrapper.build", return_value=(False, "dummy-error")) as dummy1:
            with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value=None) as dummy2:
                v, r = self.bazel_task.task_build(print, self.existent_path1, None, None, None, [], None, None, False)
                self.assertFalse(v)
                self.assertEqual(r, "dummy-error")
                dummy1.assert_called_with(self.existent_path1, None, None, None, [])
                dummy2.assert_not_called()

    def testBazelPluginTaskBuild2(self):

        with mock.patch("bazel_wrapper.build", return_value=(True, (True, "", ""))) as dummy1:
            with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value=None) as dummy2:
                v, r = self.bazel_task.task_build(print, self.existent_path1, None, None, None, [], None, None, False)
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy1.assert_called_with(self.existent_path1, None, None, None, [])
                out_list = [("bazel_plugin_stdout", "", "Bazel's stdout"), ("bazel_plugin_stderr", "", "Bazel's stderr")]
                dummy2.assert_called_with(True, print, out_list)

    def testBazelPluginTaskBuild3(self):

        with mock.patch("bazel_wrapper.build", return_value=(True, (True, "", ""))) as dummy1:
            with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value=None) as dummy2:
                v, r = self.bazel_task.task_build(print, self.existent_path1, "64", None, None, [], None, None, False)
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy1.assert_called_with(self.existent_path1, "64", None, None, [])
                out_list = [("bazel_plugin_stdout", "", "Bazel's stdout"), ("bazel_plugin_stderr", "", "Bazel's stderr")]
                dummy2.assert_called_with(True, print, out_list)

    def testBazelPluginTaskBuild4(self):

        with mock.patch("bazel_wrapper.build", return_value=(True, (True, "", ""))) as dummy1:
            with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value=None) as dummy2:
                v, r = self.bazel_task.task_build(print, self.existent_path1, None, "dummy_value1", None, [], None, None, False)
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy1.assert_called_with(self.existent_path1, None, "dummy_value1", None, [])
                out_list = [("bazel_plugin_stdout", "", "Bazel's stdout"), ("bazel_plugin_stderr", "", "Bazel's stderr")]
                dummy2.assert_called_with(True, print, out_list)

    def testBazelPluginTaskBuild5(self):

        with mock.patch("bazel_wrapper.build", return_value=(True, (True, "", ""))) as dummy1:
            with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value=None) as dummy2:
                v, r = self.bazel_task.task_build(print, self.existent_path1, None, None, "dummy_value1", [], None, None, False)
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy1.assert_called_with(self.existent_path1, None, None, "dummy_value1", [])
                out_list = [("bazel_plugin_stdout", "", "Bazel's stdout"), ("bazel_plugin_stderr", "", "Bazel's stderr")]
                dummy2.assert_called_with(True, print, out_list)

    def testBazelPluginTaskBuild6(self):

        with mock.patch("bazel_wrapper.build", return_value=(True, (True, "", ""))) as dummy1:
            with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value=None) as dummy2:
                v, r = self.bazel_task.task_build(print, self.existent_path1, None, None, "dummy_value1", ["dummy_value2"], None, None, False)
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy1.assert_called_with(self.existent_path1, None, None, "dummy_value1", ["dummy_value2"])
                out_list = [("bazel_plugin_stdout", "", "Bazel's stdout"), ("bazel_plugin_stderr", "", "Bazel's stderr")]
                dummy2.assert_called_with(True, print, out_list)

    def testBazelPluginTaskBuild7(self):

        with mock.patch("bazel_wrapper.build", return_value=(True, (True, "test-stdout", ""))) as dummy1:
            with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value=None) as dummy2:
                v, r = self.bazel_task.task_build(print, self.existent_path1, None, None, None, [], self.dumped_stdout_file, None, False)
                self.assertTrue(v)
                self.assertEqual(r, None)
                self.assertTrue(FileHasContents(self.dumped_stdout_file, "test-stdout"))
                dummy1.assert_called_with(self.existent_path1, None, None, None, [])
                out_list = [("bazel_plugin_stdout", "test-stdout", "Bazel's stdout"), ("bazel_plugin_stderr", "", "Bazel's stderr")]
                dummy2.assert_called_with(True, print, out_list)

    def testBazelPluginTaskBuild8(self):

        with mock.patch("bazel_wrapper.build", return_value=(True, (True, "", "test-stderr"))) as dummy1:
            with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value=None) as dummy2:
                v, r = self.bazel_task.task_build(print, self.existent_path1, None, None, None, [], None, self.dumped_stderr_file, False)
                self.assertTrue(v)
                self.assertEqual(r, "test-stderr")
                self.assertTrue(FileHasContents(self.dumped_stderr_file, "test-stderr"))
                dummy1.assert_called_with(self.existent_path1, None, None, None, [])
                out_list = [("bazel_plugin_stdout", "", "Bazel's stdout"), ("bazel_plugin_stderr", "test-stderr", "Bazel's stderr")]
                dummy2.assert_called_with(True, print, out_list)

    def testBazelPluginTaskBuild9(self):

        with mock.patch("bazel_wrapper.build", return_value=(True, (True, "", ""))) as dummy1:
            with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value="somewarning") as dummy2:
                v, r = self.bazel_task.task_build(print, self.existent_path1, None, None, "dummy_value1", [], None, None, False)
                self.assertTrue(v)
                self.assertEqual(r, "somewarning")
                dummy1.assert_called_with(self.existent_path1, None, None, "dummy_value1", [])
                out_list = [("bazel_plugin_stdout", "", "Bazel's stdout"), ("bazel_plugin_stderr", "", "Bazel's stderr")]
                dummy2.assert_called_with(True, print, out_list)

    def testBazelPluginTaskBuild10(self):

        with mock.patch("bazel_wrapper.build", return_value=(True, (True, "", "test-stderr"))) as dummy1:
            with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value=None) as dummy2:
                v, r = self.bazel_task.task_build(print, self.existent_path1, None, None, None, [], None, self.dumped_stderr_file, True)
                self.assertTrue(v)
                self.assertEqual(r, "bazel's stderr has been suppressed")
                self.assertTrue(FileHasContents(self.dumped_stderr_file, "test-stderr"))
                dummy1.assert_called_with(self.existent_path1, None, None, None, [])
                out_list = [("bazel_plugin_stdout", "", "Bazel's stdout"), ("bazel_plugin_stderr", "test-stderr", "Bazel's stderr")]
                dummy2.assert_called_with(True, print, out_list)

    def testBazelPluginTaskFetch1(self):

        with mock.patch("bazel_wrapper.fetch", return_value=(False, "dummy-error")) as dummy1:
            with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value=None) as dummy2:
                v, r = self.bazel_task.task_fetch(print, self.existent_path1, None, None, None, False)
                self.assertFalse(v)
                self.assertEqual(r, "dummy-error")
                dummy1.assert_called_with(self.existent_path1, None)
                dummy2.assert_not_called()

    def testBazelPluginTaskFetch2(self):

        with mock.patch("bazel_wrapper.fetch", return_value=(True, (True, "", ""))) as dummy1:
            with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value=None) as dummy2:
                v, r = self.bazel_task.task_fetch(print, self.existent_path1, None, None, None, False)
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy1.assert_called_with(self.existent_path1, None)
                out_list = [("bazel_plugin_stdout", "", "Bazel's stdout"), ("bazel_plugin_stderr", "", "Bazel's stderr")]
                dummy2.assert_called_with(True, print, out_list)

    def testBazelPluginTaskFetch3(self):

        with mock.patch("bazel_wrapper.fetch", return_value=(True, (True, "", ""))) as dummy1:
            with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value=None) as dummy2:
                v, r = self.bazel_task.task_fetch(print, self.existent_path1, "dummy_value1", None, None, False)
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy1.assert_called_with(self.existent_path1, "dummy_value1")
                out_list = [("bazel_plugin_stdout", "", "Bazel's stdout"), ("bazel_plugin_stderr", "", "Bazel's stderr")]
                dummy2.assert_called_with(True, print, out_list)

    def testBazelPluginTaskFetch4(self):

        with mock.patch("bazel_wrapper.fetch", return_value=(True, (True, "test-stdout", ""))) as dummy1:
            with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value=None) as dummy2:
                v, r = self.bazel_task.task_fetch(print, self.existent_path1, None, self.dumped_stdout_file, None, False)
                self.assertTrue(v)
                self.assertEqual(r, None)
                self.assertTrue(FileHasContents(self.dumped_stdout_file, "test-stdout"))
                dummy1.assert_called_with(self.existent_path1, None)
                out_list = [("bazel_plugin_stdout", "test-stdout", "Bazel's stdout"), ("bazel_plugin_stderr", "", "Bazel's stderr")]
                dummy2.assert_called_with(True, print, out_list)

    def testBazelPluginTaskFetch5(self):

        with mock.patch("bazel_wrapper.fetch", return_value=(True, (True, "", "test-stderr"))) as dummy1:
            with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value=None) as dummy2:
                v, r = self.bazel_task.task_fetch(print, self.existent_path1, None, None, self.dumped_stderr_file, False)
                self.assertTrue(v)
                self.assertEqual(r, "test-stderr")
                self.assertTrue(FileHasContents(self.dumped_stderr_file, "test-stderr"))
                dummy1.assert_called_with(self.existent_path1, None)
                out_list = [("bazel_plugin_stdout", "", "Bazel's stdout"), ("bazel_plugin_stderr", "test-stderr", "Bazel's stderr")]
                dummy2.assert_called_with(True, print, out_list)

    def testBazelPluginTaskFetch6(self):

        with mock.patch("bazel_wrapper.fetch", return_value=(True, (True, "", ""))) as dummy1:
            with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value="somewarning") as dummy2:
                v, r = self.bazel_task.task_fetch(print, self.existent_path1, "dummy_value1", None, None, False)
                self.assertTrue(v)
                self.assertEqual(r, "somewarning")
                dummy1.assert_called_with(self.existent_path1, "dummy_value1")
                out_list = [("bazel_plugin_stdout", "", "Bazel's stdout"), ("bazel_plugin_stderr", "", "Bazel's stderr")]
                dummy2.assert_called_with(True, print, out_list)

    def testBazelPluginTaskFetch7(self):

        with mock.patch("bazel_wrapper.fetch", return_value=(True, (True, "", "test-stderr"))) as dummy1:
            with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value=None) as dummy2:
                v, r = self.bazel_task.task_fetch(print, self.existent_path1, None, None, self.dumped_stderr_file, True)
                self.assertTrue(v)
                self.assertEqual(r, "bazel's stderr has been suppressed")
                self.assertTrue(FileHasContents(self.dumped_stderr_file, "test-stderr"))
                dummy1.assert_called_with(self.existent_path1, None)
                out_list = [("bazel_plugin_stdout", "", "Bazel's stdout"), ("bazel_plugin_stderr", "test-stderr", "Bazel's stderr")]
                dummy2.assert_called_with(True, print, out_list)

    def testBazelPluginTaskClean1(self):

        with mock.patch("bazel_wrapper.clean", return_value=(False, "dummy-error")) as dummy1:
            with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value=None) as dummy2:
                v, r = self.bazel_task.task_clean(print, self.existent_path1, False, None, None, False)
                self.assertFalse(v)
                self.assertEqual(r, "dummy-error")
                dummy1.assert_called_with(self.existent_path1, False)
                dummy2.assert_not_called()

    def testBazelPluginTaskClean2(self):

        with mock.patch("bazel_wrapper.clean", return_value=(True, (True, "", ""))) as dummy1:
            with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value=None) as dummy2:
                v, r = self.bazel_task.task_clean(print, self.existent_path1, False, None, None, False)
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy1.assert_called_with(self.existent_path1, False)
                out_list = [("bazel_plugin_stdout", "", "Bazel's stdout"), ("bazel_plugin_stderr", "", "Bazel's stderr")]
                dummy2.assert_called_with(True, print, out_list)

    def testBazelPluginTaskClean3(self):

        with mock.patch("bazel_wrapper.clean", return_value=(True, (True, "", ""))) as dummy1:
            with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value=None) as dummy2:
                v, r = self.bazel_task.task_clean(print, self.existent_path1, True, None, None, False)
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy1.assert_called_with(self.existent_path1, True)
                out_list = [("bazel_plugin_stdout", "", "Bazel's stdout"), ("bazel_plugin_stderr", "", "Bazel's stderr")]
                dummy2.assert_called_with(True, print, out_list)

    def testBazelPluginTaskClean4(self):

        with mock.patch("bazel_wrapper.clean", return_value=(True, (True, "test-stdout", ""))) as dummy1:
            with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value=None) as dummy2:
                v, r = self.bazel_task.task_clean(print, self.existent_path1, False, self.dumped_stdout_file, None, False)
                self.assertTrue(v)
                self.assertEqual(r, None)
                self.assertTrue(FileHasContents(self.dumped_stdout_file, "test-stdout"))
                dummy1.assert_called_with(self.existent_path1, False)
                out_list = [("bazel_plugin_stdout", "test-stdout", "Bazel's stdout"), ("bazel_plugin_stderr", "", "Bazel's stderr")]
                dummy2.assert_called_with(True, print, out_list)

    def testBazelPluginTaskClean5(self):

        with mock.patch("bazel_wrapper.clean", return_value=(True, (True, "", "test-stderr"))) as dummy1:
            with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value=None) as dummy2:
                v, r = self.bazel_task.task_clean(print, self.existent_path1, False, None, self.dumped_stderr_file, False)
                self.assertTrue(v)
                self.assertEqual(r, "test-stderr")
                self.assertTrue(FileHasContents(self.dumped_stderr_file, "test-stderr"))
                dummy1.assert_called_with(self.existent_path1, False)
                out_list = [("bazel_plugin_stdout", "", "Bazel's stdout"), ("bazel_plugin_stderr", "test-stderr", "Bazel's stderr")]
                dummy2.assert_called_with(True, print, out_list)

    def testBazelPluginTaskClean6(self):

        with mock.patch("bazel_wrapper.clean", return_value=(True, (True, "", ""))) as dummy1:
            with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value="somewarning") as dummy2:
                v, r = self.bazel_task.task_clean(print, self.existent_path1, False, None, None, False)
                self.assertTrue(v)
                self.assertEqual(r, "somewarning")
                dummy1.assert_called_with(self.existent_path1, False)
                out_list = [("bazel_plugin_stdout", "", "Bazel's stdout"), ("bazel_plugin_stderr", "", "Bazel's stderr")]
                dummy2.assert_called_with(True, print, out_list)

    def testBazelPluginTaskClean7(self):

        with mock.patch("bazel_wrapper.clean", return_value=(True, (True, "", "test-stderr"))) as dummy1:
            with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value=None) as dummy2:
                v, r = self.bazel_task.task_clean(print, self.existent_path1, False, None, self.dumped_stderr_file, True)
                self.assertTrue(v)
                self.assertEqual(r, "bazel's stderr has been suppressed")
                self.assertTrue(FileHasContents(self.dumped_stderr_file, "test-stderr"))
                dummy1.assert_called_with(self.existent_path1, False)
                out_list = [("bazel_plugin_stdout", "", "Bazel's stdout"), ("bazel_plugin_stderr", "test-stderr", "Bazel's stderr")]
                dummy2.assert_called_with(True, print, out_list)

    def testBazelPluginTaskTest1(self):

        with mock.patch("bazel_wrapper.test", return_value=(False, "dummy-error")) as dummy1:
            with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value=None) as dummy2:
                v, r = self.bazel_task.task_test(print, self.existent_path1, None, None, None, False, [], None, None, False)
                self.assertFalse(v)
                self.assertEqual(r, "dummy-error")
                dummy1.assert_called_with(self.existent_path1, None, None, None, [])
                dummy2.assert_not_called()

    def testBazelPluginTaskTest2(self):

        with mock.patch("bazel_wrapper.test", return_value=(True, (True, "", ""))) as dummy1:
            with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value=None) as dummy2:
                v, r = self.bazel_task.task_test(print, self.existent_path1, None, None, None, False, [], None, None, False)
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy1.assert_called_with(self.existent_path1, None, None, None, [])
                out_list = [("bazel_plugin_stdout", "", "Bazel's stdout"), ("bazel_plugin_stderr", "", "Bazel's stderr")]
                dummy2.assert_called_with(True, print, out_list)

    def testBazelPluginTaskTest3(self):

        with mock.patch("bazel_wrapper.test", return_value=(True, (True, "", ""))) as dummy1:
            with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value=None) as dummy2:
                v, r = self.bazel_task.task_test(print, self.existent_path1, "64", None, None, False, [], None, None, False)
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy1.assert_called_with(self.existent_path1, "64", None, None, [])
                out_list = [("bazel_plugin_stdout", "", "Bazel's stdout"), ("bazel_plugin_stderr", "", "Bazel's stderr")]
                dummy2.assert_called_with(True, print, out_list)

    def testBazelPluginTaskTest4(self):

        with mock.patch("bazel_wrapper.test", return_value=(True, (True, "", ""))) as dummy1:
            with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value=None) as dummy2:
                v, r = self.bazel_task.task_test(print, self.existent_path1, None, "dummy_value1", None, False, [], None, None, False)
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy1.assert_called_with(self.existent_path1, None, "dummy_value1", None, [])
                out_list = [("bazel_plugin_stdout", "", "Bazel's stdout"), ("bazel_plugin_stderr", "", "Bazel's stderr")]
                dummy2.assert_called_with(True, print, out_list)

    def testBazelPluginTaskTest5(self):

        with mock.patch("bazel_wrapper.test", return_value=(True, (True, "", ""))) as dummy1:
            with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value=None) as dummy2:
                v, r = self.bazel_task.task_test(print, self.existent_path1, None, None, "dummy_value1", False, [], None, None, False)
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy1.assert_called_with(self.existent_path1, None, None, "dummy_value1", [])
                out_list = [("bazel_plugin_stdout", "", "Bazel's stdout"), ("bazel_plugin_stderr", "", "Bazel's stderr")]
                dummy2.assert_called_with(True, print, out_list)

    def testBazelPluginTaskTest6(self):

        with mock.patch("bazel_wrapper.test", return_value=(True, (False, "", ""))) as dummy1:
            with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value=None) as dummy2:
                v, r = self.bazel_task.task_test(print, self.existent_path1, None, None, "dummy_value1", True, [], None, None, False)
                self.assertFalse(v)
                self.assertEqual(r, None)
                dummy1.assert_called_with(self.existent_path1, None, None, "dummy_value1", [])
                out_list = [("bazel_plugin_stdout", "", "Bazel's stdout"), ("bazel_plugin_stderr", "", "Bazel's stderr")]
                dummy2.assert_called_with(False, print, out_list)

    def testBazelPluginTaskTest7(self):

        with mock.patch("bazel_wrapper.test", return_value=(True, (True, "", ""))) as dummy1:
            with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value=None) as dummy2:
                v, r = self.bazel_task.task_test(print, self.existent_path1, None, None, None, False, ["dummy_value1"], None, None, False)
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy1.assert_called_with(self.existent_path1, None, None, None, ["dummy_value1"])
                out_list = [("bazel_plugin_stdout", "", "Bazel's stdout"), ("bazel_plugin_stderr", "", "Bazel's stderr")]
                dummy2.assert_called_with(True, print, out_list)

    def testBazelPluginTaskTest8(self):

        with mock.patch("bazel_wrapper.test", return_value=(True, (True, "test-stdout", ""))) as dummy1:
            with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value=None) as dummy2:
                v, r = self.bazel_task.task_test(print, self.existent_path1, None, None, None, False, [], self.dumped_stdout_file, None, False)
                self.assertTrue(v)
                self.assertEqual(r, None)
                self.assertTrue(FileHasContents(self.dumped_stdout_file, "test-stdout"))
                dummy1.assert_called_with(self.existent_path1, None, None, None, [])
                out_list = [("bazel_plugin_stdout", "test-stdout", "Bazel's stdout"), ("bazel_plugin_stderr", "", "Bazel's stderr")]
                dummy2.assert_called_with(True, print, out_list)

    def testBazelPluginTaskTest9(self):

        with mock.patch("bazel_wrapper.test", return_value=(True, (True, "", "test-stderr"))) as dummy1:
            with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value=None) as dummy2:
                v, r = self.bazel_task.task_test(print, self.existent_path1, None, None, None, False, [], None, self.dumped_stderr_file, False)
                self.assertTrue(v)
                self.assertEqual(r, "test-stderr")
                self.assertTrue(FileHasContents(self.dumped_stderr_file, "test-stderr"))
                dummy1.assert_called_with(self.existent_path1, None, None, None, [])
                out_list = [("bazel_plugin_stdout", "", "Bazel's stdout"), ("bazel_plugin_stderr", "test-stderr", "Bazel's stderr")]
                dummy2.assert_called_with(True, print, out_list)

    def testBazelPluginTaskTest10(self):

        with mock.patch("bazel_wrapper.test", return_value=(True, (True, "", ""))) as dummy1:
            with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value="somewarning") as dummy2:
                v, r = self.bazel_task.task_test(print, self.existent_path1, None, None, "dummy_value1", False, [], None, None, False)
                self.assertTrue(v)
                self.assertEqual(r, "somewarning")
                dummy1.assert_called_with(self.existent_path1, None, None, "dummy_value1", [])
                out_list = [("bazel_plugin_stdout", "", "Bazel's stdout"), ("bazel_plugin_stderr", "", "Bazel's stderr")]
                dummy2.assert_called_with(True, print, out_list)

    def testBazelPluginTaskTest11(self):

        with mock.patch("bazel_wrapper.test", return_value=(True, (True, "", "test-stderr"))) as dummy1:
            with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value=None) as dummy2:
                v, r = self.bazel_task.task_test(print, self.existent_path1, None, None, None, False, [], None, self.dumped_stderr_file, True)
                self.assertTrue(v)
                self.assertEqual(r, "bazel's stderr has been suppressed")
                self.assertTrue(FileHasContents(self.dumped_stderr_file, "test-stderr"))
                dummy1.assert_called_with(self.existent_path1, None, None, None, [])
                out_list = [("bazel_plugin_stdout", "", "Bazel's stdout"), ("bazel_plugin_stderr", "test-stderr", "Bazel's stderr")]
                dummy2.assert_called_with(True, print, out_list)

    def testBazelPluginTaskTest12(self):

        with mock.patch("bazel_wrapper.test", return_value=(True, (False, "", ""))) as dummy1:
            with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value=None) as dummy2:
                v, r = self.bazel_task.task_test(print, self.existent_path1, None, None, "dummy_value1", False, [], None, None, False)
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy1.assert_called_with(self.existent_path1, None, None, "dummy_value1", [])
                out_list = [("bazel_plugin_stdout", "", "Bazel's stdout"), ("bazel_plugin_stderr", "", "Bazel's stderr")]
                dummy2.assert_called_with(False, print, out_list)

if __name__ == '__main__':
    unittest.main()
