#!/usr/bin/env python

import sys
import os
import shutil
import unittest
from unittest import mock
from unittest.mock import patch

import mvtools_test_fixture

import check_platform_plugin

class CheckPlatformPluginTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("check_platform_plugin_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # the test task
        self.check_platform_task = check_platform_plugin.CustomTask()

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testCheckPlatformPluginReadParams1(self):

        local_params = {}
        local_params["expected"] = "dummy_value1"
        self.check_platform_task.params = local_params

        v, r = self.check_platform_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ["dummy_value1"] )

    def testCheckPlatformPluginReadParams2(self):

        local_params = {}
        local_params["expected"] = ["dummy_value1", "dummy_value2"]
        self.check_platform_task.params = local_params

        v, r = self.check_platform_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ["dummy_value1", "dummy_value2"] )

    def testCheckPlatformPluginReadParams3(self):

        local_params = {}
        self.check_platform_task.params = local_params

        v, r = self.check_platform_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, None )

    def testCheckPlatformPluginRunTask1(self):

        local_params = {}
        self.check_platform_task.params = local_params

        v, r = self.check_platform_task.run_task(print, "exe_name")
        self.assertTrue(v)

    def testCheckPlatformPluginRunTask2(self):

        local_params = {}
        local_params["expected"] = "dummy_value1"
        self.check_platform_task.params = local_params

        with mock.patch("get_platform.getplat", return_value="dummy_value2") as dummy:
            v, r = self.check_platform_task.run_task(print, "exe_name")
            self.assertFalse(v)
            self.assertEqual(r, "Local platform [dummy_value2] is not expected")
            dummy.assert_called()

    def testCheckPlatformPluginRunTask3(self):

        local_params = {}
        local_params["expected"] = "dummy_value1"
        self.check_platform_task.params = local_params

        with mock.patch("get_platform.getplat", return_value="dummy_value1") as dummy:
            v, r = self.check_platform_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called()

if __name__ == "__main__":
    unittest.main()
