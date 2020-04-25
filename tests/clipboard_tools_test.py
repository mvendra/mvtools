#!/usr/bin/env python3

import sys
import os
import unittest

import getfromclipboard
import sendtoclipboard

class ClipboardToolsTest(unittest.TestCase):

    def testSanityCheck(self):

        test_string = "parabola"
        sendtoclipboard.sendtoclipboard(test_string)
        self.assertEqual(getfromclipboard.getfromclipboard(), test_string)

if __name__ == '__main__':
    unittest.main()
