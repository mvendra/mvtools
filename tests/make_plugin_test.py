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
import make_wrapper

import make_plugin

class MakePluginTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("make_plugin_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        self.output_backup_storage = path_utils.concat_path(self.test_dir, "output_backup")
        os.mkdir(self.output_backup_storage)

        # the test task
        self.make_task = make_plugin.CustomTask()

        # existent path 1
        self.existent_path1 = path_utils.concat_path(self.test_dir, "existent_path1")
        os.mkdir(self.existent_path1)

        # existent path 2
        self.existent_path2 = path_utils.concat_path(self.test_dir, "existent_path2")
        os.mkdir(self.existent_path2)

        # nonexistent path 1
        self.nonexistent_path1 = path_utils.concat_path(self.test_dir, "nonexistent_path1")

        # nonexistent file 1
        self.nonexistent_file1 = path_utils.concat_path(self.test_dir, "non_pre_existent_file1.txt")

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testMakePluginReadParams1(self):

        local_params = {}
        self.make_task.params = local_params

        v, r = self.make_task._read_params()
        self.assertFalse(v)

    def testMakePluginReadParams2(self):

        local_params = {}
        local_params["work_dir"] = self.existent_path1
        self.make_task.params = local_params

        v, r = self.make_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, (self.existent_path1, None, None, None, False))

    def testMakePluginReadParams3(self):

        local_params = {}
        local_params["work_dir"] = self.nonexistent_path1
        self.make_task.params = local_params

        v, r = self.make_task._read_params()
        self.assertFalse(v)

    def testMakePluginReadParams4(self):

        local_params = {}
        local_params["work_dir"] = self.existent_path1
        local_params["save_output"] = self.existent_path2
        self.make_task.params = local_params

        v, r = self.make_task._read_params()
        self.assertFalse(v)

    def testMakePluginReadParams5(self):

        local_params = {}
        local_params["work_dir"] = self.existent_path1
        local_params["save_error_output"] = self.existent_path2
        self.make_task.params = local_params

        v, r = self.make_task._read_params()
        self.assertFalse(v)

    def testMakePluginReadParams6(self):

        local_params = {}
        local_params["work_dir"] = self.existent_path1
        local_params["target"] = "dummy_value2"
        self.make_task.params = local_params

        v, r = self.make_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, (self.existent_path1, "dummy_value2", None, None, False))

    def testMakePluginReadParams7(self):

        local_params = {}
        local_params["work_dir"] = self.existent_path1
        local_params["target"] = "dummy_value2"
        local_params["save_output"] = "dummy_value3"
        self.make_task.params = local_params

        v, r = self.make_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, (self.existent_path1, "dummy_value2", "dummy_value3", None, False))

    def testMakePluginReadParams8(self):

        local_params = {}
        local_params["work_dir"] = self.existent_path1
        local_params["target"] = "dummy_value2"
        local_params["save_output"] = "dummy_value3"
        local_params["save_error_output"] = "dummy_value4"
        self.make_task.params = local_params

        v, r = self.make_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, (self.existent_path1, "dummy_value2", "dummy_value3", "dummy_value4", False))

    def testMakePluginReadParams9(self):

        local_params = {}
        local_params["work_dir"] = self.existent_path1
        local_params["target"] = "dummy_value2"
        local_params["save_output"] = "dummy_value3"
        local_params["save_error_output"] = "dummy_value4"
        local_params["suppress_stderr_warnings"] = "dummy_value5"
        self.make_task.params = local_params

        v, r = self.make_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, (self.existent_path1, "dummy_value2", "dummy_value3", "dummy_value4", True))

    def testMakePluginDumpOutput(self):
        self.assertFalse(os.path.exists(self.nonexistent_file1))
        make_plugin._dump_output(print, "test", self.nonexistent_file1, "test-contents")
        self.assertTrue(os.path.exists(self.nonexistent_file1))
        contents = ""
        with open(self.nonexistent_file1) as f:
            contents = f.read()
        self.assertTrue(contents, "test-contents")

    def testMakePluginDumpOutputsBackup1(self):

        test_stdout_fn = path_utils.concat_path(self.output_backup_storage, "make_plugin_output_backup_test_timestamp.txt")
        test_stderr_fn = path_utils.concat_path(self.output_backup_storage, "make_plugin_error_output_backup_test_timestamp.txt")

        self.assertFalse(os.path.exists(test_stdout_fn))
        self.assertFalse(os.path.exists(test_stderr_fn))

        with mock.patch("mvtools_envvars.mvtools_envvar_read_temp_path", return_value=(False, "error msg")) as dummy1:
            with mock.patch("maketimestamp.get_timestamp_now_compact", return_value="test_timestamp") as dummy2:
                v, r = make_plugin._dump_outputs_backup(print, "test-stdout", "test-stderr")
                self.assertFalse(v)

    def testMakePluginDumpOutputsBackup2(self):

        test_stdout_fn = path_utils.concat_path(self.output_backup_storage, "make_plugin_output_backup_test_timestamp.txt")
        test_stderr_fn = path_utils.concat_path(self.output_backup_storage, "make_plugin_error_output_backup_test_timestamp.txt")

        self.assertFalse(os.path.exists(test_stdout_fn))
        self.assertFalse(os.path.exists(test_stderr_fn))

        with open(test_stdout_fn, "w") as f:
            f.write("contents")

        self.assertTrue(os.path.exists(test_stdout_fn))

        with mock.patch("mvtools_envvars.mvtools_envvar_read_temp_path", return_value=(True, self.output_backup_storage)) as dummy1:
            with mock.patch("maketimestamp.get_timestamp_now_compact", return_value="test_timestamp") as dummy2:
                v, r = make_plugin._dump_outputs_backup(print, "test-stdout", "test-stderr")
                self.assertFalse(v)

    def testMakePluginDumpOutputsBackup3(self):

        test_stdout_fn = path_utils.concat_path(self.output_backup_storage, "make_plugin_output_backup_test_timestamp.txt")
        test_stderr_fn = path_utils.concat_path(self.output_backup_storage, "make_plugin_error_output_backup_test_timestamp.txt")

        self.assertFalse(os.path.exists(test_stdout_fn))
        self.assertFalse(os.path.exists(test_stderr_fn))

        with open(test_stderr_fn, "w") as f:
            f.write("contents")

        self.assertTrue(os.path.exists(test_stderr_fn))

        with mock.patch("mvtools_envvars.mvtools_envvar_read_temp_path", return_value=(True, self.output_backup_storage)) as dummy1:
            with mock.patch("maketimestamp.get_timestamp_now_compact", return_value="test_timestamp") as dummy2:
                v, r = make_plugin._dump_outputs_backup(print, "test-stdout", "test-stderr")
                self.assertFalse(v)

    def testMakePluginDumpOutputsBackup4(self):

        test_stdout_fn = path_utils.concat_path(self.output_backup_storage, "make_plugin_output_backup_test_timestamp.txt")
        test_stderr_fn = path_utils.concat_path(self.output_backup_storage, "make_plugin_error_output_backup_test_timestamp.txt")

        self.assertFalse(os.path.exists(test_stdout_fn))
        self.assertFalse(os.path.exists(test_stderr_fn))

        with mock.patch("mvtools_envvars.mvtools_envvar_read_temp_path", return_value=(True, self.output_backup_storage)) as dummy1:
            with mock.patch("maketimestamp.get_timestamp_now_compact", return_value="test_timestamp") as dummy2:
                v, r = make_plugin._dump_outputs_backup(print, "test-stdout", "test-stderr")
                self.assertTrue(v)

        self.assertTrue(os.path.exists(test_stdout_fn))
        self.assertTrue(os.path.exists(test_stderr_fn))

        stdout_contents = ""
        with open(test_stdout_fn, "r") as f:
            stdout_contents = f.read()
        self.assertEqual(stdout_contents, "test-stdout")

        stderr_contents = ""
        with open(test_stderr_fn, "r") as f:
            stderr_contents = f.read()
        self.assertEqual(stderr_contents, "test-stderr")

    def testMakePluginRunTask1(self):

        local_params = {}
        local_params["work_dir"] = self.existent_path1
        self.make_task.params = local_params

        with mock.patch("make_wrapper.make", return_value=(False, (True, "test1", "test2"))) as dummy1:
            with mock.patch("make_plugin._dump_output") as dummy2:
                with mock.patch("make_plugin._dump_outputs_backup", return_value=(True, None)) as dummy3:

                    v, r = self.make_task.run_task(print, "exe_name")
                    self.assertFalse(v)
                    dummy1.assert_called_with(self.existent_path1, None)
                    dummy2.assert_not_called()
                    dummy3.assert_not_called()

    def testMakePluginRunTask2(self):

        local_params = {}
        local_params["work_dir"] = self.existent_path1
        self.make_task.params = local_params

        with mock.patch("make_wrapper.make", return_value=(True, (False, "test1", "test2"))) as dummy1:
            with mock.patch("make_plugin._dump_output") as dummy2:
                with mock.patch("make_plugin._dump_outputs_backup", return_value=(True, None)) as dummy3:

                    v, r = self.make_task.run_task(print, "exe_name")
                    self.assertTrue(v)
                    self.assertEqual(r, "test2")
                    dummy1.assert_called_with(self.existent_path1, None)
                    dummy2.assert_has_calls([call(print, "output", None, "test1"), call(print, "error output", None, "test2")])
                    dummy3.assert_called_with(print, "test1", "test2")

    def testMakePluginRunTask3(self):

        local_params = {}
        local_params["work_dir"] = self.existent_path1
        self.make_task.params = local_params

        with mock.patch("make_wrapper.make", return_value=(True, (False, "test1", "test2"))) as dummy1:
            with mock.patch("make_plugin._dump_output") as dummy2:
                with mock.patch("make_plugin._dump_outputs_backup", return_value=(False, "test-warning-msg")) as dummy3:

                    v, r = self.make_task.run_task(print, "exe_name")
                    self.assertTrue(v)
                    self.assertEqual(r, "test-warning-msg%stest2" % os.linesep)
                    dummy1.assert_called_with(self.existent_path1, None)
                    dummy2.assert_has_calls([call(print, "output", None, "test1"), call(print, "error output", None, "test2")])
                    dummy3.assert_called_with(print, "test1", "test2")

    def testMakePluginRunTask4(self):

        local_params = {}
        local_params["work_dir"] = self.existent_path1
        local_params["suppress_stderr_warnings"] = "dummy_value5"
        self.make_task.params = local_params

        with mock.patch("make_wrapper.make", return_value=(True, (False, "test1", "test2"))) as dummy1:
            with mock.patch("make_plugin._dump_output") as dummy2:
                with mock.patch("make_plugin._dump_outputs_backup", return_value=(False, "test-warning-msg")) as dummy3:

                    v, r = self.make_task.run_task(print, "exe_name")
                    self.assertTrue(v)
                    self.assertEqual(r, "test-warning-msg")
                    dummy1.assert_called_with(self.existent_path1, None)
                    dummy2.assert_has_calls([call(print, "output", None, "test1"), call(print, "error output", None, "test2")])
                    dummy3.assert_called_with(print, "test1", "test2")

    def testMakePluginRunTask5(self):

        local_params = {}
        local_params["work_dir"] = self.existent_path1
        self.make_task.params = local_params

        with mock.patch("make_wrapper.make", return_value=(True, (True, "test1", "test2"))) as dummy1:
            with mock.patch("make_plugin._dump_output") as dummy2:
                with mock.patch("make_plugin._dump_outputs_backup", return_value=(True, None)) as dummy3:

                    v, r = self.make_task.run_task(print, "exe_name")
                    self.assertTrue(v)
                    dummy1.assert_called_with(self.existent_path1, None)
                    dummy2.assert_has_calls([call(print, "output", None, "test1"), call(print, "error output", None, "test2")])
                    dummy3.assert_not_called()

    def testMakePluginRunTask6(self):

        local_params = {}
        local_params["work_dir"] = self.existent_path1
        local_params["save_output"] = "dummy_value5"
        local_params["save_error_output"] = "dummy_value6"
        self.make_task.params = local_params

        with mock.patch("make_wrapper.make", return_value=(True, (True, "test1", "test2"))) as dummy1:
            with mock.patch("make_plugin._dump_output") as dummy2:
                with mock.patch("make_plugin._dump_outputs_backup", return_value=(True, None)) as dummy3:

                    v, r = self.make_task.run_task(print, "exe_name")
                    self.assertTrue(v)
                    dummy1.assert_called_with(self.existent_path1, None)
                    dummy2.assert_has_calls([call(print, "output", "dummy_value5", "test1"), call(print, "error output", "dummy_value6", "test2")])
                    dummy3.assert_not_called()

    def testMakePluginRunTask7(self):

        local_params = {}
        local_params["work_dir"] = self.existent_path1
        local_params["target"] = "dummy_value2"
        self.make_task.params = local_params

        with mock.patch("make_wrapper.make", return_value=(True, (True, "test1", "test2"))) as dummy1:
            with mock.patch("make_plugin._dump_output") as dummy2:
                with mock.patch("make_plugin._dump_outputs_backup", return_value=(True, None)) as dummy3:

                    v, r = self.make_task.run_task(print, "exe_name")
                    self.assertTrue(v)
                    dummy1.assert_called_with(self.existent_path1, "dummy_value2")
                    dummy2.assert_has_calls([call(print, "output", None, "test1"), call(print, "error output", None, "test2")])
                    dummy3.assert_not_called()

if __name__ == '__main__':
    unittest.main()
