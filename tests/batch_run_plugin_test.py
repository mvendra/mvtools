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

        self.existent_path = path_utils.concat_path(self.test_dir, "existent_path")
        self.assertTrue(file_create_contents(self.existent_path, "test contents"))
        self.nonexistent_path = path_utils.concat_path(self.test_dir, "nonexistent_path")

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testBatchRunPluginReadParams1(self):

        local_params = {}
        self.batch_run_task.params = local_params

        v, r = self.batch_run_task._read_params()
        self.assertFalse(v)

    def testBatchRunPluginReadParams2(self):

        local_params = {}
        local_params["target"] = self.existent_path
        self.batch_run_task.params = local_params

        v, r = self.batch_run_task._read_params()
        self.assertFalse(v)

    def testBatchRunPluginReadParams3(self):

        local_params = {}
        local_params["target"] = self.existent_path
        local_params["output"] = self.nonexistent_path
        self.batch_run_task.params = local_params

        v, r = self.batch_run_task._read_params()
        self.assertFalse(v)

    def testBatchRunPluginReadParams4(self):

        local_params = {}
        local_params["target"] = self.existent_path
        local_params["output"] = self.nonexistent_path
        local_params["op_mode"] = "until-fail"
        self.batch_run_task.params = local_params

        v, r = self.batch_run_task._read_params()
        self.assertFalse(v)

    def testBatchRunPluginReadParams5(self):

        local_params = {}
        local_params["target"] = self.existent_path
        local_params["output"] = self.nonexistent_path
        local_params["op_mode"] = "until-fail"
        local_params["op_mode_arg"] = "dummy_value1"
        self.batch_run_task.params = local_params

        v, r = self.batch_run_task._read_params()
        self.assertFalse(v)

    def testBatchRunPluginReadParams6(self):

        local_params = {}
        local_params["target"] = self.existent_path
        local_params["output"] = self.nonexistent_path
        local_params["op_mode"] = "until-fail"
        local_params["op_mode_arg"] = "dummy_value1"
        local_params["save_mode"] = "save-all"
        self.batch_run_task.params = local_params

        v, r = self.batch_run_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, (self.existent_path, self.nonexistent_path, "until-fail", "dummy_value1", "save-all", []))

    def testBatchRunPluginReadParams7(self):

        local_params = {}
        local_params["target"] = self.existent_path
        local_params["output"] = self.nonexistent_path
        local_params["op_mode"] = "until-fail"
        local_params["op_mode_arg"] = "dummy_value1"
        local_params["save_mode"] = "save-all"
        local_params["target_args"] = ["dummy_value2", "dummy_value3"]
        self.batch_run_task.params = local_params

        v, r = self.batch_run_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, (self.existent_path, self.nonexistent_path, "until-fail", "dummy_value1", "save-all", ["dummy_value2", "dummy_value3"]))

    def testBatchRunPluginReadParams8(self):

        local_params = {}
        local_params["target"] = self.nonexistent_path
        local_params["output"] = self.nonexistent_path
        local_params["op_mode"] = "until-fail"
        local_params["op_mode_arg"] = "dummy_value1"
        local_params["save_mode"] = "save-all"
        self.batch_run_task.params = local_params

        v, r = self.batch_run_task._read_params()
        self.assertFalse(v)

    def testBatchRunPluginReadParams9(self):

        local_params = {}
        local_params["target"] = self.existent_path
        local_params["output"] = self.existent_path
        local_params["op_mode"] = "until-fail"
        local_params["op_mode_arg"] = "dummy_value1"
        local_params["save_mode"] = "save-all"
        self.batch_run_task.params = local_params

        v, r = self.batch_run_task._read_params()
        self.assertFalse(v)

    def testBatchRunPluginReadParams10(self):

        local_params = {}
        local_params["target"] = self.existent_path
        local_params["output"] = self.nonexistent_path
        local_params["op_mode"] = "invalid-op-mode"
        local_params["op_mode_arg"] = "dummy_value1"
        local_params["save_mode"] = "save-all"
        self.batch_run_task.params = local_params

        v, r = self.batch_run_task._read_params()
        self.assertFalse(v)

    def testBatchRunPluginReadParams11(self):

        local_params = {}
        local_params["target"] = self.existent_path
        local_params["output"] = self.nonexistent_path
        local_params["op_mode"] = "until-fail"
        local_params["op_mode_arg"] = "dummy_value1"
        local_params["save_mode"] = "invalid-save-mode"
        self.batch_run_task.params = local_params

        v, r = self.batch_run_task._read_params()
        self.assertFalse(v)

    def testBatchRunPluginRunTask1(self):

        local_params = {}
        local_params["target"] = self.existent_path
        local_params["output"] = self.nonexistent_path
        local_params["op_mode"] = "until-fail"
        local_params["op_mode_arg"] = "dummy_value1"
        local_params["save_mode"] = "save-all"
        local_params["target_args"] = ["dummy_value2", "dummy_value3"]
        self.batch_run_task.params = local_params

        with mock.patch("batch_run.batch_run", return_value=(True, None)) as dummy:
            v, r = self.batch_run_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(self.existent_path, self.nonexistent_path, "until-fail", "dummy_value1", "save-all", ["dummy_value2", "dummy_value3"])

if __name__ == '__main__':
    unittest.main()
