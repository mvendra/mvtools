#!/usr/bin/env python3

import sys
import os
import shutil
import unittest
from unittest import mock
from unittest.mock import patch

import path_utils
import mvtools_test_fixture
import create_and_write_file

import cmake_lib

class CmakeLibTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("cmake_lib_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        self.test_opts = cmake_lib.boot_options()

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testSetOptionFail(self):
        self.assertEqual(cmake_lib.set_option(None, "", "", ""), None)

    def testSetOption(self):
        self.assertEqual(cmake_lib.set_option(self.test_opts, "optname", "opttype", "optval"), {"optname": ("opttype", "optval")})

    def testSetOptionParseFail(self):
        self.assertEqual(cmake_lib.set_option_parse(self.test_opts, "optname-opttype=optval"), None)
        self.assertEqual(cmake_lib.set_option_parse(self.test_opts, "optname:opttype-optval"), None)
        self.assertEqual(cmake_lib.set_option_parse(self.test_opts, "optname-opttype+optval"), None)

    def testSetOptionParse(self):
        self.assertEqual(cmake_lib.set_option_parse(self.test_opts, "optname:opttype=optval"), {"optname": ("opttype", "optval")})

    def testSetOptionToolchain(self):
        self.assertEqual(cmake_lib.set_option_toolchain(self.test_opts, "optval"), {"CMAKE_TOOLCHAIN_FILE": ("STRING", "optval")})

    def testSetOptionInstallPrefix(self):
        self.assertEqual(cmake_lib.set_option_install_prefix(self.test_opts, "optval"), {"CMAKE_INSTALL_PREFIX": ("STRING", "optval")})

    def testSetOptionBuildTypeFail(self):
        self.assertEqual(cmake_lib.set_option_build_type(self.test_opts, "invalid"), None)
        self.assertEqual(cmake_lib.set_option_build_type(self.test_opts, None), None)

    def testSetOptionBuildType(self):
        self.assertEqual(cmake_lib.set_option_build_type(self.test_opts, "Debug"), {"CMAKE_BUILD_TYPE": ("STRING", "Debug")})
        self.assertEqual(cmake_lib.set_option_build_type(self.test_opts, "Release"), {"CMAKE_BUILD_TYPE": ("STRING", "Release")})
        self.assertEqual(cmake_lib.set_option_build_type(self.test_opts, "RelWithDebInfo"), {"CMAKE_BUILD_TYPE": ("STRING", "RelWithDebInfo")})
        self.assertEqual(cmake_lib.set_option_build_type(self.test_opts, "MinSizeRel"), {"CMAKE_BUILD_TYPE": ("STRING", "MinSizeRel")})

    def testExtractOptions1(self):

        self.folder1 = "folder1"
        self.folder2 = "folder2"
        self.file1 = "file1"
        self.folder1_full = path_utils.concat_path(self.test_dir, self.folder1)
        self.folder2_full = path_utils.concat_path(self.test_dir, self.folder2)
        self.file1_full = path_utils.concat_path(self.test_dir, self.file1)
        os.mkdir(self.folder1_full)
        create_and_write_file.create_file_contents(self.file1_full, "test contents")

        with mock.patch("cmake_wrapper.extract_options", return_value=(True, (True, "test1", "test2"))) as dummy:
            v, r = cmake_lib.extract_options("test-cmake-path", self.folder1_full, self.folder2_full, self.file1_full)
            self.assertFalse(v)
            self.assertEqual(r, "Output path [%s] already exists" % self.file1_full)
            dummy.assert_not_called()

    def testExtractOptions2(self):

        self.folder1 = "folder1"
        self.folder2 = "folder2"
        self.file1 = "file1"
        self.folder1_full = path_utils.concat_path(self.test_dir, self.folder1)
        self.folder2_full = path_utils.concat_path(self.test_dir, self.folder2)
        self.file1_full = path_utils.concat_path(self.test_dir, self.file1)
        os.mkdir(self.folder1_full)

        with mock.patch("cmake_wrapper.extract_options", return_value=(False, "test error message [test1][test2]")) as dummy:
            v, r = cmake_lib.extract_options("test-cmake-path", self.folder1_full, self.folder2_full, self.file1_full)
            self.assertFalse(v)
            self.assertEqual(r, "test error message [test1][test2]")
            dummy.assert_called_with("test-cmake-path", self.folder1_full, self.folder2_full)

        self.assertFalse(os.path.exists(self.file1_full))

    def testExtractOptions3(self):

        self.folder1 = "folder1"
        self.folder2 = "folder2"
        self.file1 = "file1"
        self.folder1_full = path_utils.concat_path(self.test_dir, self.folder1)
        self.folder2_full = path_utils.concat_path(self.test_dir, self.folder2)
        self.file1_full = path_utils.concat_path(self.test_dir, self.file1)
        os.mkdir(self.folder1_full)

        with mock.patch("cmake_wrapper.extract_options", return_value=(True, (True, "test1", "test2"))) as dummy:
            v, r = cmake_lib.extract_options("test-cmake-path", self.folder1_full, self.folder2_full, self.file1_full)
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with("test-cmake-path", self.folder1_full, self.folder2_full)

        read_contents = None
        with open(self.file1_full, "r") as f:
            read_contents = f.read()

        self.assertEqual(read_contents, "test1")

    def testConfigureAndGenerate(self):

        with mock.patch("cmake_wrapper.configure_and_generate", return_value=(True, None, None)) as dummy:
            self.assertEqual(cmake_lib.configure_and_generate("test-cmake-path", "test-source-path", "test-output-path", "makefile", self.test_opts), (True, None, None))
            dummy.assert_called_with("test-cmake-path", "test-source-path", "test-output-path", "Unix Makefiles", self.test_opts)

if __name__ == "__main__":
    unittest.main()
