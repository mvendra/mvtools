#!/usr/bin/env python3

import os
import shutil
import unittest

import filter_output

class FilterOutputTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):
        return True, ""

    def tearDown(self):
        pass

    def testIsDigit(self):
        self.assertTrue(filter_output.is_digit("0"))
        self.assertTrue(filter_output.is_digit("1"))
        self.assertTrue(filter_output.is_digit("2"))
        self.assertTrue(filter_output.is_digit("3"))
        self.assertTrue(filter_output.is_digit("4"))
        self.assertTrue(filter_output.is_digit("5"))
        self.assertTrue(filter_output.is_digit("6"))
        self.assertTrue(filter_output.is_digit("7"))
        self.assertTrue(filter_output.is_digit("8"))
        self.assertTrue(filter_output.is_digit("9"))
        self.assertFalse(filter_output.is_digit("a"))

    def testIsHexDigit(self):
        self.assertTrue(filter_output.is_hex_digit("0"))
        self.assertTrue(filter_output.is_hex_digit("1"))
        self.assertTrue(filter_output.is_hex_digit("2"))
        self.assertTrue(filter_output.is_hex_digit("3"))
        self.assertTrue(filter_output.is_hex_digit("4"))
        self.assertTrue(filter_output.is_hex_digit("5"))
        self.assertTrue(filter_output.is_hex_digit("6"))
        self.assertTrue(filter_output.is_hex_digit("7"))
        self.assertTrue(filter_output.is_hex_digit("8"))
        self.assertTrue(filter_output.is_hex_digit("9"))
        self.assertTrue(filter_output.is_hex_digit("a"))
        self.assertTrue(filter_output.is_hex_digit("b"))
        self.assertTrue(filter_output.is_hex_digit("c"))
        self.assertTrue(filter_output.is_hex_digit("d"))
        self.assertTrue(filter_output.is_hex_digit("e"))
        self.assertTrue(filter_output.is_hex_digit("f"))
        self.assertFalse(filter_output.is_hex_digit("g"))

    def testScanHexAddress1(self):
        v, r = filter_output.scan_hex_address(" ", True)
        self.assertFalse(v)

    def testScanHexAddress2(self):
        v, r = filter_output.scan_hex_address("0x7f4b548g59cf abc", True)
        self.assertFalse(v)

    def testScanHexAddress3(self):
        v, r = filter_output.scan_hex_address("0x7f4b548359cf", True)
        self.assertFalse(v)

    def testScanHexAddress4(self):
        v, r = filter_output.scan_hex_address("0x7f4b548359cf abc", True)
        self.assertTrue(v)
        self.assertEqual(r, "abc")

    def testScanHexAddress5(self):
        v, r = filter_output.scan_hex_address("0x7ffffffff def", True)
        self.assertTrue(v)
        self.assertEqual(r, "def")

    def testScanHexAddress6(self):
        v, r = filter_output.scan_hex_address("0x7ffffffff  (something else)", True)
        self.assertTrue(v)
        self.assertEqual(r, "(something else)")

    def testScanHexAddress7(self):
        v, r = filter_output.scan_hex_address("0xffffffffffffffff0 abc", True)
        self.assertFalse(v)

    def testScanHexAddress8(self):
        v, r = filter_output.scan_hex_address("0x7f4b548359cf", False)
        self.assertTrue(v)

    def testScanNextFrameNum1(self):
        v, r = filter_output.scan_next_frame_num(0, " ")
        self.assertFalse(v)

    def testScanNextFrameNum2(self):
        v, r = filter_output.scan_next_frame_num(0, "0 ")
        self.assertTrue(v)
        self.assertEqual(r, "")

    def testScanNextFrameNum3(self):
        v, r = filter_output.scan_next_frame_num(1, "1 ")
        self.assertTrue(v)
        self.assertEqual(r, "")

    def testScanNextFrameNum4(self):
        v, r = filter_output.scan_next_frame_num(2, "2 ")
        self.assertTrue(v)
        self.assertEqual(r, "")

    def testScanNextFrameNum5(self):
        v, r = filter_output.scan_next_frame_num(3, "3 abcdef")
        self.assertTrue(v)
        self.assertEqual(r, "abcdef")

    def testScanNextFrameNum6(self):
        v, r = filter_output.scan_next_frame_num(0, "1 ")
        self.assertFalse(v)

    def testScanNextFrameNum7(self):
        v, r = filter_output.scan_next_frame_num(1, "2 ")
        self.assertFalse(v)

    def testScanEqEqPidEqEq1(self):
        v, r = filter_output.scan_eq_eq_pid_eq_eq("=1==")
        self.assertFalse(v)

    def testScanEqEqPidEqEq2(self):
        v, r = filter_output.scan_eq_eq_pid_eq_eq("==1=")
        self.assertFalse(v)

    def testScanEqEqPidEqEq3(self):
        v, r = filter_output.scan_eq_eq_pid_eq_eq("1")
        self.assertFalse(v)

    def testScanEqEqPidEqEq4(self):
        v, r = filter_output.scan_eq_eq_pid_eq_eq("==12a34==")
        self.assertFalse(v)

    def testScanEqEqPidEqEq5(self):
        v, r = filter_output.scan_eq_eq_pid_eq_eq("==1==")
        self.assertTrue(v)
        self.assertEqual(r, "")

    def testScanEqEqPidEqEq6(self):
        v, r = filter_output.scan_eq_eq_pid_eq_eq("==1234==")
        self.assertTrue(v)
        self.assertEqual(r, "")

    def testScanEqEqPidEqEq7(self):
        v, r = filter_output.scan_eq_eq_pid_eq_eq("==1234==: other stuff")
        self.assertTrue(v)
        self.assertEqual(r, ": other stuff")

    def testIsAsanStackEntry1(self):
        v, r = filter_output.is_asan_stack_entry(0, "   #0 0x7f4b58acda57 in __interceptor_calloc ../../../../src/libsanitizer/asan/asan_malloc_linux.cpp:154")
        self.assertFalse(v)

    def testIsAsanStackEntry2(self):
        v, r = filter_output.is_asan_stack_entry(0, "    #0 0x7f4b58acda57 in")
        self.assertFalse(v)

    def testIsAsanStackEntry3(self):
        v, r = filter_output.is_asan_stack_entry(1, "    #1 0x7f4b5569b045  (<unknown module>")
        self.assertFalse(v)

    def testIsAsanStackEntry4(self):
        v, r = filter_output.is_asan_stack_entry(0, "    #0 0x7f4b58acda57 in __interceptor_calloc ../../../../src/libsanitizer/asan/asan_malloc_linux.cpp:154")
        self.assertTrue(v)

    def testIsAsanStackEntry5(self):
        v, r = filter_output.is_asan_stack_entry(1, "    #1 0x7f4b5569b045  (<unknown module>)")
        self.assertTrue(v)

    def testIsAsanStackEntry6(self):
        v, r = filter_output.is_asan_stack_entry(1, "    #1 0x7f4b5569b045  (<unknown modula>)")
        self.assertFalse(v)

    def testIsAsanStackEntry7(self):
        v, r = filter_output.is_asan_stack_entry(1, "    #1 0x7fb5de828801  (/home/path/out/linux/debug/selftests+0x3a1801)")
        self.assertTrue(v)

if __name__ == "__main__":
    unittest.main()
