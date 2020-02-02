#!/usr/bin/env python3

import sys
import os
import shutil
import unittest

import mvtools_test_fixture
import create_and_write_file

import pakgen
import tar_wrapper

class PakGenTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("pakgen_wrapper_test_base")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # the target tar file
        self.target_file = os.path.join(self.test_dir, "target")
        self.target_file_tar_bz2 = self.target_file + ".tar.bz2"
        self.target_file_tar_bz2_hash = self.target_file_tar_bz2 + ".sha256"
        self.target_with_space = os.path.join(self.test_dir, "te st")
        self.target_with_space_tar_bz2 = self.target_with_space + ".tar.bz2"
        self.target_with_space_tar_bz2_hash = self.target_with_space_tar_bz2 + ".sha256"

        self.file_nonexistant = os.path.join(self.test_dir, "no_file")

        # create test content
        self.file_with_space = os.path.join(self.test_dir, "fi le.txt")
        create_and_write_file.create_file_contents(self.file_with_space, "abc")

        self.file1 = os.path.join(self.test_dir, "file1.txt")
        create_and_write_file.create_file_contents(self.file1, "abc")

        self.folder1 = os.path.join(self.test_dir, "folder1")
        os.mkdir(self.folder1)

        self.folder1_file1 = os.path.join(self.folder1, "file1.txt")
        create_and_write_file.create_file_contents(self.folder1_file1, "abc")

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testPrecheck(self):
        v = pakgen.pakgen(self.target_file, False, [self.file_nonexistant])
        self.assertFalse(v)

    def testPakGen1(self):
        v = pakgen.pakgen(self.target_file, False, [self.file1])
        self.assertTrue(v)
        self.assertTrue( os.path.exists(self.target_file_tar_bz2) )
        self.assertFalse( os.path.exists ( self.target_file_tar_bz2_hash ) )

    def testPakGen2(self):
        v = pakgen.pakgen(self.target_file, True, [self.file1, self.file_with_space, self.folder1])
        self.assertTrue(v)
        self.assertTrue( os.path.exists(self.target_file_tar_bz2) )
        self.assertTrue( os.path.exists ( self.target_file_tar_bz2_hash ) )

        extracted_folder = os.path.join(self.test_dir, "extracted")
        os.mkdir(extracted_folder)

        v, r = tar_wrapper.extract(self.target_file_tar_bz2, extracted_folder)
        self.assertTrue(v)

        ext_file_with_space = os.path.join( extracted_folder, self.file_with_space )
        ext_file1 = os.path.join( extracted_folder, self.file1 )
        ext_folder1 = os.path.join( extracted_folder, self.folder1 )
        ext_folder1_file1 = os.path.join( extracted_folder, self.folder1_file1 )

        self.assertTrue( os.path.exists( ext_file_with_space ) )
        self.assertTrue( os.path.exists( ext_file1 ) )
        self.assertTrue( os.path.exists( ext_folder1 ) )
        self.assertTrue( os.path.exists( ext_folder1_file1 ) )

    def testPakGen3(self):
        v = pakgen.pakgen(self.target_with_space, True, [self.file_with_space, self.folder1])
        self.assertTrue(v)
        self.assertTrue( os.path.exists(self.target_with_space_tar_bz2) )
        self.assertTrue( os.path.exists ( self.target_with_space_tar_bz2_hash ) )

        extracted_folder = os.path.join(self.test_dir, "extracted")
        os.mkdir(extracted_folder)

        v, r = tar_wrapper.extract(self.target_with_space_tar_bz2, extracted_folder)
        self.assertTrue(v)

        ext_file_with_space = os.path.join( extracted_folder, self.file_with_space )
        ext_file1 = os.path.join( extracted_folder, self.file1 )

        self.assertTrue( os.path.exists( ext_file_with_space ) )
        self.assertTrue( os.path.exists( ext_file1 ) )

if __name__ == '__main__':
    unittest.main()
