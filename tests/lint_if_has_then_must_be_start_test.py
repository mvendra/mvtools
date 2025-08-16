#!/usr/bin/env python3

import sys
import os
import shutil
import unittest

import mvtools_test_fixture
import path_utils

import lint_if_has_then_must_be_start

class LintIfHasThenMustBeStartTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("lint_if_has_then_must_be_start_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testLintName(self):

        self.assertEqual(lint_if_has_then_must_be_start.lint_name(), "lint_if_has_then_must_be_start.py")

    def testLintDesc(self):

        self.assertEqual(lint_if_has_then_must_be_start.lint_desc(), "checks whether the given patterns, if/when found, are found at the beginning of the source content")

    def testLintPre1(self):

        test_file = "test_file.txt"
        test_lines = ["some pattern", "something else", "some other thing"]
        test_plugins_params = {}
        test_shared_state = {}

        v, r = lint_if_has_then_must_be_start.lint_pre(test_plugins_params, test_file, test_shared_state, len(test_lines))
        self.assertFalse(v)
        self.assertEqual(r, "required parameter {lint-if-has-then-must-be-start-pattern} was not provided")

    def testLintPre2(self):

        test_file = "test_file.txt"
        test_lines = ["some pattern", "something else", "some other thing"]
        test_plugins_params = {}
        test_shared_state = {}

        test_plugins_params["lint-if-has-then-must-be-start-pattern"] = [""]

        v, r = lint_if_has_then_must_be_start.lint_pre(test_plugins_params, test_file, test_shared_state, len(test_lines))
        self.assertFalse(v)
        self.assertEqual(r, "parameters from {lint-if-has-then-must-be-start-pattern} cannot be empty")

    def testLintPre3(self):

        test_file = "test_file.txt"
        test_lines = ["some pattern", "something else", "some other thing"]
        test_plugins_params = {}
        test_shared_state = {}

        test_plugins_params["lint-if-has-then-must-be-start-pattern"] = ["some"]

        v, r = lint_if_has_then_must_be_start.lint_pre(test_plugins_params, test_file, test_shared_state, len(test_lines))
        self.assertTrue(v)
        self.assertEqual(r, None)

        expected_shared_state = {}

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintCycle1(self):

        test_file = "test_file.txt"
        test_lines = ["some pattern", "something else", "some other thing"]
        test_plugins_params = {}
        test_shared_state = {}

        test_plugins_params["lint-if-has-then-must-be-start-pattern"] = ["some"]

        expected_shared_state1 = {}
        expected_shared_state2 = {}
        expected_shared_state3 = {}

        expected_shared_states = [expected_shared_state1, expected_shared_state2, expected_shared_state3]

        expected_result1 = None
        expected_result2 = None
        expected_result3 = None

        expected_results = [expected_result1, expected_result2, expected_result3]

        for test_index in range(len(test_lines)):

            v, r = lint_if_has_then_must_be_start.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, expected_results[test_index])

            self.assertEqual(test_shared_state, expected_shared_states[test_index])

    def testLintCycle2(self):

        test_file = "test_file.txt"
        test_lines = ["some pattern", "else something", "some other thing"]
        test_plugins_params = {}
        test_shared_state = {}

        test_plugins_params["lint-if-has-then-must-be-start-pattern"] = ["some"]

        expected_shared_state1 = {}
        expected_shared_state2 = {}
        expected_shared_state3 = {}

        expected_shared_states = [expected_shared_state1, expected_shared_state2, expected_shared_state3]

        expected_result1 = None
        expected_result2 = ("[test_file.txt:2]: line [else something] has the pattern [some] - but not at the beginning.", [])
        expected_result3 = None

        expected_results = [expected_result1, expected_result2, expected_result3]

        for test_index in range(len(test_lines)):

            v, r = lint_if_has_then_must_be_start.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, expected_results[test_index])

            self.assertEqual(test_shared_state, expected_shared_states[test_index])

    def testLintCycle3(self):

        test_file = "test_file.txt"
        test_lines = ["some pattern", "else something", "some other thing", "other contents dissimilar and etc"]
        test_plugins_params = {}
        test_shared_state = {}

        test_plugins_params["lint-if-has-then-must-be-start-pattern"] = ["some", "etc"]

        expected_shared_state1 = {}
        expected_shared_state2 = {}
        expected_shared_state3 = {}
        expected_shared_state4 = {}

        expected_shared_states = [expected_shared_state1, expected_shared_state2, expected_shared_state3, expected_shared_state4]

        expected_result1 = None
        expected_result2 = ("[test_file.txt:2]: line [else something] has the pattern [some] - but not at the beginning.", [])
        expected_result3 = None
        expected_result4 = ("[test_file.txt:4]: line [other contents dissimilar and etc] has the pattern [etc] - but not at the beginning.", [])

        expected_results = [expected_result1, expected_result2, expected_result3, expected_result4]

        for test_index in range(len(test_lines)):

            v, r = lint_if_has_then_must_be_start.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, expected_results[test_index])

            self.assertEqual(test_shared_state, expected_shared_states[test_index])

    def testLintPost1(self):

        test_file = "test_file.txt"
        test_lines = ["some pattern", "something else", "some other thing"]
        test_plugins_params = {}
        test_shared_state = {}

        test_plugins_params["lint-if-has-then-must-be-start-pattern"] = ["some"]

        v, r = lint_if_has_then_must_be_start.lint_post(test_plugins_params, test_file, test_shared_state)
        self.assertTrue(v)
        self.assertEqual(r, None)

        expected_shared_state = {}

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintComplete(self):

        test_file = "test_file.txt"
        test_lines = ["some pattern", "else something", "some other thing", "other contents dissimilar and etc"]
        test_plugins_params = {}
        test_shared_state = {}

        test_plugins_params["lint-if-has-then-must-be-start-pattern"] = ["some", "etc"]

        expected_shared_state1 = {}
        expected_shared_state2 = {}
        expected_shared_state3 = {}
        expected_shared_state4 = {}

        expected_shared_states = [expected_shared_state1, expected_shared_state2, expected_shared_state3, expected_shared_state4]

        expected_result1 = None
        expected_result2 = ("[test_file.txt:2]: line [else something] has the pattern [some] - but not at the beginning.", [])
        expected_result3 = None
        expected_result4 = ("[test_file.txt:4]: line [other contents dissimilar and etc] has the pattern [etc] - but not at the beginning.", [])

        expected_results = [expected_result1, expected_result2, expected_result3, expected_result4]

        v, r = lint_if_has_then_must_be_start.lint_pre(test_plugins_params, test_file, test_shared_state, len(test_lines))
        self.assertTrue(v)
        self.assertEqual(r, None)

        for test_index in range(len(test_lines)):

            v, r = lint_if_has_then_must_be_start.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, expected_results[test_index])

            self.assertEqual(test_shared_state, expected_shared_states[test_index])

        v, r = lint_if_has_then_must_be_start.lint_post(test_plugins_params, test_file, test_shared_state)
        self.assertTrue(v)
        self.assertEqual(r, None)

if __name__ == "__main__":
    unittest.main()
