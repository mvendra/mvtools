#!/usr/bin/env python3

import sys
import os
import shutil
import unittest

import mvtools_test_fixture
import create_and_write_file
import path_utils

import tree_wrapper

class TreeWrapperTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("tree_wrapper_test_base")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # create test content

        self.file_with_space = path_utils.concat_path(self.test_dir, "fi le.txt")
        create_and_write_file.create_file_contents(self.file_with_space, "abc")
        self.file_with_sep = path_utils.concat_path(self.test_dir, "file_with_sep.txt")
        create_and_write_file.create_file_contents(self.file_with_sep, "abc")
        self.file_with_sep += os.sep

        self.folder_with_space = path_utils.concat_path(self.test_dir, "fol der")
        os.mkdir(self.folder_with_space)
        self.folder_with_space_filler = path_utils.concat_path(self.folder_with_space, "filler.txt")
        create_and_write_file.create_file_contents(self.folder_with_space_filler, "abc")

        self.folder_with_sep = path_utils.concat_path(self.test_dir, "folder_with_sep")
        os.mkdir(self.folder_with_sep)
        self.folder_with_sep_filler = path_utils.concat_path(self.folder_with_sep, "filler.txt")
        create_and_write_file.create_file_contents(self.folder_with_sep_filler, "abc")
        self.folder_with_sep += os.sep

        # base, files
        self.file1 = path_utils.concat_path(self.test_dir, "file1.txt")
        create_and_write_file.create_file_contents(self.file1, "abc")

        self.file_esp1 = path_utils.concat_path(self.test_dir, "   file_esp1.txt")
        create_and_write_file.create_file_contents(self.file_esp1, "abc")

        self.file_esp2 = path_utils.concat_path(self.test_dir, "file_esp2.txt   ")
        create_and_write_file.create_file_contents(self.file_esp2, "abc")

        self.file2 = path_utils.concat_path(self.test_dir, "file2.txt")
        create_and_write_file.create_file_contents(self.file2, "abc")

        # base, folders
        self.folder1 = path_utils.concat_path(self.test_dir, "folder1")
        os.mkdir(self.folder1)

        self.folder2 = path_utils.concat_path(self.test_dir, "folder2")
        os.mkdir(self.folder2)

        self.folder2_sub1 = path_utils.concat_path(self.folder2, "sub1")
        os.mkdir(self.folder2_sub1)

        self.folder2_sub1_file1 = path_utils.concat_path(self.folder2_sub1, "file1.txt")
        create_and_write_file.create_file_contents(self.folder2_sub1_file1, "abc")

        # files in folders

        # folder1
        self.folder1_file1 = path_utils.concat_path(self.folder1, "file1.txt")
        create_and_write_file.create_file_contents(self.folder1_file1, "abc")

        self.folder1_file2 = path_utils.concat_path(self.folder1, "file2.txt")
        create_and_write_file.create_file_contents(self.folder1_file2, "abc")

        # folder2
        self.folder2_file1 = path_utils.concat_path(self.folder2, "file1.txt")
        create_and_write_file.create_file_contents(self.folder2_file1, "abc")

        self.folder2_file2 = path_utils.concat_path(self.folder2, "file2.txt")
        create_and_write_file.create_file_contents(self.folder2_file2, "abc")

        self.expected_contents = "./tree_wrapper_test_base/" + os.linesep + "├── file1.txt" + os.linesep + "├── file2.txt" + os.linesep + "├──    file_esp1.txt" + os.linesep + "├── file_esp2.txt   " + os.linesep + "├── fi le.txt" + os.linesep + "├── file_with_sep.txt" + os.linesep + "├── fol der" + os.linesep + "│   └── filler.txt" + os.linesep + "├── folder1" + os.linesep + "│   ├── file1.txt" + os.linesep + "│   └── file2.txt" + os.linesep + "├── folder2" + os.linesep + "│   ├── file1.txt" + os.linesep + "│   ├── file2.txt" + os.linesep + "│   └── sub1" + os.linesep + "│       └── file1.txt" + os.linesep + "└── folder_with_sep" + os.linesep + "    └── filler.txt" + os.linesep + os.linesep + "5 directories, 13 files" + os.linesep

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testMakeTree(self):
        v, r = tree_wrapper.make_tree(self.test_dir)
        self.assertTrue(v)
        print(r)
        #self.assertEqual(r, self.expected_contents)

if __name__ == '__main__':
    unittest.main()
