#!/usr/bin/env python

import sys
import os
import shutil
import unittest
from unittest import mock
from unittest.mock import patch

import mvtools_test_fixture

import bazel_wrapper
import generic_run

class BazelWrapperTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("bazel_wrapper_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        self.result_obj = generic_run.run_cmd_result(None, None, None, None)

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testBuildFail1(self):
        with mock.patch("generic_run.run_cmd", return_value=(True, self.result_obj)) as dummy:
            v, r = bazel_wrapper.build(None, None, None, None, [])
            self.assertFalse(v)
            dummy.assert_not_called()

    def testBuildFail2(self):
        with mock.patch("generic_run.run_cmd", return_value=(True, self.result_obj)) as dummy:
            v, r = bazel_wrapper.build("nonempty", None, None, [], [])
            self.assertFalse(v)

    def testBuild1(self):
        with mock.patch("generic_run.run_cmd", return_value=(True, self.result_obj)) as dummy:
            v, r = bazel_wrapper.build("nonempty", None, None, None, [])
            self.assertTrue(v)
            dummy.assert_called_with(["bazel", "build"], use_cwd="nonempty")

    def testBuild2(self):
        with mock.patch("generic_run.run_cmd", return_value=(True, self.result_obj)) as dummy:
            v, r = bazel_wrapper.build("nonempty", "64", None, None, [])
            self.assertTrue(v)
            dummy.assert_called_with(["bazel", "build", "--jobs=64"], use_cwd="nonempty")

    def testBuild3(self):
        with mock.patch("generic_run.run_cmd", return_value=(True, self.result_obj)) as dummy:
            v, r = bazel_wrapper.build("nonempty", "64", "test-config", None, [])
            self.assertTrue(v)
            dummy.assert_called_with(["bazel", "build", "--jobs=64", "--config=test-config"], use_cwd="nonempty")

    def testBuild4(self):
        with mock.patch("generic_run.run_cmd", return_value=(True, self.result_obj)) as dummy:
            v, r = bazel_wrapper.build("nonempty", "64", "test-config", "test-target", [])
            self.assertTrue(v)
            dummy.assert_called_with(["bazel", "build", "--jobs=64", "--config=test-config", "test-target"], use_cwd="nonempty")

    def testFetchFail1(self):
        with mock.patch("generic_run.run_cmd", return_value=(True, self.result_obj)) as dummy:
            v, r = bazel_wrapper.fetch(None, None)
            self.assertFalse(v)
            dummy.assert_not_called()

    def testFetchFail2(self):
        with mock.patch("generic_run.run_cmd", return_value=(True, self.result_obj)) as dummy:
            v, r = bazel_wrapper.fetch("nonempty", [])
            self.assertFalse(v)

    def testFetch1(self):
        with mock.patch("generic_run.run_cmd", return_value=(True, self.result_obj)) as dummy:
            v, r = bazel_wrapper.fetch("nonempty", None)
            self.assertTrue(v)
            dummy.assert_called_with(["bazel", "fetch"], use_cwd="nonempty")

    def testFetch2(self):
        with mock.patch("generic_run.run_cmd", return_value=(True, self.result_obj)) as dummy:
            v, r = bazel_wrapper.fetch("nonempty", "test-target")
            self.assertTrue(v)
            dummy.assert_called_with(["bazel", "fetch", "test-target"], use_cwd="nonempty")

    def testCleanFail1(self):
        with mock.patch("generic_run.run_cmd", return_value=(True, self.result_obj)) as dummy:
            v, r = bazel_wrapper.clean(None, False)
            self.assertFalse(v)
            dummy.assert_not_called()

    def testClean1(self):
        with mock.patch("generic_run.run_cmd", return_value=(True, self.result_obj)) as dummy:
            v, r = bazel_wrapper.clean("nonempty", False)
            self.assertTrue(v)
            dummy.assert_called_with(["bazel", "clean"], use_cwd="nonempty")

    def testClean2(self):
        with mock.patch("generic_run.run_cmd", return_value=(True, self.result_obj)) as dummy:
            v, r = bazel_wrapper.clean("nonempty", True)
            self.assertTrue(v)
            dummy.assert_called_with(["bazel", "clean", "--expunge"], use_cwd="nonempty")

    def testRun1(self):
        with mock.patch("generic_run.run_cmd", return_value=(True, self.result_obj)) as dummy:
            v, r = bazel_wrapper.run(None, None, [])
            self.assertFalse(v)

    def testRun2(self):
        with mock.patch("generic_run.run_cmd", return_value=(True, self.result_obj)) as dummy:
            v, r = bazel_wrapper.run("nonempty", [], [])
            self.assertFalse(v)

    def testRun3(self):
        with mock.patch("generic_run.run_cmd", return_value=(True, self.result_obj)) as dummy:
            v, r = bazel_wrapper.run("nonempty", None, "alsononemptybutnotalist")
            self.assertFalse(v)

    def testRun4(self):
        with mock.patch("generic_run.run_cmd", return_value=(False, self.result_obj)) as dummy:
            v, r = bazel_wrapper.run("nonempty", None, [])
            self.assertFalse(v)
            dummy.assert_called_with(["bazel", "run"], use_cwd="nonempty")

    def testRun5(self):
        with mock.patch("generic_run.run_cmd", return_value=(True, self.result_obj)) as dummy:
            v, r = bazel_wrapper.run("nonempty", None, [])
            self.assertTrue(v)
            dummy.assert_called_with(["bazel", "run"], use_cwd="nonempty")

    def testRun6(self):
        with mock.patch("generic_run.run_cmd", return_value=(True, self.result_obj)) as dummy:
            v, r = bazel_wrapper.run("nonempty", "alsononempty", [])
            self.assertTrue(v)
            dummy.assert_called_with(["bazel", "run", "alsononempty"], use_cwd="nonempty")

    def testRun7(self):
        with mock.patch("generic_run.run_cmd", return_value=(True, self.result_obj)) as dummy:
            v, r = bazel_wrapper.run("nonempty", "alsononempty", ["morestuff"])
            self.assertTrue(v)
            dummy.assert_called_with(["bazel", "run", "alsononempty", "--", "morestuff"], use_cwd="nonempty")

    def testTestFail1(self):
        with mock.patch("generic_run.run_cmd", return_value=(True, self.result_obj)) as dummy:
            v, r = bazel_wrapper.test(None, None, None, None, [])
            self.assertFalse(v)
            dummy.assert_not_called()

    def testTestFail2(self):
        with mock.patch("generic_run.run_cmd", return_value=(True, self.result_obj)) as dummy:
            v, r = bazel_wrapper.test("nonempty", None, None, [], [])
            self.assertFalse(v)

    def testTest1(self):
        with mock.patch("generic_run.run_cmd", return_value=(True, self.result_obj)) as dummy:
            v, r = bazel_wrapper.test("nonempty", None, None, None, [])
            self.assertTrue(v)
            dummy.assert_called_with(["bazel", "test"], use_cwd="nonempty")

    def testTest2(self):
        with mock.patch("generic_run.run_cmd", return_value=(True, self.result_obj)) as dummy:
            v, r = bazel_wrapper.test("nonempty", "64", None, None, [])
            self.assertTrue(v)
            dummy.assert_called_with(["bazel", "test", "--jobs=64"], use_cwd="nonempty")

    def testTest3(self):
        with mock.patch("generic_run.run_cmd", return_value=(True, self.result_obj)) as dummy:
            v, r = bazel_wrapper.test("nonempty", "64", "test-config", None, [])
            self.assertTrue(v)
            dummy.assert_called_with(["bazel", "test", "--jobs=64", "--config=test-config"], use_cwd="nonempty")

    def testTest4(self):
        with mock.patch("generic_run.run_cmd", return_value=(True, self.result_obj)) as dummy:
            v, r = bazel_wrapper.test("nonempty", "64", "test-config", "test-target", [])
            self.assertTrue(v)
            dummy.assert_called_with(["bazel", "test", "--jobs=64", "--config=test-config", "test-target"], use_cwd="nonempty")

if __name__ == "__main__":
    unittest.main()
