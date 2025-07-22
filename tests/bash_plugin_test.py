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
import getcontents
import path_utils
import output_backup_helper

import bash_plugin

class BashPluginTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("bash_plugin_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # the test task
        self.bash_task = bash_plugin.CustomTask()

        # existent path 1
        self.existent_path1 = path_utils.concat_path(self.test_dir, "existent_path1")
        os.mkdir(self.existent_path1)

        # existent path 2
        self.existent_path2 = path_utils.concat_path(self.test_dir, "existent_path2")
        os.mkdir(self.existent_path2)

        # nonexistent path 1
        self.nonexistent_path1 = path_utils.concat_path(self.test_dir, "nonexistent_path1")

        # dumped_stdout_file
        self.dumped_stdout_file = path_utils.concat_path(self.test_dir, "dumped_stdout_file")

        # dumped_stderr_file
        self.dumped_stderr_file = path_utils.concat_path(self.test_dir, "dumped_stderr_file")

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testBashPluginReadParams1(self):

        local_params = {}
        self.bash_task.params = local_params

        v, r = self.bash_task._read_params()
        self.assertFalse(v)

    def testBashPluginReadParams2(self):

        local_params = {}
        local_params["script"] = self.nonexistent_path1
        self.bash_task.params = local_params

        v, r = self.bash_task._read_params()
        self.assertFalse(v)

    def testBashPluginReadParams3(self):

        local_params = {}
        local_params["script"] = self.existent_path1
        self.bash_task.params = local_params

        v, r = self.bash_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, (self.existent_path1, None, [], None, None, False) )

    def testBashPluginReadParams4(self):

        local_params = {}
        local_params["script"] = self.existent_path1
        local_params["cwd"] = self.nonexistent_path1
        self.bash_task.params = local_params

        v, r = self.bash_task._read_params()
        self.assertFalse(v)

    def testBashPluginReadParams5(self):

        local_params = {}
        local_params["script"] = self.existent_path1
        local_params["cwd"] = self.existent_path2
        self.bash_task.params = local_params

        v, r = self.bash_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, (self.existent_path1, self.existent_path2, [], None, None, False) )

    def testBashPluginReadParams6(self):

        local_params = {}
        local_params["script"] = self.existent_path1
        local_params["cwd"] = self.existent_path2
        local_params["arg"] = "dummy_value1"
        self.bash_task.params = local_params

        v, r = self.bash_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, (self.existent_path1, self.existent_path2, ["dummy_value1"], None, None, False) )

    def testBashPluginReadParams7(self):

        local_params = {}
        local_params["script"] = self.existent_path1
        local_params["cwd"] = self.existent_path2
        local_params["arg"] = ["dummy_value1", "dummy_value2"]
        self.bash_task.params = local_params

        v, r = self.bash_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, (self.existent_path1, self.existent_path2, ["dummy_value1", "dummy_value2"], None, None, False) )

    def testBashPluginReadParams8(self):

        local_params = {}
        local_params["script"] = self.existent_path1
        local_params["cwd"] = self.existent_path2
        local_params["arg"] = "dummy_value1"
        local_params["save_output"] = "dummy_value2"
        self.bash_task.params = local_params

        v, r = self.bash_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, (self.existent_path1, self.existent_path2, ["dummy_value1"], "dummy_value2", None, False) )

    def testBashPluginReadParams9(self):

        local_params = {}
        local_params["script"] = self.existent_path1
        local_params["cwd"] = self.existent_path2
        local_params["arg"] = "dummy_value1"
        local_params["save_output"] = "dummy_value2"
        local_params["save_error_output"] = "dummy_value3"
        self.bash_task.params = local_params

        v, r = self.bash_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, (self.existent_path1, self.existent_path2, ["dummy_value1"], "dummy_value2", "dummy_value3", False) )

    def testBashPluginReadParams10(self):

        local_params = {}
        local_params["script"] = self.existent_path1
        local_params["cwd"] = self.existent_path2
        local_params["arg"] = "dummy_value1"
        local_params["save_output"] = "dummy_value2"
        local_params["save_error_output"] = "dummy_value3"
        local_params["suppress_stderr_warnings"] = "dummy_value4"
        self.bash_task.params = local_params

        v, r = self.bash_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, (self.existent_path1, self.existent_path2, ["dummy_value1"], "dummy_value2", "dummy_value3", True) )

    def testBashPluginRunTask1(self):

        local_params = {}
        local_params["script"] = self.existent_path1
        self.bash_task.params = local_params

        with mock.patch("bash_wrapper.exec", return_value=(True, (True, "", ""))) as dummy:
            v, r = self.bash_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(self.existent_path1, None, [])

    def testBashPluginRunTask2(self):

        local_params = {}
        local_params["script"] = self.existent_path1
        local_params["cwd"] = self.existent_path2
        self.bash_task.params = local_params

        with mock.patch("bash_wrapper.exec", return_value=(True, (True, "", ""))) as dummy:
            v, r = self.bash_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(self.existent_path1, self.existent_path2, [])

    def testBashPluginRunTask3(self):

        local_params = {}
        local_params["script"] = self.existent_path1
        local_params["cwd"] = self.existent_path2
        local_params["arg"] = "dummy_value1"
        self.bash_task.params = local_params

        with mock.patch("bash_wrapper.exec", return_value=(True, (True, "", ""))) as dummy:
            v, r = self.bash_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(self.existent_path1, self.existent_path2, ["dummy_value1"])

    def testBashPluginRunTask4(self):

        local_params = {}
        local_params["script"] = self.existent_path1
        local_params["cwd"] = self.existent_path2
        local_params["arg"] = "dummy_value1"
        local_params["save_output"] = self.dumped_stdout_file
        local_params["save_error_output"] = self.dumped_stderr_file
        self.bash_task.params = local_params

        with mock.patch("bash_wrapper.exec", return_value=(True, (True, "test-stdout", "test-stderr"))) as dummy1:
            with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value="somewarning") as dummy2:
                v, r = self.bash_task.run_task(print, "exe_name")
                self.assertTrue(v)
                self.assertTrue("somewarning" in r)
                self.assertTrue("test-stderr" in r)
                self.assertTrue("test-stdout" in getcontents.getcontents(self.dumped_stdout_file))
                self.assertTrue("test-stderr" in getcontents.getcontents(self.dumped_stderr_file))
                dummy1.assert_called_with(self.existent_path1, self.existent_path2, ["dummy_value1"])

    def testBashPluginRunTask5(self):

        local_params = {}
        local_params["script"] = self.existent_path1
        local_params["cwd"] = self.existent_path2
        local_params["arg"] = "dummy_value1"
        local_params["save_output"] = self.dumped_stdout_file
        local_params["save_error_output"] = self.dumped_stderr_file
        local_params["suppress_stderr_warnings"] = True
        self.bash_task.params = local_params

        with mock.patch("bash_wrapper.exec", return_value=(True, (True, "test-stdout", "test-stderr"))) as dummy1:
            with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value="somewarning") as dummy2:
                v, r = self.bash_task.run_task(print, "exe_name")
                self.assertTrue(v)
                self.assertTrue("somewarning" in r)
                self.assertFalse("test-stderr" in r)
                self.assertTrue("test-stdout" in getcontents.getcontents(self.dumped_stdout_file))
                self.assertTrue("test-stderr" in getcontents.getcontents(self.dumped_stderr_file))
                dummy1.assert_called_with(self.existent_path1, self.existent_path2, ["dummy_value1"])

if __name__ == "__main__":
    unittest.main()
