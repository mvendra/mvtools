#!/usr/bin/env python3

import sys
import os
import shutil
import unittest
from unittest import mock
from unittest.mock import patch

import mvtools_test_fixture

import svn_lib
import get_platform

class SvnLibTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("svn_lib_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testExtractFileFromStatusLine(self):
        self.assertEqual(svn_lib.extract_file_from_status_line("       "), None)
        self.assertEqual(svn_lib.extract_file_from_status_line("        "), None)
        self.assertEqual(svn_lib.extract_file_from_status_line("A        "), " ")
        self.assertEqual(svn_lib.extract_file_from_status_line("D       a"), "a")
        self.assertEqual(svn_lib.extract_file_from_status_line("        > moved from BUGS"), None)
        self.assertEqual(svn_lib.extract_file_from_status_line("<       > moved from BUGS"), "> moved from BUGS")

    def testIsNonNumber(self):

        self.assertTrue(svn_lib.is_nonnumber("a"))
        self.assertTrue(svn_lib.is_nonnumber("!"))
        self.assertFalse(svn_lib.is_nonnumber("1"))

    def testIsNonSpaceOrTabs(self):

        self.assertTrue(svn_lib.is_nonspaceortabs("a"))
        self.assertFalse(svn_lib.is_nonspaceortabs(" "))
        self.assertFalse(svn_lib.is_nonspaceortabs("\t"))

    def testFixCygwinPath(self):

        with mock.patch("get_platform.getplat", return_value=get_platform.PLAT_LINUX):
            self.assertEqual(svn_lib.fix_cygwin_path(""), None)
            self.assertEqual(svn_lib.fix_cygwin_path("C:\\windows\\data"), "C:\\windows\\data")
            self.assertEqual(svn_lib.fix_cygwin_path("C:/windows/data"), "C:/windows/data")

        with mock.patch("get_platform.getplat", return_value=get_platform.PLAT_CYGWIN):
            with mock.patch("mvtools_envvars.mvtools_envvar_read_cygwin_install_path", return_value="C:/cygwin"):
                self.assertEqual(svn_lib.fix_cygwin_path(""), None)
                self.assertEqual(svn_lib.fix_cygwin_path("C:\\windows\\data"), None)
                self.assertEqual(svn_lib.fix_cygwin_path("C:/windows/data"), None)
                self.assertEqual(svn_lib.fix_cygwin_path("/cygdrive/c/mp1/folder"), "C:/mp1/folder")

        with mock.patch("get_platform.getplat", return_value=get_platform.PLAT_WINDOWS):
            self.assertEqual(svn_lib.fix_cygwin_path(""), None)
            self.assertEqual(svn_lib.fix_cygwin_path("C:\\windows\\data"), "C:\\windows\\data")
            self.assertEqual(svn_lib.fix_cygwin_path("C:/windows/data"), "C:/windows/data")

    def testSanitizeWindowsPath(self):

        with mock.patch("get_platform.getplat", return_value=get_platform.PLAT_LINUX):
            self.assertEqual(svn_lib.sanitize_windows_path(""), None)
            self.assertEqual(svn_lib.sanitize_windows_path("C:\\windows\\data"), "C:\\windows\\data")
            self.assertEqual(svn_lib.sanitize_windows_path("C:/windows/data"), "C:/windows/data")

        with mock.patch("get_platform.getplat", return_value=get_platform.PLAT_CYGWIN):
            self.assertEqual(svn_lib.sanitize_windows_path(""), None)
            self.assertEqual(svn_lib.sanitize_windows_path("C:\\windows\\data"), "C:/windows/data")
            self.assertEqual(svn_lib.sanitize_windows_path("C:/windows/data"), "C:/windows/data")

        with mock.patch("get_platform.getplat", return_value=get_platform.PLAT_WINDOWS):
            self.assertEqual(svn_lib.sanitize_windows_path(""), None)
            self.assertEqual(svn_lib.sanitize_windows_path("C:\\windows\\data"), "C:/windows/data")
            self.assertEqual(svn_lib.sanitize_windows_path("C:/windows/data"), "C:/windows/data")

if __name__ == "__main__":
    unittest.main()
