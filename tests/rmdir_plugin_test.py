#!/usr/bin/env python3

import sys
import os
import shutil
import unittest

import mvtools_test_fixture
import path_utils

import rmdir_plugin

class RmdirPluginTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("rmdir_plugin_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        self.test_target_path = path_utils.concat_path(self.test_dir, "test_target_path")

        self.folder1 = path_utils.concat_path(self.test_dir, "folder1")
        os.mkdir(self.folder1)

        self.nonexistent = path_utils.concat_path(self.test_dir, "nonexistent")

        # the test task
        self.rmdir_task = rmdir_plugin.CustomTask()

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testRmdirPluginFail1(self):

        local_params = {}
        self.rmdir_task.params = local_params

        v, r = self.rmdir_task.run_task(print, "exe_name")
        self.assertFalse(v)

    def testRmdirPluginFail2(self):

        local_params = {}
        local_params["target_path"] = self.nonexistent
        self.rmdir_task.params = local_params

        v, r = self.rmdir_task.run_task(print, "exe_name")
        self.assertFalse(v)

    def testRmdirPluginErrorIgnored(self):

        local_params = {}
        local_params["target_path"] = self.nonexistent
        local_params["ignore_non_pre_existence"] = None
        self.rmdir_task.params = local_params

        v, r = self.rmdir_task.run_task(print, "exe_name")
        self.assertTrue(v)

    def testRmdirPluginVanilla(self):

        local_params = {}
        local_params["target_path"] = self.folder1
        self.rmdir_task.params = local_params

        self.assertTrue(os.path.exists(self.folder1))
        v, r = self.rmdir_task.run_task(print, "exe_name")
        self.assertTrue(v)
        self.assertFalse(os.path.exists(self.folder1))

if __name__ == '__main__':
    unittest.main()
