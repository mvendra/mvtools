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

        # existent path 3
        self.existent_path3 = path_utils.concat_path(self.test_dir, "existent_path3")
        os.mkdir(self.existent_path3)

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

    def testCmakePluginReadParams1(self):

        local_params = {}
        local_params["source_path"] = self.existent_path1
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertFalse(v)

    def testCmakePluginReadParams2(self):

        local_params = {}
        local_params["operation"] = "cfg-and-gen"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertFalse(v)

    def testCmakePluginReadParams3(self):

        local_params = {}
        local_params["operation"] = "ext-opts"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertFalse(v)

    def testCmakePluginReadParams4(self):

        local_params = {}
        local_params["operation"] = "build"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertFalse(v)

    def testCmakePluginReadParams5(self):

        local_params = {}
        local_params["operation"] = "install"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertFalse(v)

    def testCmakePluginReadParams6(self):

        local_params = {}
        local_params["operation"] = "cfg-and-gen"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        local_params["gen_type"] = "dummy_value1"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("cfg-and-gen", self.existent_path1, self.existent_path2, "dummy_value1", None, None, None, None, None, None, None, None, None, False, False) )

    def testCmakePluginReadParams7(self):

        local_params = {}
        local_params["operation"] = "cfg-and-gen"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        local_params["gen_type"] = "dummy_value1"
        local_params["temp_path"] = "dummy_value2"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("cfg-and-gen", self.existent_path1, self.existent_path2, "dummy_value1", "dummy_value2", None, None, None, None, None, None, None, None, False, False) )

    def testCmakePluginReadParams8(self):

        local_params = {}
        local_params["operation"] = "cfg-and-gen"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        local_params["gen_type"] = "dummy_value1"
        local_params["temp_path"] = "dummy_value2"
        local_params["cmake_path"] = "dummy_value3"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("cfg-and-gen", self.existent_path1, self.existent_path2, "dummy_value1", "dummy_value2", "dummy_value3", None, None, None, None, None, None, None, False, False) )

    def testCmakePluginReadParams9(self):

        local_params = {}
        local_params["operation"] = "cfg-and-gen"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        local_params["gen_type"] = "dummy_value1"
        local_params["temp_path"] = "dummy_value2"
        local_params["cmake_path"] = "dummy_value3"
        local_params["build_type"] = "dummy_value4"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("cfg-and-gen", self.existent_path1, self.existent_path2, "dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4", None, None, None, None, None, None, False, False) )

    def testCmakePluginReadParams10(self):

        local_params = {}
        local_params["operation"] = "cfg-and-gen"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        local_params["gen_type"] = "dummy_value1"
        local_params["temp_path"] = "dummy_value2"
        local_params["cmake_path"] = "dummy_value3"
        local_params["build_type"] = "dummy_value4"
        local_params["install_prefix"] = "dummy_value5"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("cfg-and-gen", self.existent_path1, self.existent_path2, "dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4", "dummy_value5", None, None, None, None, None, False, False) )

    def testCmakePluginReadParams11(self):

        local_params = {}
        local_params["operation"] = "cfg-and-gen"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        local_params["gen_type"] = "dummy_value1"
        local_params["temp_path"] = "dummy_value2"
        local_params["cmake_path"] = "dummy_value3"
        local_params["build_type"] = "dummy_value4"
        local_params["install_prefix"] = "dummy_value5"
        local_params["prefix_path"] = "dummy_value6"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("cfg-and-gen", self.existent_path1, self.existent_path2, "dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4", "dummy_value5", "dummy_value6", None, None, None, None, False, False) )

    def testCmakePluginReadParams12(self):

        local_params = {}
        local_params["operation"] = "cfg-and-gen"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        local_params["gen_type"] = "dummy_value1"
        local_params["temp_path"] = "dummy_value2"
        local_params["cmake_path"] = "dummy_value3"
        local_params["build_type"] = "dummy_value4"
        local_params["install_prefix"] = "dummy_value5"
        local_params["prefix_path"] = "dummy_value6"
        local_params["toolchain"] = "dummy_value7"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("cfg-and-gen", self.existent_path1, self.existent_path2, "dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4", "dummy_value5", "dummy_value6", "dummy_value7", None, None, None, False, False) )

    def testCmakePluginReadParams13(self):

        local_params = {}
        local_params["operation"] = "cfg-and-gen"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        local_params["gen_type"] = "dummy_value1"
        local_params["temp_path"] = "dummy_value2"
        local_params["cmake_path"] = "dummy_value3"
        local_params["build_type"] = "dummy_value4"
        local_params["install_prefix"] = "dummy_value5"
        local_params["prefix_path"] = "dummy_value6"
        local_params["toolchain"] = "dummy_value7"
        local_params["option"] = "dummy_value8"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("cfg-and-gen", self.existent_path1, self.existent_path2, "dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4", "dummy_value5", "dummy_value6", "dummy_value7", ["dummy_value8"], None, None, False, False) )

    def testCmakePluginReadParams14(self):

        local_params = {}
        local_params["operation"] = "cfg-and-gen"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        local_params["gen_type"] = "dummy_value1"
        local_params["temp_path"] = "dummy_value2"
        local_params["cmake_path"] = "dummy_value3"
        local_params["build_type"] = "dummy_value4"
        local_params["install_prefix"] = "dummy_value5"
        local_params["prefix_path"] = "dummy_value6"
        local_params["toolchain"] = "dummy_value7"
        local_params["option"] = ["dummy_value8", "dummy_value9"]
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("cfg-and-gen", self.existent_path1, self.existent_path2, "dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4", "dummy_value5", "dummy_value6", "dummy_value7", ["dummy_value8", "dummy_value9"], None, None, False, False) )

    def testCmakePluginReadParams15(self):

        local_params = {}
        local_params["operation"] = "cfg-and-gen"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        local_params["gen_type"] = "dummy_value1"
        local_params["temp_path"] = "dummy_value2"
        local_params["cmake_path"] = "dummy_value3"
        local_params["build_type"] = "dummy_value4"
        local_params["install_prefix"] = "dummy_value5"
        local_params["prefix_path"] = "dummy_value6"
        local_params["toolchain"] = "dummy_value7"
        local_params["option"] = ["dummy_value8", "dummy_value9"]
        local_params["save_output"] = "dummy_value10"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("cfg-and-gen", self.existent_path1, self.existent_path2, "dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4", "dummy_value5", "dummy_value6", "dummy_value7", ["dummy_value8", "dummy_value9"], "dummy_value10", None, False, False) )

    def testCmakePluginReadParams16(self):

        local_params = {}
        local_params["operation"] = "cfg-and-gen"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        local_params["gen_type"] = "dummy_value1"
        local_params["temp_path"] = "dummy_value2"
        local_params["cmake_path"] = "dummy_value3"
        local_params["build_type"] = "dummy_value4"
        local_params["install_prefix"] = "dummy_value5"
        local_params["prefix_path"] = "dummy_value6"
        local_params["toolchain"] = "dummy_value7"
        local_params["option"] = ["dummy_value8", "dummy_value9"]
        local_params["save_output"] = "dummy_value10"
        local_params["save_error_output"] = "dummy_value11"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("cfg-and-gen", self.existent_path1, self.existent_path2, "dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4", "dummy_value5", "dummy_value6", "dummy_value7", ["dummy_value8", "dummy_value9"], "dummy_value10", "dummy_value11", False, False) )

    def testCmakePluginReadParams17(self):

        local_params = {}
        local_params["operation"] = "cfg-and-gen"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        local_params["gen_type"] = "dummy_value1"
        local_params["temp_path"] = "dummy_value2"
        local_params["cmake_path"] = "dummy_value3"
        local_params["build_type"] = "dummy_value4"
        local_params["install_prefix"] = "dummy_value5"
        local_params["prefix_path"] = "dummy_value6"
        local_params["toolchain"] = "dummy_value7"
        local_params["option"] = ["dummy_value8", "dummy_value9"]
        local_params["save_output"] = "dummy_value10"
        local_params["save_error_output"] = "dummy_value11"
        local_params["suppress_stderr_warnings"] = "dummy_value12"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("cfg-and-gen", self.existent_path1, self.existent_path2, "dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4", "dummy_value5", "dummy_value6", "dummy_value7", ["dummy_value8", "dummy_value9"], "dummy_value10", "dummy_value11", True, False) )

    def testCmakePluginReadParams18(self):

        local_params = {}
        local_params["operation"] = "cfg-and-gen"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        local_params["gen_type"] = "dummy_value1"
        local_params["temp_path"] = "dummy_value2"
        local_params["cmake_path"] = "dummy_value3"
        local_params["build_type"] = "dummy_value4"
        local_params["install_prefix"] = "dummy_value5"
        local_params["prefix_path"] = "dummy_value6"
        local_params["toolchain"] = "dummy_value7"
        local_params["option"] = ["dummy_value8", "dummy_value9"]
        local_params["save_output"] = "dummy_value10"
        local_params["save_error_output"] = "dummy_value11"
        local_params["suppress_stderr_warnings"] = "dummy_value12"
        local_params["parallel"] = "dummy_value13"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("cfg-and-gen", self.existent_path1, self.existent_path2, "dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4", "dummy_value5", "dummy_value6", "dummy_value7", ["dummy_value8", "dummy_value9"], "dummy_value10", "dummy_value11", True, True) )

    def testCmakePluginReadParams19(self):

        local_params = {}
        local_params["operation"] = "ext-opts"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.nonexistent_path1
        local_params["temp_path"] = "dummy_value1"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("ext-opts", self.existent_path1, self.nonexistent_path1, None, "dummy_value1", None, None, None, None, None, None, None, None, False, False) )

    def testCmakePluginReadParams20(self):

        local_params = {}
        local_params["operation"] = "ext-opts"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.nonexistent_path1
        local_params["gen_type"] = "dummy_value1"
        local_params["temp_path"] = "dummy_value2"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("ext-opts", self.existent_path1, self.nonexistent_path1, "dummy_value1", "dummy_value2", None, None, None, None, None, None, None, None, False, False) )

    def testCmakePluginReadParams21(self):

        local_params = {}
        local_params["operation"] = "ext-opts"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.nonexistent_path1
        local_params["gen_type"] = "dummy_value1"
        local_params["temp_path"] = "dummy_value2"
        local_params["cmake_path"] = "dummy_value3"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("ext-opts", self.existent_path1, self.nonexistent_path1, "dummy_value1", "dummy_value2", "dummy_value3", None, None, None, None, None, None, None, False, False) )

    def testCmakePluginReadParams22(self):

        local_params = {}
        local_params["operation"] = "ext-opts"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.nonexistent_path1
        local_params["gen_type"] = "dummy_value1"
        local_params["temp_path"] = "dummy_value2"
        local_params["cmake_path"] = "dummy_value3"
        local_params["build_type"] = "dummy_value4"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("ext-opts", self.existent_path1, self.nonexistent_path1, "dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4", None, None, None, None, None, None, False, False) )

    def testCmakePluginReadParams23(self):

        local_params = {}
        local_params["operation"] = "ext-opts"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.nonexistent_path1
        local_params["gen_type"] = "dummy_value1"
        local_params["temp_path"] = "dummy_value2"
        local_params["cmake_path"] = "dummy_value3"
        local_params["build_type"] = "dummy_value4"
        local_params["install_prefix"] = "dummy_value5"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("ext-opts", self.existent_path1, self.nonexistent_path1, "dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4", "dummy_value5", None, None, None, None, None, False, False) )

    def testCmakePluginReadParams24(self):

        local_params = {}
        local_params["operation"] = "ext-opts"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.nonexistent_path1
        local_params["gen_type"] = "dummy_value1"
        local_params["temp_path"] = "dummy_value2"
        local_params["cmake_path"] = "dummy_value3"
        local_params["build_type"] = "dummy_value4"
        local_params["install_prefix"] = "dummy_value5"
        local_params["prefix_path"] = "dummy_value6"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("ext-opts", self.existent_path1, self.nonexistent_path1, "dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4", "dummy_value5", "dummy_value6", None, None, None, None, False, False) )

    def testCmakePluginReadParams25(self):

        local_params = {}
        local_params["operation"] = "ext-opts"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.nonexistent_path1
        local_params["gen_type"] = "dummy_value1"
        local_params["temp_path"] = "dummy_value2"
        local_params["cmake_path"] = "dummy_value3"
        local_params["build_type"] = "dummy_value4"
        local_params["install_prefix"] = "dummy_value5"
        local_params["prefix_path"] = "dummy_value6"
        local_params["toolchain"] = "dummy_value7"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("ext-opts", self.existent_path1, self.nonexistent_path1, "dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4", "dummy_value5", "dummy_value6", "dummy_value7", None, None, None, False, False) )

    def testCmakePluginReadParams26(self):

        local_params = {}
        local_params["operation"] = "ext-opts"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.nonexistent_path1
        local_params["gen_type"] = "dummy_value1"
        local_params["temp_path"] = "dummy_value2"
        local_params["cmake_path"] = "dummy_value3"
        local_params["build_type"] = "dummy_value4"
        local_params["install_prefix"] = "dummy_value5"
        local_params["prefix_path"] = "dummy_value6"
        local_params["toolchain"] = "dummy_value7"
        local_params["option"] = "dummy_value8"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("ext-opts", self.existent_path1, self.nonexistent_path1, "dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4", "dummy_value5", "dummy_value6", "dummy_value7", ["dummy_value8"], None, None, False, False) )

    def testCmakePluginReadParams27(self):

        local_params = {}
        local_params["operation"] = "ext-opts"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.nonexistent_path1
        local_params["gen_type"] = "dummy_value1"
        local_params["temp_path"] = "dummy_value2"
        local_params["cmake_path"] = "dummy_value3"
        local_params["build_type"] = "dummy_value4"
        local_params["install_prefix"] = "dummy_value5"
        local_params["prefix_path"] = "dummy_value6"
        local_params["toolchain"] = "dummy_value7"
        local_params["option"] = ["dummy_value8", "dummy_value9"]
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("ext-opts", self.existent_path1, self.nonexistent_path1, "dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4", "dummy_value5", "dummy_value6", "dummy_value7", ["dummy_value8", "dummy_value9"], None, None, False, False) )

    def testCmakePluginReadParams28(self):

        local_params = {}
        local_params["operation"] = "ext-opts"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.nonexistent_path1
        local_params["gen_type"] = "dummy_value1"
        local_params["temp_path"] = "dummy_value2"
        local_params["cmake_path"] = "dummy_value3"
        local_params["build_type"] = "dummy_value4"
        local_params["install_prefix"] = "dummy_value5"
        local_params["prefix_path"] = "dummy_value6"
        local_params["toolchain"] = "dummy_value7"
        local_params["option"] = ["dummy_value8", "dummy_value9"]
        local_params["save_output"] = "dummy_value10"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("ext-opts", self.existent_path1, self.nonexistent_path1, "dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4", "dummy_value5", "dummy_value6", "dummy_value7", ["dummy_value8", "dummy_value9"], "dummy_value10", None, False, False) )

    def testCmakePluginReadParams29(self):

        local_params = {}
        local_params["operation"] = "ext-opts"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.nonexistent_path1
        local_params["gen_type"] = "dummy_value1"
        local_params["temp_path"] = "dummy_value2"
        local_params["cmake_path"] = "dummy_value3"
        local_params["build_type"] = "dummy_value4"
        local_params["install_prefix"] = "dummy_value5"
        local_params["prefix_path"] = "dummy_value6"
        local_params["toolchain"] = "dummy_value7"
        local_params["option"] = ["dummy_value8", "dummy_value9"]
        local_params["save_output"] = "dummy_value10"
        local_params["save_error_output"] = "dummy_value11"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("ext-opts", self.existent_path1, self.nonexistent_path1, "dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4", "dummy_value5", "dummy_value6", "dummy_value7", ["dummy_value8", "dummy_value9"], "dummy_value10", "dummy_value11", False, False) )

    def testCmakePluginReadParams30(self):

        local_params = {}
        local_params["operation"] = "ext-opts"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.nonexistent_path1
        local_params["gen_type"] = "dummy_value1"
        local_params["temp_path"] = "dummy_value2"
        local_params["cmake_path"] = "dummy_value3"
        local_params["build_type"] = "dummy_value4"
        local_params["install_prefix"] = "dummy_value5"
        local_params["prefix_path"] = "dummy_value6"
        local_params["toolchain"] = "dummy_value7"
        local_params["option"] = ["dummy_value8", "dummy_value9"]
        local_params["save_output"] = "dummy_value10"
        local_params["save_error_output"] = "dummy_value11"
        local_params["suppress_stderr_warnings"] = "dummy_value12"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("ext-opts", self.existent_path1, self.nonexistent_path1, "dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4", "dummy_value5", "dummy_value6", "dummy_value7", ["dummy_value8", "dummy_value9"], "dummy_value10", "dummy_value11", True, False) )

    def testCmakePluginReadParams31(self):

        local_params = {}
        local_params["operation"] = "ext-opts"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.nonexistent_path1
        local_params["gen_type"] = "dummy_value1"
        local_params["temp_path"] = "dummy_value2"
        local_params["cmake_path"] = "dummy_value3"
        local_params["build_type"] = "dummy_value4"
        local_params["install_prefix"] = "dummy_value5"
        local_params["prefix_path"] = "dummy_value6"
        local_params["toolchain"] = "dummy_value7"
        local_params["option"] = ["dummy_value8", "dummy_value9"]
        local_params["save_output"] = "dummy_value10"
        local_params["save_error_output"] = "dummy_value11"
        local_params["suppress_stderr_warnings"] = "dummy_value12"
        local_params["parallel"] = "dummy_value13"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("ext-opts", self.existent_path1, self.nonexistent_path1, "dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4", "dummy_value5", "dummy_value6", "dummy_value7", ["dummy_value8", "dummy_value9"], "dummy_value10", "dummy_value11", True, True) )

    def testCmakePluginReadParams32(self):

        local_params = {}
        local_params["operation"] = "build"
        local_params["source_path"] = self.existent_path1
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("build", self.existent_path1, None, None, None, None, None, None, None, None, None, None, None, False, False) )

    def testCmakePluginReadParams33(self):

        local_params = {}
        local_params["operation"] = "build"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = "dummy_value1"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("build", self.existent_path1, "dummy_value1", None, None, None, None, None, None, None, None, None, None, False, False) )

    def testCmakePluginReadParams34(self):

        local_params = {}
        local_params["operation"] = "build"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = "dummy_value1"
        local_params["gen_type"] = "dummy_value2"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("build", self.existent_path1, "dummy_value1", "dummy_value2", None, None, None, None, None, None, None, None, None, False, False) )

    def testCmakePluginReadParams35(self):

        local_params = {}
        local_params["operation"] = "build"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = "dummy_value1"
        local_params["gen_type"] = "dummy_value2"
        local_params["temp_path"] = "dummy_value3"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("build", self.existent_path1, "dummy_value1", "dummy_value2", "dummy_value3", None, None, None, None, None, None, None, None, False, False) )

    def testCmakePluginReadParams36(self):

        local_params = {}
        local_params["operation"] = "build"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = "dummy_value1"
        local_params["gen_type"] = "dummy_value2"
        local_params["temp_path"] = "dummy_value3"
        local_params["cmake_path"] = "dummy_value4"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("build", self.existent_path1, "dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4", None, None, None, None, None, None, None, False, False) )

    def testCmakePluginReadParams37(self):

        local_params = {}
        local_params["operation"] = "build"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = "dummy_value1"
        local_params["gen_type"] = "dummy_value2"
        local_params["temp_path"] = "dummy_value3"
        local_params["cmake_path"] = "dummy_value4"
        local_params["build_type"] = "dummy_value5"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("build", self.existent_path1, "dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4", "dummy_value5", None, None, None, None, None, None, False, False) )

    def testCmakePluginReadParams38(self):

        local_params = {}
        local_params["operation"] = "build"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = "dummy_value1"
        local_params["gen_type"] = "dummy_value2"
        local_params["temp_path"] = "dummy_value3"
        local_params["cmake_path"] = "dummy_value4"
        local_params["build_type"] = "dummy_value5"
        local_params["install_prefix"] = "dummy_value6"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("build", self.existent_path1, "dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4", "dummy_value5", "dummy_value6", None, None, None, None, None, False, False) )

    def testCmakePluginReadParams39(self):

        local_params = {}
        local_params["operation"] = "build"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = "dummy_value1"
        local_params["gen_type"] = "dummy_value2"
        local_params["temp_path"] = "dummy_value3"
        local_params["cmake_path"] = "dummy_value4"
        local_params["build_type"] = "dummy_value5"
        local_params["install_prefix"] = "dummy_value6"
        local_params["prefix_path"] = "dummy_value7"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("build", self.existent_path1, "dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4", "dummy_value5", "dummy_value6", "dummy_value7", None, None, None, None, False, False) )

    def testCmakePluginReadParams40(self):

        local_params = {}
        local_params["operation"] = "build"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = "dummy_value1"
        local_params["gen_type"] = "dummy_value2"
        local_params["temp_path"] = "dummy_value3"
        local_params["cmake_path"] = "dummy_value4"
        local_params["build_type"] = "dummy_value5"
        local_params["install_prefix"] = "dummy_value6"
        local_params["prefix_path"] = "dummy_value7"
        local_params["toolchain"] = "dummy_value8"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("build", self.existent_path1, "dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4", "dummy_value5", "dummy_value6", "dummy_value7", "dummy_value8", None, None, None, False, False) )

    def testCmakePluginReadParams41(self):

        local_params = {}
        local_params["operation"] = "build"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = "dummy_value1"
        local_params["gen_type"] = "dummy_value2"
        local_params["temp_path"] = "dummy_value3"
        local_params["cmake_path"] = "dummy_value4"
        local_params["build_type"] = "dummy_value5"
        local_params["install_prefix"] = "dummy_value6"
        local_params["prefix_path"] = "dummy_value7"
        local_params["toolchain"] = "dummy_value8"
        local_params["option"] = "dummy_value9"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("build", self.existent_path1, "dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4", "dummy_value5", "dummy_value6", "dummy_value7", "dummy_value8", ["dummy_value9"], None, None, False, False) )

    def testCmakePluginReadParams42(self):

        local_params = {}
        local_params["operation"] = "build"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = "dummy_value1"
        local_params["gen_type"] = "dummy_value2"
        local_params["temp_path"] = "dummy_value3"
        local_params["cmake_path"] = "dummy_value4"
        local_params["build_type"] = "dummy_value5"
        local_params["install_prefix"] = "dummy_value6"
        local_params["prefix_path"] = "dummy_value7"
        local_params["toolchain"] = "dummy_value8"
        local_params["option"] = ["dummy_value9", "dummy_value10"]
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("build", self.existent_path1, "dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4", "dummy_value5", "dummy_value6", "dummy_value7", "dummy_value8", ["dummy_value9", "dummy_value10"], None, None, False, False) )

    def testCmakePluginReadParams43(self):

        local_params = {}
        local_params["operation"] = "build"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = "dummy_value1"
        local_params["gen_type"] = "dummy_value2"
        local_params["temp_path"] = "dummy_value3"
        local_params["cmake_path"] = "dummy_value4"
        local_params["build_type"] = "dummy_value5"
        local_params["install_prefix"] = "dummy_value6"
        local_params["prefix_path"] = "dummy_value7"
        local_params["toolchain"] = "dummy_value8"
        local_params["option"] = ["dummy_value9", "dummy_value10"]
        local_params["save_output"] = "dummy_value11"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("build", self.existent_path1, "dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4", "dummy_value5", "dummy_value6", "dummy_value7", "dummy_value8", ["dummy_value9", "dummy_value10"], "dummy_value11", None, False, False) )

    def testCmakePluginReadParams44(self):

        local_params = {}
        local_params["operation"] = "build"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = "dummy_value1"
        local_params["gen_type"] = "dummy_value2"
        local_params["temp_path"] = "dummy_value3"
        local_params["cmake_path"] = "dummy_value4"
        local_params["build_type"] = "dummy_value5"
        local_params["install_prefix"] = "dummy_value6"
        local_params["prefix_path"] = "dummy_value7"
        local_params["toolchain"] = "dummy_value8"
        local_params["option"] = ["dummy_value9", "dummy_value10"]
        local_params["save_output"] = "dummy_value11"
        local_params["save_error_output"] = "dummy_value12"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("build", self.existent_path1, "dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4", "dummy_value5", "dummy_value6", "dummy_value7", "dummy_value8", ["dummy_value9", "dummy_value10"], "dummy_value11", "dummy_value12", False, False) )

    def testCmakePluginReadParams45(self):

        local_params = {}
        local_params["operation"] = "build"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = "dummy_value1"
        local_params["gen_type"] = "dummy_value2"
        local_params["temp_path"] = "dummy_value3"
        local_params["cmake_path"] = "dummy_value4"
        local_params["build_type"] = "dummy_value5"
        local_params["install_prefix"] = "dummy_value6"
        local_params["prefix_path"] = "dummy_value7"
        local_params["toolchain"] = "dummy_value8"
        local_params["option"] = ["dummy_value9", "dummy_value10"]
        local_params["save_output"] = "dummy_value11"
        local_params["save_error_output"] = "dummy_value12"
        local_params["suppress_stderr_warnings"] = "dummy_value13"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("build", self.existent_path1, "dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4", "dummy_value5", "dummy_value6", "dummy_value7", "dummy_value8", ["dummy_value9", "dummy_value10"], "dummy_value11", "dummy_value12", True, False) )

    def testCmakePluginReadParams46(self):

        local_params = {}
        local_params["operation"] = "build"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = "dummy_value1"
        local_params["gen_type"] = "dummy_value2"
        local_params["temp_path"] = "dummy_value3"
        local_params["cmake_path"] = "dummy_value4"
        local_params["build_type"] = "dummy_value5"
        local_params["install_prefix"] = "dummy_value6"
        local_params["prefix_path"] = "dummy_value7"
        local_params["toolchain"] = "dummy_value8"
        local_params["option"] = ["dummy_value9", "dummy_value10"]
        local_params["save_output"] = "dummy_value11"
        local_params["save_error_output"] = "dummy_value12"
        local_params["suppress_stderr_warnings"] = "dummy_value13"
        local_params["parallel"] = "dummy_value14"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("build", self.existent_path1, "dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4", "dummy_value5", "dummy_value6", "dummy_value7", "dummy_value8", ["dummy_value9", "dummy_value10"], "dummy_value11", "dummy_value12", True, True) )

    def testCmakePluginReadParams47(self):

        local_params = {}
        local_params["operation"] = "install"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("install", self.existent_path1, self.existent_path2, None, None, None, None, None, None, None, None, None, None, False, False) )

    def testCmakePluginReadParams48(self):

        local_params = {}
        local_params["operation"] = "install"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        local_params["gen_type"] = "dummy_value1"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("install", self.existent_path1, self.existent_path2, "dummy_value1", None, None, None, None, None, None, None, None, None, False, False) )

    def testCmakePluginReadParams49(self):

        local_params = {}
        local_params["operation"] = "install"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        local_params["gen_type"] = "dummy_value1"
        local_params["temp_path"] = "dummy_value2"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("install", self.existent_path1, self.existent_path2, "dummy_value1", "dummy_value2", None, None, None, None, None, None, None, None, False, False) )

    def testCmakePluginReadParams50(self):

        local_params = {}
        local_params["operation"] = "install"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        local_params["gen_type"] = "dummy_value1"
        local_params["temp_path"] = "dummy_value2"
        local_params["cmake_path"] = "dummy_value3"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("install", self.existent_path1, self.existent_path2, "dummy_value1", "dummy_value2", "dummy_value3", None, None, None, None, None, None, None, False, False) )

    def testCmakePluginReadParams51(self):

        local_params = {}
        local_params["operation"] = "install"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        local_params["gen_type"] = "dummy_value1"
        local_params["temp_path"] = "dummy_value2"
        local_params["cmake_path"] = "dummy_value3"
        local_params["build_type"] = "dummy_value4"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("install", self.existent_path1, self.existent_path2, "dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4", None, None, None, None, None, None, False, False) )

    def testCmakePluginReadParams52(self):

        local_params = {}
        local_params["operation"] = "install"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        local_params["gen_type"] = "dummy_value1"
        local_params["temp_path"] = "dummy_value2"
        local_params["cmake_path"] = "dummy_value3"
        local_params["build_type"] = "dummy_value4"
        local_params["install_prefix"] = "dummy_value5"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("install", self.existent_path1, self.existent_path2, "dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4", "dummy_value5", None, None, None, None, None, False, False) )

    def testCmakePluginReadParams53(self):

        local_params = {}
        local_params["operation"] = "install"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        local_params["gen_type"] = "dummy_value1"
        local_params["temp_path"] = "dummy_value2"
        local_params["cmake_path"] = "dummy_value3"
        local_params["build_type"] = "dummy_value4"
        local_params["install_prefix"] = "dummy_value5"
        local_params["prefix_path"] = "dummy_value6"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("install", self.existent_path1, self.existent_path2, "dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4", "dummy_value5", "dummy_value6", None, None, None, None, False, False) )

    def testCmakePluginReadParams54(self):

        local_params = {}
        local_params["operation"] = "install"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        local_params["gen_type"] = "dummy_value1"
        local_params["temp_path"] = "dummy_value2"
        local_params["cmake_path"] = "dummy_value3"
        local_params["build_type"] = "dummy_value4"
        local_params["install_prefix"] = "dummy_value5"
        local_params["prefix_path"] = "dummy_value6"
        local_params["toolchain"] = "dummy_value7"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("install", self.existent_path1, self.existent_path2, "dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4", "dummy_value5", "dummy_value6", "dummy_value7", None, None, None, False, False) )

    def testCmakePluginReadParams55(self):

        local_params = {}
        local_params["operation"] = "install"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        local_params["gen_type"] = "dummy_value1"
        local_params["temp_path"] = "dummy_value2"
        local_params["cmake_path"] = "dummy_value3"
        local_params["build_type"] = "dummy_value4"
        local_params["install_prefix"] = "dummy_value5"
        local_params["prefix_path"] = "dummy_value6"
        local_params["toolchain"] = "dummy_value7"
        local_params["option"] = "dummy_value8"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("install", self.existent_path1, self.existent_path2, "dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4", "dummy_value5", "dummy_value6", "dummy_value7", ["dummy_value8"], None, None, False, False) )

    def testCmakePluginReadParams56(self):

        local_params = {}
        local_params["operation"] = "install"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        local_params["gen_type"] = "dummy_value1"
        local_params["temp_path"] = "dummy_value2"
        local_params["cmake_path"] = "dummy_value3"
        local_params["build_type"] = "dummy_value4"
        local_params["install_prefix"] = "dummy_value5"
        local_params["prefix_path"] = "dummy_value6"
        local_params["toolchain"] = "dummy_value7"
        local_params["option"] = ["dummy_value8", "dummy_value9"]
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("install", self.existent_path1, self.existent_path2, "dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4", "dummy_value5", "dummy_value6", "dummy_value7", ["dummy_value8", "dummy_value9"], None, None, False, False) )

    def testCmakePluginReadParams57(self):

        local_params = {}
        local_params["operation"] = "install"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        local_params["gen_type"] = "dummy_value1"
        local_params["temp_path"] = "dummy_value2"
        local_params["cmake_path"] = "dummy_value3"
        local_params["build_type"] = "dummy_value4"
        local_params["install_prefix"] = "dummy_value5"
        local_params["prefix_path"] = "dummy_value6"
        local_params["toolchain"] = "dummy_value7"
        local_params["option"] = ["dummy_value8", "dummy_value9"]
        local_params["save_output"] = "dummy_value10"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("install", self.existent_path1, self.existent_path2, "dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4", "dummy_value5", "dummy_value6", "dummy_value7", ["dummy_value8", "dummy_value9"], "dummy_value10", None, False, False) )

    def testCmakePluginReadParams58(self):

        local_params = {}
        local_params["operation"] = "install"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        local_params["gen_type"] = "dummy_value1"
        local_params["temp_path"] = "dummy_value2"
        local_params["cmake_path"] = "dummy_value3"
        local_params["build_type"] = "dummy_value4"
        local_params["install_prefix"] = "dummy_value5"
        local_params["prefix_path"] = "dummy_value6"
        local_params["toolchain"] = "dummy_value7"
        local_params["option"] = ["dummy_value8", "dummy_value9"]
        local_params["save_output"] = "dummy_value10"
        local_params["save_error_output"] = "dummy_value11"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("install", self.existent_path1, self.existent_path2, "dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4", "dummy_value5", "dummy_value6", "dummy_value7", ["dummy_value8", "dummy_value9"], "dummy_value10", "dummy_value11", False, False) )

    def testCmakePluginReadParams59(self):

        local_params = {}
        local_params["operation"] = "install"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        local_params["gen_type"] = "dummy_value1"
        local_params["temp_path"] = "dummy_value2"
        local_params["cmake_path"] = "dummy_value3"
        local_params["build_type"] = "dummy_value4"
        local_params["install_prefix"] = "dummy_value5"
        local_params["prefix_path"] = "dummy_value6"
        local_params["toolchain"] = "dummy_value7"
        local_params["option"] = ["dummy_value8", "dummy_value9"]
        local_params["save_output"] = "dummy_value10"
        local_params["save_error_output"] = "dummy_value11"
        local_params["suppress_stderr_warnings"] = "dummy_value12"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("install", self.existent_path1, self.existent_path2, "dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4", "dummy_value5", "dummy_value6", "dummy_value7", ["dummy_value8", "dummy_value9"], "dummy_value10", "dummy_value11", True, False) )

    def testCmakePluginReadParams60(self):

        local_params = {}
        local_params["operation"] = "install"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        local_params["gen_type"] = "dummy_value1"
        local_params["temp_path"] = "dummy_value2"
        local_params["cmake_path"] = "dummy_value3"
        local_params["build_type"] = "dummy_value4"
        local_params["install_prefix"] = "dummy_value5"
        local_params["prefix_path"] = "dummy_value6"
        local_params["toolchain"] = "dummy_value7"
        local_params["option"] = ["dummy_value8", "dummy_value9"]
        local_params["save_output"] = "dummy_value10"
        local_params["save_error_output"] = "dummy_value11"
        local_params["suppress_stderr_warnings"] = "dummy_value12"
        local_params["parallel"] = "dummy_value13"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("install", self.existent_path1, self.existent_path2, "dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4", "dummy_value5", "dummy_value6", "dummy_value7", ["dummy_value8", "dummy_value9"], "dummy_value10", "dummy_value11", True, True) )

    def testCmakePluginReadParams61(self):

        local_params = {}
        local_params["operation"] = "unknown"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertFalse(v)

    def testCmakePluginReadParams62(self):

        local_params = {}
        local_params["operation"] = "build"
        local_params["source_path"] = self.nonexistent_path1
        local_params["output_path"] = self.existent_path2
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertFalse(v)

    def testCmakePluginReadParams63(self):

        local_params = {}
        local_params["operation"] = "cfg-and-gen"
        local_params["source_path"] = self.existent_path1
        local_params["gen_type"] = "dummy_value1"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertFalse(v)

    def testCmakePluginReadParams64(self):

        local_params = {}
        local_params["operation"] = "cfg-and-gen"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertFalse(v)

    def testCmakePluginReadParams65(self):

        local_params = {}
        local_params["operation"] = "cfg-and-gen"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.nonexistent_path1
        local_params["gen_type"] = "dummy_value1"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertFalse(v)

    def testCmakePluginReadParams66(self):

        local_params = {}
        local_params["operation"] = "cfg-and-gen"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        local_params["gen_type"] = "dummy_value1"
        local_params["save_output"] = self.existent_path3
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertFalse(v)

    def testCmakePluginReadParams67(self):

        local_params = {}
        local_params["operation"] = "cfg-and-gen"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        local_params["gen_type"] = "dummy_value1"
        local_params["save_error_output"] = self.existent_path3
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertFalse(v)

    def testCmakePluginReadParams68(self):

        local_params = {}
        local_params["operation"] = "ext-opts"
        local_params["source_path"] = self.existent_path1
        local_params["temp_path"] = "dummy_value1"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertFalse(v)

    def testCmakePluginReadParams69(self):

        local_params = {}
        local_params["operation"] = "ext-opts"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.nonexistent_path1
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertFalse(v)

    def testCmakePluginReadParams70(self):

        local_params = {}
        local_params["operation"] = "ext-opts"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        local_params["temp_path"] = "dummy_value1"
        self.cmake_task.params = local_params

        v, r = self.cmake_task._read_params()
        self.assertFalse(v)

    def testCmakePluginAssembleOptions1(self):
        v, r = cmake_plugin._assemble_options(None, None, None, None, None)
        self.assertTrue(v)
        self.assertEqual(r, self.test_opts)

    def testCmakePluginAssembleOptions2(self):
        v, r = cmake_plugin._assemble_options("test1", None, None, None, None)
        self.assertFalse(v)
        self.assertEqual(r, "Invalid option value (build_type): [test1]")

    def testCmakePluginAssembleOptions3(self):
        v, r = cmake_plugin._assemble_options("release", None, None, None, None)
        self.assertTrue(v)
        self.assertEqual(r, {"CMAKE_BUILD_TYPE": ("STRING", "release")})

    def testCmakePluginAssembleOptions4(self):
        v, r = cmake_plugin._assemble_options(None, "test1", None, None, None)
        self.assertTrue(v)
        self.assertEqual(r, {"CMAKE_INSTALL_PREFIX": ("STRING", "test1")})

    def testCmakePluginAssembleOptions5(self):

        with mock.patch("cmake_lib.set_option_install_prefix", return_value=None) as dummy:
            v, r = cmake_plugin._assemble_options(None, "test1", None, None, None)
            self.assertFalse(v)
            self.assertEqual(r, "Invalid option value (install_prefix): [test1]")
            dummy.assert_called_with(cmake_lib.boot_options(), "test1")

    def testCmakePluginAssembleOptions6(self):
        v, r = cmake_plugin._assemble_options(None, None, "test1", None, None)
        self.assertTrue(v)
        self.assertEqual(r, {"CMAKE_PREFIX_PATH": ("STRING", "test1")})

    def testCmakePluginAssembleOptions7(self):

        with mock.patch("cmake_lib.set_option_prefix_path", return_value=None) as dummy:
            v, r = cmake_plugin._assemble_options(None, None, "test1", None, None)
            self.assertFalse(v)
            self.assertEqual(r, "Invalid option value (prefix_path): [test1]")
            dummy.assert_called_with(cmake_lib.boot_options(), "test1")

    def testCmakePluginAssembleOptions8(self):
        v, r = cmake_plugin._assemble_options(None, None, None, "test1", None)
        self.assertTrue(v)
        self.assertEqual(r, {"CMAKE_TOOLCHAIN_FILE": ("STRING", "test1")})

    def testCmakePluginAssembleOptions9(self):

        with mock.patch("cmake_lib.set_option_toolchain", return_value=None) as dummy:
            v, r = cmake_plugin._assemble_options(None, None, None, "test1", None)
            self.assertFalse(v)
            self.assertEqual(r, "Invalid option value (toolchain): [test1]")
            dummy.assert_called_with(cmake_lib.boot_options(), "test1")

    def testCmakePluginAssembleOptions10(self):

        v, r = cmake_plugin._assemble_options(None, None, None, None, "test1")
        self.assertFalse(v)
        self.assertEqual(r, "Invalid custom option: [t]")

        v, r = cmake_plugin._assemble_options(None, None, None, None, "test1:test2")
        self.assertFalse(v)
        self.assertEqual(r, "Invalid custom option: [t]")

        v, r = cmake_plugin._assemble_options(None, None, None, None, ["test1:test2=test3"])
        self.assertTrue(v)
        self.assertEqual(r, {"test1" : ("test2", "test3")})

    def testCmakePluginRunTask1(self):

        local_params = {}
        self.cmake_task.params = local_params

        with mock.patch("cmake_plugin.CustomTask._read_params", return_value=(True, (None, None, None, None, None, None, "dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4", "dummy_value5", None, None, None, None))) as dummy1:
            with mock.patch("cmake_plugin._assemble_options", return_value=(False, "dummy_message1")) as dummy2:

                v, r = self.cmake_task.run_task(print, "exe_name")
                self.assertFalse(v)
                self.assertEqual(r, "dummy_message1")
                dummy1.assert_called_with()
                dummy2.assert_called_with("dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4", "dummy_value5")

    def testCmakePluginRunTask2(self):

        local_params = {}
        local_params["operation"] = "cfg-and-gen"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        local_params["gen_type"] = "dummy_value1"
        local_params["cmake_path"] = "dummy_value2"
        self.cmake_task.params = local_params

        with mock.patch("cmake_lib.configure_and_generate", return_value=(False, (True, "test1", "test2"))) as dummy1:
            with mock.patch("output_backup_helper.dump_output") as dummy2:
                with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value=None) as dummy3:

                    v, r = self.cmake_task.run_task(print, "exe_name")
                    self.assertFalse(v)
                    dummy1.assert_called_with("dummy_value2", self.existent_path1, self.existent_path2, "dummy_value1", {})
                    dummy2.assert_not_called()
                    dummy3.assert_not_called()

    def testCmakePluginRunTask3(self):

        local_params = {}
        local_params["operation"] = "cfg-and-gen"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        local_params["gen_type"] = "dummy_value1"
        local_params["cmake_path"] = "dummy_value2"
        self.cmake_task.params = local_params

        with mock.patch("cmake_lib.configure_and_generate", return_value=(True, (False, "test1", "test2"))) as dummy1:
            with mock.patch("output_backup_helper.dump_output") as dummy2:
                with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value=None) as dummy3:

                    v, r = self.cmake_task.run_task(print, "exe_name")
                    self.assertTrue(v)
                    self.assertEqual(r, "test2")
                    dummy1.assert_called_with("dummy_value2", self.existent_path1, self.existent_path2, "dummy_value1", {})
                    dummy2.assert_has_calls([call(print, None, "test1", ("Cmake's stdout has been saved to: [%s]" % None)), call(print, None, "test2", ("Cmake's stderr has been saved to: [%s]" % None))])
                    dummy3.assert_called_with(False, print, [("cmake_plugin_stdout", "test1", "Cmake's stdout"), ("cmake_plugin_stderr", "test2", "Cmake's stderr")])

    def testCmakePluginRunTask4(self):

        local_params = {}
        local_params["operation"] = "cfg-and-gen"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        local_params["gen_type"] = "dummy_value1"
        local_params["cmake_path"] = "dummy_value2"
        self.cmake_task.params = local_params

        with mock.patch("cmake_lib.configure_and_generate", return_value=(True, (False, "test1", "test2"))) as dummy1:
            with mock.patch("output_backup_helper.dump_output") as dummy2:
                with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value="test-warning-msg") as dummy3:

                    v, r = self.cmake_task.run_task(print, "exe_name")
                    self.assertTrue(v)
                    self.assertEqual(r, "test-warning-msg%stest2" % os.linesep)
                    dummy1.assert_called_with("dummy_value2", self.existent_path1, self.existent_path2, "dummy_value1", {})
                    dummy2.assert_has_calls([call(print, None, "test1", ("Cmake's stdout has been saved to: [%s]" % None)), call(print, None, "test2", ("Cmake's stderr has been saved to: [%s]" % None))])
                    dummy3.assert_called_with(False, print, [("cmake_plugin_stdout", "test1", "Cmake's stdout"), ("cmake_plugin_stderr", "test2", "Cmake's stderr")])

    def testCmakePluginRunTask5(self):

        local_params = {}
        local_params["operation"] = "cfg-and-gen"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        local_params["gen_type"] = "dummy_value1"
        local_params["cmake_path"] = "dummy_value2"
        local_params["suppress_stderr_warnings"] = "dummy_value3"
        self.cmake_task.params = local_params

        with mock.patch("cmake_lib.configure_and_generate", return_value=(True, (False, "test1", "test2"))) as dummy1:
            with mock.patch("output_backup_helper.dump_output") as dummy2:
                with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value="test-warning-msg") as dummy3:

                    v, r = self.cmake_task.run_task(print, "exe_name")
                    self.assertTrue(v)
                    self.assertEqual(r, "test-warning-msg%scmake's stderr has been suppressed" % os.linesep)
                    dummy1.assert_called_with("dummy_value2", self.existent_path1, self.existent_path2, "dummy_value1", {})
                    dummy2.assert_has_calls([call(print, None, "test1", ("Cmake's stdout has been saved to: [%s]" % None)), call(print, None, "test2", ("Cmake's stderr has been saved to: [%s]" % None))])
                    dummy3.assert_called_with(False, print, [("cmake_plugin_stdout", "test1", "Cmake's stdout"), ("cmake_plugin_stderr", "test2", "Cmake's stderr")])

    def testCmakePluginRunTask6(self):

        local_params = {}
        local_params["operation"] = "cfg-and-gen"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        local_params["gen_type"] = "dummy_value1"
        local_params["cmake_path"] = "dummy_value2"
        self.cmake_task.params = local_params

        with mock.patch("cmake_lib.configure_and_generate", return_value=(True, (True, "test1", "test2"))) as dummy1:
            with mock.patch("output_backup_helper.dump_output") as dummy2:
                with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value=None) as dummy3:

                    v, r = self.cmake_task.run_task(print, "exe_name")
                    self.assertTrue(v)
                    dummy1.assert_called_with("dummy_value2", self.existent_path1, self.existent_path2, "dummy_value1", {})
                    dummy2.assert_has_calls([call(print, None, "test1", ("Cmake's stdout has been saved to: [%s]" % None)), call(print, None, "test2", ("Cmake's stderr has been saved to: [%s]" % None))])
                    dummy3.assert_called_with(True, print, [("cmake_plugin_stdout", "test1", "Cmake's stdout"), ("cmake_plugin_stderr", "test2", "Cmake's stderr")])

    def testCmakePluginRunTask7(self):

        local_params = {}
        local_params["operation"] = "cfg-and-gen"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        local_params["gen_type"] = "dummy_value1"
        local_params["cmake_path"] = "dummy_value2"
        local_params["save_output"] = "dummy_value3"
        local_params["save_error_output"] = "dummy_value4"
        self.cmake_task.params = local_params

        with mock.patch("cmake_lib.configure_and_generate", return_value=(True, (True, "test1", "test2"))) as dummy1:
            with mock.patch("output_backup_helper.dump_output") as dummy2:
                with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value=None) as dummy3:

                    v, r = self.cmake_task.run_task(print, "exe_name")
                    self.assertTrue(v)
                    dummy1.assert_called_with("dummy_value2", self.existent_path1, self.existent_path2, "dummy_value1", {})
                    dummy2.assert_has_calls([call(print, "dummy_value3", "test1", ("Cmake's stdout has been saved to: [dummy_value3]")), call(print, "dummy_value4", "test2", ("Cmake's stderr has been saved to: [dummy_value4]"))])
                    dummy3.assert_called_with(True, print, [("cmake_plugin_stdout", "test1", "Cmake's stdout"), ("cmake_plugin_stderr", "test2", "Cmake's stderr")])

    def testCmakePluginRunTask8(self):

        local_params = {}
        local_params["operation"] = "ext-opts"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.nonexistent_path1
        local_params["temp_path"] = self.nonexistent_path2
        self.cmake_task.params = local_params

        with mock.patch("cmake_lib.extract_options", return_value=(False, "err-msg")) as dummy:

            v, r = self.cmake_task.run_task(print, "exe_name")
            self.assertFalse(v)
            self.assertEqual(r, "err-msg")
            dummy.assert_called_with(None, self.existent_path1, self.nonexistent_path1, self.nonexistent_path2, {})

    def testCmakePluginRunTask9(self):

        local_params = {}
        local_params["operation"] = "ext-opts"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.nonexistent_path1
        local_params["temp_path"] = self.nonexistent_path2
        local_params["cmake_path"] = "dummy_value1"
        self.cmake_task.params = local_params

        with mock.patch("cmake_lib.extract_options", return_value=(False, "err-msg")) as dummy:

            v, r = self.cmake_task.run_task(print, "exe_name")
            self.assertFalse(v)
            self.assertEqual(r, "err-msg")
            dummy.assert_called_with("dummy_value1", self.existent_path1, self.nonexistent_path1, self.nonexistent_path2, {})

    def testCmakePluginRunTask10(self):

        local_params = {}
        local_params["operation"] = "ext-opts"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.nonexistent_path1
        local_params["temp_path"] = self.nonexistent_path2
        self.cmake_task.params = local_params

        with mock.patch("cmake_lib.extract_options", return_value=(True, None)) as dummy:

            v, r = self.cmake_task.run_task(print, "exe_name")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(None, self.existent_path1, self.nonexistent_path1, self.nonexistent_path2, {})

    def testCmakePluginRunTask11(self):

        local_params = {}
        local_params["operation"] = "ext-opts"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.nonexistent_path1
        local_params["temp_path"] = self.nonexistent_path2
        local_params["cmake_path"] = "dummy_value1"
        self.cmake_task.params = local_params

        with mock.patch("cmake_lib.extract_options", return_value=(True, None)) as dummy:

            v, r = self.cmake_task.run_task(print, "exe_name")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with("dummy_value1", self.existent_path1, self.nonexistent_path1, self.nonexistent_path2, {})

    def testCmakePluginRunTask12(self):

        local_params = {}
        local_params["operation"] = "ext-opts"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.nonexistent_path1
        local_params["temp_path"] = self.nonexistent_path2
        local_params["cmake_path"] = "dummy_value1"
        local_params["build_type"] = "debug"
        local_params["install_prefix"] = "dummy_value2"
        local_params["prefix_path"] = "dummy_value3"
        local_params["toolchain"] = "dummy_value4"
        local_params["custom_options"] = "dummy_value5"
        self.cmake_task.params = local_params

        with mock.patch("cmake_lib.extract_options", return_value=(True, None)) as dummy:

            v, r = self.cmake_task.run_task(print, "exe_name")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with("dummy_value1", self.existent_path1, self.nonexistent_path1, self.nonexistent_path2, {"CMAKE_BUILD_TYPE": ("STRING", "debug"), "CMAKE_INSTALL_PREFIX": ("STRING", "dummy_value2"), "CMAKE_PREFIX_PATH": ("STRING", "dummy_value3"), "CMAKE_TOOLCHAIN_FILE": ("STRING", "dummy_value4")})

    def testCmakePluginRunTask13(self):

        local_params = {}
        local_params["operation"] = "build"
        local_params["source_path"] = self.existent_path1
        self.cmake_task.params = local_params

        with mock.patch("cmake_lib.build", return_value=(True, None)) as dummy:

            v, r = self.cmake_task.run_task(print, "exe_name")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(None, self.existent_path1, False)

    def testCmakePluginRunTask14(self):

        local_params = {}
        local_params["operation"] = "build"
        local_params["source_path"] = self.existent_path1
        local_params["cmake_path"] = "dummy_value1"
        self.cmake_task.params = local_params

        with mock.patch("cmake_lib.build", return_value=(True, None)) as dummy:

            v, r = self.cmake_task.run_task(print, "exe_name")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with("dummy_value1", self.existent_path1, False)

    def testCmakePluginRunTask15(self):

        local_params = {}
        local_params["operation"] = "build"
        local_params["source_path"] = self.existent_path1
        local_params["parallel"] = "dummy_value1"
        self.cmake_task.params = local_params

        with mock.patch("cmake_lib.build", return_value=(True, None)) as dummy:

            v, r = self.cmake_task.run_task(print, "exe_name")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(None, self.existent_path1, True)

    def testCmakePluginRunTask16(self):

        local_params = {}
        local_params["operation"] = "install"
        local_params["source_path"] = self.existent_path1
        self.cmake_task.params = local_params

        with mock.patch("cmake_lib.install", return_value=(True, None)) as dummy:

            v, r = self.cmake_task.run_task(print, "exe_name")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(None, self.existent_path1, None)

    def testCmakePluginRunTask17(self):

        local_params = {}
        local_params["operation"] = "install"
        local_params["source_path"] = self.existent_path1
        local_params["cmake_path"] = "dummy_value1"
        self.cmake_task.params = local_params

        with mock.patch("cmake_lib.install", return_value=(True, None)) as dummy:

            v, r = self.cmake_task.run_task(print, "exe_name")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with("dummy_value1", self.existent_path1, None)

    def testCmakePluginRunTask18(self):

        local_params = {}
        local_params["operation"] = "install"
        local_params["source_path"] = self.existent_path1
        local_params["output_path"] = self.existent_path2
        self.cmake_task.params = local_params

        with mock.patch("cmake_lib.install", return_value=(True, None)) as dummy:

            v, r = self.cmake_task.run_task(print, "exe_name")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(None, self.existent_path1, self.existent_path2)

if __name__ == "__main__":
    unittest.main()
