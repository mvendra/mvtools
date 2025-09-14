#!/usr/bin/env python

import sys
import os
import shutil
import unittest

import mvtools_test_fixture
import create_and_write_file
import path_utils

import text18_header_indexer

def file_has_contents(filename, contents):
    if not os.path.exists(filename):
        return False
    local_contents = ""
    with open(filename, "r") as f:
        local_contents = f.read()
    if local_contents == contents:
        return True
    return False

class Text18HeaderIndexerTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("text18_header_indexer_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # source files
        self.source1_t20 = path_utils.concat_path(self.test_dir, "source1.t20")
        self.source2_t20 = path_utils.concat_path(self.test_dir, "source2.t20")

        # target output
        self.target_h = path_utils.concat_path(self.test_dir, "target.h")

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testGenerateHeaderIndex1(self):

        create_and_write_file.create_file_contents(self.source1_t20, "[\n@main\n* entry = \"value\"\n]")

        v, r = text18_header_indexer.generate_header_index([self.source1_t20], self.target_h)
        self.assertTrue(v)
        self.assertTrue(file_has_contents(self.target_h, "\n#ifndef _GENERATED_H_\n#define _GENERATED_H_\n\n// main\nTEXT18_MAIN 0\nTEXT18_MAIN_ENTRY 0\n\n#endif // _GENERATED_H_\n"))

    def testGenerateHeaderIndex2(self):

        create_and_write_file.create_file_contents(self.source1_t20, "[\n@main\n* entry1 = \"value1\"\n* entry2 = \"value2\"\n]")

        v, r = text18_header_indexer.generate_header_index([self.source1_t20], self.target_h)
        self.assertTrue(v)
        self.assertTrue(file_has_contents(self.target_h, "\n#ifndef _GENERATED_H_\n#define _GENERATED_H_\n\n// main\nTEXT18_MAIN 0\nTEXT18_MAIN_ENTRY1 0\nTEXT18_MAIN_ENTRY2 1\n\n#endif // _GENERATED_H_\n"))

    def testGenerateHeaderIndex3(self):

        create_and_write_file.create_file_contents(self.source1_t20, "[\n@main\n* entry = \"value\"\n]\n[\n@sub\n* entry = \"value\"\n]")

        v, r = text18_header_indexer.generate_header_index([self.source1_t20], self.target_h)
        self.assertTrue(v)
        self.assertTrue(file_has_contents(self.target_h, "\n#ifndef _GENERATED_H_\n#define _GENERATED_H_\n\n// main\nTEXT18_MAIN 0\nTEXT18_MAIN_ENTRY 0\n\n// sub\nTEXT18_SUB 1\nTEXT18_SUB_ENTRY 0\n\n#endif // _GENERATED_H_\n"))

    def testGenerateHeaderIndex4(self):

        create_and_write_file.create_file_contents(self.source1_t20, "[\n@main\n* entry1 = \"value\"\n* entry2 = \"value\"\n]\n[\n@sub\n* entry1 = \"value\"\n* entry2 = \"value\"\n]")

        v, r = text18_header_indexer.generate_header_index([self.source1_t20], self.target_h)
        self.assertTrue(v)
        self.assertTrue(file_has_contents(self.target_h, "\n#ifndef _GENERATED_H_\n#define _GENERATED_H_\n\n// main\nTEXT18_MAIN 0\nTEXT18_MAIN_ENTRY1 0\nTEXT18_MAIN_ENTRY2 1\n\n// sub\nTEXT18_SUB 1\nTEXT18_SUB_ENTRY1 0\nTEXT18_SUB_ENTRY2 1\n\n#endif // _GENERATED_H_\n"))

    def testGenerateHeaderIndex5(self):

        create_and_write_file.create_file_contents(self.source1_t20, "[\n@main\n* entry = \"value\"\n]")
        create_and_write_file.create_file_contents(self.source2_t20, "[\n@sub\n* entry = \"value\"\n]")

        v, r = text18_header_indexer.generate_header_index([self.source1_t20, self.source2_t20], self.target_h)
        self.assertTrue(v)
        self.assertTrue(file_has_contents(self.target_h, "\n#ifndef _GENERATED_H_\n#define _GENERATED_H_\n\n// main\nTEXT18_MAIN 0\nTEXT18_MAIN_ENTRY 0\n\n// sub\nTEXT18_SUB 1\nTEXT18_SUB_ENTRY 0\n\n#endif // _GENERATED_H_\n"))

    def testGenerateHeaderIndex6(self):

        create_and_write_file.create_file_contents(self.source1_t20, "[\n@main\n* entry1 = \"value\"\n* entry2 = \"value\"\n]")
        create_and_write_file.create_file_contents(self.source2_t20, "[\n@sub\n* entry1 = \"value\"\n* entry2 = \"value\"\n]")

        v, r = text18_header_indexer.generate_header_index([self.source1_t20, self.source2_t20], self.target_h)
        self.assertTrue(v)
        self.assertTrue(file_has_contents(self.target_h, "\n#ifndef _GENERATED_H_\n#define _GENERATED_H_\n\n// main\nTEXT18_MAIN 0\nTEXT18_MAIN_ENTRY1 0\nTEXT18_MAIN_ENTRY2 1\n\n// sub\nTEXT18_SUB 1\nTEXT18_SUB_ENTRY1 0\nTEXT18_SUB_ENTRY2 1\n\n#endif // _GENERATED_H_\n"))

if __name__ == "__main__":
    unittest.main()
