#!/usr/bin/env python3

import sys
import os
import shutil
import unittest

import mvtools_test_fixture
import create_and_write_file
import path_utils

import sha512_wrapper

class Sha512WrapperTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        self.internal_counter = 0

        v, r = mvtools_test_fixture.makeAndGetTestFolder("sha512_wrapper_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        self.content1 = "thenotsoquickyellowfoxwagsitstailthencirclesaroundthebluecat"
        self.filename1 = path_utils.concat_path(self.test_dir, "file.txt")
        create_and_write_file.create_file_contents(self.filename1, self.content1)
        self.content1_sha512 = "b5011e56ea61610e6dc76c6cd63dd43252c215c0250dcfeb343c8853cabb1413aeb1c8bcb17ca49240ec977a82fb444b0f6a85a949d7e3edc2d11af13ced1c23"

        self.content2 = "thenotsoquickyellowfoxwagsitstailthencirclesaroundthebluedonkey"
        self.filename2 = path_utils.concat_path(self.test_dir, "fi le.txt")
        create_and_write_file.create_file_contents(self.filename2, self.content2)
        self.content2_sha512 = "2df9e207e4dd719e28d39f01f646f03357329e444481e09f5ca7a4743813d3bd7590ff4861e457ddd041f739cfcffd7e82f872ad9dc6045d223a6599feffd80c"

        self.content3 = "thenotsoquickorangefoxwagsitstailthensquaresaroundthebluewren"
        self.filename3 = path_utils.concat_path(self.test_dir, "   file.txt")
        create_and_write_file.create_file_contents(self.filename3, self.content3)
        self.content3_sha512 = "3c3afbee7a24dcdbe430508e6079d95b475884e873ad5c82c8e0bfb7d120633976ae4e218969df473810f03c45a887c63d9aa71371cd9acdef0a8bba41ec9475"

        self.content4 = "thenotsoquickvelvetfoxwagsitstailthensquaresaroundthebluegiraffe"
        self.filename4 = path_utils.concat_path(self.test_dir, "file.txt   ")
        create_and_write_file.create_file_contents(self.filename4, self.content4)
        self.content4_sha512 = "173da3e3133de7761d6b06745980805c278ee577f1cfbe122e6fda5d1238eb768e2c5edc837dcfa82e93fd4e09391614d14edd161e56ca83ab939365436e3cc4"

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testHash512AppContent1(self):
        v, r = sha512_wrapper.hash_sha_512_app_content(self.content1)
        self.assertTrue(v)
        self.assertEqual(r, self.content1_sha512)

    def testHash512AppFile1(self):
        v, r = sha512_wrapper.hash_sha_512_app_file(self.filename1)
        self.assertTrue(v)
        self.assertEqual(r, self.content1_sha512)

    def testHash512AppContent2(self):
        v, r = sha512_wrapper.hash_sha_512_app_content(self.content2)
        self.assertTrue(v)
        self.assertEqual(r, self.content2_sha512)

    def testHash512AppFile2(self):
        v, r = sha512_wrapper.hash_sha_512_app_file(self.filename2)
        self.assertTrue(v)
        self.assertEqual(r, self.content2_sha512)

    def testHash512AppFile3(self):
        v, r = sha512_wrapper.hash_sha_512_app_file(self.filename3)
        self.assertTrue(v)
        self.assertEqual(r, self.content3_sha512)

    def testHash512AppFile4(self):
        v, r = sha512_wrapper.hash_sha_512_app_file(self.filename4)
        self.assertTrue(v)
        self.assertEqual(r, self.content4_sha512)

    def testHash512AppFile5(self):
        v, r = sha512_wrapper.hash_sha_512_app_file(self.filename1)
        self.assertTrue(v)
        self.assertNotEqual(r, "not-the-right-hash")

    def testHash512AppFile6(self):

        blanksub = path_utils.concat_path(self.test_dir, " ")
        self.assertFalse(os.path.exists(blanksub))
        os.mkdir(blanksub)
        self.assertTrue(os.path.exists(blanksub))

        blanksub_blankfn = path_utils.concat_path(blanksub, " ")
        self.assertFalse(os.path.exists(blanksub_blankfn))
        create_and_write_file.create_file_contents(blanksub_blankfn, self.content1)
        self.assertTrue(os.path.exists(blanksub_blankfn))

        v, r = sha512_wrapper.hash_sha_512_app_file(blanksub_blankfn)
        self.assertTrue(v)
        self.assertEqual(r, self.content1_sha512)

if __name__ == '__main__':
    unittest.main()
