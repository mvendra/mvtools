#!/usr/bin/env python3

import sys
import os
import shutil
import unittest
from unittest import mock
from unittest.mock import patch
from unittest.mock import call

import mvtools_test_fixture

import path_utils
import prjcleanup_plugin

class ProjCleanupPluginTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("prjcleanup_plugin_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # the test task
        self.prjcleanup_task = prjcleanup_plugin.CustomTask()

        # existent path
        self.existent_path = path_utils.concat_path(self.test_dir, "existent_path")
        os.mkdir(self.existent_path)

        # nonexistent path
        self.nonexistent_path = path_utils.concat_path(self.test_dir, "nonexistent_path")

        return True, None

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testProjCleanupPluginReadParams1(self):

        local_params = {}
        self.prjcleanup_task.params = local_params

        v, r = self.prjcleanup_task._read_params()
        self.assertFalse(v)

    def testProjCleanupPluginReadParams2(self):

        local_params = {}
        local_params["proj"] = self.nonexistent_path
        self.prjcleanup_task.params = local_params

        v, r = self.prjcleanup_task._read_params()
        self.assertFalse(v)

    def testProjCleanupPluginReadParams3(self):

        local_params = {}
        local_params["proj"] = self.existent_path
        self.prjcleanup_task.params = local_params

        v, r = self.prjcleanup_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, (self.existent_path, False, False, False) )

    def testProjCleanupPluginReadParams4(self):

        local_params = {}
        local_params["proj"] = self.existent_path
        local_params["dep"] = "dummy_value1"
        self.prjcleanup_task.params = local_params

        v, r = self.prjcleanup_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, (self.existent_path, True, False, False) )

    def testProjCleanupPluginReadParams5(self):

        local_params = {}
        local_params["proj"] = self.existent_path
        local_params["dep"] = "dummy_value1"
        local_params["tmp"] = "dummy_value2"
        self.prjcleanup_task.params = local_params

        v, r = self.prjcleanup_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, (self.existent_path, True, True, False) )

    def testProjCleanupPluginReadParams6(self):

        local_params = {}
        local_params["proj"] = self.existent_path
        local_params["dep"] = "dummy_value1"
        local_params["tmp"] = "dummy_value2"
        local_params["out"] = "dummy_value3"
        self.prjcleanup_task.params = local_params

        v, r = self.prjcleanup_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, (self.existent_path, True, True, True) )

    def testProjCleanupPluginRunTask1(self):

        local_params = {}
        local_params["proj"] = self.existent_path
        self.prjcleanup_task.params = local_params

        with mock.patch("prjcleanup.prjcleanup", return_value=(False, "test error message")) as dummy:
            v, r = self.prjcleanup_task.run_task(print, "exe_name")
            self.assertFalse(v)
            dummy.assert_called_with(self.existent_path, False, False, False)

    def testProjCleanupPluginRunTask2(self):

        local_params = {}
        local_params["proj"] = self.existent_path
        self.prjcleanup_task.params = local_params

        with mock.patch("prjcleanup.prjcleanup", return_value=(True, None)) as dummy:
            v, r = self.prjcleanup_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(self.existent_path, False, False, False)

    def testProjCleanupPluginRunTask3(self):

        local_params = {}
        local_params["proj"] = self.existent_path
        local_params["dep"] = "dummy_value1"
        self.prjcleanup_task.params = local_params

        with mock.patch("prjcleanup.prjcleanup", return_value=(True, None)) as dummy:
            v, r = self.prjcleanup_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(self.existent_path, True, False, False)

    def testProjCleanupPluginRunTask4(self):

        local_params = {}
        local_params["proj"] = self.existent_path
        local_params["dep"] = "dummy_value1"
        local_params["tmp"] = "dummy_value2"
        self.prjcleanup_task.params = local_params

        with mock.patch("prjcleanup.prjcleanup", return_value=(True, None)) as dummy:
            v, r = self.prjcleanup_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(self.existent_path, True, True, False)

    def testProjCleanupPluginRunTask5(self):

        local_params = {}
        local_params["proj"] = self.existent_path
        local_params["dep"] = "dummy_value1"
        local_params["tmp"] = "dummy_value2"
        local_params["out"] = "dummy_value3"
        self.prjcleanup_task.params = local_params

        with mock.patch("prjcleanup.prjcleanup", return_value=(True, None)) as dummy:
            v, r = self.prjcleanup_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(self.existent_path, True, True, True)

if __name__ == "__main__":
    unittest.main()
