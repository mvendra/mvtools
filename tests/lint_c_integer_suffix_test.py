#!/usr/bin/env python

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

    def testLintDesc(self):

        self.assertEqual(lint_c_integer_suffix.lint_desc(), "checks C source files for proper integer constant suffix usage")

    def testLintPre1(self):

        test_file = "test_file.txt"
        test_lines = ["first", "second", "third"]
        test_plugins_params = {}
        test_shared_state = {}

        test_shared_state["lint-c-integer-suffix-internal-slash-asterisk-state"] = False

        v, r = lint_c_integer_suffix.lint_pre(test_plugins_params, test_file, test_shared_state, len(test_lines))
        self.assertFalse(v)
        self.assertEqual(r, "shared state already contains {lint-c-integer-suffix-internal-slash-asterisk-state}")

    def testLintPre2(self):

        test_file = "test_file.txt"
        test_lines = ["first", "second", "third"]
        test_plugins_params = {}
        test_shared_state = {}

        expected_shared_state = {}
        expected_shared_state["lint-c-integer-suffix-internal-slash-asterisk-state"] = False

        v, r = lint_c_integer_suffix.lint_pre(test_plugins_params, test_file, test_shared_state, len(test_lines))
        self.assertTrue(v)
        self.assertEqual(r, None)

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintCycle1(self):

        test_file = "test_file.txt"
        test_lines = ["first", "second", "third"]
        test_plugins_params = {}
        test_shared_state = {}

        test_shared_state["lint-c-integer-suffix-internal-slash-asterisk-state"] = False

        expected_shared_state = {}
        expected_shared_state["lint-c-integer-suffix-internal-slash-asterisk-state"] = False

        expected_result1 = None
        expected_result2 = None
        expected_result3 = None

        expected_results = [expected_result1, expected_result2, expected_result3]

        for test_index in range(len(test_lines)):

            v, r = lint_c_integer_suffix.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, expected_results[test_index])

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintCycle2(self):

        test_file = "test_file.txt"
        test_lines = ["123", "010", "0xab", "0XDF", "0b10101", "0B10101", "0.0"]
        test_plugins_params = {}
        test_shared_state = {}

        test_shared_state["lint-c-integer-suffix-internal-slash-asterisk-state"] = False

        expected_shared_state = {}
        expected_shared_state["lint-c-integer-suffix-internal-slash-asterisk-state"] = False

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

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintCycle3(self):

        test_file = "test_file.txt"
        test_lines = ["123U", "010U", "0xabU", "0XDFU", "0b10101U", "0B10101U", "0.0F"]
        test_plugins_params = {}
        test_shared_state = {}

        test_shared_state["lint-c-integer-suffix-internal-slash-asterisk-state"] = False

        expected_shared_state = {}
        expected_shared_state["lint-c-integer-suffix-internal-slash-asterisk-state"] = False

        expected_result1 = ("[test_file.txt:1] has [1] integer suffix violation.", [(1, "123")])
        expected_result2 = ("[test_file.txt:2] has [1] integer suffix violation.", [(2, "010")])
        expected_result3 = ("[test_file.txt:3] has [1] integer suffix violation.", [(3, "0xab")])
        expected_result4 = ("[test_file.txt:4] has [1] integer suffix violation.", [(4, "0XDF")])
        expected_result5 = ("[test_file.txt:5] has [1] integer suffix violation.", [(5, "0b10101")])
        expected_result6 = ("[test_file.txt:6] has [1] integer suffix violation.", [(6, "0B10101")])
        expected_result7 = ("[test_file.txt:7] has [1] integer suffix violation.", [(7, "0.0")])

        expected_results = [expected_result1, expected_result2, expected_result3, expected_result4, expected_result5, expected_result6, expected_result7]

        for test_index in range(len(test_lines)):

            v, r = lint_c_integer_suffix.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, expected_results[test_index])

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintCycle4(self):

        test_file = "test_file.txt"
        test_lines = ["123U;", "010U;", "0xabU;", "0XDFU;", "0b10101U;", "0B10101U;", "0.0F;"]
        test_plugins_params = {}
        test_shared_state = {}

        test_shared_state["lint-c-integer-suffix-internal-slash-asterisk-state"] = False

        expected_shared_state = {}
        expected_shared_state["lint-c-integer-suffix-internal-slash-asterisk-state"] = False

        expected_result1 = ("[test_file.txt:1] has [1] integer suffix violation.", [(1, "123;")])
        expected_result2 = ("[test_file.txt:2] has [1] integer suffix violation.", [(2, "010;")])
        expected_result3 = ("[test_file.txt:3] has [1] integer suffix violation.", [(3, "0xab;")])
        expected_result4 = ("[test_file.txt:4] has [1] integer suffix violation.", [(4, "0XDF;")])
        expected_result5 = ("[test_file.txt:5] has [1] integer suffix violation.", [(5, "0b10101;")])
        expected_result6 = ("[test_file.txt:6] has [1] integer suffix violation.", [(6, "0B10101;")])
        expected_result7 = ("[test_file.txt:7] has [1] integer suffix violation.", [(7, "0.0;")])

        expected_results = [expected_result1, expected_result2, expected_result3, expected_result4, expected_result5, expected_result6, expected_result7]

        for test_index in range(len(test_lines)):

            v, r = lint_c_integer_suffix.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, expected_results[test_index])

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintCycle5(self):

        test_file = "test_file.txt"
        test_lines = ["    123LL", "    010LL", "    0xabLL", "    0XDFLL", "    0b10101LL", "    0B10101LL", "    0.0F"]
        test_plugins_params = {}
        test_shared_state = {}

        test_shared_state["lint-c-integer-suffix-internal-slash-asterisk-state"] = False

        expected_shared_state = {}
        expected_shared_state["lint-c-integer-suffix-internal-slash-asterisk-state"] = False

        expected_result1 = ("[test_file.txt:1] has [1] integer suffix violation.", [(1, "    123")])
        expected_result2 = ("[test_file.txt:2] has [1] integer suffix violation.", [(2, "    010")])
        expected_result3 = ("[test_file.txt:3] has [1] integer suffix violation.", [(3, "    0xab")])
        expected_result4 = ("[test_file.txt:4] has [1] integer suffix violation.", [(4, "    0XDF")])
        expected_result5 = ("[test_file.txt:5] has [1] integer suffix violation.", [(5, "    0b10101")])
        expected_result6 = ("[test_file.txt:6] has [1] integer suffix violation.", [(6, "    0B10101")])
        expected_result7 = ("[test_file.txt:7] has [1] integer suffix violation.", [(7, "    0.0")])

        expected_results = [expected_result1, expected_result2, expected_result3, expected_result4, expected_result5, expected_result6, expected_result7]

        for test_index in range(len(test_lines)):

            v, r = lint_c_integer_suffix.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, expected_results[test_index])

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintCycle6(self):

        test_file = "test_file.txt"
        test_lines = ["    123LL;321ULL    ", "    010LL 111ULL", "    0xabLL;0xccULL    0xddULL", "    0XDFLL    0XFDLL;", "    0b10101Ll", "    0B10101LL;;  8l", "    0..F", "    0.F   ", "    .F   "]
        test_plugins_params = {}
        test_shared_state = {}

        test_shared_state["lint-c-integer-suffix-internal-slash-asterisk-state"] = False

        expected_shared_state = {}
        expected_shared_state["lint-c-integer-suffix-internal-slash-asterisk-state"] = False

        expected_result1 = ("[test_file.txt:1] has [2] integer suffix violations.", [(1, "    123;321    ")])
        expected_result2 = ("[test_file.txt:2] has [2] integer suffix violations.", [(2, "    010 111")])
        expected_result3 = ("[test_file.txt:3] has [3] integer suffix violations.", [(3, "    0xab;0xcc    0xdd")])
        expected_result4 = ("[test_file.txt:4] has [2] integer suffix violations.", [(4, "    0XDF    0XFD;")])
        expected_result5 = ("[test_file.txt:5] has [1] integer suffix violation.", [(5, "    0b10101")])
        expected_result6 = ("[test_file.txt:6] has [2] integer suffix violations.", [(6, "    0B10101;;  8")])
        expected_result7 = None
        expected_result8 = None
        expected_result9 = None

        expected_results = [expected_result1, expected_result2, expected_result3, expected_result4, expected_result5, expected_result6, expected_result7, expected_result8, expected_result9]

        for test_index in range(len(test_lines)):

            v, r = lint_c_integer_suffix.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, expected_results[test_index])

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintCycle7(self):

        test_file = "test_file.txt"
        test_lines = ["123", "010", "0xab", "0XDF", "0b10101", "0B10101", "0.0"]
        test_plugins_params = {}
        test_shared_state = {}

        test_shared_state["lint-c-integer-suffix-internal-slash-asterisk-state"] = False

        expected_shared_state = {}
        expected_shared_state["lint-c-integer-suffix-internal-slash-asterisk-state"] = False

        test_plugins_params["lint-c-integer-suffix-warn-no-suffix"] = ["yes"]

        expected_result1 = ("[test_file.txt:1] has [1] integer suffix violation.", [])
        expected_result2 = ("[test_file.txt:2] has [1] integer suffix violation.", [])
        expected_result3 = ("[test_file.txt:3] has [1] integer suffix violation.", [])
        expected_result4 = ("[test_file.txt:4] has [1] integer suffix violation.", [])
        expected_result5 = ("[test_file.txt:5] has [1] integer suffix violation.", [])
        expected_result6 = ("[test_file.txt:6] has [1] integer suffix violation.", [])
        expected_result7 = ("[test_file.txt:7] has [1] integer suffix violation.", [])

        expected_results = [expected_result1, expected_result2, expected_result3, expected_result4, expected_result5, expected_result6, expected_result7]

        for test_index in range(len(test_lines)):

            v, r = lint_c_integer_suffix.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, expected_results[test_index])

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintCycle8(self):

        test_file = "test_file.txt"
        test_lines = ["123 123U;", " 50LF  010", "0xab  0x11L ", "0XDF  ;   0XAAl ;  ", "  0b111ul 0b10101  ", " 0B10101 ;  0B101U", "0.0 0.0F "]
        test_plugins_params = {}
        test_shared_state = {}

        test_shared_state["lint-c-integer-suffix-internal-slash-asterisk-state"] = False

        expected_shared_state = {}
        expected_shared_state["lint-c-integer-suffix-internal-slash-asterisk-state"] = False

        test_plugins_params["lint-c-integer-suffix-warn-no-suffix"] = ["yes"]

        expected_result1 = ("[test_file.txt:1] has [2] integer suffix violations.", [(1, "123 123;")])
        expected_result2 = ("[test_file.txt:2] has [2] integer suffix violations.", [(2, " 50  010")])
        expected_result3 = ("[test_file.txt:3] has [2] integer suffix violations.", [(3, "0xab  0x11 ")])
        expected_result4 = ("[test_file.txt:4] has [2] integer suffix violations.", [(4, "0XDF  ;   0XAA ;  ")])
        expected_result5 = ("[test_file.txt:5] has [2] integer suffix violations.", [(5, "  0b111 0b10101  ")])
        expected_result6 = ("[test_file.txt:6] has [2] integer suffix violations.", [(6, " 0B10101 ;  0B101")])
        expected_result7 = ("[test_file.txt:7] has [2] integer suffix violations.", [(7, "0.0 0.0 ")])

        expected_results = [expected_result1, expected_result2, expected_result3, expected_result4, expected_result5, expected_result6, expected_result7]

        for test_index in range(len(test_lines)):

            v, r = lint_c_integer_suffix.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, expected_results[test_index])

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintCycle9(self):

        test_file = "test_file.txt"
        test_lines = ["some1Uvar", "Somevar1U", "some1 var", "_2L", "funcname2()", "_f3(){}", "funcname2U()", "_f3L(){}"]
        test_plugins_params = {}
        test_shared_state = {}

        test_shared_state["lint-c-integer-suffix-internal-slash-asterisk-state"] = False

        expected_shared_state = {}
        expected_shared_state["lint-c-integer-suffix-internal-slash-asterisk-state"] = False

        expected_result1 = None
        expected_result2 = None
        expected_result3 = None
        expected_result4 = None
        expected_result5 = None
        expected_result6 = None
        expected_result7 = None
        expected_result8 = None

        expected_results = [expected_result1, expected_result2, expected_result3, expected_result4, expected_result5, expected_result6, expected_result7, expected_result8]

        for test_index in range(len(test_lines)):

            v, r = lint_c_integer_suffix.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, expected_results[test_index])

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintCycle10(self):

        test_file = "test_file.txt"
        test_lines = ["\"1U\"", "\"some 1U str\"", "\"somestr1U\"", "\"_ 2L\"", "\"some_\\\"str 1U\"", "\"\\K\""]
        test_plugins_params = {}
        test_shared_state = {}

        test_shared_state["lint-c-integer-suffix-internal-slash-asterisk-state"] = False

        expected_shared_state = {}
        expected_shared_state["lint-c-integer-suffix-internal-slash-asterisk-state"] = False

        expected_result1 = None
        expected_result2 = None
        expected_result3 = None
        expected_result4 = None
        expected_result5 = None
        expected_result6 = None

        expected_results = [expected_result1, expected_result2, expected_result3, expected_result4, expected_result5, expected_result6]

        for test_index in range(len(test_lines)):

            v, r = lint_c_integer_suffix.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, expected_results[test_index])

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintCycle11(self):

        test_file = "test_file.txt"
        test_lines = ["\'1\'"]
        test_plugins_params = {}
        test_shared_state = {}

        test_shared_state["lint-c-integer-suffix-internal-slash-asterisk-state"] = False

        expected_shared_state = {}
        expected_shared_state["lint-c-integer-suffix-internal-slash-asterisk-state"] = False

        expected_result1 = None

        expected_results = [expected_result1]

        for test_index in range(len(test_lines)):

            v, r = lint_c_integer_suffix.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, expected_results[test_index])

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintCycle12(self):

        test_file = "test_file.txt"
        test_lines = ["0.0u", "0.0u 123u"]
        test_plugins_params = {}
        test_shared_state = {}

        test_shared_state["lint-c-integer-suffix-internal-slash-asterisk-state"] = False

        expected_shared_state = {}
        expected_shared_state["lint-c-integer-suffix-internal-slash-asterisk-state"] = False

        expected_result1 = ("[test_file.txt:1] has [1] integer suffix violation.", [(1, "0.0")])
        expected_result2 = ("[test_file.txt:2] has [1] integer suffix violation.", [(2, "0.0 123u")])

        expected_results = [expected_result1, expected_result2]

        for test_index in range(len(test_lines)):

            v, r = lint_c_integer_suffix.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, expected_results[test_index])

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintCycle13(self):

        test_file = "test_file.txt"
        test_lines = ["// 20U", "/* 20U */", "/* 20U */ 20U", "/ / 20U", "/* * 20U */"]
        test_plugins_params = {}
        test_shared_state = {}

        test_shared_state["lint-c-integer-suffix-internal-slash-asterisk-state"] = False

        expected_shared_state = {}
        expected_shared_state["lint-c-integer-suffix-internal-slash-asterisk-state"] = False

        expected_result1 = None
        expected_result2 = None
        expected_result3 = ("[test_file.txt:3] has [1] integer suffix violation.", [(3, "/* 20U */ 20")])
        expected_result4 = ("[test_file.txt:4] has [1] integer suffix violation.", [(4, "/ / 20")])
        expected_result5 = None

        expected_results = [expected_result1, expected_result2, expected_result3, expected_result4, expected_result5]

        for test_index in range(len(test_lines)):

            v, r = lint_c_integer_suffix.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, expected_results[test_index])

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintCycle14(self):

        test_file = "test_file.txt"
        test_lines = ["/**", "*", "20U", "**/", "20U"]
        test_plugins_params = {}
        test_shared_state = {}

        test_shared_state["lint-c-integer-suffix-internal-slash-asterisk-state"] = False

        expected_shared_state = {}
        expected_shared_state["lint-c-integer-suffix-internal-slash-asterisk-state"] = False

        expected_result1 = None
        expected_result2 = None
        expected_result3 = None
        expected_result4 = None
        expected_result5 = ("[test_file.txt:5] has [1] integer suffix violation.", [(5, "20")])

        expected_results = [expected_result1, expected_result2, expected_result3, expected_result4, expected_result5]

        for test_index in range(len(test_lines)):

            v, r = lint_c_integer_suffix.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, expected_results[test_index])

        self.assertEqual(test_shared_state, expected_shared_state)

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

        expected_shared_state = {}
        expected_shared_state["lint-c-integer-suffix-internal-slash-asterisk-state"] = False

        expected_result1 = ("[test_file.txt:1] has [1] integer suffix violation.", [(1, "123")])
        expected_result2 = ("[test_file.txt:2] has [1] integer suffix violation.", [(2, "010")])
        expected_result3 = ("[test_file.txt:3] has [1] integer suffix violation.", [(3, "0xab")])
        expected_result4 = ("[test_file.txt:4] has [1] integer suffix violation.", [(4, "0XDF")])
        expected_result5 = ("[test_file.txt:5] has [1] integer suffix violation.", [(5, "0b10101")])
        expected_result6 = ("[test_file.txt:6] has [1] integer suffix violation.", [(6, "0B10101")])
        expected_result7 = ("[test_file.txt:7] has [1] integer suffix violation.", [(7, "0.0")])

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

        self.assertEqual(test_shared_state, expected_shared_state)

if __name__ == "__main__":
    unittest.main()
