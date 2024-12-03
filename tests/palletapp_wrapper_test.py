#!/usr/bin/env python3

import sys
import os
import shutil
import unittest

import mvtools_test_fixture
import create_and_write_file
import path_utils
import get_platform
import convcygpath

import palletapp_wrapper

def conv_cyg_if_needed(in_path):
    plat_local = get_platform.getplat()
    if plat_local == get_platform.PLAT_CYGWIN:
        return convcygpath.convert_cygwin_path_to_win_path(in_path)
    return in_path

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

        # the target pallet file
        self.pallet_file_full = path_utils.concat_path(self.test_dir, "test.plt")

        # the source base folder
        self.source_base_folder = "source_base_folder"
        self.source_base_folder_full = path_utils.concat_path(self.test_dir, self.source_base_folder)
        os.mkdir(self.source_base_folder_full)

        # the extracted-to folder
        self.extracted_folder = "extracted"
        self.extracted_folder_full = path_utils.concat_path(self.test_dir, self.extracted_folder)
        os.mkdir(self.extracted_folder_full)

        plat_local = get_platform.getplat()

        # create test content

        self.file1 = "file1.txt"
        self.file2 = "file2.txt"
        self.folder1 = "folder1"
        self.folder2 = "folder2"
        self.file_nonexistent = "nonexistent_file"
        self.file_esp1 = "   file_esp1.txt"
        self.file_esp2 = "file_esp2.txt   "
        self.file_with_space = "fi le.txt"
        self.folder_with_space = "fol der"
        self.filler = "filler.txt"
        self.hidden_file = ".file.txt"
        self.hidden_folder = ".folder"

        self.folder1_file1 = path_utils.concat_path(self.folder1, self.file1)
        self.folder1_file2 = path_utils.concat_path(self.folder1, self.file2)
        self.folder2_file1 = path_utils.concat_path(self.folder2, self.file1)
        self.folder2_file2 = path_utils.concat_path(self.folder2, self.file2)
        self.folder2_sub1 = path_utils.concat_path(self.folder2, "sub1")
        self.folder2_sub1_file1 = path_utils.concat_path(self.folder2_sub1, self.file1)
        self.folder_with_space_filler = path_utils.concat_path(self.folder_with_space, self.filler)

        self.file1_full = path_utils.concat_path(self.source_base_folder_full, self.file1)
        self.file2_full = path_utils.concat_path(self.source_base_folder_full, self.file2)
        self.folder1_full = path_utils.concat_path(self.source_base_folder_full, self.folder1)
        self.folder2_full = path_utils.concat_path(self.source_base_folder_full, self.folder2)
        self.folder2_sub1_full = path_utils.concat_path(self.source_base_folder_full, self.folder2_sub1)
        self.folder1_file1_full = path_utils.concat_path(self.source_base_folder_full, self.folder1_file1)
        self.folder1_file2_full = path_utils.concat_path(self.source_base_folder_full, self.folder1_file2)
        self.folder2_file1_full = path_utils.concat_path(self.source_base_folder_full, self.folder2_file1)
        self.folder2_file2_full = path_utils.concat_path(self.source_base_folder_full, self.folder2_file2)
        self.folder2_sub1_file1_full = path_utils.concat_path(self.source_base_folder_full, self.folder2_sub1_file1)
        self.file_nonexistent_full = path_utils.concat_path(self.source_base_folder_full, self.file_nonexistent)
        self.file_esp1_full = path_utils.concat_path(self.source_base_folder_full, self.file_esp1)
        self.file_esp2_full = path_utils.concat_path(self.source_base_folder_full, self.file_esp2)
        self.file_with_space_full = path_utils.concat_path(self.source_base_folder_full, self.file_with_space)
        self.folder_with_space_full = path_utils.concat_path(self.source_base_folder_full, self.folder_with_space)
        self.folder_with_space_filler_full = path_utils.concat_path(self.source_base_folder_full, self.folder_with_space_filler)
        self.hidden_file_full = path_utils.concat_path(self.source_base_folder_full, self.hidden_file)
        self.hidden_folder_full = path_utils.concat_path(self.source_base_folder_full, self.hidden_folder)

        self.file1_extracted = path_utils.concat_path(self.test_dir, self.extracted_folder, self.source_base_folder, self.file1)
        self.file2_extracted = path_utils.concat_path(self.test_dir, self.extracted_folder, self.source_base_folder, self.file2)
        self.folder1_extracted = path_utils.concat_path(self.test_dir, self.extracted_folder, self.source_base_folder, self.folder1)
        self.folder2_extracted = path_utils.concat_path(self.test_dir, self.extracted_folder, self.source_base_folder, self.folder2)
        self.folder2_sub1_extracted = path_utils.concat_path(self.test_dir, self.extracted_folder, self.source_base_folder, self.folder2_sub1)
        self.folder1_file1_extracted = path_utils.concat_path(self.test_dir, self.extracted_folder, self.source_base_folder, self.folder1_file1)
        self.folder1_file2_extracted = path_utils.concat_path(self.test_dir, self.extracted_folder, self.source_base_folder, self.folder1_file2)
        self.folder2_file1_extracted = path_utils.concat_path(self.test_dir, self.extracted_folder, self.source_base_folder, self.folder2_file1)
        self.folder2_file2_extracted = path_utils.concat_path(self.test_dir, self.extracted_folder, self.source_base_folder, self.folder2_file2)
        self.folder2_sub1_file1_extracted = path_utils.concat_path(self.test_dir, self.extracted_folder, self.source_base_folder, self.folder2_sub1_file1)
        self.file_nonexistent_extracted = path_utils.concat_path(self.test_dir, self.extracted_folder, self.source_base_folder, self.file_nonexistent)
        self.file_esp1_extracted = path_utils.concat_path(self.test_dir, self.extracted_folder, self.source_base_folder, self.file_esp1)
        self.file_esp2_extracted = path_utils.concat_path(self.test_dir, self.extracted_folder, self.source_base_folder, self.file_esp2)
        self.file_with_space_extracted = path_utils.concat_path(self.test_dir, self.extracted_folder, self.source_base_folder, self.file_with_space)
        self.folder_with_space_extracted = path_utils.concat_path(self.test_dir, self.extracted_folder, self.source_base_folder, self.folder_with_space)
        self.folder_with_space_filler_extracted = path_utils.concat_path(self.test_dir, self.extracted_folder, self.source_base_folder, self.folder_with_space_filler)
        self.hidden_file_extracted = path_utils.concat_path(self.test_dir, self.extracted_folder, self.source_base_folder, self.hidden_file)
        self.hidden_folder_extracted = path_utils.concat_path(self.test_dir, self.extracted_folder, self.source_base_folder, self.hidden_folder)

        os.mkdir(self.folder1_full)
        os.mkdir(self.folder2_full)
        os.mkdir(self.folder2_sub1_full)
        os.mkdir(self.folder_with_space_full)
        os.mkdir(self.hidden_folder_full)

        create_and_write_file.create_file_contents(self.file1_full, "abc")
        create_and_write_file.create_file_contents(self.file2_full, "abc")
        create_and_write_file.create_file_contents(self.folder1_file1_full, "abc")
        create_and_write_file.create_file_contents(self.folder1_file2_full, "abc")
        create_and_write_file.create_file_contents(self.folder2_file1_full, "abc")
        create_and_write_file.create_file_contents(self.folder2_file2_full, "abc")
        create_and_write_file.create_file_contents(self.folder2_sub1_file1_full, "abc")
        create_and_write_file.create_file_contents(self.file_esp1_full, "abc")
        if plat_local != get_platform.PLAT_CYGWIN:
            create_and_write_file.create_file_contents(self.file_esp2_full, "abc")
        create_and_write_file.create_file_contents(self.file_with_space_full, "abc")
        create_and_write_file.create_file_contents(self.folder_with_space_filler_full, "abc")
        create_and_write_file.create_file_contents(self.hidden_file_full, "abc")

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testCreatePrechecks1(self):
        v, r = palletapp_wrapper.create(None, self.pallet_file_full)
        self.assertFalse(v)

    def testCreatePrechecks2(self):
        v, r = palletapp_wrapper.create(self.file1_full, None)
        self.assertFalse(v)

    def testCreatePrechecks3(self):
        create_and_write_file.create_file_contents(self.pallet_file_full, "abc")
        v, r = palletapp_wrapper.create(self.file1_full, self.pallet_file_full)
        self.assertFalse(v)

    def testCreatePrechecks4(self):
        v, r = palletapp_wrapper.create(self.file_nonexistent, self.pallet_file_full)
        self.assertFalse(v)

    def testExtractPrechecks1(self):
        create_and_write_file.create_file_contents_hex(self.pallet_file_full, "504c5400018350d7d37adf19ad8cb89b63462e63216c6cf43130b6c15aee68398357c1191bccb38628f0fa03b6a227e7aebe7023d61c65d523c31c66991c2a872009a12b6800000000000000020100000012736f757263655f626173655f666f6c646572020000001c736f757263655f626173655f666f6c6465722f66696c65312e7478740000000000000003000000000000000b78da4b4c4a0600024d0127")
        v, r = palletapp_wrapper.extract(None, self.extracted_folder_full)
        self.assertFalse(v)

    def testExtractPrechecks2(self):
        create_and_write_file.create_file_contents_hex(self.pallet_file_full, "504c5400018350d7d37adf19ad8cb89b63462e63216c6cf43130b6c15aee68398357c1191bccb38628f0fa03b6a227e7aebe7023d61c65d523c31c66991c2a872009a12b6800000000000000020100000012736f757263655f626173655f666f6c646572020000001c736f757263655f626173655f666f6c6465722f66696c65312e7478740000000000000003000000000000000b78da4b4c4a0600024d0127")
        v, r = palletapp_wrapper.extract(self.pallet_file_full, None)
        self.assertFalse(v)

    def testExtractPrechecks3(self):
        v, r = palletapp_wrapper.extract(self.pallet_file_full, self.extracted_folder_full)
        self.assertFalse(v)

    def testExtractPrechecks4(self):
        create_and_write_file.create_file_contents_hex(self.pallet_file_full, "504c5400018350d7d37adf19ad8cb89b63462e63216c6cf43130b6c15aee68398357c1191bccb38628f0fa03b6a227e7aebe7023d61c65d523c31c66991c2a872009a12b6800000000000000020100000012736f757263655f626173655f666f6c646572020000001c736f757263655f626173655f666f6c6465722f66696c65312e7478740000000000000003000000000000000b78da4b4c4a0600024d0127")
        os.rmdir(self.extracted_folder_full)
        v, r = palletapp_wrapper.extract(self.pallet_file_full, self.extracted_folder_full)
        self.assertFalse(v)

    def testExtractPrechecks5(self):
        create_and_write_file.create_file_contents_hex(self.pallet_file_full, "504c5400018350d7d37adf19ad8cb89b63462e63216c6cf43130b6c15aee68398357c1191bccb38628f0fa03b6a227e7aebe7023d61c65d523c31c66991c2a872009a12b6800000000000000020100000012736f757263655f626173655f666f6c646572020000001c736f757263655f626173655f666f6c6465722f66696c65312e7478740000000000000003000000000000000b78da4b4c4a0600024d0127")
        v, r = palletapp_wrapper.extract(self.file_nonexistent, self.extracted_folder_full)
        self.assertFalse(v)

    def testCreateAndExtract(self):

        plat_local = get_platform.getplat()

        v, r = palletapp_wrapper.create(conv_cyg_if_needed(self.source_base_folder_full), conv_cyg_if_needed(self.pallet_file_full))
        self.assertTrue(v)
        self.assertTrue(os.path.exists(self.pallet_file_full))

        v, r = palletapp_wrapper.extract(conv_cyg_if_needed(self.pallet_file_full), conv_cyg_if_needed(self.extracted_folder_full))
        self.assertTrue(v)

        self.assertTrue(os.path.exists(self.file1_extracted))
        self.assertTrue(os.path.exists(self.file2_extracted))
        self.assertTrue(os.path.exists(self.folder1_extracted))
        self.assertTrue(os.path.exists(self.folder2_extracted))
        self.assertTrue(os.path.exists(self.folder2_sub1_extracted))
        self.assertTrue(os.path.exists(self.folder1_file1_extracted))
        self.assertTrue(os.path.exists(self.folder1_file2_extracted))
        self.assertTrue(os.path.exists(self.folder2_file1_extracted))
        self.assertTrue(os.path.exists(self.folder2_file2_extracted))
        self.assertTrue(os.path.exists(self.folder2_sub1_file1_extracted))
        self.assertFalse(os.path.exists(self.file_nonexistent_extracted))
        self.assertTrue(os.path.exists(self.file_esp1_extracted))
        if plat_local != get_platform.PLAT_CYGWIN:
            self.assertTrue(os.path.exists(self.file_esp2_extracted))
        self.assertTrue(os.path.exists(self.file_with_space_extracted))
        self.assertTrue(os.path.exists(self.folder_with_space_extracted))
        self.assertTrue(os.path.exists(self.folder_with_space_filler_extracted))
        self.assertTrue(os.path.exists(self.hidden_file_extracted))
        self.assertTrue(os.path.exists(self.hidden_folder_extracted))

if __name__ == '__main__':
    unittest.main()
