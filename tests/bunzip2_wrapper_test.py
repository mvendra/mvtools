#!/usr/bin/env python3

import sys
import os
import shutil
import unittest

import mvtools_test_fixture
import create_and_write_file
import path_utils

import tar_wrapper
import bzip2_wrapper
import bunzip2_wrapper
import sha512_wrapper

class Bunzip2WrapperTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("bunzip2_wrapper_test_base")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # the target tar file
        self.tar_file = path_utils.concat_path(self.test_dir, "test.tar")
        self.tar_file_with_space_1 = path_utils.concat_path(self.test_dir, "te st.tar")
        self.tar_file_with_space_2 = path_utils.concat_path(self.test_dir, "   test.tar")
        self.tar_file_with_space_3 = path_utils.concat_path(self.test_dir, "test.tar   ")

        # create test content
        self.file_nonexistant = path_utils.concat_path(self.test_dir, "no_file")

        # base, files
        self.file1 = path_utils.concat_path(self.test_dir, "file1.txt")
        create_and_write_file.create_file_contents(self.file1, "abc")

        v, r = tar_wrapper.make_pack(self.tar_file, [self.file1])
        if not v:
            return v, r

        v, r = tar_wrapper.make_pack(self.tar_file_with_space_1, [self.file1])
        if not v:
            return v, r

        v, r = tar_wrapper.make_pack(self.tar_file_with_space_2, [self.file1])
        if not v:
            return v, r

        v, r = tar_wrapper.make_pack(self.tar_file_with_space_3, [self.file1])
        if not v:
            return v, r

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testPrecheck(self):
        v, r = bunzip2_wrapper.decompress(self.file_nonexistant)
        self.assertFalse(v)

    def testCompress1(self):

        v, r = sha512_wrapper.hash_sha_512_app_file(self.tar_file)
        self.assertTrue(v)
        hash = r

        v, r = bzip2_wrapper.compress(self.tar_file)
        self.assertTrue(v)

        tar_bz_file = self.tar_file + ".bz2"
        self.assertTrue(os.path.exists(tar_bz_file))

        self.assertFalse( os.path.exists(self.tar_file) )

        v, r = bunzip2_wrapper.decompress(tar_bz_file)
        self.assertTrue(v)

        v, r = sha512_wrapper.hash_sha_512_app_file(self.tar_file)
        self.assertTrue(v)
        self.assertEqual(r, hash)

    def testCompress2(self):

        v, r = sha512_wrapper.hash_sha_512_app_file(self.tar_file_with_space_1)
        self.assertTrue(v)
        hash = r

        v, r = bzip2_wrapper.compress(self.tar_file_with_space_1)
        self.assertTrue(v)

        tar_bz_file_with_space = self.tar_file_with_space_1 + ".bz2"
        self.assertTrue(os.path.exists(tar_bz_file_with_space))

        self.assertFalse( os.path.exists(self.tar_file_with_space_1) )

        v, r = bunzip2_wrapper.decompress(tar_bz_file_with_space)
        self.assertTrue(v)

        v, r = sha512_wrapper.hash_sha_512_app_file(self.tar_file_with_space_1)
        self.assertTrue(v)
        self.assertEqual(r, hash)

    def testCompress3(self):

        v, r = sha512_wrapper.hash_sha_512_app_file(self.tar_file_with_space_2)
        self.assertTrue(v)
        hash = r

        v, r = bzip2_wrapper.compress(self.tar_file_with_space_2)
        self.assertTrue(v)

        tar_bz_file_with_space = self.tar_file_with_space_2 + ".bz2"
        self.assertTrue(os.path.exists(tar_bz_file_with_space))

        self.assertFalse( os.path.exists(self.tar_file_with_space_2) )

        v, r = bunzip2_wrapper.decompress(tar_bz_file_with_space)
        self.assertTrue(v)

        v, r = sha512_wrapper.hash_sha_512_app_file(self.tar_file_with_space_2)
        self.assertTrue(v)
        self.assertEqual(r, hash)

    def testCompress4(self):

        v, r = sha512_wrapper.hash_sha_512_app_file(self.tar_file_with_space_3)
        self.assertTrue(v)
        hash = r

        v, r = bzip2_wrapper.compress(self.tar_file_with_space_3)
        self.assertTrue(v)

        tar_bz_file_with_space = self.tar_file_with_space_3 + ".bz2"
        self.assertTrue(os.path.exists(tar_bz_file_with_space))

        self.assertFalse( os.path.exists(self.tar_file_with_space_3) )

        v, r = bunzip2_wrapper.decompress(tar_bz_file_with_space)
        self.assertTrue(v)

        v, r = sha512_wrapper.hash_sha_512_app_file(self.tar_file_with_space_3)
        self.assertTrue(v)
        self.assertEqual(r, hash)

if __name__ == '__main__':
    unittest.main()
