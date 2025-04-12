#!/usr/bin/env python3

import sys
import os
import shutil
import unittest

import mvtools_test_fixture
import create_and_write_file
import path_utils
import generic_run
from unittest import mock
from unittest.mock import patch

import diff_wrapper

class DiffWrapperTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("diff_wrapper_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # create test content

        self.file1 = path_utils.concat_path(self.test_dir, "file1.txt")
        self.file2 = path_utils.concat_path(self.test_dir, "file2.txt")
        self.file1_empty = path_utils.concat_path(self.test_dir, "file1_empty.txt")
        self.file2_empty = path_utils.concat_path(self.test_dir, "file2_empty.txt")
        self.file1_hid = path_utils.concat_path(self.test_dir, ".file1.txt")
        self.file2_hid = path_utils.concat_path(self.test_dir, ".file2.txt")
        self.file1_esp1 = path_utils.concat_path(self.test_dir, "   file1.txt")
        self.file2_esp1 = path_utils.concat_path(self.test_dir, "   file2.txt")
        self.file1_esp2 = path_utils.concat_path(self.test_dir, "file1   .txt")
        self.file2_esp2 = path_utils.concat_path(self.test_dir, "file2   .txt")
        self.file1_esp3 = path_utils.concat_path(self.test_dir, "file1.txt   ")
        self.file2_esp3 = path_utils.concat_path(self.test_dir, "file2.txt   ")
        self.file1_esp4 = path_utils.concat_path(self.test_dir, "file1_esp4.txt")
        self.file2_esp4 = path_utils.concat_path(self.test_dir, "file2_esp4.txt")
        self.file1_bin = path_utils.concat_path(self.test_dir, "file1.bin")
        self.file2_bin = path_utils.concat_path(self.test_dir, "file2.bin")
        self.nonexistent1 = path_utils.concat_path(self.test_dir, "nonexistent1")
        self.nonexistent2 = path_utils.concat_path(self.test_dir, "nonexistent2")

        self.assertTrue(create_and_write_file.create_file_contents(self.file1, "abc"))
        self.assertTrue(create_and_write_file.create_file_contents(self.file2, "def"))
        self.assertTrue(create_and_write_file.create_file_contents(self.file1_empty, ""))
        self.assertTrue(create_and_write_file.create_file_contents(self.file2_empty, ""))
        self.assertTrue(create_and_write_file.create_file_contents(self.file1_hid, "abc"))
        self.assertTrue(create_and_write_file.create_file_contents(self.file2_hid, "def"))
        self.assertTrue(create_and_write_file.create_file_contents(self.file1_esp1, "abc"))
        self.assertTrue(create_and_write_file.create_file_contents(self.file2_esp1, "def"))
        self.assertTrue(create_and_write_file.create_file_contents(self.file1_esp2, "abc"))
        self.assertTrue(create_and_write_file.create_file_contents(self.file2_esp2, "def"))
        self.assertTrue(create_and_write_file.create_file_contents(self.file1_esp3, "abc"))
        self.assertTrue(create_and_write_file.create_file_contents(self.file2_esp3, "def"))
        self.assertTrue(create_and_write_file.create_file_contents(self.file1_esp4, "abc"))
        self.assertTrue(create_and_write_file.create_file_contents(self.file2_esp4, "def"))
        self.file1_esp4 += "/"
        self.file2_esp4 += "/"

        with open(self.file1_bin, "wb+") as f:
            f.write(b"\xa1\xb2\xc3")

        with open(self.file2_bin, "wb+") as f:
            f.write(b"\xd4\xe5\xf6")

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testDoDiff1(self):

        v, r = diff_wrapper.do_diff(self.file1, self.nonexistent2)
        self.assertFalse(v)
        self.assertEqual(r, "[%s] does not exist." % self.nonexistent2)

    def testDoDiff2(self):

        v, r = diff_wrapper.do_diff(self.nonexistent1, self.file2)
        self.assertFalse(v)
        self.assertEqual(r, "[%s] does not exist." % self.nonexistent1)

    def testDoDiff3(self):

        v, r = diff_wrapper.do_diff(self.nonexistent1, self.nonexistent2)
        self.assertFalse(v)
        self.assertEqual(r, "[%s] does not exist." % self.nonexistent1)

    def testDoDiff4(self):

        with mock.patch("generic_run.run_cmd", return_value=(False, "test error message")) as dummy:
            v, r = diff_wrapper.do_diff(self.file1, self.file2)
            self.assertFalse(v)
            self.assertEqual(r, "Failed running diff command: [test error message]")
            dummy.assert_called_with(["diff", self.file1, self.file2])

    def testDoDiff5(self):

        test_res = generic_run.run_cmd_result(False, 2, "dummy-stdout", "dummy-stderr")
        with mock.patch("generic_run.run_cmd", return_value=(True, test_res)) as dummy:
            v, r = diff_wrapper.do_diff(self.file1, self.file2)
            self.assertFalse(v)
            self.assertEqual(r, "Failed running diff command: [dummy-stdout][dummy-stderr]")
            dummy.assert_called_with(["diff", self.file1, self.file2])

    def testDoDiff6(self):

        v, r = diff_wrapper.do_diff(self.file1, self.file2)
        self.assertTrue(v)
        self.assertEqual(r, "1c1%s< abc%s\\ No newline at end of file%s---%s> def%s\\ No newline at end of file%s" % (os.linesep, os.linesep, os.linesep, os.linesep, os.linesep, os.linesep))

    def testDoDiff7(self):

        v, r = diff_wrapper.do_diff(self.file1, self.file1)
        self.assertTrue(v)
        self.assertEqual(r, "")

    def testDoDiff8(self):

        v, r = diff_wrapper.do_diff(self.file1, self.file2_bin)
        self.assertTrue(v)
        self.assertEqual(r[0:44], "1c1%s< abc%s\\ No newline at end of file%s---%s> " % (os.linesep, os.linesep, os.linesep, os.linesep))
        self.assertEqual(r[44:], "%s\\ No newline at end of file%s" % (os.linesep, os.linesep))

    def testDoDiff9(self):

        v, r = diff_wrapper.do_diff(self.file1_bin, self.file2)
        self.assertTrue(v)
        self.assertEqual(r[0:6], "1c1%s< " % (os.linesep))
        self.assertEqual(r[6:], "%s\\ No newline at end of file%s---%s> def%s\\ No newline at end of file%s" % (os.linesep, os.linesep, os.linesep, os.linesep, os.linesep))

    def testDoDiff10(self):

        v, r = diff_wrapper.do_diff(self.file1_bin, self.file2_bin)
        self.assertTrue(v)
        self.assertEqual(r[0:6], "1c1%s< " % (os.linesep))
        self.assertEqual(r[6:41], "%s\\ No newline at end of file%s---%s> " % (os.linesep, os.linesep, os.linesep))
        self.assertEqual(r[41:70], "%s\\ No newline at end of file%s" % (os.linesep, os.linesep))

    def testDoDiff11(self):

        v, r = diff_wrapper.do_diff(self.file1_bin, self.file1_bin)
        self.assertTrue(v)
        self.assertEqual(r, "")

    def testDoDiff12(self):

        v, r = diff_wrapper.do_diff(self.file1_hid, self.file2_hid)
        self.assertTrue(v)
        self.assertEqual(r, "1c1%s< abc%s\\ No newline at end of file%s---%s> def%s\\ No newline at end of file%s" % (os.linesep, os.linesep, os.linesep, os.linesep, os.linesep, os.linesep))

    def testDoDiff13(self):

        v, r = diff_wrapper.do_diff(self.file1_esp1, self.file2_esp1)
        self.assertTrue(v)
        self.assertEqual(r, "1c1%s< abc%s\\ No newline at end of file%s---%s> def%s\\ No newline at end of file%s" % (os.linesep, os.linesep, os.linesep, os.linesep, os.linesep, os.linesep))

    def testDoDiff14(self):

        v, r = diff_wrapper.do_diff(self.file1_esp2, self.file2_esp2)
        self.assertTrue(v)
        self.assertEqual(r, "1c1%s< abc%s\\ No newline at end of file%s---%s> def%s\\ No newline at end of file%s" % (os.linesep, os.linesep, os.linesep, os.linesep, os.linesep, os.linesep))

    def testDoDiff15(self):

        v, r = diff_wrapper.do_diff(self.file1_esp3, self.file2_esp3)
        self.assertTrue(v)
        self.assertEqual(r, "1c1%s< abc%s\\ No newline at end of file%s---%s> def%s\\ No newline at end of file%s" % (os.linesep, os.linesep, os.linesep, os.linesep, os.linesep, os.linesep))

    def testDoDiff16(self):

        v, r = diff_wrapper.do_diff(self.file1_esp4, self.file2_esp4)
        self.assertTrue(v)
        self.assertEqual(r, "1c1%s< abc%s\\ No newline at end of file%s---%s> def%s\\ No newline at end of file%s" % (os.linesep, os.linesep, os.linesep, os.linesep, os.linesep, os.linesep))

    def testDoDiff17(self):

        v, r = diff_wrapper.do_diff(self.file1_empty, self.file1_empty)
        self.assertTrue(v)
        self.assertEqual(r, "")

if __name__ == '__main__':
    unittest.main()
