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

import check_dir_contents_plugin

class CheckDirContentsPluginTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("check_dir_contents_plugin_test")
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
        self.check_dir_contents_task = check_dir_contents_plugin.CustomTask()

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testCheckDirContentsPluginReadParams1(self):

        local_params = {}
        local_params["has_only"] = "dummy_value1"
        self.check_dir_contents_task.params = local_params

        v, r = self.check_dir_contents_task._read_params()
        self.assertFalse(v)
        self.assertEqual(r, "target_path is a required parameter")

    def testCheckDirContentsPluginReadParams2(self):

        local_params = {}
        local_params["target_path"] = self.existent_dir
        local_params["has_only"] = "dummy_value1"
        self.check_dir_contents_task.params = local_params

        v, r = self.check_dir_contents_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, (self.existent_dir, ["dummy_value1"], None, None))

    def testCheckDirContentsPluginReadParams3(self):

        local_params = {}
        local_params["target_path"] = self.existent_dir
        local_params["has_only"] = ["dummy_value1", "dummy_value2"]
        self.check_dir_contents_task.params = local_params

        v, r = self.check_dir_contents_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, (self.existent_dir, ["dummy_value1", "dummy_value2"], None, None))

    def testCheckDirContentsPluginReadParams4(self):

        local_params = {}
        local_params["target_path"] = self.existent_dir
        local_params["has"] = "dummy_value1"
        self.check_dir_contents_task.params = local_params

        v, r = self.check_dir_contents_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, (self.existent_dir, None, ["dummy_value1"], None))

    def testCheckDirContentsPluginReadParams5(self):

        local_params = {}
        local_params["target_path"] = self.existent_dir
        local_params["has"] = ["dummy_value1", "dummy_value2"]
        self.check_dir_contents_task.params = local_params

        v, r = self.check_dir_contents_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, (self.existent_dir, None, ["dummy_value1", "dummy_value2"], None))

    def testCheckDirContentsPluginReadParams6(self):

        local_params = {}
        local_params["target_path"] = self.existent_dir
        local_params["not"] = "dummy_value1"
        self.check_dir_contents_task.params = local_params

        v, r = self.check_dir_contents_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, (self.existent_dir, None, None, ["dummy_value1"]))

    def testCheckDirContentsPluginReadParams7(self):

        local_params = {}
        local_params["target_path"] = self.existent_dir
        local_params["not"] = ["dummy_value1", "dummy_value2"]
        self.check_dir_contents_task.params = local_params

        v, r = self.check_dir_contents_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, (self.existent_dir, None, None, ["dummy_value1", "dummy_value2"]))

    def testCheckDirContentsPluginReadParams8(self):

        local_params = {}
        local_params["target_path"] = self.nonexistent
        local_params["has_only"] = "dummy_value1"
        self.check_dir_contents_task.params = local_params

        v, r = self.check_dir_contents_task._read_params()
        self.assertFalse(v)
        self.assertEqual(r, "target path [%s] does not exist" % self.nonexistent)

    def testCheckDirContentsPluginReadParams9(self):

        local_params = {}
        local_params["target_path"] = self.existent_file
        local_params["has_only"] = "dummy_value1"
        self.check_dir_contents_task.params = local_params

        v, r = self.check_dir_contents_task._read_params()
        self.assertFalse(v)
        self.assertEqual(r, "target path [%s] is not a folder" % self.existent_file)

    def testCheckDirContentsPluginReadParams10(self):

        local_params = {}
        local_params["target_path"] = self.existent_dir
        self.check_dir_contents_task.params = local_params

        v, r = self.check_dir_contents_task._read_params()
        self.assertFalse(v)
        self.assertEqual(r, "no checks selected")

    def testCheckDirContentsPluginReadParams11(self):

        local_params = {}
        local_params["target_path"] = self.existent_dir
        local_params["has_only"] = "dummy_value1"
        local_params["has"] = "dummy_value2"
        self.check_dir_contents_task.params = local_params

        v, r = self.check_dir_contents_task._read_params()
        self.assertFalse(v)
        self.assertEqual(r, "has_only cannot be selected with anything else")

    def testCheckDirContentsPluginReadParams12(self):

        local_params = {}
        local_params["target_path"] = self.existent_dir
        local_params["has_only"] = "dummy_value1"
        local_params["not"] = "dummy_value2"
        self.check_dir_contents_task.params = local_params

        v, r = self.check_dir_contents_task._read_params()
        self.assertFalse(v)
        self.assertEqual(r, "has_only cannot be selected with anything else")

    def testCheckDirContentsPluginRunTask1(self):

        local_params = {}
        local_params["target_path"] = self.existent_dir
        local_params["has_only"] = "dummy_value1"
        self.check_dir_contents_task.params = local_params

        with mock.patch("fsquery.makecontentlist", return_value=(False, "dummy_error_msg")) as dummy:
            v, r = self.check_dir_contents_task.run_task(print, "exe_name")
            self.assertFalse(v)
            self.assertEqual(r, "dummy_error_msg")
            dummy.assert_called_with(self.existent_dir, False, False, True, True, True, True, True, None)

    def testCheckDirContentsPluginRunTask2(self):

        local_params = {}
        local_params["target_path"] = self.existent_dir
        local_params["has_only"] = "dummy_value1"
        self.check_dir_contents_task.params = local_params

        with mock.patch("fsquery.makecontentlist", return_value=(True, ["/base/dummy_value1"])) as dummy:
            v, r = self.check_dir_contents_task.run_task(print, "exe_name")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(self.existent_dir, False, False, True, True, True, True, True, None)

    def testCheckDirContentsPluginRunTask3(self):

        local_params = {}
        local_params["target_path"] = self.existent_dir
        local_params["has_only"] = ["dummy_value1", "dummy_value2"]
        self.check_dir_contents_task.params = local_params

        with mock.patch("fsquery.makecontentlist", return_value=(True, ["/base/dummy_value1", "/base/dummy_value2"])) as dummy:
            v, r = self.check_dir_contents_task.run_task(print, "exe_name")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(self.existent_dir, False, False, True, True, True, True, True, None)

    def testCheckDirContentsPluginRunTask4(self):

        local_params = {}
        local_params["target_path"] = self.existent_dir
        local_params["has_only"] = "dummy_value1"
        self.check_dir_contents_task.params = local_params

        with mock.patch("fsquery.makecontentlist", return_value=(True, ["/base/dummy_value2"])) as dummy:
            v, r = self.check_dir_contents_task.run_task(print, "exe_name")
            self.assertFalse(v)
            self.assertEqual(r, "[dummy_value2] is unexpectedly contained on [%s] (has-only). found none of the [1] expected on [%s] (has-only)" % (self.existent_dir, self.existent_dir))
            dummy.assert_called_with(self.existent_dir, False, False, True, True, True, True, True, None)

    def testCheckDirContentsPluginRunTask5(self):

        local_params = {}
        local_params["target_path"] = self.existent_dir
        local_params["has_only"] = "dummy_value1"
        self.check_dir_contents_task.params = local_params

        with mock.patch("fsquery.makecontentlist", return_value=(True, [])) as dummy:
            v, r = self.check_dir_contents_task.run_task(print, "exe_name")
            self.assertFalse(v)
            self.assertEqual(r, "found none of the [1] expected on [%s] (has-only)" % self.existent_dir)
            dummy.assert_called_with(self.existent_dir, False, False, True, True, True, True, True, None)

    def testCheckDirContentsPluginRunTask6(self):

        local_params = {}
        local_params["target_path"] = self.existent_dir
        local_params["has_only"] = ["dummy_value1", "dummy_value2"]
        self.check_dir_contents_task.params = local_params

        with mock.patch("fsquery.makecontentlist", return_value=(True, ["/base/dummy_value3", "/base/dummy_value4"])) as dummy:
            v, r = self.check_dir_contents_task.run_task(print, "exe_name")
            self.assertFalse(v)
            self.assertEqual(r, "[dummy_value3] is unexpectedly contained on [%s] (has-only). [dummy_value4] is unexpectedly contained on [%s] (has-only). found none of the [2] expected on [%s] (has-only)" % (self.existent_dir, self.existent_dir, self.existent_dir))
            dummy.assert_called_with(self.existent_dir, False, False, True, True, True, True, True, None)

    def testCheckDirContentsPluginRunTask7(self):

        local_params = {}
        local_params["target_path"] = self.existent_dir
        local_params["has_only"] = ["dummy_value1", "dummy_value2"]
        self.check_dir_contents_task.params = local_params

        with mock.patch("fsquery.makecontentlist", return_value=(True, ["/base/dummy_value2", "/base/dummy_value3"])) as dummy:
            v, r = self.check_dir_contents_task.run_task(print, "exe_name")
            self.assertFalse(v)
            self.assertEqual(r, "[dummy_value3] is unexpectedly contained on [%s] (has-only). found only [1] out of [2] expected on [%s] (has-only)" % (self.existent_dir, self.existent_dir))
            dummy.assert_called_with(self.existent_dir, False, False, True, True, True, True, True, None)

    def testCheckDirContentsPluginRunTask8(self):

        local_params = {}
        local_params["target_path"] = self.existent_dir
        local_params["has_only"] = "dummy_value1"
        self.check_dir_contents_task.params = local_params

        with mock.patch("fsquery.makecontentlist", return_value=(True, ["/base/dummy_value1", "/base/dummy_value2"])) as dummy:
            v, r = self.check_dir_contents_task.run_task(print, "exe_name")
            self.assertFalse(v)
            self.assertEqual(r, "[dummy_value2] is unexpectedly contained on [%s] (has-only)" % self.existent_dir)
            dummy.assert_called_with(self.existent_dir, False, False, True, True, True, True, True, None)

    def testCheckDirContentsPluginRunTask9(self):

        local_params = {}
        local_params["target_path"] = self.existent_dir
        local_params["has_only"] = "dummy_value1"
        self.check_dir_contents_task.params = local_params

        with mock.patch("fsquery.makecontentlist", return_value=(True, ["/base/dummy_value2", "/base/dummy_value1"])) as dummy:
            v, r = self.check_dir_contents_task.run_task(print, "exe_name")
            self.assertFalse(v)
            self.assertEqual(r, "[dummy_value2] is unexpectedly contained on [%s] (has-only)" % self.existent_dir)
            dummy.assert_called_with(self.existent_dir, False, False, True, True, True, True, True, None)

    def testCheckDirContentsPluginRunTask10(self):

        local_params = {}
        local_params["target_path"] = self.existent_dir
        local_params["has"] = ["dummy_value1"]
        self.check_dir_contents_task.params = local_params

        with mock.patch("fsquery.makecontentlist", return_value=(True, ["/base/dummy_value1"])) as dummy:
            v, r = self.check_dir_contents_task.run_task(print, "exe_name")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(self.existent_dir, False, False, True, True, True, True, True, None)

    def testCheckDirContentsPluginRunTask11(self):

        local_params = {}
        local_params["target_path"] = self.existent_dir
        local_params["has"] = ["dummy_value1", "dummy_value2"]
        self.check_dir_contents_task.params = local_params

        with mock.patch("fsquery.makecontentlist", return_value=(True, ["/base/dummy_value1", "/base/dummy_value2"])) as dummy:
            v, r = self.check_dir_contents_task.run_task(print, "exe_name")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(self.existent_dir, False, False, True, True, True, True, True, None)

    def testCheckDirContentsPluginRunTask12(self):

        local_params = {}
        local_params["target_path"] = self.existent_dir
        local_params["has"] = ["dummy_value1", "dummy_value2"]
        self.check_dir_contents_task.params = local_params

        with mock.patch("fsquery.makecontentlist", return_value=(True, ["/base/dummy_value1"])) as dummy:
            v, r = self.check_dir_contents_task.run_task(print, "exe_name")
            self.assertFalse(v)
            self.assertEqual(r, "[dummy_value2] was expected on [%s] (has)" % self.existent_dir)
            dummy.assert_called_with(self.existent_dir, False, False, True, True, True, True, True, None)

    def testCheckDirContentsPluginRunTask13(self):

        local_params = {}
        local_params["target_path"] = self.existent_dir
        local_params["not"] = ["dummy_value1"]
        self.check_dir_contents_task.params = local_params

        with mock.patch("fsquery.makecontentlist", return_value=(True, ["/base/dummy_value2"])) as dummy:
            v, r = self.check_dir_contents_task.run_task(print, "exe_name")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(self.existent_dir, False, False, True, True, True, True, True, None)

    def testCheckDirContentsPluginRunTask14(self):

        local_params = {}
        local_params["target_path"] = self.existent_dir
        local_params["not"] = ["dummy_value1", "dummy_value2"]
        self.check_dir_contents_task.params = local_params

        with mock.patch("fsquery.makecontentlist", return_value=(True, ["/base/dummy_value3", "/base/dummy_value4"])) as dummy:
            v, r = self.check_dir_contents_task.run_task(print, "exe_name")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(self.existent_dir, False, False, True, True, True, True, True, None)

    def testCheckDirContentsPluginRunTask15(self):

        local_params = {}
        local_params["target_path"] = self.existent_dir
        local_params["not"] = ["dummy_value1", "dummy_value2"]
        self.check_dir_contents_task.params = local_params

        with mock.patch("fsquery.makecontentlist", return_value=(True, ["/base/dummy_value2", "/base/dummy_value3"])) as dummy:
            v, r = self.check_dir_contents_task.run_task(print, "exe_name")
            self.assertFalse(v)
            self.assertEqual(r, "[dummy_value2] is unexpectedly contained on [%s] (not)" % self.existent_dir)
            dummy.assert_called_with(self.existent_dir, False, False, True, True, True, True, True, None)

if __name__ == "__main__":
    unittest.main()
