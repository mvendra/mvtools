#!/usr/bin/env python3

import sys
import os
import shutil
import unittest
from unittest import mock
from unittest.mock import patch

import mvtools_test_fixture
import mvtools_exception
import create_and_write_file
import path_utils

import output_backup_helper

class OutputBackupHelperTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("output_backup_helper_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        self.output_backup_storage = path_utils.concat_path(self.test_dir, "output_backup")
        os.mkdir(self.output_backup_storage)

        self.nonexistent_file1 = path_utils.concat_path(self.test_dir, "nonexistent_file1")

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testOutputBackupHelper_DumpOutput1(self):

        self.assertFalse(os.path.exists(self.nonexistent_file1))
        output_backup_helper.dump_output(print, self.nonexistent_file1, "test-contents", "")
        self.assertTrue(os.path.exists(self.nonexistent_file1))

        contents = ""
        with open(self.nonexistent_file1) as f:
            contents = f.read()
        self.assertTrue(contents, "test-contents")

    def testOutputBackupHelper_DumpOutput2(self):

        ex_raised = False
        try:
            output_backup_helper.dump_output(print, None, "test-contents", "")
        except mvtools_exception.mvtools_exception as mvtex:
            ex_raised = True

        self.assertFalse(ex_raised)

    def testOutputBackupHelper_DumpOutput3(self):

        self.assertFalse(os.path.exists(self.nonexistent_file1))
        create_and_write_file.create_file_contents(self.nonexistent_file1, "contents")

        ex_raised = False
        try:
            output_backup_helper.dump_output(print, self.nonexistent_file1, "test-contents", "")
        except mvtools_exception.mvtools_exception as mvtex:
            ex_raised = True

        self.assertTrue(ex_raised)

    def testOutputBackupHelper_DumpOutputsAutobackup1(self):

        test_stdout_fn = path_utils.concat_path(self.output_backup_storage, "app_stdout_autobackup_0_test_timestamp.txt")
        test_stderr_fn = path_utils.concat_path(self.output_backup_storage, "app_stderr_autobackup_0_test_timestamp.txt")

        self.assertFalse(os.path.exists(test_stdout_fn))
        self.assertFalse(os.path.exists(test_stderr_fn))

        with mock.patch("mvtools_envvars.mvtools_envvar_read_temp_path", return_value=(False, "error msg")) as dummy1:
            with mock.patch("toolbus.get_all_fields", return_value=(True, [])) as dummy2:
                with mock.patch("maketimestamp.get_timestamp_now_compact", return_value="test_timestamp") as dummy3:
                    with mock.patch("toolbus.get_field", return_value=(True, ("index", "0", []))) as dummy4:
                        with mock.patch("toolbus.set_field", return_value=(True, None)) as dummy5:
                            out_list = [ ( "app_stdout", "stdout-contents", "test-app-stdout" ) , ( "app_stderr", "stderr-contents", "test-app-stderr" ) ]
                            self.assertNotEqual(output_backup_helper.dump_outputs_autobackup(False, print, out_list), None)

    def testOutputBackupHelper_DumpOutputsAutobackup2(self):

        test_stdout_fn = path_utils.concat_path(self.output_backup_storage, "app_stdout_autobackup_0_test_timestamp.txt")
        test_stderr_fn = path_utils.concat_path(self.output_backup_storage, "app_stderr_autobackup_0_test_timestamp.txt")

        self.assertFalse(os.path.exists(test_stdout_fn))
        self.assertFalse(os.path.exists(test_stderr_fn))
        create_and_write_file.create_file_contents(test_stdout_fn, "contents")
        self.assertTrue(os.path.exists(test_stdout_fn))

        with mock.patch("mvtools_envvars.mvtools_envvar_read_temp_path", return_value=(True, self.output_backup_storage)) as dummy1:
            with mock.patch("toolbus.get_all_fields", return_value=(True, [])) as dummy2:
                with mock.patch("maketimestamp.get_timestamp_now_compact", return_value="test_timestamp") as dummy3:
                    with mock.patch("toolbus.get_field", return_value=(True, ("index", "0", []))) as dummy4:
                        with mock.patch("toolbus.set_field", return_value=(True, None)) as dummy5:
                            out_list = [ ( "app_stdout", "stdout-contents", "test-app-stdout" ) , ( "app_stderr", "stderr-contents", "test-app-stderr" ) ]
                            self.assertNotEqual(output_backup_helper.dump_outputs_autobackup(False, print, out_list), None)

    def testOutputBackupHelper_DumpOutputsAutobackup3(self):

        test_stdout_fn = path_utils.concat_path(self.output_backup_storage, "app_stdout_autobackup_0_test_timestamp.txt")
        test_stderr_fn = path_utils.concat_path(self.output_backup_storage, "app_stderr_autobackup_0_test_timestamp.txt")

        self.assertFalse(os.path.exists(test_stdout_fn))
        self.assertFalse(os.path.exists(test_stderr_fn))
        create_and_write_file.create_file_contents(test_stderr_fn, "contents")
        self.assertTrue(os.path.exists(test_stderr_fn))

        with mock.patch("mvtools_envvars.mvtools_envvar_read_temp_path", return_value=(True, self.output_backup_storage)) as dummy1:
            with mock.patch("toolbus.get_all_fields", return_value=(True, [])) as dummy2:
                with mock.patch("maketimestamp.get_timestamp_now_compact", return_value="test_timestamp") as dummy3:
                    with mock.patch("toolbus.get_field", return_value=(True, ("index", "0", []))) as dummy4:
                        with mock.patch("toolbus.set_field", return_value=(True, None)) as dummy5:
                            out_list = [ ( "app_stdout", "stdout-contents", "test-app-stdout" ) , ( "app_stderr", "stderr-contents", "test-app-stderr" ) ]
                            self.assertNotEqual(output_backup_helper.dump_outputs_autobackup(False, print, out_list), None)

    def testOutputBackupHelper_DumpOutputsAutobackup4(self):

        test_stdout_fn = path_utils.concat_path(self.output_backup_storage, "app_stdout_autobackup_0_test_timestamp.txt")
        test_stderr_fn = path_utils.concat_path(self.output_backup_storage, "app_stderr_autobackup_0_test_timestamp.txt")

        self.assertFalse(os.path.exists(test_stdout_fn))
        self.assertFalse(os.path.exists(test_stderr_fn))

        with mock.patch("mvtools_envvars.mvtools_envvar_read_temp_path", return_value=(True, self.output_backup_storage)) as dummy1:
            with mock.patch("toolbus.get_all_fields", return_value=(True, [])) as dummy2:
                with mock.patch("maketimestamp.get_timestamp_now_compact", return_value="test_timestamp") as dummy3:
                    with mock.patch("toolbus.get_field", return_value=(True, ("index", "0", []))) as dummy4:
                        with mock.patch("toolbus.set_field", return_value=(True, None)) as dummy5:
                            out_list = [ ( "app_stdout", "stdout-contents", "test-app-stdout" ) , ( "app_stderr", "stderr-contents", "test-app-stderr" ) ]
                            self.assertEqual(output_backup_helper.dump_outputs_autobackup(False, print, out_list), None)

        self.assertTrue(os.path.exists(test_stdout_fn))
        self.assertTrue(os.path.exists(test_stderr_fn))

        stdout_contents = ""
        with open(test_stdout_fn, "r") as f:
            stdout_contents = f.read()
        self.assertEqual(stdout_contents, "stdout-contents")

        stderr_contents = ""
        with open(test_stderr_fn, "r") as f:
            stderr_contents = f.read()
        self.assertEqual(stderr_contents, "stderr-contents")

    def testOutputBackupHelper_DumpOutputsAutobackup5(self):

        test_stdout_fn = path_utils.concat_path(self.output_backup_storage, "app_stdout_autobackup_0_test_timestamp.txt")
        test_stderr_fn = path_utils.concat_path(self.output_backup_storage, "app_stderr_autobackup_0_test_timestamp.txt")

        self.assertFalse(os.path.exists(test_stdout_fn))
        self.assertFalse(os.path.exists(test_stderr_fn))

        with mock.patch("mvtools_envvars.mvtools_envvar_read_temp_path", return_value=(True, self.output_backup_storage)) as dummy1:
            with mock.patch("toolbus.get_all_fields", return_value=(True, [])) as dummy2:
                with mock.patch("maketimestamp.get_timestamp_now_compact", return_value="test_timestamp") as dummy3:
                    with mock.patch("toolbus.get_field", return_value=(True, ("index", "0", []))) as dummy4:
                        with mock.patch("toolbus.set_field", return_value=(True, None)) as dummy5:
                            out_list = [ ( "app_stdout", "stdout-contents", "test-app-stdout" ) , ( "app_stderr", "stderr-contents", "test-app-stderr" ) ]
                            self.assertEqual(output_backup_helper.dump_outputs_autobackup(False, print, out_list), None)

        self.assertTrue(os.path.exists(test_stdout_fn))
        self.assertTrue(os.path.exists(test_stderr_fn))

        with open(test_stdout_fn, "a") as f:
            f.write("-more stuff on stdout")

        with open(test_stderr_fn, "a") as f:
            f.write("-more stuff on stderr")

        with mock.patch("mvtools_envvars.mvtools_envvar_read_temp_path", return_value=(True, self.output_backup_storage)) as dummy1:
            with mock.patch("toolbus.get_all_fields", return_value=(True, [])) as dummy2:
                with mock.patch("maketimestamp.get_timestamp_now_compact", return_value="test_timestamp") as dummy3:
                    with mock.patch("toolbus.get_field", return_value=(True, ("index", "0", []))) as dummy4:
                        with mock.patch("toolbus.set_field", return_value=(True, None)) as dummy5:
                            out_list = [ ( "app_stdout", "stdout-contents", "saved stdout" ) , ( "app_stderr", "stderr-contents", "saved stderr" ) ]
                            self.assertNotEqual(output_backup_helper.dump_outputs_autobackup(False, print, out_list), None)

        stdout_contents = ""
        with open(test_stdout_fn, "r") as f:
            stdout_contents = f.read()
        self.assertEqual(stdout_contents, "stdout-contents-more stuff on stdout") # should not have been replaced

        stderr_contents = ""
        with open(test_stderr_fn, "r") as f:
            stderr_contents = f.read()
        self.assertEqual(stderr_contents, "stderr-contents-more stuff on stderr") # should not have been replaced

    def testOutputBackupHelper_DumpOutputsAutobackup6(self):

        test_stdout_fn = path_utils.concat_path(self.output_backup_storage, "app_stdout_autobackup_0_test_timestamp.txt")
        test_stderr_fn = path_utils.concat_path(self.output_backup_storage, "app_stderr_autobackup_0_test_timestamp.txt")

        self.assertFalse(os.path.exists(test_stdout_fn))
        self.assertFalse(os.path.exists(test_stderr_fn))

        with mock.patch("mvtools_envvars.mvtools_envvar_read_temp_path", return_value=(True, self.output_backup_storage)) as dummy1:
            with mock.patch("toolbus.get_all_fields", return_value=(True, [])) as dummy2:
                with mock.patch("maketimestamp.get_timestamp_now_compact", return_value="test_timestamp") as dummy3:
                    with mock.patch("toolbus.get_field", return_value=(True, ("index", "0", []))) as dummy4:
                        with mock.patch("toolbus.set_field", return_value=(True, None)) as dummy5:
                            out_list = [ ( "app_stdout", "stdout-contents", "test-app-stdout" ) , ( "app_stderr", "stderr-contents", "test-app-stderr" ) ]
                            self.assertEqual(output_backup_helper.dump_outputs_autobackup(True, print, out_list), None)

        self.assertFalse(os.path.exists(test_stdout_fn))
        self.assertFalse(os.path.exists(test_stderr_fn))

    def testOutputBackupHelper_DumpOutputsAutobackup7(self):

        test_stdout_fn = path_utils.concat_path(self.output_backup_storage, "app_stdout_autobackup_5_test_timestamp.txt")
        test_stderr_fn = path_utils.concat_path(self.output_backup_storage, "app_stderr_autobackup_5_test_timestamp.txt")

        self.assertFalse(os.path.exists(test_stdout_fn))
        self.assertFalse(os.path.exists(test_stderr_fn))

        with mock.patch("mvtools_envvars.mvtools_envvar_read_temp_path", return_value=(True, self.output_backup_storage)) as dummy1:
            with mock.patch("toolbus.get_all_fields", return_value=(True, [])) as dummy2:
                with mock.patch("maketimestamp.get_timestamp_now_compact", return_value="test_timestamp") as dummy3:
                    with mock.patch("toolbus.get_field", return_value=(True, ("index", "5", []))) as dummy4:
                        with mock.patch("toolbus.set_field", return_value=(True, None)) as dummy5:
                            out_list = [ ( "app_stdout", "stdout-contents", "test-app-stdout" ) , ( "app_stderr", "stderr-contents", "test-app-stderr" ) ]
                            self.assertEqual(output_backup_helper.dump_outputs_autobackup(True, print, out_list), None)

        self.assertFalse(os.path.exists(test_stdout_fn))
        self.assertFalse(os.path.exists(test_stderr_fn))

    def testOutputBackupHelper_DumpSingleAutobackup1(self):

        test_out_fn = path_utils.concat_path(self.output_backup_storage, "app_out_autobackup_0_test_timestamp.txt")
        self.assertFalse(os.path.exists(test_out_fn))

        with mock.patch("toolbus.get_all_fields", return_value=(True, [])) as dummy1:
            with mock.patch("maketimestamp.get_timestamp_now_compact", return_value="test_timestamp") as dummy2:
                with mock.patch("toolbus.get_field", return_value=(True, ("index", "0", []))) as dummy3:
                    with mock.patch("toolbus.set_field", return_value=(True, None)) as dummy4:
                        self.assertEqual(output_backup_helper.dump_single_autobackup(print, self.output_backup_storage, "app_out", "output contents", "test-app-out"), None)

        self.assertTrue(os.path.exists(test_out_fn))

    def testOutputBackupHelper_DumpSingleAutobackup2(self):

        test_out_fn = path_utils.concat_path(self.output_backup_storage, "app_out_autobackup_0_test_timestamp.txt")
        self.assertFalse(os.path.exists(test_out_fn))
        create_and_write_file.create_file_contents(test_out_fn, "contents")

        with mock.patch("toolbus.get_all_fields", return_value=(True, [])) as dummy1:
            with mock.patch("maketimestamp.get_timestamp_now_compact", return_value="test_timestamp") as dummy2:
                with mock.patch("toolbus.get_field", return_value=(True, ("index", "0", []))) as dummy3:
                    with mock.patch("toolbus.set_field", return_value=(True, None)) as dummy4:
                        self.assertNotEqual(output_backup_helper.dump_single_autobackup(print, self.output_backup_storage, "app_out", "output contents", "test-app-out"), None)

        self.assertTrue(os.path.exists(test_out_fn))

    def testOutputBackupHelper_DumpSingleAutobackup3(self):

        test_out_fn = path_utils.concat_path(self.output_backup_storage, "app_out_autobackup_8_test_timestamp.txt")
        self.assertFalse(os.path.exists(test_out_fn))
        create_and_write_file.create_file_contents(test_out_fn, "contents")

        with mock.patch("toolbus.get_all_fields", return_value=(True, [])) as dummy1:
            with mock.patch("maketimestamp.get_timestamp_now_compact", return_value="test_timestamp") as dummy2:
                with mock.patch("toolbus.get_field", return_value=(True, ("index", "8", []))) as dummy3:
                    with mock.patch("toolbus.set_field", return_value=(True, None)) as dummy4:
                        self.assertNotEqual(output_backup_helper.dump_single_autobackup(print, self.output_backup_storage, "app_out", "output contents", "test-app-out"), None)

        self.assertTrue(os.path.exists(test_out_fn))

if __name__ == "__main__":
    unittest.main()
