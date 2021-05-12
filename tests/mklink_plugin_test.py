#!/usr/bin/env python3

import sys
import os
import shutil
import unittest

import mvtools_test_fixture

import create_and_write_file
import path_utils

import mklink_plugin

class MklinkPluginTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("mklink_plugin_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        self.test_source_file = path_utils.concat_path(self.test_dir, "test_source_file")
        if not create_and_write_file.create_file_contents(self.test_source_file, "test-contents"):
            return False, "Unable to create test file [%s]" % self.test_source_file
        if not os.path.exists(self.test_source_file):
            return False, "Unable to create test file [%s]" % self.test_source_file

        self.test_nonexistent_file = path_utils.concat_path(self.test_dir, "test_nonexistent_file")
        if os.path.exists(self.test_nonexistent_file):
            return False, "File [%s] already exists" % self.test_nonexistent_file

        # the test task
        self.mklink_task = mklink_plugin.CustomTask()

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testMklinkPluginFail1(self):

        local_params = {}
        self.mklink_task.params = local_params

        v, r = self.mklink_task.run_task(print, "exe_name")
        self.assertFalse(v)

    def testMklinkPluginFail2(self):

        local_params = {}
        local_params["source_path"] = self.test_source_file
        self.mklink_task.params = local_params

        v, r = self.mklink_task.run_task(print, "exe_name")
        self.assertFalse(v)

    def testMklinkPluginFail3(self):

        local_params = {}
        local_params["source_path"] = self.test_nonexistent_file
        local_params["target_path"] = path_utils.concat_path(self.test_dir, "test_target_file")
        self.mklink_task.params = local_params

        v, r = self.mklink_task.run_task(print, "exe_name")
        self.assertFalse(v)

    def testMklinkPluginFail4(self):

        local_target_file = path_utils.concat_path(self.test_dir, "test_target_file")

        local_params = {}
        local_params["source_path"] = self.test_source_file
        local_params["target_path"] = local_target_file
        self.mklink_task.params = local_params

        self.assertTrue(create_and_write_file.create_file_contents(local_target_file, "test-contents"))
        self.assertTrue(os.path.exists(local_target_file))

        v, r = self.mklink_task.run_task(print, "exe_name")
        self.assertFalse(v)

    def testMklinkPluginFail5(self):

        local_params = {}
        local_params["source_path"] = self.test_source_file
        local_params["target_path"] = path_utils.concat_path(self.test_dir, "test_target_file", "second_level")
        self.mklink_task.params = local_params

        v, r = self.mklink_task.run_task(print, "exe_name")
        self.assertFalse(v)

    def testMklinkPluginVanilla(self):

        local_params = {}
        local_params["source_path"] = self.test_source_file
        local_params["target_path"] = path_utils.concat_path(self.test_dir, "test_target_file")
        self.mklink_task.params = local_params

        v, r = self.mklink_task.run_task(print, "exe_name")
        self.assertTrue(v)

if __name__ == '__main__':
    unittest.main()
