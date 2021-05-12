#!/usr/bin/env python3

import sys
import os
import shutil
import unittest

import mvtools_test_fixture
import path_utils

import scratchfolder_plugin

class ScratchfolderTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("scratchfolder_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        self.nonexistent = path_utils.concat_path(self.test_dir, "nonexistent")

        self.test_target_path = path_utils.concat_path(self.test_dir, "test_target_path")
        os.mkdir(self.test_target_path)

        # the test task
        self.scratchfolder_task = scratchfolder_plugin.CustomTask()

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testScratchfolderFail1(self):

        local_params = {}
        self.scratchfolder_task.params = local_params

        v, r = self.scratchfolder_task.run_task(print, "exe_name")
        self.assertFalse(v)

    def testScratchfolderVanilla1(self):

        local_params = {}
        local_params["target_path"] = self.nonexistent
        self.scratchfolder_task.params = local_params

        self.assertFalse(os.path.exists( self.nonexistent ))
        v, r = self.scratchfolder_task.run_task(print, "exe_name")
        self.assertTrue(v)
        self.assertTrue(os.path.exists( self.nonexistent ))

    def testScratchfolderVanilla2(self):

        local_params = {}
        local_params["target_path"] = self.test_target_path
        self.scratchfolder_task.params = local_params

        self.assertTrue(os.path.exists( self.test_target_path ))
        v, r = self.scratchfolder_task.run_task(print, "exe_name")
        self.assertTrue(v)
        self.assertTrue(os.path.exists( self.test_target_path ))

if __name__ == '__main__':
    unittest.main()
