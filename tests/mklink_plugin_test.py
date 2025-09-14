#!/usr/bin/env python

import sys
import os
import shutil
import unittest
from unittest import mock
from unittest.mock import patch
from unittest.mock import call

import mvtools_test_fixture

import create_and_write_file
import path_utils
import mvtools_exception

import mklink_plugin

class MklinkPluginTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("mklink_plugin_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        self.test_source_file = path_utils.concat_path(self.test_dir, "test_source_file")
        create_and_write_file.create_file_contents(self.test_source_file, "test-contents")
        if not os.path.exists(self.test_source_file):
            return False, "Unable to create test file [%s]" % self.test_source_file

        self.test_nonexistent_file1 = path_utils.concat_path(self.test_dir, "test_nonexistent_file1")
        if os.path.exists(self.test_nonexistent_file1):
            return False, "File [%s] already exists" % self.test_nonexistent_file1

        self.test_nonexistent_file2 = path_utils.concat_path(self.test_dir, "test_nonexistent_file2")
        if os.path.exists(self.test_nonexistent_file2):
            return False, "File [%s] already exists" % self.test_nonexistent_file2

        self.helper_os_path_exists_counter = 0
        self.helper_os_path_exists_fail_zero = False

        # the test task
        self.mklink_task = mklink_plugin.CustomTask()

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def _helper_os_path_exists(self, target_path):

        if self.helper_os_path_exists_counter > 0:
            self.helper_os_path_exists_counter -= 1
        if self.helper_os_path_exists_fail_zero and self.helper_os_path_exists_counter == 0:
            return False
        return ((self.helper_os_path_exists_counter % 2) == 0)

    def _helper_throw_except(self):

        raise mvtools_exception.mvtools_exception("dummy exception")

    def testMklinkPluginReadParams1(self):

        local_params = {}
        local_params["target_path"] = self.test_nonexistent_file1
        self.mklink_task.params = local_params

        v, r = self.mklink_task._read_params()
        self.assertFalse(v)

    def testMklinkPluginReadParams2(self):

        local_params = {}
        local_params["target_path"] = self.test_nonexistent_file1
        self.mklink_task.params = local_params

        v, r = self.mklink_task._read_params()
        self.assertFalse(v)

    def testMklinkPluginReadParams3(self):

        local_params = {}
        local_params["source_path"] = self.test_nonexistent_file1
        local_params["target_path"] = self.test_nonexistent_file2
        self.mklink_task.params = local_params

        v, r = self.mklink_task._read_params()
        self.assertFalse(v)

    def testMklinkPluginReadParams4(self):

        create_and_write_file.create_file_contents(self.test_nonexistent_file1, "test-contents")
        self.assertTrue(os.path.exists(self.test_nonexistent_file1))

        local_params = {}
        local_params["source_path"] = self.test_source_file
        local_params["target_path"] = self.test_nonexistent_file1
        self.mklink_task.params = local_params

        v, r = self.mklink_task._read_params()
        self.assertFalse(v)

    def testMklinkPluginReadParams5(self):

        local_params = {}
        local_params["source_path"] = self.test_source_file
        local_params["target_path"] = self.test_nonexistent_file1
        self.mklink_task.params = local_params

        v, r = self.mklink_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, (self.test_source_file, self.test_nonexistent_file1))

    def testMklinkPluginRunTask1(self):

        local_params = {}
        local_params["source_path"] = self.test_source_file
        local_params["target_path"] = self.test_nonexistent_file1
        self.mklink_task.params = local_params

        with mock.patch("os.symlink", return_value=(False)) as dummy:
            dummy.side_effect = self._helper_throw_except
            v, r = self.mklink_task.run_task(print, "exe_name")
            self.assertFalse(v)
            self.assertEqual(r, "mklink failed - unable to create symlink from [%s] to [%s]" % (self.test_source_file, self.test_nonexistent_file1))
            dummy.assert_called_with(self.test_source_file, self.test_nonexistent_file1)

    def testMklinkPluginRunTask2(self):

        local_params = {}
        local_params["source_path"] = self.test_source_file
        local_params["target_path"] = self.test_nonexistent_file1
        self.mklink_task.params = local_params

        self.helper_os_path_exists_counter = 3
        self.helper_os_path_exists_fail_zero = True
        with mock.patch("os.symlink", return_value=(True)) as dummy1:
            with mock.patch("os.path.exists", return_value=(True)) as dummy2:
                dummy2.side_effect = self._helper_os_path_exists
                v, r = self.mklink_task.run_task(print, "exe_name")
                self.assertFalse(v)
                self.assertEqual(r, "mklink failed - symlink from [%s] to [%s] was not created" % (self.test_source_file, self.test_nonexistent_file1))
                dummy1.assert_called_with(self.test_source_file, self.test_nonexistent_file1)
                dummy2.assert_has_calls([call(self.test_source_file), call(self.test_nonexistent_file1), call(self.test_nonexistent_file1)])

    def testMklinkPluginRunTask3(self):

        local_params = {}
        local_params["source_path"] = self.test_source_file
        local_params["target_path"] = self.test_nonexistent_file1
        self.mklink_task.params = local_params

        self.helper_os_path_exists_counter = 3
        with mock.patch("os.symlink", return_value=(True)) as dummy1:
            with mock.patch("os.path.exists", return_value=(True)) as dummy2:
                dummy2.side_effect = self._helper_os_path_exists
                v, r = self.mklink_task.run_task(print, "exe_name")
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy1.assert_called_with(self.test_source_file, self.test_nonexistent_file1)
                dummy2.assert_has_calls([call(self.test_source_file), call(self.test_nonexistent_file1), call(self.test_nonexistent_file1)])

if __name__ == "__main__":
    unittest.main()
