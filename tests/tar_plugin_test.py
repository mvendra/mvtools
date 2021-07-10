#!/usr/bin/env python3

import sys
import os
import shutil
import unittest
from unittest import mock
from unittest.mock import patch

import mvtools_test_fixture
import create_and_write_file
import path_utils

import tar_plugin

class TarPluginTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("tar_plugin_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # the test task
        self.tar_task = tar_plugin.CustomTask()

        # existent path 1
        self.existent_path1 = path_utils.concat_path(self.test_dir, "existent_path1")
        os.mkdir(self.existent_path1)

        # existent path 2
        self.existent_path2 = path_utils.concat_path(self.test_dir, "existent_path2")
        os.mkdir(self.existent_path2)

        # nonexistent path 1
        self.nonexistent_path1 = path_utils.concat_path(self.test_dir, "nonexistent_path1")

        # existent archive 1
        self.existent_archive1 = path_utils.concat_path(self.test_dir, "existent_archive1.tar")
        create_and_write_file.create_file_contents(self.existent_archive1, "fake tar file")

        # nonexistent archive 1
        self.nonexistent_archive1 = path_utils.concat_path(self.test_dir, "nonexistent_archive1")

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testTarPluginReadParams1(self):

        local_params = {}
        self.tar_task.params = local_params

        v, r = self.tar_task._read_params()
        self.assertFalse(v)

    def testTarPluginReadParams2(self):

        local_params = {}
        local_params["operation"] = "dummy_value1"
        self.tar_task.params = local_params

        v, r = self.tar_task._read_params()
        self.assertFalse(v)

    def testTarPluginReadParams3(self):

        local_params = {}
        local_params["operation"] = "dummy_value1"
        local_params["target_archive"] = "dummy_value2"
        self.tar_task.params = local_params

        v, r = self.tar_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", None, None) )

    def testTarPluginReadParams4(self):

        local_params = {}
        local_params["operation"] = "dummy_value1"
        local_params["target_archive"] = "dummy_value2"
        local_params["source_path"] = "dummy_value3"
        self.tar_task.params = local_params

        v, r = self.tar_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", "dummy_value3", None) )

    def testTarPluginReadParams5(self):

        local_params = {}
        local_params["operation"] = "dummy_value1"
        local_params["target_archive"] = "dummy_value2"
        local_params["source_path"] = "dummy_value3"
        local_params["target_path"] = "dummy_value4"
        self.tar_task.params = local_params

        v, r = self.tar_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4") )

    def testTarPluginRunTask1(self):

        local_params = {}
        local_params["operation"] = "dummy_value1"
        local_params["target_archive"] = "dummy_value2"
        self.tar_task.params = local_params

        v, r = self.tar_task.run_task(print, "exe_name")
        self.assertFalse(v)

    def testTarPluginRunTask_CreatePackage1(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        local_params = {}
        local_params["operation"] = "create"
        local_params["target_archive"] = "dummy_value1"
        local_params["source_path"] = "dummy_value2"
        self.tar_task.params = local_params

        with mock.patch("tar_plugin.CustomTask.task_create_package", return_value=(True, None)) as dummy:
            v, r = self.tar_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(print, "dummy_value1", "dummy_value2")

    def testTarPluginRunTask_ExtractPackage1(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        local_params = {}
        local_params["operation"] = "extract"
        local_params["target_archive"] = "dummy_value1"
        local_params["target_path"] = "dummy_value2"
        self.tar_task.params = local_params

        with mock.patch("tar_plugin.CustomTask.task_extract_package", return_value=(True, None)) as dummy:
            v, r = self.tar_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(print, "dummy_value1", "dummy_value2")

    def testTarPluginTaskCreatePackage1(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        with mock.patch("tar_wrapper.make_pack", return_value=(True, None)) as dummy:
            v, r = self.tar_task.task_create_package(print, None, self.existent_path1)
            self.assertFalse(v)

    def testTarPluginTaskCreatePackage2(self):

        self.assertTrue(os.path.exists(self.existent_archive1))
        self.assertTrue(os.path.exists(self.existent_path1))

        with mock.patch("tar_wrapper.make_pack", return_value=(True, None)) as dummy:
            v, r = self.tar_task.task_create_package(print, self.existent_archive1, self.existent_path1)
            self.assertFalse(v)

    def testTarPluginTaskCreatePackage3(self):

        self.assertFalse(os.path.exists(self.nonexistent_archive1))

        with mock.patch("tar_wrapper.make_pack", return_value=(True, None)) as dummy:
            v, r = self.tar_task.task_create_package(print, self.nonexistent_archive1, None)
            self.assertFalse(v)

    def testTarPluginTaskCreatePackage4(self):

        self.assertFalse(os.path.exists(self.nonexistent_archive1))
        self.assertFalse(os.path.exists(self.nonexistent_path1))

        with mock.patch("tar_wrapper.make_pack", return_value=(True, None)) as dummy:
            v, r = self.tar_task.task_create_package(print, self.nonexistent_archive1, self.nonexistent_path1)
            self.assertFalse(v)

    def testTarPluginTaskCreatePackage5(self):

        self.assertFalse(os.path.exists(self.nonexistent_archive1))
        self.assertTrue(os.path.exists(self.existent_path1))

        with mock.patch("tar_wrapper.make_pack", return_value=(True, None)) as dummy:
            v, r = self.tar_task.task_create_package(print, self.nonexistent_archive1, [self.existent_path1])
            self.assertTrue(v)
            dummy.assert_called_with(self.nonexistent_archive1, [self.existent_path1])

    def testTarPluginTaskCreatePackage6(self):

        self.assertFalse(os.path.exists(self.nonexistent_archive1))
        self.assertTrue(os.path.exists(self.existent_path1))

        with mock.patch("tar_wrapper.make_pack", return_value=(True, None)) as dummy:
            v, r = self.tar_task.task_create_package(print, self.nonexistent_archive1, self.existent_path1)
            self.assertTrue(v)
            dummy.assert_called_with(self.nonexistent_archive1, [self.existent_path1])

    def testTarPluginTaskExtractPackage1(self):

        self.assertFalse(os.path.exists(self.nonexistent_path1))
        self.assertTrue(os.path.exists(self.existent_path2))

        with mock.patch("tar_wrapper.extract", return_value=(True, None)) as dummy:
            v, r = self.tar_task.task_extract_package(print, self.nonexistent_path1, self.existent_path2)
            self.assertFalse(v)

    def testTarPluginTaskExtractPackage2(self):

        self.assertTrue(os.path.exists(self.existent_path2))

        with mock.patch("tar_wrapper.extract", return_value=(True, None)) as dummy:
            v, r = self.tar_task.task_extract_package(print, self.existent_path1, None)
            self.assertFalse(v)

    def testTarPluginTaskExtractPackage3(self):

        self.assertTrue(os.path.exists(self.existent_path2))
        self.assertFalse(os.path.exists(self.nonexistent_path1))

        with mock.patch("tar_wrapper.extract", return_value=(True, None)) as dummy:
            v, r = self.tar_task.task_extract_package(print, self.existent_path1, self.nonexistent_path1)
            self.assertFalse(v)

    def testTarPluginTaskExtractPackage4(self):

        self.assertTrue(os.path.exists(self.existent_path1))
        self.assertTrue(os.path.exists(self.existent_path2))

        with mock.patch("tar_wrapper.extract", return_value=(True, None)) as dummy:
            v, r = self.tar_task.task_extract_package(print, self.existent_path1, self.existent_path2)
            self.assertTrue(v)
            dummy.assert_called_with(self.existent_path1, self.existent_path2)

if __name__ == '__main__':
    unittest.main()
