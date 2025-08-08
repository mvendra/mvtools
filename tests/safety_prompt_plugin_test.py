#!/usr/bin/env python3

import sys
import os
import shutil
import unittest
from unittest import mock
from unittest.mock import patch

import mvtools_test_fixture

import safety_prompt_plugin

class SafetyPromptPluginTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("safety_prompt_plugin_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # internal buffer
        self.internal_buffer = None

        # the test task
        self.safety_prompt_task = safety_prompt_plugin.CustomTask()

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def _helper_mock_feedback_obj(self, input_msg):
        self.internal_buffer = input_msg

    def testSafetyPromptPluginReadParams1(self):

        local_params = {}
        self.safety_prompt_task.params = local_params

        v, r = self.safety_prompt_task._read_params()
        self.assertFalse(v)
        self.assertEqual(r, "msg is a required parameter")

    def testSafetyPromptPluginReadParams2(self):

        local_params = {}
        local_params["msg"] = "dummy_value"
        self.safety_prompt_task.params = local_params

        v, r = self.safety_prompt_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, "dummy_value")

    def testSafetyPromptPluginRunTask1(self):

        local_params = {}
        local_params["msg"] = "dummy_value"
        self.safety_prompt_task.params = local_params

        with mock.patch("builtins.input", return_value="yes") as dummy:
            v, r = self.safety_prompt_task.run_task(self._helper_mock_feedback_obj, "exe_name")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with("Input your answer (yes / no): ")

        self.assertEqual(self.internal_buffer, "dummy_value")

    def testSafetyPromptPluginRunTask2(self):

        local_params = {}
        local_params["msg"] = "dummy_value1"
        self.safety_prompt_task.params = local_params

        with mock.patch("builtins.input", return_value="dummy_value2") as dummy:
            v, r = self.safety_prompt_task.run_task(self._helper_mock_feedback_obj, "exe_name")
            self.assertFalse(v)
            self.assertEqual(r, "safety_prompt failed: the provided answer was in the negative: [dummy_value2]")
            dummy.assert_called_with("Input your answer (yes / no): ")

        self.assertEqual(self.internal_buffer, "dummy_value1")

if __name__ == "__main__":
    unittest.main()
