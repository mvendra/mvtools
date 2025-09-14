#!/usr/bin/env python

import sys
import os
import shutil
import unittest
from unittest import mock
from unittest.mock import patch

import path_utils
import create_and_write_file
import mvtools_test_fixture

import openssl_wrapper

class OpensslWrapperTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("openssl_wrapper_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        self.file1 = path_utils.concat_path(self.test_dir, "file1.txt")
        self.file2 = path_utils.concat_path(self.test_dir, "file2.txt.enc")
        self.file3 = path_utils.concat_path(self.test_dir, "file3.txt")

        self.nonexistent_path1 = path_utils.concat_path(self.test_dir, "nonexistent_path")

        self.test_passphrase = "test-passphrase"

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testEncryptDes3Pbkdf2_1(self):

        with mock.patch("generic_run.run_cmd_simple", return_value=(True, "")) as dummy:
            self.assertEqual(openssl_wrapper.encrypt_des3_pbkdf2(self.file1, self.file2, self.test_passphrase), (False, "%s does not exist." % self.file1))
            dummy.assert_not_called()

    def testEncryptDes3Pbkdf2_2(self):

        os.mkdir(self.file1)

        with mock.patch("generic_run.run_cmd_simple", return_value=(True, "")) as dummy:
            self.assertEqual(openssl_wrapper.encrypt_des3_pbkdf2(self.file1, self.file2, self.test_passphrase), (False, "%s is not a file." % self.file1))
            dummy.assert_not_called()

    def testEncryptDes3Pbkdf2_3(self):

        create_and_write_file.create_file_contents(self.file1, "xyz")

        with mock.patch("generic_run.run_cmd_simple", return_value=(True, "")) as dummy:
            self.assertEqual(openssl_wrapper.encrypt_des3_pbkdf2(self.file1, "", self.test_passphrase), (False, "Invalid output filename."))
            dummy.assert_not_called()

    def testEncryptDes3Pbkdf2_4(self):

        create_and_write_file.create_file_contents(self.file1, "xyz")

        with mock.patch("generic_run.run_cmd_simple", return_value=(True, "")) as dummy:
            self.assertEqual(openssl_wrapper.encrypt_des3_pbkdf2(self.file1, None, self.test_passphrase), (False, "Invalid output filename."))
            dummy.assert_not_called()

    def testEncryptDes3Pbkdf2_5(self):

        create_and_write_file.create_file_contents(self.file1, "xyz")
        create_and_write_file.create_file_contents(self.file2, "xyz")

        with mock.patch("generic_run.run_cmd_simple", return_value=(True, "")) as dummy:
            self.assertEqual(openssl_wrapper.encrypt_des3_pbkdf2(self.file1, self.file2, self.test_passphrase), (False, "%s already exists." % self.file2))
            dummy.assert_not_called()

    def testEncryptDes3Pbkdf2_6(self):

        create_and_write_file.create_file_contents(self.file1, "xyz")

        with mock.patch("generic_run.run_cmd_simple", return_value=(True, "")) as dummy:
            self.assertEqual(openssl_wrapper.encrypt_des3_pbkdf2(self.file1, self.file2, ""), (False, "Invalid passphrase."))
            dummy.assert_not_called()

    def testEncryptDes3Pbkdf2_7(self):

        create_and_write_file.create_file_contents(self.file1, "xyz")

        with mock.patch("generic_run.run_cmd_simple", return_value=(True, "")) as dummy:
            self.assertEqual(openssl_wrapper.encrypt_des3_pbkdf2(self.file1, self.file2, None), (False, "Invalid passphrase."))
            dummy.assert_not_called()

    def testEncryptDes3Pbkdf2_8(self):

        create_and_write_file.create_file_contents(self.file1, "xyz")

        with mock.patch("generic_run.run_cmd_simple", return_value=(True, "")) as dummy:
            self.assertEqual(openssl_wrapper.encrypt_des3_pbkdf2(self.file1, self.file2, self.test_passphrase), (True, None))
            dummy.assert_called_with(["openssl", "des3", "-e", "-pbkdf2", "-in", self.file1, "-out", self.file2, "-k", self.test_passphrase])

    def testDecryptDes3Pbkdf2_1(self):

        with mock.patch("generic_run.run_cmd_simple", return_value=(True, "")) as dummy:
            self.assertEqual(openssl_wrapper.decrypt_des3_pbkdf2(self.file1, self.file2, self.test_passphrase), (False, "%s does not exist." % self.file1))
            dummy.assert_not_called()

    def testDecryptDes3Pbkdf2_2(self):

        create_and_write_file.create_file_contents(self.file1, "xyz")

        with mock.patch("generic_run.run_cmd_simple", return_value=(True, "")) as dummy:
            self.assertEqual(openssl_wrapper.decrypt_des3_pbkdf2(self.file1, "", self.test_passphrase), (False, "Invalid output filename."))
            dummy.assert_not_called()

    def testDecryptDes3Pbkdf2_3(self):

        create_and_write_file.create_file_contents(self.file1, "xyz")

        with mock.patch("generic_run.run_cmd_simple", return_value=(True, "")) as dummy:
            self.assertEqual(openssl_wrapper.decrypt_des3_pbkdf2(self.file1, None, self.test_passphrase), (False, "Invalid output filename."))
            dummy.assert_not_called()

    def testDecryptDes3Pbkdf2_4(self):

        create_and_write_file.create_file_contents(self.file1, "xyz")
        create_and_write_file.create_file_contents(self.file2, "xyz")

        with mock.patch("generic_run.run_cmd_simple", return_value=(True, "")) as dummy:
            self.assertEqual(openssl_wrapper.decrypt_des3_pbkdf2(self.file1, self.file2, self.test_passphrase), (False, "%s already exists." % self.file2))
            dummy.assert_not_called()

    def testDecryptDes3Pbkdf2_5(self):

        create_and_write_file.create_file_contents(self.file1, "xyz")

        with mock.patch("generic_run.run_cmd_simple", return_value=(True, "")) as dummy:
            self.assertEqual(openssl_wrapper.decrypt_des3_pbkdf2(self.file1, self.file2, ""), (False, "Invalid passphrase."))
            dummy.assert_not_called()

    def testDecryptDes3Pbkdf2_6(self):

        create_and_write_file.create_file_contents(self.file1, "xyz")

        with mock.patch("generic_run.run_cmd_simple", return_value=(True, "")) as dummy:
            self.assertEqual(openssl_wrapper.decrypt_des3_pbkdf2(self.file1, self.file2, None), (False, "Invalid passphrase."))
            dummy.assert_not_called()

    def testDecryptDes3Pbkdf2_7(self):

        create_and_write_file.create_file_contents(self.file1, "xyz")

        with mock.patch("generic_run.run_cmd_simple", return_value=(True, "")) as dummy:
            self.assertEqual(openssl_wrapper.decrypt_des3_pbkdf2(self.file1, self.file2, self.test_passphrase), (True, None))
            dummy.assert_called_with(["openssl", "des3", "-d", "-pbkdf2", "-in", self.file1, "-out", self.file2, "-k", self.test_passphrase])

    def testEncryptDes3Pbkdf2_DecryptDes3Pbkdf2(self):

        create_and_write_file.create_file_contents(self.file1, "xyz")

        self.assertEqual(openssl_wrapper.encrypt_des3_pbkdf2(self.file1, self.file2, self.test_passphrase), (True, None))
        self.assertEqual(openssl_wrapper.decrypt_des3_pbkdf2(self.file2, self.file3, self.test_passphrase), (True, None))

        contents_file1 = ""
        contents_file3 = ""

        with open(self.file1, "r") as f:
            contents_file1 = f.read()

        with open(self.file3, "r") as f:
            contents_file3 = f.read()

        self.assertEqual(contents_file1, contents_file3)

if __name__ == "__main__":
    unittest.main()
