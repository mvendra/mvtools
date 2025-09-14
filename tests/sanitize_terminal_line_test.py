#!/usr/bin/env python

import sys
import os
import unittest

import sanitize_terminal_line

class SanitizeTerminalLineTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):
        return True, ""

    def tearDown(self):
        pass

    def testSanitizeLine(self):
        self.assertEqual(sanitize_terminal_line.sanitize_terminal_line("\x1b[0m\x1b[01;34m__pycache__\x1b[0m/"), "__pycache__/")
        self.assertEqual(sanitize_terminal_line.sanitize_terminal_line("\x1b[01;34m__pycache__\x1b[0m/"), "__pycache__/")
        self.assertEqual(sanitize_terminal_line.sanitize_terminal_line("\x1b[01;34m__pycache__/"), "__pycache__/")
        self.assertEqual(sanitize_terminal_line.sanitize_terminal_line("__pycache__/"), "__pycache__/")

if __name__ == "__main__":
    unittest.main()
