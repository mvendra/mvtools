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

    def testGenericParse(self):

        self.assertEqual(string_utils.generic_parse(None, None), None)
        self.assertEqual(string_utils.generic_parse("", None), None)
        self.assertEqual(string_utils.generic_parse("", ""), "")
        self.assertEqual(string_utils.generic_parse("abc:def", ":"), "abc")

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

    def testConvertDosToUnix(self):

        self.assertEqual(string_utils.convert_dos_to_unix(None), None)
        self.assertEqual(string_utils.convert_dos_to_unix(""), "")
        self.assertEqual(string_utils.convert_dos_to_unix("abc\r\ndef"), "abc\ndef")
        self.assertEqual(string_utils.convert_dos_to_unix("abc\r\rdef"), "abc\r\rdef")
        self.assertEqual(string_utils.convert_dos_to_unix("abc\rdef"), "abc\rdef")
        self.assertEqual(string_utils.convert_dos_to_unix("abc\ndef"), "abc\ndef")
        self.assertEqual(string_utils.convert_dos_to_unix("abc\n\ndef"), "abc\n\ndef")
        self.assertEqual(string_utils.convert_dos_to_unix("abc\n\rdef"), "abc\n\rdef")
        self.assertEqual(string_utils.convert_dos_to_unix("abc\n\rdef"), "abc\n\rdef")
        self.assertEqual(string_utils.convert_dos_to_unix("abc\r\n\rdef"), "abc\n\rdef")
        self.assertEqual(string_utils.convert_dos_to_unix("abc\r\n\r\ndef"), "abc\n\ndef")
        self.assertEqual(string_utils.convert_dos_to_unix("abc\x0D\x0Adef"), "abc\ndef")
        self.assertEqual(string_utils.convert_dos_to_unix("abc\x0Adef"), "abc\ndef")

if __name__ == '__main__':
    unittest.main()
