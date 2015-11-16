#!/usr/bin/python

import unittest
 
import path_utils

class PathUtilsTest(unittest.TestCase):

    def setUp(self):
        pass

    def testFilterPathListNoSameBranch(self):
        expected = ["/bug", "/home", "/shome"]
        result = path_utils.filter_path_list_no_same_branch(["/home", "/home/user/nuke", "/bug", "/home/ooser", "/shome", "/home/bork/nuke/bark"])
        self.assertEqual( expected, result )

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()

