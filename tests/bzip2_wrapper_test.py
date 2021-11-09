#!/usr/bin/env python3

import sys
import os
import shutil
import unittest

import mvtools_test_fixture
import create_and_write_file
import path_utils
import sha512_wrapper
import tar_wrapper

import bzip2_wrapper

class Bzip2WrapperTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("bzip2_wrapper_test")
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

    def testCompressPrecheck(self):
        v, r = bzip2_wrapper.compress(self.file_nonexistant)
        self.assertFalse(v)

    def testCompress1(self):
        v, r = bzip2_wrapper.compress(self.tar_file)
        self.assertTrue(v)
        tar_bz_file = self.tar_file + ".bz2"
        self.assertTrue(os.path.exists(tar_bz_file))

    def testCompress2(self):
        v, r = bzip2_wrapper.compress(self.tar_file_with_space_1)
        self.assertTrue(v)
        tar_bz_file_with_space = self.tar_file_with_space_1 + ".bz2"
        self.assertTrue(os.path.exists(tar_bz_file_with_space))

    def testCompress3(self):
        v, r = bzip2_wrapper.compress(self.tar_file_with_space_2)
        self.assertTrue(v)
        tar_bz_file_with_space = self.tar_file_with_space_2 + ".bz2"
        self.assertTrue(os.path.exists(tar_bz_file_with_space))

    def testCompress4(self):
        v, r = bzip2_wrapper.compress(self.tar_file_with_space_3)
        self.assertTrue(v)
        tar_bz_file_with_space = self.tar_file_with_space_3 + ".bz2"
        self.assertTrue(os.path.exists(tar_bz_file_with_space))

    def testDecompress1(self):

        v, r = sha512_wrapper.hash_sha_512_app_file(self.tar_file)
        self.assertTrue(v)
        hash = r

        v, r = bzip2_wrapper.compress(self.tar_file)
        self.assertTrue(v)

        tar_bz_file = self.tar_file + ".bz2"
        self.assertTrue(os.path.exists(tar_bz_file))

        self.assertFalse( os.path.exists(self.tar_file) )

        v, r = bzip2_wrapper.decompress(tar_bz_file)
        self.assertTrue(v)

        v, r = sha512_wrapper.hash_sha_512_app_file(self.tar_file)
        self.assertTrue(v)
        self.assertEqual(r, hash)

    def testDecompress2(self):

        v, r = sha512_wrapper.hash_sha_512_app_file(self.tar_file_with_space_1)
        self.assertTrue(v)
        hash = r

        v, r = bzip2_wrapper.compress(self.tar_file_with_space_1)
        self.assertTrue(v)

        tar_bz_file_with_space = self.tar_file_with_space_1 + ".bz2"
        self.assertTrue(os.path.exists(tar_bz_file_with_space))

        self.assertFalse( os.path.exists(self.tar_file_with_space_1) )

        v, r = bzip2_wrapper.decompress(tar_bz_file_with_space)
        self.assertTrue(v)

        v, r = sha512_wrapper.hash_sha_512_app_file(self.tar_file_with_space_1)
        self.assertTrue(v)
        self.assertEqual(r, hash)

    def testDecompress3(self):

        v, r = sha512_wrapper.hash_sha_512_app_file(self.tar_file_with_space_2)
        self.assertTrue(v)
        hash = r

        v, r = bzip2_wrapper.compress(self.tar_file_with_space_2)
        self.assertTrue(v)

        tar_bz_file_with_space = self.tar_file_with_space_2 + ".bz2"
        self.assertTrue(os.path.exists(tar_bz_file_with_space))

        self.assertFalse( os.path.exists(self.tar_file_with_space_2) )

        v, r = bzip2_wrapper.decompress(tar_bz_file_with_space)
        self.assertTrue(v)

        v, r = sha512_wrapper.hash_sha_512_app_file(self.tar_file_with_space_2)
        self.assertTrue(v)
        self.assertEqual(r, hash)

    def testDecompress4(self):

        v, r = sha512_wrapper.hash_sha_512_app_file(self.tar_file_with_space_3)
        self.assertTrue(v)
        hash = r

        v, r = bzip2_wrapper.compress(self.tar_file_with_space_3)
        self.assertTrue(v)

        tar_bz_file_with_space = self.tar_file_with_space_3 + ".bz2"
        self.assertTrue(os.path.exists(tar_bz_file_with_space))

        self.assertFalse( os.path.exists(self.tar_file_with_space_3) )

        v, r = bzip2_wrapper.decompress(tar_bz_file_with_space)
        self.assertTrue(v)

        v, r = sha512_wrapper.hash_sha_512_app_file(self.tar_file_with_space_3)
        self.assertTrue(v)
        self.assertEqual(r, hash)

    def testCompressAndDecompress_BlankFilename(self):

        blanksub = path_utils.concat_path(self.test_dir, " ")
        self.assertFalse(os.path.exists(blanksub))
        os.mkdir(blanksub)
        self.assertTrue(os.path.exists(blanksub))

        blankfile = path_utils.concat_path(blanksub, " ")
        self.assertFalse(os.path.exists(blankfile))
        self.assertTrue(create_and_write_file.create_file_contents(blankfile, "abc"))
        self.assertTrue(os.path.exists(blankfile))

        blankfile_bz = blankfile + ".bz2"
        self.assertFalse(os.path.exists(blankfile_bz))
        v, r = bzip2_wrapper.compress(blankfile)
        self.assertTrue(v)
        self.assertTrue(os.path.exists(blankfile_bz))
        self.assertFalse(os.path.exists(blankfile))

        v, r = bzip2_wrapper.decompress(blankfile_bz)
        self.assertTrue(v)
        self.assertFalse(os.path.exists(blankfile_bz))
        self.assertTrue(os.path.exists(blankfile))

        with open(blankfile, "r") as f:
            self.assertTrue("abc" in f.read())

    def testCompressAndDecompress_BrokenSymlink(self):

        test_source_file = path_utils.concat_path(self.test_dir, "test_source_file.txt")
        self.assertFalse(os.path.exists(test_source_file))
        self.assertTrue(create_and_write_file.create_file_contents(test_source_file, "abc"))
        self.assertTrue(os.path.exists(test_source_file))

        test_source_link = path_utils.concat_path(self.test_dir, "test_source_link.txt")
        self.assertFalse(os.path.exists(test_source_link))
        os.symlink(test_source_file, test_source_link)
        self.assertTrue(os.path.exists(test_source_link))

        os.unlink(test_source_file)
        self.assertFalse(os.path.exists(test_source_file))
        self.assertTrue(path_utils.is_path_broken_symlink(test_source_link))

        test_source_link_bz = test_source_link + ".bz2"
        self.assertFalse(os.path.exists(test_source_link_bz))
        v, r = bzip2_wrapper.compress(test_source_link)
        self.assertFalse(v) # bzip2 version 1.0.8 does not support broken symlinks
        self.assertFalse(os.path.exists(test_source_link_bz))
        self.assertTrue(path_utils.is_path_broken_symlink(test_source_link))

if __name__ == '__main__':
    unittest.main()
