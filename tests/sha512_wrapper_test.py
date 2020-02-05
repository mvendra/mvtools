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

        v, r = mvtools_test_fixture.makeAndGetTestFolder("sha512_wrapper_test_base")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        self.content1 = "thenotsoquickyellowfoxwagsitstailthencirclesaroundthebluecat"
        self.filename1 = os.path.join(self.test_dir, path_utils.filter_join_abs("file.txt") )
        create_and_write_file.create_file_contents(self.filename1, self.content1)
        self.content1_sha512 = "b5011e56ea61610e6dc76c6cd63dd43252c215c0250dcfeb343c8853cabb1413aeb1c8bcb17ca49240ec977a82fb444b0f6a85a949d7e3edc2d11af13ced1c23"

        self.content2 = "thenotsoquickyellowfoxwagsitstailthencirclesaroundthebluedonkey"
        self.filename2 = os.path.join(self.test_dir, path_utils.filter_join_abs("fi le.txt") )
        create_and_write_file.create_file_contents(self.filename2, self.content2)
        self.content2_sha512 = "2df9e207e4dd719e28d39f01f646f03357329e444481e09f5ca7a4743813d3bd7590ff4861e457ddd041f739cfcffd7e82f872ad9dc6045d223a6599feffd80c"

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

if __name__ == '__main__':
    unittest.main()
