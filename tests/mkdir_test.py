#!/usr/bin/env python3

import sys
import os
import shutil
import unittest

import mvtools_test_fixture
import path_utils

import mkdir_plugin

class MkdirTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("mkdir_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        self.test_target_path = path_utils.concat_path(self.test_dir, "test_target_path")

        # the test task
        self.mkdir_task = mkdir_plugin.CustomTask()

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testMkdirFail1(self):

        local_params = {}
        self.mkdir_task.params = local_params

        v, r = self.mkdir_task.run_task(print, "exe_name")
        self.assertFalse(v)

    def testMkdirVanilla(self):

        local_params = {}
        local_params["target_path"] = self.test_target_path
        self.mkdir_task.params = local_params

        self.assertFalse(os.path.exists( self.test_target_path ))
        v, r = self.mkdir_task.run_task(print, "exe_name")
        self.assertTrue(v)
        self.assertTrue(os.path.exists( self.test_target_path ))

    def testMkdirVanillaRedundantError(self):

        local_params = {}
        local_params["target_path"] = self.test_target_path
        self.mkdir_task.params = local_params

        self.assertFalse(os.path.exists( self.test_target_path ))
        os.mkdir(self.test_target_path)
        self.assertTrue(os.path.exists( self.test_target_path ))
        v, r = self.mkdir_task.run_task(print, "exe_name")
        self.assertFalse(v)

    def testMkdirVanillaBadPathError(self):

        local_test_folder = path_utils.concat_path(self.test_target_path, "second_level")
        local_params = {}
        local_params["target_path"] = local_test_folder
        self.assertFalse(os.path.exists( local_test_folder ))

        self.mkdir_task.params = local_params
        v, r = self.mkdir_task.run_task(print, "exe_name")
        self.assertFalse(v)

    def testMkdirVanillaRedundantNoError(self):

        local_params = {}
        local_params["target_path"] = self.test_target_path
        local_params["ignore_pre_existence"] = ""
        self.mkdir_task.params = local_params

        self.assertFalse(os.path.exists( self.test_target_path ))
        os.mkdir(self.test_target_path)
        self.assertTrue(os.path.exists( self.test_target_path ))
        v, r = self.mkdir_task.run_task(print, "exe_name")
        self.assertTrue(v)
        self.assertTrue(os.path.exists( self.test_target_path ))

if __name__ == '__main__':
    unittest.main()
