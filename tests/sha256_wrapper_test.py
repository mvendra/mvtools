#!/usr/bin/env python3

import sys
import os
import shutil
import unittest

import mvtools_test_fixture
import create_and_write_file

import sha256_wrapper

class HashAlgosTest(unittest.TestCase):

    def makeFilename(self):
        self.internal_counter += 1
        filename = "testfile_%s.txt" % self.internal_counter
        return filename

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        self.internal_counter = 0

        v, r = mvtools_test_fixture.makeAndGetTestFolder("sha256_wrapper_test_base")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        self.content1 = "thenotsoquickyellowfoxwagsitstailthencirclesaroundthebluecat"
        self.filename1 = os.path.join(self.test_dir, self.makeFilename())
        create_and_write_file.create_file_contents(self.filename1, self.content1)

        self.content1_sha256 = "735e24cec929ca91d81076fb56bed40642a3b0c5f8fe3b1a4d98b425dadc8c99"

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testHash256AppContent(self):
        v, r = sha256_wrapper.hash_sha_256_app_content(self.content1)
        self.assertTrue(v)
        self.assertEqual(r, self.content1_sha256)

    def testHash256AppFile(self):
        v, r = sha256_wrapper.hash_sha_256_app_file(self.filename1)
        self.assertTrue(v)
        self.assertEqual(r, self.content1_sha256)

if __name__ == '__main__':
    unittest.main()
