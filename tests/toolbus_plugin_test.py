#!/usr/bin/env python3

import sys
import os
import shutil
import unittest
from unittest import mock
from unittest.mock import patch

import mvtools_test_fixture
import toolbus_plugin

class ToolbusPluginTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("toolbus_plugin_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # the test task
        self.toolbus_task = toolbus_plugin.CustomTask()

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testToolbusPluginReadParams1(self):

        local_params = {}
        self.toolbus_task.params = local_params

        v, r = self.toolbus_task._read_params()
        self.assertFalse(v)

    def testToolbusPluginReadParams2(self):

        local_params = {}
        local_params["operation"] = "set_signal"
        self.toolbus_task.params = local_params

        v, r = self.toolbus_task._read_params()
        self.assertFalse(v)

    def testToolbusPluginReadParams3(self):

        local_params = {}
        local_params["operation"] = "set_signal"
        local_params["signal_name"] = "dummy_value1"
        self.toolbus_task.params = local_params

        v, r = self.toolbus_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, ("set_signal", "dummy_value1", None))

    def testToolbusPluginReadParams4(self):

        local_params = {}
        local_params["operation"] = "set_signal"
        local_params["signal_name"] = "dummy_value1"
        local_params["signal_value"] = "dummy_value2"
        self.toolbus_task.params = local_params

        v, r = self.toolbus_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, ("set_signal", "dummy_value1", "dummy_value2"))

    def testToolbusPluginReadParams5(self):

        local_params = {}
        local_params["operation"] = "set_signal"
        local_params["signal_value"] = "dummy_value1"
        self.toolbus_task.params = local_params

        v, r = self.toolbus_task._read_params()
        self.assertFalse(v)

    def testToolbusPluginRunTask1(self):

        local_params = {}
        local_params["operation"] = "set_signal"
        local_params["signal_name"] = "dummy_value1"
        local_params["signal_value"] = "dummy_value2"
        self.toolbus_task.params = local_params

        with mock.patch("toolbus_plugin.CustomTask.set_signal", return_value=(True, None)) as dummy:
            v, r = self.toolbus_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(print, "dummy_value1", "dummy_value2")

    def testToolbusPluginRunTask2(self):

        local_params = {}
        local_params["operation"] = "wait_signal"
        local_params["signal_name"] = "dummy_value1"
        self.toolbus_task.params = local_params

        with mock.patch("toolbus_plugin.CustomTask.wait_signal", return_value=(True, None)) as dummy:
            v, r = self.toolbus_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(print, "dummy_value1")

    def testToolbusPluginSetSignal1(self):

        with mock.patch("toolbus.set_signal", return_value=(True, None)) as dummy:
            v, r = self.toolbus_task.set_signal(print, "dummy_value1", "dummy_value2")
            self.assertTrue(v)
            dummy.assert_called_with("dummy_value1", "dummy_value2")

    def testToolbusPluginSetSignal2(self):

        with mock.patch("toolbus.set_signal", return_value=(True, None)) as dummy:
            v, r = self.toolbus_task.set_signal(print, "dummy_value1", None)
            self.assertFalse(v)
            dummy.assert_not_called()

    def testToolbusPluginWaitSignal1(self):

        with mock.patch("toolbus.get_signal", return_value=(True, True)) as dummy:
            v, r = self.toolbus_task.wait_signal(print, "dummy_value1")
            self.assertTrue(v)
            dummy.assert_called_with("dummy_value1")

if __name__ == '__main__':
    unittest.main()
