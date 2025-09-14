#!/usr/bin/env python

import sys
import os
import shutil
import unittest

import mvtools_test_fixture
import create_and_write_file
import path_utils

import text18_schema_checker

class Text18SchemaCheckerTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("text18_schema_checker_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # target files
        self.left_t20 = path_utils.concat_path(self.test_dir, "left.t20")
        self.right_t20 = path_utils.concat_path(self.test_dir, "right.t20")
        self.nonexistent = path_utils.concat_path(self.test_dir, "nonexistent")

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testCompareT18Schemas1(self):

        create_and_write_file.create_file_contents(self.left_t20, "[\n@main\n* entry = \"value1\"\n]")
        create_and_write_file.create_file_contents(self.right_t20, "[\n@main\n* entry = \"value2\"\n]")

        v, r = text18_schema_checker.compare_t18_schemas(self.nonexistent, self.right_t20)
        self.assertFalse(v)

    def testCompareT18Schemas2(self):

        create_and_write_file.create_file_contents(self.left_t20, "[\n@main\n* entry = \"value1\"\n]")
        create_and_write_file.create_file_contents(self.right_t20, "[\n@main\n* entry = \"value2\"\n]")

        v, r = text18_schema_checker.compare_t18_schemas(self.left_t20, self.nonexistent)
        self.assertFalse(v)

    def testCompareT18Schemas3(self):

        create_and_write_file.create_file_contents(self.left_t20, "[\n@main\n* entry = \"value1\"\n")
        create_and_write_file.create_file_contents(self.right_t20, "[\n@main\n* entry = \"value2\"\n]")

        v, r = text18_schema_checker.compare_t18_schemas(self.left_t20, self.right_t20)
        self.assertFalse(v)

    def testCompareT18Schemas4(self):

        create_and_write_file.create_file_contents(self.left_t20, "[\n@main\n* entry = \"value1\"\n]")
        create_and_write_file.create_file_contents(self.right_t20, "[\n@main\n* entry = \"value2\"\n")

        v, r = text18_schema_checker.compare_t18_schemas(self.left_t20, self.right_t20)
        self.assertFalse(v)

    def testCompareT18Schemas5(self):

        create_and_write_file.create_file_contents(self.left_t20, "[\n@main\n* entry = \"value1\"\n]")
        create_and_write_file.create_file_contents(self.right_t20, "[\n@main\n* entry = \"value2\"\n]")

        v, r = text18_schema_checker.compare_t18_schemas(self.left_t20, self.right_t20)
        self.assertTrue(v)
        self.assertEqual(r, [])

    def testCompareT18Schemas6(self):

        create_and_write_file.create_file_contents(self.left_t20, "[\n@main\n* entry = \"value1\"\n]\n[\n@sub\n* entry = \"value1\"\n]")
        create_and_write_file.create_file_contents(self.right_t20, "[\n@main\n* entry = \"value2\"\n]")

        v, r = text18_schema_checker.compare_t18_schemas(self.left_t20, self.right_t20)
        self.assertTrue(v)
        self.assertEqual(r, ["[left.t20] has [2] groups, whereas [right.t20] has [1]"])

    def testCompareT18Schemas7(self):

        create_and_write_file.create_file_contents(self.left_t20, "[\n@main\n* entry = \"value1\"\n]\n[\n@sub\n* entry = \"value1\"\n]")
        create_and_write_file.create_file_contents(self.right_t20, "[\n@main\n* entry = \"value2\"\n]\n[\n@bus\n* entry = \"value2\"\n]")

        v, r = text18_schema_checker.compare_t18_schemas(self.left_t20, self.right_t20)
        self.assertTrue(v)
        self.assertEqual(r, ["Groups at index [1] are different: [left.t20][sub] vs. [right.t20][bus]"])

    def testCompareT18Schemas8(self):

        create_and_write_file.create_file_contents(self.left_t20, "[\n@main\n* entry = \"value1\"\n]\n[\n@sub\n* entry = \"value1\"\n]\n[\n@more\n* entry = \"value1\"\n]")
        create_and_write_file.create_file_contents(self.right_t20, "[\n@main\n* entry = \"value2\"\n]\n[\n@bus\n* entry = \"value2\"\n]\n[\n@moar\n* entry = \"value2\"\n]")

        v, r = text18_schema_checker.compare_t18_schemas(self.left_t20, self.right_t20)
        self.assertTrue(v)
        self.assertEqual(r, ["Groups at index [1] are different: [left.t20][sub] vs. [right.t20][bus]", "Groups at index [2] are different: [left.t20][more] vs. [right.t20][moar]"])

    def testCompareT18Schemas9(self):

        create_and_write_file.create_file_contents(self.left_t20, "[\n@main\n* entry1 = \"value1\"\n]")
        create_and_write_file.create_file_contents(self.right_t20, "[\n@main\n* entry1 = \"value2\"\n* entry2 = \"value3\"\n]")

        v, r = text18_schema_checker.compare_t18_schemas(self.left_t20, self.right_t20)
        self.assertTrue(v)
        self.assertEqual(r, ["[left.t20][main] has [1] entries, whereas [right.t20][main] has [2]"])

    def testCompareT18Schemas10(self):

        create_and_write_file.create_file_contents(self.left_t20, "[\n@main\n* entry1 = \"value\"\n]")
        create_and_write_file.create_file_contents(self.right_t20, "[\n@main\n* entry2 = \"value\"\n]")

        v, r = text18_schema_checker.compare_t18_schemas(self.left_t20, self.right_t20)
        self.assertTrue(v)
        self.assertEqual(r, ["Entries at index [0] (from groups at index [0]) are different: [left.t20][main][entry1] vs. [right.t20][main][entry2]"])

    def testCompareT18Schemas11(self):

        create_and_write_file.create_file_contents(self.left_t20, "[\n@main\n* entry1 = \"value\"\n* entry2 = \"value\"\n]")
        create_and_write_file.create_file_contents(self.right_t20, "[\n@main\n* entry3 = \"value\"\n* entry4 = \"value\"\n]")

        v, r = text18_schema_checker.compare_t18_schemas(self.left_t20, self.right_t20)
        self.assertTrue(v)
        self.assertEqual(r, ["Entries at index [0] (from groups at index [0]) are different: [left.t20][main][entry1] vs. [right.t20][main][entry3]", "Entries at index [1] (from groups at index [0]) are different: [left.t20][main][entry2] vs. [right.t20][main][entry4]"])

if __name__ == "__main__":
    unittest.main()
