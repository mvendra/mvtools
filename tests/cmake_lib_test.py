#!/usr/bin/env python3

import sys
import os
import shutil
import unittest
from unittest import mock
from unittest.mock import patch

import mvtools_test_fixture

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

    def testConfigureAndGenerate(self):

        with mock.patch("cmake_wrapper.configure_and_generate", return_value=(True, None, None)) as dummy:
            self.assertEqual(cmake_lib.configure_and_generate("test-cmake-path", "test-source-path", "test-output-path", "makefile", self.test_opts), (True, None, None))
            dummy.assert_called_with("test-cmake-path", "test-source-path", "test-output-path", "Unix Makefiles", self.test_opts)

if __name__ == '__main__':
    unittest.main()
