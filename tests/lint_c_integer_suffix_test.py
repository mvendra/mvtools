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

        for test_index in range(len(test_lines)):

            v, r = lint_c_integer_suffix.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, expected_results[test_index])

    def testLintCycle2(self):

        test_file = "test_file.txt"
        test_lines = ["123", "010", "0xab", "0XDF", "0b10101", "0B10101", "0.0"]
        test_plugins_params = {}
        test_shared_state = {}

        expected_result1 = None
        expected_result2 = None
        expected_result3 = None
        expected_result4 = None
        expected_result5 = None
        expected_result6 = None
        expected_result7 = None

        expected_results = [expected_result1, expected_result2, expected_result3, expected_result4, expected_result5, expected_result6, expected_result7]

        for test_index in range(len(test_lines)):

            v, r = lint_c_integer_suffix.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, expected_results[test_index])

    def testLintCycle3(self):

        test_file = "test_file.txt"
        test_lines = ["123U", "010U", "0xabU", "0XDFU", "0b10101U", "0B10101U", "0.0F"]
        test_plugins_params = {}
        test_shared_state = {}

        expected_result1 = ("line [1] has [1] integer suffix violations", [(1, "123")])
        expected_result2 = ("line [2] has [1] integer suffix violations", [(2, "010")])
        expected_result3 = ("line [3] has [1] integer suffix violations", [(3, "0xab")])
        expected_result4 = ("line [4] has [1] integer suffix violations", [(4, "0XDF")])
        expected_result5 = ("line [5] has [1] integer suffix violations", [(5, "0b10101")])
        expected_result6 = ("line [6] has [1] integer suffix violations", [(6, "0B10101")])
        expected_result7 = ("line [7] has [1] integer suffix violations", [(7, "0.0")])

        expected_results = [expected_result1, expected_result2, expected_result3, expected_result4, expected_result5, expected_result6, expected_result7]

        for test_index in range(len(test_lines)):

            v, r = lint_c_integer_suffix.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, expected_results[test_index])

    def testLintCycle4(self):

        test_file = "test_file.txt"
        test_lines = ["123U;", "010U;", "0xabU;", "0XDFU;", "0b10101U;", "0B10101U;", "0.0F;"]
        test_plugins_params = {}
        test_shared_state = {}

        expected_result1 = ("line [1] has [1] integer suffix violations", [(1, "123;")])
        expected_result2 = ("line [2] has [1] integer suffix violations", [(2, "010;")])
        expected_result3 = ("line [3] has [1] integer suffix violations", [(3, "0xab;")])
        expected_result4 = ("line [4] has [1] integer suffix violations", [(4, "0XDF;")])
        expected_result5 = ("line [5] has [1] integer suffix violations", [(5, "0b10101;")])
        expected_result6 = ("line [6] has [1] integer suffix violations", [(6, "0B10101;")])
        expected_result7 = ("line [7] has [1] integer suffix violations", [(7, "0.0;")])

        expected_results = [expected_result1, expected_result2, expected_result3, expected_result4, expected_result5, expected_result6, expected_result7]

        for test_index in range(len(test_lines)):

            v, r = lint_c_integer_suffix.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, expected_results[test_index])

    def testLintCycle5(self):

        test_file = "test_file.txt"
        test_lines = ["    123LL", "    010LL", "    0xabLL", "    0XDFLL", "    0b10101LL", "    0B10101LL", "    0.0F"]
        test_plugins_params = {}
        test_shared_state = {}

        expected_result1 = ("line [1] has [1] integer suffix violations", [(1, "    123")])
        expected_result2 = ("line [2] has [1] integer suffix violations", [(2, "    010")])
        expected_result3 = ("line [3] has [1] integer suffix violations", [(3, "    0xab")])
        expected_result4 = ("line [4] has [1] integer suffix violations", [(4, "    0XDF")])
        expected_result5 = ("line [5] has [1] integer suffix violations", [(5, "    0b10101")])
        expected_result6 = ("line [6] has [1] integer suffix violations", [(6, "    0B10101")])
        expected_result7 = ("line [7] has [1] integer suffix violations", [(7, "    0.0")])

        expected_results = [expected_result1, expected_result2, expected_result3, expected_result4, expected_result5, expected_result6, expected_result7]

        for test_index in range(len(test_lines)):

            v, r = lint_c_integer_suffix.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, expected_results[test_index])

    def testLintCycle6(self):

        test_file = "test_file.txt"
        test_lines = ["    123LL;321ULL    ", "    010LL 111ULL", "    0xabLL;0xccULL    0xddULL", "    0XDFLL    0XFDLL;", "    0b10101Ll", "    0B10101LL;;  8l", "    0..F", "    0.F   ", "    .F   "]
        test_plugins_params = {}
        test_shared_state = {}

        expected_result1 = ("line [1] has [2] integer suffix violations", [(1, "    123;321    ")])
        expected_result2 = ("line [2] has [2] integer suffix violations", [(2, "    010 111")])
        expected_result3 = ("line [3] has [3] integer suffix violations", [(3, "    0xab;0xcc    0xdd")])
        expected_result4 = ("line [4] has [2] integer suffix violations", [(4, "    0XDF    0XFD;")])
        expected_result5 = ("line [5] has [1] integer suffix violations", [(5, "    0b10101")])
        expected_result6 = ("line [6] has [2] integer suffix violations", [(6, "    0B10101;;  8")])
        expected_result7 = None
        expected_result8 = None
        expected_result9 = None

        expected_results = [expected_result1, expected_result2, expected_result3, expected_result4, expected_result5, expected_result6, expected_result7, expected_result8, expected_result9]

        for test_index in range(len(test_lines)):

            v, r = lint_c_integer_suffix.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, expected_results[test_index])

    def testLintCycle7(self):

        test_file = "test_file.txt"
        test_lines = ["123", "010", "0xab", "0XDF", "0b10101", "0B10101", "0.0"]
        test_plugins_params = {}
        test_shared_state = {}

        test_plugins_params["lint-c-integer-suffix-warn-no-suffix"] = "yes"

        expected_result1 = ("line [1] has [1] integer suffix violations", [])
        expected_result2 = ("line [2] has [1] integer suffix violations", [])
        expected_result3 = ("line [3] has [1] integer suffix violations", [])
        expected_result4 = ("line [4] has [1] integer suffix violations", [])
        expected_result5 = ("line [5] has [1] integer suffix violations", [])
        expected_result6 = ("line [6] has [1] integer suffix violations", [])
        expected_result7 = ("line [7] has [1] integer suffix violations", [])

        expected_results = [expected_result1, expected_result2, expected_result3, expected_result4, expected_result5, expected_result6, expected_result7]

        for test_index in range(len(test_lines)):

            v, r = lint_c_integer_suffix.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, expected_results[test_index])

    def testLintCycle8(self):

        test_file = "test_file.txt"
        test_lines = ["123 123U;", " 50LF  010", "0xab  0x11L ", "0XDF  ;   0XAAl ;  ", "  0b111ul 0b10101  ", " 0B10101 ;  0B101U", "0.0 0.0F "]
        test_plugins_params = {}
        test_shared_state = {}

        test_plugins_params["lint-c-integer-suffix-warn-no-suffix"] = "yes"

        expected_result1 = ("line [1] has [2] integer suffix violations", [(1, "123 123;")])
        expected_result2 = ("line [2] has [2] integer suffix violations", [(2, " 50  010")])
        expected_result3 = ("line [3] has [2] integer suffix violations", [(3, "0xab  0x11 ")])
        expected_result4 = ("line [4] has [2] integer suffix violations", [(4, "0XDF  ;   0XAA ;  ")])
        expected_result5 = ("line [5] has [2] integer suffix violations", [(5, "  0b111 0b10101  ")])
        expected_result6 = ("line [6] has [2] integer suffix violations", [(6, " 0B10101 ;  0B101")])
        expected_result7 = ("line [7] has [2] integer suffix violations", [(7, "0.0 0.0 ")])

        expected_results = [expected_result1, expected_result2, expected_result3, expected_result4, expected_result5, expected_result6, expected_result7]

        for test_index in range(len(test_lines)):

            v, r = lint_c_integer_suffix.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, expected_results[test_index])

    def testLintPost1(self):

        test_file = "test_file.txt"
        test_lines = ["first", "second", "third"]
        test_plugins_params = {}
        test_shared_state = {}

        v, r = lint_c_integer_suffix.lint_post(test_plugins_params, test_file, test_shared_state)
        self.assertTrue(v)
        self.assertEqual(r, None)

    def testLintComplete(self):

        test_file = "test_file.txt"
        test_lines = ["123U", "010U", "0xabU", "0XDFU", "0b10101U", "0B10101U", "0.0F"]
        test_plugins_params = {}
        test_shared_state = {}

        expected_result1 = ("line [1] has [1] integer suffix violations", [(1, "123")])
        expected_result2 = ("line [2] has [1] integer suffix violations", [(2, "010")])
        expected_result3 = ("line [3] has [1] integer suffix violations", [(3, "0xab")])
        expected_result4 = ("line [4] has [1] integer suffix violations", [(4, "0XDF")])
        expected_result5 = ("line [5] has [1] integer suffix violations", [(5, "0b10101")])
        expected_result6 = ("line [6] has [1] integer suffix violations", [(6, "0B10101")])
        expected_result7 = ("line [7] has [1] integer suffix violations", [(7, "0.0")])

        expected_results = [expected_result1, expected_result2, expected_result3, expected_result4, expected_result5, expected_result6, expected_result7]

        v, r = lint_c_integer_suffix.lint_pre(test_plugins_params, test_file, test_shared_state, len(test_lines))
        self.assertTrue(v)
        self.assertEqual(r, None)

        for test_index in range(len(test_lines)):

            v, r = lint_c_integer_suffix.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, expected_results[test_index])

        v, r = lint_c_integer_suffix.lint_post(test_plugins_params, test_file, test_shared_state)
        self.assertTrue(v)
        self.assertEqual(r, None)

if __name__ == "__main__":
    unittest.main()
