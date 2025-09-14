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

import zip_plugin

class ZipPluginTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("zip_plugin_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # the test task
        self.zip_task = zip_plugin.CustomTask()

        # existent path 1
        self.existent_path1 = path_utils.concat_path(self.test_dir, "existent_path1")
        os.mkdir(self.existent_path1)

        # existent path 2
        self.existent_path2 = path_utils.concat_path(self.test_dir, "existent_path2")
        os.mkdir(self.existent_path2)

        # nonexistent path 1
        self.nonexistent_path1 = path_utils.concat_path(self.test_dir, "nonexistent_path1")

        # existent archive 1
        self.existent_archive1 = path_utils.concat_path(self.test_dir, "existent_archive1.zip")
        create_and_write_file.create_file_contents(self.existent_archive1, "fake zip file")

        # nonexistent archive 1
        self.nonexistent_archive1 = path_utils.concat_path(self.test_dir, "nonexistent_archive1")

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testZipPluginReadParams1(self):

        local_params = {}
        self.zip_task.params = local_params

        v, r = self.zip_task._read_params()
        self.assertFalse(v)

    def testZipPluginReadParams2(self):

        local_params = {}
        local_params["operation"] = "dummy_value1"
        self.zip_task.params = local_params

        v, r = self.zip_task._read_params()
        self.assertFalse(v)

    def testZipPluginReadParams3(self):

        local_params = {}
        local_params["operation"] = "dummy_value1"
        local_params["target_archive"] = "dummy_value2"
        self.zip_task.params = local_params

        v, r = self.zip_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", None, None) )

    def testZipPluginReadParams4(self):

        local_params = {}
        local_params["operation"] = "dummy_value1"
        local_params["target_archive"] = "dummy_value2"
        local_params["source_path"] = "dummy_value3"
        self.zip_task.params = local_params

        v, r = self.zip_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", "dummy_value3", None) )

    def testZipPluginReadParams5(self):

        local_params = {}
        local_params["operation"] = "dummy_value1"
        local_params["target_archive"] = "dummy_value2"
        local_params["source_path"] = "dummy_value3"
        local_params["target_path"] = "dummy_value4"
        self.zip_task.params = local_params

        v, r = self.zip_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4") )

    def testZipPluginRunTask1(self):

        local_params = {}
        local_params["operation"] = "dummy_value1"
        local_params["target_archive"] = "dummy_value2"
        self.zip_task.params = local_params

        v, r = self.zip_task.run_task(print, "exe_name")
        self.assertFalse(v)

    def testZipPluginRunTask_CreatePackage1(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        local_params = {}
        local_params["operation"] = "create"
        local_params["target_archive"] = "dummy_value1"
        local_params["source_path"] = "dummy_value2"
        self.zip_task.params = local_params

        with mock.patch("zip_plugin.CustomTask.task_create_package", return_value=(True, None)) as dummy:
            v, r = self.zip_task.run_task(print, "exe_name")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(print, "dummy_value1", "dummy_value2")

    def testZipPluginRunTask_ExtractPackage1(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        local_params = {}
        local_params["operation"] = "extract"
        local_params["target_archive"] = "dummy_value1"
        local_params["target_path"] = "dummy_value2"
        self.zip_task.params = local_params

        with mock.patch("zip_plugin.CustomTask.task_extract_package", return_value=(True, None)) as dummy:
            v, r = self.zip_task.run_task(print, "exe_name")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(print, "dummy_value1", "dummy_value2")

    def testZipPluginTaskCreatePackage1(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        with mock.patch("zip_wrapper.make_pack", return_value=(True, None)) as dummy:
            v, r = self.zip_task.task_create_package(print, None, self.existent_path1)
            self.assertFalse(v)

    def testZipPluginTaskCreatePackage2(self):

        self.assertTrue(os.path.exists(self.existent_archive1))
        self.assertTrue(os.path.exists(self.existent_path1))

        with mock.patch("zip_wrapper.make_pack", return_value=(True, None)) as dummy:
            v, r = self.zip_task.task_create_package(print, self.existent_archive1, self.existent_path1)
            self.assertFalse(v)

    def testZipPluginTaskCreatePackage3(self):

        self.assertFalse(os.path.exists(self.nonexistent_archive1))

        with mock.patch("zip_wrapper.make_pack", return_value=(True, None)) as dummy:
            v, r = self.zip_task.task_create_package(print, self.nonexistent_archive1, None)
            self.assertFalse(v)

    def testZipPluginTaskCreatePackage4(self):

        self.assertFalse(os.path.exists(self.nonexistent_archive1))
        self.assertFalse(os.path.exists(self.nonexistent_path1))

        with mock.patch("zip_wrapper.make_pack", return_value=(True, None)) as dummy:
            v, r = self.zip_task.task_create_package(print, self.nonexistent_archive1, self.nonexistent_path1)
            self.assertFalse(v)

    def testZipPluginTaskCreatePackage5(self):

        self.assertFalse(os.path.exists(self.nonexistent_archive1))
        self.assertTrue(os.path.exists(self.existent_path1))

        with mock.patch("zip_wrapper.make_pack", return_value=(True, None)) as dummy:
            v, r = self.zip_task.task_create_package(print, self.nonexistent_archive1, [self.existent_path1])
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(self.nonexistent_archive1, [self.existent_path1])

    def testZipPluginTaskCreatePackage6(self):

        self.assertFalse(os.path.exists(self.nonexistent_archive1))
        self.assertTrue(os.path.exists(self.existent_path1))

        with mock.patch("zip_wrapper.make_pack", return_value=(True, None)) as dummy:
            v, r = self.zip_task.task_create_package(print, self.nonexistent_archive1, self.existent_path1)
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(self.nonexistent_archive1, [self.existent_path1])

    def testZipPluginTaskExtractPackage1(self):

        self.assertFalse(os.path.exists(self.nonexistent_path1))
        self.assertTrue(os.path.exists(self.existent_path2))

        with mock.patch("zip_wrapper.extract", return_value=(True, None)) as dummy:
            v, r = self.zip_task.task_extract_package(print, self.nonexistent_path1, self.existent_path2)
            self.assertFalse(v)

    def testZipPluginTaskExtractPackage2(self):

        self.assertTrue(os.path.exists(self.existent_path2))

        with mock.patch("zip_wrapper.extract", return_value=(True, None)) as dummy:
            v, r = self.zip_task.task_extract_package(print, self.existent_path1, None)
            self.assertFalse(v)

    def testZipPluginTaskExtractPackage3(self):

        self.assertTrue(os.path.exists(self.existent_path2))
        self.assertFalse(os.path.exists(self.nonexistent_path1))

        with mock.patch("zip_wrapper.extract", return_value=(True, None)) as dummy:
            v, r = self.zip_task.task_extract_package(print, self.existent_path1, self.nonexistent_path1)
            self.assertFalse(v)

    def testZipPluginTaskExtractPackage4(self):

        self.assertTrue(os.path.exists(self.existent_path1))
        self.assertTrue(os.path.exists(self.existent_path2))

        with mock.patch("zip_wrapper.extract", return_value=(True, None)) as dummy:
            v, r = self.zip_task.task_extract_package(print, self.existent_path1, self.existent_path2)
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(self.existent_path1, self.existent_path2)

if __name__ == "__main__":
    unittest.main()
