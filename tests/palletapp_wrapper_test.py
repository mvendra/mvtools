#!/usr/bin/env python

import sys
import os
import shutil
import unittest
from unittest import mock
from unittest.mock import patch

import mvtools_test_fixture
import create_and_write_file
import path_utils

import palletapp_wrapper

class PalletappWrapperTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("palletapp_wrapper_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # test contents
        self.pallet_file = "test.plt"
        self.pallet_file_full = path_utils.concat_path(self.test_dir, self.pallet_file)

        self.test_folder = "test_folder"
        self.test_folder_full = path_utils.concat_path(self.test_dir, self.test_folder)

        self.test_file1 = "test_file1"
        self.test_file1_full = path_utils.concat_path(self.test_dir, self.test_file1)

        self.test_file2 = "test_file2"
        self.test_file2_full = path_utils.concat_path(self.test_dir, self.test_file2)

        self.nonexistent_file = "nonexistent_file"
        self.nonexistent_file_full = path_utils.concat_path(self.test_dir, self.nonexistent_file)

        os.mkdir(self.test_folder_full)
        create_and_write_file.create_file_contents(self.test_file1_full, "file1 contents")
        create_and_write_file.create_file_contents(self.test_file2_full, "file2 contents")

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testInit1(self):

        with mock.patch("generic_run.run_cmd_simple", return_value=(True, None)) as dummy:
            v, r = palletapp_wrapper.init(None)
            self.assertFalse(v)
            self.assertEqual(r, "Invalid target archive path")
            dummy.assert_not_called()

    def testInit2(self):

        create_and_write_file.create_file_contents(self.pallet_file_full, "test contents")

        with mock.patch("generic_run.run_cmd_simple", return_value=(True, None)) as dummy:
            v, r = palletapp_wrapper.init(self.pallet_file_full)
            self.assertFalse(v)
            self.assertEqual(r, "[%s] already exists." % self.pallet_file_full)
            dummy.assert_not_called()

    def testInit3(self):

        with mock.patch("generic_run.run_cmd_simple", return_value=(True, None)) as dummy:
            v, r = palletapp_wrapper.init(self.pallet_file_full)
            self.assertTrue(v)
            dummy.assert_called_with(["palletapp", "--init", self.pallet_file_full])

    def testInit4(self):

        with mock.patch("generic_run.run_cmd_simple", return_value=(False, "test error")) as dummy:
            v, r = palletapp_wrapper.init(self.pallet_file_full)
            self.assertFalse(v)
            self.assertEqual(r, "Failed running palletapp init command: [test error]")
            dummy.assert_called_with(["palletapp", "--init", self.pallet_file_full])

    def testCreate1(self):

        with mock.patch("generic_run.run_cmd_simple", return_value=(True, None)) as dummy:
            v, r = palletapp_wrapper.create(None, self.test_file1_full)
            self.assertFalse(v)
            self.assertEqual(r, "Invalid target archive path")
            dummy.assert_not_called()

    def testCreate2(self):

        create_and_write_file.create_file_contents(self.pallet_file_full, "test contents")

        with mock.patch("generic_run.run_cmd_simple", return_value=(True, None)) as dummy:
            v, r = palletapp_wrapper.create(self.pallet_file_full, self.test_file1_full)
            self.assertFalse(v)
            self.assertEqual(r, "[%s] already exists." % self.pallet_file_full)
            dummy.assert_not_called()

    def testCreate3(self):

        with mock.patch("generic_run.run_cmd_simple", return_value=(True, None)) as dummy:
            v, r = palletapp_wrapper.create(self.pallet_file_full, None)
            self.assertFalse(v)
            self.assertEqual(r, "Invalid source path")
            dummy.assert_not_called()

    def testCreate4(self):

        os.unlink(self.test_file1_full)

        with mock.patch("generic_run.run_cmd_simple", return_value=(True, None)) as dummy:
            v, r = palletapp_wrapper.create(self.pallet_file_full, self.test_file1_full)
            self.assertFalse(v)
            self.assertEqual(r, "[%s] does not exist." % self.test_file1_full)
            dummy.assert_not_called()

    def testCreate5(self):

        with mock.patch("generic_run.run_cmd_simple", return_value=(True, None)) as dummy:
            v, r = palletapp_wrapper.create(self.pallet_file_full, self.test_file1_full)
            self.assertTrue(v)
            dummy.assert_called_with(["palletapp", "--create", self.pallet_file_full, self.test_file1_full])

    def testExtract1(self):

        create_and_write_file.create_file_contents(self.pallet_file_full, "test contents")

        with mock.patch("generic_run.run_cmd_simple", return_value=(True, None)) as dummy:
            v, r = palletapp_wrapper.extract(None, self.test_folder_full)
            self.assertFalse(v)
            self.assertEqual(r, "Invalid source archive")
            dummy.assert_not_called()

    def testExtract2(self):

        with mock.patch("generic_run.run_cmd_simple", return_value=(True, None)) as dummy:
            v, r = palletapp_wrapper.extract(self.pallet_file_full, self.test_folder_full)
            self.assertFalse(v)
            self.assertEqual(r, "[%s] does not exist." % self.pallet_file_full)
            dummy.assert_not_called()

    def testExtract3(self):

        create_and_write_file.create_file_contents(self.pallet_file_full, "test contents")

        with mock.patch("generic_run.run_cmd_simple", return_value=(True, None)) as dummy:
            v, r = palletapp_wrapper.extract(self.pallet_file_full, None)
            self.assertFalse(v)
            self.assertEqual(r, "Invalid target path")
            dummy.assert_not_called()

    def testExtract4(self):

        create_and_write_file.create_file_contents(self.pallet_file_full, "test contents")
        shutil.rmtree(self.test_folder_full)

        with mock.patch("generic_run.run_cmd_simple", return_value=(True, None)) as dummy:
            v, r = palletapp_wrapper.extract(self.pallet_file_full, self.test_folder_full)
            self.assertFalse(v)
            self.assertEqual(r, "[%s] does not exist." % self.test_folder_full)
            dummy.assert_not_called()

    def testExtract5(self):

        create_and_write_file.create_file_contents(self.pallet_file_full, "test contents")
        shutil.rmtree(self.test_folder_full)
        create_and_write_file.create_file_contents(self.test_folder_full, "folder impostor")

        with mock.patch("generic_run.run_cmd_simple", return_value=(True, None)) as dummy:
            v, r = palletapp_wrapper.extract(self.pallet_file_full, self.test_folder_full)
            self.assertFalse(v)
            self.assertEqual(r, "[%s] is not a folder." % self.test_folder_full)
            dummy.assert_not_called()

    def testExtract6(self):

        create_and_write_file.create_file_contents(self.pallet_file_full, "test contents")

        with mock.patch("generic_run.run_cmd_simple", return_value=(True, None)) as dummy:
            v, r = palletapp_wrapper.extract(self.pallet_file_full, self.test_folder_full)
            self.assertTrue(v)
            dummy.assert_called_with(["palletapp", "--extract", self.pallet_file_full, self.test_folder_full])

    def testExtract7(self):

        create_and_write_file.create_file_contents(self.pallet_file_full, "test contents")

        with mock.patch("generic_run.run_cmd_simple", return_value=(False, "test error")) as dummy:
            v, r = palletapp_wrapper.extract(self.pallet_file_full, self.test_folder_full)
            self.assertFalse(v)
            self.assertEqual(r, "Failed running palletapp extract command: [test error]")
            dummy.assert_called_with(["palletapp", "--extract", self.pallet_file_full, self.test_folder_full])

    def testLoad1(self):

        create_and_write_file.create_file_contents(self.pallet_file_full, "test contents")

        with mock.patch("generic_run.run_cmd_simple", return_value=(True, None)) as dummy:
            v, r = palletapp_wrapper.load(None, self.test_file1_full)
            self.assertFalse(v)
            self.assertEqual(r, "Invalid target archive path")
            dummy.assert_not_called()

    def testLoad2(self):

        with mock.patch("generic_run.run_cmd_simple", return_value=(True, None)) as dummy:
            v, r = palletapp_wrapper.load(self.pallet_file_full, self.test_file1_full)
            self.assertFalse(v)
            self.assertEqual(r, "[%s] does not exist." % self.pallet_file_full)
            dummy.assert_not_called()

    def testLoad3(self):

        create_and_write_file.create_file_contents(self.pallet_file_full, "test contents")

        with mock.patch("generic_run.run_cmd_simple", return_value=(True, None)) as dummy:
            v, r = palletapp_wrapper.load(self.pallet_file_full, None)
            self.assertFalse(v)
            self.assertEqual(r, "Invalid source path")
            dummy.assert_not_called()

    def testLoad4(self):

        create_and_write_file.create_file_contents(self.pallet_file_full, "test contents")
        os.unlink(self.test_file1_full)

        with mock.patch("generic_run.run_cmd_simple", return_value=(True, None)) as dummy:
            v, r = palletapp_wrapper.load(self.pallet_file_full, self.test_file1_full)
            self.assertFalse(v)
            self.assertEqual(r, "[%s] does not exist." % self.test_file1_full)
            dummy.assert_not_called()

    def testLoad5(self):

        create_and_write_file.create_file_contents(self.pallet_file_full, "test contents")

        with mock.patch("generic_run.run_cmd_simple", return_value=(True, None)) as dummy:
            v, r = palletapp_wrapper.load(self.pallet_file_full, self.test_file1_full)
            self.assertTrue(v)
            dummy.assert_called_with(["palletapp", "--load", self.pallet_file_full, self.test_file1_full])

    def testLoad6(self):

        create_and_write_file.create_file_contents(self.pallet_file_full, "test contents")

        with mock.patch("generic_run.run_cmd_simple", return_value=(False, "test error")) as dummy:
            v, r = palletapp_wrapper.load(self.pallet_file_full, self.test_file1_full)
            self.assertFalse(v)
            self.assertEqual(r, "Failed running palletapp load command: [test error]")
            dummy.assert_called_with(["palletapp", "--load", self.pallet_file_full, self.test_file1_full])

    def testDitch1(self):

        create_and_write_file.create_file_contents(self.pallet_file_full, "test contents")

        with mock.patch("generic_run.run_cmd_simple", return_value=(True, None)) as dummy:
            v, r = palletapp_wrapper.ditch(None, self.test_file1_full)
            self.assertFalse(v)
            self.assertEqual(r, "Invalid source archive")
            dummy.assert_not_called()

    def testDitch2(self):

        with mock.patch("generic_run.run_cmd_simple", return_value=(True, None)) as dummy:
            v, r = palletapp_wrapper.ditch(self.pallet_file_full, self.test_file1_full)
            self.assertFalse(v)
            self.assertEqual(r, "[%s] does not exist." % self.pallet_file_full)
            dummy.assert_not_called()

    def testDitch3(self):

        create_and_write_file.create_file_contents(self.pallet_file_full, "test contents")

        with mock.patch("generic_run.run_cmd_simple", return_value=(True, None)) as dummy:
            v, r = palletapp_wrapper.ditch(self.pallet_file_full, None)
            self.assertFalse(v)
            self.assertEqual(r, "Invalid target route")
            dummy.assert_not_called()

    def testDitch4(self):

        create_and_write_file.create_file_contents(self.pallet_file_full, "test contents")

        with mock.patch("generic_run.run_cmd_simple", return_value=(True, None)) as dummy:
            v, r = palletapp_wrapper.ditch(self.pallet_file_full, self.test_file1_full)
            self.assertTrue(v)
            dummy.assert_called_with(["palletapp", "--ditch", self.pallet_file_full, self.test_file1_full])

    def testDitch5(self):

        create_and_write_file.create_file_contents(self.pallet_file_full, "test contents")

        with mock.patch("generic_run.run_cmd_simple", return_value=(False, "test error")) as dummy:
            v, r = palletapp_wrapper.ditch(self.pallet_file_full, self.test_file1_full)
            self.assertFalse(v)
            self.assertEqual(r, "Failed running palletapp ditch command: [test error]")
            dummy.assert_called_with(["palletapp", "--ditch", self.pallet_file_full, self.test_file1_full])

    def testExport1(self):

        create_and_write_file.create_file_contents(self.pallet_file_full, "test contents")

        with mock.patch("generic_run.run_cmd_simple", return_value=(True, None)) as dummy:
            v, r = palletapp_wrapper.export(None, "test_route", self.test_folder_full)
            self.assertFalse(v)
            self.assertEqual(r, "Invalid source archive")
            dummy.assert_not_called()

    def testExport2(self):

        with mock.patch("generic_run.run_cmd_simple", return_value=(True, None)) as dummy:
            v, r = palletapp_wrapper.export(self.pallet_file_full, "test_route", self.test_folder_full)
            self.assertFalse(v)
            self.assertEqual(r, "[%s] does not exist." % self.pallet_file_full)
            dummy.assert_not_called()

    def testExport3(self):

        create_and_write_file.create_file_contents(self.pallet_file_full, "test contents")

        with mock.patch("generic_run.run_cmd_simple", return_value=(True, None)) as dummy:
            v, r = palletapp_wrapper.export(self.pallet_file_full, None, self.test_folder_full)
            self.assertFalse(v)
            self.assertEqual(r, "Invalid target route")
            dummy.assert_not_called()

    def testExport4(self):

        create_and_write_file.create_file_contents(self.pallet_file_full, "test contents")

        with mock.patch("generic_run.run_cmd_simple", return_value=(True, None)) as dummy:
            v, r = palletapp_wrapper.export(self.pallet_file_full, "test_route", None)
            self.assertFalse(v)
            self.assertEqual(r, "Invalid target path")
            dummy.assert_not_called()

    def testExport5(self):

        create_and_write_file.create_file_contents(self.pallet_file_full, "test contents")
        shutil.rmtree(self.test_folder_full)

        with mock.patch("generic_run.run_cmd_simple", return_value=(True, None)) as dummy:
            v, r = palletapp_wrapper.export(self.pallet_file_full, "test_route", self.test_folder_full)
            self.assertFalse(v)
            self.assertEqual(r, "[%s] does not exist." % self.test_folder_full)
            dummy.assert_not_called()

    def testExport6(self):

        create_and_write_file.create_file_contents(self.pallet_file_full, "test contents")
        shutil.rmtree(self.test_folder_full)
        create_and_write_file.create_file_contents(self.test_folder_full, "folder impostor")

        with mock.patch("generic_run.run_cmd_simple", return_value=(True, None)) as dummy:
            v, r = palletapp_wrapper.export(self.pallet_file_full, "test_route", self.test_folder_full)
            self.assertFalse(v)
            self.assertEqual(r, "[%s] is not a folder." % self.test_folder_full)
            dummy.assert_not_called()

    def testExport7(self):

        create_and_write_file.create_file_contents(self.pallet_file_full, "test contents")

        with mock.patch("generic_run.run_cmd_simple", return_value=(True, None)) as dummy:
            v, r = palletapp_wrapper.export(self.pallet_file_full, "test_route", self.test_folder_full)
            self.assertTrue(v)
            dummy.assert_called_with(["palletapp", "--export", self.pallet_file_full, "test_route", self.test_folder_full])

    def testExport8(self):

        create_and_write_file.create_file_contents(self.pallet_file_full, "test contents")

        with mock.patch("generic_run.run_cmd_simple", return_value=(False, "test error")) as dummy:
            v, r = palletapp_wrapper.export(self.pallet_file_full, "test_route", self.test_folder_full)
            self.assertFalse(v)
            self.assertEqual(r, "Failed running palletapp export command: [test error]")
            dummy.assert_called_with(["palletapp", "--export", self.pallet_file_full, "test_route", self.test_folder_full])

    def testList1(self):

        create_and_write_file.create_file_contents(self.pallet_file_full, "test contents")

        with mock.patch("generic_run.run_cmd_simple", return_value=(True, None)) as dummy:
            v, r = palletapp_wrapper.list(None)
            self.assertFalse(v)
            self.assertEqual(r, "Invalid source archive path")
            dummy.assert_not_called()

    def testList2(self):

        with mock.patch("generic_run.run_cmd_simple", return_value=(True, None)) as dummy:
            v, r = palletapp_wrapper.list(self.pallet_file_full)
            self.assertFalse(v)
            self.assertEqual(r, "[%s] does not exist." % self.pallet_file_full)
            dummy.assert_not_called()

    def testList3(self):

        create_and_write_file.create_file_contents(self.pallet_file_full, "test contents")

        with mock.patch("generic_run.run_cmd_simple", return_value=(True, "test listed contents")) as dummy:
            v, r = palletapp_wrapper.list(self.pallet_file_full)
            self.assertTrue(v)
            self.assertEqual(r, "test listed contents")
            dummy.assert_called_with(["palletapp", "--list", self.pallet_file_full])

    def testList4(self):

        create_and_write_file.create_file_contents(self.pallet_file_full, "test contents")

        with mock.patch("generic_run.run_cmd_simple", return_value=(False, "test error")) as dummy:
            v, r = palletapp_wrapper.list(self.pallet_file_full)
            self.assertFalse(v)
            self.assertEqual(r, "Failed running palletapp list command: [test error]")
            dummy.assert_called_with(["palletapp", "--list", self.pallet_file_full])

if __name__ == "__main__":
    unittest.main()
