#!/usr/bin/env python

import sys
import os
import shutil
import unittest
from unittest import mock
from unittest.mock import patch

import mvtools_test_fixture
import create_and_write_file
import path_utils

import generic_run_plugin

class GenericRunPluginTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("generic_run_plugin_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # the test task
        self.generic_run_task = generic_run_plugin.CustomTask()

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testGenericRunPluginReadParams1(self):

        local_params = {}
        self.generic_run_task.params = local_params

        v, r = self.generic_run_task._read_params()
        self.assertFalse(v)

    def testGenericRunPluginReadParams2(self):

        local_params = {}
        local_params["command"] = "dummy_value1"
        self.generic_run_task.params = local_params

        v, r = self.generic_run_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", None, None) )

    def testGenericRunPluginReadParams3(self):

        local_params = {}
        local_params["command"] = "dummy_value1"
        local_params["cwd"] = "dummy_value2"
        self.generic_run_task.params = local_params

        v, r = self.generic_run_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", None) )

    def testGenericRunPluginReadParams4(self):

        local_params = {}
        local_params["command"] = "dummy_value1"
        local_params["arg"] = "dummy_value2"
        self.generic_run_task.params = local_params

        v, r = self.generic_run_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", None, ["dummy_value2"]) )

    def testGenericRunPluginReadParams5(self):

        local_params = {}
        local_params["command"] = "dummy_value1"
        local_params["cwd"] = "dummy_value2"
        local_params["arg"] = "dummy_value3"
        self.generic_run_task.params = local_params

        v, r = self.generic_run_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", ["dummy_value3"]) )

    def testGenericRunPluginReadParams6(self):

        local_params = {}
        local_params["command"] = "dummy_value1"
        local_params["arg"] = ["dummy_value2", "dummy_value3"]
        self.generic_run_task.params = local_params

        v, r = self.generic_run_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", None, ["dummy_value2", "dummy_value3"]) )

    def testGenericRunPluginReadParams6(self):

        local_params = {}
        local_params["command"] = "dummy_value1"
        local_params["cwd"] = "dummy_value2"
        local_params["arg"] = ["dummy_value3", "dummy_value4"]
        self.generic_run_task.params = local_params

        v, r = self.generic_run_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", ["dummy_value3", "dummy_value4"]) )

    def testGenericRunPluginRunTask1(self):

        local_params = {}
        local_params["command"] = "dummy_value1"
        local_params["arg"] = "dummy_value2"
        self.generic_run_task.params = local_params

        with mock.patch("generic_run.run_cmd_simple", return_value=(True, None)) as dummy:
            v, r = self.generic_run_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(["dummy_value1", "dummy_value2"], use_cwd=None)

    def testGenericRunPluginRunTask2(self):

        local_params = {}
        local_params["command"] = "dummy_value1"
        local_params["cwd"] = "dummy_value2"
        self.generic_run_task.params = local_params

        with mock.patch("generic_run.run_cmd_simple", return_value=(True, None)) as dummy:
            v, r = self.generic_run_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(["dummy_value1"], use_cwd="dummy_value2")

    def testGenericRunPluginRunTask3(self):

        local_params = {}
        local_params["command"] = "dummy_value1"
        local_params["arg"] = ["dummy_value2", "dummy_value3"]
        self.generic_run_task.params = local_params

        with mock.patch("generic_run.run_cmd_simple", return_value=(True, None)) as dummy:
            v, r = self.generic_run_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(["dummy_value1", "dummy_value2", "dummy_value3"], use_cwd=None)

    def testGenericRunPluginRunTask4(self):

        local_params = {}
        local_params["command"] = "dummy_value1"
        local_params["cwd"] = "dummy_value2"
        local_params["arg"] = ["dummy_value3", "dummy_value4"]
        self.generic_run_task.params = local_params

        with mock.patch("generic_run.run_cmd_simple", return_value=(True, None)) as dummy:
            v, r = self.generic_run_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(["dummy_value1", "dummy_value3", "dummy_value4"], use_cwd="dummy_value2")

    def testGenericRunPluginRunTask5(self):

        local_params = {}
        local_params["command"] = "dummy_value1"
        local_params["cwd"] = "dummy_value2"
        local_params["arg"] = "dummy_value3"
        self.generic_run_task.params = local_params

        with mock.patch("generic_run.run_cmd_simple", return_value=(False, None)) as dummy:
            v, r = self.generic_run_task.run_task(print, "exe_name")
            self.assertFalse(v)

if __name__ == "__main__":
    unittest.main()
