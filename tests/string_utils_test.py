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

    def testLineListToString(self):

        self.assertEqual(string_utils.line_list_to_string(None), None)
        self.assertEqual(string_utils.line_list_to_string(123), None)
        self.assertEqual(string_utils.line_list_to_string([123]), None)
        self.assertEqual(string_utils.line_list_to_string([]), "")
        self.assertEqual(string_utils.line_list_to_string(["first"]), "first")
        self.assertEqual(string_utils.line_list_to_string(["first", "second", "third"]), "first\nsecond\nthird")

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

    def testIsHexString(self):

        self.assertFalse(string_utils.is_hex_string(None))
        self.assertFalse(string_utils.is_hex_string(""))
        self.assertTrue(string_utils.is_hex_string("aabbcc"))
        self.assertTrue(string_utils.is_hex_string("ab38563fd1a6b839c"))
        self.assertTrue(string_utils.is_hex_string("11111111111111"))
        self.assertFalse(string_utils.is_hex_string("ab38563fd1g6b839c"))
        self.assertFalse(string_utils.is_hex_string("aabb.c"))

    def testIsDecString(self):

        self.assertFalse(string_utils.is_dec_string(None))
        self.assertFalse(string_utils.is_dec_string(""))
        self.assertFalse(string_utils.is_dec_string("aabbcc"))
        self.assertFalse(string_utils.is_dec_string("ab38563fd1a6b839c"))
        self.assertTrue(string_utils.is_dec_string("11111111111111"))
        self.assertTrue(string_utils.is_dec_string("1234567890"))
        self.assertFalse(string_utils.is_dec_string("1234567890a"))
        self.assertFalse(string_utils.is_dec_string("ab38563fd1g6b839c"))
        self.assertFalse(string_utils.is_dec_string("123.0"))

    def testIsAscCharString(self):

        self.assertFalse(string_utils.is_asc_char_string(None))
        self.assertFalse(string_utils.is_asc_char_string(""))
        self.assertTrue(string_utils.is_asc_char_string("qwertyuiopasdfghjklzxcvbnm"))
        self.assertTrue(string_utils.is_asc_char_string("QWERTYUIOPASDFGHJKLZXCVBNM"))
        self.assertFalse(string_utils.is_asc_char_string("qwertyuiopasdfghjklzxcvbnm1"))
        self.assertFalse(string_utils.is_asc_char_string("qwertyuiopasdfghjklzxcvbnm2"))
        self.assertFalse(string_utils.is_asc_char_string("qwertyuiopasdfghjklzxcvbnm3"))
        self.assertFalse(string_utils.is_asc_char_string("qwertyuiopasdfghjklzxcvbnm4"))
        self.assertFalse(string_utils.is_asc_char_string("qwertyuiopasdfghjklzxcvbnm5"))
        self.assertFalse(string_utils.is_asc_char_string("qwertyuiopasdfghjklzxcvbnm6"))
        self.assertFalse(string_utils.is_asc_char_string("qwertyuiopasdfghjklzxcvbnm7"))
        self.assertFalse(string_utils.is_asc_char_string("qwertyuiopasdfghjklzxcvbnm8"))
        self.assertFalse(string_utils.is_asc_char_string("qwertyuiopasdfghjklzxcvbnm9"))
        self.assertFalse(string_utils.is_asc_char_string("qwertyuiopasdfghjklzxcvbnm0"))
        self.assertFalse(string_utils.is_asc_char_string("qwertyuiopasdfghjklzxcvbnm!"))
        self.assertFalse(string_utils.is_asc_char_string("qwertyuiopasdfghjklzxcvbnm@"))
        self.assertFalse(string_utils.is_asc_char_string("qwertyuiopasdfghjklzxcvbnm#"))
        self.assertFalse(string_utils.is_asc_char_string("qwertyuiopasdfghjklzxcvbnm$"))
        self.assertFalse(string_utils.is_asc_char_string("qwertyuiopasdfghjklzxcvbnm%"))
        self.assertFalse(string_utils.is_asc_char_string("qwertyuiopasdfghjklzxcvbnm^"))
        self.assertFalse(string_utils.is_asc_char_string("qwertyuiopasdfghjklzxcvbnm&"))
        self.assertFalse(string_utils.is_asc_char_string("qwertyuiopasdfghjklzxcvbnm*"))
        self.assertFalse(string_utils.is_asc_char_string("qwertyuiopasdfghjklzxcvbnm("))
        self.assertFalse(string_utils.is_asc_char_string("qwertyuiopasdfghjklzxcvbnm)"))
        self.assertFalse(string_utils.is_asc_char_string("qwertyuiopasdfghjklzxcvbnm_"))
        self.assertFalse(string_utils.is_asc_char_string("qwertyuiopasdfghjklzxcvbnm-"))
        self.assertFalse(string_utils.is_asc_char_string("qwertyuiopasdfghjklzxcvbnm+"))
        self.assertFalse(string_utils.is_asc_char_string("qwertyuiopasdfghjklzxcvbnm="))
        self.assertFalse(string_utils.is_asc_char_string("qwertyuiopasdfghjklzxcvbnm~"))
        self.assertFalse(string_utils.is_asc_char_string("qwertyuiopasdfghjklzxcvbnm`"))
        self.assertFalse(string_utils.is_asc_char_string("qwertyuiopasdfghjklzxcvbnm,"))
        self.assertFalse(string_utils.is_asc_char_string("qwertyuiopasdfghjklzxcvbnm<"))
        self.assertFalse(string_utils.is_asc_char_string("qwertyuiopasdfghjklzxcvbnm."))
        self.assertFalse(string_utils.is_asc_char_string("qwertyuiopasdfghjklzxcvbnm>"))
        self.assertFalse(string_utils.is_asc_char_string("qwertyuiopasdfghjklzxcvbnm/"))
        self.assertFalse(string_utils.is_asc_char_string("qwertyuiopasdfghjklzxcvbnm?"))
        self.assertFalse(string_utils.is_asc_char_string("qwertyuiopasdfghjklzxcvbnm:"))
        self.assertFalse(string_utils.is_asc_char_string("qwertyuiopasdfghjklzxcvbnm;"))
        self.assertFalse(string_utils.is_asc_char_string("qwertyuiopasdfghjklzxcvbnm\""))
        self.assertFalse(string_utils.is_asc_char_string("qwertyuiopasdfghjklzxcvbnm'"))
        self.assertFalse(string_utils.is_asc_char_string("qwertyuiopasdfghjklzxcvbnm["))
        self.assertFalse(string_utils.is_asc_char_string("qwertyuiopasdfghjklzxcvbnm{"))
        self.assertFalse(string_utils.is_asc_char_string("qwertyuiopasdfghjklzxcvbnm]"))
        self.assertFalse(string_utils.is_asc_char_string("qwertyuiopasdfghjklzxcvbnm}"))
        self.assertFalse(string_utils.is_asc_char_string("qwertyuiopasdfghjklzxcvbnm\\"))
        self.assertFalse(string_utils.is_asc_char_string("qwertyuiopasdfghjklzxcvbnm|"))

if __name__ == "__main__":
    unittest.main()
