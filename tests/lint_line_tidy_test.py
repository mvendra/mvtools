#!/usr/bin/env python

import sys
import os
import shutil
import unittest

import mvtools_test_fixture
import path_utils

import lint_line_tidy

class LintLineTidyTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("lint_line_tidy_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testLintName(self):

        self.assertEqual(lint_line_tidy.lint_name(), "lint_line_tidy.py")

    def testLintDesc(self):

        self.assertEqual(lint_line_tidy.lint_desc(), "detects trailing spaces")

    def testLintPre1(self):

        test_file = "test_file.txt"
        test_lines = ["first", "second", "third"]
        test_plugins_params = {}
        test_shared_state = {}

        expected_shared_state = {}

        v, r = lint_line_tidy.lint_pre(test_plugins_params, test_file, test_shared_state, len(test_lines))
        self.assertTrue(v)
        self.assertEqual(r, None)

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintCycle1(self):

        test_file = "test_file.txt"
        test_lines = ["first", "    second", "third"]
        test_plugins_params = {}
        test_shared_state = {}

        expected_result1 = None
        expected_result2 = None
        expected_result3 = None

        expected_results = [expected_result1, expected_result2, expected_result3]

        for test_index in range(len(test_lines)):

            v, r = lint_line_tidy.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, expected_results[test_index])

    def testLintCycle2(self):

        test_file = "test_file.txt"
        test_lines = ["first   ", "second", "third "]
        test_plugins_params = {}
        test_shared_state = {}

        expected_result1 = ("[test_file.txt:1]: trailing spaces detected.", [(1, "first")])
        expected_result2 = None
        expected_result3 = ("[test_file.txt:3]: trailing spaces detected.", [(3, "third")])

        expected_results = [expected_result1, expected_result2, expected_result3]

        for test_index in range(len(test_lines)):

            v, r = lint_line_tidy.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, expected_results[test_index])

    def testLintCycle3(self):

        test_file = "test_file.txt"
        test_lines = ["    first    ", "        second        ", "third  "]
        test_plugins_params = {}
        test_shared_state = {}

        expected_result1 = ("[test_file.txt:1]: trailing spaces detected.", [(1, "    first")])
        expected_result2 = ("[test_file.txt:2]: trailing spaces detected.", [(2, "        second")])
        expected_result3 = ("[test_file.txt:3]: trailing spaces detected.", [(3, "third")])

        expected_results = [expected_result1, expected_result2, expected_result3]

        for test_index in range(len(test_lines)):

            v, r = lint_line_tidy.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, expected_results[test_index])

    def testLintCycle4(self):

        test_file = "test_file.txt"
        test_lines = ["  first", "   second", "     third", "      fourth", "       fifth", "         sixth"]
        test_plugins_params = {}
        test_shared_state = {}

        expected_result1 = ("[test_file.txt:1]: bad indentation detected.", [])
        expected_result2 = ("[test_file.txt:2]: bad indentation detected.", [])
        expected_result3 = ("[test_file.txt:3]: bad indentation detected.", [])
        expected_result4 = ("[test_file.txt:4]: bad indentation detected.", [])
        expected_result5 = ("[test_file.txt:5]: bad indentation detected.", [])
        expected_result6 = ("[test_file.txt:6]: bad indentation detected.", [])

        expected_results = [expected_result1, expected_result2, expected_result3, expected_result4, expected_result5, expected_result6]

        for test_index in range(len(test_lines)):

            v, r = lint_line_tidy.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, expected_results[test_index])

    def testLintCycle5(self):

        test_file = "test_file.txt"
        test_lines = ["  first   ", "   second", "     third ", "      fourth", "       fifth    ", "         sixth"]
        test_plugins_params = {}
        test_shared_state = {}

        expected_result1 = ("[test_file.txt:1]: bad indentation detected. trailing spaces detected.", [(1, "  first")])
        expected_result2 = ("[test_file.txt:2]: bad indentation detected.", [])
        expected_result3 = ("[test_file.txt:3]: bad indentation detected. trailing spaces detected.", [(3, "     third")])
        expected_result4 = ("[test_file.txt:4]: bad indentation detected.", [])
        expected_result5 = ("[test_file.txt:5]: bad indentation detected. trailing spaces detected.", [(5, "       fifth")])
        expected_result6 = ("[test_file.txt:6]: bad indentation detected.", [])

        expected_results = [expected_result1, expected_result2, expected_result3, expected_result4, expected_result5, expected_result6]

        for test_index in range(len(test_lines)):

            v, r = lint_line_tidy.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, expected_results[test_index])

    def testLintPost1(self):

        test_file = "test_file.txt"
        test_lines = ["first", "second", "third"]
        test_plugins_params = {}
        test_shared_state = {}

        v, r = lint_line_tidy.lint_post(test_plugins_params, test_file, test_shared_state)
        self.assertTrue(v)
        self.assertEqual(r, None)

    def testLintComplete(self):

        test_file = "test_file.txt"
        test_lines = ["    first    ", "        second        ", "third  ", " fourth", "fifth", "   sixth  "]
        test_plugins_params = {}
        test_shared_state = {}

        expected_shared_state = {}

        expected_result1 = ("[test_file.txt:1]: trailing spaces detected.", [(1, "    first")])
        expected_result2 = ("[test_file.txt:2]: trailing spaces detected.", [(2, "        second")])
        expected_result3 = ("[test_file.txt:3]: trailing spaces detected.", [(3, "third")])
        expected_result4 = ("[test_file.txt:4]: bad indentation detected.", [])
        expected_result5 = None
        expected_result6 = ("[test_file.txt:6]: bad indentation detected. trailing spaces detected.", [(6, "   sixth")])

        expected_results = [expected_result1, expected_result2, expected_result3, expected_result4, expected_result5, expected_result6]

        v, r = lint_line_tidy.lint_pre(test_plugins_params, test_file, test_shared_state, len(test_lines))
        self.assertTrue(v)
        self.assertEqual(r, None)

        for test_index in range(len(test_lines)):

            v, r = lint_line_tidy.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, expected_results[test_index])

        v, r = lint_line_tidy.lint_post(test_plugins_params, test_file, test_shared_state)
        self.assertTrue(v)
        self.assertEqual(r, None)

        self.assertEqual(test_shared_state, expected_shared_state)

if __name__ == "__main__":
    unittest.main()
