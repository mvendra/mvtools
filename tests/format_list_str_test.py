#!/usr/bin/env python3

import sys
import os
import unittest

import format_list_str

class FormatListStrTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testVanilla(self):

        self.assertEqual(format_list_str.format_list_str(None, ""), None)
        self.assertEqual(format_list_str.format_list_str([], ""), "")
        self.assertEqual(format_list_str.format_list_str(["first"], ". "), "first")
        self.assertEqual(format_list_str.format_list_str(["first", "second"], ". "), "first. second")
        self.assertEqual(format_list_str.format_list_str(["first", "second", "third"], ". "), "first. second. third")

if __name__ == "__main__":
    unittest.main()
