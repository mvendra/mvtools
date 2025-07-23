#!/usr/bin/env python3

import sys
import os
import shutil
import unittest

import mvtools_test_fixture
import path_utils

import lint_c_integer_suffix

class LintCIntegerSuffixTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("lint_c_integer_suffix_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testScanLargestOf(self):

        self.assertEqual(lint_c_integer_suffix.scan_largest_of("", 0, ["a", "ab", "abc"]), 0)
        self.assertEqual(lint_c_integer_suffix.scan_largest_of("abc123def", 0, ["a", "ab", "abc"]), 3)
        self.assertEqual(lint_c_integer_suffix.scan_largest_of("abc123def", 1, ["a", "ab", "abc"]), 0)
        self.assertEqual(lint_c_integer_suffix.scan_largest_of("ab123abc", 0, ["a", "ab", "abc"]), 2)
        self.assertEqual(lint_c_integer_suffix.scan_largest_of("ababc", 0, ["a", "ab", "abc"]), 2)
        self.assertEqual(lint_c_integer_suffix.scan_largest_of("ababc", 1, ["a", "ab", "abc"]), 0)
        self.assertEqual(lint_c_integer_suffix.scan_largest_of("ababc", 2, ["a", "ab", "abc"]), 3)
        self.assertEqual(lint_c_integer_suffix.scan_largest_of("123ull", 0, ["ll", "f", "u", "ull"]), 0)
        self.assertEqual(lint_c_integer_suffix.scan_largest_of("123ull", 3, ["ll", "f", "u", "ull"]), 3)
        self.assertEqual(lint_c_integer_suffix.scan_largest_of("123ull; // some comment", 3, ["ll", "f", "u", "ull"]), 3)
        self.assertEqual(lint_c_integer_suffix.scan_largest_of("123u; // some comment", 3, ["ll", "f", "u", "ull"]), 1)
        self.assertEqual(lint_c_integer_suffix.scan_largest_of("123; 456ull // some comment", 3, ["ll", "f", "u", "ull"]), 0)

    def testLintName(self):

        self.assertEqual(lint_c_integer_suffix.lint_name(), "lint_c_integer_suffix.py")

    def testLintPre1(self):

        test_file = "test_file.txt"
        test_lines = ["first", "second", "third"]
        test_plugins_params = {}
        test_shared_state = {}

        v, r = lint_c_integer_suffix.lint_pre(test_plugins_params, test_file, test_shared_state, len(test_lines))
        self.assertTrue(v)
        self.assertEqual(r, None)

    def testLintCycle1(self):

        test_file = "test_file.txt"
        test_lines = ["first", "second", "third"]
        test_plugins_params = {}
        test_shared_state = {}

        expected_result1 = None
        expected_result2 = None
        expected_result3 = None

        expected_results = [expected_result1, expected_result2, expected_result3]

        for test_index in [1, 2, 3]:

            v, r = lint_c_integer_suffix.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index, test_lines[test_index-1])
            self.assertTrue(v)
            self.assertEqual(r, expected_results[test_index-1])

    def testLintCycle2(self):

        test_file = "test_file.txt"
        test_lines = ["123", "123U", "123llu"]
        test_plugins_params = {}
        test_shared_state = {}

        expected_result1 = None
        expected_result2 = ("line [2] has integer suffix violations", [(2, "123")])
        expected_result3 = None

        expected_results = [expected_result1, expected_result2, expected_result3]

        for test_index in [1, 2, 3]:

            print("\nmvdebug ut: [%s]" % test_index)

            v, r = lint_c_integer_suffix.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index, test_lines[test_index-1])
            self.assertTrue(v)
            self.assertEqual(r, expected_results[test_index-1])

    def testLintPost1(self):

        test_file = "test_file.txt"
        test_lines = ["first", "second", "third"]
        test_plugins_params = {}
        test_shared_state = {}

        v, r = lint_c_integer_suffix.lint_post(test_plugins_params, test_file, test_shared_state)
        self.assertTrue(v)
        self.assertEqual(r, None)

if __name__ == "__main__":
    unittest.main()
