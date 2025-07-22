#!/usr/bin/env python3

import sys
import os
import unittest

import getfromclipboard
import sendtoclipboard

class ClipboardToolsTest(unittest.TestCase):

    def testSanityCheck(self):

        test_string = "parabola"
        #v, r = sendtoclipboard.sendtoclipboard(test_string) # mvtodo: hangs the terminal when called with launch_list.
        #self.assertTrue(v)
        #v, r = getfromclipboard.getfromclipboard() # mvtodo: meaningless without the above
        #self.assertTrue(v)
        #self.assertEqual(r, test_string)

if __name__ == "__main__":
    unittest.main()
