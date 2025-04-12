#!/usr/bin/env python3

import sys
import os
import shutil
import unittest
from unittest import mock
from unittest.mock import patch

import mvtools_test_fixture
import create_and_write_file
import path_utils

import diff_plugin

class DiffPluginTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("diff_plugin_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # the test task
        self.diff_task = diff_plugin.CustomTask()

        # left path
        self.left_path = "left_path"
        self.left_path_full = path_utils.concat_path(self.test_dir, self.left_path)
        os.mkdir(self.left_path_full)

        # right path
        self.right_path = "right_path"
        self.right_path_full = path_utils.concat_path(self.test_dir, self.right_path)

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testDiffPluginReadParams1(self):

        local_params = {}
        local_params["left_path"] = self.left_path
        self.diff_task.params = local_params

        v, r = self.diff_task._read_params()
        self.assertFalse(v)

    def testDiffPluginReadParams2(self):

        local_params = {}
        local_params["left_path"] = self.left_path
        local_params["right_path"] = self.right_path
        self.diff_task.params = local_params

        v, r = self.diff_task._read_params()
        self.assertFalse(v)

    def testDiffPluginReadParams3(self):

        local_params = {}
        local_params["left_path"] = self.left_path
        local_params["right_path"] = self.right_path
        local_params["mode"] = "invalid"
        self.diff_task.params = local_params

        v, r = self.diff_task._read_params()
        self.assertFalse(v)

    def testDiffPluginReadParams4(self):

        local_params = {}
        local_params["left_path"] = self.left_path
        local_params["right_path"] = self.right_path
        local_params["mode"] = "eq-fail"
        self.diff_task.params = local_params

        v, r = self.diff_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, (self.left_path, self.right_path, "eq-fail"))

    def testDiffPluginReadParams5(self):

        local_params = {}
        local_params["left_path"] = self.left_path
        local_params["right_path"] = self.right_path
        local_params["mode"] = "eq-warn"
        self.diff_task.params = local_params

        v, r = self.diff_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, (self.left_path, self.right_path, "eq-warn"))

    def testDiffPluginReadParams6(self):

        local_params = {}
        local_params["left_path"] = self.left_path
        local_params["right_path"] = self.right_path
        local_params["mode"] = "ne-fail"
        self.diff_task.params = local_params

        v, r = self.diff_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, (self.left_path, self.right_path, "ne-fail"))

    def testDiffPluginReadParams7(self):

        local_params = {}
        local_params["left_path"] = self.left_path
        local_params["right_path"] = self.right_path
        local_params["mode"] = "ne-warn"
        self.diff_task.params = local_params

        v, r = self.diff_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, (self.left_path, self.right_path, "ne-warn"))

    def testDiffPluginRunTask1(self):

        local_params = {}
        local_params["left_path"] = self.left_path
        local_params["right_path"] = self.right_path
        local_params["mode"] = "eq-fail"
        self.diff_task.params = local_params

        with mock.patch("diff_wrapper.do_diff", return_value=(True, "")) as dummy:
            v, r = self.diff_task.run_task(print, "exe_name")
            self.assertFalse(v)
            self.assertEqual(r, "contents of [%s] and [%s] are equal" % (self.left_path, self.right_path))
            dummy.assert_called_with(self.left_path, self.right_path)

    def testDiffPluginRunTask2(self):

        local_params = {}
        local_params["left_path"] = self.left_path
        local_params["right_path"] = self.right_path
        local_params["mode"] = "eq-fail"
        self.diff_task.params = local_params

        with mock.patch("diff_wrapper.do_diff", return_value=(True, "mocked contents")) as dummy:
            v, r = self.diff_task.run_task(print, "exe_name")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(self.left_path, self.right_path)

    def testDiffPluginRunTask3(self):

        local_params = {}
        local_params["left_path"] = self.left_path
        local_params["right_path"] = self.right_path
        local_params["mode"] = "eq-warn"
        self.diff_task.params = local_params

        with mock.patch("diff_wrapper.do_diff", return_value=(True, "")) as dummy:
            v, r = self.diff_task.run_task(print, "exe_name")
            self.assertTrue(v)
            self.assertEqual(r, "contents of [%s] and [%s] are equal" % (self.left_path, self.right_path))
            dummy.assert_called_with(self.left_path, self.right_path)

    def testDiffPluginRunTask4(self):

        local_params = {}
        local_params["left_path"] = self.left_path
        local_params["right_path"] = self.right_path
        local_params["mode"] = "eq-warn"
        self.diff_task.params = local_params

        with mock.patch("diff_wrapper.do_diff", return_value=(True, "mocked contents")) as dummy:
            v, r = self.diff_task.run_task(print, "exe_name")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(self.left_path, self.right_path)

    def testDiffPluginRunTask5(self):

        local_params = {}
        local_params["left_path"] = self.left_path
        local_params["right_path"] = self.right_path
        local_params["mode"] = "ne-fail"
        self.diff_task.params = local_params

        with mock.patch("diff_wrapper.do_diff", return_value=(True, "")) as dummy:
            v, r = self.diff_task.run_task(print, "exe_name")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(self.left_path, self.right_path)

    def testDiffPluginRunTask6(self):

        local_params = {}
        local_params["left_path"] = self.left_path
        local_params["right_path"] = self.right_path
        local_params["mode"] = "ne-fail"
        self.diff_task.params = local_params

        with mock.patch("diff_wrapper.do_diff", return_value=(True, "mocked contents")) as dummy:
            v, r = self.diff_task.run_task(print, "exe_name")
            self.assertFalse(v)
            self.assertEqual(r, "contents of [%s] and [%s] are not equal" % (self.left_path, self.right_path))
            dummy.assert_called_with(self.left_path, self.right_path)

    def testDiffPluginRunTask7(self):

        local_params = {}
        local_params["left_path"] = self.left_path
        local_params["right_path"] = self.right_path
        local_params["mode"] = "ne-warn"
        self.diff_task.params = local_params

        with mock.patch("diff_wrapper.do_diff", return_value=(True, "")) as dummy:
            v, r = self.diff_task.run_task(print, "exe_name")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(self.left_path, self.right_path)

    def testDiffPluginRunTask8(self):

        local_params = {}
        local_params["left_path"] = self.left_path
        local_params["right_path"] = self.right_path
        local_params["mode"] = "ne-warn"
        self.diff_task.params = local_params

        with mock.patch("diff_wrapper.do_diff", return_value=(True, "mocked contents")) as dummy:
            v, r = self.diff_task.run_task(print, "exe_name")
            self.assertTrue(v)
            self.assertEqual(r, "contents of [%s] and [%s] are not equal" % (self.left_path, self.right_path))
            dummy.assert_called_with(self.left_path, self.right_path)

if __name__ == '__main__':
    unittest.main()
