#!/usr/bin/env python3

import sys
import os
import shutil
import unittest

import mvtools_test_fixture
import path_utils

import lint_check_c_header_guards

class LintCheckCHeaderGuardsTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("lint_check_c_header_guards_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testLintName(self):

        self.assertEqual(lint_check_c_header_guards.lint_name(), "lint_check_c_header_guards.py")

    def testLintPre1(self):

        test_file = "test_file.txt"
        test_lines = ["#ifndef __module_name__", "#define __module_name__", "", "#endif // __module_name__"]
        test_plugins_params = {}
        test_shared_state = {}

        test_shared_state["lint-check-c-header-guards-state"] = "expecting-ifndef"

        v, r = lint_check_c_header_guards.lint_pre(test_plugins_params, test_file, test_shared_state, len(test_lines))
        self.assertFalse(v)
        self.assertEqual(r, "shared state already contains {lint-check-c-header-guards-state}")

    def testLintPre2(self):

        test_file = "test_file.txt"
        test_lines = ["#ifndef __module_name__", "#define __module_name__", "", "#endif // __module_name__"]
        test_plugins_params = {}
        test_shared_state = {}

        v, r = lint_check_c_header_guards.lint_pre(test_plugins_params, test_file, test_shared_state, len(test_lines))
        self.assertTrue(v)
        self.assertEqual(r, None)

        expected_shared_state = {}
        expected_shared_state["lint-check-c-header-guards-state"] = "expecting-ifndef"

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintCycleX(self): # mvtodo

        test_file = "test_file.txt"
        test_lines = ["#ifndef __module_name__", "#define __module_name__", "", "#endif // __module_name__"]
        test_plugins_params = {}
        test_shared_state = {}

        test_shared_state["lint-check-c-header-guards-state"] = "expecting-ifndef"

        expected_shared_state1 = {}
        expected_shared_state1["lint-check-c-header-guards-state"] = "expecting-define"
        expected_shared_state1["lint-check-c-header-guards-first-ifndef-is"] = "__module_name__"

        expected_shared_state2 = {}
        expected_shared_state2["lint-check-c-header-guards-state"] = "expecting-endif"
        expected_shared_state2["lint-check-c-header-guards-first-ifndef-is"] = "__module_name__"

        expected_shared_state3 = {}
        expected_shared_state3["lint-check-c-header-guards-state"] = "expecting-endif"
        expected_shared_state3["lint-check-c-header-guards-first-ifndef-is"] = "__module_name__"

        expected_shared_state4 = {}
        expected_shared_state4["lint-check-c-header-guards-state"] = "expecting-endif"
        expected_shared_state4["lint-check-c-header-guards-first-ifndef-is"] = "__module_name__"
        expected_shared_state4["lint-check-c-header-guards-last-endif"] = "#endif // __module_name__"

        expected_shared_states = [expected_shared_state1, expected_shared_state2, expected_shared_state3, expected_shared_state4]

        for test_index in [1, 2, 3, 4]:

            v, r = lint_check_c_header_guards.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index, test_lines[test_index-1])
            self.assertTrue(v)
            self.assertEqual(r, None)

            self.assertEqual(test_shared_state, expected_shared_states[test_index-1])

    # mvtodo: all together also

if __name__ == "__main__":
    unittest.main()
