#!/usr/bin/env python3

import os
import shutil
import unittest

import mvtools_test_fixture
import path_utils

class PathUtilsTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("path_utils_test")
        if not v:
            return v, r
        self.test_base_dir = r[0]
        self.test_dir = r[1]

        self.folder1 = os.path.join(self.test_dir, "folder1")
        os.mkdir(self.folder1)
        self.folder2 = os.path.join(self.test_dir, "folder2")
        os.mkdir(self.folder2)
        self.nonexistent = os.path.join(self.test_dir, "nonexistent")

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testPopLastExtension(self):
        expected = "file.txt"
        result = path_utils.poplastextension("file.txt.enc")
        self.assertEqual( expected, result )

    def testDeleteFile_IgnoreErrors(self):

        full_test_file_path = path_utils.concat_path(self.test_dir, "test_file")

        with open(full_test_file_path, "w+") as f:
            f.write("rubbish\n")

        path_utils.deletefile_ignoreerrors(full_test_file_path)

        self.assertFalse(os.path.exists(full_test_file_path))

    def testBackpedal_Path(self):
        self.assertEqual("/", path_utils.backpedal_path("/tmp"))
        self.assertEqual("/tmp", path_utils.backpedal_path("/tmp/folder"))
        self.assertEqual(None, path_utils.backpedal_path("/"))
        self.assertEqual(None, None)
        self.assertEqual("/tmp/folder", path_utils.backpedal_path("/tmp/folder/next"))

    def testArrayToPath(self):
        expected = "/home/user/nuke/"
        result = path_utils.arraytopath(["home", "user", "nuke"])
        self.assertEqual(expected, result)

    def testExplodePath(self):
        expected = "home user"
        result = path_utils.explodepath("/home/user")
        self.assertEqual(expected, result)

    def testScratchFolder1(self):

        test_folder_full = path_utils.concat_path(self.test_dir, "scratch")

        # safety first
        if os.path.exists(test_folder_full):
            self.fail("[%s] already exists." % test_folder_full)

        result = path_utils.scratchfolder(test_folder_full)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(test_folder_full))
        shutil.rmtree(test_folder_full)

    def testScratchFolder2(self):

        test_folder_full = path_utils.concat_path(self.test_dir, "scratch")

        # safety first
        if os.path.exists(test_folder_full):
            self.fail("[%s] already exists." % test_folder_full)

        os.mkdir(test_folder_full) # variation: will scratch a pre-existing folder
        result = path_utils.scratchfolder(test_folder_full)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(test_folder_full))
        shutil.rmtree(test_folder_full)

    def testGuaranteeFolder(self):

        test_folder_first = path_utils.concat_path(self.test_dir, "first")
        test_folder_second = path_utils.concat_path(test_folder_first, "second")

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

    def testFilterRemoveTrailingSep(self):
        path1 = "/path/folder"
        path2 = "/path/folder/"
        path3 = "/path/folder\\"
        self.assertEqual( path_utils.filter_remove_trailing_sep(path1), path1 )
        self.assertEqual( path_utils.filter_remove_trailing_sep(path2), path1 )
        self.assertEqual( path_utils.filter_remove_trailing_sep(path3), path1 )

    def testJoinpathAbsolute(self):
        self.assertEqual(path_utils.filter_join_abs(None), None)
        self.assertEqual(path_utils.filter_join_abs("/home/user"), "home/user")
        self.assertEqual(path_utils.filter_join_abs("home/user"), "home/user")
        self.assertEqual(path_utils.filter_join_abs(""), "")

    def testConcatPath(self):
        self.assertEqual(path_utils.concat_path(None), None)
        self.assertEqual(path_utils.concat_path(None, None), None)
        self.assertEqual(path_utils.concat_path("/home"), "/home")
        self.assertEqual(path_utils.concat_path("/home/user", "home/user"), "/home/user/home/user")
        self.assertEqual(path_utils.concat_path("/home/user", "home"), "/home/user/home")
        self.assertEqual(path_utils.concat_path("/home/", "/home"), "/home/home")
        self.assertEqual(path_utils.concat_path("/", "home"), "/home")
        self.assertEqual(path_utils.concat_path("/", "home", "user", "more", "stuff"), "/home/user/more/stuff")
        self.assertEqual(path_utils.concat_path("/", "home", "user", "more", "stuff", "/home/user/more/stuff"), "/home/user/more/stuff/home/user/more/stuff")

    def testBasenameFiltered(self):
        self.assertEqual(path_utils.basename_filtered("/home"), "home")
        self.assertEqual(path_utils.basename_filtered("/home/"), "home")
        self.assertEqual(path_utils.basename_filtered("/home/user"), "user")
        self.assertEqual(path_utils.basename_filtered("/home/user/"), "user")

    def testDirnameFiltered(self):
        self.assertEqual(path_utils.dirname_filtered("/home/user"), "/home")
        self.assertEqual(path_utils.dirname_filtered("/home/user/"), "/home")
        self.assertEqual(path_utils.dirname_filtered("/"), "")

    def testSplitPath(self):
        self.assertEqual(path_utils.splitpath(os.sep), [])
        self.assertEqual(path_utils.splitpath("/"), [])
        self.assertEqual(path_utils.splitpath("/tmp"), ["tmp"])
        self.assertEqual(path_utils.splitpath( "%sfirst%ssecond" % (os.sep, os.sep) ), ["first", "second"])
        self.assertEqual(path_utils.splitpath( "%sfirst%ssecond%s" % (os.sep, os.sep, os.sep) ), ["first", "second"])

    def testGetExtension(self):
        self.assertEqual(path_utils.getextension(None), None)
        self.assertEqual(path_utils.getextension("file.txt"), "txt")
        self.assertEqual(path_utils.getextension("file.png"), "png")
        self.assertEqual(path_utils.getextension(""), "")
        self.assertEqual(path_utils.getextension("..."), "")
        self.assertEqual(path_utils.getextension("package.tar.gz"), "gz")
        self.assertEqual(path_utils.getextension("name"), "")
        self.assertEqual(path_utils.getextension("/usr/local/file"), "")
        self.assertEqual(path_utils.getextension("/usr/local/file.dat"), "dat")
        self.assertEqual(path_utils.getextension("/usr/local/file.dat.bin"), "bin")

    def testCheckIfPathsExistStopFirst(self):
        v, r = path_utils.check_if_paths_exist_stop_first([self.folder1, self.folder2])
        self.assertFalse(v)
        v, r = path_utils.check_if_paths_exist_stop_first([self.folder2])
        self.assertFalse(v)
        v, r = path_utils.check_if_paths_exist_stop_first([self.nonexistent])
        self.assertTrue(v)
        v, r = path_utils.check_if_paths_exist_stop_first([self.nonexistent, self.folder1, self.folder2])
        self.assertFalse(v)

    def testCheckIfPathsNotExistStopFirst(self):
        v, r = path_utils.check_if_paths_not_exist_stop_first([self.folder1, self.folder2])
        self.assertTrue(v)
        v, r = path_utils.check_if_paths_not_exist_stop_first([self.folder2])
        self.assertTrue(v)
        v, r = path_utils.check_if_paths_not_exist_stop_first([self.nonexistent])
        self.assertFalse(v)
        v, r = path_utils.check_if_paths_not_exist_stop_first([self.nonexistent, self.folder1, self.folder2])
        self.assertFalse(v)

    def testFindMiddlePathParts(self):
        self.assertEqual(path_utils.find_middle_path_parts(None, None), None)
        self.assertEqual(path_utils.find_middle_path_parts("/valid/path", None), None)
        self.assertEqual(path_utils.find_middle_path_parts(None, "/second/path"), None)
        self.assertEqual(path_utils.find_middle_path_parts("/valid/path", "/second/path"), None)
        self.assertEqual(path_utils.find_middle_path_parts("/valid/path", "/second/path/more"), None)
        self.assertEqual(path_utils.find_middle_path_parts("/home/user", "/home/user"), None)
        self.assertEqual(path_utils.find_middle_path_parts("/home/user", "/home/user/folder"), "")
        self.assertEqual(path_utils.find_middle_path_parts("/home/user", "/home/user/folder/path"), "folder")
        self.assertEqual(path_utils.find_middle_path_parts("/home/user", "/home/user/folder/another/path"), "folder%sanother" % os.sep)

if __name__ == '__main__':
    unittest.main()
