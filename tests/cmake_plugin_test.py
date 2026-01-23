#!/usr/bin/env python

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
import cmake_lib

import cmake_plugin

class CmakePluginTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("cmake_plugin_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # the test task
        self.cmake_task = cmake_plugin.CustomTask()

        # existent path 1
        self.existent_path1 = path_utils.concat_path(self.test_dir, "existent_path1")
        os.mkdir(self.existent_path1)

        # existent path 2
        self.existent_path2 = path_utils.concat_path(self.test_dir, "existent_path2")
        os.mkdir(self.existent_path2)

        # nonexistent path 1
        self.nonexistent_path1 = path_utils.concat_path(self.test_dir, "nonexistent_path1")

        # nonexistent path 2
        self.nonexistent_path2 = path_utils.concat_path(self.test_dir, "nonexistent_path2")

        # existent file 1
        self.existent_file1 = path_utils.concat_path(self.test_dir, "existent_file1.txt")
        create_and_write_file.create_file_contents(self.existent_file1, "test file 1")

        self.test_opts = cmake_lib.boot_options()

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    # mvtodo: remake {_read_params} coverage

    def testCmakePluginAssembleOptions1(self):
        self.assertEqual(cmake_plugin._assemble_options(None, None, None, None, None), self.test_opts)

    def testCmakePluginAssembleOptions2(self):
        self.assertEqual(cmake_plugin._assemble_options("test1", None, None, None, None), None)

    def testCmakePluginAssembleOptions3(self):
        self.assertEqual(cmake_plugin._assemble_options("release", None, None, None, None), {"CMAKE_BUILD_TYPE": ("STRING", "release")})

    def testCmakePluginAssembleOptions4(self):
        self.assertEqual(cmake_plugin._assemble_options(None, "test1", None, None, None), {"CMAKE_INSTALL_PREFIX": ("STRING", "test1")})

    def testCmakePluginAssembleOptions5(self):
        self.assertEqual(cmake_plugin._assemble_options(None, None, "test1", None, None), {"CMAKE_PREFIX_PATH": ("STRING", "test1")})

    def testCmakePluginAssembleOptions6(self):
        self.assertEqual(cmake_plugin._assemble_options(None, None, None, "test1", None), {"CMAKE_TOOLCHAIN_FILE": ("STRING", "test1")})

    def testCmakePluginAssembleOptions7(self):
        self.assertEqual(cmake_plugin._assemble_options(None, None, None, None, "test1"), None)
        self.assertEqual(cmake_plugin._assemble_options(None, None, None, None, "test1:test2"), None)
        self.assertEqual(cmake_plugin._assemble_options(None, None, None, None, ["test1:test2=test3"]), {"test1" : ("test2", "test3")})

    def testCmakePluginRunTask1(self):

        local_params = {}
        local_params["operation"] = "cfg-and-gen"
        local_params["cmake_path"] = "dummy_value1"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        local_params["gen_type"] = "dummy_value4"
        self.cmake_task.params = local_params

        with mock.patch("cmake_lib.configure_and_generate", return_value=(False, (True, "test1", "test2"))) as dummy1:
            with mock.patch("output_backup_helper.dump_output") as dummy2:
                with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value=None) as dummy3:

                    v, r = self.cmake_task.run_task(print, "exe_name")
                    self.assertFalse(v)
                    dummy1.assert_called_with("dummy_value1", self.existent_path1, self.existent_path2, "dummy_value4", {})
                    dummy2.assert_not_called()
                    dummy3.assert_not_called()

    def testCmakePluginRunTask2(self):

        local_params = {}
        local_params["operation"] = "cfg-and-gen"
        local_params["cmake_path"] = "dummy_value1"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        local_params["gen_type"] = "dummy_value4"
        self.cmake_task.params = local_params

        with mock.patch("cmake_lib.configure_and_generate", return_value=(True, (False, "test1", "test2"))) as dummy1:
            with mock.patch("output_backup_helper.dump_output") as dummy2:
                with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value=None) as dummy3:

                    v, r = self.cmake_task.run_task(print, "exe_name")
                    self.assertTrue(v)
                    self.assertEqual(r, "test2")
                    dummy1.assert_called_with("dummy_value1", self.existent_path1, self.existent_path2, "dummy_value4", {})
                    dummy2.assert_has_calls([call(print, None, "test1", ("Cmake's stdout has been saved to: [%s]" % None)), call(print, None, "test2", ("Cmake's stderr has been saved to: [%s]" % None))])
                    dummy3.assert_called_with(False, print, [("cmake_plugin_stdout", "test1", "Cmake's stdout"), ("cmake_plugin_stderr", "test2", "Cmake's stderr")])

    def testCmakePluginRunTask3(self):

        local_params = {}
        local_params["operation"] = "cfg-and-gen"
        local_params["cmake_path"] = "dummy_value1"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        local_params["gen_type"] = "dummy_value4"
        self.cmake_task.params = local_params

        with mock.patch("cmake_lib.configure_and_generate", return_value=(True, (False, "test1", "test2"))) as dummy1:
            with mock.patch("output_backup_helper.dump_output") as dummy2:
                with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value="test-warning-msg") as dummy3:

                    v, r = self.cmake_task.run_task(print, "exe_name")
                    self.assertTrue(v)
                    self.assertEqual(r, "test-warning-msg%stest2" % os.linesep)
                    dummy1.assert_called_with("dummy_value1", self.existent_path1, self.existent_path2, "dummy_value4", {})
                    dummy2.assert_has_calls([call(print, None, "test1", ("Cmake's stdout has been saved to: [%s]" % None)), call(print, None, "test2", ("Cmake's stderr has been saved to: [%s]" % None))])
                    dummy3.assert_called_with(False, print, [("cmake_plugin_stdout", "test1", "Cmake's stdout"), ("cmake_plugin_stderr", "test2", "Cmake's stderr")])

    def testCmakePluginRunTask4(self):

        local_params = {}
        local_params["operation"] = "cfg-and-gen"
        local_params["cmake_path"] = "dummy_value1"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        local_params["gen_type"] = "dummy_value4"
        local_params["suppress_stderr_warnings"] = "dummy_value5"
        self.cmake_task.params = local_params

        with mock.patch("cmake_lib.configure_and_generate", return_value=(True, (False, "test1", "test2"))) as dummy1:
            with mock.patch("output_backup_helper.dump_output") as dummy2:
                with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value="test-warning-msg") as dummy3:

                    v, r = self.cmake_task.run_task(print, "exe_name")
                    self.assertTrue(v)
                    self.assertEqual(r, "test-warning-msg%scmake's stderr has been suppressed" % os.linesep)
                    dummy1.assert_called_with("dummy_value1", self.existent_path1, self.existent_path2, "dummy_value4", {})
                    dummy2.assert_has_calls([call(print, None, "test1", ("Cmake's stdout has been saved to: [%s]" % None)), call(print, None, "test2", ("Cmake's stderr has been saved to: [%s]" % None))])
                    dummy3.assert_called_with(False, print, [("cmake_plugin_stdout", "test1", "Cmake's stdout"), ("cmake_plugin_stderr", "test2", "Cmake's stderr")])

    def testCmakePluginRunTask5(self):

        local_params = {}
        local_params["operation"] = "cfg-and-gen"
        local_params["cmake_path"] = "dummy_value1"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        local_params["gen_type"] = "dummy_value4"
        self.cmake_task.params = local_params

        with mock.patch("cmake_lib.configure_and_generate", return_value=(True, (True, "test1", "test2"))) as dummy1:
            with mock.patch("output_backup_helper.dump_output") as dummy2:
                with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value=None) as dummy3:

                    v, r = self.cmake_task.run_task(print, "exe_name")
                    self.assertTrue(v)
                    dummy1.assert_called_with("dummy_value1", self.existent_path1, self.existent_path2, "dummy_value4", {})
                    dummy2.assert_has_calls([call(print, None, "test1", ("Cmake's stdout has been saved to: [%s]" % None)), call(print, None, "test2", ("Cmake's stderr has been saved to: [%s]" % None))])
                    dummy3.assert_called_with(True, print, [("cmake_plugin_stdout", "test1", "Cmake's stdout"), ("cmake_plugin_stderr", "test2", "Cmake's stderr")])

    def testCmakePluginRunTask6(self):

        local_params = {}
        local_params["operation"] = "cfg-and-gen"
        local_params["cmake_path"] = "dummy_value1"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        local_params["gen_type"] = "dummy_value4"
        local_params["save_output"] = "dummy_value5"
        local_params["save_error_output"] = "dummy_value6"
        self.cmake_task.params = local_params

        with mock.patch("cmake_lib.configure_and_generate", return_value=(True, (True, "test1", "test2"))) as dummy1:
            with mock.patch("output_backup_helper.dump_output") as dummy2:
                with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value=None) as dummy3:

                    v, r = self.cmake_task.run_task(print, "exe_name")
                    self.assertTrue(v)
                    dummy1.assert_called_with("dummy_value1", self.existent_path1, self.existent_path2, "dummy_value4", {})
                    dummy2.assert_has_calls([call(print, "dummy_value5", "test1", ("Cmake's stdout has been saved to: [dummy_value5]")), call(print, "dummy_value6", "test2", ("Cmake's stderr has been saved to: [dummy_value6]"))])
                    dummy3.assert_called_with(True, print, [("cmake_plugin_stdout", "test1", "Cmake's stdout"), ("cmake_plugin_stderr", "test2", "Cmake's stderr")])

    def testCmakePluginRunTask7(self):

        local_params = {}
        local_params["operation"] = "ext-opts"
        local_params["cmake_path"] = None
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.nonexistent_path1
        local_params["temp_path"] = self.nonexistent_path2
        self.cmake_task.params = local_params

        with mock.patch("cmake_lib.extract_options", return_value=(False, "err-msg")) as dummy:

            v, r = self.cmake_task.run_task(print, "exe_name")
            self.assertFalse(v)
            self.assertEqual(r, "err-msg")
            dummy.assert_called_with(None, self.existent_path1, self.nonexistent_path1, self.nonexistent_path2)

    def testCmakePluginRunTask8(self):

        local_params = {}
        local_params["operation"] = "ext-opts"
        local_params["cmake_path"] = "dummy_value1"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.nonexistent_path1
        local_params["temp_path"] = self.nonexistent_path2
        self.cmake_task.params = local_params

        with mock.patch("cmake_lib.extract_options", return_value=(False, "err-msg")) as dummy:

            v, r = self.cmake_task.run_task(print, "exe_name")
            self.assertFalse(v)
            self.assertEqual(r, "err-msg")
            dummy.assert_called_with("dummy_value1", self.existent_path1, self.nonexistent_path1, self.nonexistent_path2)

    def testCmakePluginRunTask9(self):

        local_params = {}
        local_params["operation"] = "ext-opts"
        local_params["cmake_path"] = None
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.nonexistent_path1
        local_params["temp_path"] = self.nonexistent_path2
        self.cmake_task.params = local_params

        with mock.patch("cmake_lib.extract_options", return_value=(True, None)) as dummy:

            v, r = self.cmake_task.run_task(print, "exe_name")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(None, self.existent_path1, self.nonexistent_path1, self.nonexistent_path2)

    def testCmakePluginRunTask10(self):

        local_params = {}
        local_params["operation"] = "ext-opts"
        local_params["cmake_path"] = "dummy_value1"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.nonexistent_path1
        local_params["temp_path"] = self.nonexistent_path2
        self.cmake_task.params = local_params

        with mock.patch("cmake_lib.extract_options", return_value=(True, None)) as dummy:

            v, r = self.cmake_task.run_task(print, "exe_name")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with("dummy_value1", self.existent_path1, self.nonexistent_path1, self.nonexistent_path2)

if __name__ == "__main__":
    unittest.main()
