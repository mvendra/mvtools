#!/usr/bin/env python

import sys
import os
import shutil
import unittest
from unittest import mock
from unittest.mock import patch

import mvtools_test_fixture
import create_and_write_file
import path_utils
import standard_c
import generic_run
import get_platform

import gcc_wrapper

class GccWrapperTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("gcc_wrapper_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # prepare test content
        self.main_c = "main.c"
        self.main_c_full = path_utils.concat_path(self.test_dir, self.main_c)

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testExec1(self):

        create_and_write_file.create_file_contents(self.main_c_full, standard_c.get_main_c_app())

        v, r = gcc_wrapper.exec(None, self.main_c_full, self.test_dir)
        self.assertFalse(v)
        self.assertEqual(r, "options_list must be a list")

    def testExec2(self):

        v, r = gcc_wrapper.exec(None, [self.main_c_full], self.test_dir)
        self.assertFalse(v)

    def testExec3(self):

        create_and_write_file.create_file_contents(self.main_c_full, standard_c.get_main_c_app())

        v, r = gcc_wrapper.exec([], [self.main_c_full], self.test_dir)
        self.assertFalse(v)
        self.assertEqual(r, "compiler_base, when present, must be a string")

    def testExec4(self):

        create_and_write_file.create_file_contents(self.main_c_full, standard_c.get_main_c_app())

        with mock.patch("generic_run.run_cmd_simple", return_value=(False, "dummy_error_msg")) as dummy:
            v, r = gcc_wrapper.exec(None, [self.main_c_full])
            self.assertFalse(v)
            self.assertEqual(r, "Failed running gcc command: [dummy_error_msg]")
            dummy.assert_called_with(["gcc", self.main_c_full], use_cwd=None)

    def testExec5(self):

        create_and_write_file.create_file_contents(self.main_c_full, standard_c.get_main_c_app())

        with mock.patch("generic_run.run_cmd_simple", return_value=(True, None)) as dummy:
            v, r = gcc_wrapper.exec("custom_install_path", [self.main_c_full])
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with([path_utils.concat_path("custom_install_path", "bin", "gcc"), self.main_c_full], use_cwd=None)

    def testExec6(self):

        create_and_write_file.create_file_contents(self.main_c_full, standard_c.get_main_c_app())

        v, r = gcc_wrapper.exec(None, [self.main_c_full], self.test_dir)
        self.assertTrue(v)
        self.assertEqual(r, None)

        compiled_applet = ""
        local_plat = get_platform.getplat()
        if (local_plat == get_platform.PLAT_LINUX) or (local_plat == get_platform.PLAT_MACOS):
            compiled_applet = "a.out"
        elif (local_plat == get_platform.PLAT_WINDOWS) or (local_plat == get_platform.PLAT_CYGWIN) or (local_plat == get_platform.PLAT_MSYS) or (local_plat == get_platform.PLAT_MINGW) or (local_plat == get_platform.PLAT_MSYS_MINGW_GRAY):
            compiled_applet = "a.exe"
        else:
            self.fail("Unsupported platform")

        compiled_applet_full = path_utils.concat_path(self.test_dir, compiled_applet)
        v, r = generic_run.run_cmd_simple([compiled_applet_full], use_cwd=self.test_dir)
        self.assertTrue(v)
        self.assertEqual(r.strip(), "test for echo")

if __name__ == "__main__":
    unittest.main()
