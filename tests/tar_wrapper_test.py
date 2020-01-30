#!/usr/bin/env python3

import sys
import os
import shutil
import unittest

import mvtools_test_fixture
import create_and_write_file

import tar_wrapper

class TarWrapperTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("tar_wrapper_test_base")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # the target tar file
        self.tar_file = os.path.join(self.test_dir, "test.tar")

        # create test content

        self.file_nonexistant = os.path.join(self.test_dir, "no_file")

        # base, files
        self.file1 = os.path.join(self.test_dir, "file1.txt")
        create_and_write_file.create_file_contents(self.file1, "abc")

        self.file2 = os.path.join(self.test_dir, "file2.txt")
        create_and_write_file.create_file_contents(self.file2, "abc")

        # base, folders
        self.folder1 = os.path.join(self.test_dir, "folder1")
        os.mkdir(self.folder1)

        self.folder2 = os.path.join(self.test_dir, "folder2")
        os.mkdir(self.folder2)

        self.folder2_sub1 = os.path.join(self.folder2, "sub1")
        os.mkdir(self.folder2_sub1)

        self.folder2_sub1_file1 = os.path.join(self.folder2_sub1, "file1.txt")
        create_and_write_file.create_file_contents(self.folder2_sub1_file1, "abc")

        # files in folders

        # folder1
        self.folder1_file1 = os.path.join(self.folder1, "file1.txt")
        create_and_write_file.create_file_contents(self.folder1_file1, "abc")

        self.folder1_file2 = os.path.join(self.folder1, "file2.txt")
        create_and_write_file.create_file_contents(self.folder1_file2, "abc")

        # folder2
        self.folder2_file1 = os.path.join(self.folder2, "file1.txt")
        create_and_write_file.create_file_contents(self.folder2_file1, "abc")

        self.folder2_file2 = os.path.join(self.folder2, "file2.txt")
        create_and_write_file.create_file_contents(self.folder2_file2, "abc")

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testPrechecks1(self):
        v, r = tar_wrapper.make_pack(self.file1, [self.file2])
        self.assertFalse(v)

    def testPrechecks2(self):
        v, r = tar_wrapper.make_pack(self.file_nonexistant, [])
        self.assertFalse(v)

    def testMakeAndExtract1(self):
        v, r = tar_wrapper.make_pack(self.tar_file, [self.folder1, self.folder2, self.file1, self.file2])
        self.assertTrue(v)
        self.assertTrue(os.path.exists(self.tar_file))

        self.extracted_folder = os.path.join(self.test_dir, "extracted")
        os.mkdir(self.extracted_folder)

        v, r = tar_wrapper.extract(self.tar_file, self.extracted_folder)
        self.assertTrue(v)

        self.ext_file1 = os.path.join(self.extracted_folder, self.file1)
        self.ext_file2 = os.path.join(self.extracted_folder, self.file2)
        self.ext_folder1 = os.path.join(self.extracted_folder, self.folder1)
        self.ext_folder2 = os.path.join(self.extracted_folder, self.folder2)
        self.ext_folder1_file1 = os.path.join(self.extracted_folder, self.folder1_file1)
        self.ext_folder1_file2 = os.path.join(self.extracted_folder, self.folder1_file2)
        self.ext_folder2_file1 = os.path.join(self.extracted_folder, self.folder2_file1)
        self.ext_folder2_file2 = os.path.join(self.extracted_folder, self.folder2_file2)
        self.ext_folder2_sub1 = os.path.join(self.extracted_folder, self.folder2_sub1)
        self.ext_folder2_sub1_file1 = os.path.join(self.extracted_folder, self.folder2_sub1_file1)

        self.assertTrue(os.path.exists( self.ext_file1 ))
        self.assertTrue(os.path.exists( self.ext_file2 ))
        self.assertTrue(os.path.exists( self.ext_folder1 ))
        self.assertTrue(os.path.exists( self.ext_folder2 ))
        self.assertTrue(os.path.exists( self.ext_folder1_file1 ))
        self.assertTrue(os.path.exists( self.ext_folder1_file2 ))
        self.assertTrue(os.path.exists( self.ext_folder2_file1 ))
        self.assertTrue(os.path.exists( self.ext_folder2_file2 ))
        self.assertTrue(os.path.exists( self.ext_folder2_sub1 ))
        self.assertTrue(os.path.exists( self.ext_folder2_sub1_file1 ))

    def testMakeAndExtract2(self):
        #v, r = tar_wrapper.make_pack(self.tar_file, [self.folder1, self.folder2, self.file1, self.file2], [self.folder2_sub1])
        v, r = tar_wrapper.make_pack(self.tar_file, [self.folder1, self.folder2, self.file1, self.file2])
        self.assertTrue(v)
        self.assertTrue(os.path.exists(self.tar_file))

        self.extracted_folder = os.path.join(self.test_dir, "extracted")
        os.mkdir(self.extracted_folder)

        v, r = tar_wrapper.extract(self.tar_file, self.extracted_folder)
        self.assertTrue(v)

        self.ext_file1 = os.path.join(self.extracted_folder, self.file1)
        self.ext_file2 = os.path.join(self.extracted_folder, self.file2)
        self.ext_folder1 = os.path.join(self.extracted_folder, self.folder1)
        self.ext_folder2 = os.path.join(self.extracted_folder, self.folder2)
        self.ext_folder1_file1 = os.path.join(self.extracted_folder, self.folder1_file1)
        self.ext_folder1_file2 = os.path.join(self.extracted_folder, self.folder1_file2)
        self.ext_folder2_file1 = os.path.join(self.extracted_folder, self.folder2_file1)
        self.ext_folder2_file2 = os.path.join(self.extracted_folder, self.folder2_file2)
        self.ext_folder2_sub1 = os.path.join(self.extracted_folder, self.folder2_sub1)
        self.ext_folder2_sub1_file1 = os.path.join(self.extracted_folder, self.folder2_sub1_file1)

        self.assertTrue(os.path.exists( self.ext_file1 ))
        self.assertTrue(os.path.exists( self.ext_file2 ))
        self.assertTrue(os.path.exists( self.ext_folder1 ))
        self.assertTrue(os.path.exists( self.ext_folder2 ))
        self.assertTrue(os.path.exists( self.ext_folder1_file1 ))
        self.assertTrue(os.path.exists( self.ext_folder1_file2 ))
        self.assertTrue(os.path.exists( self.ext_folder2_file1 ))
        self.assertTrue(os.path.exists( self.ext_folder2_file2 ))
        #self.assertFalse(os.path.exists( self.ext_folder2_sub1 ))
        #self.assertFalse(os.path.exists( self.ext_folder2_sub1_file1 ))
        self.assertTrue(os.path.exists( self.ext_folder2_sub1 ))
        self.assertTrue(os.path.exists( self.ext_folder2_sub1_file1 ))

if __name__ == '__main__':
    unittest.main()
