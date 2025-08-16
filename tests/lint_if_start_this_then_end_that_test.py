#!/usr/bin/env python3

import sys
import os
import shutil
import unittest

import mvtools_test_fixture
import path_utils

import lint_if_start_this_then_end_that

class LintIfStartThisThenEndThatTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("lint_if_start_this_then_end_that_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testLintName(self):

        self.assertEqual(lint_if_start_this_then_end_that.lint_name(), "lint_if_start_this_then_end_that.py")

    def testLintDesc(self):

        self.assertEqual(lint_if_start_this_then_end_that.lint_desc(), "checks whether a given pattern, if/when found at the beginning of the source content, will have a corresponding specific given pattern at the end of the source content")

    def testLintPre1(self):

        test_file = "test_file.txt"
        test_lines = ["start end", "start stuff end", "stuff start end"]
        test_plugins_params = {}
        test_shared_state = {}

        test_plugins_params["lint-if-start-this-then-end-that-end-pattern"] = ["end"]

        v, r = lint_if_start_this_then_end_that.lint_pre(test_plugins_params, test_file, test_shared_state, len(test_lines))
        self.assertFalse(v)
        self.assertEqual(r, "required parameter {lint-if-start-this-then-end-that-start-pattern} was not provided")

    def testLintPre2(self):

        test_file = "test_file.txt"
        test_lines = ["start end", "start stuff end", "stuff start end"]
        test_plugins_params = {}
        test_shared_state = {}

        test_plugins_params["lint-if-start-this-then-end-that-start-pattern"] = ["start"]

        v, r = lint_if_start_this_then_end_that.lint_pre(test_plugins_params, test_file, test_shared_state, len(test_lines))
        self.assertFalse(v)
        self.assertEqual(r, "required parameter {lint-if-start-this-then-end-that-end-pattern} was not provided")

    def testLintPre3(self):

        test_file = "test_file.txt"
        test_lines = ["start end", "start stuff end", "stuff start end"]
        test_plugins_params = {}
        test_shared_state = {}

        test_plugins_params["lint-if-start-this-then-end-that-start-pattern"] = ["start", "another"]
        test_plugins_params["lint-if-start-this-then-end-that-end-pattern"] = ["end"]

        v, r = lint_if_start_this_then_end_that.lint_pre(test_plugins_params, test_file, test_shared_state, len(test_lines))
        self.assertFalse(v)
        self.assertEqual(r, "the parameter {lint-if-start-this-then-end-that-start-pattern} must contain one (and only) entry")

    def testLintPre4(self):

        test_file = "test_file.txt"
        test_lines = ["start end", "start stuff end", "stuff start end"]
        test_plugins_params = {}
        test_shared_state = {}

        test_plugins_params["lint-if-start-this-then-end-that-start-pattern"] = ["start"]
        test_plugins_params["lint-if-start-this-then-end-that-end-pattern"] = ["end", "another"]

        v, r = lint_if_start_this_then_end_that.lint_pre(test_plugins_params, test_file, test_shared_state, len(test_lines))
        self.assertFalse(v)
        self.assertEqual(r, "the parameter {lint-if-start-this-then-end-that-end-pattern} must contain one (and only) entry")

    def testLintPre5(self):

        test_file = "test_file.txt"
        test_lines = ["start end", "start stuff end", "stuff start end"]
        test_plugins_params = {}
        test_shared_state = {}

        test_plugins_params["lint-if-start-this-then-end-that-start-pattern"] = [""]
        test_plugins_params["lint-if-start-this-then-end-that-end-pattern"] = ["end"]

        v, r = lint_if_start_this_then_end_that.lint_pre(test_plugins_params, test_file, test_shared_state, len(test_lines))
        self.assertFalse(v)
        self.assertEqual(r, "the parameter {lint-if-start-this-then-end-that-start-pattern} cannot be empty")

    def testLintPre6(self):

        test_file = "test_file.txt"
        test_lines = ["start end", "start stuff end", "stuff start end"]
        test_plugins_params = {}
        test_shared_state = {}

        test_plugins_params["lint-if-start-this-then-end-that-start-pattern"] = ["start"]
        test_plugins_params["lint-if-start-this-then-end-that-end-pattern"] = [""]

        v, r = lint_if_start_this_then_end_that.lint_pre(test_plugins_params, test_file, test_shared_state, len(test_lines))
        self.assertFalse(v)
        self.assertEqual(r, "the parameter {lint-if-start-this-then-end-that-end-pattern} cannot be empty")

    def testLintPre7(self):

        test_file = "test_file.txt"
        test_lines = ["start end", "start stuff end", "stuff start end"]
        test_plugins_params = {}
        test_shared_state = {}

        test_plugins_params["lint-if-start-this-then-end-that-start-pattern"] = ["start"]
        test_plugins_params["lint-if-start-this-then-end-that-end-pattern"] = ["end"]

        v, r = lint_if_start_this_then_end_that.lint_pre(test_plugins_params, test_file, test_shared_state, len(test_lines))
        self.assertTrue(v)
        self.assertEqual(r, None)

        expected_shared_state = {}

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintCycle1(self):

        test_file = "test_file.txt"
        test_lines = ["start end", "start stuff end", "stuff start end", "none of either"]
        test_plugins_params = {}
        test_shared_state = {}

        test_plugins_params["lint-if-start-this-then-end-that-start-pattern"] = ["start"]
        test_plugins_params["lint-if-start-this-then-end-that-end-pattern"] = ["end"]

        expected_shared_state1 = {}
        expected_shared_state2 = {}
        expected_shared_state3 = {}
        expected_shared_state4 = {}

        expected_shared_states = [expected_shared_state1, expected_shared_state2, expected_shared_state3, expected_shared_state4]

        expected_result1 = None
        expected_result2 = None
        expected_result3 = None
        expected_result4 = None

        expected_results = [expected_result1, expected_result2, expected_result3, expected_result4]

        for test_index in range(len(test_lines)):

            v, r = lint_if_start_this_then_end_that.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, expected_results[test_index])

            self.assertEqual(test_shared_state, expected_shared_states[test_index])

    def testLintCycle2(self):

        test_file = "test_file.txt"
        test_lines = ["start other", "start stuff end", "stuff start end"]
        test_plugins_params = {}
        test_shared_state = {}

        test_plugins_params["lint-if-start-this-then-end-that-start-pattern"] = ["start"]
        test_plugins_params["lint-if-start-this-then-end-that-end-pattern"] = ["end"]

        expected_shared_state1 = {}
        expected_shared_state2 = {}
        expected_shared_state3 = {}

        expected_shared_states = [expected_shared_state1, expected_shared_state2, expected_shared_state3]

        expected_result1 = ("[test_file.txt:1]: line [start other] has the pattern [start] in the beginning - but not the pattern [end] at the end.", [])
        expected_result2 = None
        expected_result3 = None

        expected_results = [expected_result1, expected_result2, expected_result3]

        for test_index in range(len(test_lines)):

            v, r = lint_if_start_this_then_end_that.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, expected_results[test_index])

            self.assertEqual(test_shared_state, expected_shared_states[test_index])

    def testLintPost1(self):

        test_file = "test_file.txt"
        test_lines = ["start end", "start stuff end", "stuff start end"]
        test_plugins_params = {}
        test_shared_state = {}

        test_plugins_params["lint-if-start-this-then-end-that-start-pattern"] = ["start"]
        test_plugins_params["lint-if-start-this-then-end-that-end-pattern"] = ["end"]

        v, r = lint_if_start_this_then_end_that.lint_post(test_plugins_params, test_file, test_shared_state)
        self.assertTrue(v)
        self.assertEqual(r, None)

        expected_shared_state = {}

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintComplete(self):

        test_file = "test_file.txt"
        test_lines = ["start other", "start stuff end", "stuff start end"]
        test_plugins_params = {}
        test_shared_state = {}

        test_plugins_params["lint-if-start-this-then-end-that-start-pattern"] = ["start"]
        test_plugins_params["lint-if-start-this-then-end-that-end-pattern"] = ["end"]

        expected_shared_state1 = {}
        expected_shared_state2 = {}
        expected_shared_state3 = {}

        expected_shared_states = [expected_shared_state1, expected_shared_state2, expected_shared_state3]

        expected_result1 = ("[test_file.txt:1]: line [start other] has the pattern [start] in the beginning - but not the pattern [end] at the end.", [])
        expected_result2 = None
        expected_result3 = None

        expected_results = [expected_result1, expected_result2, expected_result3]

        v, r = lint_if_start_this_then_end_that.lint_pre(test_plugins_params, test_file, test_shared_state, len(test_lines))
        self.assertTrue(v)
        self.assertEqual(r, None)

        for test_index in range(len(test_lines)):

            v, r = lint_if_start_this_then_end_that.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, expected_results[test_index])

            self.assertEqual(test_shared_state, expected_shared_states[test_index])

        v, r = lint_if_start_this_then_end_that.lint_post(test_plugins_params, test_file, test_shared_state)
        self.assertTrue(v)
        self.assertEqual(r, None)

if __name__ == "__main__":
    unittest.main()
