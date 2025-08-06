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

import cleanup_dir_plugin

class CleanupDirPluginTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("cleanup_dir_plugin_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # test paths
        self.nonexistent = path_utils.concat_path(self.test_dir, "nonexistent")
        self.existent_dir = path_utils.concat_path(self.test_dir, "existent_dir")
        self.existent_file = path_utils.concat_path(self.test_dir, "existent_file.txt")

        os.mkdir(self.existent_dir)
        create_and_write_file.create_file_contents(self.existent_file, "contents")

        # the test task
        self.cleanup_dir_task = cleanup_dir_plugin.CustomTask()

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testCleanupDirPluginReadParams1(self):

        local_params = {}
        local_params["keep_only"] = "dummy_value1"
        self.cleanup_dir_task.params = local_params

        v, r = self.cleanup_dir_task._read_params()
        self.assertFalse(v)
        self.assertEqual(r, "target_path is a required parameter")

    def testCleanupDirPluginReadParams2(self):

        local_params = {}
        local_params["target_path"] = self.existent_dir
        local_params["keep_only"] = "dummy_value1"
        self.cleanup_dir_task.params = local_params

        v, r = self.cleanup_dir_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, (self.existent_dir, ["dummy_value1"], None))

    def testCleanupDirPluginReadParams3(self):

        local_params = {}
        local_params["target_path"] = self.existent_dir
        local_params["keep_only"] = ["dummy_value1", "dummy_value2"]
        self.cleanup_dir_task.params = local_params

        v, r = self.cleanup_dir_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, (self.existent_dir, ["dummy_value1", "dummy_value2"], None))

    def testCleanupDirPluginReadParams4(self):

        local_params = {}
        local_params["target_path"] = self.existent_dir
        local_params["ditch"] = "dummy_value1"
        self.cleanup_dir_task.params = local_params

        v, r = self.cleanup_dir_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, (self.existent_dir, None, ["dummy_value1"]))

    def testCleanupDirPluginReadParams5(self):

        local_params = {}
        local_params["target_path"] = self.existent_dir
        local_params["ditch"] = ["dummy_value1", "dummy_value2"]
        self.cleanup_dir_task.params = local_params

        v, r = self.cleanup_dir_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, (self.existent_dir, None, ["dummy_value1", "dummy_value2"]))

    def testCleanupDirPluginReadParams6(self):

        local_params = {}
        local_params["target_path"] = self.nonexistent
        local_params["keep_only"] = "dummy_value1"
        self.cleanup_dir_task.params = local_params

        v, r = self.cleanup_dir_task._read_params()
        self.assertFalse(v)
        self.assertEqual(r, "target path [%s] does not exist" % self.nonexistent)

    def testCleanupDirPluginReadParams7(self):

        local_params = {}
        local_params["target_path"] = self.existent_file
        local_params["keep_only"] = "dummy_value1"
        self.cleanup_dir_task.params = local_params

        v, r = self.cleanup_dir_task._read_params()
        self.assertFalse(v)
        self.assertEqual(r, "target path [%s] is not a folder" % self.existent_file)

    def testCleanupDirPluginReadParams8(self):

        local_params = {}
        local_params["target_path"] = self.existent_dir
        self.cleanup_dir_task.params = local_params

        v, r = self.cleanup_dir_task._read_params()
        self.assertFalse(v)
        self.assertEqual(r, "no operations selected")

    def testCleanupDirPluginReadParams9(self):

        local_params = {}
        local_params["target_path"] = self.existent_dir
        local_params["keep_only"] = "dummy_value1"
        local_params["ditch"] = "dummy_value2"
        self.cleanup_dir_task.params = local_params

        v, r = self.cleanup_dir_task._read_params()
        self.assertFalse(v)
        self.assertEqual(r, "keep_only cannot be selected with ditch")

    def testCleanupDirPluginRunTask1(self):

        local_params = {}
        local_params["target_path"] = self.existent_dir
        local_params["keep_only"] = "dummy_value1"
        self.cleanup_dir_task.params = local_params

        with mock.patch("fsquery.makecontentlist", return_value=(False, "dummy_error_msg")) as dummy:
            v, r = self.cleanup_dir_task.run_task(print, "exe_name")
            self.assertFalse(v)
            self.assertEqual(r, "dummy_error_msg")
            dummy.assert_called_with(self.existent_dir, False, False, True, True, True, True, True, None)

    def testCleanupDirPluginRunTask2(self):

        local_params = {}
        local_params["target_path"] = self.existent_dir
        local_params["keep_only"] = "dummy_value1"
        self.cleanup_dir_task.params = local_params

        with mock.patch("fsquery.makecontentlist", return_value=(True, ["/base/dummy_value1"])) as dummy1:
            with mock.patch("path_utils.remove_path", return_value=(True)) as dummy2:
                v, r = self.cleanup_dir_task.run_task(print, "exe_name")
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy1.assert_called_with(self.existent_dir, False, False, True, True, True, True, True, None)
                dummy2.assert_not_called()

    def testCleanupDirPluginRunTask3(self):

        local_params = {}
        local_params["target_path"] = self.existent_dir
        local_params["keep_only"] = ["dummy_value1", "dummy_value2"]
        self.cleanup_dir_task.params = local_params

        with mock.patch("fsquery.makecontentlist", return_value=(True, ["/base/dummy_value1", "/base/dummy_value2"])) as dummy1:
            with mock.patch("path_utils.remove_path", return_value=(True)) as dummy2:
                v, r = self.cleanup_dir_task.run_task(print, "exe_name")
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy1.assert_called_with(self.existent_dir, False, False, True, True, True, True, True, None)
                dummy2.assert_not_called()

    def testCleanupDirPluginRunTask4(self):

        local_params = {}
        local_params["target_path"] = self.existent_dir
        local_params["keep_only"] = "dummy_value1"
        self.cleanup_dir_task.params = local_params

        with mock.patch("fsquery.makecontentlist", return_value=(True, ["/base/dummy_value2"])) as dummy1:
            with mock.patch("path_utils.remove_path", return_value=(True)) as dummy2:
                v, r = self.cleanup_dir_task.run_task(print, "exe_name")
                self.assertTrue(v)
                self.assertEqual(r, "not all expected entries found on [%s] (keep-only)" % self.existent_dir)
                dummy1.assert_called_with(self.existent_dir, False, False, True, True, True, True, True, None)
                dummy2.assert_called_with("/base/dummy_value2")

    def testCleanupDirPluginRunTask5(self):

        local_params = {}
        local_params["target_path"] = self.existent_dir
        local_params["keep_only"] = ["dummy_value1", "dummy_value2"]
        self.cleanup_dir_task.params = local_params

        with mock.patch("fsquery.makecontentlist", return_value=(True, ["/base/dummy_value3", "/base/dummy_value4"])) as dummy1:
            with mock.patch("path_utils.remove_path", return_value=(True)) as dummy2:
                v, r = self.cleanup_dir_task.run_task(print, "exe_name")
                self.assertTrue(v)
                self.assertEqual(r, "not all expected entries found on [%s] (keep-only)" % self.existent_dir)
                dummy1.assert_called_with(self.existent_dir, False, False, True, True, True, True, True, None)
                dummy2.assert_has_calls([call("/base/dummy_value3"), call("/base/dummy_value4")])

    def testCleanupDirPluginRunTask6(self):

        local_params = {}
        local_params["target_path"] = self.existent_dir
        local_params["keep_only"] = "dummy_value1"
        self.cleanup_dir_task.params = local_params

        with mock.patch("fsquery.makecontentlist", return_value=(True, ["/base/dummy_value1", "/base/dummy_value2", "/base/dummy_value3"])) as dummy1:
            with mock.patch("path_utils.remove_path", return_value=(True)) as dummy2:
                v, r = self.cleanup_dir_task.run_task(print, "exe_name")
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy1.assert_called_with(self.existent_dir, False, False, True, True, True, True, True, None)
                dummy2.assert_has_calls([call("/base/dummy_value2"), call("/base/dummy_value3")])

    def testCleanupDirPluginRunTask7(self):

        local_params = {}
        local_params["target_path"] = self.existent_dir
        local_params["keep_only"] = "dummy_value1"
        self.cleanup_dir_task.params = local_params

        with mock.patch("fsquery.makecontentlist", return_value=(True, ["/base/dummy_value2"])) as dummy1:
            with mock.patch("path_utils.remove_path", return_value=(False)) as dummy2:
                v, r = self.cleanup_dir_task.run_task(print, "exe_name")
                self.assertFalse(v)
                self.assertEqual(r, "could not remove [/base/dummy_value2] (keep-only)")
                dummy1.assert_called_with(self.existent_dir, False, False, True, True, True, True, True, None)
                dummy2.assert_called_with("/base/dummy_value2")

    def testCleanupDirPluginRunTask8(self):

        local_params = {}
        local_params["target_path"] = self.existent_dir
        local_params["ditch"] = ["dummy_value1"]
        self.cleanup_dir_task.params = local_params

        with mock.patch("fsquery.makecontentlist", return_value=(True, ["/base/dummy_value1"])) as dummy1:
            with mock.patch("path_utils.remove_path", return_value=(True)) as dummy2:
                v, r = self.cleanup_dir_task.run_task(print, "exe_name")
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy1.assert_called_with(self.existent_dir, False, False, True, True, True, True, True, None)
                dummy2.assert_called_with("/base/dummy_value1")

    def testCleanupDirPluginRunTask9(self):

        local_params = {}
        local_params["target_path"] = self.existent_dir
        local_params["ditch"] = ["dummy_value1"]
        self.cleanup_dir_task.params = local_params

        with mock.patch("fsquery.makecontentlist", return_value=(True, ["/base/dummy_value2"])) as dummy1:
            with mock.patch("path_utils.remove_path", return_value=(True)) as dummy2:
                v, r = self.cleanup_dir_task.run_task(print, "exe_name")
                self.assertTrue(v)
                self.assertEqual(r, "[dummy_value1] was not found on [%s] (ditch)" % self.existent_dir)
                dummy1.assert_called_with(self.existent_dir, False, False, True, True, True, True, True, None)
                dummy2.assert_not_called()

    def testCleanupDirPluginRunTask10(self):

        local_params = {}
        local_params["target_path"] = self.existent_dir
        local_params["ditch"] = ["dummy_value1"]
        self.cleanup_dir_task.params = local_params

        with mock.patch("fsquery.makecontentlist", return_value=(True, ["/base/dummy_value1", "/base/dummy_value2"])) as dummy1:
            with mock.patch("path_utils.remove_path", return_value=(True)) as dummy2:
                v, r = self.cleanup_dir_task.run_task(print, "exe_name")
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy1.assert_called_with(self.existent_dir, False, False, True, True, True, True, True, None)
                dummy2.assert_called_with("/base/dummy_value1")

    def testCleanupDirPluginRunTask11(self):

        local_params = {}
        local_params["target_path"] = self.existent_dir
        local_params["ditch"] = ["dummy_value1"]
        self.cleanup_dir_task.params = local_params

        with mock.patch("fsquery.makecontentlist", return_value=(True, ["/base/dummy_value1"])) as dummy1:
            with mock.patch("path_utils.remove_path", return_value=(False)) as dummy2:
                v, r = self.cleanup_dir_task.run_task(print, "exe_name")
                self.assertFalse(v)
                self.assertEqual(r, "could not remove [/base/dummy_value1] (ditch)")
                dummy1.assert_called_with(self.existent_dir, False, False, True, True, True, True, True, None)
                dummy2.assert_called_with("/base/dummy_value1")

if __name__ == "__main__":
    unittest.main()
