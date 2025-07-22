#!/usr/bin/env python3

import sys
import os
import shutil
import unittest
from unittest import mock
from unittest.mock import patch

import mvtools_test_fixture
import path_utils

import batch_run_plugin

def file_create_contents(fn_full, contents):
    if os.path.exists(fn_full):
        return False
    with open(fn_full, "w") as f:
        f.write(contents)
    return True
    if not os.path.exists(fn_full):
        return False

class BatchRunPluginTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("batch_run_plugin_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # the test task
        self.batch_run_task = batch_run_plugin.CustomTask()

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testBatchRunPluginReadParams1(self):

        local_params = {}
        local_params["output"] = "dummy_value1"
        local_params["op_modes"] = "dummy_value2"
        local_params["op_modes_args"] = "dummy_value3"
        local_params["stop_mode"] = "dummy_value4"
        local_params["save_mode"] = "dummy_value5"
        self.batch_run_task.params = local_params

        v, r = self.batch_run_task._read_params()
        self.assertFalse(v)

    def testBatchRunPluginReadParams2(self):

        local_params = {}
        local_params["target"] = "dummy_value1"
        local_params["op_modes"] = "dummy_value2"
        local_params["op_modes_args"] = "dummy_value3"
        local_params["stop_mode"] = "dummy_value4"
        local_params["save_mode"] = "dummy_value5"
        self.batch_run_task.params = local_params

        v, r = self.batch_run_task._read_params()
        self.assertFalse(v)

    def testBatchRunPluginReadParams3(self):

        local_params = {}
        local_params["target"] = "dummy_value1"
        local_params["output"] = "dummy_value2"
        local_params["op_modes_args"] = "dummy_value3"
        local_params["stop_mode"] = "dummy_value4"
        local_params["save_mode"] = "dummy_value5"
        self.batch_run_task.params = local_params

        v, r = self.batch_run_task._read_params()
        self.assertFalse(v)

    def testBatchRunPluginReadParams4(self):

        local_params = {}
        local_params["target"] = "dummy_value1"
        local_params["output"] = "dummy_value2"
        local_params["op_modes"] = "dummy_value3"
        local_params["stop_mode"] = "dummy_value4"
        local_params["save_mode"] = "dummy_value5"
        self.batch_run_task.params = local_params

        v, r = self.batch_run_task._read_params()
        self.assertFalse(v)

    def testBatchRunPluginReadParams5(self):

        local_params = {}
        local_params["target"] = "dummy_value1"
        local_params["output"] = "dummy_value2"
        local_params["op_modes"] = "dummy_value3"
        local_params["op_modes_args"] = "dummy_value4"
        local_params["save_mode"] = "dummy_value5"
        self.batch_run_task.params = local_params

        v, r = self.batch_run_task._read_params()
        self.assertFalse(v)

    def testBatchRunPluginReadParams6(self):

        local_params = {}
        local_params["target"] = "dummy_value1"
        local_params["output"] = "dummy_value2"
        local_params["op_modes"] = "dummy_value3"
        local_params["op_modes_args"] = "dummy_value4"
        local_params["stop_mode"] = "dummy_value5"
        self.batch_run_task.params = local_params

        v, r = self.batch_run_task._read_params()
        self.assertFalse(v)

    def testBatchRunPluginReadParams7(self):

        local_params = {}
        local_params["target"] = "dummy_value1"
        local_params["output"] = "dummy_value2"
        local_params["op_modes"] = "dummy_value3"
        local_params["op_modes_args"] = "dummy_value4"
        local_params["stop_mode"] = "dummy_value5"
        local_params["save_mode"] = "dummy_value6"
        self.batch_run_task.params = local_params

        v, r = self.batch_run_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, ("dummy_value1", "dummy_value2", ["dummy_value3"], ["dummy_value4"], "dummy_value5", "dummy_value6", []))

    def testBatchRunPluginReadParams8(self):

        local_params = {}
        local_params["target"] = "dummy_value1"
        local_params["output"] = "dummy_value2"
        local_params["op_modes"] = ["dummy_value3", "dummy_value4"]
        local_params["op_modes_args"] = "dummy_value5"
        local_params["stop_mode"] = "dummy_value6"
        local_params["save_mode"] = "dummy_value7"
        self.batch_run_task.params = local_params

        v, r = self.batch_run_task._read_params()
        self.assertFalse(v)

    def testBatchRunPluginReadParams9(self):

        local_params = {}
        local_params["target"] = "dummy_value1"
        local_params["output"] = "dummy_value2"
        local_params["op_modes"] = ["dummy_value3", "dummy_value4"]
        local_params["op_modes_args"] = ["dummy_value5", "dummy_value6"]
        local_params["stop_mode"] = "dummy_value7"
        local_params["save_mode"] = "dummy_value8"
        self.batch_run_task.params = local_params

        v, r = self.batch_run_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, ("dummy_value1", "dummy_value2", ["dummy_value3", "dummy_value4"], ["dummy_value5", "dummy_value6"], "dummy_value7", "dummy_value8", []))

    def testBatchRunPluginReadParams10(self):

        local_params = {}
        local_params["target"] = "dummy_value1"
        local_params["output"] = "dummy_value2"
        local_params["op_modes"] = "dummy_value3"
        local_params["op_modes_args"] = "dummy_value4"
        local_params["stop_mode"] = "dummy_value5"
        local_params["save_mode"] = "dummy_value6"
        local_params["target_args"] = "dummy_value7"
        self.batch_run_task.params = local_params

        v, r = self.batch_run_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, ("dummy_value1", "dummy_value2", ["dummy_value3"], ["dummy_value4"], "dummy_value5", "dummy_value6", ["dummy_value7"]))

    def testBatchRunPluginReadParams11(self):

        local_params = {}
        local_params["target"] = "dummy_value1"
        local_params["output"] = "dummy_value2"
        local_params["op_modes"] = "dummy_value3"
        local_params["op_modes_args"] = "dummy_value4"
        local_params["stop_mode"] = "dummy_value5"
        local_params["save_mode"] = "dummy_value6"
        local_params["target_args"] = ["dummy_value7", "dummy_value8"]
        self.batch_run_task.params = local_params

        v, r = self.batch_run_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, ("dummy_value1", "dummy_value2", ["dummy_value3"], ["dummy_value4"], "dummy_value5", "dummy_value6", ["dummy_value7", "dummy_value8"]))

    def testBatchRunPluginRunTask1(self):

        local_params = {}
        local_params["target"] = "dummy_value1"
        local_params["output"] = "dummy_value2"
        local_params["op_modes"] = "dummy_value3"
        local_params["op_modes_args"] = "dummy_value4"
        local_params["stop_mode"] = "dummy_value5"
        local_params["save_mode"] = "dummy_value6"
        self.batch_run_task.params = local_params

        with mock.patch("batch_run.batch_run", return_value=(True, None)) as dummy:
            v, r = self.batch_run_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with("dummy_value1", "dummy_value2", [["dummy_value3", "dummy_value4"]], "dummy_value5", "dummy_value6", [])

    def testBatchRunPluginRunTask2(self):

        local_params = {}
        local_params["target"] = "dummy_value1"
        local_params["output"] = "dummy_value2"
        local_params["op_modes"] = ["dummy_value3", "dummy_value4"]
        local_params["op_modes_args"] = ["dummy_value5", "dummy_value6"]
        local_params["stop_mode"] = "dummy_value7"
        local_params["save_mode"] = "dummy_value8"
        self.batch_run_task.params = local_params

        with mock.patch("batch_run.batch_run", return_value=(True, None)) as dummy:
            v, r = self.batch_run_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with("dummy_value1", "dummy_value2", [["dummy_value3", "dummy_value5"], ["dummy_value4", "dummy_value6"]], "dummy_value7", "dummy_value8", [])

    def testBatchRunPluginRunTask3(self):

        local_params = {}
        local_params["target"] = "dummy_value1"
        local_params["output"] = "dummy_value2"
        local_params["op_modes"] = "dummy_value3"
        local_params["op_modes_args"] = "dummy_value4"
        local_params["stop_mode"] = "dummy_value5"
        local_params["save_mode"] = "dummy_value6"
        local_params["target_args"] = "dummy_value7"
        self.batch_run_task.params = local_params

        with mock.patch("batch_run.batch_run", return_value=(True, None)) as dummy:
            v, r = self.batch_run_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with("dummy_value1", "dummy_value2", [["dummy_value3", "dummy_value4"]], "dummy_value5", "dummy_value6", ["dummy_value7"])

    def testBatchRunPluginRunTask4(self):

        local_params = {}
        local_params["target"] = "dummy_value1"
        local_params["output"] = "dummy_value2"
        local_params["op_modes"] = "dummy_value3"
        local_params["op_modes_args"] = "dummy_value4"
        local_params["stop_mode"] = "dummy_value5"
        local_params["save_mode"] = "dummy_value6"
        local_params["target_args"] = ["dummy_value7", "dummy_value8"]
        self.batch_run_task.params = local_params

        with mock.patch("batch_run.batch_run", return_value=(True, None)) as dummy:
            v, r = self.batch_run_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with("dummy_value1", "dummy_value2", [["dummy_value3", "dummy_value4"]], "dummy_value5", "dummy_value6", ["dummy_value7", "dummy_value8"])

if __name__ == "__main__":
    unittest.main()
