#!/usr/bin/env python3

import sys
import os
import stat
import shutil
import unittest
from unittest import mock
from unittest.mock import patch

import create_and_write_file
import mvtools_test_fixture

import backup_preparation

import path_utils

class BackupPreparationTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("backup_preparation_test")
        if not v:
            return v, r
        self.test_base_dir = r[0]
        self.test_dir = r[1]

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testConvertToByteFail(self):
        self.assertEqual(backup_preparation.convert_to_bytes("1b"), (False, None))
        self.assertEqual(backup_preparation.convert_to_bytes("50bb"), (False, None))
        self.assertEqual(backup_preparation.convert_to_bytes("abc"), (False, None))
        self.assertEqual(backup_preparation.convert_to_bytes(""), (False, None))

    def testConvertToByteSuccess(self):
        self.assertEqual(backup_preparation.convert_to_bytes("50"), (True, 50))
        self.assertEqual(backup_preparation.convert_to_bytes("1024"), (True, 1024))
        self.assertEqual(backup_preparation.convert_to_bytes("1kb"), (True, 1024))
        self.assertEqual(backup_preparation.convert_to_bytes("20kb"), (True, 20480))
        self.assertEqual(backup_preparation.convert_to_bytes("1mb"), (True, 1048576))
        self.assertEqual(backup_preparation.convert_to_bytes("20mb"), (True, 20971520))
        self.assertEqual(backup_preparation.convert_to_bytes("1gb"), (True, 1073741824))
        self.assertEqual(backup_preparation.convert_to_bytes("1tb"), (True, 1073741824*1024))

if __name__ == '__main__':
    unittest.main()
