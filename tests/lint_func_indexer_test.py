#!/usr/bin/env python3

import sys
import os
import shutil
import unittest

import mvtools_test_fixture
import path_utils

import lint_func_indexer

class LintFuncIndexerTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("lint_func_indexer_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testLintName(self):

        self.assertEqual(lint_func_indexer.lint_name(), "lint_func_indexer.py")

    def testLintDesc(self):

        self.assertEqual(lint_func_indexer.lint_desc(), "checks whether a proper indexing takes place inbetween two text patterns")

    def testLintPre1(self):

        test_file = "test_file.txt"
        test_lines = ["left1right", "left2right", "left3right"]
        test_plugins_params = {}
        test_shared_state = {}

        test_plugins_params["lint-func-indexer-param-left"] = ["left"]
        test_plugins_params["lint-func-indexer-param-right"] = ["right"]

        test_shared_state["lint-func-indexer-counter"] = 0

        v, r = lint_func_indexer.lint_pre(test_plugins_params, test_file, test_shared_state, len(test_lines))
        self.assertFalse(v)
        self.assertEqual(r, "shared state already contains {lint-func-indexer-counter}")

    def testLintPre2(self):

        test_file = "test_file.txt"
        test_lines = ["left1right", "left2right", "left3right"]
        test_plugins_params = {}
        test_shared_state = {}

        test_plugins_params["lint-func-indexer-param-right"] = ["right"]

        v, r = lint_func_indexer.lint_pre(test_plugins_params, test_file, test_shared_state, len(test_lines))
        self.assertFalse(v)
        self.assertEqual(r, "required parameter {lint-func-indexer-param-left} was not provided")

        expected_shared_state = {}
        expected_shared_state["lint-func-indexer-counter"] = 0

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintPre3(self):

        test_file = "test_file.txt"
        test_lines = ["left1right", "left2right", "left3right"]
        test_plugins_params = {}
        test_shared_state = {}

        test_plugins_params["lint-func-indexer-param-left"] = ["left"]

        v, r = lint_func_indexer.lint_pre(test_plugins_params, test_file, test_shared_state, len(test_lines))
        self.assertFalse(v)
        self.assertEqual(r, "required parameter {lint-func-indexer-param-right} was not provided")

        expected_shared_state = {}
        expected_shared_state["lint-func-indexer-counter"] = 0

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintPre4(self):

        test_file = "test_file.txt"
        test_lines = ["left1right", "left2right", "left3right"]
        test_plugins_params = {}
        test_shared_state = {}

        test_plugins_params["lint-func-indexer-param-left"] = []
        test_plugins_params["lint-func-indexer-param-right"] = ["right"]

        v, r = lint_func_indexer.lint_pre(test_plugins_params, test_file, test_shared_state, len(test_lines))
        self.assertFalse(v)
        self.assertEqual(r, "the parameter {lint-func-indexer-param-left} must contain at least one entry")

        expected_shared_state = {}
        expected_shared_state["lint-func-indexer-counter"] = 0

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintPre5(self):

        test_file = "test_file.txt"
        test_lines = ["left1right", "left2right", "left3right"]
        test_plugins_params = {}
        test_shared_state = {}

        test_plugins_params["lint-func-indexer-param-left"] = ["left"]
        test_plugins_params["lint-func-indexer-param-right"] = []

        v, r = lint_func_indexer.lint_pre(test_plugins_params, test_file, test_shared_state, len(test_lines))
        self.assertFalse(v)
        self.assertEqual(r, "the parameter {lint-func-indexer-param-right} must contain at least one entry")

        expected_shared_state = {}
        expected_shared_state["lint-func-indexer-counter"] = 0

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintPre6(self):

        test_file = "test_file.txt"
        test_lines = ["left1right", "left2right", "left3right"]
        test_plugins_params = {}
        test_shared_state = {}

        test_plugins_params["lint-func-indexer-param-left"] = [""]
        test_plugins_params["lint-func-indexer-param-right"] = ["right"]

        v, r = lint_func_indexer.lint_pre(test_plugins_params, test_file, test_shared_state, len(test_lines))
        self.assertFalse(v)
        self.assertEqual(r, "the parameter {lint-func-indexer-param-left} cannot be empty")

        expected_shared_state = {}
        expected_shared_state["lint-func-indexer-counter"] = 0

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintPre7(self):

        test_file = "test_file.txt"
        test_lines = ["left1right", "left2right", "left3right"]
        test_plugins_params = {}
        test_shared_state = {}

        test_plugins_params["lint-func-indexer-param-left"] = ["left"]
        test_plugins_params["lint-func-indexer-param-right"] = [""]

        v, r = lint_func_indexer.lint_pre(test_plugins_params, test_file, test_shared_state, len(test_lines))
        self.assertFalse(v)
        self.assertEqual(r, "the parameter {lint-func-indexer-param-right} cannot be empty")

        expected_shared_state = {}
        expected_shared_state["lint-func-indexer-counter"] = 0

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintPre8(self):

        test_file = "test_file.txt"
        test_lines = ["left1right", "left2right", "left3right"]
        test_plugins_params = {}
        test_shared_state = {}

        test_plugins_params["lint-func-indexer-param-left"] = ["left"]
        test_plugins_params["lint-func-indexer-param-right"] = ["right"]

        v, r = lint_func_indexer.lint_pre(test_plugins_params, test_file, test_shared_state, len(test_lines))
        self.assertTrue(v)
        self.assertEqual(r, None)

        expected_shared_state = {}
        expected_shared_state["lint-func-indexer-counter"] = 0

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintCycle1(self):

        test_file = "test_file.txt"
        test_lines = ["", "   ", ""]
        test_plugins_params = {}
        test_shared_state = {}

        test_plugins_params["lint-func-indexer-param-left"] = ["left"]
        test_plugins_params["lint-func-indexer-param-right"] = ["right"]

        test_shared_state["lint-func-indexer-counter"] = 0

        expected_shared_state1 = {}
        expected_shared_state1["lint-func-indexer-counter"] = 0

        expected_shared_state2 = {}
        expected_shared_state2["lint-func-indexer-counter"] = 0

        expected_shared_state3 = {}
        expected_shared_state3["lint-func-indexer-counter"] = 0

        expected_shared_states = [expected_shared_state1, expected_shared_state2, expected_shared_state3]

        for test_index in range(len(test_lines)):

            v, r = lint_func_indexer.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, None)

            self.assertEqual(test_shared_state, expected_shared_states[test_index])

    def testLintCycle2(self):

        test_file = "test_file.txt"
        test_lines = ["left1right", "left2right", "left3right"]
        test_plugins_params = {}
        test_shared_state = {}

        test_plugins_params["lint-func-indexer-param-left"] = ["left"]
        test_plugins_params["lint-func-indexer-param-right"] = ["right"]

        test_shared_state["lint-func-indexer-counter"] = 0

        expected_shared_state1 = {}
        expected_shared_state1["lint-func-indexer-counter"] = 1

        expected_shared_state2 = {}
        expected_shared_state2["lint-func-indexer-counter"] = 2

        expected_shared_state3 = {}
        expected_shared_state3["lint-func-indexer-counter"] = 3

        expected_shared_states = [expected_shared_state1, expected_shared_state2, expected_shared_state3]

        for test_index in range(len(test_lines)):

            v, r = lint_func_indexer.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, None)

            self.assertEqual(test_shared_state, expected_shared_states[test_index])

    def testLintCycle3(self):

        test_file = "test_file.txt"
        test_lines = ["left3right", "left2right", "left1right"]
        test_plugins_params = {}
        test_shared_state = {}

        test_plugins_params["lint-func-indexer-param-left"] = ["left"]
        test_plugins_params["lint-func-indexer-param-right"] = ["right"]

        test_shared_state["lint-func-indexer-counter"] = 0

        expected_shared_state1 = {}
        expected_shared_state1["lint-func-indexer-counter"] = 1

        expected_shared_state2 = {}
        expected_shared_state2["lint-func-indexer-counter"] = 2

        expected_shared_state3 = {}
        expected_shared_state3["lint-func-indexer-counter"] = 3

        expected_shared_states = [expected_shared_state1, expected_shared_state2, expected_shared_state3]

        expected_result1 = ("[test_file.txt:1]: expected index [1], have [3].", [(1, "left1right")])
        expected_result2 = None
        expected_result3 = ("[test_file.txt:3]: expected index [3], have [1].", [(3, "left3right")])

        expected_results = [expected_result1, expected_result2, expected_result3]

        for test_index in range(len(test_lines)):

            v, r = lint_func_indexer.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, expected_results[test_index])

            self.assertEqual(test_shared_state, expected_shared_states[test_index])

    def testLintCycle4(self):

        test_file = "test_file.txt"
        test_lines = ["leftright", "leftright", "leftright"]
        test_plugins_params = {}
        test_shared_state = {}

        test_plugins_params["lint-func-indexer-param-left"] = ["left"]
        test_plugins_params["lint-func-indexer-param-right"] = ["right"]

        test_shared_state["lint-func-indexer-counter"] = 0

        expected_shared_state1 = {}
        expected_shared_state1["lint-func-indexer-counter"] = 0

        expected_shared_state2 = {}
        expected_shared_state2["lint-func-indexer-counter"] = 0

        expected_shared_state3 = {}
        expected_shared_state3["lint-func-indexer-counter"] = 0

        expected_shared_states = [expected_shared_state1, expected_shared_state2, expected_shared_state3]

        for test_index in range(len(test_lines)):

            v, r = lint_func_indexer.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, None)

            self.assertEqual(test_shared_state, expected_shared_states[test_index])

    def testLintCycle5(self):

        test_file = "test_file.txt"
        test_lines = ["left1right", "leftX2right", "left3right"]
        test_plugins_params = {}
        test_shared_state = {}

        test_plugins_params["lint-func-indexer-param-left"] = ["left"]
        test_plugins_params["lint-func-indexer-param-right"] = ["right"]

        test_shared_state["lint-func-indexer-counter"] = 0

        expected_shared_state1 = {}
        expected_shared_state1["lint-func-indexer-counter"] = 1

        expected_shared_state2 = {}
        expected_shared_state2["lint-func-indexer-counter"] = 2

        expected_shared_state3 = {}
        expected_shared_state3["lint-func-indexer-counter"] = 3

        expected_shared_states = [expected_shared_state1, expected_shared_state2, expected_shared_state3]

        expected_result1 = None
        expected_result2 = ("[test_file.txt:2]: expected index [2], have [X2].", [(2, "left2right")])
        expected_result3 = None

        expected_results = [expected_result1, expected_result2, expected_result3]

        for test_index in range(len(test_lines)):

            v, r = lint_func_indexer.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, expected_results[test_index])

            self.assertEqual(test_shared_state, expected_shared_states[test_index])

    def testLintCycle6(self):

        test_file = "test_file.txt"
        test_lines = ["leftXright", "left3right", "left2right"]
        test_plugins_params = {}
        test_shared_state = {}

        test_plugins_params["lint-func-indexer-param-left"] = ["left"]
        test_plugins_params["lint-func-indexer-param-right"] = ["right"]

        test_shared_state["lint-func-indexer-counter"] = 0

        expected_shared_state1 = {}
        expected_shared_state1["lint-func-indexer-counter"] = 1

        expected_shared_state2 = {}
        expected_shared_state2["lint-func-indexer-counter"] = 2

        expected_shared_state3 = {}
        expected_shared_state3["lint-func-indexer-counter"] = 3

        expected_shared_states = [expected_shared_state1, expected_shared_state2, expected_shared_state3]

        expected_result1 = ("[test_file.txt:1]: expected index [1], have [X].", [(1, "left1right")])
        expected_result2 = ("[test_file.txt:2]: expected index [2], have [3].", [(2, "left2right")])
        expected_result3 = ("[test_file.txt:3]: expected index [3], have [2].", [(3, "left3right")])

        expected_results = [expected_result1, expected_result2, expected_result3]

        for test_index in range(len(test_lines)):

            v, r = lint_func_indexer.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, expected_results[test_index])

            self.assertEqual(test_shared_state, expected_shared_states[test_index])

    def testLintCycle7(self):

        test_file = "test_file.txt"
        test_lines = ["leftXright // needs fixing", "left0right", "leftZright // also needs fixing"]
        test_plugins_params = {}
        test_shared_state = {}

        test_plugins_params["lint-func-indexer-param-left"] = ["left"]
        test_plugins_params["lint-func-indexer-param-right"] = ["right", "right // needs fixing"]

        test_shared_state["lint-func-indexer-counter"] = 0

        expected_shared_state1 = {}
        expected_shared_state1["lint-func-indexer-counter"] = 1

        expected_shared_state2 = {}
        expected_shared_state2["lint-func-indexer-counter"] = 2

        expected_shared_state3 = {}
        expected_shared_state3["lint-func-indexer-counter"] = 2

        expected_shared_states = [expected_shared_state1, expected_shared_state2, expected_shared_state3]

        expected_result1 = ("[test_file.txt:1]: expected index [1], have [X].", [(1, "left1right // needs fixing")])
        expected_result2 = ("[test_file.txt:2]: expected index [2], have [0].", [(2, "left2right")])
        expected_result3 = None

        expected_results = [expected_result1, expected_result2, expected_result3]

        for test_index in range(len(test_lines)):

            v, r = lint_func_indexer.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, expected_results[test_index])

            self.assertEqual(test_shared_state, expected_shared_states[test_index])

    def testLintPost1(self):

        test_file = "test_file.txt"
        test_lines = ["left1right", "left2right", "left3right"]
        test_plugins_params = {}
        test_shared_state = {}

        test_plugins_params["lint-func-indexer-param-left"] = ["left"]
        test_plugins_params["lint-func-indexer-param-right"] = ["right"]

        test_shared_state["lint-func-indexer-counter"] = 0

        v, r = lint_func_indexer.lint_post(test_plugins_params, test_file, test_shared_state)
        self.assertTrue(v)
        self.assertEqual(r, None)

        expected_shared_state = {}
        expected_shared_state["lint-func-indexer-counter"] = 0

        self.assertEqual(test_shared_state, expected_shared_state)

    def testLintComplete(self):

        test_file = "test_file.txt"
        test_lines = ["left3right", "left2right", "left1right"]
        test_plugins_params = {}
        test_shared_state = {}

        test_plugins_params["lint-func-indexer-param-left"] = ["left"]
        test_plugins_params["lint-func-indexer-param-right"] = ["right"]

        expected_shared_state1 = {}
        expected_shared_state1["lint-func-indexer-counter"] = 1

        expected_shared_state2 = {}
        expected_shared_state2["lint-func-indexer-counter"] = 2

        expected_shared_state3 = {}
        expected_shared_state3["lint-func-indexer-counter"] = 3

        expected_shared_states = [expected_shared_state1, expected_shared_state2, expected_shared_state3]

        expected_result1 = ("[test_file.txt:1]: expected index [1], have [3].", [(1, "left1right")])
        expected_result2 = None
        expected_result3 = ("[test_file.txt:3]: expected index [3], have [1].", [(3, "left3right")])

        expected_results = [expected_result1, expected_result2, expected_result3]

        v, r = lint_func_indexer.lint_pre(test_plugins_params, test_file, test_shared_state, len(test_lines))
        self.assertTrue(v)
        self.assertEqual(r, None)

        for test_index in range(len(test_lines)):

            v, r = lint_func_indexer.lint_cycle(test_plugins_params, test_file, test_shared_state, test_index+1, test_lines[test_index])
            self.assertTrue(v)
            self.assertEqual(r, expected_results[test_index])

            self.assertEqual(test_shared_state, expected_shared_states[test_index])

        v, r = lint_func_indexer.lint_post(test_plugins_params, test_file, test_shared_state)
        self.assertTrue(v)
        self.assertEqual(r, None)

if __name__ == "__main__":
    unittest.main()
