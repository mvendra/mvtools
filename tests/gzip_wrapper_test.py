#!/usr/bin/env python3

import sys
import os
import shutil
import unittest

import mvtools_test_fixture
import create_and_write_file
import path_utils
import tar_wrapper

import gzip_wrapper

class GzipWrapperTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("gzip_wrapper_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # the target tar file
        self.tar_file = path_utils.concat_path(self.test_dir, "test.tar")
        self.tar_gz_file = path_utils.concat_path(self.test_dir, "test.tar.gz")

        # base, files
        self.file1 = path_utils.concat_path(self.test_dir, "file1.txt")
        create_and_write_file.create_file_contents(self.file1, "abc")

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testGzipWrapperCompress(self):

        v, r = tar_wrapper.make_pack(self.tar_file, [self.file1])
        self.assertTrue(v)

        self.assertTrue(os.path.exists(self.tar_file))
        self.assertFalse(os.path.exists(self.tar_gz_file))

        v, r = gzip_wrapper.compress(self.tar_file)
        self.assertTrue(v)

        self.assertFalse(os.path.exists(self.tar_file))
        self.assertTrue(os.path.exists(self.tar_gz_file))

    def testGzipWrapperCompressAndDecompress1(self):

        v, r = tar_wrapper.make_pack(self.tar_file, [self.file1])
        self.assertTrue(v)

        self.assertTrue(os.path.exists(self.tar_file))
        self.assertFalse(os.path.exists(self.tar_gz_file))

        v, r = gzip_wrapper.compress(self.tar_file)
        self.assertTrue(v)

        self.assertFalse(os.path.exists(self.tar_file))
        self.assertTrue(os.path.exists(self.tar_gz_file))

        v, r = gzip_wrapper.decompress(self.tar_gz_file)
        self.assertTrue(v)

        self.assertTrue(os.path.exists(self.tar_file))
        self.assertFalse(os.path.exists(self.tar_gz_file))

    def testGzipWrapperCompressAndDecompress2(self):

        blanksub = path_utils.concat_path(self.test_dir, " ")
        self.assertFalse(os.path.exists(blanksub))
        os.mkdir(blanksub)
        self.assertTrue(os.path.exists(blanksub))

        blanksub_blankfn = path_utils.concat_path(blanksub, " ")
        self.assertFalse(os.path.exists(blanksub_blankfn))
        create_and_write_file.create_file_contents(blanksub_blankfn, "def")
        self.assertTrue(os.path.exists(blanksub_blankfn))

        blanksub_blankfn_gz = blanksub_blankfn + ".gz"
        self.assertFalse(os.path.exists(blanksub_blankfn_gz))

        v, r = gzip_wrapper.compress(blanksub_blankfn)
        self.assertTrue(v)

        self.assertFalse(os.path.exists(blanksub_blankfn))
        self.assertTrue(os.path.exists(blanksub_blankfn_gz))

        v, r = gzip_wrapper.decompress(blanksub_blankfn_gz)
        self.assertTrue(v)

        self.assertTrue(os.path.exists(blanksub_blankfn))
        self.assertFalse(os.path.exists(blanksub_blankfn_gz))

        with open(blanksub_blankfn, "r") as f:
            self.assertTrue("def" in f.read())

    def testGzipWrapperCompressAndDecompress3(self):

        testfile1 = path_utils.concat_path(self.test_dir, "testfile1.txt")
        self.assertFalse(os.path.exists(testfile1))
        create_and_write_file.create_file_contents(testfile1, "def")
        self.assertTrue(os.path.exists(testfile1))

        testfile2 = path_utils.concat_path(self.test_dir, "testfile2.txt")
        self.assertFalse(os.path.exists(testfile2))
        os.symlink(testfile1, testfile2)
        self.assertTrue(os.path.exists(testfile2))

        os.unlink(testfile1)
        self.assertFalse(os.path.exists(testfile1))
        self.assertTrue(path_utils.is_path_broken_symlink(testfile2))

        testfile2_gz = testfile2 + ".gz"
        self.assertFalse(os.path.exists(testfile2_gz))

        v, r = gzip_wrapper.compress(testfile2)
        self.assertFalse(v) # gzip 1.10 (of L21) does not support broken symlinks
        self.assertFalse(os.path.exists(testfile2_gz))

    def testGzipWrapperCompressAndDecompressFails(self):

        v, r = tar_wrapper.make_pack(self.tar_file, [self.file1])
        self.assertTrue(v)

        self.assertTrue(os.path.exists(self.tar_file))
        self.assertFalse(os.path.exists(self.tar_gz_file))

        v, r = gzip_wrapper.compress(self.tar_file)
        self.assertTrue(v)

        self.assertFalse(os.path.exists(self.tar_file))
        self.assertTrue(os.path.exists(self.tar_gz_file))

        create_and_write_file.create_file_contents(self.tar_file, "fake archive")
        self.assertTrue(os.path.exists(self.tar_file))

        v, r = gzip_wrapper.decompress(self.tar_gz_file)
        self.assertFalse(v)

        self.assertTrue(os.path.exists(self.tar_file))
        self.assertTrue(os.path.exists(self.tar_gz_file))

if __name__ == '__main__':
    unittest.main()
