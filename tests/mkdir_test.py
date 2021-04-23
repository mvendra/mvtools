#!/usr/bin/env python3

import sys
import os
import shutil
import unittest

import mvtools_test_fixture
import path_utils

import mkdir

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

        self.test_target_folder = path_utils.concat_path(self.test_dir, "test_target_folder")

        # the test task
        self.mkdir_task = mkdir.CustomTask()

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
        local_params["target_folder"] = self.test_target_folder
        self.mkdir_task.params = local_params

        self.assertFalse(os.path.exists( self.test_target_folder ))
        v, r = self.mkdir_task.run_task(print, "exe_name")
        self.assertTrue(v)
        self.assertTrue(os.path.exists( self.test_target_folder ))

    def testMkdirVanillaRedundantError(self):

        local_params = {}
        local_params["target_folder"] = self.test_target_folder
        self.mkdir_task.params = local_params

        self.assertFalse(os.path.exists( self.test_target_folder ))
        os.mkdir(self.test_target_folder)
        self.assertTrue(os.path.exists( self.test_target_folder ))
        v, r = self.mkdir_task.run_task(print, "exe_name")
        self.assertFalse(v)

    def testMkdirVanillaBadPathError(self):

        local_test_folder = path_utils.concat_path(self.test_target_folder, "second_level")
        local_params = {}
        local_params["target_folder"] = local_test_folder
        self.assertFalse(os.path.exists( local_test_folder ))

        self.mkdir_task.params = local_params
        v, r = self.mkdir_task.run_task(print, "exe_name")
        self.assertFalse(v)

    def testMkdirVanillaRedundantNoError(self):

        local_params = {}
        local_params["target_folder"] = self.test_target_folder
        local_params["ignore_pre_existence"] = ""
        self.mkdir_task.params = local_params

        self.assertFalse(os.path.exists( self.test_target_folder ))
        os.mkdir(self.test_target_folder)
        self.assertTrue(os.path.exists( self.test_target_folder ))
        v, r = self.mkdir_task.run_task(print, "exe_name")
        self.assertTrue(v)
        self.assertTrue(os.path.exists( self.test_target_folder ))

if __name__ == '__main__':
    unittest.main()
