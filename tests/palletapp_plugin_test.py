#!/usr/bin/env python

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

import palletapp_plugin

class DummyCapture:
    def __init__(self):
        self.buffer = []
    def __call__(self, input):
        self.buffer.append(input)

class PalletappPluginTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("palletapp_plugin_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # the test task
        self.palletapp_task = palletapp_plugin.CustomTask()

        # test contents
        self.pallet_file = "test.plt"
        self.pallet_file_full = path_utils.concat_path(self.test_dir, self.pallet_file)

        self.test_folder = "test_folder"
        self.test_folder_full = path_utils.concat_path(self.test_dir, self.test_folder)

        self.test_file1 = "test_file1"
        self.test_file1_full = path_utils.concat_path(self.test_dir, self.test_file1)

        self.test_file2 = "test_file2"
        self.test_file2_full = path_utils.concat_path(self.test_dir, self.test_file2)

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testPalletappPluginReadParams1(self):

        local_params = {}
        self.palletapp_task.params = local_params

        v, r = self.palletapp_task._read_params()
        self.assertFalse(v)

    def testPalletappPluginReadParams2(self):

        local_params = {}
        local_params["operation"] = "dummy_value1"
        self.palletapp_task.params = local_params

        v, r = self.palletapp_task._read_params()
        self.assertFalse(v)

    def testPalletappPluginReadParams3(self):

        local_params = {}
        local_params["operation"] = "dummy_value1"
        local_params["archive"] = "dummy_value2"
        self.palletapp_task.params = local_params

        v, r = self.palletapp_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", None, None) )

    def testPalletappPluginReadParams4(self):

        local_params = {}
        local_params["operation"] = "dummy_value1"
        local_params["archive"] = "dummy_value2"
        local_params["path"] = "dummy_value3"
        self.palletapp_task.params = local_params

        v, r = self.palletapp_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", ["dummy_value3"], None) )

    def testPalletappPluginReadParams5(self):

        local_params = {}
        local_params["operation"] = "dummy_value1"
        local_params["archive"] = "dummy_value2"
        local_params["path"] = ["dummy_value3", "dummy_value4"]
        self.palletapp_task.params = local_params

        v, r = self.palletapp_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", ["dummy_value3", "dummy_value4"], None) )

    def testPalletappPluginReadParams6(self):

        local_params = {}
        local_params["operation"] = "dummy_value1"
        local_params["archive"] = "dummy_value2"
        local_params["path"] = ["dummy_value3", "dummy_value4"]
        local_params["route"] = "dummy_value5"
        self.palletapp_task.params = local_params

        v, r = self.palletapp_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", ["dummy_value3", "dummy_value4"], ["dummy_value5"]) )

    def testPalletappPluginReadParams7(self):

        local_params = {}
        local_params["operation"] = "dummy_value1"
        local_params["archive"] = "dummy_value2"
        local_params["path"] = ["dummy_value3", "dummy_value4"]
        local_params["route"] = ["dummy_value5", "dummy_value6"]
        self.palletapp_task.params = local_params

        v, r = self.palletapp_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", ["dummy_value3", "dummy_value4"], ["dummy_value5", "dummy_value6"]) )

    def testPalletappPluginRunTask1(self):

        local_params = {}
        local_params["operation"] = "dummy_value1"
        local_params["archive"] = "dummy_value2"
        local_params["path"] = ["dummy_value3", "dummy_value4"]
        local_params["route"] = ["dummy_value5", "dummy_value6"]
        self.palletapp_task.params = local_params

        v, r = self.palletapp_task.run_task(print, "exe_name")
        self.assertFalse(v)
        self.assertEqual(r, "Operation [dummy_value1] is invalid")

    def testPalletappPluginRunTask2(self):

        local_params = {}
        local_params["operation"] = "init"
        local_params["archive"] = "dummy_value2"
        local_params["path"] = ["dummy_value3", "dummy_value4"]
        local_params["route"] = ["dummy_value5", "dummy_value6"]
        self.palletapp_task.params = local_params

        with mock.patch("palletapp_plugin.CustomTask.task_init", return_value=(True, None)) as dummy:
            v, r = self.palletapp_task.run_task(print, "exe_name")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(print, "dummy_value2")

    def testPalletappPluginRunTask3(self):

        local_params = {}
        local_params["operation"] = "create"
        local_params["archive"] = "dummy_value2"
        local_params["path"] = ["dummy_value3", "dummy_value4"]
        local_params["route"] = ["dummy_value5", "dummy_value6"]
        self.palletapp_task.params = local_params

        with mock.patch("palletapp_plugin.CustomTask.task_create", return_value=(True, None)) as dummy:
            v, r = self.palletapp_task.run_task(print, "exe_name")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(print, "dummy_value2", ["dummy_value3", "dummy_value4"])

    def testPalletappPluginRunTask4(self):

        local_params = {}
        local_params["operation"] = "extract"
        local_params["archive"] = "dummy_value2"
        local_params["path"] = ["dummy_value3", "dummy_value4"]
        local_params["route"] = ["dummy_value5", "dummy_value6"]
        self.palletapp_task.params = local_params

        with mock.patch("palletapp_plugin.CustomTask.task_extract", return_value=(True, None)) as dummy:
            v, r = self.palletapp_task.run_task(print, "exe_name")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(print, "dummy_value2", ["dummy_value3", "dummy_value4"])

    def testPalletappPluginRunTask5(self):

        local_params = {}
        local_params["operation"] = "load"
        local_params["archive"] = "dummy_value2"
        local_params["path"] = ["dummy_value3", "dummy_value4"]
        local_params["route"] = ["dummy_value5", "dummy_value6"]
        self.palletapp_task.params = local_params

        with mock.patch("palletapp_plugin.CustomTask.task_load", return_value=(True, None)) as dummy:
            v, r = self.palletapp_task.run_task(print, "exe_name")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(print, "dummy_value2", ["dummy_value3", "dummy_value4"])

    def testPalletappPluginRunTask6(self):

        local_params = {}
        local_params["operation"] = "ditch"
        local_params["archive"] = "dummy_value2"
        local_params["path"] = ["dummy_value3", "dummy_value4"]
        local_params["route"] = ["dummy_value5", "dummy_value6"]
        self.palletapp_task.params = local_params

        with mock.patch("palletapp_plugin.CustomTask.task_ditch", return_value=(True, None)) as dummy:
            v, r = self.palletapp_task.run_task(print, "exe_name")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(print, "dummy_value2", ["dummy_value5", "dummy_value6"])

    def testPalletappPluginRunTask7(self):

        local_params = {}
        local_params["operation"] = "export"
        local_params["archive"] = "dummy_value2"
        local_params["path"] = ["dummy_value3", "dummy_value4"]
        local_params["route"] = ["dummy_value5", "dummy_value6"]
        self.palletapp_task.params = local_params

        with mock.patch("palletapp_plugin.CustomTask.task_export", return_value=(True, None)) as dummy:
            v, r = self.palletapp_task.run_task(print, "exe_name")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(print, "dummy_value2", ["dummy_value5", "dummy_value6"], ["dummy_value3", "dummy_value4"])

    def testPalletappPluginRunTask8(self):

        local_params = {}
        local_params["operation"] = "list"
        local_params["archive"] = "dummy_value2"
        local_params["path"] = ["dummy_value3", "dummy_value4"]
        local_params["route"] = ["dummy_value5", "dummy_value6"]
        self.palletapp_task.params = local_params

        with mock.patch("palletapp_plugin.CustomTask.task_list", return_value=(True, None)) as dummy:
            v, r = self.palletapp_task.run_task(print, "exe_name")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(print, "dummy_value2")

    def testPalletappPluginTaskInit1(self):

        with mock.patch("palletapp_wrapper.init", return_value=(False, "test error")) as dummy:
            v, r = self.palletapp_task.task_init(print, "dummy_value1")
            self.assertFalse(v)
            self.assertEqual(r, "test error")
            dummy.assert_called_with("dummy_value1")

    def testPalletappPluginTaskInit2(self):

        with mock.patch("palletapp_wrapper.init", return_value=(True, "test return")) as dummy:
            v, r = self.palletapp_task.task_init(print, "dummy_value1")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with("dummy_value1")

    def testPalletappPluginTaskCreate1(self):

        with mock.patch("palletapp_wrapper.create", return_value=(True, "test return")) as dummy:
            v, r = self.palletapp_task.task_create(print, "dummy_value1", None)
            self.assertFalse(v)
            self.assertEqual(r, "path is a required parameter, for the create operation")
            dummy.assert_not_called()

    def testPalletappPluginTaskCreate2(self):

        with mock.patch("palletapp_wrapper.create", return_value=(False, "test error")) as dummy:
            v, r = self.palletapp_task.task_create(print, "dummy_value1", ["dummy_value2", "dummy_value3"])
            self.assertFalse(v)
            self.assertEqual(r, "test error")
            dummy.assert_called_with("dummy_value1", "dummy_value2")

    def testPalletappPluginTaskCreate3(self):

        with mock.patch("palletapp_wrapper.create", return_value=(True, "test return")) as dummy:
            v, r = self.palletapp_task.task_create(print, "dummy_value1", ["dummy_value2", "dummy_value3"])
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with("dummy_value1", "dummy_value2")

    def testPalletappPluginTaskExtract1(self):

        with mock.patch("palletapp_wrapper.extract", return_value=(True, "test return")) as dummy:
            v, r = self.palletapp_task.task_extract(print, "dummy_value1", None)
            self.assertFalse(v)
            self.assertEqual(r, "path is a required parameter, for the extract operation")
            dummy.assert_not_called()

    def testPalletappPluginTaskExtract2(self):

        with mock.patch("palletapp_wrapper.extract", return_value=(False, "test error")) as dummy:
            v, r = self.palletapp_task.task_extract(print, "dummy_value1", ["dummy_value2", "dummy_value3"])
            self.assertFalse(v)
            self.assertEqual(r, "test error")
            dummy.assert_called_with("dummy_value1", "dummy_value2")

    def testPalletappPluginTaskExtract3(self):

        with mock.patch("palletapp_wrapper.extract", return_value=(True, "test return")) as dummy:
            v, r = self.palletapp_task.task_extract(print, "dummy_value1", ["dummy_value2", "dummy_value3"])
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with("dummy_value1", "dummy_value2")

    def testPalletappPluginTaskLoad1(self):

        with mock.patch("palletapp_wrapper.load", return_value=(True, "test return")) as dummy:
            v, r = self.palletapp_task.task_load(print, "dummy_value1", None)
            self.assertFalse(v)
            self.assertEqual(r, "path is a required parameter, for the load operation")
            dummy.assert_not_called()

    def testPalletappPluginTaskLoad2(self):

        with mock.patch("palletapp_wrapper.load", return_value=(False, "test error")) as dummy:
            v, r = self.palletapp_task.task_load(print, "dummy_value1", ["dummy_value2", "dummy_value3"])
            self.assertFalse(v)
            self.assertEqual(r, "test error")
            dummy.assert_called_with("dummy_value1", "dummy_value2")

    def testPalletappPluginTaskLoad3(self):

        with mock.patch("palletapp_wrapper.load", return_value=(True, "test return")) as dummy:
            v, r = self.palletapp_task.task_load(print, "dummy_value1", ["dummy_value2", "dummy_value3"])
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_has_calls([call("dummy_value1", "dummy_value2"), call("dummy_value1", "dummy_value3")])

    def testPalletappPluginTaskDitch1(self):

        with mock.patch("palletapp_wrapper.ditch", return_value=(True, "test return")) as dummy:
            v, r = self.palletapp_task.task_ditch(print, "dummy_value1", None)
            self.assertFalse(v)
            self.assertEqual(r, "route is a required parameter, for the ditch operation")
            dummy.assert_not_called()

    def testPalletappPluginTaskDitch2(self):

        with mock.patch("palletapp_wrapper.ditch", return_value=(False, "test error")) as dummy:
            v, r = self.palletapp_task.task_ditch(print, "dummy_value1", ["dummy_value2", "dummy_value3"])
            self.assertFalse(v)
            self.assertEqual(r, "test error")
            dummy.assert_called_with("dummy_value1", "dummy_value2")

    def testPalletappPluginTaskDitch3(self):

        with mock.patch("palletapp_wrapper.ditch", return_value=(True, "test return")) as dummy:
            v, r = self.palletapp_task.task_ditch(print, "dummy_value1", ["dummy_value2", "dummy_value3"])
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_has_calls([call("dummy_value1", "dummy_value2"), call("dummy_value1", "dummy_value3")])

    def testPalletappPluginTaskExport1(self):

        with mock.patch("palletapp_wrapper.export", return_value=(True, "test return")) as dummy:
            v, r = self.palletapp_task.task_export(print, "dummy_value1", None, ["dummy_value4", "dummy_value5"])
            self.assertFalse(v)
            self.assertEqual(r, "route is a required parameter, for the export operation")
            dummy.assert_not_called()

    def testPalletappPluginTaskExport2(self):

        with mock.patch("palletapp_wrapper.export", return_value=(True, "test return")) as dummy:
            v, r = self.palletapp_task.task_export(print, "dummy_value1", ["dummy_value2", "dummy_value3"], None)
            self.assertFalse(v)
            self.assertEqual(r, "path is a required parameter, for the export operation")
            dummy.assert_not_called()

    def testPalletappPluginTaskExport3(self):

        with mock.patch("palletapp_wrapper.export", return_value=(False, "test error")) as dummy:
            v, r = self.palletapp_task.task_export(print, "dummy_value1", ["dummy_value2", "dummy_value3"], ["dummy_value4", "dummy_value5"])
            self.assertFalse(v)
            self.assertEqual(r, "test error")
            dummy.assert_called_with("dummy_value1", "dummy_value2", "dummy_value4")

    def testPalletappPluginTaskExport4(self):

        with mock.patch("palletapp_wrapper.export", return_value=(True, "test return")) as dummy:
            v, r = self.palletapp_task.task_export(print, "dummy_value1", ["dummy_value2", "dummy_value3"], ["dummy_value4", "dummy_value5"])
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with("dummy_value1", "dummy_value2", "dummy_value4")

    def testPalletappPluginTaskList1(self):

        with mock.patch("palletapp_wrapper.list", return_value=(False, "test error")) as dummy:
            v, r = self.palletapp_task.task_list(print, "dummy_value1")
            self.assertFalse(v)
            self.assertEqual(r, "test error")
            dummy.assert_called_with("dummy_value1")

    def testPalletappPluginTaskList2(self):

        dummy_capture = DummyCapture()

        with mock.patch("palletapp_wrapper.list", return_value=(True, "test return, line1%stest return, line2" % os.linesep)) as dummy:
            v, r = self.palletapp_task.task_list(dummy_capture, "dummy_value1")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with("dummy_value1")

        self.assertEqual(dummy_capture.buffer, ["Archive contents:", "test return, line1", "test return, line2"])

if __name__ == "__main__":
    unittest.main()
