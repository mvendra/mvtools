#!/usr/bin/env python3

import sys
import os
import unittest

import string_utils

class StringUtilsTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testRfindFirstOf_Fail(self):

        self.assertEqual(string_utils.rfind_first_of("", ["e"]), None)
        self.assertEqual(string_utils.rfind_first_of(None, ["e"]), None)
        self.assertEqual(string_utils.rfind_first_of("abcdef", None), None)
        self.assertEqual(string_utils.rfind_first_of("abcdef", []), None)

    def testRfindFirstOf(self):

        self.assertEqual(string_utils.rfind_first_of("abcdef", ["e"]), (4, "e"))
        self.assertEqual(string_utils.rfind_first_of("abcdef", ["z"]), (None, None))
        self.assertEqual(string_utils.rfind_first_of("aaabbbccc", ["b"]), (5, "b"))
        self.assertEqual(string_utils.rfind_first_of("zaabbbccc", ["z"]), (0, "z"))
        self.assertEqual(string_utils.rfind_first_of("aaabbbccc", ["b", "c"]), (8, "c"))
        self.assertEqual(string_utils.rfind_first_of("aaabbbccc", ["b", "c", "a"]), (8, "c"))
        self.assertEqual(string_utils.rfind_first_of("aaabbbccc", ["b", "z"]), (5, "b"))

if __name__ == '__main__':
    unittest.main()
