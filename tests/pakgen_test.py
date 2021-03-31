#!/usr/bin/env python3

import sys
import os
import shutil
import unittest

import mvtools_test_fixture
import create_and_write_file
import path_utils

import pakgen
import tar_wrapper

class PakGenTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("pakgen_wrapper_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # the target tar file
        self.target_file = path_utils.concat_path(self.test_dir, "target")
        self.target_file_tar_bz2 = self.target_file + ".tar.bz2"
        self.target_file_tar_bz2_hash = self.target_file_tar_bz2 + ".sha256"

        self.target_with_space_1 = path_utils.concat_path(self.test_dir, "te st")
        self.target_with_space_1_tar_bz2 = self.target_with_space_1 + ".tar.bz2"
        self.target_with_space_1_tar_bz2_hash = self.target_with_space_1_tar_bz2 + ".sha256"

        self.target_with_space_2 = path_utils.concat_path(self.test_dir, "  test")
        self.target_with_space_2_tar_bz2 = self.target_with_space_2 + ".tar.bz2"
        self.target_with_space_2_tar_bz2_hash = self.target_with_space_2_tar_bz2 + ".sha256"

        self.target_with_space_3 = path_utils.concat_path(self.test_dir, "test   ")
        self.target_with_space_3_tar_bz2 = self.target_with_space_3 + ".tar.bz2"
        self.target_with_space_3_tar_bz2_hash = self.target_with_space_3_tar_bz2 + ".sha256"

        self.file_nonexistant = path_utils.concat_path(self.test_dir, "no_file")

        # create test content
        self.file_with_space_1 = path_utils.concat_path(self.test_dir, "fi le.txt")
        create_and_write_file.create_file_contents(self.file_with_space_1, "abc")

        self.file_with_space_2 = path_utils.concat_path(self.test_dir, "  file.txt")
        create_and_write_file.create_file_contents(self.file_with_space_2, "abc")

        self.file_with_space_3 = path_utils.concat_path(self.test_dir, "file.txt  ")
        create_and_write_file.create_file_contents(self.file_with_space_3, "abc")

        self.file1 = path_utils.concat_path(self.test_dir, "file1.txt")
        create_and_write_file.create_file_contents(self.file1, "abc")

        self.folder1 = path_utils.concat_path(self.test_dir, "folder1")
        os.mkdir(self.folder1)

        self.folder1_file1 = path_utils.concat_path(self.folder1, "file1.txt")
        create_and_write_file.create_file_contents(self.folder1_file1, "abc")

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testPrecheck(self):
        v, r = pakgen.pakgen(self.target_file, False, [self.file_nonexistant])
        self.assertFalse(v)

    def testPakGen1(self):
        v, r = pakgen.pakgen(self.target_file, False, [self.file1])
        self.assertTrue(v)
        self.assertTrue( os.path.exists(self.target_file_tar_bz2) )
        self.assertFalse( os.path.exists ( self.target_file_tar_bz2_hash ) )

    def testPakGen2(self):
        v, r = pakgen.pakgen(self.target_file, True, [self.file1, self.file_with_space_1, self.folder1])
        self.assertTrue(v)
        self.assertTrue( os.path.exists(self.target_file_tar_bz2) )
        self.assertTrue( os.path.exists ( self.target_file_tar_bz2_hash ) )

        extracted_folder = path_utils.concat_path(self.test_dir, "extracted")
        os.mkdir(extracted_folder)

        v, r = tar_wrapper.extract(self.target_file_tar_bz2, extracted_folder)
        self.assertTrue(v)

        ext_file_with_space = path_utils.concat_path( extracted_folder, self.file_with_space_1)
        ext_file1 = path_utils.concat_path( extracted_folder, self.file1)
        ext_folder1 = path_utils.concat_path( extracted_folder, self.folder1)
        ext_folder1_file1 = path_utils.concat_path( extracted_folder, self.folder1_file1)

        self.assertTrue( os.path.exists( ext_file_with_space ) )
        self.assertTrue( os.path.exists( ext_file1 ) )
        self.assertTrue( os.path.exists( ext_folder1 ) )
        self.assertTrue( os.path.exists( ext_folder1_file1 ) )

    def testPakGen3(self):
        v, r = pakgen.pakgen(self.target_with_space_1, True, [self.file_with_space_1, self.file_with_space_2, self.file_with_space_3, self.folder1, self.file1])
        self.assertTrue(v)
        self.assertTrue( os.path.exists(self.target_with_space_1_tar_bz2) )
        self.assertTrue( os.path.exists ( self.target_with_space_1_tar_bz2_hash ) )

        extracted_folder = path_utils.concat_path(self.test_dir, "extracted")
        os.mkdir(extracted_folder)

        v, r = tar_wrapper.extract(self.target_with_space_1_tar_bz2, extracted_folder)
        self.assertTrue(v)

        ext_file_with_space_1 = path_utils.concat_path( extracted_folder, self.file_with_space_1)
        ext_file_with_space_2 = path_utils.concat_path( extracted_folder, self.file_with_space_2)
        ext_file_with_space_3 = path_utils.concat_path( extracted_folder, self.file_with_space_3)

        ext_file1 = path_utils.concat_path( extracted_folder, self.file1)
        ext_folder1 = path_utils.concat_path( extracted_folder, self.folder1)
        ext_folder1_file1 = path_utils.concat_path( extracted_folder, self.folder1_file1)

        self.assertTrue( os.path.exists( ext_file_with_space_1 ) )
        self.assertTrue( os.path.exists( ext_file_with_space_2 ) )
        self.assertTrue( os.path.exists( ext_file_with_space_3 ) )
        self.assertTrue( os.path.exists( ext_file1 ) )

    def testPakGen4(self):
        v, r = pakgen.pakgen(self.target_with_space_2, True, [self.file1])
        self.assertTrue(v)
        self.assertTrue( os.path.exists(self.target_with_space_2_tar_bz2) )
        self.assertTrue( os.path.exists ( self.target_with_space_2_tar_bz2_hash ) )

        extracted_folder = path_utils.concat_path(self.test_dir, "extracted")
        os.mkdir(extracted_folder)

        v, r = tar_wrapper.extract(self.target_with_space_2_tar_bz2, extracted_folder)
        self.assertTrue(v)

        ext_file1 = path_utils.concat_path( extracted_folder, self.file1)
        self.assertTrue( os.path.exists( ext_file1 ) )

    def testPakGen5(self):
        v, r = pakgen.pakgen(self.target_with_space_3, True, [self.file1])
        self.assertTrue(v)
        self.assertTrue( os.path.exists(self.target_with_space_3_tar_bz2) )
        self.assertTrue( os.path.exists ( self.target_with_space_3_tar_bz2_hash ) )

        extracted_folder = path_utils.concat_path(self.test_dir, "extracted")
        os.mkdir(extracted_folder)

        v, r = tar_wrapper.extract(self.target_with_space_3_tar_bz2, extracted_folder)
        self.assertTrue(v)

        ext_file1 = path_utils.concat_path( extracted_folder, self.file1)
        self.assertTrue( os.path.exists( ext_file1 ) )

    def testPakGen_AddStrToReport(self):

        report = ""
        report = pakgen.add_str_to_report(report, "add1")
        self.assertEqual(report, "add1")
        report = pakgen.add_str_to_report(report, "add2")
        self.assertEqual(report, "add1 / add2")
        report = pakgen.add_str_to_report(report, "")
        self.assertEqual(report, "add1 / add2")

if __name__ == '__main__':
    unittest.main()
