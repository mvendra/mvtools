#!/usr/bin/env python3

import sys
import os
import shutil
import unittest

import mvtools_test_fixture
import create_and_write_file
import path_utils

import tar_wrapper

class TarWrapperTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("tar_wrapper_test_base")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # the target tar file
        self.tar_file = os.path.join(self.test_dir, path_utils.filter_join_abs("test.tar") )

        # create test content

        # special cases
        self.file_nonexistant = os.path.join(self.test_dir, path_utils.filter_join_abs("no_file") )

        self.file_with_space = os.path.join(self.test_dir, path_utils.filter_join_abs("fi le.txt") )
        create_and_write_file.create_file_contents(self.file_with_space, "abc")
        self.file_with_sep = os.path.join(self.test_dir, path_utils.filter_join_abs("file_with_sep.txt") )
        create_and_write_file.create_file_contents(self.file_with_sep, "abc")
        self.file_with_sep += os.sep

        self.folder_with_space = os.path.join(self.test_dir, path_utils.filter_join_abs("fol der") )
        os.mkdir(self.folder_with_space)
        self.folder_with_space_filler = os.path.join(self.folder_with_space, path_utils.filter_join_abs("filler.txt") )
        create_and_write_file.create_file_contents(self.folder_with_space_filler, "abc")

        self.folder_with_sep = os.path.join(self.test_dir, path_utils.filter_join_abs("folder_with_sep") )
        os.mkdir(self.folder_with_sep)
        self.folder_with_sep_filler = os.path.join(self.folder_with_sep, path_utils.filter_join_abs("filler.txt") )
        create_and_write_file.create_file_contents(self.folder_with_sep_filler, "abc")
        self.folder_with_sep += os.sep

        # base, files
        self.file1 = os.path.join(self.test_dir, path_utils.filter_join_abs("file1.txt") )
        create_and_write_file.create_file_contents(self.file1, "abc")

        self.file_esp1 = os.path.join(self.test_dir, path_utils.filter_join_abs("   file_esp1.txt") )
        create_and_write_file.create_file_contents(self.file_esp1, "abc")

        self.file_esp2 = os.path.join(self.test_dir, path_utils.filter_join_abs("file_esp2.txt   ") )
        create_and_write_file.create_file_contents(self.file_esp2, "abc")

        self.file2 = os.path.join(self.test_dir, path_utils.filter_join_abs("file2.txt") )
        create_and_write_file.create_file_contents(self.file2, "abc")

        # base, folders
        self.folder1 = os.path.join(self.test_dir, path_utils.filter_join_abs("folder1") )
        os.mkdir(self.folder1)

        self.folder2 = os.path.join(self.test_dir, path_utils.filter_join_abs("folder2") )
        os.mkdir(self.folder2)

        self.folder2_sub1 = os.path.join(self.folder2, path_utils.filter_join_abs("sub1") )
        os.mkdir(self.folder2_sub1)

        self.folder2_sub1_file1 = os.path.join(self.folder2_sub1, path_utils.filter_join_abs("file1.txt") )
        create_and_write_file.create_file_contents(self.folder2_sub1_file1, "abc")

        # files in folders

        # folder1
        self.folder1_file1 = os.path.join(self.folder1, path_utils.filter_join_abs("file1.txt") )
        create_and_write_file.create_file_contents(self.folder1_file1, "abc")

        self.folder1_file2 = os.path.join(self.folder1, path_utils.filter_join_abs("file2.txt") )
        create_and_write_file.create_file_contents(self.folder1_file2, "abc")

        # folder2
        self.folder2_file1 = os.path.join(self.folder2, path_utils.filter_join_abs("file1.txt") )
        create_and_write_file.create_file_contents(self.folder2_file1, "abc")

        self.folder2_file2 = os.path.join(self.folder2, path_utils.filter_join_abs("file2.txt") )
        create_and_write_file.create_file_contents(self.folder2_file2, "abc")

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testPrechecks1(self):
        v, r = tar_wrapper.make_pack(self.file1, [self.file2])
        self.assertFalse(v)

    def testPrechecks2(self):
        v, r = tar_wrapper.make_pack(self.file_nonexistant, [])
        self.assertFalse(v)

    def testMakeAndExtract1(self):
        v, r = tar_wrapper.make_pack(self.tar_file, [self.folder1, self.folder2, self.file1, self.file2])
        self.assertTrue(v)
        self.assertTrue(os.path.exists(self.tar_file))

        self.extracted_folder = os.path.join(self.test_dir, path_utils.filter_join_abs("extracted") )
        os.mkdir(self.extracted_folder)

        v, r = tar_wrapper.extract(self.tar_file, self.extracted_folder)
        self.assertTrue(v)

        self.ext_file1 = os.path.join(self.extracted_folder, path_utils.filter_join_abs(self.file1) )
        self.ext_file2 = os.path.join(self.extracted_folder, path_utils.filter_join_abs(self.file2) )
        self.ext_folder1 = os.path.join(self.extracted_folder, path_utils.filter_join_abs(self.folder1) )
        self.ext_folder2 = os.path.join(self.extracted_folder, path_utils.filter_join_abs(self.folder2) )
        self.ext_folder1_file1 = os.path.join(self.extracted_folder, path_utils.filter_join_abs(self.folder1_file1) )
        self.ext_folder1_file2 = os.path.join(self.extracted_folder, path_utils.filter_join_abs(self.folder1_file2) )
        self.ext_folder2_file1 = os.path.join(self.extracted_folder, path_utils.filter_join_abs(self.folder2_file1) )
        self.ext_folder2_file2 = os.path.join(self.extracted_folder, path_utils.filter_join_abs(self.folder2_file2) )
        self.ext_folder2_sub1 = os.path.join(self.extracted_folder, path_utils.filter_join_abs(self.folder2_sub1) )
        self.ext_folder2_sub1_file1 = os.path.join(self.extracted_folder, path_utils.filter_join_abs(self.folder2_sub1_file1) )

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
        #v, r = tar_wrapper.make_pack(self.tar_file, [self.folder1, self.folder2, self.file1, self.file2], [self.folder2_sub1])
        v, r = tar_wrapper.make_pack(self.tar_file, [self.folder1, self.folder2, self.file1, self.file2])
        self.assertTrue(v)
        self.assertTrue(os.path.exists(self.tar_file))

        self.extracted_folder = os.path.join(self.test_dir, path_utils.filter_join_abs("extracted") )
        os.mkdir(self.extracted_folder)

        v, r = tar_wrapper.extract(self.tar_file, self.extracted_folder)
        self.assertTrue(v)

        self.ext_file1 = os.path.join(self.extracted_folder, path_utils.filter_join_abs(self.file1) )
        self.ext_file2 = os.path.join(self.extracted_folder, path_utils.filter_join_abs(self.file2) )
        self.ext_folder1 = os.path.join(self.extracted_folder, path_utils.filter_join_abs(self.folder1) )
        self.ext_folder2 = os.path.join(self.extracted_folder, path_utils.filter_join_abs(self.folder2) )
        self.ext_folder1_file1 = os.path.join(self.extracted_folder, path_utils.filter_join_abs(self.folder1_file1) )
        self.ext_folder1_file2 = os.path.join(self.extracted_folder, path_utils.filter_join_abs(self.folder1_file2) )
        self.ext_folder2_file1 = os.path.join(self.extracted_folder, path_utils.filter_join_abs(self.folder2_file1) )
        self.ext_folder2_file2 = os.path.join(self.extracted_folder, path_utils.filter_join_abs(self.folder2_file2) )
        self.ext_folder2_sub1 = os.path.join(self.extracted_folder, path_utils.filter_join_abs(self.folder2_sub1) )
        self.ext_folder2_sub1_file1 = os.path.join(self.extracted_folder, path_utils.filter_join_abs(self.folder2_sub1_file1) )

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
        v, r = tar_wrapper.make_pack(self.tar_file, [self.file_with_sep, self.folder_with_sep])
        self.assertTrue(v)
        self.assertTrue(os.path.exists(self.tar_file))

        self.extracted_folder = os.path.join(self.test_dir, path_utils.filter_join_abs("extracted") )
        os.mkdir(self.extracted_folder)

        v, r = tar_wrapper.extract(self.tar_file, self.extracted_folder)
        self.assertTrue(v)

        self.ext_file_with_sep = os.path.join(self.extracted_folder, path_utils.filter_join_abs(self.file_with_sep))
        self.ext_folder_with_sep = os.path.join(self.extracted_folder, path_utils.filter_join_abs(self.folder_with_sep))
        self.ext_folder_with_sep_filler = os.path.join(self.extracted_folder, path_utils.filter_join_abs(self.folder_with_sep_filler))

        self.assertTrue(os.path.exists( self.ext_file_with_sep[:len(self.ext_file_with_sep)-1] ))
        self.assertTrue(os.path.exists( self.ext_folder_with_sep ))
        self.assertTrue(os.path.exists( self.ext_folder_with_sep_filler ))

    def testSpecialCases2(self):
        v, r = tar_wrapper.make_pack(self.tar_file, [self.file_with_space, self.folder_with_space])
        self.assertTrue(v)
        self.assertTrue(os.path.exists(self.tar_file))

        self.extracted_folder = os.path.join(self.test_dir, path_utils.filter_join_abs("extracted") )
        os.mkdir(self.extracted_folder)

        v, r = tar_wrapper.extract(self.tar_file, self.extracted_folder)
        self.assertTrue(v)

        self.ext_file_with_space = os.path.join(self.extracted_folder, path_utils.filter_join_abs(self.file_with_space) )
        self.ext_folder_with_space = os.path.join(self.extracted_folder, path_utils.filter_join_abs(self.folder_with_space) )
        self.ext_folder_with_space_filler = os.path.join(self.extracted_folder, path_utils.filter_join_abs(self.folder_with_space_filler) )

        self.assertTrue( os.path.exists( self.ext_file_with_space ) )
        self.assertTrue( os.path.exists( self.ext_folder_with_space ) )
        self.assertTrue( os.path.exists( self.ext_folder_with_space_filler ) )

    def testSpecialCases3(self):

        tar_file_spaced = os.path.join(self.test_dir, path_utils.filter_join_abs("te st.tar") )

        v, r = tar_wrapper.make_pack(tar_file_spaced, [self.file1, self.file_esp1, self.file_esp2])
        self.assertTrue(v)
        self.assertTrue(os.path.exists(tar_file_spaced))

        self.extracted_folder = os.path.join(self.test_dir, path_utils.filter_join_abs("extracted") )
        os.mkdir(self.extracted_folder)

        v, r = tar_wrapper.extract(tar_file_spaced, self.extracted_folder)
        self.assertTrue(v)

        self.ext_file1 = os.path.join(self.extracted_folder, path_utils.filter_join_abs(self.file1) )
        self.ext_file_esp1 = os.path.join(self.extracted_folder, path_utils.filter_join_abs(self.file_esp1) )
        self.ext_file_esp2 = os.path.join(self.extracted_folder, path_utils.filter_join_abs(self.file_esp2) )

        self.assertTrue( os.path.exists( self.ext_file1 ) )
        self.assertTrue( os.path.exists( self.ext_file_esp1 ) )
        self.assertTrue( os.path.exists( self.ext_file_esp2 ) )

    def testSpecialCases4(self):

        tar_file_spaced_2 = os.path.join(self.test_dir, path_utils.filter_join_abs("  test.tar") )

        v, r = tar_wrapper.make_pack(tar_file_spaced_2, [self.file1])
        self.assertTrue(v)
        self.assertTrue(os.path.exists(tar_file_spaced_2))

        self.extracted_folder = os.path.join(self.test_dir, path_utils.filter_join_abs("extracted") )
        os.mkdir(self.extracted_folder)

        v, r = tar_wrapper.extract(tar_file_spaced_2, self.extracted_folder)
        self.assertTrue(v)

        self.ext_file1 = os.path.join(self.extracted_folder, path_utils.filter_join_abs(self.file1) )
        self.assertTrue( os.path.exists( self.ext_file1 ) )

    def testSpecialCases5(self):

        tar_file_spaced_3 = os.path.join(self.test_dir, path_utils.filter_join_abs("test.tar   ") )

        v, r = tar_wrapper.make_pack(tar_file_spaced_3, [self.file1])
        self.assertTrue(v)
        self.assertTrue(os.path.exists(tar_file_spaced_3))

        self.extracted_folder = os.path.join(self.test_dir, path_utils.filter_join_abs("extracted") )
        os.mkdir(self.extracted_folder)

        v, r = tar_wrapper.extract(tar_file_spaced_3, self.extracted_folder)
        self.assertTrue(v)

        self.ext_file1 = os.path.join(self.extracted_folder, path_utils.filter_join_abs(self.file1) )
        self.assertTrue( os.path.exists( self.ext_file1 ) )

if __name__ == '__main__':
    unittest.main()
