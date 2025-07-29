#!/usr/bin/env python3

import sys
import os
import shutil
import unittest
from unittest import mock
from unittest.mock import patch

import mvtools_test_fixture
import create_and_write_file
import getcontents
import path_utils

import lint_test_helper
import lint_test_helper_sidekick

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

        self.helper_process_result_mock_flag = 0
        self.helper_process_result_mock_msg = ""
        self.helper_process_result_stashed_ptr = codelint.helper_process_result

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def helper_process_result_mock(self, r, report, autocorrect, lines_copy):

        if self.helper_process_result_mock_flag > 0:
            self.helper_process_result_mock_flag -= 1
            if self.helper_process_result_mock_flag == 0:
                return False, self.helper_process_result_mock_msg
        return self.helper_process_result_stashed_ptr(r, report, autocorrect, lines_copy)

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
        self.assertEqual(r, 0)

    def testHelperApplyPatches4(self):

        test_lines = ["first", "second", "third"]
        test_patches = [(1, "first-mod"), (2, "second-mod"), (3, "third-mod")]

        v, r = codelint.helper_apply_patches(test_lines, test_patches)
        self.assertTrue(v)
        self.assertEqual(r, 3)

        self.assertEqual(test_lines[0], "first-mod")
        self.assertEqual(test_lines[1], "second-mod")
        self.assertEqual(test_lines[2], "third-mod")

    def testHelperProcessResult1(self):

        test_report = []
        test_lines = ["first", "second", "third"]

        v, r = codelint.helper_process_result(None, test_report, True, test_lines)
        self.assertTrue(v)
        self.assertEqual(r, (0, 0))

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
        self.assertEqual(r, (1, 3))

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
        self.assertEqual(r, (1, 0))

        self.assertEqual(test_report, [(True, "content-msg")])
        self.assertEqual(test_lines[0], "first")
        self.assertEqual(test_lines[1], "second")
        self.assertEqual(test_lines[2], "third")

    def testHelperMakeExtraPluginEndStr(self):

        self.assertEqual(codelint.helper_make_extra_plugin_end_str(0, 0), "")
        self.assertEqual(codelint.helper_make_extra_plugin_end_str(0, 1), " (applied 1 patch)")
        self.assertEqual(codelint.helper_make_extra_plugin_end_str(0, 2), " (applied 2 patches)")
        self.assertEqual(codelint.helper_make_extra_plugin_end_str(1, 0), " (detected 1 finding)")
        self.assertEqual(codelint.helper_make_extra_plugin_end_str(2, 0), " (detected 2 findings)")
        self.assertEqual(codelint.helper_make_extra_plugin_end_str(1, 1), " (detected 1 finding, applied 1 patch)")
        self.assertEqual(codelint.helper_make_extra_plugin_end_str(2, 1), " (detected 2 findings, applied 1 patch)")
        self.assertEqual(codelint.helper_make_extra_plugin_end_str(1, 2), " (detected 1 finding, applied 2 patches)")
        self.assertEqual(codelint.helper_make_extra_plugin_end_str(2, 2), " (detected 2 findings, applied 2 patches)")

    def testCodelint1(self):

        test_file1 = path_utils.concat_path(self.test_dir, "file1.txt")
        create_and_write_file.create_file_contents(test_file1, "first-line\nsecond-line\nthird-line\nfourth-line\nfifth-line")

        codelint.plugin_table["lint-test-helper"] = (lint_test_helper, "")

        test_plugins = ["lint-test-helper"]
        test_plugins_params = {}
        test_filters = {}
        test_files = [test_file1]

        test_plugins_params["lint-test-helper-cycle-pattern-match"] = ["third-line"]
        test_plugins_params["lint-test-helper-cycle-pattern-replace"] = ["modified-third-line"]

        v, r = codelint.codelint(test_plugins, test_plugins_params, test_filters, [], test_files)
        self.assertFalse(v)
        self.assertEqual(r, ("autocorrect is not a bool", []))

        self.assertEqual(getcontents.getcontents(test_file1), "first-line\nsecond-line\nthird-line\nfourth-line\nfifth-line")

    def testCodelint2(self):

        test_file1 = path_utils.concat_path(self.test_dir, "file1.txt")
        create_and_write_file.create_file_contents(test_file1, "first-line\nsecond-line\nthird-line\nfourth-line\nfifth-line")

        codelint.plugin_table["lint-test-helper"] = (lint_test_helper, "")

        test_plugins = (lint_test_helper)
        test_plugins_params = {}
        test_filters = {}
        test_files = [test_file1]

        test_plugins_params["lint-test-helper-cycle-pattern-match"] = ["third-line"]
        test_plugins_params["lint-test-helper-cycle-pattern-replace"] = ["modified-third-line"]

        v, r = codelint.codelint(test_plugins, test_plugins_params, test_filters, True, test_files)
        self.assertFalse(v)
        self.assertEqual(r, ("plugins is not a list", []))

        self.assertEqual(getcontents.getcontents(test_file1), "first-line\nsecond-line\nthird-line\nfourth-line\nfifth-line")

    def testCodelint3(self):

        test_file1 = path_utils.concat_path(self.test_dir, "file1.txt")
        create_and_write_file.create_file_contents(test_file1, "first-line\nsecond-line\nthird-line\nfourth-line\nfifth-line")

        codelint.plugin_table["lint-test-helper"] = (lint_test_helper, "")

        test_plugins = ["lint-test-helper"]
        test_plugins_params = []
        test_filters = {}
        test_files = [test_file1]

        expected_report = []

        v, r = codelint.codelint(test_plugins, test_plugins_params, test_filters, False, test_files)
        self.assertFalse(v)
        self.assertEqual(r, ("plugins_params is not a dict", []))

    def testCodelint4(self):

        test_file1 = path_utils.concat_path(self.test_dir, "file1.txt")
        create_and_write_file.create_file_contents(test_file1, "first-line\nsecond-line\nthird-line\nfourth-line\nfifth-line")

        codelint.plugin_table["lint-test-helper"] = (lint_test_helper, "")

        test_plugins = ["lint-test-helper"]
        test_plugins_params = {}
        test_filters = {}
        test_files = (test_file1)

        test_plugins_params["lint-test-helper-cycle-pattern-match"] = ["third-line"]
        test_plugins_params["lint-test-helper-cycle-pattern-replace"] = ["modified-third-line"]

        v, r = codelint.codelint(test_plugins, test_plugins_params, test_filters, True, test_files)
        self.assertFalse(v)
        self.assertEqual(r, ("files is not a list", []))

        self.assertEqual(getcontents.getcontents(test_file1), "first-line\nsecond-line\nthird-line\nfourth-line\nfifth-line")

    def testCodelint5(self):

        test_file1 = path_utils.concat_path(self.test_dir, "file1.txt")
        create_and_write_file.create_file_contents(test_file1, "first-line\nsecond-line\nthird-line\nfourth-line\nfifth-line")

        codelint.plugin_table["lint-test-helper"] = (lint_test_helper, "")

        test_plugins = []
        test_plugins_params = {}
        test_filters = {}
        test_files = [test_file1]

        test_plugins_params["lint-test-helper-cycle-pattern-match"] = ["third-line"]
        test_plugins_params["lint-test-helper-cycle-pattern-replace"] = ["modified-third-line"]

        v, r = codelint.codelint(test_plugins, test_plugins_params, test_filters, True, test_files)
        self.assertFalse(v)
        self.assertEqual(r, ("No plugins selected", []))

        self.assertEqual(getcontents.getcontents(test_file1), "first-line\nsecond-line\nthird-line\nfourth-line\nfifth-line")

    def testCodelint6(self):

        test_file1 = path_utils.concat_path(self.test_dir, "file1.txt")
        create_and_write_file.create_file_contents(test_file1, "first-line\nsecond-line\nthird-line\nfourth-line\nfifth-line")

        codelint.plugin_table["lint-test-helper"] = (lint_test_helper, "")
        codelint.plugin_table["lint-test-helper-sidekick"] = (lint_test_helper_sidekick, "")

        test_plugins = [lint_test_helper, lint_test_helper_sidekick]
        test_plugins_params = {}
        test_filters = {}
        test_files = [test_file1]

        test_plugins_params["lint-test-helper-cycle-pattern-match"] = ["third-line"]
        test_plugins_params["lint-test-helper-cycle-pattern-replace"] = ["modified-third-line"]

        v, r = codelint.codelint(test_plugins, test_plugins_params, test_filters, True, test_files)
        self.assertFalse(v)
        self.assertEqual(r, ("Only one plugin is allowed to be executed with autocorrect turned on", []))

        self.assertEqual(getcontents.getcontents(test_file1), "first-line\nsecond-line\nthird-line\nfourth-line\nfifth-line")

    def testCodelint7(self):

        codelint.plugin_table["lint-test-helper"] = (lint_test_helper, "")

        test_plugins = ["lint-test-helper"]
        test_plugins_params = {}
        test_filters = {}
        test_files = []

        test_plugins_params["lint-test-helper-cycle-pattern-match"] = ["third-line"]
        test_plugins_params["lint-test-helper-cycle-pattern-replace"] = ["modified-third-line"]

        v, r = codelint.codelint(test_plugins, test_plugins_params, test_filters, True, test_files)
        self.assertFalse(v)
        self.assertEqual(r, ("No target files selected", []))

    def testCodelint8(self):

        test_file1 = path_utils.concat_path(self.test_dir, "file1.txt")

        codelint.plugin_table["lint-test-helper"] = (lint_test_helper, "")

        test_plugins = ["lint-test-helper"]
        test_plugins_params = {}
        test_filters = {}
        test_files = [test_file1]

        test_plugins_params["lint-test-helper-cycle-pattern-match"] = ["third-line"]
        test_plugins_params["lint-test-helper-cycle-pattern-replace"] = ["modified-third-line"]

        v, r = codelint.codelint(test_plugins, test_plugins_params, test_filters, True, test_files)
        self.assertFalse(v)
        self.assertEqual(r, ("File [%s] does not exist" % test_file1, []))

    def testCodelint9(self):

        test_file1 = path_utils.concat_path(self.test_dir, "file1.txt")
        os.mkdir(test_file1)

        codelint.plugin_table["lint-test-helper"] = (lint_test_helper, "")

        test_plugins = ["lint-test-helper"]
        test_plugins_params = {}
        test_filters = {}
        test_files = [test_file1]

        test_plugins_params["lint-test-helper-cycle-pattern-match"] = ["third-line"]
        test_plugins_params["lint-test-helper-cycle-pattern-replace"] = ["modified-third-line"]

        v, r = codelint.codelint(test_plugins, test_plugins_params, test_filters, True, test_files)
        self.assertFalse(v)
        self.assertEqual(r, ("File [%s] is a directory" % test_file1, []))

    def testCodelint10(self):

        test_file1 = path_utils.concat_path(self.test_dir, "file1.txt")
        create_and_write_file.create_file_contents(test_file1, "first-line\nsecond-line\nthird-line\nfourth-line\nfifth-line")

        codelint.plugin_table["lint-test-helper"] = (lint_test_helper, "")

        test_plugins = ["lint-test-helper"]
        test_plugins_params = {}
        test_filters = {}
        test_files = [test_file1]

        test_plugins_params["lint-test-helper-pre-fail"] = ["failing the pre step"]
        test_plugins_params["lint-test-helper-cycle-pattern-match"] = ["third-line"]
        test_plugins_params["lint-test-helper-cycle-pattern-replace"] = ["modified-third-line"]

        expected_report = []
        expected_report.append((False, "Processing [%s] - begin" % test_file1))
        expected_report.append((False, "Plugin: [lint_test_helper.py] - begin"))

        v, r = codelint.codelint(test_plugins, test_plugins_params, test_filters, True, test_files)
        self.assertFalse(v)
        self.assertEqual(r, ("Plugin [lint_test_helper.py] failed (pre): [failing the pre step]", expected_report))

        self.assertEqual(getcontents.getcontents(test_file1), "first-line\nsecond-line\nthird-line\nfourth-line\nfifth-line")

    def testCodelint11(self):

        test_file1 = path_utils.concat_path(self.test_dir, "file1.txt")
        create_and_write_file.create_file_contents(test_file1, "first-line\nsecond-line\nthird-line\nfourth-line\nfifth-line")

        codelint.plugin_table["lint-test-helper"] = (lint_test_helper, "")

        test_plugins = ["lint-test-helper"]
        test_plugins_params = {}
        test_filters = {}
        test_files = [test_file1]

        test_plugins_params["lint-test-helper-cycle-fail"] = ["failing the cycle step"]
        test_plugins_params["lint-test-helper-cycle-pattern-match"] = ["third-line"]
        test_plugins_params["lint-test-helper-cycle-pattern-replace"] = ["modified-third-line"]

        expected_report = []
        expected_report.append((False, "Processing [%s] - begin" % test_file1))
        expected_report.append((False, "Plugin: [lint_test_helper.py] - begin"))

        v, r = codelint.codelint(test_plugins, test_plugins_params, test_filters, True, test_files)
        self.assertFalse(v)
        self.assertEqual(r, ("Plugin [lint_test_helper.py] failed (cycle): [failing the cycle step]", expected_report))

        self.assertEqual(getcontents.getcontents(test_file1), "first-line\nsecond-line\nthird-line\nfourth-line\nfifth-line")

    def testCodelint12(self):

        test_file1 = path_utils.concat_path(self.test_dir, "file1.txt")
        create_and_write_file.create_file_contents(test_file1, "first-line\nsecond-line\nthird-line\nfourth-line\nfifth-line")

        codelint.plugin_table["lint-test-helper"] = (lint_test_helper, "")

        test_plugins = ["lint-test-helper"]
        test_plugins_params = {}
        test_filters = {}
        test_files = [test_file1]

        test_plugins_params["lint-test-helper-cycle-pattern-match"] = ["third-line"]
        test_plugins_params["lint-test-helper-cycle-pattern-replace"] = ["modified-third-line"]
        test_plugins_params["lint-test-helper-post-fail"] = ["failing the post step"]

        expected_report = []
        expected_report.append((False, "Processing [%s] - begin" % test_file1))
        expected_report.append((False, "Plugin: [lint_test_helper.py] - begin"))
        expected_report.append((True, "detected pattern [third-line] at line [3]"))

        v, r = codelint.codelint(test_plugins, test_plugins_params, test_filters, True, test_files)
        self.assertFalse(v)
        self.assertEqual(r, ("Plugin [lint_test_helper.py] failed (post): [failing the post step]", expected_report))

        self.assertEqual(getcontents.getcontents(test_file1), "first-line\nsecond-line\nthird-line\nfourth-line\nfifth-line")

    def testCodelint13(self):

        test_file1 = path_utils.concat_path(self.test_dir, "file1.txt")
        create_and_write_file.create_file_contents(test_file1, "first-line\nsecond-line\nthird-line\nfourth-line\nfifth-line")

        codelint.plugin_table["lint-test-helper"] = (lint_test_helper, "")

        test_plugins = ["lint-test-helper"]
        test_plugins_params = {}
        test_filters = {}
        test_files = [test_file1]

        test_plugins_params["lint-test-helper-cycle-pattern-match"] = ["third-line"]
        test_plugins_params["lint-test-helper-cycle-pattern-replace"] = ["modified-third-line"]

        expected_report = []
        expected_report.append((False, "Processing [%s] - begin" % test_file1))
        expected_report.append((False, "Plugin: [lint_test_helper.py] - begin"))

        self.helper_process_result_mock_flag = 1
        self.helper_process_result_mock_msg = "helper_process_result to fail artificially (cycle-result)"

        with patch("codelint.helper_process_result", wraps=self.helper_process_result_mock) as dummy:
            v, r = codelint.codelint(test_plugins, test_plugins_params, test_filters, True, test_files)
            self.assertFalse(v)
            self.assertEqual(r, ("Plugin [lint_test_helper.py] failed (cycle-result): [helper_process_result to fail artificially (cycle-result)]", expected_report))
            dummy.assert_called_once()

        self.assertEqual(getcontents.getcontents(test_file1), "first-line\nsecond-line\nthird-line\nfourth-line\nfifth-line")

    def testCodelint14(self):

        test_file1 = path_utils.concat_path(self.test_dir, "file1.txt")
        create_and_write_file.create_file_contents(test_file1, "sole-line")

        codelint.plugin_table["lint-test-helper"] = (lint_test_helper, "")

        test_plugins = ["lint-test-helper"]
        test_plugins_params = {}
        test_filters = {}
        test_files = [test_file1]

        test_plugins_params["lint-test-helper-cycle-pattern-match"] = ["sole-line"]
        test_plugins_params["lint-test-helper-cycle-pattern-replace"] = ["modified-sole-line"]

        expected_report = []
        expected_report.append((False, "Processing [%s] - begin" % test_file1))
        expected_report.append((False, "Plugin: [lint_test_helper.py] - begin"))
        expected_report.append((True, "detected pattern [sole-line] at line [1]"))

        self.helper_process_result_mock_flag = 2
        self.helper_process_result_mock_msg = "helper_process_result to fail artificially (post-result)"

        with patch("codelint.helper_process_result", wraps=self.helper_process_result_mock) as dummy:
            v, r = codelint.codelint(test_plugins, test_plugins_params, test_filters, True, test_files)
            self.assertFalse(v)
            self.assertEqual(r, ("Plugin [lint_test_helper.py] failed (post-result): [helper_process_result to fail artificially (post-result)]", expected_report))
            dummy.assert_called()

        self.assertEqual(getcontents.getcontents(test_file1), "sole-line")

    def testCodelint15(self):

        test_file1 = path_utils.concat_path(self.test_dir, "file1.txt")
        create_and_write_file.create_file_contents(test_file1, "first-line\nsecond-line\nthird-line\nfourth-line\nfifth-line")

        codelint.plugin_table["lint-test-helper"] = (lint_test_helper, "")

        test_plugins = ["lint-test-helper"]
        test_plugins_params = {}
        test_filters = {}
        test_files = [test_file1]

        test_plugins_params["lint-test-helper-cycle-pattern-match"] = ["third-line"]
        test_plugins_params["lint-test-helper-cycle-pattern-replace"] = ["modified-third-line"]

        expected_report = []
        expected_report.append((False, "Processing [%s] - begin" % test_file1))
        expected_report.append((False, "Plugin: [lint_test_helper.py] - begin"))
        expected_report.append((True, "detected pattern [third-line] at line [3]"))
        expected_report.append((False, "Plugin: [lint_test_helper.py] - end (detected 1 finding, applied 1 patch)"))
        expected_report.append((False, "Processing [%s] - end" % test_file1))

        v, r = codelint.codelint(test_plugins, test_plugins_params, test_filters, True, test_files)
        self.assertTrue(v)
        self.assertEqual(r, expected_report)

        self.assertEqual(getcontents.getcontents(test_file1), "first-line\nsecond-line\nmodified-third-line\nfourth-line\nfifth-line")

    def testCodelint16(self):

        test_file1 = path_utils.concat_path(self.test_dir, "file1.txt")
        create_and_write_file.create_file_contents(test_file1, "first-line\nsecond-line\nthird-line\nfourth-line\nfifth-line")

        codelint.plugin_table["lint-test-helper"] = (lint_test_helper, "")

        test_plugins = ["lint-test-helper"]
        test_plugins_params = {}
        test_filters = {}
        test_files = [test_file1]

        test_plugins_params["lint-test-helper-cycle-pattern-match"] = ["third-line"]
        test_plugins_params["lint-test-helper-cycle-pattern-replace"] = ["modified-third-line"]

        expected_report = []
        expected_report.append((False, "Processing [%s] - begin" % test_file1))
        expected_report.append((False, "Plugin: [lint_test_helper.py] - begin"))
        expected_report.append((True, "detected pattern [third-line] at line [3]"))
        expected_report.append((False, "Plugin: [lint_test_helper.py] - end (detected 1 finding)"))
        expected_report.append((False, "Processing [%s] - end" % test_file1))

        v, r = codelint.codelint(test_plugins, test_plugins_params, test_filters, False, test_files)
        self.assertTrue(v)
        self.assertEqual(r, expected_report)

        self.assertEqual(getcontents.getcontents(test_file1), "first-line\nsecond-line\nthird-line\nfourth-line\nfifth-line")

    def testCodelint17(self):

        test_file1 = path_utils.concat_path(self.test_dir, "file1.txt")
        create_and_write_file.create_file_contents(test_file1, "first-line\nsecond-line\nthird-line\nfourth-line\nfifth-line")

        codelint.plugin_table["lint-test-helper"] = (lint_test_helper, "")

        test_plugins = ["lint-test-helper"]
        test_plugins_params = {}
        test_filters = {}
        test_files = [test_file1]

        test_plugins_params["lint-test-helper-cycle-pattern-match"] = ["third-line"]
        test_plugins_params["lint-test-helper-cycle-pattern-replace"] = ["modified-third-line"]
        test_plugins_params["lint-test-helper-pre-verify-filename"] = [path_utils.basename_filtered(test_file1)]

        expected_report = []
        expected_report.append((False, "Processing [%s] - begin" % test_file1))
        expected_report.append((False, "Plugin: [lint_test_helper.py] - begin"))
        expected_report.append((True, "detected pattern [third-line] at line [3]"))
        expected_report.append((False, "Plugin: [lint_test_helper.py] - end (detected 1 finding)"))
        expected_report.append((False, "Processing [%s] - end" % test_file1))

        v, r = codelint.codelint(test_plugins, test_plugins_params, test_filters, False, test_files)
        self.assertTrue(v)
        self.assertEqual(r, expected_report)

        self.assertEqual(getcontents.getcontents(test_file1), "first-line\nsecond-line\nthird-line\nfourth-line\nfifth-line")

    def testCodelint18(self):

        test_file1 = path_utils.concat_path(self.test_dir, "file1.txt")
        create_and_write_file.create_file_contents(test_file1, "first-line\nsecond-line\nthird-line\nfourth-line\nfifth-line")

        codelint.plugin_table["lint-test-helper"] = (lint_test_helper, "")

        test_plugins = ["lint-test-helper"]
        test_plugins_params = {}
        test_filters = {}
        test_files = [test_file1]

        test_plugins_params["lint-test-helper-cycle-pattern-match"] = ["third-line"]
        test_plugins_params["lint-test-helper-cycle-pattern-replace"] = ["modified-third-line"]
        test_plugins_params["lint-test-helper-cycle-verify-filename"] = [path_utils.basename_filtered(test_file1)]

        expected_report = []
        expected_report.append((False, "Processing [%s] - begin" % test_file1))
        expected_report.append((False, "Plugin: [lint_test_helper.py] - begin"))
        expected_report.append((True, "detected pattern [third-line] at line [3]"))
        expected_report.append((False, "Plugin: [lint_test_helper.py] - end (detected 1 finding)"))
        expected_report.append((False, "Processing [%s] - end" % test_file1))

        v, r = codelint.codelint(test_plugins, test_plugins_params, test_filters, False, test_files)
        self.assertTrue(v)
        self.assertEqual(r, expected_report)

        self.assertEqual(getcontents.getcontents(test_file1), "first-line\nsecond-line\nthird-line\nfourth-line\nfifth-line")

    def testCodelint19(self):

        test_file1 = path_utils.concat_path(self.test_dir, "file1.txt")
        create_and_write_file.create_file_contents(test_file1, "first-line\nsecond-line\nthird-line\nfourth-line\nfifth-line")

        codelint.plugin_table["lint-test-helper"] = (lint_test_helper, "")

        test_plugins = ["lint-test-helper"]
        test_plugins_params = {}
        test_filters = {}
        test_files = [test_file1]

        test_plugins_params["lint-test-helper-cycle-pattern-match"] = ["third-line"]
        test_plugins_params["lint-test-helper-cycle-pattern-replace"] = ["modified-third-line"]
        test_plugins_params["lint-test-helper-post-verify-filename"] = [path_utils.basename_filtered(test_file1)]

        expected_report = []
        expected_report.append((False, "Processing [%s] - begin" % test_file1))
        expected_report.append((False, "Plugin: [lint_test_helper.py] - begin"))
        expected_report.append((True, "detected pattern [third-line] at line [3]"))
        expected_report.append((False, "Plugin: [lint_test_helper.py] - end (detected 1 finding)"))
        expected_report.append((False, "Processing [%s] - end" % test_file1))

        v, r = codelint.codelint(test_plugins, test_plugins_params, test_filters, False, test_files)
        self.assertTrue(v)
        self.assertEqual(r, expected_report)

        self.assertEqual(getcontents.getcontents(test_file1), "first-line\nsecond-line\nthird-line\nfourth-line\nfifth-line")

    def testCodelint20(self):

        test_file1 = path_utils.concat_path(self.test_dir, "file1.txt")
        create_and_write_file.create_file_contents(test_file1, "first-line\nsecond-line\nthird-line\nfourth-line\nfifth-line")

        codelint.plugin_table["lint-test-helper"] = (lint_test_helper, "")

        test_plugins = ["lint-test-helper"]
        test_plugins_params = {}
        test_filters = {}
        test_files = [test_file1]

        test_plugins_params["lint-test-helper-pre-write-to-shared-state"] = ["pre-to-cycle-to-post-connection-test"]
        test_plugins_params["lint-test-helper-cycle-verify-shared-state"] = ["pre-to-cycle-to-post-connection-test"]
        test_plugins_params["lint-test-helper-cycle-pattern-match"] = ["third-line"]
        test_plugins_params["lint-test-helper-cycle-pattern-replace"] = ["modified-third-line"]
        test_plugins_params["lint-test-helper-post-verify-shared-state"] = ["pre-to-cycle-to-post-connection-test"]

        expected_report = []
        expected_report.append((False, "Processing [%s] - begin" % test_file1))
        expected_report.append((False, "Plugin: [lint_test_helper.py] - begin"))
        expected_report.append((True, "detected pattern [third-line] at line [3]"))
        expected_report.append((False, "Plugin: [lint_test_helper.py] - end (detected 1 finding)"))
        expected_report.append((False, "Processing [%s] - end" % test_file1))

        v, r = codelint.codelint(test_plugins, test_plugins_params, test_filters, False, test_files)
        self.assertTrue(v)
        self.assertEqual(r, expected_report)

        self.assertEqual(getcontents.getcontents(test_file1), "first-line\nsecond-line\nthird-line\nfourth-line\nfifth-line")

    def testCodelint21(self):

        test_file1 = path_utils.concat_path(self.test_dir, "file1.txt")
        create_and_write_file.create_file_contents(test_file1, "first-line\nsecond-line\nthird-line\nfourth-line\nfifth-line")

        codelint.plugin_table["lint-test-helper"] = (lint_test_helper, "")

        test_plugins = ["lint-test-helper"]
        test_plugins_params = {}
        test_filters = {}
        test_files = [test_file1]

        test_plugins_params["lint-test-helper-pre-lines-check"] = ["5"]
        test_plugins_params["lint-test-helper-cycle-pattern-match"] = ["third-line"]
        test_plugins_params["lint-test-helper-cycle-pattern-replace"] = ["modified-third-line"]

        expected_report = []
        expected_report.append((False, "Processing [%s] - begin" % test_file1))
        expected_report.append((False, "Plugin: [lint_test_helper.py] - begin"))
        expected_report.append((True, "detected pattern [third-line] at line [3]"))
        expected_report.append((False, "Plugin: [lint_test_helper.py] - end (detected 1 finding)"))
        expected_report.append((False, "Processing [%s] - end" % test_file1))

        v, r = codelint.codelint(test_plugins, test_plugins_params, test_filters, False, test_files)
        self.assertTrue(v)
        self.assertEqual(r, expected_report)

        self.assertEqual(getcontents.getcontents(test_file1), "first-line\nsecond-line\nthird-line\nfourth-line\nfifth-line")

    def testCodelint22(self):

        test_file1 = path_utils.concat_path(self.test_dir, "file1.txt")
        create_and_write_file.create_file_contents(test_file1, "first-line\nsecond-line\nthird-line\nfourth-line\nfifth-line")

        codelint.plugin_table["lint-test-helper"] = (lint_test_helper, "")

        test_plugins = ["lint-test-helper"]
        test_plugins_params = {}
        test_filters = {}
        test_files = [test_file1]

        test_plugins_params["lint-test-helper-cycle-line-idx-check"] = ["4"]
        test_plugins_params["lint-test-helper-cycle-line-content-check"] = ["fourth-line"]
        test_plugins_params["lint-test-helper-cycle-pattern-match"] = ["third-line"]
        test_plugins_params["lint-test-helper-cycle-pattern-replace"] = ["modified-third-line"]

        expected_report = []
        expected_report.append((False, "Processing [%s] - begin" % test_file1))
        expected_report.append((False, "Plugin: [lint_test_helper.py] - begin"))
        expected_report.append((True, "detected pattern [third-line] at line [3]"))
        expected_report.append((False, "Plugin: [lint_test_helper.py] - end (detected 1 finding)"))
        expected_report.append((False, "Processing [%s] - end" % test_file1))

        v, r = codelint.codelint(test_plugins, test_plugins_params, test_filters, False, test_files)
        self.assertTrue(v)
        self.assertEqual(r, expected_report)

        self.assertEqual(getcontents.getcontents(test_file1), "first-line\nsecond-line\nthird-line\nfourth-line\nfifth-line")

    def testCodelint23(self):

        test_file1 = path_utils.concat_path(self.test_dir, "file1.txt")
        create_and_write_file.create_file_contents(test_file1, "first-line\nsecond-line\nthird-line\nfourth-line\nfifth-line")

        codelint.plugin_table["lint-test-helper"] = (lint_test_helper, "")

        test_plugins = ["lint-test-helper"]
        test_plugins_params = {}
        test_filters = {}
        test_files = [test_file1]

        test_plugins_params["lint-test-helper-post-tag-line-index"] = ["1"]
        test_plugins_params["lint-test-helper-post-tag-line-content"] = ["modified-header"]

        expected_report = []
        expected_report.append((False, "Processing [%s] - begin" % test_file1))
        expected_report.append((False, "Plugin: [lint_test_helper.py] - begin"))
        expected_report.append((True, "tagging line [1] with [modified-header]"))
        expected_report.append((False, "Plugin: [lint_test_helper.py] - end (detected 1 finding, applied 1 patch)"))
        expected_report.append((False, "Processing [%s] - end" % test_file1))

        v, r = codelint.codelint(test_plugins, test_plugins_params, test_filters, True, test_files)
        self.assertTrue(v)
        self.assertEqual(r, expected_report)

        self.assertEqual(getcontents.getcontents(test_file1), "modified-header\nsecond-line\nthird-line\nfourth-line\nfifth-line")

    def testCodelint24(self):

        test_file1 = path_utils.concat_path(self.test_dir, "file1.txt")
        create_and_write_file.create_file_contents(test_file1, "first-line\nsecond-line\nthird-line\nfourth-line\nfifth-line")

        codelint.plugin_table["lint-test-helper"] = (lint_test_helper, "")

        test_plugins = ["lint-test-helper"]
        test_plugins_params = {}
        test_filters = {}
        test_files = [test_file1]

        test_plugins_params["lint-test-helper-post-tag-line-index"] = ["1"]
        test_plugins_params["lint-test-helper-post-tag-line-content"] = ["modified-header"]

        expected_report = []
        expected_report.append((False, "Processing [%s] - begin" % test_file1))
        expected_report.append((False, "Plugin: [lint_test_helper.py] - begin"))
        expected_report.append((True, "tagging line [1] with [modified-header]"))
        expected_report.append((False, "Plugin: [lint_test_helper.py] - end (detected 1 finding)"))
        expected_report.append((False, "Processing [%s] - end" % test_file1))

        v, r = codelint.codelint(test_plugins, test_plugins_params, test_filters, False, test_files)
        self.assertTrue(v)
        self.assertEqual(r, expected_report)

        self.assertEqual(getcontents.getcontents(test_file1), "first-line\nsecond-line\nthird-line\nfourth-line\nfifth-line")

    def testCodelint25(self):

        test_file1 = path_utils.concat_path(self.test_dir, "file1.txt")
        test_file2 = path_utils.concat_path(self.test_dir, "file2.txt")

        create_and_write_file.create_file_contents(test_file1, "first-line\nsecond-line\nthird-line\nfourth-line\nfifth-line")
        create_and_write_file.create_file_contents(test_file2, "some-stuff\nsome-other-stuff")

        codelint.plugin_table["lint-test-helper"] = (lint_test_helper, "")
        codelint.plugin_table["lint-test-helper-sidekick"] = (lint_test_helper_sidekick, "")

        test_plugins = ["lint-test-helper", "lint-test-helper-sidekick"]
        test_plugins_params = {}
        test_filters = {}
        test_files = [test_file1, test_file2]

        test_plugins_params["lint-test-helper-cycle-pattern-match"] = ["third-line"]
        test_plugins_params["lint-test-helper-cycle-pattern-replace"] = ["modified-third-line"]

        test_plugins_params["lint-test-helper-sidekick-cycle-pattern-match"] = ["some-other-stuff"]
        test_plugins_params["lint-test-helper-sidekick-cycle-pattern-replace"] = ["modified-some-other-stuff"]

        expected_report = []
        expected_report.append((False, "Processing [%s] - begin" % test_file1))
        expected_report.append((False, "Plugin: [lint_test_helper.py] - begin"))
        expected_report.append((True, "detected pattern [third-line] at line [3]"))
        expected_report.append((False, "Plugin: [lint_test_helper.py] - end (detected 1 finding)"))
        expected_report.append((False, "Plugin: [lint_test_helper_sidekick.py] - begin"))
        expected_report.append((False, "Plugin: [lint_test_helper_sidekick.py] - end (detected 1 finding)"))
        expected_report.append((False, "Processing [%s] - end" % test_file1))
        expected_report.append((False, "Processing [%s] - begin" % test_file2))
        expected_report.append((False, "Plugin: [lint_test_helper.py] - begin"))
        expected_report.append((False, "Plugin: [lint_test_helper.py] - end"))
        expected_report.append((False, "Plugin: [lint_test_helper_sidekick.py] - begin"))
        expected_report.append((True, "(sidekick) detected pattern [some-other-stuff] at line [2]"))
        expected_report.append((False, "Plugin: [lint_test_helper_sidekick.py] - end (detected 1 finding)"))
        expected_report.append((False, "Processing [%s] - end" % test_file2))

        v, r = codelint.codelint(test_plugins, test_plugins_params, test_filters, False, test_files)
        self.assertTrue(v)
        self.assertEqual(r, expected_report)

        self.assertEqual(getcontents.getcontents(test_file1), "first-line\nsecond-line\nthird-line\nfourth-line\nfifth-line")
        self.assertEqual(getcontents.getcontents(test_file2), "some-stuff\nsome-other-stuff")

if __name__ == "__main__":
    unittest.main()
