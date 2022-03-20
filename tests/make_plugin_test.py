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
        self.assertEqual(r, (self.existent_path1, None, None, None, None, False))

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
        self.assertEqual(r, (self.existent_path1, "dummy_value2", None, None, None, False))

    def testMakePluginReadParams7(self):

        local_params = {}
        local_params["work_dir"] = self.existent_path1
        local_params["target"] = "dummy_value2"
        local_params["prefix"] = "dummy_value3"
        self.make_task.params = local_params

        v, r = self.make_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, (self.existent_path1, "dummy_value2", "dummy_value3", None, None, False))

    def testMakePluginReadParams8(self):

        local_params = {}
        local_params["work_dir"] = self.existent_path1
        local_params["target"] = "dummy_value2"
        local_params["prefix"] = "dummy_value3"
        local_params["save_output"] = "dummy_value4"
        self.make_task.params = local_params

        v, r = self.make_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, (self.existent_path1, "dummy_value2", "dummy_value3", "dummy_value4", None, False))

    def testMakePluginReadParams9(self):

        local_params = {}
        local_params["work_dir"] = self.existent_path1
        local_params["target"] = "dummy_value2"
        local_params["prefix"] = "dummy_value3"
        local_params["save_output"] = "dummy_value4"
        local_params["save_error_output"] = "dummy_value5"
        self.make_task.params = local_params

        v, r = self.make_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, (self.existent_path1, "dummy_value2", "dummy_value3", "dummy_value4", "dummy_value5", False))

    def testMakePluginReadParams10(self):

        local_params = {}
        local_params["work_dir"] = self.existent_path1
        local_params["target"] = "dummy_value2"
        local_params["prefix"] = "dummy_value3"
        local_params["save_output"] = "dummy_value4"
        local_params["save_error_output"] = "dummy_value5"
        local_params["suppress_stderr_warnings"] = "dummy_value6"
        self.make_task.params = local_params

        v, r = self.make_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, (self.existent_path1, "dummy_value2", "dummy_value3", "dummy_value4", "dummy_value5", True))

    def testMakePluginRunTask1(self):

        local_params = {}
        local_params["work_dir"] = self.existent_path1
        self.make_task.params = local_params

        with mock.patch("make_wrapper.make", return_value=(False, (True, "test1", "test2"))) as dummy1:
            with mock.patch("output_backup_helper.dump_output") as dummy2:
                with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value=None) as dummy3:

                    v, r = self.make_task.run_task(print, "exe_name")
                    self.assertFalse(v)
                    dummy1.assert_called_with(self.existent_path1, None, None)
                    dummy2.assert_not_called()
                    dummy3.assert_not_called()

    def testMakePluginRunTask2(self):

        local_params = {}
        local_params["work_dir"] = self.existent_path1
        self.make_task.params = local_params

        with mock.patch("make_wrapper.make", return_value=(True, (False, "test1", "test2"))) as dummy1:
            with mock.patch("output_backup_helper.dump_output") as dummy2:
                with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value=None) as dummy3:

                    v, r = self.make_task.run_task(print, "exe_name")
                    self.assertTrue(v)
                    self.assertEqual(r, "test2")
                    dummy1.assert_called_with(self.existent_path1, None, None)
                    dummy2.assert_has_calls([call(print, None, "test1", ("Make's stdout has been saved to: [%s]" % None)), call(print, None, "test2", ("Make's stderr has been saved to: [%s]" % None))])
                    dummy3.assert_called_with(False, print, [("make_plugin_stdout", "test1", "Make's stdout"), ("make_plugin_stderr", "test2", "Make's stderr")])

    def testMakePluginRunTask3(self):

        local_params = {}
        local_params["work_dir"] = self.existent_path1
        self.make_task.params = local_params

        with mock.patch("make_wrapper.make", return_value=(True, (False, "test1", "test2"))) as dummy1:
            with mock.patch("output_backup_helper.dump_output") as dummy2:
                with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value="test-warning-msg") as dummy3:

                    v, r = self.make_task.run_task(print, "exe_name")
                    self.assertTrue(v)
                    self.assertEqual(r, "test-warning-msg%stest2" % os.linesep)
                    dummy1.assert_called_with(self.existent_path1, None, None)
                    dummy2.assert_has_calls([call(print, None, "test1", ("Make's stdout has been saved to: [%s]" % None)), call(print, None, "test2", ("Make's stderr has been saved to: [%s]" % None))])
                    dummy3.assert_called_with(False, print, [("make_plugin_stdout", "test1", "Make's stdout"), ("make_plugin_stderr", "test2", "Make's stderr")])

    def testMakePluginRunTask4(self):

        local_params = {}
        local_params["work_dir"] = self.existent_path1
        local_params["suppress_stderr_warnings"] = "dummy_value5"
        self.make_task.params = local_params

        with mock.patch("make_wrapper.make", return_value=(True, (False, "test1", "test2"))) as dummy1:
            with mock.patch("output_backup_helper.dump_output") as dummy2:
                with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value="test-warning-msg") as dummy3:

                    v, r = self.make_task.run_task(print, "exe_name")
                    self.assertTrue(v)
                    self.assertEqual(r, "test-warning-msg%smake's stderr has been suppressed" % os.linesep)
                    dummy1.assert_called_with(self.existent_path1, None, None)
                    dummy2.assert_has_calls([call(print, None, "test1", ("Make's stdout has been saved to: [%s]" % None)), call(print, None, "test2", ("Make's stderr has been saved to: [%s]" % None))])
                    dummy3.assert_called_with(False, print, [("make_plugin_stdout", "test1", "Make's stdout"), ("make_plugin_stderr", "test2", "Make's stderr")])

    def testMakePluginRunTask5(self):

        local_params = {}
        local_params["work_dir"] = self.existent_path1
        self.make_task.params = local_params

        with mock.patch("make_wrapper.make", return_value=(True, (True, "test1", "test2"))) as dummy1:
            with mock.patch("output_backup_helper.dump_output") as dummy2:
                with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value=None) as dummy3:

                    v, r = self.make_task.run_task(print, "exe_name")
                    self.assertTrue(v)
                    dummy1.assert_called_with(self.existent_path1, None, None)
                    dummy2.assert_has_calls([call(print, None, "test1", ("Make's stdout has been saved to: [%s]" % None)), call(print, None, "test2", ("Make's stderr has been saved to: [%s]" % None))])
                    dummy3.assert_called_with(True, print, [("make_plugin_stdout", "test1", "Make's stdout"), ("make_plugin_stderr", "test2", "Make's stderr")])

    def testMakePluginRunTask6(self):

        local_params = {}
        local_params["work_dir"] = self.existent_path1
        local_params["save_output"] = "dummy_value5"
        local_params["save_error_output"] = "dummy_value6"
        self.make_task.params = local_params

        with mock.patch("make_wrapper.make", return_value=(True, (True, "test1", "test2"))) as dummy1:
            with mock.patch("output_backup_helper.dump_output") as dummy2:
                with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value=None) as dummy3:

                    v, r = self.make_task.run_task(print, "exe_name")
                    self.assertTrue(v)
                    dummy1.assert_called_with(self.existent_path1, None, None)
                    dummy2.assert_has_calls([call(print, "dummy_value5", "test1", ("Make's stdout has been saved to: [dummy_value5]")), call(print, "dummy_value6", "test2", ("Make's stderr has been saved to: [dummy_value6]"))])
                    dummy3.assert_called_with(True, print, [("make_plugin_stdout", "test1", "Make's stdout"), ("make_plugin_stderr", "test2", "Make's stderr")])

    def testMakePluginRunTask7(self):

        local_params = {}
        local_params["work_dir"] = self.existent_path1
        local_params["target"] = "dummy_value2"
        self.make_task.params = local_params

        with mock.patch("make_wrapper.make", return_value=(True, (True, "test1", "test2"))) as dummy1:
            with mock.patch("output_backup_helper.dump_output") as dummy2:
                with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value=None) as dummy3:

                    v, r = self.make_task.run_task(print, "exe_name")
                    self.assertTrue(v)
                    dummy1.assert_called_with(self.existent_path1, "dummy_value2", None)
                    dummy2.assert_has_calls([call(print, None, "test1", ("Make's stdout has been saved to: [%s]" % None)), call(print, None, "test2", ("Make's stderr has been saved to: [%s]" % None))])
                    dummy3.assert_called_with(True, print, [("make_plugin_stdout", "test1", "Make's stdout"), ("make_plugin_stderr", "test2", "Make's stderr")])

    def testMakePluginRunTask8(self):

        local_params = {}
        local_params["work_dir"] = self.existent_path1
        local_params["target"] = "dummy_value2"
        local_params["prefix"] = "dummy_value3"
        self.make_task.params = local_params

        with mock.patch("make_wrapper.make", return_value=(True, (True, "test1", "test2"))) as dummy1:
            with mock.patch("output_backup_helper.dump_output") as dummy2:
                with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value=None) as dummy3:

                    v, r = self.make_task.run_task(print, "exe_name")
                    self.assertTrue(v)
                    dummy1.assert_called_with(self.existent_path1, "dummy_value2", "dummy_value3")
                    dummy2.assert_has_calls([call(print, None, "test1", ("Make's stdout has been saved to: [%s]" % None)), call(print, None, "test2", ("Make's stderr has been saved to: [%s]" % None))])
                    dummy3.assert_called_with(True, print, [("make_plugin_stdout", "test1", "Make's stdout"), ("make_plugin_stderr", "test2", "Make's stderr")])

if __name__ == '__main__':
    unittest.main()
