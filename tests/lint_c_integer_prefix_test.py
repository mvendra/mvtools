#!/usr/bin/env python

import sys
import os
import shutil
import unittest

import mvtools_test_fixture
import path_utils

import lint_c_integer_prefix

class LintCIntegerPrefixTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("lint_c_integer_prefix_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testLintName(self):

        self.assertEqual(lint_c_integer_prefix.lint_name(), "lint_c_integer_prefix.py")

    def testLintDesc(self):

        self.assertEqual(lint_c_integer_prefix.lint_desc(), "checks C source files for proper integer constant prefix usage")

    def testLintPre1(self):

        test_file = "test_file.txt"
        test_lines = ["first", "second", "third"]
        test_plugins_params = {}
        test_shared_state = {}

        test_shared_state["lint-c-integer-prefix-internal-slash-asterisk-state"] = False

        v, r = lint_c_integer_prefix.lint_pre(test_plugins_params, test_file, test_shared_state, len(test_lines))
        self.assertFalse(v)
        self.assertEqual(r, "shared state already contains {lint-c-integer-prefix-internal-slash-asterisk-state}")

    def testLintPre2(self):

        test_file = "test_file.txt"
        test_lines = ["first", "second", "third"]
        test_plugins_params = {}
        test_shared_state = {}

        expected_shared_state = {}
        expected_shared_state["lint-c-integer-prefix-internal-slash-asterisk-state"] = False

        v, r = lint_c_integer_prefix.lint_pre(test_plugins_params, test_file, test_shared_state, len(test_lines))
        self.assertTrue(v)
        self.assertEqual(r, None)

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintCycle1(self):

        test_file = "test_file.txt"
        test_lines = ["first", "second", "third"]
        test_plugins_params = {}
        test_shared_state = {}

        test_shared_state["lint-c-integer-prefix-internal-slash-asterisk-state"] = False

        expected_shared_state = {}
        expected_shared_state["lint-c-integer-prefix-internal-slash-asterisk-state"] = False

        expected_result1 = None
        expected_result2 = None
        expected_result3 = None

        expected_results = [expected_result1, expected_result2, expected_result3]

        for test_index in range(len(test_lines)):

            v, r = lint_c_integer_prefix.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, expected_results[test_index])

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintCycle2(self):

        test_file = "test_file.txt"
        test_lines = ["123", "010", "0xab", "0XDF", "0b10101", "0B10101", "0.0"]
        test_plugins_params = {}
        test_shared_state = {}

        test_shared_state["lint-c-integer-prefix-internal-slash-asterisk-state"] = False

        expected_shared_state = {}
        expected_shared_state["lint-c-integer-prefix-internal-slash-asterisk-state"] = False

        expected_result1 = None
        expected_result2 = None
        expected_result3 = None
        expected_result4 = ("[test_file.txt:4] has [1] integer prefix violation.", [(4, "0xDF")])
        expected_result5 = None
        expected_result6 = ("[test_file.txt:6] has [1] integer prefix violation.", [(6, "0b10101")])
        expected_result7 = None

        expected_results = [expected_result1, expected_result2, expected_result3, expected_result4, expected_result5, expected_result6, expected_result7]

        for test_index in range(len(test_lines)):

            v, r = lint_c_integer_prefix.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, expected_results[test_index])

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintCycle3(self):

        test_file = "test_file.txt"
        test_lines = ["123;321", "010;1001", "0xab;0xba", "0XDF;0xaa;0Xbb", "0b10101;0B101", "0B10101;0B111", "0.0;0.02aX"]
        test_plugins_params = {}
        test_shared_state = {}

        test_shared_state["lint-c-integer-prefix-internal-slash-asterisk-state"] = False

        expected_shared_state = {}
        expected_shared_state["lint-c-integer-prefix-internal-slash-asterisk-state"] = False

        expected_result1 = None
        expected_result2 = None
        expected_result3 = None
        expected_result4 = ("[test_file.txt:4] has [2] integer prefix violations.", [(4, "0xDF;0xaa;0xbb")])
        expected_result5 = ("[test_file.txt:5] has [1] integer prefix violation.", [(5, "0b10101;0b101")])
        expected_result6 = ("[test_file.txt:6] has [2] integer prefix violations.", [(6, "0b10101;0b111")])
        expected_result7 = None

        expected_results = [expected_result1, expected_result2, expected_result3, expected_result4, expected_result5, expected_result6, expected_result7]

        for test_index in range(len(test_lines)):

            v, r = lint_c_integer_prefix.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, expected_results[test_index])

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintCycle4(self):

        test_file = "test_file.txt"
        test_lines = ["//0Xaa", "/*0Xaa*/", "\"0Xaa\"", "var0Xaa", "\'0Xaa\'", "0X", "Xaa"]
        test_plugins_params = {}
        test_shared_state = {}

        test_shared_state["lint-c-integer-prefix-internal-slash-asterisk-state"] = False

        expected_shared_state = {}
        expected_shared_state["lint-c-integer-prefix-internal-slash-asterisk-state"] = False

        expected_result1 = None
        expected_result2 = None
        expected_result3 = None
        expected_result4 = None
        expected_result5 = None
        expected_result6 = ("[test_file.txt:6] has [1] integer prefix violation.", [(6, "0x")])
        expected_result7 = None

        expected_results = [expected_result1, expected_result2, expected_result3, expected_result4, expected_result5, expected_result6, expected_result7]

        for test_index in range(len(test_lines)):

            v, r = lint_c_integer_prefix.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, expected_results[test_index])

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintCycle5(self):

        test_file = "test_file.txt"
        test_lines = ["/**", "*", "0Xaa", "**/", "0Xa"]
        test_plugins_params = {}
        test_shared_state = {}

        test_shared_state["lint-c-integer-prefix-internal-slash-asterisk-state"] = False

        expected_shared_state = {}
        expected_shared_state["lint-c-integer-prefix-internal-slash-asterisk-state"] = False

        expected_result1 = None
        expected_result2 = None
        expected_result3 = None
        expected_result4 = None
        expected_result5 = ("[test_file.txt:5] has [1] integer prefix violation.", [(5, "0xa")])

        expected_results = [expected_result1, expected_result2, expected_result3, expected_result4, expected_result5]

        for test_index in range(len(test_lines)):

            v, r = lint_c_integer_prefix.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, expected_results[test_index])

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintCycle6(self):

        test_file = "test_file.txt"
        test_lines = ["0XX", "0BB", "0XB", "0BX"]
        test_plugins_params = {}
        test_shared_state = {}

        test_shared_state["lint-c-integer-prefix-internal-slash-asterisk-state"] = False

        expected_shared_state = {}
        expected_shared_state["lint-c-integer-prefix-internal-slash-asterisk-state"] = False

        expected_result1 = ("[test_file.txt:1] has [1] integer prefix violation.", [(1, "0xX")])
        expected_result2 = ("[test_file.txt:2] has [1] integer prefix violation.", [(2, "0bB")])
        expected_result3 = ("[test_file.txt:3] has [1] integer prefix violation.", [(3, "0xB")])
        expected_result4 = ("[test_file.txt:4] has [1] integer prefix violation.", [(4, "0bX")])

        expected_results = [expected_result1, expected_result2, expected_result3, expected_result4]

        for test_index in range(len(test_lines)):

            v, r = lint_c_integer_prefix.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, expected_results[test_index])

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintPost1(self):

        test_file = "test_file.txt"
        test_lines = ["first", "second", "third"]
        test_plugins_params = {}
        test_shared_state = {}

        v, r = lint_c_integer_prefix.lint_post(test_plugins_params, test_file, test_shared_state)
        self.assertTrue(v)
        self.assertEqual(r, None)

    def testLintComplete(self):

        test_file = "test_file.txt"
        test_lines = ["0X123", "0B101", "0x123", "0b101", "X123", "B123"]
        test_plugins_params = {}
        test_shared_state = {}

        expected_shared_state = {}
        expected_shared_state["lint-c-integer-prefix-internal-slash-asterisk-state"] = False

        expected_result1 = ("[test_file.txt:1] has [1] integer prefix violation.", [(1, "0x123")])
        expected_result2 = ("[test_file.txt:2] has [1] integer prefix violation.", [(2, "0b101")])
        expected_result3 = None
        expected_result4 = None
        expected_result5 = None
        expected_result6 = None

        expected_results = [expected_result1, expected_result2, expected_result3, expected_result4, expected_result5, expected_result6]

        v, r = lint_c_integer_prefix.lint_pre(test_plugins_params, test_file, test_shared_state, len(test_lines))
        self.assertTrue(v)
        self.assertEqual(r, None)

        for test_index in range(len(test_lines)):

            v, r = lint_c_integer_prefix.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, expected_results[test_index])

        v, r = lint_c_integer_prefix.lint_post(test_plugins_params, test_file, test_shared_state)
        self.assertTrue(v)
        self.assertEqual(r, None)

        self.assertEqual(test_shared_state, expected_shared_state)

if __name__ == "__main__":
    unittest.main()
