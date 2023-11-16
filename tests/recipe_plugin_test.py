#!/usr/bin/env python3

import sys
import os
import shutil
import unittest
from unittest import mock
from unittest.mock import patch
from unittest.mock import call

import mvtools_test_fixture
import create_and_write_file
import path_utils
import output_backup_helper

import recipe_plugin

class RecipePluginTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("recipe_plugin_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # the test task
        self.recipe_task = recipe_plugin.CustomTask()

        # existent path 1
        self.existent_path1 = path_utils.concat_path(self.test_dir, "existent_path1")
        os.mkdir(self.existent_path1)

        # nonexistent path 1
        self.nonexistent_path1 = path_utils.concat_path(self.test_dir, "nonexistent_path1")

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testRecipePluginReadParams1(self):

        local_params = {}
        self.recipe_task.params = local_params

        v, r = self.recipe_task._read_params()
        self.assertFalse(v)

    def testRecipePluginReadParams2(self):

        local_params = {}
        local_params["run"] = "dummy_value1"
        local_params["recipe"] = self.existent_path1
        self.recipe_task.params = local_params

        v, r = self.recipe_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("run", self.existent_path1, None, None, None, None, None, []) )

    def testRecipePluginReadParams3(self):

        local_params = {}
        local_params["test"] = "dummy_value1"
        local_params["recipe"] = self.existent_path1
        self.recipe_task.params = local_params

        v, r = self.recipe_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("test", self.existent_path1, None, None, None, None, None, []) )

    def testRecipePluginReadParams4(self):

        local_params = {}
        local_params["recipe"] = self.existent_path1
        self.recipe_task.params = local_params

        v, r = self.recipe_task._read_params()
        self.assertFalse(v)

    def testRecipePluginReadParams5(self):

        local_params = {}
        local_params["run"] = "dummy_value1"
        local_params["test"] = "dummy_value2"
        local_params["recipe"] = self.existent_path1
        self.recipe_task.params = local_params

        v, r = self.recipe_task._read_params()
        self.assertFalse(v)

    def testRecipePluginReadParams6(self):

        local_params = {}
        local_params["test"] = "dummy_value1"
        local_params["recipe"] = self.nonexistent_path1
        self.recipe_task.params = local_params

        v, r = self.recipe_task._read_params()
        self.assertFalse(v)

    def testRecipePluginReadParams7(self):

        local_params = {}
        local_params["test"] = "dummy_value1"
        local_params["recipe"] = self.existent_path1
        local_params["exec_name"] = "dummy_value2"
        self.recipe_task.params = local_params

        v, r = self.recipe_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("test", self.existent_path1, "dummy_value2", None, None, None, None, []) )

    def testRecipePluginReadParams8(self):

        local_params = {}
        local_params["test"] = "dummy_value1"
        local_params["recipe"] = self.existent_path1
        local_params["exec_name"] = "dummy_value2"
        local_params["early_abort"] = "dummy_value3"
        self.recipe_task.params = local_params

        v, r = self.recipe_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("test", self.existent_path1, "dummy_value2", "dummy_value3", None, None, None, []) )

    def testRecipePluginReadParams9(self):

        local_params = {}
        local_params["test"] = "dummy_value1"
        local_params["recipe"] = self.existent_path1
        local_params["exec_name"] = "dummy_value2"
        local_params["early_abort"] = "dummy_value3"
        local_params["time_delay"] = "dummy_value4"
        self.recipe_task.params = local_params

        v, r = self.recipe_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("test", self.existent_path1, "dummy_value2", "dummy_value3", "dummy_value4", None, None, []) )

    def testRecipePluginReadParams10(self):

        local_params = {}
        local_params["test"] = "dummy_value1"
        local_params["recipe"] = self.existent_path1
        local_params["exec_name"] = "dummy_value2"
        local_params["early_abort"] = "dummy_value3"
        local_params["time_delay"] = "dummy_value4"
        local_params["signal_delay"] = "dummy_value5"
        self.recipe_task.params = local_params

        v, r = self.recipe_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("test", self.existent_path1, "dummy_value2", "dummy_value3", "dummy_value4", "dummy_value5", None, []) )

    def testRecipePluginReadParams11(self):

        local_params = {}
        local_params["test"] = "dummy_value1"
        local_params["recipe"] = self.existent_path1
        local_params["exec_name"] = "dummy_value2"
        local_params["early_abort"] = "dummy_value3"
        local_params["time_delay"] = "dummy_value4"
        local_params["signal_delay"] = "dummy_value5"
        local_params["execution_delay"] = "dummy_value6"
        self.recipe_task.params = local_params

        v, r = self.recipe_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("test", self.existent_path1, "dummy_value2", "dummy_value3", "dummy_value4", "dummy_value5", "dummy_value6", []) )

    def testRecipePluginReadParams12(self):

        local_params = {}
        local_params["test"] = "dummy_value1"
        local_params["recipe"] = self.existent_path1
        local_params["exec_name"] = "dummy_value2"
        local_params["early_abort"] = "dummy_value3"
        local_params["time_delay"] = "dummy_value4"
        local_params["signal_delay"] = "dummy_value5"
        local_params["execution_delay"] = "dummy_value6"
        local_params["envvar"] = "dummy_value7"
        self.recipe_task.params = local_params

        v, r = self.recipe_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("test", self.existent_path1, "dummy_value2", "dummy_value3", "dummy_value4", "dummy_value5", "dummy_value6", ["dummy_value7"]) )

    def testRecipePluginReadParams13(self):

        local_params = {}
        local_params["test"] = "dummy_value1"
        local_params["recipe"] = self.existent_path1
        local_params["exec_name"] = "dummy_value2"
        local_params["early_abort"] = "dummy_value3"
        local_params["time_delay"] = "dummy_value4"
        local_params["signal_delay"] = "dummy_value5"
        local_params["execution_delay"] = "dummy_value6"
        local_params["envvar"] = ["dummy_value7", "dummy_value8"]
        self.recipe_task.params = local_params

        v, r = self.recipe_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("test", self.existent_path1, "dummy_value2", "dummy_value3", "dummy_value4", "dummy_value5", "dummy_value6", ["dummy_value7", "dummy_value8"]) )

    def testRecipePluginRunTask1(self):

        local_params = {}
        local_params["run"] = "dummy_value1"
        local_params["recipe"] = self.existent_path1
        self.recipe_task.params = local_params

        with mock.patch("recipe_processor.run_jobs_from_recipe_file", return_value=(False, "error-message")) as dummy1:
            with mock.patch("recipe_processor.assemble_requested_options", return_value="req_opts_mock") as dummy2:
                v, r = self.recipe_task.run_task(print, "exe_name")
                self.assertFalse(v)
                self.assertEqual(r, "error-message")

    def testRecipePluginRunTask2(self):

        local_params = {}
        local_params["run"] = "dummy_value1"
        local_params["recipe"] = self.existent_path1
        self.recipe_task.params = local_params

        with mock.patch("recipe_processor.run_jobs_from_recipe_file", return_value=(True, None)) as dummy1:
            with mock.patch("recipe_processor.assemble_requested_options", return_value="req_opts_mock") as dummy2:
                v, r = self.recipe_task.run_task(print, "exe_name")
                self.assertTrue(v)
                dummy1.assert_called_with(self.existent_path1, None, "req_opts_mock")
                dummy2.assert_called_with(None, None, None, None)

    def testRecipePluginRunTask3(self):

        local_params = {}
        local_params["run"] = "dummy_value1"
        local_params["recipe"] = self.existent_path1
        local_params["exec_name"] = "dummy_value2"
        self.recipe_task.params = local_params

        with mock.patch("recipe_processor.run_jobs_from_recipe_file", return_value=(True, None)) as dummy1:
            with mock.patch("recipe_processor.assemble_requested_options", return_value="req_opts_mock") as dummy2:
                v, r = self.recipe_task.run_task(print, "exe_name")
                self.assertTrue(v)
                dummy1.assert_called_with(self.existent_path1, "dummy_value2", "req_opts_mock")
                dummy2.assert_called_with(None, None, None, None)

    def testRecipePluginRunTask4(self):

        local_params = {}
        local_params["run"] = "dummy_value1"
        local_params["recipe"] = self.existent_path1
        local_params["early_abort"] = "dummy_value2"
        self.recipe_task.params = local_params

        with mock.patch("recipe_processor.run_jobs_from_recipe_file", return_value=(True, None)) as dummy1:
            with mock.patch("recipe_processor.assemble_requested_options", return_value="req_opts_mock") as dummy2:
                v, r = self.recipe_task.run_task(print, "exe_name")
                self.assertTrue(v)
                dummy1.assert_called_with(self.existent_path1, None, "req_opts_mock")
                dummy2.assert_called_with(None, None, None, None)

    def testRecipePluginRunTask5(self):

        local_params = {}
        local_params["run"] = "dummy_value1"
        local_params["recipe"] = self.existent_path1
        local_params["early_abort"] = "no"
        self.recipe_task.params = local_params

        with mock.patch("recipe_processor.run_jobs_from_recipe_file", return_value=(True, None)) as dummy1:
            with mock.patch("recipe_processor.assemble_requested_options", return_value="req_opts_mock") as dummy2:
                v, r = self.recipe_task.run_task(print, "exe_name")
                self.assertTrue(v)
                dummy1.assert_called_with(self.existent_path1, None, "req_opts_mock")
                dummy2.assert_called_with(False, None, None, None)

    def testRecipePluginRunTask6(self):

        local_params = {}
        local_params["run"] = "dummy_value1"
        local_params["recipe"] = self.existent_path1
        local_params["early_abort"] = "yes"
        self.recipe_task.params = local_params

        with mock.patch("recipe_processor.run_jobs_from_recipe_file", return_value=(True, None)) as dummy1:
            with mock.patch("recipe_processor.assemble_requested_options", return_value="req_opts_mock") as dummy2:
                v, r = self.recipe_task.run_task(print, "exe_name")
                self.assertTrue(v)
                dummy1.assert_called_with(self.existent_path1, None, "req_opts_mock")
                dummy2.assert_called_with(True, None, None, None)

    def testRecipePluginRunTask7(self):

        local_params = {}
        local_params["run"] = "dummy_value1"
        local_params["recipe"] = self.existent_path1
        local_params["time_delay"] = "dummy_value2"
        self.recipe_task.params = local_params

        with mock.patch("recipe_processor.run_jobs_from_recipe_file", return_value=(True, None)) as dummy1:
            with mock.patch("recipe_processor.assemble_requested_options", return_value="req_opts_mock") as dummy2:
                v, r = self.recipe_task.run_task(print, "exe_name")
                self.assertTrue(v)
                dummy1.assert_called_with(self.existent_path1, None, "req_opts_mock")
                dummy2.assert_called_with(None, "dummy_value2", None, None)

    def testRecipePluginRunTask8(self):

        local_params = {}
        local_params["run"] = "dummy_value1"
        local_params["recipe"] = self.existent_path1
        local_params["signal_delay"] = "dummy_value2"
        self.recipe_task.params = local_params

        with mock.patch("recipe_processor.run_jobs_from_recipe_file", return_value=(True, None)) as dummy1:
            with mock.patch("recipe_processor.assemble_requested_options", return_value="req_opts_mock") as dummy2:
                v, r = self.recipe_task.run_task(print, "exe_name")
                self.assertTrue(v)
                dummy1.assert_called_with(self.existent_path1, None, "req_opts_mock")
                dummy2.assert_called_with(None, None, "dummy_value2", None)

    def testRecipePluginRunTask9(self):

        local_params = {}
        local_params["run"] = "dummy_value1"
        local_params["recipe"] = self.existent_path1
        local_params["execution_delay"] = "dummy_value2"
        self.recipe_task.params = local_params

        with mock.patch("recipe_processor.run_jobs_from_recipe_file", return_value=(True, None)) as dummy1:
            with mock.patch("recipe_processor.assemble_requested_options", return_value="req_opts_mock") as dummy2:
                v, r = self.recipe_task.run_task(print, "exe_name")
                self.assertTrue(v)
                dummy1.assert_called_with(self.existent_path1, None, "req_opts_mock")
                dummy2.assert_called_with(None, None, None, "dummy_value2")

    def testRecipePluginRunTask10(self):

        local_params = {}
        local_params["test"] = "dummy_value1"
        local_params["recipe"] = self.existent_path1
        self.recipe_task.params = local_params

        with mock.patch("recipe_processor.test_jobs_from_recipe_file", return_value=(False, "error-message")) as dummy1:
            with mock.patch("recipe_processor.assemble_requested_options", return_value="req_opts_mock") as dummy2:
                v, r = self.recipe_task.run_task(print, "exe_name")
                self.assertFalse(v)
                self.assertEqual(r, "error-message")

    def testRecipePluginRunTask11(self):

        local_params = {}
        local_params["test"] = "dummy_value1"
        local_params["recipe"] = self.existent_path1
        self.recipe_task.params = local_params

        with mock.patch("recipe_processor.test_jobs_from_recipe_file", return_value=(True, None)) as dummy1:
            with mock.patch("recipe_processor.assemble_requested_options", return_value="req_opts_mock") as dummy2:
                v, r = self.recipe_task.run_task(print, "exe_name")
                self.assertTrue(v)
                dummy1.assert_called_with(self.existent_path1, None, "req_opts_mock")
                dummy2.assert_called_with(None, None, None, None)

    def testRecipePluginRunTask12(self):

        local_params = {}
        local_params["test"] = "dummy_value1"
        local_params["recipe"] = self.existent_path1
        local_params["exec_name"] = "dummy_value2"
        self.recipe_task.params = local_params

        with mock.patch("recipe_processor.test_jobs_from_recipe_file", return_value=(True, None)) as dummy1:
            with mock.patch("recipe_processor.assemble_requested_options", return_value="req_opts_mock") as dummy2:
                v, r = self.recipe_task.run_task(print, "exe_name")
                self.assertTrue(v)
                dummy1.assert_called_with(self.existent_path1, "dummy_value2", "req_opts_mock")
                dummy2.assert_called_with(None, None, None, None)

    def testRecipePluginRunTask13(self):

        local_params = {}
        local_params["test"] = "dummy_value1"
        local_params["recipe"] = self.existent_path1
        local_params["early_abort"] = "dummy_value2"
        self.recipe_task.params = local_params

        with mock.patch("recipe_processor.test_jobs_from_recipe_file", return_value=(True, None)) as dummy1:
            with mock.patch("recipe_processor.assemble_requested_options", return_value="req_opts_mock") as dummy2:
                v, r = self.recipe_task.run_task(print, "exe_name")
                self.assertTrue(v)
                dummy1.assert_called_with(self.existent_path1, None, "req_opts_mock")
                dummy2.assert_called_with(None, None, None, None)

    def testRecipePluginRunTask14(self):

        local_params = {}
        local_params["test"] = "dummy_value1"
        local_params["recipe"] = self.existent_path1
        local_params["early_abort"] = "no"
        self.recipe_task.params = local_params

        with mock.patch("recipe_processor.test_jobs_from_recipe_file", return_value=(True, None)) as dummy1:
            with mock.patch("recipe_processor.assemble_requested_options", return_value="req_opts_mock") as dummy2:
                v, r = self.recipe_task.run_task(print, "exe_name")
                self.assertTrue(v)
                dummy1.assert_called_with(self.existent_path1, None, "req_opts_mock")
                dummy2.assert_called_with(False, None, None, None)

    def testRecipePluginRunTask15(self):

        local_params = {}
        local_params["test"] = "dummy_value1"
        local_params["recipe"] = self.existent_path1
        local_params["early_abort"] = "yes"
        self.recipe_task.params = local_params

        with mock.patch("recipe_processor.test_jobs_from_recipe_file", return_value=(True, None)) as dummy1:
            with mock.patch("recipe_processor.assemble_requested_options", return_value="req_opts_mock") as dummy2:
                v, r = self.recipe_task.run_task(print, "exe_name")
                self.assertTrue(v)
                dummy1.assert_called_with(self.existent_path1, None, "req_opts_mock")
                dummy2.assert_called_with(True, None, None, None)

    def testRecipePluginRunTask16(self):

        local_params = {}
        local_params["test"] = "dummy_value1"
        local_params["recipe"] = self.existent_path1
        local_params["time_delay"] = "dummy_value2"
        self.recipe_task.params = local_params

        with mock.patch("recipe_processor.test_jobs_from_recipe_file", return_value=(True, None)) as dummy1:
            with mock.patch("recipe_processor.assemble_requested_options", return_value="req_opts_mock") as dummy2:
                v, r = self.recipe_task.run_task(print, "exe_name")
                self.assertTrue(v)
                dummy1.assert_called_with(self.existent_path1, None, "req_opts_mock")
                dummy2.assert_called_with(None, "dummy_value2", None, None)

    def testRecipePluginRunTask17(self):

        local_params = {}
        local_params["test"] = "dummy_value1"
        local_params["recipe"] = self.existent_path1
        local_params["signal_delay"] = "dummy_value2"
        self.recipe_task.params = local_params

        with mock.patch("recipe_processor.test_jobs_from_recipe_file", return_value=(True, None)) as dummy1:
            with mock.patch("recipe_processor.assemble_requested_options", return_value="req_opts_mock") as dummy2:
                v, r = self.recipe_task.run_task(print, "exe_name")
                self.assertTrue(v)
                dummy1.assert_called_with(self.existent_path1, None, "req_opts_mock")
                dummy2.assert_called_with(None, None, "dummy_value2", None)

    def testRecipePluginRunTask18(self):

        local_params = {}
        local_params["test"] = "dummy_value1"
        local_params["recipe"] = self.existent_path1
        local_params["execution_delay"] = "dummy_value2"
        self.recipe_task.params = local_params

        with mock.patch("recipe_processor.test_jobs_from_recipe_file", return_value=(True, None)) as dummy1:
            with mock.patch("recipe_processor.assemble_requested_options", return_value="req_opts_mock") as dummy2:
                v, r = self.recipe_task.run_task(print, "exe_name")
                self.assertTrue(v)
                dummy1.assert_called_with(self.existent_path1, None, "req_opts_mock")
                dummy2.assert_called_with(None, None, None, "dummy_value2")

if __name__ == '__main__':
    unittest.main()
