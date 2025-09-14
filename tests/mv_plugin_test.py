#!/usr/bin/env python

import sys
import os
import shutil
import unittest
from unittest import mock
from unittest.mock import patch

import mvtools_test_fixture
import path_utils

import mv_plugin

class MvPluginTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("mv_plugin_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        self.test_target_path = path_utils.concat_path(self.test_dir, "test_target_path")

        self.nonexistent1 = path_utils.concat_path(self.test_dir, "nonexistent1")
        self.nonexistent2 = path_utils.concat_path(self.test_dir, "nonexistent2")

        self.path1 = path_utils.concat_path(self.test_dir, "path1")
        self.path2 = path_utils.concat_path(self.test_dir, "path2")
        self.file_path = path_utils.concat_path(self.test_dir, "file_path")

        os.mkdir(self.path1)
        os.mkdir(self.path2)
        with open(self.file_path, "w") as f:
            f.write("dummy contents")

        # the test task
        self.mv_task = mv_plugin.CustomTask()

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testMvPluginReadParams1(self):

        local_params = {}
        self.mv_task.params = local_params

        v, r = self.mv_task._read_params()
        self.assertFalse(v)

    def testMvPluginReadParams2(self):

        local_params = {}
        local_params["source_path"] = "dummy_value1"
        self.mv_task.params = local_params

        v, r = self.mv_task._read_params()
        self.assertFalse(v)

    def testMvPluginReadParams3(self):

        local_params = {}
        local_params["source_path"] = "dummy_value1"
        local_params["target_path"] = "dummy_value2"
        self.mv_task.params = local_params

        v, r = self.mv_task._read_params()
        self.assertFalse(v)

    def testMvPluginReadParams4(self):

        local_params = {}
        local_params["source_path"] = self.nonexistent1
        local_params["target_path"] = self.path2
        self.mv_task.params = local_params

        v, r = self.mv_task._read_params()
        self.assertFalse(v)

    def testMvPluginReadParams5(self):

        local_params = {}
        local_params["source_path"] = self.path1
        local_params["target_path"] = self.nonexistent1
        self.mv_task.params = local_params

        v, r = self.mv_task._read_params()
        self.assertFalse(v)

    def testMvPluginReadParams6(self):

        local_params = {}
        local_params["source_path"] = self.path1
        local_params["target_path"] = self.path2
        self.mv_task.params = local_params

        v, r = self.mv_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, (self.path1, self.path2))

    def testMvPluginReadParams7(self):

        local_params = {}
        local_params["source_path"] = self.path1
        local_params["target_path"] = self.file_path
        self.mv_task.params = local_params

        v, r = self.mv_task._read_params()
        self.assertFalse(v)

    def testMvPluginReadParams8(self):

        final_path = path_utils.concat_path(self.path2, path_utils.basename_filtered(self.path1))
        os.mkdir(final_path)

        local_params = {}
        local_params["source_path"] = self.path1
        local_params["target_path"] = self.path2
        self.mv_task.params = local_params

        v, r = self.mv_task._read_params()
        self.assertFalse(v)

    def testMvPluginRunTask1(self):

        local_params = {}
        local_params["source_path"] = self.path1
        local_params["target_path"] = self.path2
        self.mv_task.params = local_params

        with mock.patch("mv_wrapper.move", return_value=(False, "dummy_error_msg")) as dummy:
            v, r = self.mv_task.run_task(print, "exe_name")
            self.assertFalse(v)
            self.assertEqual(r, "dummy_error_msg")
            dummy.assert_called_with(self.path1, self.path2)

    def testMvPluginRunTask2(self):

        local_params = {}
        local_params["source_path"] = self.path1
        local_params["target_path"] = self.path2
        self.mv_task.params = local_params

        with mock.patch("mv_wrapper.move", return_value=(True, (True, "stdout", "stderr"))) as dummy:
            v, r = self.mv_task.run_task(print, "exe_name")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(self.path1, self.path2)

if __name__ == "__main__":
    unittest.main()
