#!/usr/bin/env python3

import sys
import os
import shutil
import unittest

import mvtools_test_fixture
import path_utils

import timestamper_plugin

class TimestamperPluginTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("timestamper_plugin_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        self.test_file = path_utils.concat_path(self.test_dir, "test_file.txt")

        # the test task
        self.timestamper_task = timestamper_plugin.CustomTask()

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testTimestamperPluginFail1(self):

        local_params = {}
        self.timestamper_task.params = local_params

        v, r = self.timestamper_task.run_task(print, "exe_name")
        self.assertFalse(v)

    def testTimestamperPluginFail2(self):

        local_params = {}
        local_params["target_filename"] = self.test_file
        self.timestamper_task.params = local_params

        # create dummy file
        with open(self.test_file, "w") as f:
            f.write("dummy")

        v, r = self.timestamper_task.run_task(print, "exe_name")
        self.assertFalse(v)

    def testTimestamperPluginVanilla(self):

        local_params = {}
        local_params["target_filename"] = self.test_file
        self.timestamper_task.params = local_params

        self.assertFalse(os.path.exists(self.test_file))
        v, r = self.timestamper_task.run_task(print, "exe_name")
        self.assertTrue(v)
        self.assertTrue(os.path.exists(self.test_file))

    def testTimestamperPluginCustomMessage(self):

        LOCAL_CUSTOM_MESSAGE = "sun dogs fire on the horizon"

        local_params = {}
        local_params["target_filename"] = self.test_file
        local_params["message"] = LOCAL_CUSTOM_MESSAGE
        self.timestamper_task.params = local_params

        self.assertFalse(os.path.exists(self.test_file))
        v, r = self.timestamper_task.run_task(print, "exe_name")
        self.assertTrue(v)
        self.assertTrue(os.path.exists(self.test_file))

        read_contents = ""
        with open(self.test_file, "r") as f:
            read_contents = f.read()
        self.assertTrue(LOCAL_CUSTOM_MESSAGE in read_contents)

if __name__ == "__main__":
    unittest.main()
