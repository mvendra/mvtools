#!/usr/bin/env python3

import sys
import os
import shutil
import unittest

import mvtools_test_fixture
import create_and_write_file
import getcontents
import path_utils

import lint_test_helper

import codelint

class CodeLintTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("codelint_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testHelperValidateMsgpatchReturn1(self):

        v, r = codelint.helper_validate_msgpatch_return(123, [])
        self.assertFalse(v)
        self.assertEqual(r, "invalid result return: msg is not a str")

    def testHelperValidateMsgpatchReturn2(self):

        v, r = codelint.helper_validate_msgpatch_return("error-msg", ())
        self.assertFalse(v)
        self.assertEqual(r, "invalid result return: patches is not a list")

    def testHelperValidateMsgpatchReturn3(self):

        v, r = codelint.helper_validate_msgpatch_return("error-msg", [123])
        self.assertFalse(v)
        self.assertEqual(r, "invalid result return: patches entry is not a tuple")

    def testHelperValidateMsgpatchReturn4(self):

        v, r = codelint.helper_validate_msgpatch_return("error-msg", [("1", "contents")])
        self.assertFalse(v)
        self.assertEqual(r, "invalid result return: patches entry, first tuple entry is not an int")

    def testHelperValidateMsgpatchReturn5(self):

        v, r = codelint.helper_validate_msgpatch_return("error-msg", [(1, 123)])
        self.assertFalse(v)
        self.assertEqual(r, "invalid result return: patches entry, second tuple entry is not a str")

    def testHelperValidateMsgpatchReturn6(self):

        v, r = codelint.helper_validate_msgpatch_return("error-msg", [])
        self.assertTrue(v)
        self.assertEqual(r, None)

    def testHelperValidateMsgpatchReturn7(self):

        v, r = codelint.helper_validate_msgpatch_return("error-msg", [(1, "contents")])
        self.assertTrue(v)
        self.assertEqual(r, None)

    def testHelperApplyPatches1(self):

        test_lines = ["first", "second", "third"]
        test_patches = [(1, "first-mod"), (2, "second-mod"), (4, "third-mod")]

        v, r = codelint.helper_apply_patches(test_lines, test_patches)
        self.assertFalse(v)
        self.assertEqual(r, "patch index [4] is out of bounds [3]")

    def testHelperApplyPatches2(self):

        test_lines = ["first", "second", "third"]
        test_patches = [(0, "first-mod"), (2, "second-mod"), (3, "third-mod")]

        v, r = codelint.helper_apply_patches(test_lines, test_patches)
        self.assertFalse(v)
        self.assertEqual(r, "patch index is zero (invalid base)")

    def testHelperApplyPatches3(self):

        test_lines = []
        test_patches = []

        v, r = codelint.helper_apply_patches(test_lines, test_patches)
        self.assertTrue(v)
        self.assertEqual(r, None)

    def testHelperApplyPatches4(self):

        test_lines = ["first", "second", "third"]
        test_patches = [(1, "first-mod"), (2, "second-mod"), (3, "third-mod")]

        v, r = codelint.helper_apply_patches(test_lines, test_patches)
        self.assertTrue(v)
        self.assertEqual(r, None)

        self.assertEqual(test_lines[0], "first-mod")
        self.assertEqual(test_lines[1], "second-mod")
        self.assertEqual(test_lines[2], "third-mod")

    def testHelperProcessResult1(self):

        test_report = []
        test_lines = ["first", "second", "third"]

        v, r = codelint.helper_process_result(None, test_report, True, test_lines)
        self.assertTrue(v)
        self.assertEqual(r, None)

        self.assertEqual(test_report, [])
        self.assertEqual(test_lines[0], "first")
        self.assertEqual(test_lines[1], "second")
        self.assertEqual(test_lines[2], "third")

    def testHelperProcessResult2(self):

        test_msg = 123
        test_patches = [(1, "first-mod"), (2, "second-mod"), (3, "third-mod")]
        test_report = []
        test_lines = ["first", "second", "third"]

        v, r = codelint.helper_process_result((test_msg, test_patches), test_report, True, test_lines)
        self.assertFalse(v)
        self.assertEqual(r, "invalid result return: msg is not a str")

    def testHelperProcessResult3(self):

        test_msg = "content-msg"
        test_patches = ((1, "first-mod"), (2, "second-mod"), (3, "third-mod"))
        test_report = []
        test_lines = ["first", "second", "third"]

        v, r = codelint.helper_process_result((test_msg, test_patches), test_report, True, test_lines)
        self.assertFalse(v)
        self.assertEqual(r, "invalid result return: patches is not a list")

        self.assertEqual(test_report, [])
        self.assertEqual(test_lines[0], "first")
        self.assertEqual(test_lines[1], "second")
        self.assertEqual(test_lines[2], "third")

    def testHelperProcessResult4(self):

        test_msg = "content-msg"
        test_patches = [[1, "first-mod"], [2, "second-mod"], [3, "third-mod"]]
        test_report = []
        test_lines = ["first", "second", "third"]

        v, r = codelint.helper_process_result((test_msg, test_patches), test_report, True, test_lines)
        self.assertFalse(v)
        self.assertEqual(r, "invalid result return: patches entry is not a tuple")

        self.assertEqual(test_report, [])
        self.assertEqual(test_lines[0], "first")
        self.assertEqual(test_lines[1], "second")
        self.assertEqual(test_lines[2], "third")

    def testHelperProcessResult5(self):

        test_msg = "content-msg"
        test_patches = [("1", "first-mod"), ("2", "second-mod"), ("3", "third-mod")]
        test_report = []
        test_lines = ["first", "second", "third"]

        v, r = codelint.helper_process_result((test_msg, test_patches), test_report, True, test_lines)
        self.assertFalse(v)
        self.assertEqual(r, "invalid result return: patches entry, first tuple entry is not an int")

        self.assertEqual(test_report, [])
        self.assertEqual(test_lines[0], "first")
        self.assertEqual(test_lines[1], "second")
        self.assertEqual(test_lines[2], "third")

    def testHelperProcessResult6(self):

        test_msg = "content-msg"
        test_patches = [(1, 123), (2, "second-mod"), (3, "third-mod")]
        test_report = []
        test_lines = ["first", "second", "third"]

        v, r = codelint.helper_process_result((test_msg, test_patches), test_report, True, test_lines)
        self.assertFalse(v)
        self.assertEqual(r, "invalid result return: patches entry, second tuple entry is not a str")

        self.assertEqual(test_report, [])
        self.assertEqual(test_lines[0], "first")
        self.assertEqual(test_lines[1], "second")
        self.assertEqual(test_lines[2], "third")

    def testHelperProcessResult7(self):

        test_msg = "content-msg"
        test_patches = [(4, "first-mod"), (2, "second-mod"), (3, "third-mod")]
        test_report = []
        test_lines = ["first", "second", "third"]

        v, r = codelint.helper_process_result((test_msg, test_patches), test_report, True, test_lines)
        self.assertFalse(v)
        self.assertEqual(r, "patch index [4] is out of bounds [3]")

        self.assertEqual(test_report, [(True, "content-msg")])
        self.assertEqual(test_lines[0], "first")
        self.assertEqual(test_lines[1], "second")
        self.assertEqual(test_lines[2], "third")

    def testHelperProcessResult8(self):

        test_msg = "content-msg"
        test_patches = [(0, "first-mod"), (2, "second-mod"), (3, "third-mod")]
        test_report = []
        test_lines = ["first", "second", "third"]

        v, r = codelint.helper_process_result((test_msg, test_patches), test_report, True, test_lines)
        self.assertFalse(v)
        self.assertEqual(r, "patch index is zero (invalid base)")

        self.assertEqual(test_report, [(True, "content-msg")])
        self.assertEqual(test_lines[0], "first")
        self.assertEqual(test_lines[1], "second")
        self.assertEqual(test_lines[2], "third")

    def testHelperProcessResult9(self):

        test_msg = "content-msg"
        test_patches = [(1, "first-mod"), (2, "second-mod"), (3, "third-mod")]
        test_report = []
        test_lines = ["first", "second", "third"]

        v, r = codelint.helper_process_result((test_msg, test_patches), test_report, True, test_lines)
        self.assertTrue(v)
        self.assertEqual(r, None)

        self.assertEqual(test_report, [(True, "content-msg")])
        self.assertEqual(test_lines[0], "first-mod")
        self.assertEqual(test_lines[1], "second-mod")
        self.assertEqual(test_lines[2], "third-mod")

    def testHelperProcessResult10(self):

        test_msg = "content-msg"
        test_patches = [(1, "first-mod"), (2, "second-mod"), (3, "third-mod")]
        test_report = []
        test_lines = ["first", "second", "third"]

        v, r = codelint.helper_process_result((test_msg, test_patches), test_report, False, test_lines)
        self.assertTrue(v)
        self.assertEqual(r, None)

        self.assertEqual(test_report, [(True, "content-msg")])
        self.assertEqual(test_lines[0], "first")
        self.assertEqual(test_lines[1], "second")
        self.assertEqual(test_lines[2], "third")

    def testCodelintX(self): # mvtodo

        test_file1 = path_utils.concat_path(self.test_dir, "file1.txt")
        create_and_write_file.create_file_contents(test_file1, "first-line\nsecond-line\nthird-line\nfourth-line\nfifth-line")

        test_plugins = [lint_test_helper]
        test_plugins_params = {}
        test_files = [test_file1]

        test_plugins_params["lint-test-helper-cycle-pattern-match"] = "third-line"
        test_plugins_params["lint-test-helper-cycle-pattern-replace"] = "modified-third-line"

        expected_report = []
        expected_report.append((False, "Processing [%s] - begin" % test_file1))
        expected_report.append((False, "Plugin: [lint_test_helper.py] - begin"))
        expected_report.append((True, "detected pattern [third-line] at line [3]"))
        expected_report.append((False, "Plugin: [lint_test_helper.py] - end"))
        expected_report.append((False, "Processing [%s] - end" % test_file1))

        v, r = codelint.codelint(test_plugins, test_plugins_params, True, test_files)
        self.assertTrue(v)
        self.assertEqual(r, expected_report)

        self.assertEqual(getcontents.getcontents(test_file1), "first-line\nsecond-line\nmodified-third-line\nfourth-line\nfifth-line")

if __name__ == "__main__":
    unittest.main()
