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

    def testCountAnyOfFail(self):

        self.assertEqual(string_utils.count_any_of("", ["e"]), None)
        self.assertEqual(string_utils.count_any_of(None, ["e"]), None)
        self.assertEqual(string_utils.count_any_of("abcdef", None), None)
        self.assertEqual(string_utils.count_any_of("abcdef", []), None)

    def testCountAnyOf(self):

        self.assertEqual(string_utils.count_any_of("aaa/bbb/ccc", ["/"]), 2)
        self.assertEqual(string_utils.count_any_of("aaa/bbb/ccc", ["z"]), 0)
        self.assertEqual(string_utils.count_any_of("aaa/bbb/ccc", ["a"]), 3)
        self.assertEqual(string_utils.count_any_of("aaa/bbb/ccccc", ["c"]), 5)
        self.assertEqual(string_utils.count_any_of("aaa/bbb/cc", ["c", "a"]), 3)
        self.assertEqual(string_utils.count_any_of("aaa/bbb/cc", ["a", "c"]), 3)
        self.assertEqual(string_utils.count_any_of("aaa/bbb/cc", ["a", "c", "a"]), 3)
        self.assertEqual(string_utils.count_any_of("aaa/bbbb/cc", ["a", "c", "a", "b"]), 4)
        self.assertEqual(string_utils.count_any_of("/aaa/bbb/ccc", ["/", "\\"]), 3)
        self.assertEqual(string_utils.count_any_of("C:\\Data\\Folder", ["/", "\\"]), 2)

if __name__ == '__main__':
    unittest.main()
