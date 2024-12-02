#!/usr/bin/env python3

import sys
import os
import shutil
import unittest

import mvtools_test_fixture
import create_and_write_file
import path_utils

import seven_z_wrapper

class SevenZWrapperTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("seven_z_wrapper_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # the target 7z file
        self.seven_z_file = path_utils.concat_path(self.test_dir, "test.7z")

        # create test content

        # special cases
        self.file_nonexistent = path_utils.concat_path(self.test_dir, "no_file")

        self.file_with_space = "fi le.txt"
        self.file_with_space_full = path_utils.concat_path(self.test_dir, self.file_with_space)
        create_and_write_file.create_file_contents(self.file_with_space_full, "abc")
        self.file_with_sep = "file_with_sep.txt"
        self.file_with_sep_full = path_utils.concat_path(self.test_dir, self.file_with_sep)
        create_and_write_file.create_file_contents(self.file_with_sep_full, "abc")
        self.file_with_sep_full += "/"

        self.folder_with_space = "fol der"
        self.folder_with_space_full = path_utils.concat_path(self.test_dir, self.folder_with_space)
        os.mkdir(self.folder_with_space_full)
        self.folder_with_space_filler = path_utils.concat_path(self.folder_with_space, "filler.txt")
        self.folder_with_space_filler_full = path_utils.concat_path(self.test_dir, self.folder_with_space_filler)
        create_and_write_file.create_file_contents(self.folder_with_space_filler_full, "abc")

        self.folder_with_sep = "folder_with_sep"
        self.folder_with_sep_full = path_utils.concat_path(self.test_dir, self.folder_with_sep)
        os.mkdir(self.folder_with_sep_full)
        self.folder_with_sep_filler = path_utils.concat_path(self.folder_with_sep, "filler.txt")
        self.folder_with_sep_filler_full = path_utils.concat_path(self.test_dir, self.folder_with_sep_filler)
        create_and_write_file.create_file_contents(self.folder_with_sep_filler_full, "abc")
        self.folder_with_sep_full += "/"

        # base, files
        self.file1 = "file1.txt"
        self.file1_full = path_utils.concat_path(self.test_dir, self.file1)
        create_and_write_file.create_file_contents(self.file1_full, "abc")

        self.file_esp1 = "   file_esp1.txt"
        self.file_esp1_full = path_utils.concat_path(self.test_dir, self.file_esp1)
        create_and_write_file.create_file_contents(self.file_esp1_full, "abc")

        self.file_esp2 = "file_esp2.txt   "
        self.file_esp2_full = path_utils.concat_path(self.test_dir, self.file_esp2)
        create_and_write_file.create_file_contents(self.file_esp2_full, "abc")

        self.file2 = "file2.txt"
        self.file2_full = path_utils.concat_path(self.test_dir, self.file2)
        create_and_write_file.create_file_contents(self.file2_full, "abc")

        # base, folders
        self.folder1 = "folder1"
        self.folder1_full = path_utils.concat_path(self.test_dir, self.folder1)
        os.mkdir(self.folder1_full)

        self.folder2 = "folder2"
        self.folder2_full = path_utils.concat_path(self.test_dir, self.folder2)
        os.mkdir(self.folder2_full)

        self.folder2_sub1 = path_utils.concat_path(self.folder2, "sub1")
        self.folder2_sub1_full = path_utils.concat_path(self.test_dir, self.folder2_sub1)
        os.mkdir(self.folder2_sub1_full)

        self.folder2_sub1_file1 = path_utils.concat_path(self.folder2_sub1, "file1.txt")
        self.folder2_sub1_file1_full = path_utils.concat_path(self.test_dir, self.folder2_sub1_file1)
        create_and_write_file.create_file_contents(self.folder2_sub1_file1_full, "abc")

        # files in folders

        # folder1
        self.folder1_file1 = path_utils.concat_path(self.folder1, "file1.txt")
        self.folder1_file1_full = path_utils.concat_path(self.test_dir, self.folder1_file1)
        create_and_write_file.create_file_contents(self.folder1_file1_full, "abc")

        self.folder1_file2 = path_utils.concat_path(self.folder1, "file2.txt")
        self.folder1_file2_full = path_utils.concat_path(self.test_dir, self.folder1_file2)
        create_and_write_file.create_file_contents(self.folder1_file2_full, "abc")

        # folder2
        self.folder2_file1 = path_utils.concat_path(self.folder2, "file1.txt")
        self.folder2_file1_full = path_utils.concat_path(self.test_dir, self.folder2_file1)
        create_and_write_file.create_file_contents(self.folder2_file1_full, "abc")

        self.folder2_file2 = path_utils.concat_path(self.folder2, "file2.txt")
        self.folder2_file2_full = path_utils.concat_path(self.test_dir, self.folder2_file2)
        create_and_write_file.create_file_contents(self.folder2_file2_full, "abc")

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testPrechecks1(self):
        v, r = seven_z_wrapper.make_pack(self.file1_full, [self.file2_full])
        self.assertFalse(v)

    def testPrechecks2(self):
        v, r = seven_z_wrapper.make_pack(self.file_nonexistent, [])
        self.assertFalse(v)

    def testMakeAndExtract1(self):
        v, r = seven_z_wrapper.make_pack(self.seven_z_file, [self.folder1_full, self.folder2_full, self.file1_full, self.file2_full])
        self.assertTrue(v)
        self.assertTrue(os.path.exists(self.seven_z_file))

        self.extracted_folder = path_utils.concat_path(self.test_dir, "extracted")
        os.mkdir(self.extracted_folder)

        v, r = seven_z_wrapper.extract(self.seven_z_file, self.extracted_folder)
        self.assertTrue(v)

        self.ext_file1 = path_utils.concat_path(self.extracted_folder, self.file1)
        self.ext_file2 = path_utils.concat_path(self.extracted_folder, self.file2)
        self.ext_folder1 = path_utils.concat_path(self.extracted_folder, self.folder1)
        self.ext_folder2 = path_utils.concat_path(self.extracted_folder, self.folder2)
        self.ext_folder1_file1 = path_utils.concat_path(self.extracted_folder, self.folder1_file1)
        self.ext_folder1_file2 = path_utils.concat_path(self.extracted_folder, self.folder1_file2)
        self.ext_folder2_file1 = path_utils.concat_path(self.extracted_folder, self.folder2_file1)
        self.ext_folder2_file2 = path_utils.concat_path(self.extracted_folder, self.folder2_file2)
        self.ext_folder2_sub1 = path_utils.concat_path(self.extracted_folder, self.folder2_sub1)
        self.ext_folder2_sub1_file1 = path_utils.concat_path(self.extracted_folder, self.folder2_sub1_file1)

        self.assertTrue(os.path.exists( self.ext_file1 ))
        self.assertTrue(os.path.exists( self.ext_file2 ))
        self.assertTrue(os.path.exists( self.ext_folder1 ))
        self.assertTrue(os.path.exists( self.ext_folder2 ))
        self.assertTrue(os.path.exists( self.ext_folder1_file1 ))
        self.assertTrue(os.path.exists( self.ext_folder1_file2 ))
        self.assertTrue(os.path.exists( self.ext_folder2_file1 ))
        self.assertTrue(os.path.exists( self.ext_folder2_file2 ))
        self.assertTrue(os.path.exists( self.ext_folder2_sub1 ))
        self.assertTrue(os.path.exists( self.ext_folder2_sub1_file1 ))

    def testMakeAndExtract2(self):
        v, r = seven_z_wrapper.make_pack(self.seven_z_file, [self.folder1_full, self.folder2_full, self.file1_full, self.file2_full])
        self.assertTrue(v)
        self.assertTrue(os.path.exists(self.seven_z_file))

        self.extracted_folder = path_utils.concat_path(self.test_dir, "extracted")
        os.mkdir(self.extracted_folder)

        v, r = seven_z_wrapper.extract(self.seven_z_file, self.extracted_folder)
        self.assertTrue(v)

        self.ext_file1 = path_utils.concat_path(self.extracted_folder, self.file1)
        self.ext_file2 = path_utils.concat_path(self.extracted_folder, self.file2)
        self.ext_folder1 = path_utils.concat_path(self.extracted_folder, self.folder1)
        self.ext_folder2 = path_utils.concat_path(self.extracted_folder, self.folder2)
        self.ext_folder1_file1 = path_utils.concat_path(self.extracted_folder, self.folder1_file1)
        self.ext_folder1_file2 = path_utils.concat_path(self.extracted_folder, self.folder1_file2)
        self.ext_folder2_file1 = path_utils.concat_path(self.extracted_folder, self.folder2_file1)
        self.ext_folder2_file2 = path_utils.concat_path(self.extracted_folder, self.folder2_file2)
        self.ext_folder2_sub1 = path_utils.concat_path(self.extracted_folder, self.folder2_sub1)
        self.ext_folder2_sub1_file1 = path_utils.concat_path(self.extracted_folder, self.folder2_sub1_file1)

        self.assertTrue(os.path.exists( self.ext_file1 ))
        self.assertTrue(os.path.exists( self.ext_file2 ))
        self.assertTrue(os.path.exists( self.ext_folder1 ))
        self.assertTrue(os.path.exists( self.ext_folder2 ))
        self.assertTrue(os.path.exists( self.ext_folder1_file1 ))
        self.assertTrue(os.path.exists( self.ext_folder1_file2 ))
        self.assertTrue(os.path.exists( self.ext_folder2_file1 ))
        self.assertTrue(os.path.exists( self.ext_folder2_file2 ))
        #self.assertFalse(os.path.exists( self.ext_folder2_sub1 ))
        #self.assertFalse(os.path.exists( self.ext_folder2_sub1_file1 ))
        self.assertTrue(os.path.exists( self.ext_folder2_sub1 ))
        self.assertTrue(os.path.exists( self.ext_folder2_sub1_file1 ))

    def testSpecialCases1(self):
        v, r = seven_z_wrapper.make_pack(self.seven_z_file, [self.file_with_sep_full, self.folder_with_sep_full])
        self.assertTrue(v)
        self.assertTrue(os.path.exists(self.seven_z_file))

        self.extracted_folder = path_utils.concat_path(self.test_dir, "extracted")
        os.mkdir(self.extracted_folder)

        v, r = seven_z_wrapper.extract(self.seven_z_file, self.extracted_folder)
        self.assertTrue(v)

        # see below: concat_path removes the trailing "/" (as of l21)
        self.ext_file_with_sep = "%s/" % (path_utils.concat_path(self.extracted_folder, self.file_with_sep))
        self.ext_folder_with_sep = "%s/" % (path_utils.concat_path(self.extracted_folder, self.folder_with_sep))
        self.ext_folder_with_sep_filler = path_utils.concat_path(self.extracted_folder, self.folder_with_sep_filler)

        self.assertTrue(os.path.exists( self.ext_file_with_sep[:len(self.ext_file_with_sep)-1] ))
        self.assertTrue(os.path.exists( self.ext_folder_with_sep ))
        self.assertTrue(os.path.exists( self.ext_folder_with_sep_filler ))

    def testSpecialCases2(self):
        v, r = seven_z_wrapper.make_pack(self.seven_z_file, [self.file_with_space_full, self.folder_with_space_full])
        self.assertTrue(v)
        self.assertTrue(os.path.exists(self.seven_z_file))

        self.extracted_folder = path_utils.concat_path(self.test_dir, "extracted")
        os.mkdir(self.extracted_folder)

        v, r = seven_z_wrapper.extract(self.seven_z_file, self.extracted_folder)
        self.assertTrue(v)

        self.ext_file_with_space = path_utils.concat_path(self.extracted_folder, self.file_with_space)
        self.ext_folder_with_space = path_utils.concat_path(self.extracted_folder, self.folder_with_space)
        self.ext_folder_with_space_filler = path_utils.concat_path(self.extracted_folder, self.folder_with_space_filler)

        self.assertTrue( os.path.exists( self.ext_file_with_space ) )
        self.assertTrue( os.path.exists( self.ext_folder_with_space ) )
        self.assertTrue( os.path.exists( self.ext_folder_with_space_filler ) )

    def testSpecialCases3(self):

        seven_z_file_spaced = path_utils.concat_path(self.test_dir, "te st.7z")

        v, r = seven_z_wrapper.make_pack(seven_z_file_spaced, [self.file1_full, self.file_esp1_full, self.file_esp2_full])
        self.assertTrue(v)
        self.assertTrue(os.path.exists(seven_z_file_spaced))

        self.extracted_folder = path_utils.concat_path(self.test_dir, "extracted")
        os.mkdir(self.extracted_folder)

        v, r = seven_z_wrapper.extract(seven_z_file_spaced, self.extracted_folder)
        self.assertTrue(v)

        self.ext_file1 = path_utils.concat_path(self.extracted_folder, self.file1)
        self.ext_file_esp1 = path_utils.concat_path(self.extracted_folder, self.file_esp1)
        self.ext_file_esp2 = path_utils.concat_path(self.extracted_folder, self.file_esp2)

        self.assertTrue( os.path.exists( self.ext_file1 ) )
        self.assertTrue( os.path.exists( self.ext_file_esp1 ) )
        self.assertTrue( os.path.exists( self.ext_file_esp2 ) )

    def testSpecialCases4(self):

        seven_z_file_spaced_2 = path_utils.concat_path(self.test_dir, "  test.7z")

        v, r = seven_z_wrapper.make_pack(seven_z_file_spaced_2, [self.file1_full])
        self.assertTrue(v)
        self.assertTrue(os.path.exists(seven_z_file_spaced_2))

        self.extracted_folder = path_utils.concat_path(self.test_dir, "extracted")
        os.mkdir(self.extracted_folder)

        v, r = seven_z_wrapper.extract(seven_z_file_spaced_2, self.extracted_folder)
        self.assertTrue(v)

        self.ext_file1 = path_utils.concat_path(self.extracted_folder, self.file1)
        self.assertTrue( os.path.exists( self.ext_file1 ) )

    def testSpecialCases5(self):

        seven_z_file_spaced_3 = path_utils.concat_path(self.test_dir, "test.7z   ")

        v, r = seven_z_wrapper.make_pack(seven_z_file_spaced_3, [self.file1_full])
        self.assertTrue(v)
        self.assertTrue(os.path.exists(seven_z_file_spaced_3))

        self.extracted_folder = path_utils.concat_path(self.test_dir, "extracted")
        os.mkdir(self.extracted_folder)

        v, r = seven_z_wrapper.extract(seven_z_file_spaced_3, self.extracted_folder)
        self.assertTrue(v)

        self.ext_file1 = path_utils.concat_path(self.extracted_folder, self.file1)
        self.assertTrue( os.path.exists( self.ext_file1 ) )

    def testSpecialCases6(self):

        blank_sub = path_utils.concat_path(self.test_dir, " ")
        self.assertFalse(os.path.exists(blank_sub))
        os.mkdir(blank_sub)
        self.assertTrue(os.path.exists(blank_sub))

        blank_sub_blank_fn = path_utils.concat_path(blank_sub, " ")
        self.assertFalse(os.path.exists(blank_sub_blank_fn))
        create_and_write_file.create_file_contents(blank_sub_blank_fn, "abc")
        self.assertTrue(os.path.exists(blank_sub_blank_fn))

        v, r = seven_z_wrapper.make_pack(self.seven_z_file, [blank_sub_blank_fn])
        self.assertTrue(v)
        self.assertTrue(os.path.exists(self.seven_z_file))

        self.extracted_folder = path_utils.concat_path(self.test_dir, "extracted")
        os.mkdir(self.extracted_folder)

        v, r = seven_z_wrapper.extract(self.seven_z_file, self.extracted_folder)
        self.assertTrue(v)

        self.ext_file1 = path_utils.concat_path(self.extracted_folder, blank_sub_blank_fn)
        # 7z version 16.02, of L24, does not seem to like "blank" subfolder (ie. named a single space).
        self.assertFalse( os.path.exists( self.ext_file1 ) )
        self.ext_file1_adjusted = path_utils.concat_path(self.extracted_folder, " ")
        self.assertTrue( os.path.exists( self.ext_file1_adjusted ) )
        self.assertTrue( os.path.isfile( self.ext_file1_adjusted ) )
        content = ""
        with open(self.ext_file1_adjusted, "r") as f:
            content = f.read()
        self.assertEqual(content, "abc")

    def testSpecialCases7(self):

        test_source_file = path_utils.concat_path(self.test_dir, "test_source_file.txt")
        self.assertFalse(os.path.exists(test_source_file))
        create_and_write_file.create_file_contents(test_source_file, "abc")
        self.assertTrue(os.path.exists(test_source_file))

        test_source_link = path_utils.concat_path(self.test_dir, "test_source_link.txt")
        self.assertFalse(os.path.exists(test_source_link))
        os.symlink(test_source_file, test_source_link)
        self.assertTrue(os.path.exists(test_source_link))

        os.unlink(test_source_file)
        self.assertFalse(os.path.exists(test_source_file))
        self.assertTrue(path_utils.is_path_broken_symlink(test_source_link))

        v, r = seven_z_wrapper.make_pack(self.seven_z_file, [test_source_link])
        self.assertFalse(v) # 7z version 16.02, of L24, does not support broken symlinks

if __name__ == '__main__':
    unittest.main()
