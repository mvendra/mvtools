#!/usr/bin/env python3

import os
import shutil
import unittest
from unittest import mock
from unittest.mock import patch

import mvtools_test_fixture
import convcygpath
import get_platform

class ConvCygPathTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("convcygpath_test")
        if not v:
            return v, r
        self.test_base_dir = r[0]
        self.test_dir = r[1]

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testConvertCygwinPathToWinPath(self):
        self.assertEqual(convcygpath.convert_cygwin_path_to_win_path(""), None)

        with mock.patch("get_platform.getplat", return_value=get_platform.PLAT_CYGWIN):
            self.assertEqual(convcygpath.convert_cygwin_path_to_win_path("/"), None)
            self.assertEqual(convcygpath.convert_cygwin_path_to_win_path("\\"), None)
            self.assertEqual(convcygpath.convert_cygwin_path_to_win_path("\\first"), None)
            self.assertEqual(convcygpath.convert_cygwin_path_to_win_path("\\first\\second"), None)
            self.assertEqual(convcygpath.convert_cygwin_path_to_win_path("/cigdrive"), None)
            self.assertEqual(convcygpath.convert_cygwin_path_to_win_path("/cigdrive/c"), None)
            self.assertEqual(convcygpath.convert_cygwin_path_to_win_path("/cigdrive/mp1"), None)
            self.assertEqual(convcygpath.convert_cygwin_path_to_win_path("/cygdrive/c"), "C:")
            self.assertEqual(convcygpath.convert_cygwin_path_to_win_path("/cygdrive/mp1"), "MP1:")
            self.assertEqual(convcygpath.convert_cygwin_path_to_win_path("/cygdrive/mp1/"), "MP1:")
            self.assertEqual(convcygpath.convert_cygwin_path_to_win_path("/cygdrive/c/"), "C:")
            self.assertEqual(convcygpath.convert_cygwin_path_to_win_path("/cygdrive/c/mp1"), "C:/mp1")
            self.assertEqual(convcygpath.convert_cygwin_path_to_win_path("/cygdrive/c/mp1/first/second"), "C:/mp1/first/second")
            self.assertEqual(convcygpath.convert_cygwin_path_to_win_path("/cygdrive/c/mp1/first/second/"), "C:/mp1/first/second")

if __name__ == '__main__':
    unittest.main()
