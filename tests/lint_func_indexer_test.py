#!/usr/bin/env python3

import sys
import os
import shutil
import unittest

import mvtools_test_fixture
import path_utils

import lint_func_indexer

class LintFuncIndexerTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("lint_func_indexer_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testLintName(self):

        self.assertEqual(lint_func_indexer.lint_name(), "lint_func_indexer.py")

    def testLintPre1(self):

        test_file = "test_file.txt"
        test_lines = ["left1right", "left2right", "left3right"]
        test_plugins_params = {}
        test_shared_state = {}

        test_plugins_params["lint-func-indexer-param-left"] = "left"
        test_plugins_params["lint-func-indexer-param-right"] = "right"

        test_shared_state["lint-func-indexer-counter"] = 0

        v, r = lint_func_indexer.lint_pre(test_plugins_params, test_file, test_shared_state, len(test_lines))
        self.assertFalse(v)
        self.assertEqual(r, "shared state already contains {lint-func-indexer-counter}")

    def testLintPre2(self):

        test_file = "test_file.txt"
        test_lines = ["left1right", "left2right", "left3right"]
        test_plugins_params = {}
        test_shared_state = {}

        test_plugins_params["lint-func-indexer-param-right"] = "right"

        v, r = lint_func_indexer.lint_pre(test_plugins_params, test_file, test_shared_state, len(test_lines))
        self.assertFalse(v)
        self.assertEqual(r, "required parameter {lint-func-indexer-param-left} was not provided")

        expected_shared_state = {}
        expected_shared_state["lint-func-indexer-counter"] = 0

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintPre3(self):

        test_file = "test_file.txt"
        test_lines = ["left1right", "left2right", "left3right"]
        test_plugins_params = {}
        test_shared_state = {}

        test_plugins_params["lint-func-indexer-param-left"] = "left"

        v, r = lint_func_indexer.lint_pre(test_plugins_params, test_file, test_shared_state, len(test_lines))
        self.assertFalse(v)
        self.assertEqual(r, "required parameter {lint-func-indexer-param-right} was not provided")

        expected_shared_state = {}
        expected_shared_state["lint-func-indexer-counter"] = 0

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintPre4(self):

        test_file = "test_file.txt"
        test_lines = ["left1right", "left2right", "left3right"]
        test_plugins_params = {}
        test_shared_state = {}

        test_plugins_params["lint-func-indexer-param-left"] = ""
        test_plugins_params["lint-func-indexer-param-right"] = "right"

        v, r = lint_func_indexer.lint_pre(test_plugins_params, test_file, test_shared_state, len(test_lines))
        self.assertFalse(v)
        self.assertEqual(r, "the parameter {lint-func-indexer-param-left} cannot be empty")

        expected_shared_state = {}
        expected_shared_state["lint-func-indexer-counter"] = 0

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintPre5(self):

        test_file = "test_file.txt"
        test_lines = ["left1right", "left2right", "left3right"]
        test_plugins_params = {}
        test_shared_state = {}

        test_plugins_params["lint-func-indexer-param-left"] = "left"
        test_plugins_params["lint-func-indexer-param-right"] = ""

        v, r = lint_func_indexer.lint_pre(test_plugins_params, test_file, test_shared_state, len(test_lines))
        self.assertFalse(v)
        self.assertEqual(r, "the parameter {lint-func-indexer-param-right} cannot be empty")

        expected_shared_state = {}
        expected_shared_state["lint-func-indexer-counter"] = 0

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintPre6(self):

        test_file = "test_file.txt"
        test_lines = ["left1right", "left2right", "left3right"]
        test_plugins_params = {}
        test_shared_state = {}

        test_plugins_params["lint-func-indexer-param-left"] = "left"
        test_plugins_params["lint-func-indexer-param-right"] = "right"

        v, r = lint_func_indexer.lint_pre(test_plugins_params, test_file, test_shared_state, len(test_lines))
        self.assertTrue(v)
        self.assertEqual(r, None)

        expected_shared_state = {}
        expected_shared_state["lint-func-indexer-counter"] = 0

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintCycle1(self):

        test_file = "test_file.txt"
        test_lines = ["", "   ", ""]
        test_plugins_params = {}
        test_shared_state = {}

        test_plugins_params["lint-func-indexer-param-left"] = "left"
        test_plugins_params["lint-func-indexer-param-right"] = "right"

        test_shared_state["lint-func-indexer-counter"] = 0

        expected_shared_state1 = {}
        expected_shared_state1["lint-func-indexer-counter"] = 0

        expected_shared_state2 = {}
        expected_shared_state2["lint-func-indexer-counter"] = 0

        expected_shared_state3 = {}
        expected_shared_state3["lint-func-indexer-counter"] = 0

        expected_shared_states = [expected_shared_state1, expected_shared_state2, expected_shared_state3]

        for test_index in [1, 2, 3]:

            v, r = lint_func_indexer.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index, test_lines[test_index-1])
            self.assertTrue(v)
            self.assertEqual(r, None)

            self.assertEqual(test_shared_state, expected_shared_states[test_index-1])

    def testLintCycle2(self):

        test_file = "test_file.txt"
        test_lines = ["left1right", "left2right", "left3right"]
        test_plugins_params = {}
        test_shared_state = {}

        test_plugins_params["lint-func-indexer-param-left"] = "left"
        test_plugins_params["lint-func-indexer-param-right"] = "right"

        test_shared_state["lint-func-indexer-counter"] = 0

        expected_shared_state1 = {}
        expected_shared_state1["lint-func-indexer-counter"] = 1

        expected_shared_state2 = {}
        expected_shared_state2["lint-func-indexer-counter"] = 2

        expected_shared_state3 = {}
        expected_shared_state3["lint-func-indexer-counter"] = 3

        expected_shared_states = [expected_shared_state1, expected_shared_state2, expected_shared_state3]

        for test_index in [1, 2, 3]:

            v, r = lint_func_indexer.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index, test_lines[test_index-1])
            self.assertTrue(v)
            self.assertEqual(r, None)

            self.assertEqual(test_shared_state, expected_shared_states[test_index-1])

    def testLintPost1(self):

        test_file = "test_file.txt"
        test_lines = ["left1right", "left2right", "left3right"]
        test_plugins_params = {}
        test_shared_state = {}

        test_plugins_params["lint-func-indexer-param-left"] = "left"
        test_plugins_params["lint-func-indexer-param-right"] = "right"

        test_shared_state["lint-func-indexer-counter"] = 0

        v, r = lint_func_indexer.lint_post(test_plugins_params, test_file, test_shared_state)
        self.assertTrue(v)
        self.assertEqual(r, None)

        expected_shared_state = {}
        expected_shared_state["lint-func-indexer-counter"] = 0

        self.assertEqual(test_shared_state, expected_shared_state)

    # mvtodo: def testLintComplete(self):

if __name__ == "__main__":
    unittest.main()
