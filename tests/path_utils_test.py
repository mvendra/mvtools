#!/usr/bin/python3

import os
import shutil
import unittest

import path_utils

class PathUtilsTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):
        return True, ""

    def tearDown(self):
        pass

    def testPopLastExtension(self):
        expected = "file.txt"
        result = path_utils.poplastextension("file.txt.enc")
        self.assertEqual( expected, result )

    def testDeleteFile_IgnoreErrors(self):

        test_folder = os.path.expanduser("~/nuke")
        full_test_file_path = os.path.join(test_folder, "test_file")

        if not os.path.exists(test_folder):
            self.fail("[%s] does not exist." % test_folder)

        with open(full_test_file_path, "w+") as f:
            f.write("rubbish\n")

        path_utils.deletefile_ignoreerrors(full_test_file_path)

        self.assertFalse(os.path.exists(full_test_file_path))

    def testBackpedal_Path(self):
        expected = "/"
        result = path_utils.backpedal_path("/tmp")
        self.assertEqual(expected, result)

    def testArrayToPath(self):
        expected = "/home/user/nuke/"
        result = path_utils.arraytopath(["home", "user", "nuke"])
        self.assertEqual(expected, result)

    def testExplodePath(self):
        expected = "home user"
        result = path_utils.explodepath("/home/user")
        self.assertEqual(expected, result)

    def testScratchFolder1(self):

        test_folder_base = os.path.expanduser("~/nuke")
        test_folder_full = os.path.join(test_folder_base, "scratch")

        if not os.path.exists(test_folder_base):
            self.fail("[%s] does not exist." % test_folder_base)
        # safety first
        if os.path.exists(test_folder_full):
            self.fail("[%s] already exists." % test_folder_full)

        result = path_utils.scratchfolder(test_folder_full)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(test_folder_full))
        shutil.rmtree(test_folder_full)

    def testScratchFolder2(self):

        test_folder_base = os.path.expanduser("~/nuke")
        test_folder_full = os.path.join(test_folder_base, "scratch")

        if not os.path.exists(test_folder_base):
            self.fail("[%s] does not exist." % test_folder_base)
        # safety first
        if os.path.exists(test_folder_full):
            self.fail("[%s] already exists." % test_folder_full)

        os.mkdir(test_folder_full) # variation: will scratch a pre-existing folder
        result = path_utils.scratchfolder(test_folder_full)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(test_folder_full))
        shutil.rmtree(test_folder_full)

    def testGuaranteeFolder(self):

        test_folder_base = os.path.expanduser("~/nuke")
        test_folder_first = os.path.join(test_folder_base, "first")
        test_folder_second = os.path.join(test_folder_first, "second")

        if not os.path.exists(test_folder_base):
            self.fail("[%s] does not exist." % test_folder_base)

        # safety first
        if os.path.exists(test_folder_first):
            self.fail("[%s] already exists." % test_folder_first)
        if os.path.exists(test_folder_second):
            self.fail("[%s] already exists." % test_folder_second)

        path_utils.guaranteefolder(test_folder_second)
        self.assertTrue(os.path.exists(test_folder_second))
        shutil.rmtree(test_folder_first)

    def testFilterPathListNoSameBranch(self):
        expected = ["/bug", "/home", "/shome"]
        result = path_utils.filter_path_list_no_same_branch(["/home", "/home/user/nuke", "/bug", "/home/ooser", "/shome", "/home/bork/nuke/bark"])
        self.assertEqual( expected, result )

if __name__ == '__main__':
    unittest.main()
