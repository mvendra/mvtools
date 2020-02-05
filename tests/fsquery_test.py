#!/usr/bin/env python3

import sys
import os
import shutil
import unittest

import fsquery

import mvtools_test_fixture
import create_and_write_file
import path_utils

class FsqueryTest(unittest.TestCase):

    def _create_test_file(self, filename, sub=None):
        base_folder = self.test_dir
        if sub is not None:
            base_folder = os.path.join(base_folder, path_utils.filter_join_abs(sub) )
        fn_full = os.path.join(base_folder, path_utils.filter_join_abs(filename) )
        create_and_write_file.create_file_contents(fn_full, "...")
        return fn_full

    def _create_test_dir(self, dirname, sub=None):
        base_folder = self.test_dir
        if sub is not None:
            base_folder = os.path.join(base_folder, path_utils.filter_join_abs(sub) )
        dn_full = os.path.join(base_folder, path_utils.filter_join_abs(dirname) )
        os.mkdir(dn_full)
        return dn_full

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("fsquery_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # create test folders and files

        # base folder
        self.file1 = self._create_test_file("file1.txt")
        self.file2 = self._create_test_file("file2.txt")
        self.file3 = self._create_test_file("file3.txt")

        self.file4 = self._create_test_file("file4.dat")
        self.file5 = self._create_test_file("file5.bin")

        self.file6 = self._create_test_file(".file6.txt")
        self.file7 = self._create_test_file(".file7.zip")

        # subfolder 1
        self.sub1 = self._create_test_dir("sub1")
        self.sub1_file1 = self._create_test_file("file1.txt", os.path.basename(self.sub1))
        self.sub1_file2 = self._create_test_file("file2.bin", os.path.basename(self.sub1))

        # subfolder 2
        self.sub2 = self._create_test_dir("sub2")
        self.sub2_file1 = self._create_test_file("file1.txt", os.path.basename(self.sub2))
        self.sub2_file2 = self._create_test_file(".file2.txt", os.path.basename(self.sub2))
        self.sub2_sub1 = self._create_test_dir(".sub1", os.path.basename(self.sub2))

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testFilename_qualifies_extension_list(self):
        exts = ["cpp", "py", "sql"]
        self.assertTrue(fsquery.filename_qualifies_extension_list ("/tmp/file.cpp", True, exts) )
        self.assertFalse(fsquery.filename_qualifies_extension_list ("/tmp/file.zip", True, exts) )
        self.assertTrue(fsquery.filename_qualifies_extension_list ("/tmp/file", True, None) )
        self.assertTrue(fsquery.filename_qualifies_extension_list ("/tmp/another", True, []) )

    def testMakecontentlist_1(self):
        ret = fsquery.makecontentlist(self.test_dir, False, True, False, False, False, True, "txt")
        self.assertEqual(len(ret), 3)
        self.assertTrue( self.file1 in ret )
        self.assertTrue( self.file2 in ret )
        self.assertTrue( self.file3 in ret )

    def testMakecontentlist_2(self):
        ret = fsquery.makecontentlist(self.test_dir, False, True, False, False, False, True, ["txt", "dat"])
        self.assertEqual(len(ret), 4)
        self.assertTrue( self.file1 in ret )
        self.assertTrue( self.file2 in ret )
        self.assertTrue( self.file3 in ret )
        self.assertTrue( self.file4 in ret )

    def testMakecontentlist_3(self):
        ret = fsquery.makecontentlist(self.test_dir, False, True, False, False, False, False, ["txt", "dat"])
        self.assertEqual(len(ret), 1)
        self.assertTrue( self.file5 in ret )

    def testMakecontentlist_4(self):
        ret = fsquery.makecontentlist(self.test_dir, False, True, False, False, False, True, "bin")
        self.assertEqual(len(ret), 1)
        self.assertEqual( self.file5, ret[0] )

    def testMakecontentlist_5(self):
        ret = fsquery.makecontentlist(self.test_dir, True, True, False, False, False, True, "bin")
        self.assertEqual(len(ret), 2)
        self.assertTrue( self.file5 in ret )
        self.assertTrue( self.sub1_file2 in ret )

    def testMakecontentlist_6(self):
        ret = fsquery.makecontentlist(self.test_dir, False, True, False, False, False, True, None)
        self.assertEqual(len(ret), 5)
        self.assertTrue( self.file1 in ret )
        self.assertTrue( self.file2 in ret )
        self.assertTrue( self.file3 in ret )
        self.assertTrue( self.file4 in ret )
        self.assertTrue( self.file5 in ret )

    def testMakecontentlist_7(self):
        ret = fsquery.makecontentlist(self.test_dir, True, True, False, False, False, True, None)
        self.assertEqual(len(ret), 8)
        self.assertTrue( self.file1 in ret )
        self.assertTrue( self.file2 in ret )
        self.assertTrue( self.file3 in ret )
        self.assertTrue( self.file4 in ret )
        self.assertTrue( self.file5 in ret )
        self.assertTrue( self.sub1_file1 in ret )
        self.assertTrue( self.sub1_file2 in ret )
        self.assertTrue( self.sub2_file1 in ret )

    def testMakecontentlist_8(self):
        ret = fsquery.makecontentlist(self.test_dir, True, True, False, True, False, True, None)
        self.assertEqual(len(ret), 11)
        self.assertTrue( self.file1 in ret )
        self.assertTrue( self.file2 in ret )
        self.assertTrue( self.file3 in ret )
        self.assertTrue( self.file4 in ret )
        self.assertTrue( self.file5 in ret )
        self.assertTrue( self.file6 in ret )
        self.assertTrue( self.file7 in ret )
        self.assertTrue( self.sub1_file1 in ret )
        self.assertTrue( self.sub1_file2 in ret )
        self.assertTrue( self.sub2_file1 in ret )
        self.assertTrue( self.sub2_file2 in ret )

    def testMakecontentlist_9(self):
        ret = fsquery.makecontentlist(self.test_dir, True, True, True, True, False, True, None)
        self.assertEqual(len(ret), 13)
        self.assertTrue( self.file1 in ret )
        self.assertTrue( self.file2 in ret )
        self.assertTrue( self.file3 in ret )
        self.assertTrue( self.file4 in ret )
        self.assertTrue( self.file5 in ret )
        self.assertTrue( self.file6 in ret )
        self.assertTrue( self.file7 in ret )
        self.assertTrue( self.sub1 in ret )
        self.assertTrue( self.sub1_file1 in ret )
        self.assertTrue( self.sub1_file2 in ret )
        self.assertTrue( self.sub2_file1 in ret )
        self.assertTrue( self.sub2_file2 in ret )

    def testMakecontentlist_10(self):
        ret = fsquery.makecontentlist(self.test_dir, True, True, True, True, True, True, None)
        self.assertEqual(len(ret), 14)
        self.assertTrue( self.file1 in ret )
        self.assertTrue( self.file2 in ret )
        self.assertTrue( self.file3 in ret )
        self.assertTrue( self.file4 in ret )
        self.assertTrue( self.file5 in ret )
        self.assertTrue( self.file6 in ret )
        self.assertTrue( self.file7 in ret )
        self.assertTrue( self.sub1 in ret )
        self.assertTrue( self.sub1_file1 in ret )
        self.assertTrue( self.sub1_file2 in ret )
        self.assertTrue( self.sub2 in ret )
        self.assertTrue( self.sub2_file1 in ret )
        self.assertTrue( self.sub2_file2 in ret )

    def testMakecontentlist_11(self):
        ret = fsquery.makecontentlist(self.test_dir, True, False, False, False, True, True, None)
        self.assertEqual(len(ret), 1)
        self.assertTrue( self.sub2_sub1 in ret )

    def testMakecontentlist_12(self):
        ret = fsquery.makecontentlist(self.test_dir, True, False, False, True, False, True, None)
        self.assertEqual(len(ret), 3)
        self.assertTrue( self.sub2_file2 in ret )
        self.assertTrue( self.file6 in ret )
        self.assertTrue( self.file7 in ret )

    def testMakecontentlist_13(self):
        ret = fsquery.makecontentlist(self.test_dir, True, False, True, False, False, True, None)
        self.assertEqual(len(ret), 2)
        self.assertTrue( self.sub1 in ret )
        self.assertTrue( self.sub2 in ret )

if __name__ == '__main__':
    unittest.main()
