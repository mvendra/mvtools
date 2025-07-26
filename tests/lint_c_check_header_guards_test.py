#!/usr/bin/env python3

import sys
import os
import shutil
import unittest

import mvtools_test_fixture
import path_utils

import lint_c_check_header_guards

class LintCheckCHeaderGuardsTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("lint_c_check_header_guards_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testLintName(self):

        self.assertEqual(lint_c_check_header_guards.lint_name(), "lint_c_check_header_guards.py")

    def testLintPre1(self):

        test_file = "test_file.txt"
        test_lines = ["#ifndef __module_name__", "#define __module_name__", "", "#endif // __module_name__"]
        test_plugins_params = {}
        test_shared_state = {}

        test_shared_state["lint-check-c-header-guards-state"] = "expecting-ifndef"

        v, r = lint_c_check_header_guards.lint_pre(test_plugins_params, test_file, test_shared_state, len(test_lines))
        self.assertFalse(v)
        self.assertEqual(r, "shared state already contains {lint-check-c-header-guards-state}")

    def testLintPre2(self):

        test_file = "test_file.txt"
        test_lines = ["#ifndef __module_name__", "#define __module_name__", "", "#endif // __module_name__"]
        test_plugins_params = {}
        test_shared_state = {}

        v, r = lint_c_check_header_guards.lint_pre(test_plugins_params, test_file, test_shared_state, len(test_lines))
        self.assertTrue(v)
        self.assertEqual(r, None)

        expected_shared_state = {}
        expected_shared_state["lint-check-c-header-guards-state"] = "expecting-ifndef"

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintCycle1(self):

        test_file = "test_file.txt"
        test_lines = ["   ", "#ifndef __module_name__", "#define __module_name__", "   ", "#endif // __module_name__", "   "]
        test_plugins_params = {}
        test_shared_state = {}

        test_shared_state["lint-check-c-header-guards-state"] = "expecting-ifndef"

        expected_shared_state = {}
        expected_shared_state["lint-check-c-header-guards-state"] = "expecting-ifndef"

        v, r = lint_c_check_header_guards.lint_cycle(test_plugins_params, test_file, test_shared_state, 1, test_lines[0])
        self.assertTrue(v)
        self.assertEqual(r, None)

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintCycle2(self):

        test_file = "test_file.txt"
        test_lines = ["   ", "!ifndef __module_name__"]
        test_plugins_params = {}
        test_shared_state = {}

        test_shared_state["lint-check-c-header-guards-state"] = "expecting-ifndef"

        expected_shared_state1 = {}
        expected_shared_state1["lint-check-c-header-guards-state"] = "expecting-ifndef"

        expected_shared_state2 = {}
        expected_shared_state2["lint-check-c-header-guards-state"] = "expecting-ifndef"

        expected_shared_states = [expected_shared_state1, expected_shared_state2]

        for test_index in range(len(test_lines)):

            v, r = lint_c_check_header_guards.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])

            if test_index < 1:
                self.assertTrue(v)
                self.assertEqual(r, None)
            else:
                self.assertTrue(v)
                self.assertEqual(r, ("[test_file.txt:2]: first content is not an ifndef.", []))

            self.assertEqual(test_shared_state, expected_shared_states[test_index])

    def testLintCycle3(self):

        test_file = "test_file.txt"
        test_lines = ["   ", "#ifndef "]
        test_plugins_params = {}
        test_shared_state = {}

        test_shared_state["lint-check-c-header-guards-state"] = "expecting-ifndef"

        expected_shared_state1 = {}
        expected_shared_state1["lint-check-c-header-guards-state"] = "expecting-ifndef"

        expected_shared_state2 = {}
        expected_shared_state2["lint-check-c-header-guards-state"] = "expecting-ifndef"

        expected_shared_states = [expected_shared_state1, expected_shared_state2]

        for test_index in range(len(test_lines)):

            v, r = lint_c_check_header_guards.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])

            if test_index < 1:
                self.assertTrue(v)
                self.assertEqual(r, None)
            else:
                self.assertTrue(v)
                self.assertEqual(r, ("[test_file.txt:2]: first content is not an ifndef.", []))

            self.assertEqual(test_shared_state, expected_shared_states[test_index])

    def testLintCycle4(self):

        test_file = "test_file.txt"
        test_lines = ["   ", "#ifndof __module_name__"]
        test_plugins_params = {}
        test_shared_state = {}

        test_shared_state["lint-check-c-header-guards-state"] = "expecting-ifndef"

        expected_shared_state1 = {}
        expected_shared_state1["lint-check-c-header-guards-state"] = "expecting-ifndef"

        expected_shared_state2 = {}
        expected_shared_state2["lint-check-c-header-guards-state"] = "expecting-ifndef"

        expected_shared_states = [expected_shared_state1, expected_shared_state2]

        for test_index in range(len(test_lines)):

            v, r = lint_c_check_header_guards.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])

            if test_index < 1:
                self.assertTrue(v)
                self.assertEqual(r, None)
            else:
                self.assertTrue(v)
                self.assertEqual(r, ("[test_file.txt:2]: first content is not an ifndef.", []))

            self.assertEqual(test_shared_state, expected_shared_states[test_index])

    def testLintCycle5(self):

        test_file = "test_file.txt"
        test_lines = ["   ", "#ifndef __module_name__", "   "]
        test_plugins_params = {}
        test_shared_state = {}

        test_shared_state["lint-check-c-header-guards-state"] = "expecting-ifndef"

        expected_shared_state1 = {}
        expected_shared_state1["lint-check-c-header-guards-state"] = "expecting-ifndef"

        expected_shared_state2 = {}
        expected_shared_state2["lint-check-c-header-guards-state"] = "expecting-define"
        expected_shared_state2["lint-check-c-header-guards-first-ifndef-is"] = "__module_name__"

        expected_shared_state3 = {}
        expected_shared_state3["lint-check-c-header-guards-state"] = "expecting-define"
        expected_shared_state3["lint-check-c-header-guards-first-ifndef-is"] = "__module_name__"

        expected_shared_states = [expected_shared_state1, expected_shared_state2, expected_shared_state3]

        for test_index in range(len(test_lines)):

            v, r = lint_c_check_header_guards.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])

            if test_index < 2:
                self.assertTrue(v)
                self.assertEqual(r, None)
            else:
                self.assertTrue(v)
                self.assertEqual(r, ("[test_file.txt:3]: follow-up define not found just after first ifndef.", []))

            self.assertEqual(test_shared_state, expected_shared_states[test_index])

    def testLintCycle6(self):

        test_file = "test_file.txt"
        test_lines = ["   ", "#ifndef __module_name__", "!define __module_name__"]
        test_plugins_params = {}
        test_shared_state = {}

        test_shared_state["lint-check-c-header-guards-state"] = "expecting-ifndef"

        expected_shared_state1 = {}
        expected_shared_state1["lint-check-c-header-guards-state"] = "expecting-ifndef"

        expected_shared_state2 = {}
        expected_shared_state2["lint-check-c-header-guards-state"] = "expecting-define"
        expected_shared_state2["lint-check-c-header-guards-first-ifndef-is"] = "__module_name__"

        expected_shared_state3 = {}
        expected_shared_state3["lint-check-c-header-guards-state"] = "expecting-define"
        expected_shared_state3["lint-check-c-header-guards-first-ifndef-is"] = "__module_name__"

        expected_shared_states = [expected_shared_state1, expected_shared_state2, expected_shared_state3]

        for test_index in range(len(test_lines)):

            v, r = lint_c_check_header_guards.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])

            if test_index < 2:
                self.assertTrue(v)
                self.assertEqual(r, None)
            else:
                self.assertTrue(v)
                self.assertEqual(r, ("[test_file.txt:3]: follow-up define not found just after first ifndef.", []))

            self.assertEqual(test_shared_state, expected_shared_states[test_index])

    def testLintCycle7(self):

        test_file = "test_file.txt"
        test_lines = ["   ", "#ifndef __module_name__", "#define "]
        test_plugins_params = {}
        test_shared_state = {}

        test_shared_state["lint-check-c-header-guards-state"] = "expecting-ifndef"

        expected_shared_state1 = {}
        expected_shared_state1["lint-check-c-header-guards-state"] = "expecting-ifndef"

        expected_shared_state2 = {}
        expected_shared_state2["lint-check-c-header-guards-state"] = "expecting-define"
        expected_shared_state2["lint-check-c-header-guards-first-ifndef-is"] = "__module_name__"

        expected_shared_state3 = {}
        expected_shared_state3["lint-check-c-header-guards-state"] = "expecting-define"
        expected_shared_state3["lint-check-c-header-guards-first-ifndef-is"] = "__module_name__"

        expected_shared_states = [expected_shared_state1, expected_shared_state2, expected_shared_state3]

        for test_index in range(len(test_lines)):

            v, r = lint_c_check_header_guards.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])

            if test_index < 2:
                self.assertTrue(v)
                self.assertEqual(r, None)
            else:
                self.assertTrue(v)
                self.assertEqual(r, ("[test_file.txt:3]: follow-up define not found just after first ifndef.", []))

            self.assertEqual(test_shared_state, expected_shared_states[test_index])

    def testLintCycle8(self):

        test_file = "test_file.txt"
        test_lines = ["   ", "#ifndef __module_name__", "#dofine __module_name__"]
        test_plugins_params = {}
        test_shared_state = {}

        test_shared_state["lint-check-c-header-guards-state"] = "expecting-ifndef"

        expected_shared_state1 = {}
        expected_shared_state1["lint-check-c-header-guards-state"] = "expecting-ifndef"

        expected_shared_state2 = {}
        expected_shared_state2["lint-check-c-header-guards-state"] = "expecting-define"
        expected_shared_state2["lint-check-c-header-guards-first-ifndef-is"] = "__module_name__"

        expected_shared_state3 = {}
        expected_shared_state3["lint-check-c-header-guards-state"] = "expecting-define"
        expected_shared_state3["lint-check-c-header-guards-first-ifndef-is"] = "__module_name__"

        expected_shared_states = [expected_shared_state1, expected_shared_state2, expected_shared_state3]

        for test_index in range(len(test_lines)):

            v, r = lint_c_check_header_guards.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])

            if test_index < 2:
                self.assertTrue(v)
                self.assertEqual(r, None)
            else:
                self.assertTrue(v)
                self.assertEqual(r, ("[test_file.txt:3]: follow-up define not found just after first ifndef.", []))

            self.assertEqual(test_shared_state, expected_shared_states[test_index])

    def testLintCycle9(self):

        test_file = "test_file.txt"
        test_lines = ["   ", "#ifndef __module_name__", "#define __modula_name__"]
        test_plugins_params = {}
        test_shared_state = {}

        test_shared_state["lint-check-c-header-guards-state"] = "expecting-ifndef"

        expected_shared_state1 = {}
        expected_shared_state1["lint-check-c-header-guards-state"] = "expecting-ifndef"

        expected_shared_state2 = {}
        expected_shared_state2["lint-check-c-header-guards-state"] = "expecting-define"
        expected_shared_state2["lint-check-c-header-guards-first-ifndef-is"] = "__module_name__"

        expected_shared_state3 = {}
        expected_shared_state3["lint-check-c-header-guards-state"] = "expecting-define"
        expected_shared_state3["lint-check-c-header-guards-first-ifndef-is"] = "__module_name__"

        expected_shared_states = [expected_shared_state1, expected_shared_state2, expected_shared_state3]

        for test_index in range(len(test_lines)):

            v, r = lint_c_check_header_guards.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])

            if test_index < 2:
                self.assertTrue(v)
                self.assertEqual(r, None)
            else:
                self.assertTrue(v)
                self.assertEqual(r, ("[test_file.txt:3]: incorrect header guard detected (expected: [__module_name__], have: [__modula_name__]).", []))

            self.assertEqual(test_shared_state, expected_shared_states[test_index])

    def testLintCycle10(self):

        test_file = "test_file.txt"
        test_lines = ["   ", "#ifndef __module_name__", "#define __module_name__", "   "]
        test_plugins_params = {}
        test_shared_state = {}

        test_shared_state["lint-check-c-header-guards-state"] = "expecting-ifndef"

        expected_shared_state1 = {}
        expected_shared_state1["lint-check-c-header-guards-state"] = "expecting-ifndef"

        expected_shared_state2 = {}
        expected_shared_state2["lint-check-c-header-guards-state"] = "expecting-define"
        expected_shared_state2["lint-check-c-header-guards-first-ifndef-is"] = "__module_name__"

        expected_shared_state3 = {}
        expected_shared_state3["lint-check-c-header-guards-state"] = "expecting-endif"
        expected_shared_state3["lint-check-c-header-guards-first-ifndef-is"] = "__module_name__"

        expected_shared_state4 = {}
        expected_shared_state4["lint-check-c-header-guards-state"] = "expecting-endif"
        expected_shared_state4["lint-check-c-header-guards-first-ifndef-is"] = "__module_name__"

        expected_shared_states = [expected_shared_state1, expected_shared_state2, expected_shared_state3, expected_shared_state4]

        for test_index in range(len(test_lines)):

            v, r = lint_c_check_header_guards.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, None)

            self.assertEqual(test_shared_state, expected_shared_states[test_index])

    def testLintCycle11(self):

        test_file = "test_file.txt"
        test_lines = ["   ", "#ifndef __module_name__", "#define __module_name__", "   ", "#endif // __module_name__"]
        test_plugins_params = {}
        test_shared_state = {}

        test_shared_state["lint-check-c-header-guards-state"] = "expecting-ifndef"

        expected_shared_state1 = {}
        expected_shared_state1["lint-check-c-header-guards-state"] = "expecting-ifndef"

        expected_shared_state2 = {}
        expected_shared_state2["lint-check-c-header-guards-state"] = "expecting-define"
        expected_shared_state2["lint-check-c-header-guards-first-ifndef-is"] = "__module_name__"

        expected_shared_state3 = {}
        expected_shared_state3["lint-check-c-header-guards-state"] = "expecting-endif"
        expected_shared_state3["lint-check-c-header-guards-first-ifndef-is"] = "__module_name__"

        expected_shared_state4 = {}
        expected_shared_state4["lint-check-c-header-guards-state"] = "expecting-endif"
        expected_shared_state4["lint-check-c-header-guards-first-ifndef-is"] = "__module_name__"

        expected_shared_state5 = {}
        expected_shared_state5["lint-check-c-header-guards-state"] = "expecting-endif"
        expected_shared_state5["lint-check-c-header-guards-first-ifndef-is"] = "__module_name__"
        expected_shared_state5["lint-check-c-header-guards-last-endif"] = "#endif // __module_name__"

        expected_shared_states = [expected_shared_state1, expected_shared_state2, expected_shared_state3, expected_shared_state4, expected_shared_state5]

        for test_index in range(len(test_lines)):

            v, r = lint_c_check_header_guards.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, None)

            self.assertEqual(test_shared_state, expected_shared_states[test_index])

    def testLintCycle12(self):

        test_file = "test_file.txt"
        test_lines = ["   ", "#ifndef __module_name__", "#define __module_name__", "   ", "#endif // __module_name__", "   "]
        test_plugins_params = {}
        test_shared_state = {}

        test_shared_state["lint-check-c-header-guards-state"] = "expecting-something-else"

        expected_shared_state = {}
        expected_shared_state["lint-check-c-header-guards-state"] = "expecting-something-else"

        v, r = lint_c_check_header_guards.lint_cycle(test_plugins_params, test_file, test_shared_state, 1, test_lines[0])
        self.assertFalse(v)
        self.assertEqual(r, "unknown state")

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintCycle13(self):

        test_file = "test_file.txt"
        test_lines = ["   ", "#ifndef __module_name__", "#define __module_name__", "   ", "#endif // __module_name__", "   "]
        test_plugins_params = {}
        test_shared_state = {}

        test_shared_state["lint-check-c-header-guards-state"] = "expecting-ifndef"

        expected_shared_state1 = {}
        expected_shared_state1["lint-check-c-header-guards-state"] = "expecting-ifndef"

        expected_shared_state2 = {}
        expected_shared_state2["lint-check-c-header-guards-state"] = "expecting-define"
        expected_shared_state2["lint-check-c-header-guards-first-ifndef-is"] = "__module_name__"

        expected_shared_state3 = {}
        expected_shared_state3["lint-check-c-header-guards-state"] = "expecting-endif"
        expected_shared_state3["lint-check-c-header-guards-first-ifndef-is"] = "__module_name__"

        expected_shared_state4 = {}
        expected_shared_state4["lint-check-c-header-guards-state"] = "expecting-endif"
        expected_shared_state4["lint-check-c-header-guards-first-ifndef-is"] = "__module_name__"

        expected_shared_state5 = {}
        expected_shared_state5["lint-check-c-header-guards-state"] = "expecting-endif"
        expected_shared_state5["lint-check-c-header-guards-first-ifndef-is"] = "__module_name__"
        expected_shared_state5["lint-check-c-header-guards-last-endif"] = "#endif // __module_name__"

        expected_shared_state6 = {}
        expected_shared_state6["lint-check-c-header-guards-state"] = "expecting-endif"
        expected_shared_state6["lint-check-c-header-guards-first-ifndef-is"] = "__module_name__"
        expected_shared_state6["lint-check-c-header-guards-last-endif"] = "#endif // __module_name__"

        expected_shared_states = [expected_shared_state1, expected_shared_state2, expected_shared_state3, expected_shared_state4, expected_shared_state5, expected_shared_state6]

        for test_index in range(len(test_lines)):

            v, r = lint_c_check_header_guards.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, None)

            self.assertEqual(test_shared_state, expected_shared_states[test_index])

    def testLintPost1(self):

        test_file = "test_file.txt"
        test_lines = ["#ifndef __module_name__", "#define __module_name__", "   ", "#endif // __module_name__"]
        test_plugins_params = {}
        test_shared_state = {}

        test_shared_state["lint-check-c-header-guards-state"] = "expecting-define"
        test_shared_state["lint-check-c-header-guards-first-ifndef-is"] = "__module_name__"
        test_shared_state["lint-check-c-header-guards-last-endif"] = "#endif // __module_name__"

        v, r = lint_c_check_header_guards.lint_post(test_plugins_params, test_file, test_shared_state)
        self.assertFalse(v)
        self.assertEqual(r, "wrong state at post")

        expected_shared_state = {}
        expected_shared_state["lint-check-c-header-guards-state"] = "expecting-define"
        expected_shared_state["lint-check-c-header-guards-first-ifndef-is"] = "__module_name__"
        expected_shared_state["lint-check-c-header-guards-last-endif"] = "#endif // __module_name__"

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintPost2(self):

        test_file = "test_file.txt"
        test_lines = ["#ifndef __module_name__", "#define __module_name__", "   ", "#endif // __module_name__"]
        test_plugins_params = {}
        test_shared_state = {}

        test_shared_state["lint-check-c-header-guards-state"] = "expecting-endif"
        test_shared_state["lint-check-c-header-guards-first-ifndef-is"] = "__module_name__"

        v, r = lint_c_check_header_guards.lint_post(test_plugins_params, test_file, test_shared_state)
        self.assertTrue(v)
        self.assertEqual(r, ("no endifs detected", []))

        expected_shared_state = {}
        expected_shared_state["lint-check-c-header-guards-state"] = "expecting-endif"
        expected_shared_state["lint-check-c-header-guards-first-ifndef-is"] = "__module_name__"

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintPost3(self):

        test_file = "test_file.txt"
        test_lines = ["#ifndef __module_name__", "#define __module_name__", "   ", "#endif // __module_name__"]
        test_plugins_params = {}
        test_shared_state = {}

        test_shared_state["lint-check-c-header-guards-state"] = "expecting-endif"
        test_shared_state["lint-check-c-header-guards-first-ifndef-is"] = "__module_name__"
        test_shared_state["lint-check-c-header-guards-last-endif"] = ""

        v, r = lint_c_check_header_guards.lint_post(test_plugins_params, test_file, test_shared_state)
        self.assertTrue(v)
        self.assertEqual(r, ("invalid final endif", []))

        expected_shared_state = {}
        expected_shared_state["lint-check-c-header-guards-state"] = "expecting-endif"
        expected_shared_state["lint-check-c-header-guards-first-ifndef-is"] = "__module_name__"
        expected_shared_state["lint-check-c-header-guards-last-endif"] = ""

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintPost4(self):

        test_file = "test_file.txt"
        test_lines = ["#ifndef __module_name__", "#define __module_name__", "   ", "#endif // __module_name__"]
        test_plugins_params = {}
        test_shared_state = {}

        test_shared_state["lint-check-c-header-guards-state"] = "expecting-endif"
        test_shared_state["lint-check-c-header-guards-first-ifndef-is"] = "__module_name__"
        test_shared_state["lint-check-c-header-guards-last-endif"] = "endif // __module_name__"

        v, r = lint_c_check_header_guards.lint_post(test_plugins_params, test_file, test_shared_state)
        self.assertTrue(v)
        self.assertEqual(r, ("invalid final endif", []))

        expected_shared_state = {}
        expected_shared_state["lint-check-c-header-guards-state"] = "expecting-endif"
        expected_shared_state["lint-check-c-header-guards-first-ifndef-is"] = "__module_name__"
        expected_shared_state["lint-check-c-header-guards-last-endif"] = "endif // __module_name__"

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintPost5(self):

        test_file = "test_file.txt"
        test_lines = ["#ifndef __module_name__", "#define __module_name__", "   ", "#endif // __module_name__"]
        test_plugins_params = {}
        test_shared_state = {}

        test_shared_state["lint-check-c-header-guards-state"] = "expecting-endif"
        test_shared_state["lint-check-c-header-guards-first-ifndef-is"] = "__module_name__"
        test_shared_state["lint-check-c-header-guards-last-endif"] = "#endif"

        v, r = lint_c_check_header_guards.lint_post(test_plugins_params, test_file, test_shared_state)
        self.assertTrue(v)
        self.assertEqual(r, ("invalid final endif", []))

        expected_shared_state = {}
        expected_shared_state["lint-check-c-header-guards-state"] = "expecting-endif"
        expected_shared_state["lint-check-c-header-guards-first-ifndef-is"] = "__module_name__"
        expected_shared_state["lint-check-c-header-guards-last-endif"] = "#endif"

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintPost6(self):

        test_file = "test_file.txt"
        test_lines = ["#ifndef __module_name__", "#define __module_name__", "   ", "#endif // __module_name__"]
        test_plugins_params = {}
        test_shared_state = {}

        test_shared_state["lint-check-c-header-guards-state"] = "expecting-endif"
        test_shared_state["lint-check-c-header-guards-first-ifndef-is"] = "__module_name__"
        test_shared_state["lint-check-c-header-guards-last-endif"] = "#enduf // __module_name__"

        v, r = lint_c_check_header_guards.lint_post(test_plugins_params, test_file, test_shared_state)
        self.assertTrue(v)
        self.assertEqual(r, ("invalid final endif", []))

        expected_shared_state = {}
        expected_shared_state["lint-check-c-header-guards-state"] = "expecting-endif"
        expected_shared_state["lint-check-c-header-guards-first-ifndef-is"] = "__module_name__"
        expected_shared_state["lint-check-c-header-guards-last-endif"] = "#enduf // __module_name__"

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintPost7(self):

        test_file = "test_file.txt"
        test_lines = ["#ifndef __module_name__", "#define __module_name__", "   ", "#endif // __module_name__"]
        test_plugins_params = {}
        test_shared_state = {}

        test_shared_state["lint-check-c-header-guards-state"] = "expecting-endif"
        test_shared_state["lint-check-c-header-guards-first-ifndef-is"] = "__module_name__"
        test_shared_state["lint-check-c-header-guards-last-endif"] = "#endif // "

        v, r = lint_c_check_header_guards.lint_post(test_plugins_params, test_file, test_shared_state)
        self.assertTrue(v)
        self.assertEqual(r, ("invalid final endif", []))

        expected_shared_state = {}
        expected_shared_state["lint-check-c-header-guards-state"] = "expecting-endif"
        expected_shared_state["lint-check-c-header-guards-first-ifndef-is"] = "__module_name__"
        expected_shared_state["lint-check-c-header-guards-last-endif"] = "#endif // "

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintPost8(self):

        test_file = "test_file.txt"
        test_lines = ["#ifndef __module_name__", "#define __module_name__", "   ", "#endif // __module_name__"]
        test_plugins_params = {}
        test_shared_state = {}

        test_shared_state["lint-check-c-header-guards-state"] = "expecting-endif"
        test_shared_state["lint-check-c-header-guards-first-ifndef-is"] = "__module_name__"
        test_shared_state["lint-check-c-header-guards-last-endif"] = "#endif /* __module_name__ */"

        v, r = lint_c_check_header_guards.lint_post(test_plugins_params, test_file, test_shared_state)
        self.assertTrue(v)
        self.assertEqual(r, ("invalid final endif", []))

        expected_shared_state = {}
        expected_shared_state["lint-check-c-header-guards-state"] = "expecting-endif"
        expected_shared_state["lint-check-c-header-guards-first-ifndef-is"] = "__module_name__"
        expected_shared_state["lint-check-c-header-guards-last-endif"] = "#endif /* __module_name__ */"

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintPost9(self):

        test_file = "test_file.txt"
        test_lines = ["#ifndef __module_name__", "#define __module_name__", "   ", "#endif // __modula_name__"]
        test_plugins_params = {}
        test_shared_state = {}

        test_shared_state["lint-check-c-header-guards-state"] = "expecting-endif"
        test_shared_state["lint-check-c-header-guards-first-ifndef-is"] = "__module_name__"
        test_shared_state["lint-check-c-header-guards-last-endif"] = "#endif // __modula_name__"

        v, r = lint_c_check_header_guards.lint_post(test_plugins_params, test_file, test_shared_state)
        self.assertTrue(v)
        self.assertEqual(r, ("incorrect header guard detected (at the final endif) - expected [__module_name__], have [__modula_name__]", []))

        expected_shared_state = {}
        expected_shared_state["lint-check-c-header-guards-state"] = "expecting-endif"
        expected_shared_state["lint-check-c-header-guards-first-ifndef-is"] = "__module_name__"
        expected_shared_state["lint-check-c-header-guards-last-endif"] = "#endif // __modula_name__"

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintPost10(self):

        test_file = "test_file.txt"
        test_lines = ["#ifndef __module_name__", "#define __module_name__", "   ", "#endif // __module_name__"]
        test_plugins_params = {}
        test_shared_state = {}

        test_shared_state["lint-check-c-header-guards-state"] = "expecting-endif"
        test_shared_state["lint-check-c-header-guards-first-ifndef-is"] = "__module_name__"
        test_shared_state["lint-check-c-header-guards-last-endif"] = "#endif // __module_name__"

        v, r = lint_c_check_header_guards.lint_post(test_plugins_params, test_file, test_shared_state)
        self.assertTrue(v)
        self.assertEqual(r, None)

        expected_shared_state = {}
        expected_shared_state["lint-check-c-header-guards-state"] = "expecting-endif"
        expected_shared_state["lint-check-c-header-guards-first-ifndef-is"] = "__module_name__"
        expected_shared_state["lint-check-c-header-guards-last-endif"] = "#endif // __module_name__"

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintComplete(self):

        test_file = "test_file.txt"
        test_lines = ["   ", "#ifndef __module_name__", "#define __module_name__", "   ", "some other stuff in the middle", "   ", "#if 0", "#endif", "#endif // __module_name__", "   "]
        test_plugins_params = {}
        test_shared_state = {}

        expected_shared_state1 = {}
        expected_shared_state1["lint-check-c-header-guards-state"] = "expecting-ifndef"

        expected_shared_state2 = {}
        expected_shared_state2["lint-check-c-header-guards-state"] = "expecting-define"
        expected_shared_state2["lint-check-c-header-guards-first-ifndef-is"] = "__module_name__"

        expected_shared_state3 = {}
        expected_shared_state3["lint-check-c-header-guards-state"] = "expecting-endif"
        expected_shared_state3["lint-check-c-header-guards-first-ifndef-is"] = "__module_name__"

        expected_shared_state4 = {}
        expected_shared_state4["lint-check-c-header-guards-state"] = "expecting-endif"
        expected_shared_state4["lint-check-c-header-guards-first-ifndef-is"] = "__module_name__"

        expected_shared_state5 = {}
        expected_shared_state5["lint-check-c-header-guards-state"] = "expecting-endif"
        expected_shared_state5["lint-check-c-header-guards-first-ifndef-is"] = "__module_name__"

        expected_shared_state6 = {}
        expected_shared_state6["lint-check-c-header-guards-state"] = "expecting-endif"
        expected_shared_state6["lint-check-c-header-guards-first-ifndef-is"] = "__module_name__"

        expected_shared_state7 = {}
        expected_shared_state7["lint-check-c-header-guards-state"] = "expecting-endif"
        expected_shared_state7["lint-check-c-header-guards-first-ifndef-is"] = "__module_name__"

        expected_shared_state8 = {}
        expected_shared_state8["lint-check-c-header-guards-state"] = "expecting-endif"
        expected_shared_state8["lint-check-c-header-guards-first-ifndef-is"] = "__module_name__"
        expected_shared_state8["lint-check-c-header-guards-last-endif"] = "#endif"

        expected_shared_state9 = {}
        expected_shared_state9["lint-check-c-header-guards-state"] = "expecting-endif"
        expected_shared_state9["lint-check-c-header-guards-first-ifndef-is"] = "__module_name__"
        expected_shared_state9["lint-check-c-header-guards-last-endif"] = "#endif // __module_name__"

        expected_shared_state10 = {}
        expected_shared_state10["lint-check-c-header-guards-state"] = "expecting-endif"
        expected_shared_state10["lint-check-c-header-guards-first-ifndef-is"] = "__module_name__"
        expected_shared_state10["lint-check-c-header-guards-last-endif"] = "#endif // __module_name__"

        expected_shared_states = [expected_shared_state1, expected_shared_state2, expected_shared_state3, expected_shared_state4, expected_shared_state5, expected_shared_state6, expected_shared_state7, expected_shared_state8, expected_shared_state9, expected_shared_state10]

        v, r = lint_c_check_header_guards.lint_pre(test_plugins_params, test_file, test_shared_state, len(test_lines))
        self.assertTrue(v)
        self.assertEqual(r, None)

        for test_index in range(len(test_lines)):

            v, r = lint_c_check_header_guards.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, None)

            self.assertEqual(test_shared_state, expected_shared_states[test_index])

        v, r = lint_c_check_header_guards.lint_post(test_plugins_params, test_file, test_shared_state)
        self.assertTrue(v)
        self.assertEqual(r, None)

if __name__ == "__main__":
    unittest.main()
