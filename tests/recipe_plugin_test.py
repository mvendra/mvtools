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
        self.assertEqual( r, ("run", self.existent_path1, None, []) )

    def testRecipePluginReadParams3(self):

        local_params = {}
        local_params["test"] = "dummy_value1"
        local_params["recipe"] = self.existent_path1
        self.recipe_task.params = local_params

        v, r = self.recipe_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("test", self.existent_path1, None, []) )

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
        self.assertEqual( r, ("test", self.existent_path1, "dummy_value2", []) )

    def testRecipePluginReadParams8(self):

        local_params = {}
        local_params["test"] = "dummy_value1"
        local_params["recipe"] = self.existent_path1
        local_params["exec_name"] = "dummy_value2"
        local_params["envvar"] = "dummy_value3"
        self.recipe_task.params = local_params

        v, r = self.recipe_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("test", self.existent_path1, "dummy_value2", ["dummy_value3"]) )

    def testRecipePluginReadParams9(self):

        local_params = {}
        local_params["test"] = "dummy_value1"
        local_params["recipe"] = self.existent_path1
        local_params["exec_name"] = "dummy_value2"
        local_params["envvar"] = ["dummy_value3", "dummy_value4"]
        self.recipe_task.params = local_params

        v, r = self.recipe_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("test", self.existent_path1, "dummy_value2", ["dummy_value3", "dummy_value4"]) )

if __name__ == '__main__':
    unittest.main()
