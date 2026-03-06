#!/usr/bin/env python

import sys
import os
import shutil
import unittest

import mvtools_test_fixture
import path_utils

import lint_c_unsigned_integer_hex

class LintCUnsignedIntegerHexTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("lint_c_unsigned_integer_hex_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testLintName(self):

        self.assertEqual(lint_c_unsigned_integer_hex.lint_name(), "lint_c_unsigned_integer_hex.py")

    def testLintDesc(self):

        self.assertEqual(lint_c_unsigned_integer_hex.lint_desc(), "checks C source files for proper unsigned integer hexadecimal notation usage")

    def testLintPre1(self):

        test_file = "test_file.txt"
        test_lines = ["first", "second", "third"]
        test_plugins_params = {}
        test_shared_state = {}

        test_shared_state["lint-c-unsigned-integer-hex-internal-slash-asterisk-state"] = False

        v, r = lint_c_unsigned_integer_hex.lint_pre(test_plugins_params, test_file, test_shared_state, len(test_lines))
        self.assertFalse(v)
        self.assertEqual(r, "shared state already contains {lint-c-unsigned-integer-hex-internal-slash-asterisk-state}")

    def testLintPre2(self):

        test_file = "test_file.txt"
        test_lines = ["first", "second", "third"]
        test_plugins_params = {}
        test_shared_state = {}

        expected_shared_state = {}
        expected_shared_state["lint-c-unsigned-integer-hex-internal-slash-asterisk-state"] = False

        v, r = lint_c_unsigned_integer_hex.lint_pre(test_plugins_params, test_file, test_shared_state, len(test_lines))
        self.assertTrue(v)
        self.assertEqual(r, None)

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintCycle1(self):

        test_file = "test_file.txt"
        test_lines = ["first", "second", "third"]
        test_plugins_params = {}
        test_shared_state = {}

        test_shared_state["lint-c-unsigned-integer-hex-internal-slash-asterisk-state"] = False

        expected_shared_state = {}
        expected_shared_state["lint-c-unsigned-integer-hex-internal-slash-asterisk-state"] = False

        expected_result1 = None
        expected_result2 = None
        expected_result3 = None

        expected_results = [expected_result1, expected_result2, expected_result3]

        for test_index in range(len(test_lines)):

            v, r = lint_c_unsigned_integer_hex.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, expected_results[test_index])

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintCycle2(self):

        test_file = "test_file.txt"
        test_lines = ["123", "010", "0xABu", "0xDF", "0b10101", "010101ull", "0.0f"]
        test_plugins_params = {}
        test_shared_state = {}

        test_shared_state["lint-c-unsigned-integer-hex-internal-slash-asterisk-state"] = False

        expected_shared_state = {}
        expected_shared_state["lint-c-unsigned-integer-hex-internal-slash-asterisk-state"] = False

        expected_result1 = None
        expected_result2 = None
        expected_result3 = None
        expected_result4 = None
        expected_result5 = None
        expected_result6 = None
        expected_result7 = None

        expected_results = [expected_result1, expected_result2, expected_result3, expected_result4, expected_result5, expected_result6, expected_result7]

        for test_index in range(len(test_lines)):

            v, r = lint_c_unsigned_integer_hex.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, expected_results[test_index])

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintCycle3(self):

        test_file = "test_file.txt"
        test_lines = ["0xaa", "0xAA", "0xaAu", "0XDFU", "0XdfU", "0aa", "xaa"]
        test_plugins_params = {}
        test_shared_state = {}

        test_shared_state["lint-c-unsigned-integer-hex-internal-slash-asterisk-state"] = False

        expected_shared_state = {}
        expected_shared_state["lint-c-unsigned-integer-hex-internal-slash-asterisk-state"] = False

        expected_result1 = ("[test_file.txt:1] has [1] unsigned integer hexadecimal notation violation.", [(1, "0xAA")])
        expected_result2 = None
        expected_result3 = ("[test_file.txt:3] has [1] unsigned integer hexadecimal notation violation.", [(3, "0xAAu")])
        expected_result4 = None
        expected_result5 = ("[test_file.txt:5] has [1] unsigned integer hexadecimal notation violation.", [(5, "0XDFU")])
        expected_result6 = None
        expected_result7 = None

        expected_results = [expected_result1, expected_result2, expected_result3, expected_result4, expected_result5, expected_result6, expected_result7]

        for test_index in range(len(test_lines)):

            v, r = lint_c_unsigned_integer_hex.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, expected_results[test_index])

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintCycle4(self):

        test_file = "test_file.txt"
        test_lines = ["0xaa;0xbb", "// 0xaa", "/* 0xbb; */", "/* 0xcc */ 0xdd;", "uint16 dev0xbb;", "0x", "0xxaa"]
        test_plugins_params = {}
        test_shared_state = {}

        test_shared_state["lint-c-unsigned-integer-hex-internal-slash-asterisk-state"] = False

        expected_shared_state = {}
        expected_shared_state["lint-c-unsigned-integer-hex-internal-slash-asterisk-state"] = False

        expected_result1 = ("[test_file.txt:1] has [2] unsigned integer hexadecimal notation violations.", [(1, "0xAA;0xBB")])
        expected_result2 = None
        expected_result3 = None
        expected_result4 = ("[test_file.txt:4] has [1] unsigned integer hexadecimal notation violation.", [(4, "/* 0xcc */ 0xDD;")])
        expected_result5 = None
        expected_result6 = None
        expected_result7 = None

        expected_results = [expected_result1, expected_result2, expected_result3, expected_result4, expected_result5, expected_result6, expected_result7]

        for test_index in range(len(test_lines)):

            v, r = lint_c_unsigned_integer_hex.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, expected_results[test_index])

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintCycle5(self):

        test_file = "test_file.txt"
        test_lines = ["    \"0xaa\"  ", "    \"0xbb\"  0xbu  ", "0xaA ;  0xDd   ; 0xBB+0xCC-0xf", " 0x//aa ", "0x/*dd  ", "0\'xa", "\'0xcc"]
        test_plugins_params = {}
        test_shared_state = {}

        test_shared_state["lint-c-unsigned-integer-hex-internal-slash-asterisk-state"] = False

        expected_shared_state = {}
        expected_shared_state["lint-c-unsigned-integer-hex-internal-slash-asterisk-state"] = False

        expected_result1 = None
        expected_result2 = ("[test_file.txt:2] has [1] unsigned integer hexadecimal notation violation.", [(2, "    \"0xbb\"  0xBu  ")])
        expected_result3 = ("[test_file.txt:3] has [3] unsigned integer hexadecimal notation violations.", [(3, "0xAA ;  0xDD   ; 0xBB+0xCC-0xF")])
        expected_result4 = None
        expected_result5 = None
        expected_result6 = None
        expected_result7 = None

        expected_results = [expected_result1, expected_result2, expected_result3, expected_result4, expected_result5, expected_result6, expected_result7]

        for test_index in range(len(test_lines)):

            v, r = lint_c_unsigned_integer_hex.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, expected_results[test_index])

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintCycle6(self):

        test_file = "test_file.txt"
        test_lines = ["// 0xaa", "/* 0xbb */", "/* 0xcc */ 0xdd", "/ / 0xaa", "/* * 0xaa */"]
        test_plugins_params = {}
        test_shared_state = {}

        test_shared_state["lint-c-unsigned-integer-hex-internal-slash-asterisk-state"] = False

        expected_shared_state = {}
        expected_shared_state["lint-c-unsigned-integer-hex-internal-slash-asterisk-state"] = False

        expected_result1 = None
        expected_result2 = None
        expected_result3 = ("[test_file.txt:3] has [1] unsigned integer hexadecimal notation violation.", [(3, "/* 0xcc */ 0xDD")])
        expected_result4 = ("[test_file.txt:4] has [1] unsigned integer hexadecimal notation violation.", [(4, "/ / 0xAA")])
        expected_result5 = None

        expected_results = [expected_result1, expected_result2, expected_result3, expected_result4, expected_result5]

        for test_index in range(len(test_lines)):

            v, r = lint_c_unsigned_integer_hex.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, expected_results[test_index])

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintCycle7(self):

        test_file = "test_file.txt"
        test_lines = ["/**", "*", "0xaa", "**/", "0xa"]
        test_plugins_params = {}
        test_shared_state = {}

        test_shared_state["lint-c-unsigned-integer-hex-internal-slash-asterisk-state"] = False

        expected_shared_state = {}
        expected_shared_state["lint-c-unsigned-integer-hex-internal-slash-asterisk-state"] = False

        expected_result1 = None
        expected_result2 = None
        expected_result3 = None
        expected_result4 = None
        expected_result5 = ("[test_file.txt:5] has [1] unsigned integer hexadecimal notation violation.", [(5, "0xA")])

        expected_results = [expected_result1, expected_result2, expected_result3, expected_result4, expected_result5]

        for test_index in range(len(test_lines)):

            v, r = lint_c_unsigned_integer_hex.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, expected_results[test_index])

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintPost1(self):

        test_file = "test_file.txt"
        test_lines = ["first", "second", "third"]
        test_plugins_params = {}
        test_shared_state = {}

        v, r = lint_c_unsigned_integer_hex.lint_post(test_plugins_params, test_file, test_shared_state)
        self.assertTrue(v)
        self.assertEqual(r, None)

    def testLintComplete(self):

        test_file = "test_file.txt"
        test_lines = ["0xaa", "0xAau", "0xBbull", "0Xdd", "0XDD", "aa", "xaa", "0aa"]
        test_plugins_params = {}
        test_shared_state = {}

        expected_shared_state = {}
        expected_shared_state["lint-c-unsigned-integer-hex-internal-slash-asterisk-state"] = False

        expected_result1 = ("[test_file.txt:1] has [1] unsigned integer hexadecimal notation violation.", [(1, "0xAA")])
        expected_result2 = ("[test_file.txt:2] has [1] unsigned integer hexadecimal notation violation.", [(2, "0xAAu")])
        expected_result3 = ("[test_file.txt:3] has [1] unsigned integer hexadecimal notation violation.", [(3, "0xBBull")])
        expected_result4 = ("[test_file.txt:4] has [1] unsigned integer hexadecimal notation violation.", [(4, "0XDD")])
        expected_result5 = None
        expected_result6 = None
        expected_result7 = None
        expected_result8 = None

        expected_results = [expected_result1, expected_result2, expected_result3, expected_result4, expected_result5, expected_result6, expected_result7, expected_result8]

        v, r = lint_c_unsigned_integer_hex.lint_pre(test_plugins_params, test_file, test_shared_state, len(test_lines))
        self.assertTrue(v)
        self.assertEqual(r, None)

        for test_index in range(len(test_lines)):

            v, r = lint_c_unsigned_integer_hex.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, expected_results[test_index])

        v, r = lint_c_unsigned_integer_hex.lint_post(test_plugins_params, test_file, test_shared_state)
        self.assertTrue(v)
        self.assertEqual(r, None)

        self.assertEqual(test_shared_state, expected_shared_state)

if __name__ == "__main__":
    unittest.main()
