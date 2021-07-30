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

        self.output_backup_storage = path_utils.concat_path(self.test_dir, "output_backup")
        os.mkdir(self.output_backup_storage)

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

        # existent file 1
        self.existent_file1 = path_utils.concat_path(self.test_dir, "existent_file1.txt")
        create_and_write_file.create_file_contents(self.existent_file1, "test file 1")

        # nonexistent file 1
        self.nonexistent_file1 = path_utils.concat_path(self.test_dir, "non_pre_existent_file1.txt")

        self.test_opts = cmake_lib.boot_options()

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testCmakePluginReadParams1(self):

        local_params = {}
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertFalse(v)

    def testCmakePluginReadParams2(self):

        local_params = {}
        local_params["cmake_path"] = "dummy_value1"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertFalse(v)

    def testCmakePluginReadParams3(self):

        local_params = {}
        local_params["cmake_path"] = "dummy_value1"
        local_params["source_path"] = "dummy_value2"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertFalse(v)

    def testCmakePluginReadParams4(self):

        local_params = {}
        local_params["cmake_path"] = "dummy_value1"
        local_params["source_path"] = "dummy_value2"
        local_params["output_path"] = "dummy_value3"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertFalse(v)

    def testCmakePluginReadParams5(self):

        local_params = {}
        local_params["cmake_path"] = "dummy_value1"
        local_params["source_path"] = self.nonexistent_path1
        local_params["output_path"] = self.existent_path2
        local_params["gen_type"] = "dummy_value4"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertFalse(v)

    def testCmakePluginReadParams6(self):

        local_params = {}
        local_params["cmake_path"] = "dummy_value1"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.nonexistent_path1
        local_params["gen_type"] = "dummy_value4"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertFalse(v)

    def testCmakePluginReadParams7(self):

        local_params = {}
        local_params["cmake_path"] = "dummy_value1"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        local_params["gen_type"] = "dummy_value4"
        local_params["save_output"] = self.existent_file1
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertFalse(v)

    def testCmakePluginReadParams8(self):

        local_params = {}
        local_params["cmake_path"] = "dummy_value1"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        local_params["gen_type"] = "dummy_value4"
        local_params["save_error_output"] = self.existent_file1
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertFalse(v)

    def testCmakePluginReadParams9(self):

        local_params = {}
        local_params["cmake_path"] = "dummy_value1"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        local_params["gen_type"] = "dummy_value4"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", self.existent_path1, self.existent_path2, "dummy_value4", None, None, None, None, None, None, False) )

    def testCmakePluginReadParams10(self):

        local_params = {}
        local_params["cmake_path"] = "dummy_value1"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        local_params["gen_type"] = "dummy_value4"
        local_params["build_type"] = "dummy_value5"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", self.existent_path1, self.existent_path2, "dummy_value4", "dummy_value5", None, None, None, None, None, False) )

    def testCmakePluginReadParams11(self):

        local_params = {}
        local_params["cmake_path"] = "dummy_value1"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        local_params["gen_type"] = "dummy_value4"
        local_params["build_type"] = "dummy_value5"
        local_params["install_prefix"] = "dummy_value6"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", self.existent_path1, self.existent_path2, "dummy_value4", "dummy_value5", "dummy_value6", None, None, None, None, False) )

    def testCmakePluginReadParams12(self):

        local_params = {}
        local_params["cmake_path"] = "dummy_value1"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        local_params["gen_type"] = "dummy_value4"
        local_params["build_type"] = "dummy_value5"
        local_params["install_prefix"] = "dummy_value6"
        local_params["toolchain"] = "dummy_value7"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", self.existent_path1, self.existent_path2, "dummy_value4", "dummy_value5", "dummy_value6", "dummy_value7", None, None, None, False) )

    def testCmakePluginReadParams13(self):

        local_params = {}
        local_params["cmake_path"] = "dummy_value1"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        local_params["gen_type"] = "dummy_value4"
        local_params["build_type"] = "dummy_value5"
        local_params["install_prefix"] = "dummy_value6"
        local_params["toolchain"] = "dummy_value7"
        local_params["option"] = "dummy_value8"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", self.existent_path1, self.existent_path2, "dummy_value4", "dummy_value5", "dummy_value6", "dummy_value7", ["dummy_value8"], None, None, False) )

    def testCmakePluginReadParams14(self):

        local_params = {}
        local_params["cmake_path"] = "dummy_value1"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        local_params["gen_type"] = "dummy_value4"
        local_params["build_type"] = "dummy_value5"
        local_params["install_prefix"] = "dummy_value6"
        local_params["toolchain"] = "dummy_value7"
        local_params["option"] = ["dummy_value8", "dummy_value9"]
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", self.existent_path1, self.existent_path2, "dummy_value4", "dummy_value5", "dummy_value6", "dummy_value7", ["dummy_value8", "dummy_value9"], None, None, False) )

    def testCmakePluginReadParams15(self):

        local_params = {}
        local_params["cmake_path"] = "dummy_value1"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        local_params["gen_type"] = "dummy_value4"
        local_params["build_type"] = "dummy_value5"
        local_params["install_prefix"] = "dummy_value6"
        local_params["toolchain"] = "dummy_value7"
        local_params["option"] = "dummy_value8"
        local_params["save_output"] = "dummy_value9"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", self.existent_path1, self.existent_path2, "dummy_value4", "dummy_value5", "dummy_value6", "dummy_value7", ["dummy_value8"], "dummy_value9", None, False) )

    def testCmakePluginReadParams16(self):

        local_params = {}
        local_params["cmake_path"] = "dummy_value1"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        local_params["gen_type"] = "dummy_value4"
        local_params["build_type"] = "dummy_value5"
        local_params["install_prefix"] = "dummy_value6"
        local_params["toolchain"] = "dummy_value7"
        local_params["option"] = "dummy_value8"
        local_params["save_output"] = "dummy_value9"
        local_params["save_error_output"] = "dummy_value10"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", self.existent_path1, self.existent_path2, "dummy_value4", "dummy_value5", "dummy_value6", "dummy_value7", ["dummy_value8"], "dummy_value9", "dummy_value10", False) )

    def testCmakePluginReadParams17(self):

        local_params = {}
        local_params["cmake_path"] = "dummy_value1"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        local_params["gen_type"] = "dummy_value4"
        local_params["build_type"] = "dummy_value5"
        local_params["install_prefix"] = "dummy_value6"
        local_params["toolchain"] = "dummy_value7"
        local_params["option"] = "dummy_value8"
        local_params["save_output"] = "dummy_value9"
        local_params["save_error_output"] = "dummy_value10"
        local_params["suppress_stderr_warnings"] = "dummy_value11"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", self.existent_path1, self.existent_path2, "dummy_value4", "dummy_value5", "dummy_value6", "dummy_value7", ["dummy_value8"], "dummy_value9", "dummy_value10", True) )

    def testCmakePluginAssembleOptions1(self):
        self.assertEqual(self.cmake_task._assemble_options(None, None, None, None), self.test_opts)

    def testCmakePluginAssembleOptions2(self):
        self.assertEqual(self.cmake_task._assemble_options("test1", None, None, None), None)

    def testCmakePluginAssembleOptions3(self):
        self.assertEqual(self.cmake_task._assemble_options("release", None, None, None), {"CMAKE_BUILD_TYPE": ("STRING", "release")})

    def testCmakePluginAssembleOptions4(self):
        self.assertEqual(self.cmake_task._assemble_options(None, "test1", None, None), {"CMAKE_INSTALL_PREFIX": ("STRING", "test1")})

    def testCmakePluginAssembleOptions5(self):
        self.assertEqual(self.cmake_task._assemble_options(None, None, "test1", None), {"CMAKE_TOOLCHAIN_FILE": ("STRING", "test1")})

    def testCmakePluginAssembleOptions6(self):
        self.assertEqual(self.cmake_task._assemble_options(None, None, None, "test1"), None)
        self.assertEqual(self.cmake_task._assemble_options(None, None, None, "test1:test2"), None)
        self.assertEqual(self.cmake_task._assemble_options(None, None, None, ["test1:test2=test3"]), {"test1" : ("test2", "test3")})

    def testCmakePluginDumpOutput(self):
        self.assertFalse(os.path.exists(self.nonexistent_file1))
        self.cmake_task._dump_output(print, "test", self.nonexistent_file1, "test-contents")
        self.assertTrue(os.path.exists(self.nonexistent_file1))
        contents = ""
        with open(self.nonexistent_file1) as f:
            contents = f.read()
        self.assertTrue(contents, "test-contents")

    def testCmakePluginDumpOutputsBackup1(self):

        test_stdout_fn = path_utils.concat_path(self.output_backup_storage, "cmake_plugin_output_backup_test_timestamp.txt")
        test_stderr_fn = path_utils.concat_path(self.output_backup_storage, "cmake_plugin_error_output_backup_test_timestamp.txt")

        self.assertFalse(os.path.exists(test_stdout_fn))
        self.assertFalse(os.path.exists(test_stderr_fn))

        with mock.patch("mvtools_envvars.mvtools_envvar_read_temp_path", return_value=(False, "error msg")) as dummy1:
            with mock.patch("maketimestamp.get_timestamp_now_compact", return_value="test_timestamp") as dummy2:
                v, r = self.cmake_task._dump_outputs_backup(print, "test-stdout", "test-stderr")
                self.assertFalse(v)

    def testCmakePluginDumpOutputsBackup2(self):

        test_stdout_fn = path_utils.concat_path(self.output_backup_storage, "cmake_plugin_output_backup_test_timestamp.txt")
        test_stderr_fn = path_utils.concat_path(self.output_backup_storage, "cmake_plugin_error_output_backup_test_timestamp.txt")

        self.assertFalse(os.path.exists(test_stdout_fn))
        self.assertFalse(os.path.exists(test_stderr_fn))

        with open(test_stdout_fn, "w") as f:
            f.write("contents")

        self.assertTrue(os.path.exists(test_stdout_fn))

        with mock.patch("mvtools_envvars.mvtools_envvar_read_temp_path", return_value=(True, self.output_backup_storage)) as dummy1:
            with mock.patch("maketimestamp.get_timestamp_now_compact", return_value="test_timestamp") as dummy2:
                v, r = self.cmake_task._dump_outputs_backup(print, "test-stdout", "test-stderr")
                self.assertFalse(v)

    def testCmakePluginDumpOutputsBackup3(self):

        test_stdout_fn = path_utils.concat_path(self.output_backup_storage, "cmake_plugin_output_backup_test_timestamp.txt")
        test_stderr_fn = path_utils.concat_path(self.output_backup_storage, "cmake_plugin_error_output_backup_test_timestamp.txt")

        self.assertFalse(os.path.exists(test_stdout_fn))
        self.assertFalse(os.path.exists(test_stderr_fn))

        with open(test_stderr_fn, "w") as f:
            f.write("contents")

        self.assertTrue(os.path.exists(test_stderr_fn))

        with mock.patch("mvtools_envvars.mvtools_envvar_read_temp_path", return_value=(True, self.output_backup_storage)) as dummy1:
            with mock.patch("maketimestamp.get_timestamp_now_compact", return_value="test_timestamp") as dummy2:
                v, r = self.cmake_task._dump_outputs_backup(print, "test-stdout", "test-stderr")
                self.assertFalse(v)

    def testCmakePluginDumpOutputsBackup4(self):

        test_stdout_fn = path_utils.concat_path(self.output_backup_storage, "cmake_plugin_output_backup_test_timestamp.txt")
        test_stderr_fn = path_utils.concat_path(self.output_backup_storage, "cmake_plugin_error_output_backup_test_timestamp.txt")

        self.assertFalse(os.path.exists(test_stdout_fn))
        self.assertFalse(os.path.exists(test_stderr_fn))

        with mock.patch("mvtools_envvars.mvtools_envvar_read_temp_path", return_value=(True, self.output_backup_storage)) as dummy1:
            with mock.patch("maketimestamp.get_timestamp_now_compact", return_value="test_timestamp") as dummy2:
                v, r = self.cmake_task._dump_outputs_backup(print, "test-stdout", "test-stderr")
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

    def testCmakePluginRunTask1(self):

        local_params = {}
        local_params["cmake_path"] = "dummy_value1"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        local_params["gen_type"] = "dummy_value4"
        self.cmake_task.params = local_params

        with mock.patch("cmake_lib.configure_and_generate", return_value=(False, (True, "test1", "test2"))) as dummy1:
            with mock.patch("cmake_plugin.CustomTask._dump_output") as dummy2:
                with mock.patch("cmake_plugin.CustomTask._dump_outputs_backup", return_value=(True, None)) as dummy3:

                    v, r = self.cmake_task.run_task(print, "exe_name")
                    self.assertFalse(v)
                    dummy1.assert_called_with("dummy_value1", self.existent_path1, self.existent_path2, "dummy_value4", {})
                    dummy2.assert_not_called()
                    dummy3.assert_not_called()

    def testCmakePluginRunTask2(self):

        local_params = {}
        local_params["cmake_path"] = "dummy_value1"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        local_params["gen_type"] = "dummy_value4"
        self.cmake_task.params = local_params

        with mock.patch("cmake_lib.configure_and_generate", return_value=(True, (False, "test1", "test2"))) as dummy1:
            with mock.patch("cmake_plugin.CustomTask._dump_output") as dummy2:
                with mock.patch("cmake_plugin.CustomTask._dump_outputs_backup", return_value=(True, None)) as dummy3:

                    v, r = self.cmake_task.run_task(print, "exe_name")
                    self.assertTrue(v)
                    self.assertEqual(r, "test2")
                    dummy1.assert_called_with("dummy_value1", self.existent_path1, self.existent_path2, "dummy_value4", {})
                    dummy2.assert_has_calls([call(print, "output", None, "test1"), call(print, "error output", None, "test2")])
                    dummy3.assert_called_with(print, "test1", "test2")

    def testCmakePluginRunTask3(self):

        local_params = {}
        local_params["cmake_path"] = "dummy_value1"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        local_params["gen_type"] = "dummy_value4"
        self.cmake_task.params = local_params

        with mock.patch("cmake_lib.configure_and_generate", return_value=(True, (False, "test1", "test2"))) as dummy1:
            with mock.patch("cmake_plugin.CustomTask._dump_output") as dummy2:
                with mock.patch("cmake_plugin.CustomTask._dump_outputs_backup", return_value=(False, "test-warning-msg")) as dummy3:

                    v, r = self.cmake_task.run_task(print, "exe_name")
                    self.assertTrue(v)
                    self.assertEqual(r, "test-warning-msg%stest2" % os.linesep)
                    dummy1.assert_called_with("dummy_value1", self.existent_path1, self.existent_path2, "dummy_value4", {})
                    dummy2.assert_has_calls([call(print, "output", None, "test1"), call(print, "error output", None, "test2")])
                    dummy3.assert_called_with(print, "test1", "test2")

    def testCmakePluginRunTask4(self):

        local_params = {}
        local_params["cmake_path"] = "dummy_value1"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        local_params["gen_type"] = "dummy_value4"
        local_params["suppress_stderr_warnings"] = "dummy_value5"
        self.cmake_task.params = local_params

        with mock.patch("cmake_lib.configure_and_generate", return_value=(True, (False, "test1", "test2"))) as dummy1:
            with mock.patch("cmake_plugin.CustomTask._dump_output") as dummy2:
                with mock.patch("cmake_plugin.CustomTask._dump_outputs_backup", return_value=(False, "test-warning-msg")) as dummy3:

                    v, r = self.cmake_task.run_task(print, "exe_name")
                    self.assertTrue(v)
                    self.assertEqual(r, "test-warning-msg")
                    dummy1.assert_called_with("dummy_value1", self.existent_path1, self.existent_path2, "dummy_value4", {})
                    dummy2.assert_has_calls([call(print, "output", None, "test1"), call(print, "error output", None, "test2")])
                    dummy3.assert_called_with(print, "test1", "test2")

    def testCmakePluginRunTask5(self):

        local_params = {}
        local_params["cmake_path"] = "dummy_value1"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        local_params["gen_type"] = "dummy_value4"
        self.cmake_task.params = local_params

        with mock.patch("cmake_lib.configure_and_generate", return_value=(True, (True, "test1", "test2"))) as dummy1:
            with mock.patch("cmake_plugin.CustomTask._dump_output") as dummy2:
                with mock.patch("cmake_plugin.CustomTask._dump_outputs_backup", return_value=(True, None)) as dummy3:

                    v, r = self.cmake_task.run_task(print, "exe_name")
                    self.assertTrue(v)
                    dummy1.assert_called_with("dummy_value1", self.existent_path1, self.existent_path2, "dummy_value4", {})
                    dummy2.assert_has_calls([call(print, "output", None, "test1"), call(print, "error output", None, "test2")])
                    dummy3.assert_not_called()

    def testCmakePluginRunTask6(self):

        local_params = {}
        local_params["cmake_path"] = "dummy_value1"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        local_params["gen_type"] = "dummy_value4"
        local_params["save_output"] = "dummy_value5"
        local_params["save_error_output"] = "dummy_value6"
        self.cmake_task.params = local_params

        with mock.patch("cmake_lib.configure_and_generate", return_value=(True, (True, "test1", "test2"))) as dummy1:
            with mock.patch("cmake_plugin.CustomTask._dump_output") as dummy2:
                with mock.patch("cmake_plugin.CustomTask._dump_outputs_backup", return_value=(True, None)) as dummy3:

                    v, r = self.cmake_task.run_task(print, "exe_name")
                    self.assertTrue(v)
                    dummy1.assert_called_with("dummy_value1", self.existent_path1, self.existent_path2, "dummy_value4", {})
                    dummy2.assert_has_calls([call(print, "output", "dummy_value5", "test1"), call(print, "error output", "dummy_value6", "test2")])
                    dummy3.assert_not_called()

if __name__ == '__main__':
    unittest.main()
