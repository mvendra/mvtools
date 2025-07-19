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

import hash_plugin

class HashPluginTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("hash_plugin_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # the test task
        self.hash_task = hash_plugin.CustomTask()

        # existent path 1
        self.existent_path1 = path_utils.concat_path(self.test_dir, "existent_path1")
        os.mkdir(self.existent_path1)

        # existent path 2
        self.existent_path2 = path_utils.concat_path(self.test_dir, "existent_path2")
        os.mkdir(self.existent_path2)

        # nonexistent path 1
        self.nonexistent_path1 = path_utils.concat_path(self.test_dir, "nonexistent_path1")

        # nonexistent path 2
        self.nonexistent_path2 = path_utils.concat_path(self.test_dir, "nonexistent_path2")

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testHashPluginReadParams1(self):

        local_params = {}
        self.hash_task.params = local_params

        v, r = self.hash_task._read_params()
        self.assertFalse(v)

    def testHashPluginReadParams2(self):

        local_params = {}
        local_params["operation"] = "dummy_value1"
        self.hash_task.params = local_params

        v, r = self.hash_task._read_params()
        self.assertFalse(v)

    def testHashPluginReadParams3(self):

        local_params = {}
        local_params["operation"] = "dummy_value1"
        local_params["target_archive"] = "dummy_value2"
        self.hash_task.params = local_params

        v, r = self.hash_task._read_params()
        self.assertFalse(v)

    def testHashPluginReadParams4(self):

        local_params = {}
        local_params["operation"] = "dummy_value1"
        local_params["target_archive"] = "dummy_value2"
        local_params["hash_type"] = "dummy_value3"
        self.hash_task.params = local_params

        v, r = self.hash_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", "dummy_value3", None, None) )

    def testHashPluginReadParams5(self):

        local_params = {}
        local_params["operation"] = "dummy_value1"
        local_params["target_archive"] = "dummy_value2"
        local_params["hash_type"] = "dummy_value3"
        local_params["target_hash"] = "dummy_value4"
        self.hash_task.params = local_params

        v, r = self.hash_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4", None) )

    def testHashPluginReadParams6(self):

        local_params = {}
        local_params["operation"] = "dummy_value1"
        local_params["target_archive"] = "dummy_value2"
        local_params["hash_type"] = "dummy_value3"
        local_params["target_hash"] = "dummy_value4"
        local_params["target_hash_file"] = "dummy_value5"
        self.hash_task.params = local_params

        v, r = self.hash_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4", "dummy_value5") )

    def testHashPluginRunTask1(self):

        local_params = {}
        local_params["operation"] = "dummy_value1"
        local_params["target_archive"] = "dummy_value2"
        local_params["hash_type"] = "dummy_value3"
        self.hash_task.params = local_params

        v, r = self.hash_task.run_task(print, "exe_name")
        self.assertFalse(v)

    def testHashPluginRunTask_ExtractHash1(self):

        local_params = {}
        local_params["operation"] = "extract_hash"
        local_params["target_archive"] = "dummy_value2"
        local_params["hash_type"] = "dummy_value3"
        local_params["target_hash_file"] = "dummy_value4"
        self.hash_task.params = local_params

        with mock.patch("hash_plugin.CustomTask.task_extract_hash", return_value=(True, None)) as dummy:
            v, r = self.hash_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(print, "dummy_value2", "dummy_value3", "dummy_value4")

    def testHashPluginRunTask_CheckHashFromContent1(self):

        local_params = {}
        local_params["operation"] = "check_hash_from_content"
        local_params["target_archive"] = "dummy_value2"
        local_params["hash_type"] = "dummy_value3"
        local_params["target_hash"] = "dummy_value4"
        self.hash_task.params = local_params

        with mock.patch("hash_plugin.CustomTask.task_check_hash_from_content", return_value=(True, None)) as dummy:
            v, r = self.hash_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(print, "dummy_value2", "dummy_value3", "dummy_value4")

    def testHashPluginRunTask_CheckHashFromFile1(self):

        local_params = {}
        local_params["operation"] = "check_hash_from_file"
        local_params["target_archive"] = "dummy_value2"
        local_params["hash_type"] = "dummy_value3"
        local_params["target_hash_file"] = "dummy_value4"
        self.hash_task.params = local_params

        with mock.patch("hash_plugin.CustomTask.task_check_hash_from_file", return_value=(True, None)) as dummy:
            v, r = self.hash_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(print, "dummy_value2", "dummy_value3", "dummy_value4")

    def testHashPluginTaskExtractHash1(self):

        with mock.patch("sha256_wrapper.hash_sha_256_app_file", return_value=(True, "fake-256-hash")) as dummy:
            v, r = self.hash_task.task_extract_hash(print, None, "sha256", self.nonexistent_path2)
            self.assertFalse(v)
            dummy.assert_not_called()

    def testHashPluginTaskExtractHash2(self):

        self.assertFalse(os.path.exists(self.nonexistent_path1))

        with mock.patch("sha256_wrapper.hash_sha_256_app_file", return_value=(True, "fake-256-hash")) as dummy:
            v, r = self.hash_task.task_extract_hash(print, self.nonexistent_path1, "sha256", self.nonexistent_path2)
            self.assertFalse(v)
            dummy.assert_not_called()

    def testHashPluginTaskExtractHash3(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        with mock.patch("sha256_wrapper.hash_sha_256_app_file", return_value=(True, "fake-256-hash")) as dummy:
            v, r = self.hash_task.task_extract_hash(print, self.existent_path1, None, self.nonexistent_path2)
            self.assertFalse(v)
            dummy.assert_not_called()

    def testHashPluginTaskExtractHash4(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        with mock.patch("sha256_wrapper.hash_sha_256_app_file", return_value=(True, "fake-256-hash")) as dummy:
            v, r = self.hash_task.task_extract_hash(print, self.existent_path1, "sha255", self.nonexistent_path2)
            self.assertFalse(v)
            dummy.assert_not_called()

    def testHashPluginTaskExtractHash5(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        with mock.patch("sha256_wrapper.hash_sha_256_app_file", return_value=(True, "fake-256-hash")) as dummy:
            v, r = self.hash_task.task_extract_hash(print, self.existent_path1, "sha256", None)
            self.assertFalse(v)
            dummy.assert_not_called()

    def testHashPluginTaskExtractHash6(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        with mock.patch("sha256_wrapper.hash_sha_256_app_file", return_value=(True, "fake-256-hash")) as dummy:
            v, r = self.hash_task.task_extract_hash(print, self.existent_path1, "sha256", self.existent_path2)
            self.assertFalse(v)
            dummy.assert_not_called()

    def testHashPluginTaskExtractHash7(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        with mock.patch("sha256_wrapper.hash_sha_256_app_file", return_value=(True, "fake-256-hash")) as dummy:
            v, r = self.hash_task.task_extract_hash(print, self.existent_path1, "sha256", self.nonexistent_path2)
            self.assertTrue(v)
            dummy.assert_called_with(self.existent_path1)

    def testHashPluginTaskExtractHash8(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        with mock.patch("sha512_wrapper.hash_sha_512_app_file", return_value=(True, "fake-512-hash")) as dummy:
            v, r = self.hash_task.task_extract_hash(print, self.existent_path1, "sha512", self.nonexistent_path2)
            self.assertTrue(v)
            dummy.assert_called_with(self.existent_path1)

    def testHashPluginTaskCheckHashFromContent1(self):

        with mock.patch("sha256_wrapper.hash_sha_256_app_file", return_value=(True, "fake-256-hash")) as dummy:
            v, r = self.hash_task.task_check_hash_from_content(print, None, "sha256", "fake-256-hash")
            self.assertFalse(v)
            dummy.assert_not_called()

    def testHashPluginTaskCheckHashFromContent2(self):

        self.assertFalse(os.path.exists(self.nonexistent_path1))

        with mock.patch("sha256_wrapper.hash_sha_256_app_file", return_value=(True, "fake-256-hash")) as dummy:
            v, r = self.hash_task.task_check_hash_from_content(print, self.nonexistent_path1, "sha256", "fake-256-hash")
            self.assertFalse(v)
            dummy.assert_not_called()

    def testHashPluginTaskCheckHashFromContent3(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        with mock.patch("sha256_wrapper.hash_sha_256_app_file", return_value=(True, "fake-256-hash")) as dummy:
            v, r = self.hash_task.task_check_hash_from_content(print, self.existent_path1, None, "fake-256-hash")
            self.assertFalse(v)
            dummy.assert_not_called()

    def testHashPluginTaskCheckHashFromContent4(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        with mock.patch("sha256_wrapper.hash_sha_256_app_file", return_value=(True, "fake-256-hash")) as dummy:
            v, r = self.hash_task.task_check_hash_from_content(print, self.existent_path1, "sha255", "fake-256-hash")
            self.assertFalse(v)
            dummy.assert_not_called()

    def testHashPluginTaskCheckHashFromContent5(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        with mock.patch("sha256_wrapper.hash_sha_256_app_file", return_value=(True, "fake-256-hash")) as dummy:
            v, r = self.hash_task.task_check_hash_from_content(print, self.existent_path1, "sha256", None)
            self.assertFalse(v)
            dummy.assert_not_called()

    def testHashPluginTaskCheckHashFromContent6(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        with mock.patch("sha256_wrapper.hash_sha_256_app_file", return_value=(True, "fake-256-rash")) as dummy:
            v, r = self.hash_task.task_check_hash_from_content(print, self.existent_path1, "sha256", "fake-256-hash")
            self.assertFalse(v)
            dummy.assert_called_with(self.existent_path1)

    def testHashPluginTaskCheckHashFromContent7(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        with mock.patch("sha256_wrapper.hash_sha_256_app_file", return_value=(True, "fake-256-hash")) as dummy:
            v, r = self.hash_task.task_check_hash_from_content(print, self.existent_path1, "sha256", "fake-256-rash")
            self.assertFalse(v)
            dummy.assert_called_with(self.existent_path1)

    def testHashPluginTaskCheckHashFromContent8(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        with mock.patch("sha256_wrapper.hash_sha_256_app_file", return_value=(True, "fake-256-hash")) as dummy:
            v, r = self.hash_task.task_check_hash_from_content(print, self.existent_path1, "sha256", "fake-256-hash")
            self.assertTrue(v)
            dummy.assert_called_with(self.existent_path1)

    def testHashPluginTaskCheckHashFromContent9(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        with mock.patch("sha512_wrapper.hash_sha_512_app_file", return_value=(True, "fake-512-rash")) as dummy:
            v, r = self.hash_task.task_check_hash_from_content(print, self.existent_path1, "sha512", "fake-512-hash")
            self.assertFalse(v)
            dummy.assert_called_with(self.existent_path1)

    def testHashPluginTaskCheckHashFromContent10(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        with mock.patch("sha512_wrapper.hash_sha_512_app_file", return_value=(True, "fake-512-hash")) as dummy:
            v, r = self.hash_task.task_check_hash_from_content(print, self.existent_path1, "sha512", "fake-512-rash")
            self.assertFalse(v)
            dummy.assert_called_with(self.existent_path1)

    def testHashPluginTaskCheckHashFromContent11(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        with mock.patch("sha512_wrapper.hash_sha_512_app_file", return_value=(True, "fake-512-hash")) as dummy:
            v, r = self.hash_task.task_check_hash_from_content(print, self.existent_path1, "sha512", "fake-512-hash")
            self.assertTrue(v)
            dummy.assert_called_with(self.existent_path1)

    def testHashPluginTaskCheckHashFromFile1(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        test_hash_file = path_utils.concat_path(self.test_dir, "test_hash_file.txt")
        self.assertFalse(os.path.exists(test_hash_file))
        create_and_write_file.create_file_contents(test_hash_file, "fake-256-hash")
        self.assertTrue(os.path.exists(test_hash_file))

        with mock.patch("sha256_wrapper.hash_sha_256_app_file", return_value=(True, "fake-256-hash")) as dummy:
            v, r = self.hash_task.task_check_hash_from_file(print, None, "sha256", test_hash_file)
            self.assertFalse(v)
            dummy.assert_not_called()

    def testHashPluginTaskCheckHashFromFile2(self):

        self.assertFalse(os.path.exists(self.nonexistent_path1))

        test_hash_file = path_utils.concat_path(self.test_dir, "test_hash_file.txt")
        self.assertFalse(os.path.exists(test_hash_file))
        create_and_write_file.create_file_contents(test_hash_file, "fake-256-hash")
        self.assertTrue(os.path.exists(test_hash_file))

        with mock.patch("sha256_wrapper.hash_sha_256_app_file", return_value=(True, "fake-256-hash")) as dummy:
            v, r = self.hash_task.task_check_hash_from_file(print, self.nonexistent_path1, "sha256", test_hash_file)
            self.assertFalse(v)
            dummy.assert_not_called()

    def testHashPluginTaskCheckHashFromFile3(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        test_hash_file = path_utils.concat_path(self.test_dir, "test_hash_file.txt")
        self.assertFalse(os.path.exists(test_hash_file))
        create_and_write_file.create_file_contents(test_hash_file, "fake-256-hash")
        self.assertTrue(os.path.exists(test_hash_file))

        with mock.patch("sha256_wrapper.hash_sha_256_app_file", return_value=(True, "fake-256-hash")) as dummy:
            v, r = self.hash_task.task_check_hash_from_file(print, self.existent_path1, None, test_hash_file)
            self.assertFalse(v)
            dummy.assert_not_called()

    def testHashPluginTaskCheckHashFromFile4(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        test_hash_file = path_utils.concat_path(self.test_dir, "test_hash_file.txt")
        self.assertFalse(os.path.exists(test_hash_file))
        create_and_write_file.create_file_contents(test_hash_file, "fake-256-hash")
        self.assertTrue(os.path.exists(test_hash_file))

        with mock.patch("sha256_wrapper.hash_sha_256_app_file", return_value=(True, "fake-256-hash")) as dummy:
            v, r = self.hash_task.task_check_hash_from_file(print, self.existent_path1, "sha255", test_hash_file)
            self.assertFalse(v)
            dummy.assert_not_called()

    def testHashPluginTaskCheckHashFromFile5(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        test_hash_file = path_utils.concat_path(self.test_dir, "test_hash_file.txt")
        self.assertFalse(os.path.exists(test_hash_file))
        create_and_write_file.create_file_contents(test_hash_file, "fake-256-hash")
        self.assertTrue(os.path.exists(test_hash_file))

        with mock.patch("sha256_wrapper.hash_sha_256_app_file", return_value=(True, "fake-256-hash")) as dummy:
            v, r = self.hash_task.task_check_hash_from_file(print, self.existent_path1, "sha256", None)
            self.assertFalse(v)
            dummy.assert_not_called()

    def testHashPluginTaskCheckHashFromFile6(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        test_hash_file = path_utils.concat_path(self.test_dir, "test_hash_file.txt")
        self.assertFalse(os.path.exists(test_hash_file))

        with mock.patch("sha256_wrapper.hash_sha_256_app_file", return_value=(True, "fake-256-hash")) as dummy:
            v, r = self.hash_task.task_check_hash_from_file(print, self.existent_path1, "sha256", test_hash_file)
            self.assertFalse(v)
            dummy.assert_not_called()

    def testHashPluginTaskCheckHashFromFile7(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        test_hash_file = path_utils.concat_path(self.test_dir, "test_hash_file.txt")
        self.assertFalse(os.path.exists(test_hash_file))
        create_and_write_file.create_file_contents(test_hash_file, "fake-256-rash")
        self.assertTrue(os.path.exists(test_hash_file))

        with mock.patch("sha256_wrapper.hash_sha_256_app_file", return_value=(True, "fake-256-hash")) as dummy:
            v, r = self.hash_task.task_check_hash_from_file(print, self.existent_path1, "sha256", test_hash_file)
            self.assertFalse(v)
            dummy.assert_called_with(self.existent_path1)

    def testHashPluginTaskCheckHashFromFile8(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        test_hash_file = path_utils.concat_path(self.test_dir, "test_hash_file.txt")
        self.assertFalse(os.path.exists(test_hash_file))
        create_and_write_file.create_file_contents(test_hash_file, "fake-256-hash")
        self.assertTrue(os.path.exists(test_hash_file))

        with mock.patch("sha256_wrapper.hash_sha_256_app_file", return_value=(True, "fake-256-rash")) as dummy:
            v, r = self.hash_task.task_check_hash_from_file(print, self.existent_path1, "sha256", test_hash_file)
            self.assertFalse(v)
            dummy.assert_called_with(self.existent_path1)

    def testHashPluginTaskCheckHashFromFile9(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        test_hash_file = path_utils.concat_path(self.test_dir, "test_hash_file.txt")
        self.assertFalse(os.path.exists(test_hash_file))
        create_and_write_file.create_file_contents(test_hash_file, "fake-256-hash")
        self.assertTrue(os.path.exists(test_hash_file))

        with mock.patch("sha256_wrapper.hash_sha_256_app_file", return_value=(True, "fake-256-hash")) as dummy:
            v, r = self.hash_task.task_check_hash_from_file(print, self.existent_path1, "sha256", test_hash_file)
            self.assertTrue(v)
            dummy.assert_called_with(self.existent_path1)

    def testHashPluginTaskCheckHashFromFile10(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        test_hash_file = path_utils.concat_path(self.test_dir, "test_hash_file.txt")
        self.assertFalse(os.path.exists(test_hash_file))
        create_and_write_file.create_file_contents(test_hash_file, "fake-512-rash")
        self.assertTrue(os.path.exists(test_hash_file))

        with mock.patch("sha512_wrapper.hash_sha_512_app_file", return_value=(True, "fake-512-hash")) as dummy:
            v, r = self.hash_task.task_check_hash_from_file(print, self.existent_path1, "sha512", test_hash_file)
            self.assertFalse(v)
            dummy.assert_called_with(self.existent_path1)

    def testHashPluginTaskCheckHashFromFile11(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        test_hash_file = path_utils.concat_path(self.test_dir, "test_hash_file.txt")
        self.assertFalse(os.path.exists(test_hash_file))
        create_and_write_file.create_file_contents(test_hash_file, "fake-512-hash")
        self.assertTrue(os.path.exists(test_hash_file))

        with mock.patch("sha512_wrapper.hash_sha_512_app_file", return_value=(True, "fake-512-rash")) as dummy:
            v, r = self.hash_task.task_check_hash_from_file(print, self.existent_path1, "sha512", test_hash_file)
            self.assertFalse(v)
            dummy.assert_called_with(self.existent_path1)

    def testHashPluginTaskCheckHashFromFile12(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        test_hash_file = path_utils.concat_path(self.test_dir, "test_hash_file.txt")
        self.assertFalse(os.path.exists(test_hash_file))
        create_and_write_file.create_file_contents(test_hash_file, "fake-512-hash")
        self.assertTrue(os.path.exists(test_hash_file))

        with mock.patch("sha512_wrapper.hash_sha_512_app_file", return_value=(True, "fake-512-hash")) as dummy:
            v, r = self.hash_task.task_check_hash_from_file(print, self.existent_path1, "sha512", test_hash_file)
            self.assertTrue(v)
            dummy.assert_called_with(self.existent_path1)

if __name__ == '__main__':
    unittest.main()
