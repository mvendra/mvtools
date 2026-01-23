#!/usr/bin/env python

import sys
import os
import shutil
import unittest
from unittest import mock
from unittest.mock import patch

import mvtools_test_fixture
import path_utils

import cmake_wrapper
import generic_run

class CmakeWrapperTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("cmake_wrapper_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        self.result_obj = generic_run.run_cmd_result(None, None, None, None)

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testExtractOptions1(self):

        self.result_obj.success = True
        self.result_obj.stdout = "test2"
        self.result_obj.stderr = "test3"

        self.folder1 = "folder1"
        self.folder2 = "folder2"
        self.folder1_full = path_utils.concat_path(self.test_dir, self.folder1)
        self.folder2_full = path_utils.concat_path(self.test_dir, self.folder2)

        with mock.patch("generic_run.run_cmd", return_value=(True, self.result_obj)) as dummy:
            v, r = cmake_wrapper.extract_options("test1", self.folder1_full, self.folder2_full)
            self.assertFalse(v)
            self.assertEqual(r, "Source path [%s] does not exist." % self.folder1_full)
            dummy.assert_not_called()

    def testExtractOptions2(self):

        self.result_obj.success = True
        self.result_obj.stdout = "test2"
        self.result_obj.stderr = "test3"

        self.folder1 = "folder1"
        self.folder2 = "folder2"
        self.folder1_full = path_utils.concat_path(self.test_dir, self.folder1)
        self.folder2_full = path_utils.concat_path(self.test_dir, self.folder2)
        os.mkdir(self.folder1_full)
        os.mkdir(self.folder2_full)

        with mock.patch("generic_run.run_cmd", return_value=(True, self.result_obj)) as dummy:
            v, r = cmake_wrapper.extract_options("test1", self.folder1_full, self.folder2_full)
            v, r = cmake_wrapper.extract_options("test1", self.folder1_full, self.folder2_full)
            self.assertFalse(v)
            self.assertEqual(r, "Temp path [%s] already exists." % self.folder2_full)
            dummy.assert_not_called()

    def testExtractOptions3(self):

        self.result_obj.success = True
        self.result_obj.stdout = "test2"
        self.result_obj.stderr = "test3"

        self.folder1 = "folder1"
        self.folder2 = "folder2"
        self.folder1_full = path_utils.concat_path(self.test_dir, self.folder1)
        self.folder2_full = path_utils.concat_path(self.test_dir, self.folder2)
        os.mkdir(self.folder1_full)

        with mock.patch("generic_run.run_cmd", return_value=(True, self.result_obj)) as dummy:
            v, r = cmake_wrapper.extract_options("test1", self.folder1_full, self.folder2_full)
            self.assertTrue(v)
            self.assertTrue(r[0])
            self.assertEqual(r[1], "test2")
            self.assertEqual(r[2], "test3")
            dummy.assert_called_with(["test1", self.folder1_full, "-LAH"], use_cwd=self.folder2_full)

    def testConfigureAndGenerateFail1(self):
        with mock.patch("generic_run.run_cmd", return_value=(True, self.result_obj)) as dummy:
            v, r = cmake_wrapper.configure_and_generate("test3", "test4", "test5", "test6", None)
            self.assertFalse(v)

    def testConfigureAndGenerateFail2(self):
        self.result_obj.success = False
        self.result_obj.stdout = "test1"
        self.result_obj.stderr = "test2"
        with mock.patch("generic_run.run_cmd", return_value=(False, self.result_obj)) as dummy:
            v, r = cmake_wrapper.configure_and_generate("test3", "test4", "test5", "test6", {})
            self.assertFalse(v)
            self.assertEqual(r, "Failed running cmake configure-and-generate command: [test1][test2]")

    def testConfigureAndGenerate1(self):
        self.result_obj.success = True
        self.result_obj.stdout = "test1"
        self.result_obj.stderr = "test2"
        with mock.patch("generic_run.run_cmd", return_value=(True, self.result_obj)) as dummy:
            self.assertEqual(cmake_wrapper.configure_and_generate("test3", "test4", "test5", "test6", {}), (True, (True, "test1", "test2")))
            dummy.assert_called_with(["test3", "test4", "-G", "test6"], use_cwd="test5")

    def testConfigureAndGenerate2(self):
        self.result_obj.success = True
        self.result_obj.stdout = "test1"
        self.result_obj.stderr = "test2"
        with mock.patch("generic_run.run_cmd", return_value=(True, self.result_obj)) as dummy:
            self.assertEqual(cmake_wrapper.configure_and_generate("test3", "test4", "test5", "test6", {"optname": ("opttype", "optval")}), (True, (True, "test1", "test2")))
            dummy.assert_called_with(["test3", "test4", "-G", "test6", "-Doptname:opttype=optval"], use_cwd="test5")

    def testConfigureAndGenerate3(self):
        self.result_obj.success = True
        self.result_obj.stdout = "test1"
        self.result_obj.stderr = "test2"
        with mock.patch("generic_run.run_cmd", return_value=(True, self.result_obj)) as dummy:
            self.assertEqual(cmake_wrapper.configure_and_generate(None, "test4", "test5", "test6", {}), (True, (True, "test1", "test2")))
            dummy.assert_called_with(["cmake", "test4", "-G", "test6"], use_cwd="test5")

    def testBuild1(self):

        self.result_obj.success = True
        self.result_obj.stdout = "test1"
        self.result_obj.stderr = "test2"

        self.folder1 = "folder1"
        self.folder1_full = path_utils.concat_path(self.test_dir, self.folder1)

        with mock.patch("generic_run.run_cmd", return_value=(True, self.result_obj)) as dummy:
            v, r = cmake_wrapper.build(None, self.folder1_full, False)
            self.assertFalse(v)
            self.assertEqual(r, "Target path [%s] does not exist." % self.folder1_full)

    def testBuild2(self):

        self.result_obj.success = True
        self.result_obj.stdout = "test1"
        self.result_obj.stderr = "test2"

        self.folder1 = "folder1"
        self.folder1_full = path_utils.concat_path(self.test_dir, self.folder1)

        os.mkdir(self.folder1_full)

        with mock.patch("generic_run.run_cmd", return_value=(True, self.result_obj)) as dummy:
            v, r = cmake_wrapper.build(None, self.folder1_full, False)
            self.assertTrue(v)
            self.assertEqual(r, (True, "test1", "test2"))
            dummy.assert_called_with(["cmake", "--build", self.folder1_full])

    def testBuild3(self):

        self.result_obj.success = True
        self.result_obj.stdout = "test1"
        self.result_obj.stderr = "test2"

        self.folder1 = "folder1"
        self.folder1_full = path_utils.concat_path(self.test_dir, self.folder1)

        os.mkdir(self.folder1_full)

        with mock.patch("generic_run.run_cmd", return_value=(True, self.result_obj)) as dummy:
            v, r = cmake_wrapper.build("test3", self.folder1_full, False)
            self.assertTrue(v)
            self.assertEqual(r, (True, "test1", "test2"))
            dummy.assert_called_with(["test3", "--build", self.folder1_full])

    def testBuild4(self):

        self.result_obj.success = True
        self.result_obj.stdout = "test1"
        self.result_obj.stderr = "test2"

        self.folder1 = "folder1"
        self.folder1_full = path_utils.concat_path(self.test_dir, self.folder1)

        os.mkdir(self.folder1_full)

        with mock.patch("generic_run.run_cmd", return_value=(True, self.result_obj)) as dummy:
            v, r = cmake_wrapper.build("test3", self.folder1_full, True)
            self.assertTrue(v)
            self.assertEqual(r, (True, "test1", "test2"))
            dummy.assert_called_with(["test3", "--build", self.folder1_full, "--parallel"])

    def testInstall1(self):

        self.result_obj.success = True
        self.result_obj.stdout = "test1"
        self.result_obj.stderr = "test2"

        self.folder1 = "folder1"
        self.folder1_full = path_utils.concat_path(self.test_dir, self.folder1)

        with mock.patch("generic_run.run_cmd", return_value=(True, self.result_obj)) as dummy:
            v, r = cmake_wrapper.install(None, self.folder1_full, None)
            self.assertFalse(v)
            self.assertEqual(r, "Target path [%s] does not exist." % self.folder1_full)

    def testInstall2(self):

        self.result_obj.success = True
        self.result_obj.stdout = "test1"
        self.result_obj.stderr = "test2"

        self.folder1 = "folder1"
        self.folder2 = "folder2"

        self.folder1_full = path_utils.concat_path(self.test_dir, self.folder1)
        self.folder2_full = path_utils.concat_path(self.test_dir, self.folder2)

        os.mkdir(self.folder1_full)

        with mock.patch("generic_run.run_cmd", return_value=(True, self.result_obj)) as dummy:
            v, r = cmake_wrapper.install("test3", self.folder1_full, self.folder2_full)
            self.assertFalse(v)
            self.assertEqual(r, "Prefix (path) [%s] does not exist." % self.folder2_full)

    def testInstall3(self):

        self.result_obj.success = False
        self.result_obj.stdout = "test1"
        self.result_obj.stderr = "test2"

        self.folder1 = "folder1"
        self.folder1_full = path_utils.concat_path(self.test_dir, self.folder1)

        os.mkdir(self.folder1_full)

        with mock.patch("generic_run.run_cmd", return_value=(False, self.result_obj)) as dummy:
            v, r = cmake_wrapper.install(None, self.folder1_full, None)
            self.assertFalse(v)
            self.assertEqual(r, "Failed running cmake install command: [test1][test2]")
            dummy.assert_called_with(["cmake", "--install", self.folder1_full])

    def testInstall4(self):

        self.result_obj.success = True
        self.result_obj.stdout = "test1"
        self.result_obj.stderr = "test2"

        self.folder1 = "folder1"
        self.folder1_full = path_utils.concat_path(self.test_dir, self.folder1)

        os.mkdir(self.folder1_full)

        with mock.patch("generic_run.run_cmd", return_value=(True, self.result_obj)) as dummy:
            v, r = cmake_wrapper.install(None, self.folder1_full, None)
            self.assertTrue(v)
            self.assertEqual(r, (True, "test1", "test2"))
            dummy.assert_called_with(["cmake", "--install", self.folder1_full])

    def testInstall5(self):

        self.result_obj.success = True
        self.result_obj.stdout = "test1"
        self.result_obj.stderr = "test2"

        self.folder1 = "folder1"
        self.folder1_full = path_utils.concat_path(self.test_dir, self.folder1)

        os.mkdir(self.folder1_full)

        with mock.patch("generic_run.run_cmd", return_value=(True, self.result_obj)) as dummy:
            v, r = cmake_wrapper.install("test3", self.folder1_full, None)
            self.assertTrue(v)
            self.assertEqual(r, (True, "test1", "test2"))
            dummy.assert_called_with(["test3", "--install", self.folder1_full])

    def testInstall6(self):

        self.result_obj.success = True
        self.result_obj.stdout = "test1"
        self.result_obj.stderr = "test2"

        self.folder1 = "folder1"
        self.folder2 = "folder2"

        self.folder1_full = path_utils.concat_path(self.test_dir, self.folder1)
        self.folder2_full = path_utils.concat_path(self.test_dir, self.folder2)

        os.mkdir(self.folder1_full)
        os.mkdir(self.folder2_full)

        with mock.patch("generic_run.run_cmd", return_value=(True, self.result_obj)) as dummy:
            v, r = cmake_wrapper.install("test3", self.folder1_full, self.folder2_full)
            self.assertTrue(v)
            self.assertEqual(r, (True, "test1", "test2"))
            dummy.assert_called_with(["test3", "--install", self.folder1_full, "--prefix", self.folder2_full])

if __name__ == "__main__":
    unittest.main()
