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
            base_folder = path_utils.concat_path(base_folder, sub)
        fn_full = path_utils.concat_path(base_folder, filename)
        create_and_write_file.create_file_contents(fn_full, "...")
        return fn_full

    def _create_test_dir(self, dirname, sub=None):
        base_folder = self.test_dir
        if sub is not None:
            base_folder = path_utils.concat_path(base_folder, sub)
        dn_full = path_utils.concat_path(base_folder, dirname)
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
        self.sub1_file1 = self._create_test_file("file1.txt", path_utils.basename_filtered(self.sub1))
        self.sub1_file2 = self._create_test_file("file2.bin", path_utils.basename_filtered(self.sub1))

        # subfolder 2
        self.sub2 = self._create_test_dir("sub2")
        self.sub2_file1 = self._create_test_file("file1.txt", path_utils.basename_filtered(self.sub2))
        self.sub2_file2 = self._create_test_file(".file2.txt", path_utils.basename_filtered(self.sub2))
        self.sub2_sub1 = self._create_test_dir(".sub1", path_utils.basename_filtered(self.sub2))

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testAuxGraph1(self):
        g = fsquery.graph_aux(None)
        self.assertEqual(g.root, None)
        self.assertEqual(len(g.data), 1)
        self.assertTrue(None in g.data)

    def testAuxGraph2(self):
        g = fsquery.graph_aux("root")
        self.assertEqual(g.root, "root")
        self.assertTrue(g.add_node("A"))
        self.assertEqual(len(g.data), 2)
        self.assertTrue("A" in g.data)

    def testAuxGraph3(self):
        g = fsquery.graph_aux("/")
        self.assertEqual(g.root, "/")
        self.assertTrue(g.add_node("A"))
        self.assertTrue(g.add_node("B"))
        self.assertTrue(g.add_node("C"))
        self.assertEqual(len(g.data), 4)
        self.assertTrue("A" in g.data)
        self.assertTrue("B" in g.data)
        self.assertTrue("C" in g.data)

    def testAuxGraph4(self):
        g = fsquery.graph_aux("Z")
        self.assertEqual(g.root, "Z")
        self.assertTrue(g.add_node("A"))
        self.assertFalse(g.add_node("A"))
        self.assertEqual(len(g.data), 2)
        self.assertTrue("A" in g.data)

    def testAuxGraph5(self):
        g = fsquery.graph_aux("root")
        self.assertEqual(g.root, "root")
        self.assertTrue(g.add_node("A"))
        self.assertFalse(g.add_node("A"))
        self.assertTrue(g.add_node("AA"))
        self.assertEqual(len(g.data), 3)
        self.assertTrue("A" in g.data)
        self.assertTrue("AA" in g.data)

    def testAuxGraph6(self):
        g = fsquery.graph_aux("root")
        self.assertEqual(g.root, "root")
        self.assertTrue(g.add_node("A"))
        self.assertTrue(g.add_node("B"))
        self.assertTrue(g.add_node("C"))
        self.assertEqual(len(g.data), 4)
        self.assertTrue("A" in g.data)
        self.assertTrue("B" in g.data)
        self.assertTrue("C" in g.data)

        self.assertTrue(g.add_connection("A", "B"))
        self.assertTrue(g.add_connection("B", "C"))

    def testAuxGraph7(self):
        g = fsquery.graph_aux("root")
        self.assertEqual(g.root, "root")
        self.assertTrue(g.add_node("A"))
        self.assertTrue(g.add_node("B"))
        self.assertTrue(g.add_node("C"))
        self.assertEqual(len(g.data), 4)
        self.assertTrue("A" in g.data)
        self.assertTrue("B" in g.data)
        self.assertTrue("C" in g.data)

        self.assertTrue(g.add_connection("A", "B"))
        self.assertFalse(g.add_connection("A", "D"))
        self.assertFalse(g.add_connection("D", "A"))
        self.assertTrue(g.add_connection("B", "A"))

    def testAuxGraph8(self):
        g = fsquery.graph_aux("root")
        self.assertEqual(g.root, "root")
        self.assertTrue(g.add_node("A"))
        self.assertTrue(g.add_node("B"))
        self.assertTrue(g.add_node("C"))
        self.assertEqual(len(g.data), 4)
        self.assertTrue("A" in g.data)
        self.assertTrue("B" in g.data)
        self.assertTrue("C" in g.data)

        self.assertTrue(g.add_connection("A", "B"))
        self.assertFalse(g.add_connection("A", "B"))
        self.assertTrue(g.add_connection("B", "A"))
        self.assertFalse(g.add_connection("B", "A"))

    def testAuxGraph9(self):
        g = fsquery.graph_aux("root")
        self.assertEqual(g.root, "root")
        self.assertEqual(len(g.data), 1)

        self.assertTrue(g.add_connection("root", "root"))

        self.assertTrue(g.detect_cycle())

    def testAuxGraph10(self):
        g = fsquery.graph_aux("A")
        self.assertEqual(g.root, "A")
        self.assertTrue(g.add_node("B"))
        self.assertEqual(len(g.data), 2)

        self.assertTrue(g.add_connection("A", "B"))
        self.assertTrue(g.add_connection("B", "A"))

        self.assertTrue(g.detect_cycle())

    def testAuxGraph11(self):
        g = fsquery.graph_aux("A")
        self.assertEqual(g.root, "A")
        self.assertTrue(g.add_node("B"))
        self.assertTrue(g.add_node("C"))
        self.assertTrue(g.add_node("D"))
        self.assertEqual(len(g.data), 4)

        self.assertTrue(g.add_connection("A", "B"))
        self.assertTrue(g.add_connection("B", "C"))
        self.assertTrue(g.add_connection("C", "D"))
        self.assertTrue(g.add_connection("D", "B"))

        self.assertTrue(g.detect_cycle())

    def testAuxGraph12(self):
        g = fsquery.graph_aux("A")
        self.assertEqual(g.root, "A")
        self.assertTrue(g.add_node("B"))
        self.assertTrue(g.add_node("C"))
        self.assertTrue(g.add_node("D"))
        self.assertTrue(g.add_node("E"))
        self.assertEqual(len(g.data), 5)
        self.assertTrue("A" in g.data)
        self.assertTrue("B" in g.data)
        self.assertTrue("C" in g.data)
        self.assertTrue("D" in g.data)
        self.assertTrue("E" in g.data)

        self.assertTrue(g.add_connection("A", "B"))
        self.assertTrue(g.add_connection("A", "D"))
        self.assertTrue(g.add_connection("B", "C"))
        self.assertTrue(g.add_connection("B", "D"))
        self.assertTrue(g.add_connection("C", "D"))
        self.assertTrue(g.add_connection("D", "E"))

        self.assertFalse(g.detect_cycle())

    def testAuxGraph13(self):
        g = fsquery.graph_aux("A")
        self.assertEqual(g.root, "A")
        self.assertTrue(g.add_node("B"))
        self.assertTrue(g.add_node("C"))
        self.assertTrue(g.add_node("D"))
        self.assertTrue(g.add_node("E"))
        self.assertTrue(g.add_node("F"))
        self.assertEqual(len(g.data), 6)
        self.assertTrue("A" in g.data)
        self.assertTrue("B" in g.data)
        self.assertTrue("C" in g.data)
        self.assertTrue("D" in g.data)
        self.assertTrue("E" in g.data)
        self.assertTrue("F" in g.data)

        self.assertTrue(g.add_connection("A", "B"))
        self.assertTrue(g.add_connection("B", "F"))
        self.assertTrue(g.add_connection("A", "C"))
        self.assertTrue(g.add_connection("C", "F"))
        self.assertTrue(g.add_connection("A", "D"))
        self.assertTrue(g.add_connection("D", "C"))
        self.assertTrue(g.add_connection("A", "E"))
        self.assertTrue(g.add_connection("E", "F"))

        self.assertFalse(g.detect_cycle())

    def testAuxGraph14(self):
        g = fsquery.graph_aux("root")
        self.assertEqual(g.root, "root")
        self.assertTrue(g.add_node("A"))
        self.assertTrue(g.add_node("B"))
        self.assertTrue(g.add_node("C"))
        self.assertTrue(g.add_node("D"))
        self.assertTrue(g.add_node("E"))
        self.assertTrue(g.add_node("F"))
        self.assertTrue(g.add_node("G"))
        self.assertTrue(g.add_node("H"))
        self.assertTrue(g.add_node("I"))
        self.assertEqual(len(g.data), 10)
        self.assertTrue("A" in g.data)
        self.assertTrue("B" in g.data)
        self.assertTrue("C" in g.data)
        self.assertTrue("D" in g.data)
        self.assertTrue("E" in g.data)
        self.assertTrue("F" in g.data)
        self.assertTrue("G" in g.data)
        self.assertTrue("H" in g.data)
        self.assertTrue("I" in g.data)

        self.assertTrue(g.add_connection("root", "A"))
        self.assertTrue(g.add_connection("A", "B"))
        self.assertTrue(g.add_connection("B", "C"))
        self.assertTrue(g.add_connection("C", "D"))
        self.assertTrue(g.add_connection("D", "E"))
        self.assertTrue(g.add_connection("E", "F"))
        self.assertTrue(g.add_connection("F", "G"))
        self.assertTrue(g.add_connection("G", "H"))
        self.assertTrue(g.add_connection("H", "I"))

        self.assertFalse(g.detect_cycle())

    def testAuxGraph15(self):
        g = fsquery.graph_aux("root")
        self.assertEqual(g.root, "root")
        self.assertTrue(g.add_node("A"))
        self.assertTrue(g.add_node("B"))
        self.assertTrue(g.add_node("C"))
        self.assertTrue(g.add_node("D"))
        self.assertTrue(g.add_node("E"))
        self.assertTrue(g.add_node("F"))
        self.assertTrue(g.add_node("G"))
        self.assertTrue(g.add_node("H"))
        self.assertTrue(g.add_node("I"))
        self.assertEqual(len(g.data), 10)
        self.assertTrue("A" in g.data)
        self.assertTrue("B" in g.data)
        self.assertTrue("C" in g.data)
        self.assertTrue("D" in g.data)
        self.assertTrue("E" in g.data)
        self.assertTrue("F" in g.data)
        self.assertTrue("G" in g.data)
        self.assertTrue("H" in g.data)
        self.assertTrue("I" in g.data)

        self.assertTrue(g.add_connection("root", "A"))
        self.assertTrue(g.add_connection("A", "B"))
        self.assertTrue(g.add_connection("B", "C"))
        self.assertTrue(g.add_connection("C", "D"))
        self.assertTrue(g.add_connection("D", "E"))
        self.assertTrue(g.add_connection("E", "F"))
        self.assertTrue(g.add_connection("F", "G"))
        self.assertTrue(g.add_connection("G", "H"))
        self.assertTrue(g.add_connection("H", "I"))
        self.assertTrue(g.add_connection("I", "A"))

        self.assertTrue(g.detect_cycle())

    def testAuxGraph16(self):
        g = fsquery.graph_aux("A")
        self.assertEqual(g.root, "A")
        self.assertTrue(g.add_node("B"))
        self.assertTrue(g.add_node("C"))
        self.assertTrue(g.add_node("D"))
        self.assertTrue(g.add_node("E"))
        self.assertEqual(len(g.data), 5)
        self.assertTrue("A" in g.data)
        self.assertTrue("B" in g.data)
        self.assertTrue("C" in g.data)
        self.assertTrue("D" in g.data)
        self.assertTrue("E" in g.data)

        self.assertTrue(g.add_connection("A", "B"))
        self.assertTrue(g.add_connection("A", "D"))
        self.assertTrue(g.add_connection("B", "C"))
        self.assertTrue(g.add_connection("B", "D"))
        self.assertTrue(g.add_connection("C", "D"))
        self.assertTrue(g.add_connection("D", "E"))
        self.assertTrue(g.add_connection("E", "C"))

        self.assertTrue(g.detect_cycle())

    def testFilename_qualifies_extension_list(self):
        exts = ["cpp", "py", "sql"]
        self.assertTrue(fsquery.filename_qualifies_extension_list ("/tmp/file.cpp", True, exts) )
        self.assertFalse(fsquery.filename_qualifies_extension_list ("/tmp/file.zip", True, exts) )
        self.assertTrue(fsquery.filename_qualifies_extension_list ("/tmp/file", True, None) )
        self.assertTrue(fsquery.filename_qualifies_extension_list ("/tmp/another", True, []) )

    def testMakecontentlist_1(self):
        v, r = fsquery.makecontentlist(self.test_dir, False, False, True, False, False, False, True, "txt")
        self.assertTrue(v)
        self.assertEqual(len(r), 3)
        self.assertTrue( self.file1 in r )
        self.assertTrue( self.file2 in r )
        self.assertTrue( self.file3 in r )

    def testMakecontentlist_2(self):
        v, r = fsquery.makecontentlist(self.test_dir, False, False, True, False, False, False, True, ["txt", "dat"])
        self.assertTrue(v)
        self.assertEqual(len(r), 4)
        self.assertTrue( self.file1 in r )
        self.assertTrue( self.file2 in r )
        self.assertTrue( self.file3 in r )
        self.assertTrue( self.file4 in r )

    def testMakecontentlist_3(self):
        v, r = fsquery.makecontentlist(self.test_dir, False, False, True, False, False, False, False, ["txt", "dat"])
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertTrue( self.file5 in r )

    def testMakecontentlist_4(self):
        v, r = fsquery.makecontentlist(self.test_dir, False, False, True, False, False, False, True, "bin")
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertEqual( self.file5, r[0] )

    def testMakecontentlist_5(self):
        v, r = fsquery.makecontentlist(self.test_dir, True, False, True, False, False, False, True, "bin")
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertTrue( self.file5 in r )
        self.assertTrue( self.sub1_file2 in r )

    def testMakecontentlist_6(self):
        v, r = fsquery.makecontentlist(self.test_dir, False, False, True, False, False, False, True, None)
        self.assertTrue(v)
        self.assertEqual(len(r), 5)
        self.assertTrue( self.file1 in r )
        self.assertTrue( self.file2 in r )
        self.assertTrue( self.file3 in r )
        self.assertTrue( self.file4 in r )
        self.assertTrue( self.file5 in r )

    def testMakecontentlist_7(self):
        v, r = fsquery.makecontentlist(self.test_dir, True, False, True, False, False, False, True, None)
        self.assertTrue(v)
        self.assertEqual(len(r), 8)
        self.assertTrue( self.file1 in r )
        self.assertTrue( self.file2 in r )
        self.assertTrue( self.file3 in r )
        self.assertTrue( self.file4 in r )
        self.assertTrue( self.file5 in r )
        self.assertTrue( self.sub1_file1 in r )
        self.assertTrue( self.sub1_file2 in r )
        self.assertTrue( self.sub2_file1 in r )

    def testMakecontentlist_8(self):
        v, r = fsquery.makecontentlist(self.test_dir, True, False, True, False, True, False, True, None)
        self.assertTrue(v)
        self.assertEqual(len(r), 11)
        self.assertTrue( self.file1 in r )
        self.assertTrue( self.file2 in r )
        self.assertTrue( self.file3 in r )
        self.assertTrue( self.file4 in r )
        self.assertTrue( self.file5 in r )
        self.assertTrue( self.file6 in r )
        self.assertTrue( self.file7 in r )
        self.assertTrue( self.sub1_file1 in r )
        self.assertTrue( self.sub1_file2 in r )
        self.assertTrue( self.sub2_file1 in r )
        self.assertTrue( self.sub2_file2 in r )

    def testMakecontentlist_9(self):
        v, r = fsquery.makecontentlist(self.test_dir, True, False, True, True, True, False, True, None)
        self.assertTrue(v)
        self.assertEqual(len(r), 13)
        self.assertTrue( self.file1 in r )
        self.assertTrue( self.file2 in r )
        self.assertTrue( self.file3 in r )
        self.assertTrue( self.file4 in r )
        self.assertTrue( self.file5 in r )
        self.assertTrue( self.file6 in r )
        self.assertTrue( self.file7 in r )
        self.assertTrue( self.sub1 in r )
        self.assertTrue( self.sub1_file1 in r )
        self.assertTrue( self.sub1_file2 in r )
        self.assertTrue( self.sub2_file1 in r )
        self.assertTrue( self.sub2_file2 in r )

    def testMakecontentlist_10(self):
        v, r = fsquery.makecontentlist(self.test_dir, True, False, True, True, True, True, True, None)
        self.assertTrue(v)
        self.assertEqual(len(r), 14)
        self.assertTrue( self.file1 in r )
        self.assertTrue( self.file2 in r )
        self.assertTrue( self.file3 in r )
        self.assertTrue( self.file4 in r )
        self.assertTrue( self.file5 in r )
        self.assertTrue( self.file6 in r )
        self.assertTrue( self.file7 in r )
        self.assertTrue( self.sub1 in r )
        self.assertTrue( self.sub1_file1 in r )
        self.assertTrue( self.sub1_file2 in r )
        self.assertTrue( self.sub2 in r )
        self.assertTrue( self.sub2_file1 in r )
        self.assertTrue( self.sub2_file2 in r )

    def testMakecontentlist_11(self):
        v, r = fsquery.makecontentlist(self.test_dir, True, False, False, False, False, True, True, None)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertTrue( self.sub2_sub1 in r )

    def testMakecontentlist_12(self):
        v, r = fsquery.makecontentlist(self.test_dir, True, False, False, False, True, False, True, None)
        self.assertTrue(v)
        self.assertEqual(len(r), 3)
        self.assertTrue( self.sub2_file2 in r )
        self.assertTrue( self.file6 in r )
        self.assertTrue( self.file7 in r )

    def testMakecontentlist_13(self):
        v, r = fsquery.makecontentlist(self.test_dir, True, False, False, True, False, False, True, None)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertTrue( self.sub1 in r )
        self.assertTrue( self.sub2 in r )

    def testMakecontentlist_14(self):

        sub2_sub1_file21 = path_utils.concat_path(self.sub2_sub1, "file21")
        create_and_write_file.create_file_contents(sub2_sub1_file21, "file21-contents")
        self.assertTrue(os.path.exists(sub2_sub1_file21))

        sub2_sub1_file23 = path_utils.concat_path(self.sub2_sub1, "file23")
        create_and_write_file.create_file_contents(sub2_sub1_file23, "file23-contents")
        self.assertTrue(os.path.exists(sub2_sub1_file23))

        sub2_sub1_linksub = path_utils.concat_path(self.sub2_sub1, "linksub")
        os.symlink(self.sub1, sub2_sub1_linksub)
        self.assertTrue(sub2_sub1_linksub)

        linked_sub1_file1 = path_utils.concat_path(self.sub2_sub1, "linksub", path_utils.basename_filtered(self.sub1_file1))
        linked_sub1_file2 = path_utils.concat_path(self.sub2_sub1, "linksub", path_utils.basename_filtered(self.sub1_file2))

        v, r = fsquery.makecontentlist(self.sub2_sub1, True, True, True, True, True, True, True, None)
        self.assertTrue(v)
        self.assertEqual(len(r), 5)
        self.assertTrue( sub2_sub1_linksub in r )
        self.assertTrue( sub2_sub1_file21 in r )
        self.assertTrue( sub2_sub1_file23 in r )
        self.assertTrue( linked_sub1_file1 in r )
        self.assertTrue( linked_sub1_file2 in r )

    def testMakecontentlist_15(self):

        sub2_sub1_file21 = path_utils.concat_path(self.sub2_sub1, "file21")
        create_and_write_file.create_file_contents(sub2_sub1_file21, "file21-contents")
        self.assertTrue(os.path.exists(sub2_sub1_file21))

        sub2_sub1_file23 = path_utils.concat_path(self.sub2_sub1, "file23")
        create_and_write_file.create_file_contents(sub2_sub1_file23, "file23-contents")
        self.assertTrue(os.path.exists(sub2_sub1_file23))

        sub2_sub1_linksub = path_utils.concat_path(self.sub2_sub1, "linksub")
        os.symlink(self.sub1, sub2_sub1_linksub)
        self.assertTrue(sub2_sub1_linksub)

        linked_sub1_file1 = path_utils.concat_path(self.sub2_sub1, "linksub", path_utils.basename_filtered(self.sub1_file1))
        linked_sub1_file2 = path_utils.concat_path(self.sub2_sub1, "linksub", path_utils.basename_filtered(self.sub1_file2))

        v, r = fsquery.makecontentlist(self.sub2_sub1, True, False, True, True, True, True, True, None)
        self.assertTrue(v)
        self.assertEqual(len(r), 3)
        self.assertTrue( sub2_sub1_linksub in r )
        self.assertTrue( sub2_sub1_file21 in r )
        self.assertTrue( sub2_sub1_file23 in r )
        self.assertFalse( linked_sub1_file1 in r )
        self.assertFalse( linked_sub1_file2 in r )

    def testMakecontentlist_16(self):

        sub2_sub1_linksub = path_utils.concat_path(self.sub2_sub1, "linksub")
        os.symlink(self.sub1, sub2_sub1_linksub)
        self.assertTrue(sub2_sub1_linksub)

        linked_sub1_file1 = path_utils.concat_path(self.sub2_sub1, "linksub", path_utils.basename_filtered(self.sub1_file1))
        linked_sub1_file2 = path_utils.concat_path(self.sub2_sub1, "linksub", path_utils.basename_filtered(self.sub1_file2))

        v, r = fsquery.makecontentlist(sub2_sub1_linksub, True, True, True, True, True, True, True, None)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertTrue( linked_sub1_file1 in r )
        self.assertTrue( linked_sub1_file2 in r )

    def testMakecontentlist_17(self):

        sub2_sub1_linksub = path_utils.concat_path(self.sub2_sub1, "linksub")
        os.symlink(self.sub1, sub2_sub1_linksub)
        self.assertTrue(sub2_sub1_linksub)

        linked_sub1_file1 = path_utils.concat_path(self.sub2_sub1, "linksub", path_utils.basename_filtered(self.sub1_file1))
        linked_sub1_file2 = path_utils.concat_path(self.sub2_sub1, "linksub", path_utils.basename_filtered(self.sub1_file2))

        v, r = fsquery.makecontentlist(sub2_sub1_linksub, True, False, True, True, True, True, True, None)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertTrue( linked_sub1_file1 in r )
        self.assertTrue( linked_sub1_file2 in r )

    def testMakecontentlist_18(self):

        sub2_sub1_linksub = path_utils.concat_path(self.sub2_sub1, "linksub")
        os.symlink(self.sub1, sub2_sub1_linksub)
        self.assertTrue(sub2_sub1_linksub)

        linked_sub1_file1 = path_utils.concat_path(self.sub2_sub1, "linksub", path_utils.basename_filtered(self.sub1_file1))
        linked_sub1_file2 = path_utils.concat_path(self.sub2_sub1, "linksub", path_utils.basename_filtered(self.sub1_file2))

        v, r = fsquery.makecontentlist(sub2_sub1_linksub, False, True, True, True, True, True, True, None)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertTrue( linked_sub1_file1 in r )
        self.assertTrue( linked_sub1_file2 in r )

    def testMakecontentlist_19(self):

        sub2_sub1_file21 = path_utils.concat_path(self.sub2_sub1, "file21")
        create_and_write_file.create_file_contents(sub2_sub1_file21, "file21-contents")
        self.assertTrue(os.path.exists(sub2_sub1_file21))

        sub2_sub1_file23 = path_utils.concat_path(self.sub2_sub1, "file23")
        create_and_write_file.create_file_contents(sub2_sub1_file23, "file23-contents")
        self.assertTrue(os.path.exists(sub2_sub1_file23))

        sub2_sub1_linksub = path_utils.concat_path(self.sub2_sub1, "linksub")
        os.symlink(self.sub1, sub2_sub1_linksub)
        self.assertTrue(sub2_sub1_linksub)

        linked_sub1_file1 = path_utils.concat_path(self.sub2_sub1, "linksub", path_utils.basename_filtered(self.sub1_file1))
        linked_sub1_file2 = path_utils.concat_path(self.sub2_sub1, "linksub", path_utils.basename_filtered(self.sub1_file2))

        v, r = fsquery.makecontentlist(self.sub2_sub1, False, True, True, True, True, True, True, None)
        self.assertTrue(v)
        self.assertEqual(len(r), 3)
        self.assertTrue( sub2_sub1_linksub in r )
        self.assertTrue( sub2_sub1_file21 in r )
        self.assertTrue( sub2_sub1_file23 in r )
        self.assertFalse( linked_sub1_file1 in r )
        self.assertFalse( linked_sub1_file2 in r )

    def testMakecontentlist_20(self):

        sub2_sub1_file21 = path_utils.concat_path(self.sub2_sub1, "file21")
        create_and_write_file.create_file_contents(sub2_sub1_file21, "file21-contents")
        self.assertTrue(os.path.exists(sub2_sub1_file21))

        sub2_sub1_file23 = path_utils.concat_path(self.sub2_sub1, "file23")
        create_and_write_file.create_file_contents(sub2_sub1_file23, "file23-contents")
        self.assertTrue(os.path.exists(sub2_sub1_file23))

        sub2_sub1_linksub = path_utils.concat_path(self.sub2_sub1, "linksub")
        os.symlink(self.sub1, sub2_sub1_linksub)
        self.assertTrue(sub2_sub1_linksub)

        linked_sub1_file1 = path_utils.concat_path(self.sub2_sub1, "linksub", path_utils.basename_filtered(self.sub1_file1))
        linked_sub1_file2 = path_utils.concat_path(self.sub2_sub1, "linksub", path_utils.basename_filtered(self.sub1_file2))

        v, r = fsquery.makecontentlist(self.sub2_sub1, False, True, True, False, True, True, True, None)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertFalse( sub2_sub1_linksub in r )
        self.assertTrue( sub2_sub1_file21 in r )
        self.assertTrue( sub2_sub1_file23 in r )
        self.assertFalse( linked_sub1_file1 in r )
        self.assertFalse( linked_sub1_file2 in r )

    def testMakecontentlist_21(self):

        another = self._create_test_dir("another")

        sub2_sub1_file21 = path_utils.concat_path(self.sub2_sub1, "file21")
        create_and_write_file.create_file_contents(sub2_sub1_file21, "file21-contents")
        self.assertTrue(os.path.exists(sub2_sub1_file21))

        sub2_sub1_file23 = path_utils.concat_path(self.sub2_sub1, "file23")
        create_and_write_file.create_file_contents(sub2_sub1_file23, "file23-contents")
        self.assertTrue(os.path.exists(sub2_sub1_file23))

        sub2_sub1_linksub = path_utils.concat_path(self.sub2_sub1, "linksub")
        os.symlink(another, sub2_sub1_linksub)
        self.assertTrue(sub2_sub1_linksub)

        linked_sub1_file1 = path_utils.concat_path(self.sub2_sub1, "linksub", path_utils.basename_filtered(self.sub1_file1))
        linked_sub1_file2 = path_utils.concat_path(self.sub2_sub1, "linksub", path_utils.basename_filtered(self.sub1_file2))

        another_circular = path_utils.concat_path(another, "circular")
        os.symlink(self.sub2_sub1, another_circular)

        v, r = fsquery.makecontentlist(self.sub2_sub1, False, True, True, False, True, True, True, None)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertFalse( sub2_sub1_linksub in r )
        self.assertTrue( sub2_sub1_file21 in r )
        self.assertTrue( sub2_sub1_file23 in r )
        self.assertFalse( linked_sub1_file1 in r )
        self.assertFalse( linked_sub1_file2 in r )

    def testMakecontentlist_22(self):

        another = self._create_test_dir("another")

        sub2_sub1_file21 = path_utils.concat_path(self.sub2_sub1, "file21")
        create_and_write_file.create_file_contents(sub2_sub1_file21, "file21-contents")
        self.assertTrue(os.path.exists(sub2_sub1_file21))

        sub2_sub1_file23 = path_utils.concat_path(self.sub2_sub1, "file23")
        create_and_write_file.create_file_contents(sub2_sub1_file23, "file23-contents")
        self.assertTrue(os.path.exists(sub2_sub1_file23))

        sub2_sub1_linksub = path_utils.concat_path(self.sub2_sub1, "linksub")
        os.symlink(another, sub2_sub1_linksub)
        self.assertTrue(sub2_sub1_linksub)

        linked_sub1_file1 = path_utils.concat_path(self.sub2_sub1, "linksub", path_utils.basename_filtered(self.sub1_file1))
        linked_sub1_file2 = path_utils.concat_path(self.sub2_sub1, "linksub", path_utils.basename_filtered(self.sub1_file2))

        another_circular = path_utils.concat_path(another, "circular")
        os.symlink(self.sub2_sub1, another_circular)

        v, r = fsquery.makecontentlist(self.sub2_sub1, True, True, True, False, True, True, True, None)
        self.assertFalse(v)
        self.assertTrue(self.sub2_sub1 in r)

    def testMakecontentlist_23(self):

        another = self._create_test_dir("another")
        another_another = path_utils.concat_path(another, "another")
        os.mkdir(another_another)
        another_another_another = path_utils.concat_path(another_another, "another")
        os.mkdir(another_another_another)

        another_another_another_sub = path_utils.concat_path(another_another_another, "sub")
        os.mkdir(another_another_another_sub)
        another_another_another_sub_another = path_utils.concat_path(another_another_another_sub, "another")
        os.mkdir(another_another_another_sub_another)

        another_another_another_sub_another_file71 = path_utils.concat_path(another_another_another_sub_another, "file71.txt")
        create_and_write_file.create_file_contents(another_another_another_sub_another_file71, "file71-contents")
        self.assertTrue(os.path.exists(another_another_another_sub_another_file71))

        v, r = fsquery.makecontentlist(another, True, True, True, True, True, True, True, None)
        self.assertTrue(v)
        self.assertEqual(len(r), 5)
        self.assertTrue(another_another in r)
        self.assertTrue(another_another_another in r)
        self.assertTrue(another_another_another_sub in r)
        self.assertTrue(another_another_another_sub_another in r)
        self.assertTrue(another_another_another_sub_another_file71 in r)

    def testMakecontentlist_24(self):

        A = self._create_test_dir("A")
        B = path_utils.concat_path(A, "B")
        C = path_utils.concat_path(B, "C")
        D = path_utils.concat_path(A, "D")
        E = path_utils.concat_path(D, "E")
        BD = path_utils.concat_path(B, "BD")
        CD = path_utils.concat_path(C, "CD")

        self.assertTrue(os.path.exists(A))
        self.assertFalse(os.path.exists(B))
        self.assertFalse(os.path.exists(C))
        self.assertFalse(os.path.exists(D))
        self.assertFalse(os.path.exists(E))
        self.assertFalse(os.path.exists(BD))
        self.assertFalse(os.path.exists(CD))

        os.mkdir(B)
        os.mkdir(C)
        os.mkdir(D)
        os.mkdir(E)
        os.symlink(D, BD)
        os.symlink(D, CD)

        self.assertTrue(os.path.exists(B))
        self.assertTrue(os.path.exists(C))
        self.assertTrue(os.path.exists(D))
        self.assertTrue(os.path.exists(E))
        self.assertTrue(os.path.exists(BD))
        self.assertTrue(os.path.exists(CD))

        v, r = fsquery.makecontentlist(A, True, True, True, True, True, True, True, None)
        self.assertTrue(v)
        self.assertEqual(len(r), 8)
        self.assertTrue(B in r)
        self.assertTrue(C in r)
        self.assertTrue(D in r)
        self.assertTrue(E in r)
        self.assertTrue(BD in r)
        self.assertTrue(CD in r)
        self.assertTrue(path_utils.concat_path(BD, "E") in r)
        self.assertTrue(path_utils.concat_path(CD, "E") in r)

    def testMakecontentlist_25(self):

        A = self._create_test_dir("A")
        B = path_utils.concat_path(A, "B")
        C = path_utils.concat_path(B, "C")
        D = path_utils.concat_path(C, "D")
        DB = path_utils.concat_path(D, "DB")

        self.assertTrue(os.path.exists(A))
        self.assertFalse(os.path.exists(B))
        self.assertFalse(os.path.exists(C))
        self.assertFalse(os.path.exists(D))
        self.assertFalse(os.path.exists(DB))

        os.mkdir(B)
        os.mkdir(C)
        os.mkdir(D)
        os.symlink(B, DB)

        self.assertTrue(os.path.exists(B))
        self.assertTrue(os.path.exists(C))
        self.assertTrue(os.path.exists(D))
        self.assertTrue(os.path.exists(DB))

        v, r = fsquery.makecontentlist(A, True, True, True, True, True, True, True, None)
        self.assertFalse(v)
        self.assertTrue(B in r)

    def testMakecontentlist_26(self):

        another = self._create_test_dir("another")
        dummy = self._create_test_dir("dummy")

        another_sub1 = path_utils.concat_path(another, "sub1")
        another_sub2 = path_utils.concat_path(another, "sub2")
        another_sub3 = path_utils.concat_path(another, "sub3")

        self.assertFalse(os.path.exists(another_sub1))
        self.assertFalse(os.path.exists(another_sub2))
        self.assertFalse(os.path.exists(another_sub3))

        os.symlink(dummy, another_sub1)
        os.symlink(dummy, another_sub2)
        os.symlink(dummy, another_sub3)

        self.assertTrue(os.path.exists(another_sub1))
        self.assertTrue(os.path.exists(another_sub2))
        self.assertTrue(os.path.exists(another_sub3))

        another_file75 = path_utils.concat_path(another, "file75.txt")
        create_and_write_file.create_file_contents(another_file75, "file75-contents")
        self.assertTrue(os.path.exists(another_file75))

        v, r = fsquery.makecontentlist(another, True, True, True, True, True, True, True, None)
        self.assertTrue(v)
        self.assertEqual(len(r), 4)
        self.assertTrue(another_sub1 in r)
        self.assertTrue(another_sub2 in r)
        self.assertTrue(another_sub3 in r)
        self.assertTrue(another_file75 in r)

    def testMakecontentlist_27(self):

        A = self._create_test_dir("A")
        B = path_utils.concat_path(A, "B")
        C = path_utils.concat_path(B, "C")
        D = path_utils.concat_path(C, "D")
        E = path_utils.concat_path(D, "E")
        F = path_utils.concat_path(E, "F")
        G = path_utils.concat_path(F, "G")
        H = path_utils.concat_path(G, "H")
        I = path_utils.concat_path(H, "I")

        self.assertTrue(os.path.exists(A))
        self.assertFalse(os.path.exists(B))
        self.assertFalse(os.path.exists(C))
        self.assertFalse(os.path.exists(D))
        self.assertFalse(os.path.exists(E))
        self.assertFalse(os.path.exists(F))
        self.assertFalse(os.path.exists(G))
        self.assertFalse(os.path.exists(H))
        self.assertFalse(os.path.exists(I))

        os.mkdir(B)
        os.mkdir(C)
        os.mkdir(D)
        os.mkdir(E)
        os.mkdir(F)
        os.mkdir(G)
        os.mkdir(H)
        os.mkdir(I)

        self.assertTrue(os.path.exists(B))
        self.assertTrue(os.path.exists(C))
        self.assertTrue(os.path.exists(D))
        self.assertTrue(os.path.exists(E))
        self.assertTrue(os.path.exists(F))
        self.assertTrue(os.path.exists(G))
        self.assertTrue(os.path.exists(H))
        self.assertTrue(os.path.exists(I))

        v, r = fsquery.makecontentlist(A, True, True, True, True, True, True, True, None)
        self.assertTrue(v)
        self.assertEqual(len(r), 8)
        self.assertTrue(B in r)
        self.assertTrue(C in r)
        self.assertTrue(D in r)
        self.assertTrue(E in r)
        self.assertTrue(F in r)
        self.assertTrue(G in r)
        self.assertTrue(H in r)
        self.assertTrue(I in r)

    def testMakecontentlist_28(self):

        A = self._create_test_dir("A")
        B = path_utils.concat_path(A, "B")
        C = path_utils.concat_path(B, "C")
        D = path_utils.concat_path(C, "D")
        E = path_utils.concat_path(D, "E")
        F = path_utils.concat_path(E, "F")
        G = path_utils.concat_path(F, "G")
        H = path_utils.concat_path(G, "H")
        I = path_utils.concat_path(H, "I")
        IA = path_utils.concat_path(I, "IA")

        self.assertTrue(os.path.exists(A))
        self.assertFalse(os.path.exists(B))
        self.assertFalse(os.path.exists(C))
        self.assertFalse(os.path.exists(D))
        self.assertFalse(os.path.exists(E))
        self.assertFalse(os.path.exists(F))
        self.assertFalse(os.path.exists(G))
        self.assertFalse(os.path.exists(H))
        self.assertFalse(os.path.exists(I))
        self.assertFalse(os.path.exists(IA))

        os.mkdir(B)
        os.mkdir(C)
        os.mkdir(D)
        os.mkdir(E)
        os.mkdir(F)
        os.mkdir(G)
        os.mkdir(H)
        os.mkdir(I)
        os.symlink(A, IA)

        self.assertTrue(os.path.exists(B))
        self.assertTrue(os.path.exists(C))
        self.assertTrue(os.path.exists(D))
        self.assertTrue(os.path.exists(E))
        self.assertTrue(os.path.exists(F))
        self.assertTrue(os.path.exists(G))
        self.assertTrue(os.path.exists(H))
        self.assertTrue(os.path.exists(I))
        self.assertTrue(os.path.exists(IA))

        v, r = fsquery.makecontentlist(A, True, True, True, True, True, True, True, None)
        self.assertFalse(v)
        self.assertTrue(A in r)

    def testMakecontentlist_29(self):

        A = self._create_test_dir("A")
        AA = path_utils.concat_path(A, "AA")
        self.assertTrue(os.path.exists(A))
        os.symlink(A, AA)
        self.assertTrue(os.path.exists(AA))

        v, r = fsquery.makecontentlist(A, True, True, True, True, True, True, True, None)
        self.assertFalse(v)
        self.assertTrue(A in r)

    def testMakecontentlist_30(self):

        A = self._create_test_dir("A")
        B = path_utils.concat_path(A, "B")

        self.assertTrue(os.path.exists(A))
        self.assertFalse(os.path.exists(B))
        os.mkdir(B)
        self.assertTrue(os.path.exists(B))

        BA = path_utils.concat_path(B, "BA")
        self.assertFalse(os.path.exists(BA))
        os.symlink(A, BA)
        self.assertTrue(os.path.exists(BA))

        v, r = fsquery.makecontentlist(A, True, True, True, True, True, True, True, None)
        self.assertFalse(v)
        self.assertTrue(A in r)

    def testMakecontentlist_31(self):

        blanksub = path_utils.concat_path(self.test_dir, " ")
        self.assertFalse(os.path.exists(blanksub))
        os.mkdir(blanksub)
        self.assertTrue(os.path.exists(blanksub))

        blankfile1 = path_utils.concat_path(blanksub, " ")
        self.assertFalse(os.path.exists(blankfile1))
        create_and_write_file.create_file_contents(blankfile1, "blank contents")
        self.assertTrue(os.path.exists(blankfile1))

        blankfile2 = path_utils.concat_path(blanksub, "   ")
        self.assertFalse(os.path.exists(blankfile2))
        create_and_write_file.create_file_contents(blankfile2, "blank contents")
        self.assertTrue(os.path.exists(blankfile2))

        v, r = fsquery.makecontentlist(blanksub, False, False, True, False, True, True, True, None)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertTrue( blankfile1 in r )
        self.assertTrue( blankfile2 in r )

    def testMakecontentlist_32(self):

        subtest = path_utils.concat_path(self.test_dir, "subtest")
        self.assertFalse(os.path.exists(subtest))
        os.mkdir(subtest)
        self.assertTrue(os.path.exists(subtest))

        subtestfile1 = path_utils.concat_path(subtest, "file1.txt")
        self.assertFalse(os.path.exists(subtestfile1))
        create_and_write_file.create_file_contents(subtestfile1, "blank contents")
        self.assertTrue(os.path.exists(subtestfile1))

        subtestfile2 = path_utils.concat_path(subtest, "file2.txt")
        self.assertFalse(os.path.exists(subtestfile2))
        os.symlink(subtestfile1, subtestfile2)
        self.assertTrue(os.path.exists(subtestfile2))

        os.unlink(subtestfile1)
        self.assertFalse(os.path.exists(subtestfile1))
        self.assertTrue(path_utils.is_path_broken_symlink(subtestfile2))

        v, r = fsquery.makecontentlist(subtest, False, False, True, True, True, True, True, None)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertFalse( subtestfile1 in r )
        self.assertTrue( subtestfile2 in r )

    def testMakecontentlist_33(self):

        subtest = path_utils.concat_path(self.test_dir, "subtest")
        self.assertFalse(os.path.exists(subtest))
        os.mkdir(subtest)
        self.assertTrue(os.path.exists(subtest))

        subtestfile1 = path_utils.concat_path(subtest, "file1.txt")
        self.assertFalse(os.path.exists(subtestfile1))
        create_and_write_file.create_file_contents(subtestfile1, "blank contents")
        self.assertTrue(os.path.exists(subtestfile1))

        subtestfile2 = path_utils.concat_path(subtest, "file2.txt")
        self.assertFalse(os.path.exists(subtestfile2))
        os.symlink(subtestfile1, subtestfile2)
        self.assertTrue(os.path.exists(subtestfile2))

        os.unlink(subtestfile1)
        self.assertFalse(os.path.exists(subtestfile1))
        self.assertTrue(path_utils.is_path_broken_symlink(subtestfile2))

        v, r = fsquery.makecontentlist(subtest, True, False, True, True, True, True, True, None)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertFalse( subtestfile1 in r )
        self.assertTrue( subtestfile2 in r )

    def testMakecontentlist_34(self):

        subtest = path_utils.concat_path(self.test_dir, "subtest")
        self.assertFalse(os.path.exists(subtest))
        os.mkdir(subtest)
        self.assertTrue(os.path.exists(subtest))

        subtest_sub1 = path_utils.concat_path(subtest, "sub1")
        self.assertFalse(os.path.exists(subtest_sub1))
        os.mkdir(subtest_sub1)
        self.assertTrue(os.path.exists(subtest_sub1))

        subtest_sub2 = path_utils.concat_path(subtest, "sub2")
        self.assertFalse(os.path.exists(subtest_sub2))
        os.symlink(subtest_sub1, subtest_sub2)
        self.assertTrue(os.path.exists(subtest_sub2))

        shutil.rmtree(subtest_sub1)
        self.assertFalse(os.path.exists(subtest_sub1))
        self.assertTrue(path_utils.is_path_broken_symlink(subtest_sub2))

        v, r = fsquery.makecontentlist(subtest, False, False, True, True, True, True, True, None)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertFalse( subtest_sub1 in r )
        self.assertTrue( subtest_sub2 in r )

    def testMakecontentlist_35(self):

        subtest = path_utils.concat_path(self.test_dir, "subtest")
        self.assertFalse(os.path.exists(subtest))
        os.mkdir(subtest)
        self.assertTrue(os.path.exists(subtest))

        subtest_sub1 = path_utils.concat_path(subtest, "sub1")
        self.assertFalse(os.path.exists(subtest_sub1))
        os.mkdir(subtest_sub1)
        self.assertTrue(os.path.exists(subtest_sub1))

        subtest_sub2 = path_utils.concat_path(subtest, "sub2")
        self.assertFalse(os.path.exists(subtest_sub2))
        os.symlink(subtest_sub1, subtest_sub2)
        self.assertTrue(os.path.exists(subtest_sub2))

        shutil.rmtree(subtest_sub1)
        self.assertFalse(os.path.exists(subtest_sub1))
        self.assertTrue(path_utils.is_path_broken_symlink(subtest_sub2))

        v, r = fsquery.makecontentlist(subtest, True, False, True, True, True, True, True, None)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertFalse( subtest_sub1 in r )
        self.assertTrue( subtest_sub2 in r )

if __name__ == "__main__":
    unittest.main()
