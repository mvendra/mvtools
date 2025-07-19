#!/usr/bin/env python3

import sys
import os
import shutil
import unittest

import mvtools_test_fixture
import create_and_write_file
import path_utils
import standard_c
import generic_run

import gcc_wrapper

class GccWrapperTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("gcc_wrapper_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # prepare test content
        self.main_c = "main.c"
        self.main_c_full = path_utils.concat_path(self.test_dir, self.main_c)

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testExec1(self):

        create_and_write_file.create_file_contents(self.main_c_full, standard_c.get_main_c_app())

        v, r = gcc_wrapper.exec(self.main_c_full, self.test_dir)
        self.assertFalse(v)
        self.assertEqual(r, "options_list must be a list")

    def testExec2(self):

        v, r = gcc_wrapper.exec([self.main_c_full], self.test_dir)
        self.assertFalse(v)

    def testExec3(self):

        create_and_write_file.create_file_contents(self.main_c_full, standard_c.get_main_c_app())

        v, r = gcc_wrapper.exec([self.main_c_full], self.test_dir)
        self.assertTrue(v)
        self.assertEqual(r, None)

        a_out = "a.out"
        a_out_full = path_utils.concat_path(self.test_dir, a_out)

        v, r = generic_run.run_cmd_simple([a_out_full], use_cwd=self.test_dir)
        self.assertTrue(v)
        self.assertEqual(r.strip(), "test for echo")

if __name__ == '__main__':
    unittest.main()
