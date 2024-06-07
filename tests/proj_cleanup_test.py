#!/usr/bin/env python3

import os
import shutil
import unittest
from unittest import mock
from unittest.mock import patch

import mvtools_test_fixture
import create_and_write_file
import path_utils
import proj_cleanup

class ProjCleanupTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("proj_cleanup_test")
        if not v:
            return v, r
        self.test_base_dir = r[0]
        self.test_dir = r[1]

        # proj
        self.target_proj = path_utils.concat_path(self.test_dir, "target_proj")
        os.mkdir(self.target_proj)

        # dep
        self.target_proj_dep = path_utils.concat_path(self.target_proj, "dep")
        self.target_proj_dep_linux = path_utils.concat_path(self.target_proj_dep, "linux")
        self.target_proj_dep_windows = path_utils.concat_path(self.target_proj_dep, "windows")
        self.target_proj_dep_macosx = path_utils.concat_path(self.target_proj_dep, "macosx")
        os.mkdir(self.target_proj_dep)
        os.mkdir(self.target_proj_dep_linux)
        os.mkdir(self.target_proj_dep_windows)
        os.mkdir(self.target_proj_dep_macosx)

        # tmp
        self.target_proj_tmp = path_utils.concat_path(self.target_proj, "tmp")
        self.target_proj_tmp_linux = path_utils.concat_path(self.target_proj_tmp, "linux")
        self.target_proj_tmp_linux_debug = path_utils.concat_path(self.target_proj_tmp_linux, "debug")
        self.target_proj_tmp_linux_release = path_utils.concat_path(self.target_proj_tmp_linux, "release")
        self.target_proj_tmp_windows = path_utils.concat_path(self.target_proj_tmp, "windows")
        self.target_proj_tmp_windows_debug = path_utils.concat_path(self.target_proj_tmp_windows, "debug")
        self.target_proj_tmp_windows_release = path_utils.concat_path(self.target_proj_tmp_windows, "release")
        self.target_proj_tmp_macosx = path_utils.concat_path(self.target_proj_tmp, "macosx")
        self.target_proj_tmp_macosx_debug = path_utils.concat_path(self.target_proj_tmp_macosx, "debug")
        self.target_proj_tmp_macosx_release = path_utils.concat_path(self.target_proj_tmp_macosx, "release")
        os.mkdir(self.target_proj_tmp)
        os.mkdir(self.target_proj_tmp_linux)
        os.mkdir(self.target_proj_tmp_linux_debug)
        os.mkdir(self.target_proj_tmp_linux_release)
        os.mkdir(self.target_proj_tmp_windows)
        os.mkdir(self.target_proj_tmp_windows_debug)
        os.mkdir(self.target_proj_tmp_windows_release)
        os.mkdir(self.target_proj_tmp_macosx)
        os.mkdir(self.target_proj_tmp_macosx_debug)
        os.mkdir(self.target_proj_tmp_macosx_release)

        # out
        self.target_proj_out = path_utils.concat_path(self.target_proj, "out")
        self.target_proj_out_linux = path_utils.concat_path(self.target_proj_out, "linux")
        self.target_proj_out_linux_debug = path_utils.concat_path(self.target_proj_out_linux, "debug")
        self.target_proj_out_linux_release = path_utils.concat_path(self.target_proj_out_linux, "release")
        self.target_proj_out_windows = path_utils.concat_path(self.target_proj_out, "windows")
        self.target_proj_out_windows_debug = path_utils.concat_path(self.target_proj_out_windows, "debug")
        self.target_proj_out_windows_release = path_utils.concat_path(self.target_proj_out_windows, "release")
        self.target_proj_out_macosx = path_utils.concat_path(self.target_proj_out, "macosx")
        self.target_proj_out_macosx_debug = path_utils.concat_path(self.target_proj_out_macosx, "debug")
        self.target_proj_out_macosx_release = path_utils.concat_path(self.target_proj_out_macosx, "release")
        os.mkdir(self.target_proj_out)
        os.mkdir(self.target_proj_out_linux)
        os.mkdir(self.target_proj_out_linux_debug)
        os.mkdir(self.target_proj_out_linux_release)
        os.mkdir(self.target_proj_out_windows)
        os.mkdir(self.target_proj_out_windows_debug)
        os.mkdir(self.target_proj_out_windows_release)
        os.mkdir(self.target_proj_out_macosx)
        os.mkdir(self.target_proj_out_macosx_debug)
        os.mkdir(self.target_proj_out_macosx_release)

        self.nonexistent = path_utils.concat_path(self.test_dir, "nonexistent")

        return True, None

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testProjCleanup1(self):

        v, r = proj_cleanup.proj_cleanup(self.nonexistent, False, False, False)
        self.assertFalse(v)
        self.assertTrue("does not exist" in r)

    def testProjCleanup2(self):

        with mock.patch("proj_cleanup.proj_cleanup_dep", return_value=(True, None)) as dummy1:
            with mock.patch("proj_cleanup.proj_cleanup_tmp", return_value=(True, None)) as dummy2:
                with mock.patch("proj_cleanup.proj_cleanup_out", return_value=(True, None)) as dummy3:
                    v, r = proj_cleanup.proj_cleanup(self.target_proj, False, False, False)
                    self.assertTrue(v)
                    self.assertEqual(r, None)
                    dummy1.assert_not_called()
                    dummy2.assert_not_called()
                    dummy3.assert_not_called()

    def testProjCleanup3(self):

        with mock.patch("proj_cleanup.proj_cleanup_dep", return_value=(True, None)) as dummy1:
            with mock.patch("proj_cleanup.proj_cleanup_tmp", return_value=(True, None)) as dummy2:
                with mock.patch("proj_cleanup.proj_cleanup_out", return_value=(True, None)) as dummy3:
                    v, r = proj_cleanup.proj_cleanup(self.target_proj, True, False, False)
                    self.assertTrue(v)
                    self.assertEqual(r, None)
                    dummy1.assert_called_with(self.target_proj)
                    dummy2.assert_not_called()
                    dummy3.assert_not_called()

    def testProjCleanup4(self):

        with mock.patch("proj_cleanup.proj_cleanup_dep", return_value=(True, None)) as dummy1:
            with mock.patch("proj_cleanup.proj_cleanup_tmp", return_value=(True, None)) as dummy2:
                with mock.patch("proj_cleanup.proj_cleanup_out", return_value=(True, None)) as dummy3:
                    v, r = proj_cleanup.proj_cleanup(self.target_proj, False, True, False)
                    self.assertTrue(v)
                    self.assertEqual(r, None)
                    dummy1.assert_not_called()
                    dummy2.assert_called_with(self.target_proj)
                    dummy3.assert_not_called()

    def testProjCleanup5(self):

        with mock.patch("proj_cleanup.proj_cleanup_dep", return_value=(True, None)) as dummy1:
            with mock.patch("proj_cleanup.proj_cleanup_tmp", return_value=(True, None)) as dummy2:
                with mock.patch("proj_cleanup.proj_cleanup_out", return_value=(True, None)) as dummy3:
                    v, r = proj_cleanup.proj_cleanup(self.target_proj, False, False, True)
                    self.assertTrue(v)
                    self.assertEqual(r, None)
                    dummy1.assert_not_called()
                    dummy2.assert_not_called()
                    dummy3.assert_called_with(self.target_proj)

    def testProjCleanup6(self):

        with mock.patch("proj_cleanup.proj_cleanup_dep", return_value=(True, None)) as dummy1:
            with mock.patch("proj_cleanup.proj_cleanup_tmp", return_value=(True, None)) as dummy2:
                with mock.patch("proj_cleanup.proj_cleanup_out", return_value=(True, None)) as dummy3:
                    v, r = proj_cleanup.proj_cleanup(self.target_proj, True, True, True)
                    self.assertTrue(v)
                    self.assertEqual(r, None)
                    dummy1.assert_called_with(self.target_proj)
                    dummy2.assert_called_with(self.target_proj)
                    dummy3.assert_called_with(self.target_proj)

    def testProjCleanup7(self):

        dep_linux_file1 = path_utils.concat_path(self.target_proj_dep_linux, "file1")
        dep_windows_file2 = path_utils.concat_path(self.target_proj_dep_windows, "file2")
        dep_macosx_file3 = path_utils.concat_path(self.target_proj_dep_macosx, "file3")

        tmp_linux_debug_file4 = path_utils.concat_path(self.target_proj_tmp_linux_debug, "file4")
        tmp_linux_release_file5 = path_utils.concat_path(self.target_proj_tmp_linux_release, "file5")
        tmp_windows_debug_file6 = path_utils.concat_path(self.target_proj_tmp_windows_debug, "file6")
        tmp_windows_release_file7 = path_utils.concat_path(self.target_proj_tmp_windows_release, "file7")
        tmp_macosx_debug_file8 = path_utils.concat_path(self.target_proj_tmp_macosx_debug, "file8")
        tmp_macosx_release_file9 = path_utils.concat_path(self.target_proj_tmp_macosx_release, "file9")

        out_linux_debug_file10 = path_utils.concat_path(self.target_proj_out_linux_debug, "file10")
        out_linux_release_file11 = path_utils.concat_path(self.target_proj_out_linux_release, "file11")
        out_windows_debug_file12 = path_utils.concat_path(self.target_proj_out_windows_debug, "file12")
        out_windows_release_file13 = path_utils.concat_path(self.target_proj_out_windows_release, "file13")
        out_macosx_debug_file14 = path_utils.concat_path(self.target_proj_out_macosx_debug, "file14")
        out_macosx_release_file15 = path_utils.concat_path(self.target_proj_out_macosx_release, "file15")

        self.assertTrue(create_and_write_file.create_file_contents(dep_linux_file1, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(dep_windows_file2, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(dep_macosx_file3, "contents"))

        self.assertTrue(create_and_write_file.create_file_contents(tmp_linux_debug_file4, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(tmp_linux_release_file5, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(tmp_windows_debug_file6, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(tmp_windows_release_file7, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(tmp_macosx_debug_file8, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(tmp_macosx_release_file9, "contents"))

        self.assertTrue(create_and_write_file.create_file_contents(out_linux_debug_file10, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(out_linux_release_file11, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(out_windows_debug_file12, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(out_windows_release_file13, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(out_macosx_debug_file14, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(out_macosx_release_file15, "contents"))

        self.assertTrue(os.path.exists(dep_linux_file1))
        self.assertTrue(os.path.exists(dep_windows_file2))
        self.assertTrue(os.path.exists(dep_macosx_file3))

        self.assertTrue(os.path.exists(tmp_linux_debug_file4))
        self.assertTrue(os.path.exists(tmp_linux_release_file5))
        self.assertTrue(os.path.exists(tmp_windows_debug_file6))
        self.assertTrue(os.path.exists(tmp_windows_release_file7))
        self.assertTrue(os.path.exists(tmp_macosx_debug_file8))
        self.assertTrue(os.path.exists(tmp_macosx_release_file9))

        self.assertTrue(os.path.exists(out_linux_debug_file10))
        self.assertTrue(os.path.exists(out_linux_release_file11))
        self.assertTrue(os.path.exists(out_windows_debug_file12))
        self.assertTrue(os.path.exists(out_windows_release_file13))
        self.assertTrue(os.path.exists(out_macosx_debug_file14))
        self.assertTrue(os.path.exists(out_macosx_release_file15))

        v, r = proj_cleanup.proj_cleanup(self.target_proj, False, False, False)
        self.assertTrue(v)
        self.assertEqual(r, None)

        self.assertTrue(os.path.exists(dep_linux_file1))
        self.assertTrue(os.path.exists(dep_windows_file2))
        self.assertTrue(os.path.exists(dep_macosx_file3))

        self.assertTrue(os.path.exists(tmp_linux_debug_file4))
        self.assertTrue(os.path.exists(tmp_linux_release_file5))
        self.assertTrue(os.path.exists(tmp_windows_debug_file6))
        self.assertTrue(os.path.exists(tmp_windows_release_file7))
        self.assertTrue(os.path.exists(tmp_macosx_debug_file8))
        self.assertTrue(os.path.exists(tmp_macosx_release_file9))

        self.assertTrue(os.path.exists(out_linux_debug_file10))
        self.assertTrue(os.path.exists(out_linux_release_file11))
        self.assertTrue(os.path.exists(out_windows_debug_file12))
        self.assertTrue(os.path.exists(out_windows_release_file13))
        self.assertTrue(os.path.exists(out_macosx_debug_file14))
        self.assertTrue(os.path.exists(out_macosx_release_file15))

    def testProjCleanup8(self):

        dep_linux_file1 = path_utils.concat_path(self.target_proj_dep_linux, "file1")
        dep_windows_file2 = path_utils.concat_path(self.target_proj_dep_windows, "file2")
        dep_macosx_file3 = path_utils.concat_path(self.target_proj_dep_macosx, "file3")

        tmp_linux_debug_file4 = path_utils.concat_path(self.target_proj_tmp_linux_debug, "file4")
        tmp_linux_release_file5 = path_utils.concat_path(self.target_proj_tmp_linux_release, "file5")
        tmp_windows_debug_file6 = path_utils.concat_path(self.target_proj_tmp_windows_debug, "file6")
        tmp_windows_release_file7 = path_utils.concat_path(self.target_proj_tmp_windows_release, "file7")
        tmp_macosx_debug_file8 = path_utils.concat_path(self.target_proj_tmp_macosx_debug, "file8")
        tmp_macosx_release_file9 = path_utils.concat_path(self.target_proj_tmp_macosx_release, "file9")

        out_linux_debug_file10 = path_utils.concat_path(self.target_proj_out_linux_debug, "file10")
        out_linux_release_file11 = path_utils.concat_path(self.target_proj_out_linux_release, "file11")
        out_windows_debug_file12 = path_utils.concat_path(self.target_proj_out_windows_debug, "file12")
        out_windows_release_file13 = path_utils.concat_path(self.target_proj_out_windows_release, "file13")
        out_macosx_debug_file14 = path_utils.concat_path(self.target_proj_out_macosx_debug, "file14")
        out_macosx_release_file15 = path_utils.concat_path(self.target_proj_out_macosx_release, "file15")

        self.assertTrue(create_and_write_file.create_file_contents(dep_linux_file1, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(dep_windows_file2, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(dep_macosx_file3, "contents"))

        self.assertTrue(create_and_write_file.create_file_contents(tmp_linux_debug_file4, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(tmp_linux_release_file5, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(tmp_windows_debug_file6, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(tmp_windows_release_file7, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(tmp_macosx_debug_file8, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(tmp_macosx_release_file9, "contents"))

        self.assertTrue(create_and_write_file.create_file_contents(out_linux_debug_file10, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(out_linux_release_file11, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(out_windows_debug_file12, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(out_windows_release_file13, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(out_macosx_debug_file14, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(out_macosx_release_file15, "contents"))

        self.assertTrue(os.path.exists(dep_linux_file1))
        self.assertTrue(os.path.exists(dep_windows_file2))
        self.assertTrue(os.path.exists(dep_macosx_file3))

        self.assertTrue(os.path.exists(tmp_linux_debug_file4))
        self.assertTrue(os.path.exists(tmp_linux_release_file5))
        self.assertTrue(os.path.exists(tmp_windows_debug_file6))
        self.assertTrue(os.path.exists(tmp_windows_release_file7))
        self.assertTrue(os.path.exists(tmp_macosx_debug_file8))
        self.assertTrue(os.path.exists(tmp_macosx_release_file9))

        self.assertTrue(os.path.exists(out_linux_debug_file10))
        self.assertTrue(os.path.exists(out_linux_release_file11))
        self.assertTrue(os.path.exists(out_windows_debug_file12))
        self.assertTrue(os.path.exists(out_windows_release_file13))
        self.assertTrue(os.path.exists(out_macosx_debug_file14))
        self.assertTrue(os.path.exists(out_macosx_release_file15))

        v, r = proj_cleanup.proj_cleanup(self.target_proj, True, False, False)
        self.assertTrue(v)
        self.assertEqual(r, None)

        self.assertFalse(os.path.exists(dep_linux_file1))
        self.assertFalse(os.path.exists(dep_windows_file2))
        self.assertFalse(os.path.exists(dep_macosx_file3))

        self.assertTrue(os.path.exists(tmp_linux_debug_file4))
        self.assertTrue(os.path.exists(tmp_linux_release_file5))
        self.assertTrue(os.path.exists(tmp_windows_debug_file6))
        self.assertTrue(os.path.exists(tmp_windows_release_file7))
        self.assertTrue(os.path.exists(tmp_macosx_debug_file8))
        self.assertTrue(os.path.exists(tmp_macosx_release_file9))

        self.assertTrue(os.path.exists(out_linux_debug_file10))
        self.assertTrue(os.path.exists(out_linux_release_file11))
        self.assertTrue(os.path.exists(out_windows_debug_file12))
        self.assertTrue(os.path.exists(out_windows_release_file13))
        self.assertTrue(os.path.exists(out_macosx_debug_file14))
        self.assertTrue(os.path.exists(out_macosx_release_file15))

    def testProjCleanup9(self):

        dep_linux_file1 = path_utils.concat_path(self.target_proj_dep_linux, "file1")
        dep_windows_file2 = path_utils.concat_path(self.target_proj_dep_windows, "file2")
        dep_macosx_file3 = path_utils.concat_path(self.target_proj_dep_macosx, "file3")

        tmp_linux_debug_file4 = path_utils.concat_path(self.target_proj_tmp_linux_debug, "file4")
        tmp_linux_release_file5 = path_utils.concat_path(self.target_proj_tmp_linux_release, "file5")
        tmp_windows_debug_file6 = path_utils.concat_path(self.target_proj_tmp_windows_debug, "file6")
        tmp_windows_release_file7 = path_utils.concat_path(self.target_proj_tmp_windows_release, "file7")
        tmp_macosx_debug_file8 = path_utils.concat_path(self.target_proj_tmp_macosx_debug, "file8")
        tmp_macosx_release_file9 = path_utils.concat_path(self.target_proj_tmp_macosx_release, "file9")

        out_linux_debug_file10 = path_utils.concat_path(self.target_proj_out_linux_debug, "file10")
        out_linux_release_file11 = path_utils.concat_path(self.target_proj_out_linux_release, "file11")
        out_windows_debug_file12 = path_utils.concat_path(self.target_proj_out_windows_debug, "file12")
        out_windows_release_file13 = path_utils.concat_path(self.target_proj_out_windows_release, "file13")
        out_macosx_debug_file14 = path_utils.concat_path(self.target_proj_out_macosx_debug, "file14")
        out_macosx_release_file15 = path_utils.concat_path(self.target_proj_out_macosx_release, "file15")

        self.assertTrue(create_and_write_file.create_file_contents(dep_linux_file1, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(dep_windows_file2, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(dep_macosx_file3, "contents"))

        self.assertTrue(create_and_write_file.create_file_contents(tmp_linux_debug_file4, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(tmp_linux_release_file5, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(tmp_windows_debug_file6, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(tmp_windows_release_file7, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(tmp_macosx_debug_file8, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(tmp_macosx_release_file9, "contents"))

        self.assertTrue(create_and_write_file.create_file_contents(out_linux_debug_file10, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(out_linux_release_file11, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(out_windows_debug_file12, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(out_windows_release_file13, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(out_macosx_debug_file14, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(out_macosx_release_file15, "contents"))

        self.assertTrue(os.path.exists(dep_linux_file1))
        self.assertTrue(os.path.exists(dep_windows_file2))
        self.assertTrue(os.path.exists(dep_macosx_file3))

        self.assertTrue(os.path.exists(tmp_linux_debug_file4))
        self.assertTrue(os.path.exists(tmp_linux_release_file5))
        self.assertTrue(os.path.exists(tmp_windows_debug_file6))
        self.assertTrue(os.path.exists(tmp_windows_release_file7))
        self.assertTrue(os.path.exists(tmp_macosx_debug_file8))
        self.assertTrue(os.path.exists(tmp_macosx_release_file9))

        self.assertTrue(os.path.exists(out_linux_debug_file10))
        self.assertTrue(os.path.exists(out_linux_release_file11))
        self.assertTrue(os.path.exists(out_windows_debug_file12))
        self.assertTrue(os.path.exists(out_windows_release_file13))
        self.assertTrue(os.path.exists(out_macosx_debug_file14))
        self.assertTrue(os.path.exists(out_macosx_release_file15))

        v, r = proj_cleanup.proj_cleanup(self.target_proj, False, True, False)
        self.assertTrue(v)
        self.assertEqual(r, None)

        self.assertTrue(os.path.exists(dep_linux_file1))
        self.assertTrue(os.path.exists(dep_windows_file2))
        self.assertTrue(os.path.exists(dep_macosx_file3))

        self.assertFalse(os.path.exists(tmp_linux_debug_file4))
        self.assertFalse(os.path.exists(tmp_linux_release_file5))
        self.assertFalse(os.path.exists(tmp_windows_debug_file6))
        self.assertFalse(os.path.exists(tmp_windows_release_file7))
        self.assertFalse(os.path.exists(tmp_macosx_debug_file8))
        self.assertFalse(os.path.exists(tmp_macosx_release_file9))

        self.assertTrue(os.path.exists(out_linux_debug_file10))
        self.assertTrue(os.path.exists(out_linux_release_file11))
        self.assertTrue(os.path.exists(out_windows_debug_file12))
        self.assertTrue(os.path.exists(out_windows_release_file13))
        self.assertTrue(os.path.exists(out_macosx_debug_file14))
        self.assertTrue(os.path.exists(out_macosx_release_file15))

    def testProjCleanup10(self):

        dep_linux_file1 = path_utils.concat_path(self.target_proj_dep_linux, "file1")
        dep_windows_file2 = path_utils.concat_path(self.target_proj_dep_windows, "file2")
        dep_macosx_file3 = path_utils.concat_path(self.target_proj_dep_macosx, "file3")

        tmp_linux_debug_file4 = path_utils.concat_path(self.target_proj_tmp_linux_debug, "file4")
        tmp_linux_release_file5 = path_utils.concat_path(self.target_proj_tmp_linux_release, "file5")
        tmp_windows_debug_file6 = path_utils.concat_path(self.target_proj_tmp_windows_debug, "file6")
        tmp_windows_release_file7 = path_utils.concat_path(self.target_proj_tmp_windows_release, "file7")
        tmp_macosx_debug_file8 = path_utils.concat_path(self.target_proj_tmp_macosx_debug, "file8")
        tmp_macosx_release_file9 = path_utils.concat_path(self.target_proj_tmp_macosx_release, "file9")

        out_linux_debug_file10 = path_utils.concat_path(self.target_proj_out_linux_debug, "file10")
        out_linux_release_file11 = path_utils.concat_path(self.target_proj_out_linux_release, "file11")
        out_windows_debug_file12 = path_utils.concat_path(self.target_proj_out_windows_debug, "file12")
        out_windows_release_file13 = path_utils.concat_path(self.target_proj_out_windows_release, "file13")
        out_macosx_debug_file14 = path_utils.concat_path(self.target_proj_out_macosx_debug, "file14")
        out_macosx_release_file15 = path_utils.concat_path(self.target_proj_out_macosx_release, "file15")

        self.assertTrue(create_and_write_file.create_file_contents(dep_linux_file1, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(dep_windows_file2, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(dep_macosx_file3, "contents"))

        self.assertTrue(create_and_write_file.create_file_contents(tmp_linux_debug_file4, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(tmp_linux_release_file5, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(tmp_windows_debug_file6, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(tmp_windows_release_file7, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(tmp_macosx_debug_file8, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(tmp_macosx_release_file9, "contents"))

        self.assertTrue(create_and_write_file.create_file_contents(out_linux_debug_file10, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(out_linux_release_file11, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(out_windows_debug_file12, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(out_windows_release_file13, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(out_macosx_debug_file14, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(out_macosx_release_file15, "contents"))

        self.assertTrue(os.path.exists(dep_linux_file1))
        self.assertTrue(os.path.exists(dep_windows_file2))
        self.assertTrue(os.path.exists(dep_macosx_file3))

        self.assertTrue(os.path.exists(tmp_linux_debug_file4))
        self.assertTrue(os.path.exists(tmp_linux_release_file5))
        self.assertTrue(os.path.exists(tmp_windows_debug_file6))
        self.assertTrue(os.path.exists(tmp_windows_release_file7))
        self.assertTrue(os.path.exists(tmp_macosx_debug_file8))
        self.assertTrue(os.path.exists(tmp_macosx_release_file9))

        self.assertTrue(os.path.exists(out_linux_debug_file10))
        self.assertTrue(os.path.exists(out_linux_release_file11))
        self.assertTrue(os.path.exists(out_windows_debug_file12))
        self.assertTrue(os.path.exists(out_windows_release_file13))
        self.assertTrue(os.path.exists(out_macosx_debug_file14))
        self.assertTrue(os.path.exists(out_macosx_release_file15))

        v, r = proj_cleanup.proj_cleanup(self.target_proj, False, False, True)
        self.assertTrue(v)
        self.assertEqual(r, None)

        self.assertTrue(os.path.exists(dep_linux_file1))
        self.assertTrue(os.path.exists(dep_windows_file2))
        self.assertTrue(os.path.exists(dep_macosx_file3))

        self.assertTrue(os.path.exists(tmp_linux_debug_file4))
        self.assertTrue(os.path.exists(tmp_linux_release_file5))
        self.assertTrue(os.path.exists(tmp_windows_debug_file6))
        self.assertTrue(os.path.exists(tmp_windows_release_file7))
        self.assertTrue(os.path.exists(tmp_macosx_debug_file8))
        self.assertTrue(os.path.exists(tmp_macosx_release_file9))

        self.assertFalse(os.path.exists(out_linux_debug_file10))
        self.assertFalse(os.path.exists(out_linux_release_file11))
        self.assertFalse(os.path.exists(out_windows_debug_file12))
        self.assertFalse(os.path.exists(out_windows_release_file13))
        self.assertFalse(os.path.exists(out_macosx_debug_file14))
        self.assertFalse(os.path.exists(out_macosx_release_file15))

    def testProjCleanup11(self):

        dep_linux_file1 = path_utils.concat_path(self.target_proj_dep_linux, "file1")
        dep_windows_file2 = path_utils.concat_path(self.target_proj_dep_windows, "file2")
        dep_macosx_file3 = path_utils.concat_path(self.target_proj_dep_macosx, "file3")

        tmp_linux_debug_file4 = path_utils.concat_path(self.target_proj_tmp_linux_debug, "file4")
        tmp_linux_release_file5 = path_utils.concat_path(self.target_proj_tmp_linux_release, "file5")
        tmp_windows_debug_file6 = path_utils.concat_path(self.target_proj_tmp_windows_debug, "file6")
        tmp_windows_release_file7 = path_utils.concat_path(self.target_proj_tmp_windows_release, "file7")
        tmp_macosx_debug_file8 = path_utils.concat_path(self.target_proj_tmp_macosx_debug, "file8")
        tmp_macosx_release_file9 = path_utils.concat_path(self.target_proj_tmp_macosx_release, "file9")

        out_linux_debug_file10 = path_utils.concat_path(self.target_proj_out_linux_debug, "file10")
        out_linux_release_file11 = path_utils.concat_path(self.target_proj_out_linux_release, "file11")
        out_windows_debug_file12 = path_utils.concat_path(self.target_proj_out_windows_debug, "file12")
        out_windows_release_file13 = path_utils.concat_path(self.target_proj_out_windows_release, "file13")
        out_macosx_debug_file14 = path_utils.concat_path(self.target_proj_out_macosx_debug, "file14")
        out_macosx_release_file15 = path_utils.concat_path(self.target_proj_out_macosx_release, "file15")

        self.assertTrue(create_and_write_file.create_file_contents(dep_linux_file1, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(dep_windows_file2, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(dep_macosx_file3, "contents"))

        self.assertTrue(create_and_write_file.create_file_contents(tmp_linux_debug_file4, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(tmp_linux_release_file5, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(tmp_windows_debug_file6, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(tmp_windows_release_file7, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(tmp_macosx_debug_file8, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(tmp_macosx_release_file9, "contents"))

        self.assertTrue(create_and_write_file.create_file_contents(out_linux_debug_file10, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(out_linux_release_file11, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(out_windows_debug_file12, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(out_windows_release_file13, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(out_macosx_debug_file14, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(out_macosx_release_file15, "contents"))

        self.assertTrue(os.path.exists(dep_linux_file1))
        self.assertTrue(os.path.exists(dep_windows_file2))
        self.assertTrue(os.path.exists(dep_macosx_file3))

        self.assertTrue(os.path.exists(tmp_linux_debug_file4))
        self.assertTrue(os.path.exists(tmp_linux_release_file5))
        self.assertTrue(os.path.exists(tmp_windows_debug_file6))
        self.assertTrue(os.path.exists(tmp_windows_release_file7))
        self.assertTrue(os.path.exists(tmp_macosx_debug_file8))
        self.assertTrue(os.path.exists(tmp_macosx_release_file9))

        self.assertTrue(os.path.exists(out_linux_debug_file10))
        self.assertTrue(os.path.exists(out_linux_release_file11))
        self.assertTrue(os.path.exists(out_windows_debug_file12))
        self.assertTrue(os.path.exists(out_windows_release_file13))
        self.assertTrue(os.path.exists(out_macosx_debug_file14))
        self.assertTrue(os.path.exists(out_macosx_release_file15))

        v, r = proj_cleanup.proj_cleanup(self.target_proj, True, True, True)
        self.assertTrue(v)
        self.assertEqual(r, None)

        self.assertFalse(os.path.exists(dep_linux_file1))
        self.assertFalse(os.path.exists(dep_windows_file2))
        self.assertFalse(os.path.exists(dep_macosx_file3))

        self.assertFalse(os.path.exists(tmp_linux_debug_file4))
        self.assertFalse(os.path.exists(tmp_linux_release_file5))
        self.assertFalse(os.path.exists(tmp_windows_debug_file6))
        self.assertFalse(os.path.exists(tmp_windows_release_file7))
        self.assertFalse(os.path.exists(tmp_macosx_debug_file8))
        self.assertFalse(os.path.exists(tmp_macosx_release_file9))

        self.assertFalse(os.path.exists(out_linux_debug_file10))
        self.assertFalse(os.path.exists(out_linux_release_file11))
        self.assertFalse(os.path.exists(out_windows_debug_file12))
        self.assertFalse(os.path.exists(out_windows_release_file13))
        self.assertFalse(os.path.exists(out_macosx_debug_file14))
        self.assertFalse(os.path.exists(out_macosx_release_file15))

    def testProjCleanup12(self):

        self.assertTrue(os.path.isdir(self.target_proj_dep_linux))
        self.assertTrue(os.path.isdir(self.target_proj_dep_windows))
        self.assertTrue(os.path.isdir(self.target_proj_dep_macosx))

        self.assertTrue(os.path.isdir(self.target_proj_tmp_linux_debug))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_linux_release))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_windows_debug))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_windows_release))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_macosx_debug))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_macosx_release))

        self.assertTrue(os.path.isdir(self.target_proj_out_linux_debug))
        self.assertTrue(os.path.isdir(self.target_proj_out_linux_release))
        self.assertTrue(os.path.isdir(self.target_proj_out_windows_debug))
        self.assertTrue(os.path.isdir(self.target_proj_out_windows_release))
        self.assertTrue(os.path.isdir(self.target_proj_out_macosx_debug))
        self.assertTrue(os.path.isdir(self.target_proj_out_macosx_release))

        v, r = proj_cleanup.proj_cleanup(self.target_proj, False, False, False)
        self.assertTrue(v)
        self.assertEqual(r, None)

        self.assertTrue(os.path.isdir(self.target_proj_dep_linux))
        self.assertTrue(os.path.isdir(self.target_proj_dep_windows))
        self.assertTrue(os.path.isdir(self.target_proj_dep_macosx))

        self.assertTrue(os.path.isdir(self.target_proj_tmp_linux_debug))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_linux_release))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_windows_debug))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_windows_release))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_macosx_debug))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_macosx_release))

        self.assertTrue(os.path.isdir(self.target_proj_out_linux_debug))
        self.assertTrue(os.path.isdir(self.target_proj_out_linux_release))
        self.assertTrue(os.path.isdir(self.target_proj_out_windows_debug))
        self.assertTrue(os.path.isdir(self.target_proj_out_windows_release))
        self.assertTrue(os.path.isdir(self.target_proj_out_macosx_debug))
        self.assertTrue(os.path.isdir(self.target_proj_out_macosx_release))

    def testProjCleanup13(self):

        self.assertTrue(os.path.isdir(self.target_proj_dep_linux))
        self.assertTrue(os.path.isdir(self.target_proj_dep_windows))
        self.assertTrue(os.path.isdir(self.target_proj_dep_macosx))

        self.assertTrue(os.path.isdir(self.target_proj_tmp_linux_debug))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_linux_release))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_windows_debug))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_windows_release))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_macosx_debug))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_macosx_release))

        self.assertTrue(os.path.isdir(self.target_proj_out_linux_debug))
        self.assertTrue(os.path.isdir(self.target_proj_out_linux_release))
        self.assertTrue(os.path.isdir(self.target_proj_out_windows_debug))
        self.assertTrue(os.path.isdir(self.target_proj_out_windows_release))
        self.assertTrue(os.path.isdir(self.target_proj_out_macosx_debug))
        self.assertTrue(os.path.isdir(self.target_proj_out_macosx_release))

        v, r = proj_cleanup.proj_cleanup(self.target_proj, True, True, True)
        self.assertTrue(v)
        self.assertEqual(r, None)

        self.assertTrue(os.path.isdir(self.target_proj_dep_linux))
        self.assertTrue(os.path.isdir(self.target_proj_dep_windows))
        self.assertTrue(os.path.isdir(self.target_proj_dep_macosx))

        self.assertTrue(os.path.isdir(self.target_proj_tmp_linux_debug))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_linux_release))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_windows_debug))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_windows_release))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_macosx_debug))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_macosx_release))

        self.assertTrue(os.path.isdir(self.target_proj_out_linux_debug))
        self.assertTrue(os.path.isdir(self.target_proj_out_linux_release))
        self.assertTrue(os.path.isdir(self.target_proj_out_windows_debug))
        self.assertTrue(os.path.isdir(self.target_proj_out_windows_release))
        self.assertTrue(os.path.isdir(self.target_proj_out_macosx_debug))
        self.assertTrue(os.path.isdir(self.target_proj_out_macosx_release))

    def testProjCleanup14(self):

        self.assertTrue(path_utils.remove_path(self.target_proj_dep_linux))
        self.assertTrue(path_utils.remove_path(self.target_proj_dep_windows))
        self.assertTrue(path_utils.remove_path(self.target_proj_dep_macosx))

        self.assertTrue(create_and_write_file.create_file_contents(self.target_proj_dep_linux, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(self.target_proj_dep_windows, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(self.target_proj_dep_macosx, "contents"))

        self.assertTrue(os.path.exists(self.target_proj_dep_linux))
        self.assertTrue(os.path.exists(self.target_proj_dep_windows))
        self.assertTrue(os.path.exists(self.target_proj_dep_macosx))

        self.assertFalse(os.path.isdir(self.target_proj_dep_linux))
        self.assertFalse(os.path.isdir(self.target_proj_dep_windows))
        self.assertFalse(os.path.isdir(self.target_proj_dep_macosx))

        self.assertTrue(os.path.isdir(self.target_proj_tmp_linux_debug))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_linux_release))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_windows_debug))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_windows_release))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_macosx_debug))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_macosx_release))

        self.assertTrue(os.path.isdir(self.target_proj_out_linux_debug))
        self.assertTrue(os.path.isdir(self.target_proj_out_linux_release))
        self.assertTrue(os.path.isdir(self.target_proj_out_windows_debug))
        self.assertTrue(os.path.isdir(self.target_proj_out_windows_release))
        self.assertTrue(os.path.isdir(self.target_proj_out_macosx_debug))
        self.assertTrue(os.path.isdir(self.target_proj_out_macosx_release))

        v, r = proj_cleanup.proj_cleanup(self.target_proj, True, False, False)
        self.assertTrue(v)
        self.assertEqual(r, None)

        self.assertTrue(os.path.isdir(self.target_proj_dep_linux))
        self.assertTrue(os.path.isdir(self.target_proj_dep_windows))
        self.assertTrue(os.path.isdir(self.target_proj_dep_macosx))

        self.assertTrue(os.path.isdir(self.target_proj_tmp_linux_debug))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_linux_release))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_windows_debug))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_windows_release))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_macosx_debug))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_macosx_release))

        self.assertTrue(os.path.isdir(self.target_proj_out_linux_debug))
        self.assertTrue(os.path.isdir(self.target_proj_out_linux_release))
        self.assertTrue(os.path.isdir(self.target_proj_out_windows_debug))
        self.assertTrue(os.path.isdir(self.target_proj_out_windows_release))
        self.assertTrue(os.path.isdir(self.target_proj_out_macosx_debug))
        self.assertTrue(os.path.isdir(self.target_proj_out_macosx_release))

    def testProjCleanup15(self):

        self.assertTrue(path_utils.remove_path(self.target_proj_dep_linux))
        self.assertTrue(path_utils.remove_path(self.target_proj_dep_windows))
        self.assertTrue(path_utils.remove_path(self.target_proj_dep_macosx))

        self.assertTrue(create_and_write_file.create_file_contents(self.target_proj_dep_linux, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(self.target_proj_dep_windows, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(self.target_proj_dep_macosx, "contents"))

        self.assertTrue(os.path.exists(self.target_proj_dep_linux))
        self.assertTrue(os.path.exists(self.target_proj_dep_windows))
        self.assertTrue(os.path.exists(self.target_proj_dep_macosx))

        self.assertFalse(os.path.isdir(self.target_proj_dep_linux))
        self.assertFalse(os.path.isdir(self.target_proj_dep_windows))
        self.assertFalse(os.path.isdir(self.target_proj_dep_macosx))

        self.assertTrue(os.path.isdir(self.target_proj_tmp_linux_debug))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_linux_release))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_windows_debug))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_windows_release))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_macosx_debug))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_macosx_release))

        self.assertTrue(os.path.isdir(self.target_proj_out_linux_debug))
        self.assertTrue(os.path.isdir(self.target_proj_out_linux_release))
        self.assertTrue(os.path.isdir(self.target_proj_out_windows_debug))
        self.assertTrue(os.path.isdir(self.target_proj_out_windows_release))
        self.assertTrue(os.path.isdir(self.target_proj_out_macosx_debug))
        self.assertTrue(os.path.isdir(self.target_proj_out_macosx_release))

        v, r = proj_cleanup.proj_cleanup(self.target_proj, False, False, False)
        self.assertTrue(v)
        self.assertEqual(r, None)

        self.assertTrue(os.path.exists(self.target_proj_dep_linux))
        self.assertTrue(os.path.exists(self.target_proj_dep_windows))
        self.assertTrue(os.path.exists(self.target_proj_dep_macosx))

        self.assertFalse(os.path.isdir(self.target_proj_dep_linux))
        self.assertFalse(os.path.isdir(self.target_proj_dep_windows))
        self.assertFalse(os.path.isdir(self.target_proj_dep_macosx))

        self.assertTrue(os.path.isdir(self.target_proj_tmp_linux_debug))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_linux_release))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_windows_debug))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_windows_release))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_macosx_debug))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_macosx_release))

        self.assertTrue(os.path.isdir(self.target_proj_out_linux_debug))
        self.assertTrue(os.path.isdir(self.target_proj_out_linux_release))
        self.assertTrue(os.path.isdir(self.target_proj_out_windows_debug))
        self.assertTrue(os.path.isdir(self.target_proj_out_windows_release))
        self.assertTrue(os.path.isdir(self.target_proj_out_macosx_debug))
        self.assertTrue(os.path.isdir(self.target_proj_out_macosx_release))

    def testProjCleanup16(self):

        self.assertTrue(path_utils.remove_path(self.target_proj_tmp_linux_debug))
        self.assertTrue(path_utils.remove_path(self.target_proj_tmp_linux_release))
        self.assertTrue(path_utils.remove_path(self.target_proj_tmp_windows_debug))
        self.assertTrue(path_utils.remove_path(self.target_proj_tmp_windows_release))
        self.assertTrue(path_utils.remove_path(self.target_proj_tmp_macosx_debug))
        self.assertTrue(path_utils.remove_path(self.target_proj_tmp_macosx_release))

        self.assertTrue(create_and_write_file.create_file_contents(self.target_proj_tmp_linux_debug, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(self.target_proj_tmp_linux_release, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(self.target_proj_tmp_windows_debug, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(self.target_proj_tmp_windows_release, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(self.target_proj_tmp_macosx_debug, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(self.target_proj_tmp_macosx_release, "contents"))

        self.assertTrue(os.path.exists(self.target_proj_tmp_linux_debug))
        self.assertTrue(os.path.exists(self.target_proj_tmp_linux_release))
        self.assertTrue(os.path.exists(self.target_proj_tmp_windows_debug))
        self.assertTrue(os.path.exists(self.target_proj_tmp_windows_release))
        self.assertTrue(os.path.exists(self.target_proj_tmp_macosx_debug))
        self.assertTrue(os.path.exists(self.target_proj_tmp_macosx_release))

        self.assertTrue(os.path.isdir(self.target_proj_dep_linux))
        self.assertTrue(os.path.isdir(self.target_proj_dep_windows))
        self.assertTrue(os.path.isdir(self.target_proj_dep_macosx))

        self.assertFalse(os.path.isdir(self.target_proj_tmp_linux_debug))
        self.assertFalse(os.path.isdir(self.target_proj_tmp_linux_release))
        self.assertFalse(os.path.isdir(self.target_proj_tmp_windows_debug))
        self.assertFalse(os.path.isdir(self.target_proj_tmp_windows_release))
        self.assertFalse(os.path.isdir(self.target_proj_tmp_macosx_debug))
        self.assertFalse(os.path.isdir(self.target_proj_tmp_macosx_release))

        self.assertTrue(os.path.isdir(self.target_proj_out_linux_debug))
        self.assertTrue(os.path.isdir(self.target_proj_out_linux_release))
        self.assertTrue(os.path.isdir(self.target_proj_out_windows_debug))
        self.assertTrue(os.path.isdir(self.target_proj_out_windows_release))
        self.assertTrue(os.path.isdir(self.target_proj_out_macosx_debug))
        self.assertTrue(os.path.isdir(self.target_proj_out_macosx_release))

        v, r = proj_cleanup.proj_cleanup(self.target_proj, False, True, False)
        self.assertTrue(v)
        self.assertEqual(r, None)

        self.assertTrue(os.path.isdir(self.target_proj_dep_linux))
        self.assertTrue(os.path.isdir(self.target_proj_dep_windows))
        self.assertTrue(os.path.isdir(self.target_proj_dep_macosx))

        self.assertTrue(os.path.isdir(self.target_proj_tmp_linux_debug))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_linux_release))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_windows_debug))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_windows_release))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_macosx_debug))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_macosx_release))

        self.assertTrue(os.path.isdir(self.target_proj_out_linux_debug))
        self.assertTrue(os.path.isdir(self.target_proj_out_linux_release))
        self.assertTrue(os.path.isdir(self.target_proj_out_windows_debug))
        self.assertTrue(os.path.isdir(self.target_proj_out_windows_release))
        self.assertTrue(os.path.isdir(self.target_proj_out_macosx_debug))
        self.assertTrue(os.path.isdir(self.target_proj_out_macosx_release))

    def testProjCleanup16(self):

        self.assertTrue(path_utils.remove_path(self.target_proj_tmp_linux_debug))
        self.assertTrue(path_utils.remove_path(self.target_proj_tmp_linux_release))
        self.assertTrue(path_utils.remove_path(self.target_proj_tmp_windows_debug))
        self.assertTrue(path_utils.remove_path(self.target_proj_tmp_windows_release))
        self.assertTrue(path_utils.remove_path(self.target_proj_tmp_macosx_debug))
        self.assertTrue(path_utils.remove_path(self.target_proj_tmp_macosx_release))

        self.assertTrue(create_and_write_file.create_file_contents(self.target_proj_tmp_linux_debug, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(self.target_proj_tmp_linux_release, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(self.target_proj_tmp_windows_debug, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(self.target_proj_tmp_windows_release, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(self.target_proj_tmp_macosx_debug, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(self.target_proj_tmp_macosx_release, "contents"))

        self.assertTrue(os.path.exists(self.target_proj_tmp_linux_debug))
        self.assertTrue(os.path.exists(self.target_proj_tmp_linux_release))
        self.assertTrue(os.path.exists(self.target_proj_tmp_windows_debug))
        self.assertTrue(os.path.exists(self.target_proj_tmp_windows_release))
        self.assertTrue(os.path.exists(self.target_proj_tmp_macosx_debug))
        self.assertTrue(os.path.exists(self.target_proj_tmp_macosx_release))

        self.assertTrue(os.path.isdir(self.target_proj_dep_linux))
        self.assertTrue(os.path.isdir(self.target_proj_dep_windows))
        self.assertTrue(os.path.isdir(self.target_proj_dep_macosx))

        self.assertFalse(os.path.isdir(self.target_proj_tmp_linux_debug))
        self.assertFalse(os.path.isdir(self.target_proj_tmp_linux_release))
        self.assertFalse(os.path.isdir(self.target_proj_tmp_windows_debug))
        self.assertFalse(os.path.isdir(self.target_proj_tmp_windows_release))
        self.assertFalse(os.path.isdir(self.target_proj_tmp_macosx_debug))
        self.assertFalse(os.path.isdir(self.target_proj_tmp_macosx_release))

        self.assertTrue(os.path.isdir(self.target_proj_out_linux_debug))
        self.assertTrue(os.path.isdir(self.target_proj_out_linux_release))
        self.assertTrue(os.path.isdir(self.target_proj_out_windows_debug))
        self.assertTrue(os.path.isdir(self.target_proj_out_windows_release))
        self.assertTrue(os.path.isdir(self.target_proj_out_macosx_debug))
        self.assertTrue(os.path.isdir(self.target_proj_out_macosx_release))

        v, r = proj_cleanup.proj_cleanup(self.target_proj, False, False, False)
        self.assertTrue(v)
        self.assertEqual(r, None)

        self.assertTrue(os.path.exists(self.target_proj_tmp_linux_debug))
        self.assertTrue(os.path.exists(self.target_proj_tmp_linux_release))
        self.assertTrue(os.path.exists(self.target_proj_tmp_windows_debug))
        self.assertTrue(os.path.exists(self.target_proj_tmp_windows_release))
        self.assertTrue(os.path.exists(self.target_proj_tmp_macosx_debug))
        self.assertTrue(os.path.exists(self.target_proj_tmp_macosx_release))

        self.assertTrue(os.path.isdir(self.target_proj_dep_linux))
        self.assertTrue(os.path.isdir(self.target_proj_dep_windows))
        self.assertTrue(os.path.isdir(self.target_proj_dep_macosx))

        self.assertFalse(os.path.isdir(self.target_proj_tmp_linux_debug))
        self.assertFalse(os.path.isdir(self.target_proj_tmp_linux_release))
        self.assertFalse(os.path.isdir(self.target_proj_tmp_windows_debug))
        self.assertFalse(os.path.isdir(self.target_proj_tmp_windows_release))
        self.assertFalse(os.path.isdir(self.target_proj_tmp_macosx_debug))
        self.assertFalse(os.path.isdir(self.target_proj_tmp_macosx_release))

        self.assertTrue(os.path.isdir(self.target_proj_out_linux_debug))
        self.assertTrue(os.path.isdir(self.target_proj_out_linux_release))
        self.assertTrue(os.path.isdir(self.target_proj_out_windows_debug))
        self.assertTrue(os.path.isdir(self.target_proj_out_windows_release))
        self.assertTrue(os.path.isdir(self.target_proj_out_macosx_debug))
        self.assertTrue(os.path.isdir(self.target_proj_out_macosx_release))

    def testProjCleanup17(self):

        self.assertTrue(path_utils.remove_path(self.target_proj_out_linux_debug))
        self.assertTrue(path_utils.remove_path(self.target_proj_out_linux_release))
        self.assertTrue(path_utils.remove_path(self.target_proj_out_windows_debug))
        self.assertTrue(path_utils.remove_path(self.target_proj_out_windows_release))
        self.assertTrue(path_utils.remove_path(self.target_proj_out_macosx_debug))
        self.assertTrue(path_utils.remove_path(self.target_proj_out_macosx_release))

        self.assertTrue(create_and_write_file.create_file_contents(self.target_proj_out_linux_debug, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(self.target_proj_out_linux_release, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(self.target_proj_out_windows_debug, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(self.target_proj_out_windows_release, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(self.target_proj_out_macosx_debug, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(self.target_proj_out_macosx_release, "contents"))

        self.assertTrue(os.path.exists(self.target_proj_out_linux_debug))
        self.assertTrue(os.path.exists(self.target_proj_out_linux_release))
        self.assertTrue(os.path.exists(self.target_proj_out_windows_debug))
        self.assertTrue(os.path.exists(self.target_proj_out_windows_release))
        self.assertTrue(os.path.exists(self.target_proj_out_macosx_debug))
        self.assertTrue(os.path.exists(self.target_proj_out_macosx_release))

        self.assertTrue(os.path.isdir(self.target_proj_dep_linux))
        self.assertTrue(os.path.isdir(self.target_proj_dep_windows))
        self.assertTrue(os.path.isdir(self.target_proj_dep_macosx))

        self.assertTrue(os.path.isdir(self.target_proj_tmp_linux_debug))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_linux_release))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_windows_debug))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_windows_release))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_macosx_debug))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_macosx_release))

        self.assertFalse(os.path.isdir(self.target_proj_out_linux_debug))
        self.assertFalse(os.path.isdir(self.target_proj_out_linux_release))
        self.assertFalse(os.path.isdir(self.target_proj_out_windows_debug))
        self.assertFalse(os.path.isdir(self.target_proj_out_windows_release))
        self.assertFalse(os.path.isdir(self.target_proj_out_macosx_debug))
        self.assertFalse(os.path.isdir(self.target_proj_out_macosx_release))

        v, r = proj_cleanup.proj_cleanup(self.target_proj, False, False, True)
        self.assertTrue(v)
        self.assertEqual(r, None)

        self.assertTrue(os.path.isdir(self.target_proj_dep_linux))
        self.assertTrue(os.path.isdir(self.target_proj_dep_windows))
        self.assertTrue(os.path.isdir(self.target_proj_dep_macosx))

        self.assertTrue(os.path.isdir(self.target_proj_tmp_linux_debug))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_linux_release))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_windows_debug))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_windows_release))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_macosx_debug))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_macosx_release))

        self.assertTrue(os.path.isdir(self.target_proj_out_linux_debug))
        self.assertTrue(os.path.isdir(self.target_proj_out_linux_release))
        self.assertTrue(os.path.isdir(self.target_proj_out_windows_debug))
        self.assertTrue(os.path.isdir(self.target_proj_out_windows_release))
        self.assertTrue(os.path.isdir(self.target_proj_out_macosx_debug))
        self.assertTrue(os.path.isdir(self.target_proj_out_macosx_release))

    def testProjCleanup18(self):

        self.assertTrue(path_utils.remove_path(self.target_proj_out_linux_debug))
        self.assertTrue(path_utils.remove_path(self.target_proj_out_linux_release))
        self.assertTrue(path_utils.remove_path(self.target_proj_out_windows_debug))
        self.assertTrue(path_utils.remove_path(self.target_proj_out_windows_release))
        self.assertTrue(path_utils.remove_path(self.target_proj_out_macosx_debug))
        self.assertTrue(path_utils.remove_path(self.target_proj_out_macosx_release))

        self.assertTrue(create_and_write_file.create_file_contents(self.target_proj_out_linux_debug, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(self.target_proj_out_linux_release, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(self.target_proj_out_windows_debug, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(self.target_proj_out_windows_release, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(self.target_proj_out_macosx_debug, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(self.target_proj_out_macosx_release, "contents"))

        self.assertTrue(os.path.exists(self.target_proj_out_linux_debug))
        self.assertTrue(os.path.exists(self.target_proj_out_linux_release))
        self.assertTrue(os.path.exists(self.target_proj_out_windows_debug))
        self.assertTrue(os.path.exists(self.target_proj_out_windows_release))
        self.assertTrue(os.path.exists(self.target_proj_out_macosx_debug))
        self.assertTrue(os.path.exists(self.target_proj_out_macosx_release))

        self.assertTrue(os.path.isdir(self.target_proj_dep_linux))
        self.assertTrue(os.path.isdir(self.target_proj_dep_windows))
        self.assertTrue(os.path.isdir(self.target_proj_dep_macosx))

        self.assertTrue(os.path.isdir(self.target_proj_tmp_linux_debug))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_linux_release))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_windows_debug))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_windows_release))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_macosx_debug))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_macosx_release))

        self.assertFalse(os.path.isdir(self.target_proj_out_linux_debug))
        self.assertFalse(os.path.isdir(self.target_proj_out_linux_release))
        self.assertFalse(os.path.isdir(self.target_proj_out_windows_debug))
        self.assertFalse(os.path.isdir(self.target_proj_out_windows_release))
        self.assertFalse(os.path.isdir(self.target_proj_out_macosx_debug))
        self.assertFalse(os.path.isdir(self.target_proj_out_macosx_release))

        v, r = proj_cleanup.proj_cleanup(self.target_proj, False, False, False)
        self.assertTrue(v)
        self.assertEqual(r, None)

        self.assertTrue(os.path.exists(self.target_proj_out_linux_debug))
        self.assertTrue(os.path.exists(self.target_proj_out_linux_release))
        self.assertTrue(os.path.exists(self.target_proj_out_windows_debug))
        self.assertTrue(os.path.exists(self.target_proj_out_windows_release))
        self.assertTrue(os.path.exists(self.target_proj_out_macosx_debug))
        self.assertTrue(os.path.exists(self.target_proj_out_macosx_release))

        self.assertTrue(os.path.isdir(self.target_proj_dep_linux))
        self.assertTrue(os.path.isdir(self.target_proj_dep_windows))
        self.assertTrue(os.path.isdir(self.target_proj_dep_macosx))

        self.assertTrue(os.path.isdir(self.target_proj_tmp_linux_debug))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_linux_release))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_windows_debug))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_windows_release))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_macosx_debug))
        self.assertTrue(os.path.isdir(self.target_proj_tmp_macosx_release))

        self.assertFalse(os.path.isdir(self.target_proj_out_linux_debug))
        self.assertFalse(os.path.isdir(self.target_proj_out_linux_release))
        self.assertFalse(os.path.isdir(self.target_proj_out_windows_debug))
        self.assertFalse(os.path.isdir(self.target_proj_out_windows_release))
        self.assertFalse(os.path.isdir(self.target_proj_out_macosx_debug))
        self.assertFalse(os.path.isdir(self.target_proj_out_macosx_release))

    def testProjCleanup19(self):

        dep_file1 = path_utils.concat_path(self.target_proj_dep, "file1")
        tmp_file2 = path_utils.concat_path(self.target_proj_tmp, "file2")
        out_file3 = path_utils.concat_path(self.target_proj_out, "file3")

        self.assertTrue(create_and_write_file.create_file_contents(dep_file1, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(tmp_file2, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(out_file3, "contents"))

        self.assertTrue(os.path.exists(dep_file1))
        self.assertTrue(os.path.exists(tmp_file2))
        self.assertTrue(os.path.exists(out_file3))

        dep_linux_file1 = path_utils.concat_path(self.target_proj_dep_linux, "file1")
        dep_windows_file2 = path_utils.concat_path(self.target_proj_dep_windows, "file2")
        dep_macosx_file3 = path_utils.concat_path(self.target_proj_dep_macosx, "file3")

        tmp_linux_debug_file4 = path_utils.concat_path(self.target_proj_tmp_linux_debug, "file4")
        tmp_linux_release_file5 = path_utils.concat_path(self.target_proj_tmp_linux_release, "file5")
        tmp_windows_debug_file6 = path_utils.concat_path(self.target_proj_tmp_windows_debug, "file6")
        tmp_windows_release_file7 = path_utils.concat_path(self.target_proj_tmp_windows_release, "file7")
        tmp_macosx_debug_file8 = path_utils.concat_path(self.target_proj_tmp_macosx_debug, "file8")
        tmp_macosx_release_file9 = path_utils.concat_path(self.target_proj_tmp_macosx_release, "file9")

        out_linux_debug_file10 = path_utils.concat_path(self.target_proj_out_linux_debug, "file10")
        out_linux_release_file11 = path_utils.concat_path(self.target_proj_out_linux_release, "file11")
        out_windows_debug_file12 = path_utils.concat_path(self.target_proj_out_windows_debug, "file12")
        out_windows_release_file13 = path_utils.concat_path(self.target_proj_out_windows_release, "file13")
        out_macosx_debug_file14 = path_utils.concat_path(self.target_proj_out_macosx_debug, "file14")
        out_macosx_release_file15 = path_utils.concat_path(self.target_proj_out_macosx_release, "file15")

        self.assertTrue(create_and_write_file.create_file_contents(dep_linux_file1, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(dep_windows_file2, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(dep_macosx_file3, "contents"))

        self.assertTrue(create_and_write_file.create_file_contents(tmp_linux_debug_file4, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(tmp_linux_release_file5, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(tmp_windows_debug_file6, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(tmp_windows_release_file7, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(tmp_macosx_debug_file8, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(tmp_macosx_release_file9, "contents"))

        self.assertTrue(create_and_write_file.create_file_contents(out_linux_debug_file10, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(out_linux_release_file11, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(out_windows_debug_file12, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(out_windows_release_file13, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(out_macosx_debug_file14, "contents"))
        self.assertTrue(create_and_write_file.create_file_contents(out_macosx_release_file15, "contents"))

        self.assertTrue(os.path.exists(dep_linux_file1))
        self.assertTrue(os.path.exists(dep_windows_file2))
        self.assertTrue(os.path.exists(dep_macosx_file3))

        self.assertTrue(os.path.exists(tmp_linux_debug_file4))
        self.assertTrue(os.path.exists(tmp_linux_release_file5))
        self.assertTrue(os.path.exists(tmp_windows_debug_file6))
        self.assertTrue(os.path.exists(tmp_windows_release_file7))
        self.assertTrue(os.path.exists(tmp_macosx_debug_file8))
        self.assertTrue(os.path.exists(tmp_macosx_release_file9))

        self.assertTrue(os.path.exists(out_linux_debug_file10))
        self.assertTrue(os.path.exists(out_linux_release_file11))
        self.assertTrue(os.path.exists(out_windows_debug_file12))
        self.assertTrue(os.path.exists(out_windows_release_file13))
        self.assertTrue(os.path.exists(out_macosx_debug_file14))
        self.assertTrue(os.path.exists(out_macosx_release_file15))

        v, r = proj_cleanup.proj_cleanup(self.target_proj, True, True, True)
        self.assertTrue(v)
        self.assertEqual(r, None)

        self.assertTrue(os.path.exists(dep_file1))
        self.assertTrue(os.path.exists(tmp_file2))
        self.assertTrue(os.path.exists(out_file3))

        self.assertFalse(os.path.exists(dep_linux_file1))
        self.assertFalse(os.path.exists(dep_windows_file2))
        self.assertFalse(os.path.exists(dep_macosx_file3))

        self.assertFalse(os.path.exists(tmp_linux_debug_file4))
        self.assertFalse(os.path.exists(tmp_linux_release_file5))
        self.assertFalse(os.path.exists(tmp_windows_debug_file6))
        self.assertFalse(os.path.exists(tmp_windows_release_file7))
        self.assertFalse(os.path.exists(tmp_macosx_debug_file8))
        self.assertFalse(os.path.exists(tmp_macosx_release_file9))

        self.assertFalse(os.path.exists(out_linux_debug_file10))
        self.assertFalse(os.path.exists(out_linux_release_file11))
        self.assertFalse(os.path.exists(out_windows_debug_file12))
        self.assertFalse(os.path.exists(out_windows_release_file13))
        self.assertFalse(os.path.exists(out_macosx_debug_file14))
        self.assertFalse(os.path.exists(out_macosx_release_file15))

if __name__ == '__main__':
    unittest.main()
