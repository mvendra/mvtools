#!/usr/bin/env python3

import sys
import os
import shutil
import unittest
from unittest import mock
from unittest.mock import patch

import mvtools_test_fixture

import path_utils
import mv_wrapper
import generic_run

class MvWrapperTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("mv_wrapper_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        self.result_obj = generic_run.run_cmd_result(None, None, None, None)

        self.path1 = path_utils.concat_path(self.test_dir, "path1")
        self.path2 = path_utils.concat_path(self.test_dir, "path2")
        self.rel_path1 = path_utils.concat_path(self.test_dir, "..", path_utils.basename_filtered(self.test_dir), "path1")
        self.rel_path2 = path_utils.concat_path(self.test_dir, "..", path_utils.basename_filtered(self.test_dir), "path2")

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testMove1(self):
        with mock.patch("generic_run.run_cmd", return_value=(True, self.result_obj)) as dummy:
            v, r = mv_wrapper.move(None, None)
            self.assertFalse(v)
            dummy.assert_not_called()

    def testMove2(self):
        with mock.patch("generic_run.run_cmd", return_value=(True, self.result_obj)) as dummy:
            v, r = mv_wrapper.move(self.path1, None)
            self.assertFalse(v)
            dummy.assert_not_called()

    def testMove3(self):
        with mock.patch("generic_run.run_cmd", return_value=(True, self.result_obj)) as dummy:
            v, r = mv_wrapper.move(None, self.path2)
            self.assertFalse(v)
            dummy.assert_not_called()

    def testMove4(self):
        with mock.patch("generic_run.run_cmd", return_value=(True, self.result_obj)) as dummy:
            v, r = mv_wrapper.move(self.path1, self.path2)
            self.assertTrue(v)
            dummy.assert_called_with(["mv", self.path1, self.path2])

    def testMove5(self):
        with mock.patch("generic_run.run_cmd", return_value=(True, self.result_obj)) as dummy:
            v, r = mv_wrapper.move(self.rel_path1, self.rel_path2)
            self.assertTrue(v)
            dummy.assert_called_with(["mv", self.path1, self.path2])

if __name__ == '__main__':
    unittest.main()
