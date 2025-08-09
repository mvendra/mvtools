#!/usr/bin/env python3

import sys
import os
import shutil
import unittest
from unittest import mock
from unittest.mock import patch
from unittest.mock import call

import mvtools_test_fixture
import path_utils

import codelint_plugin

class CodelintPluginTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("codelint_plugin_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # the test task
        self.codelint_task = codelint_plugin.CustomTask()

        # internals
        self.feedback_obj_mock_stash = []

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)
        self.feedback_obj_mock_stash.clear()

    def feedback_object_mock(self, msg):
        self.feedback_obj_mock_stash.append(msg)

    def testCodelintPluginReadParams1(self):

        local_params = {}
        local_params["files"] = "dummy_value1"
        self.codelint_task.params = local_params

        v, r = self.codelint_task._read_params()
        self.assertFalse(v)

    def testCodelintPluginReadParams2(self):

        local_params = {}
        local_params["plugins"] = "dummy_value1"
        self.codelint_task.params = local_params

        v, r = self.codelint_task._read_params()
        self.assertFalse(v)

    def testCodelintPluginReadParams3(self):

        local_params = {}
        local_params["plugins"] = "dummy_value1"
        local_params["files"] = "dummy_value2"
        self.codelint_task.params = local_params

        v, r = self.codelint_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, (["dummy_value1"], None, None, False, False, ["dummy_value2"], None, None))

    def testCodelintPluginReadParams4(self):

        local_params = {}
        local_params["plugins"] = "dummy_value1"
        local_params["plugins_params"] = ["dummy_value2", "dummy_value3"]
        local_params["files"] = "dummy_value4"
        self.codelint_task.params = local_params

        v, r = self.codelint_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, (["dummy_value1"], ["dummy_value2", "dummy_value3"], None, False, False, ["dummy_value4"], None, None))

    def testCodelintPluginReadParams5(self):

        local_params = {}
        local_params["plugins"] = "dummy_value1"
        local_params["filters"] = ["dummy_value2", "dummy_value3"]
        local_params["files"] = "dummy_value4"
        self.codelint_task.params = local_params

        v, r = self.codelint_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, (["dummy_value1"], None, ["dummy_value2", "dummy_value3"], False, False, ["dummy_value4"], None, None))

    def testCodelintPluginReadParams6(self):

        local_params = {}
        local_params["plugins"] = "dummy_value1"
        local_params["files"] = "dummy_value2"
        local_params["autocorrect"] = "dummy_value3"
        self.codelint_task.params = local_params

        v, r = self.codelint_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, (["dummy_value1"], None, None, True, False, ["dummy_value2"], None, None))

    def testCodelintPluginReadParams7(self):

        local_params = {}
        local_params["plugins"] = "dummy_value1"
        local_params["files"] = "dummy_value2"
        local_params["skip_non_utf8"] = "dummy_value3"
        self.codelint_task.params = local_params

        v, r = self.codelint_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, (["dummy_value1"], None, None, False, True, ["dummy_value2"], None, None))

    def testCodelintPluginReadParams8(self):

        local_params = {}
        local_params["plugins"] = "dummy_value1"
        local_params["folder"] = "dummy_value2"
        self.codelint_task.params = local_params

        v, r = self.codelint_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, (["dummy_value1"], None, None, False, False, None, "dummy_value2", None))

    def testCodelintPluginReadParams9(self):

        local_params = {}
        local_params["plugins"] = "dummy_value1"
        local_params["folder"] = "dummy_value2"
        local_params["extensions"] = "dummy_value3"
        self.codelint_task.params = local_params

        v, r = self.codelint_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, (["dummy_value1"], None, None, False, False, None, "dummy_value2", ["dummy_value3"]))

    def testCodelintPluginReadParams10(self):

        local_params = {}
        local_params["plugins"] = "dummy_value1"
        local_params["folder"] = "dummy_value2"
        local_params["extensions"] = ["dummy_value3", "dummy_value4"]
        self.codelint_task.params = local_params

        v, r = self.codelint_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, (["dummy_value1"], None, None, False, False, None, "dummy_value2", ["dummy_value3", "dummy_value4"]))

    def testCodelintPluginReadParams11(self):

        local_params = {}
        local_params["plugins"] = "dummy_value1"
        local_params["plugins_params"] = ["dummy_value2"]
        local_params["files"] = "dummy_value3"
        self.codelint_task.params = local_params

        v, r = self.codelint_task._read_params()
        self.assertFalse(v)

    def testCodelintPluginReadParams12(self):

        local_params = {}
        local_params["plugins"] = "dummy_value1"
        local_params["filters"] = ["dummy_value2"]
        local_params["files"] = "dummy_value3"
        self.codelint_task.params = local_params

        v, r = self.codelint_task._read_params()
        self.assertFalse(v)

    def testCodelintPluginReadParams13(self):

        local_params = {}
        local_params["plugins"] = "dummy_value1"
        local_params["files"] = "dummy_value2"
        local_params["folder"] = "dummy_value3"
        self.codelint_task.params = local_params

        v, r = self.codelint_task._read_params()
        self.assertFalse(v)

    def testCodelintPluginReadParams14(self):

        local_params = {}
        local_params["plugins"] = "dummy_value1"
        local_params["files"] = "dummy_value2"
        local_params["extensions"] = "dummy_value3"
        self.codelint_task.params = local_params

        v, r = self.codelint_task._read_params()
        self.assertFalse(v)

    def testCodelintPluginRunTask1(self):

        local_params = {}
        local_params["plugins"] = "dummy_value1"
        local_params["files"] = "dummy_value2"
        self.codelint_task.params = local_params

        with mock.patch("codelint.codelint", return_value=(True, [])) as dummy:
            v, r = self.codelint_task.run_task(print, "exe_name")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(["dummy_value1"], {}, {}, False, False, ["dummy_value2"])

    def testCodelintPluginRunTask2(self):

        local_params = {}
        local_params["plugins"] = "dummy_value1"
        local_params["plugins_params"] = ["dummy_value2", "dummy_value3"]
        local_params["files"] = "dummy_value4"
        self.codelint_task.params = local_params

        with mock.patch("codelint.codelint", return_value=(True, [])) as dummy:
            v, r = self.codelint_task.run_task(print, "exe_name")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(["dummy_value1"], {"dummy_value2": ["dummy_value3"]}, {}, False, False, ["dummy_value4"])

    def testCodelintPluginRunTask3(self):

        local_params = {}
        local_params["plugins"] = "dummy_value1"
        local_params["plugins_params"] = ["dummy_value2", "dummy_value3", "dummy_value2", "dummy_value4"]
        local_params["files"] = "dummy_value5"
        self.codelint_task.params = local_params

        with mock.patch("codelint.codelint", return_value=(True, [])) as dummy:
            v, r = self.codelint_task.run_task(print, "exe_name")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(["dummy_value1"], {"dummy_value2": ["dummy_value3", "dummy_value4"]}, {}, False, False, ["dummy_value5"])

    def testCodelintPluginRunTask4(self):

        local_params = {}
        local_params["plugins"] = "dummy_value1"
        local_params["filters"] = ["dummy_value2", "dummy_value3"]
        local_params["files"] = "dummy_value4"
        self.codelint_task.params = local_params

        with mock.patch("codelint.codelint", return_value=(True, [])) as dummy:
            v, r = self.codelint_task.run_task(print, "exe_name")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(["dummy_value1"], {}, {"dummy_value2": ["dummy_value3"]}, False, False, ["dummy_value4"])

    def testCodelintPluginRunTask5(self):

        local_params = {}
        local_params["plugins"] = "dummy_value1"
        local_params["filters"] = ["dummy_value2", "dummy_value3", "dummy_value2", "dummy_value4"]
        local_params["files"] = "dummy_value5"
        self.codelint_task.params = local_params

        with mock.patch("codelint.codelint", return_value=(True, [])) as dummy:
            v, r = self.codelint_task.run_task(print, "exe_name")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(["dummy_value1"], {}, {"dummy_value2": ["dummy_value3", "dummy_value4"]}, False, False, ["dummy_value5"])

    def testCodelintPluginRunTask6(self):

        local_params = {}
        local_params["plugins"] = "dummy_value1"
        local_params["folder"] = "dummy_value2"
        self.codelint_task.params = local_params

        with mock.patch("codelint.codelint", return_value=(True, [])) as dummy1:
            with mock.patch("codelint.files_from_folder", return_value=(True, ["dummy_value3"])) as dummy2:
                v, r = self.codelint_task.run_task(print, "exe_name")
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy1.assert_called_with(["dummy_value1"], {}, {}, False, False, ["dummy_value3"])
                dummy2.assert_called_with("dummy_value2", None)

    def testCodelintPluginRunTask7(self):

        local_params = {}
        local_params["plugins"] = "dummy_value1"
        local_params["folder"] = "dummy_value2"
        local_params["extensions"] = ["dummy_value3"]
        self.codelint_task.params = local_params

        with mock.patch("codelint.codelint", return_value=(True, [])) as dummy1:
            with mock.patch("codelint.files_from_folder", return_value=(True, ["dummy_value4"])) as dummy2:
                v, r = self.codelint_task.run_task(print, "exe_name")
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy1.assert_called_with(["dummy_value1"], {}, {}, False, False, ["dummy_value4"])
                dummy2.assert_called_with("dummy_value2", ["dummy_value3"])

    def testCodelintPluginRunTask8(self):

        local_params = {}
        local_params["plugins"] = "dummy_value1"
        local_params["autocorrect"] = "dummy_value2"
        local_params["folder"] = "dummy_value3"
        self.codelint_task.params = local_params

        with mock.patch("codelint.codelint", return_value=(True, [])) as dummy1:
            with mock.patch("codelint.files_from_folder", return_value=(True, ["dummy_value4"])) as dummy2:
                v, r = self.codelint_task.run_task(print, "exe_name")
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy1.assert_called_with(["dummy_value1"], {}, {}, True, False, ["dummy_value4"])
                dummy2.assert_called_with("dummy_value3", None)

    def testCodelintPluginRunTask9(self):

        local_params = {}
        local_params["plugins"] = "dummy_value1"
        local_params["files"] = "dummy_value2"
        self.codelint_task.params = local_params

        with mock.patch("codelint.codelint", return_value=(False, ("dummy_value3", []))) as dummy:
            v, r = self.codelint_task.run_task(print, "exe_name")
            self.assertFalse(v)
            self.assertEqual(r, "dummy_value3")
            dummy.assert_called_with(["dummy_value1"], {}, {}, False, False, ["dummy_value2"])

    def testCodelintPluginRunTask10(self):

        local_params = {}
        local_params["plugins"] = "dummy_value1"
        local_params["files"] = "dummy_value2"
        self.codelint_task.params = local_params

        with mock.patch("codelint.codelint", return_value=(False, ("dummy_value3", [(False, "dummy_value4"), (True, "dummy_value5")]))) as dummy:
            v, r = self.codelint_task.run_task(self.feedback_object_mock, "exe_name")
            self.assertFalse(v)
            self.assertEqual(r, "dummy_value3")
            self.assertEqual(len(self.feedback_obj_mock_stash), 3)
            self.assertEqual(self.feedback_obj_mock_stash[0], "Partially generated report:")
            self.assertEqual(self.feedback_obj_mock_stash[1], "dummy_value4")
            self.assertEqual(self.feedback_obj_mock_stash[2], "dummy_value5")
            dummy.assert_called_with(["dummy_value1"], {}, {}, False, False, ["dummy_value2"])

    def testCodelintPluginRunTask11(self):

        local_params = {}
        local_params["plugins"] = "dummy_value1"
        local_params["files"] = "dummy_value2"
        self.codelint_task.params = local_params

        with mock.patch("codelint.codelint", return_value=(True, [(True, "dummy_value3")])) as dummy:
            v, r = self.codelint_task.run_task(self.feedback_object_mock, "exe_name")
            self.assertTrue(v)
            self.assertEqual(r, "(1 finding): #1: dummy_value3.")
            self.assertEqual(len(self.feedback_obj_mock_stash), 0)
            dummy.assert_called_with(["dummy_value1"], {}, {}, False, False, ["dummy_value2"])

    def testCodelintPluginRunTask12(self):

        local_params = {}
        local_params["plugins"] = "dummy_value1"
        local_params["files"] = "dummy_value2"
        self.codelint_task.params = local_params

        with mock.patch("codelint.codelint", return_value=(True, [(True, "dummy_value3"), (True, "dummy_value4")])) as dummy:
            v, r = self.codelint_task.run_task(self.feedback_object_mock, "exe_name")
            self.assertTrue(v)
            self.assertEqual(r, "(2 findings): #1: dummy_value3. #2: dummy_value4.")
            self.assertEqual(len(self.feedback_obj_mock_stash), 0)
            dummy.assert_called_with(["dummy_value1"], {}, {}, False, False, ["dummy_value2"])

    def testCodelintPluginRunTask13(self):

        local_params = {}
        local_params["plugins"] = "dummy_value1"
        local_params["files"] = "dummy_value2"
        self.codelint_task.params = local_params

        with mock.patch("codelint.codelint", return_value=(True, [(False, "dummy_value3")])) as dummy:
            v, r = self.codelint_task.run_task(self.feedback_object_mock, "exe_name")
            self.assertTrue(v)
            self.assertEqual(r, None)
            self.assertEqual(len(self.feedback_obj_mock_stash), 1)
            self.assertEqual(self.feedback_obj_mock_stash[0], "dummy_value3")
            dummy.assert_called_with(["dummy_value1"], {}, {}, False, False, ["dummy_value2"])

    def testCodelintPluginRunTask14(self):

        local_params = {}
        local_params["plugins"] = "dummy_value1"
        local_params["files"] = "dummy_value2"
        self.codelint_task.params = local_params

        with mock.patch("codelint.codelint", return_value=(True, [(False, "dummy_value3"), (False, "dummy_value4")])) as dummy:
            v, r = self.codelint_task.run_task(self.feedback_object_mock, "exe_name")
            self.assertTrue(v)
            self.assertEqual(r, None)
            self.assertEqual(len(self.feedback_obj_mock_stash), 2)
            self.assertEqual(self.feedback_obj_mock_stash[0], "dummy_value3")
            self.assertEqual(self.feedback_obj_mock_stash[1], "dummy_value4")
            dummy.assert_called_with(["dummy_value1"], {}, {}, False, False, ["dummy_value2"])

    def testCodelintPluginRunTask15(self):

        local_params = {}
        local_params["plugins"] = "dummy_value1"
        local_params["files"] = "dummy_value2"
        self.codelint_task.params = local_params

        with mock.patch("codelint.codelint", return_value=(True, [(True, "dummy_value3"), (False, "dummy_value4")])) as dummy:
            v, r = self.codelint_task.run_task(self.feedback_object_mock, "exe_name")
            self.assertTrue(v)
            self.assertEqual(r, "(1 finding): #1: dummy_value3.")
            self.assertEqual(len(self.feedback_obj_mock_stash), 1)
            self.assertEqual(self.feedback_obj_mock_stash[0], "dummy_value4")
            dummy.assert_called_with(["dummy_value1"], {}, {}, False, False, ["dummy_value2"])

if __name__ == "__main__":
    unittest.main()
