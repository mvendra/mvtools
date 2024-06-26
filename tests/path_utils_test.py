#!/usr/bin/env python3

import os
import shutil
import unittest
from unittest import mock
from unittest.mock import patch

import mvtools_test_fixture
import create_and_write_file
import path_utils
import get_platform

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

        self.folder1 = path_utils.concat_path(self.test_dir, "folder1")
        os.mkdir(self.folder1)
        self.folder2 = path_utils.concat_path(self.test_dir, "folder2")
        os.mkdir(self.folder2)
        self.nonexistent = path_utils.concat_path(self.test_dir, "nonexistent")

        self.test_file = path_utils.concat_path(self.test_dir, "test_file.txt")
        create_and_write_file.create_file_contents(self.test_file, "test-file")

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testReplaceExtension(self):

        self.assertEqual(path_utils.replace_extension(None, ".nfo", ".dat"), None)
        self.assertEqual(path_utils.replace_extension("", ".nfo", ".dat"), None)
        self.assertEqual(path_utils.replace_extension("file.txt", ".nfo", ".dat"), None)
        self.assertEqual(path_utils.replace_extension("file.txt.more", ".txt", ".dat"), None)
        self.assertEqual(path_utils.replace_extension("file.txt", ".txt", ".dat"), "file.dat")
        self.assertEqual(path_utils.replace_extension("file.txt.more", ".more", ".dat"), "file.txt.dat")

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

    def testDeleteFolder_IgnoreErrors1(self):

        self.assertTrue(os.path.exists(self.folder1))

        raised_except = False
        try:
            path_utils.deletefolder_ignoreerrors(self.folder1)
        except:
            raised_except = True
        self.assertFalse(raised_except)

    def testDeleteFolder_IgnoreErrors2(self):

        self.assertFalse(os.path.exists(self.nonexistent))

        raised_except = False
        try:
            path_utils.deletefolder_ignoreerrors(self.nonexistent)
        except:
            raised_except = True
        self.assertFalse(raised_except)

    def testBackpedal_Path(self):
        self.assertEqual("/", path_utils.backpedal_path("/tmp"))
        self.assertEqual("/tmp", path_utils.backpedal_path("/tmp/folder"))
        self.assertEqual(None, path_utils.backpedal_path("/"))
        self.assertEqual(None, None)
        self.assertEqual("/tmp/folder", path_utils.backpedal_path("/tmp/folder/next"))

    def testArrayToPath(self):
        self.assertEqual(path_utils.arraytopath([]), "")
        self.assertEqual(path_utils.arraytopath(["home"]), "home")
        self.assertEqual(path_utils.arraytopath(["home", "user", "nuke"]), "home/user/nuke")

    def testExplodePath(self):
        result = path_utils.explodepath("/home/user")
        self.assertEqual(result, "/ home user")

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

    def testGuaranteeFolderFail(self):
        self.assertFalse(path_utils.guaranteefolder(None))
        self.assertFalse(path_utils.guaranteefolder(""))
        self.assertFalse(path_utils.guaranteefolder(self.test_file))
        test_file_link = path_utils.concat_path(self.test_dir, "test_file_link.txt")
        self.assertFalse(os.path.exists(test_file_link))
        self.assertFalse(path_utils.is_path_broken_symlink(test_file_link))
        os.symlink(self.test_file, test_file_link)
        os.unlink(self.test_file)
        self.assertTrue(path_utils.is_path_broken_symlink(test_file_link))
        self.assertFalse(path_utils.guaranteefolder(test_file_link))

    def testGuaranteeFolderFailFileInTheMiddle(self):

        test_folder_first = path_utils.concat_path(self.test_dir, "first")
        test_folder_second = path_utils.concat_path(test_folder_first, "second")
        test_folder_third = path_utils.concat_path(test_folder_second, "third")
        test_folder_fourth = path_utils.concat_path(test_folder_third, "fourth")

        self.assertFalse(os.path.exists(test_folder_first))
        self.assertFalse(os.path.exists(test_folder_second))
        self.assertFalse(os.path.exists(test_folder_third))
        self.assertFalse(os.path.exists(test_folder_fourth))

        os.mkdir(test_folder_first)
        self.assertTrue(create_and_write_file.create_file_contents(test_folder_second, "fake second folder"))
        self.assertFalse(path_utils.guaranteefolder(test_folder_fourth))

        self.assertTrue(os.path.isdir(test_folder_first))
        self.assertTrue(os.path.exists(test_folder_second))
        self.assertFalse(os.path.exists(test_folder_third))
        self.assertFalse(os.path.exists(test_folder_fourth))

    def testGuaranteeFolderFailBrokenFolderSymlinkInTheMiddle(self):

        test_folder_first = path_utils.concat_path(self.test_dir, "first")
        test_folder_second = path_utils.concat_path(self.test_dir, "second")
        test_folder_third = path_utils.concat_path(test_folder_second, "third")
        test_folder_fourth = path_utils.concat_path(test_folder_third, "fourth")

        os.mkdir(test_folder_first)
        os.symlink(test_folder_first, test_folder_second)
        shutil.rmtree(test_folder_first)

        self.assertFalse(os.path.exists(test_folder_first))
        self.assertTrue(path_utils.is_path_broken_symlink(test_folder_second))
        self.assertFalse(os.path.exists(test_folder_third))
        self.assertFalse(os.path.exists(test_folder_fourth))

        self.assertFalse(path_utils.guaranteefolder(test_folder_fourth))

        self.assertFalse(os.path.exists(test_folder_first))
        self.assertTrue(path_utils.is_path_broken_symlink(test_folder_second))
        self.assertFalse(os.path.exists(test_folder_third))
        self.assertFalse(os.path.exists(test_folder_fourth))

    def testGuaranteeFolderVanilla(self):
        test_folder_first = path_utils.concat_path(self.test_dir, "first")
        self.assertFalse(os.path.exists(test_folder_first))
        self.assertTrue(path_utils.guaranteefolder(test_folder_first))
        self.assertTrue(os.path.isdir(test_folder_first))

    def testGuaranteeFolderExtended1(self):

        test_folder_first = path_utils.concat_path(self.test_dir, "first")
        test_folder_second = path_utils.concat_path(test_folder_first, "second")
        test_folder_third = path_utils.concat_path(test_folder_second, "third")
        test_folder_fourth = path_utils.concat_path(test_folder_third, "fourth")

        self.assertFalse(os.path.exists(test_folder_first))
        self.assertFalse(os.path.exists(test_folder_second))
        self.assertFalse(os.path.exists(test_folder_third))
        self.assertFalse(os.path.exists(test_folder_fourth))

        self.assertTrue(path_utils.guaranteefolder(test_folder_fourth))

        self.assertTrue(os.path.isdir(test_folder_first))
        self.assertTrue(os.path.isdir(test_folder_second))
        self.assertTrue(os.path.isdir(test_folder_third))
        self.assertTrue(os.path.isdir(test_folder_fourth))

    def testGuaranteeFolderExtended2(self):

        test_folder_first = path_utils.concat_path(self.test_dir, "first")
        test_folder_second = path_utils.concat_path(test_folder_first, "second")
        test_folder_third = path_utils.concat_path(test_folder_second, "third")
        test_folder_fourth = path_utils.concat_path(test_folder_third, "fourth")

        os.mkdir(test_folder_first)
        os.mkdir(test_folder_second)

        self.assertTrue(os.path.isdir(test_folder_first))
        self.assertTrue(os.path.isdir(test_folder_second))
        self.assertFalse(os.path.exists(test_folder_third))
        self.assertFalse(os.path.exists(test_folder_fourth))

        self.assertTrue(path_utils.guaranteefolder(test_folder_fourth))

        self.assertTrue(os.path.isdir(test_folder_first))
        self.assertTrue(os.path.isdir(test_folder_second))
        self.assertTrue(os.path.isdir(test_folder_third))
        self.assertTrue(os.path.isdir(test_folder_fourth))

    def testGuaranteeFolderExtended3(self):

        test_folder_first = path_utils.concat_path(self.test_dir, "first")
        test_folder_second = path_utils.concat_path(test_folder_first, "second")
        test_folder_third = path_utils.concat_path(test_folder_second, "third")
        test_folder_third_abs = path_utils.concat_path(test_folder_first, "third")
        test_folder_fourth = path_utils.concat_path(test_folder_third, "fourth")
        test_folder_fourth_abs = path_utils.concat_path(test_folder_third_abs, "fourth")

        os.mkdir(test_folder_first)
        os.symlink(test_folder_first, test_folder_second)

        self.assertTrue(os.path.isdir(test_folder_first))
        self.assertTrue(os.path.exists(test_folder_second))
        self.assertFalse(os.path.exists(test_folder_third))
        self.assertFalse(os.path.exists(test_folder_third_abs))
        self.assertFalse(os.path.exists(test_folder_fourth))
        self.assertFalse(os.path.exists(test_folder_fourth_abs))

        self.assertTrue(path_utils.guaranteefolder(test_folder_fourth))

        self.assertTrue(os.path.isdir(test_folder_first))
        self.assertTrue(os.path.isdir(test_folder_second))
        self.assertTrue(os.path.isdir(test_folder_third))
        self.assertTrue(os.path.isdir(test_folder_third_abs))
        self.assertTrue(os.path.isdir(test_folder_fourth))
        self.assertTrue(os.path.isdir(test_folder_fourth_abs))

    def testRecreateAsFolderIfNeeded1(self):

        target_path = path_utils.concat_path(self.test_dir, "file_target.txt")
        self.assertTrue(create_and_write_file.create_file_contents(target_path, "test-file"))
        self.assertTrue(os.path.exists(target_path))
        self.assertFalse(os.path.isdir(target_path))

        self.assertTrue(path_utils.recreate_as_folder_if_needed(target_path))
        self.assertTrue(os.path.exists(target_path))
        self.assertTrue(os.path.isdir(target_path))

    def testRecreateAsFolderIfNeeded2(self):

        target_path = path_utils.concat_path(self.test_dir, "folder_target")
        os.mkdir(target_path)
        self.assertTrue(os.path.exists(target_path))
        self.assertTrue(os.path.isdir(target_path))

        target_path_sub = path_utils.concat_path(target_path, "sub")
        self.assertTrue(create_and_write_file.create_file_contents(target_path_sub, "test-subfile"))

        self.assertTrue(os.path.exists(target_path_sub))
        self.assertTrue(path_utils.recreate_as_folder_if_needed(target_path))
        self.assertTrue(os.path.exists(target_path))
        self.assertTrue(os.path.isdir(target_path))
        self.assertFalse(os.path.exists(target_path_sub))

    def testRecreateAsFolderIfNeeded3(self):

        target_path = path_utils.concat_path(self.test_dir, "folder_target")
        target_path_sub = path_utils.concat_path(target_path, "subfolder")
        self.assertFalse(os.path.exists(target_path))
        self.assertFalse(os.path.exists(target_path_sub))

        self.assertTrue(path_utils.recreate_as_folder_if_needed(target_path_sub))
        self.assertTrue(os.path.exists(target_path))
        self.assertTrue(os.path.isdir(target_path))
        self.assertTrue(os.path.exists(target_path_sub))
        self.assertTrue(os.path.isdir(target_path_sub))

    def testRecreateAsFolderIfNeeded4(self):

        target_path = path_utils.concat_path(self.test_dir, "folder_target")
        target_path_sub = path_utils.concat_path(target_path, "subfolder")
        self.assertFalse(os.path.exists(target_path))
        self.assertFalse(os.path.exists(target_path_sub))

        self.assertTrue(create_and_write_file.create_file_contents(target_path, "test-blocking-file"))
        self.assertTrue(os.path.exists(target_path))

        self.assertFalse(path_utils.recreate_as_folder_if_needed(target_path_sub))
        self.assertTrue(os.path.exists(target_path))
        self.assertFalse(os.path.isdir(target_path))
        self.assertFalse(os.path.exists(target_path_sub))

    def testFilterPathListNoSameBranch(self):
        expected = ["/bug", "/home", "/shome"]
        result = path_utils.filter_path_list_no_same_branch(["/home", "/home/user/nuke", "/bug", "/home/ooser", "/shome", "/home/bork/nuke/bark"])
        self.assertEqual( expected, result )

    def testFilterRemoveTrailingSep(self):

        self.assertEqual( path_utils.filter_remove_trailing_sep("/path/folder", "no"), "/path/folder" )
        self.assertEqual( path_utils.filter_remove_trailing_sep("/path/folder/", "no"), "/path/folder" )
        self.assertEqual( path_utils.filter_remove_trailing_sep("/path/folder\\", "no"), "/path/folder\\" )
        self.assertEqual( path_utils.filter_remove_trailing_sep("/", "no"), "/" )

        self.assertEqual( path_utils.filter_remove_trailing_sep("/path/folder", "yes"), "/path/folder" )
        self.assertEqual( path_utils.filter_remove_trailing_sep("/path/folder/", "yes"), "/path/folder" )
        self.assertEqual( path_utils.filter_remove_trailing_sep("/path/folder\\", "yes"), "/path/folder" )
        self.assertEqual( path_utils.filter_remove_trailing_sep("/", "yes"), "" )

        with mock.patch("get_platform.getplat", return_value=get_platform.PLAT_LINUX):
            self.assertEqual( path_utils.filter_remove_trailing_sep("/path/folder", "auto"), "/path/folder" )
            self.assertEqual( path_utils.filter_remove_trailing_sep("/path/folder/", "auto"), "/path/folder" )
            self.assertEqual( path_utils.filter_remove_trailing_sep("/path/folder\\", "auto"), "/path/folder\\" )
            self.assertEqual( path_utils.filter_remove_trailing_sep("/", "auto"), "/" )

        with mock.patch("get_platform.getplat", return_value=get_platform.PLAT_WINDOWS):
            self.assertEqual( path_utils.filter_remove_trailing_sep("/path/folder", "auto"), "/path/folder" )
            self.assertEqual( path_utils.filter_remove_trailing_sep("/path/folder/", "auto"), "/path/folder" )
            self.assertEqual( path_utils.filter_remove_trailing_sep("/path/folder\\", "auto"), "/path/folder" )
            self.assertEqual( path_utils.filter_remove_trailing_sep("/", "auto"), "" )

    def testFilterJoinAbsFirstRight(self):
        self.assertEqual(path_utils.filter_join_abs_first_right(None), None)
        self.assertEqual(path_utils.filter_join_abs_first_right(""), "")
        self.assertEqual(path_utils.filter_join_abs_first_right("/"), "/")
        self.assertEqual(path_utils.filter_join_abs_first_right("/home"), "/home")
        self.assertEqual(path_utils.filter_join_abs_first_right("/home/"), "/home")
        self.assertEqual(path_utils.filter_join_abs_first_right("home/"), "home")

    def testConcatPath(self):
        self.assertEqual(path_utils.concat_path(), None)
        self.assertEqual(path_utils.concat_path(None), None)
        self.assertEqual(path_utils.concat_path(None, None), None)
        self.assertEqual(path_utils.concat_path("/home"), "/home")
        self.assertEqual(path_utils.concat_path("/home/user", "home/user"), "/home/user/home/user")
        self.assertEqual(path_utils.concat_path("/home/user", "home/user/"), "/home/user/home/user")
        self.assertEqual(path_utils.concat_path("/home/user", "home"), "/home/user/home")
        self.assertEqual(path_utils.concat_path("/home/", "/home"), "/home/home")
        self.assertEqual(path_utils.concat_path("/", None), None)
        self.assertEqual(path_utils.concat_path(None, "/home"), None)
        self.assertEqual(path_utils.concat_path("/", ""), "/")
        self.assertEqual(path_utils.concat_path("/", "/"), "/")
        self.assertEqual(path_utils.concat_path("/", "home", "/"), "/home")
        self.assertEqual(path_utils.concat_path("/", "home", "/sub/"), "/home/sub")
        self.assertEqual(path_utils.concat_path("/", "home"), "/home")
        self.assertEqual(path_utils.concat_path("/", "home", "user", "more", "stuff"), "/home/user/more/stuff")
        self.assertEqual(path_utils.concat_path("/", "home", "user", "more", "stuff", "/home/user/more/stuff"), "/home/user/more/stuff/home/user/more/stuff")
        self.assertEqual(path_utils.concat_path("http://home.org", "server/subervice"), "http://home.org/server/subervice")
        self.assertEqual(path_utils.concat_path("http://home.org/", "server/subervice"), "http://home.org/server/subervice")
        self.assertEqual(path_utils.concat_path("http://home.org", "/server/subervice"), "http://home.org/server/subervice")
        self.assertEqual(path_utils.concat_path("http://home.org/", "/server/subervice"), "http://home.org/server/subervice")
        self.assertEqual(path_utils.concat_path("http://home.org/", "/", "/server/subervice/"), "http://home.org/server/subervice")

    def testGetPathRoot(self):
        self.assertEqual(path_utils.getpathroot(""), None)
        self.assertEqual(path_utils.getpathroot(None), None)
        self.assertEqual(path_utils.getpathroot("/"), "/")
        self.assertEqual(path_utils.getpathroot("/cygdrive/c/mp1"), "/")
        self.assertEqual(path_utils.getpathroot("/root/home"), "/")
        self.assertEqual(path_utils.getpathroot("C:/folder/home"), "C:")

        with mock.patch("get_platform.getplat", return_value=get_platform.PLAT_LINUX):
            self.assertEqual(path_utils.getpathroot("C:\\folder/home"), "C:\\folder")

        with mock.patch("get_platform.getplat", return_value=get_platform.PLAT_WINDOWS):
            self.assertEqual(path_utils.getpathroot("C:\\folder/home"), "C:")

    def testSplitPath(self):

        self.assertEqual(path_utils.splitpath(None, "no"), None)
        self.assertEqual(path_utils.splitpath("", "no"), None)
        self.assertEqual(path_utils.splitpath(None, "yes"), None)
        self.assertEqual(path_utils.splitpath("", "yes"), None)
        self.assertEqual(path_utils.splitpath("/", "no"), ["/"])
        self.assertEqual(path_utils.splitpath("/", "yes"), None)

        self.assertEqual(path_utils.splitpath("/tmp", "no"), ["/", "tmp"])
        self.assertEqual(path_utils.splitpath("C:\\tmp", "no"), ["C:\\tmp"])
        self.assertEqual(path_utils.splitpath("/tmp\\first/second", "no"), ["/", "tmp\\first", "second"])
        self.assertEqual(path_utils.splitpath("tmp/subfolder", "no"), ["tmp", "subfolder"])
        self.assertEqual(path_utils.splitpath("tmp/subfolder/", "no"), ["tmp", "subfolder"])
        self.assertEqual(path_utils.splitpath("tmp\\subfolder", "no"), ["tmp\\subfolder"])
        self.assertEqual(path_utils.splitpath("C:\\tmp", "yes"), ["C:", "tmp"])
        self.assertEqual(path_utils.splitpath("C:\\tmp\\first\\second\\yetmore", "yes"), ["C:", "tmp", "first", "second", "yetmore"])
        self.assertEqual(path_utils.splitpath("/tmp", "yes"), ["tmp"])
        self.assertEqual(path_utils.splitpath("tmp\\subfolder", "yes"), ["tmp", "subfolder"])
        self.assertEqual(path_utils.splitpath("/tmp", "yes"), ["tmp"])
        self.assertEqual(path_utils.splitpath("\\", "yes"), None)
        self.assertEqual(path_utils.splitpath("F:", "yes"), ["F:"])

        with mock.patch("get_platform.getplat", return_value=get_platform.PLAT_LINUX):
            self.assertEqual(path_utils.splitpath("/tmp", "auto"), ["/", "tmp"])
            self.assertEqual(path_utils.splitpath("/home\\user/more/sub1\\sub2/yetmore/file.txt", "auto"), ["/", "home\\user", "more", "sub1\\sub2", "yetmore", "file.txt"])
            self.assertEqual(path_utils.splitpath("/tmp/", "auto"), ["/", "tmp"])
            self.assertEqual(path_utils.splitpath( "/first/second", "auto" ), ["/", "first", "second"])
            self.assertEqual(path_utils.splitpath( "/first/second/", "auto" ), ["/", "first", "second"])
            self.assertEqual(path_utils.splitpath("F:", "auto"), ["F:"])

        with mock.patch("get_platform.getplat", return_value=get_platform.PLAT_WINDOWS):
            self.assertEqual(path_utils.splitpath("/", "auto"), None)
            self.assertEqual(path_utils.splitpath("/tmp", "auto"), ["tmp"])
            self.assertEqual(path_utils.splitpath("/tmp/", "auto"), ["tmp"])
            self.assertEqual(path_utils.splitpath("/home\\user/more/sub1\\sub2/yetmore/file.txt", "auto"), ["home", "user", "more", "sub1", "sub2", "yetmore", "file.txt"])
            self.assertEqual(path_utils.splitpath("tmp", "auto"), ["tmp"])
            self.assertEqual(path_utils.splitpath("tmp\\sub\\folder\\another", "auto"), ["tmp", "sub", "folder", "another"])
            self.assertEqual(path_utils.splitpath("tmp\\sub\\folder\\another\\", "auto"), ["tmp", "sub", "folder", "another"])
            self.assertEqual(path_utils.splitpath( "/first/second", "auto" ), ["first", "second"])
            self.assertEqual(path_utils.splitpath( "/first/second/", "auto" ), ["first", "second"])
            self.assertEqual(path_utils.splitpath("F:", "auto"), ["F:"])

    def testBasenameFiltered(self):
        self.assertEqual(path_utils.basename_filtered(None, "no"), None)
        self.assertEqual(path_utils.basename_filtered("", "no"), None)
        self.assertEqual(path_utils.basename_filtered("/", "no"), "/")
        self.assertEqual(path_utils.basename_filtered("/home", "no"), "home")
        self.assertEqual(path_utils.basename_filtered("/home/", "no"), "home")
        self.assertEqual(path_utils.basename_filtered("home/", "no"), "home")
        self.assertEqual(path_utils.basename_filtered("/home/user", "no"), "user")
        self.assertEqual(path_utils.basename_filtered("home/user", "no"), "user")
        self.assertEqual(path_utils.basename_filtered("/home/user/", "no"), "user")
        self.assertEqual(path_utils.basename_filtered("/home/user/more", "no"), "more")
        self.assertEqual(path_utils.basename_filtered("/home/user/more/", "no"), "more")
        self.assertEqual(path_utils.basename_filtered("/home/user/more/sub1/sub2", "no"), "sub2")
        self.assertEqual(path_utils.basename_filtered("/home/user/more\\sub1/sub2", "no"), "sub2")
        self.assertEqual(path_utils.basename_filtered("home/user/more\\sub1/sub2", "no"), "sub2")
        self.assertEqual(path_utils.basename_filtered(None, "yes"), None)
        self.assertEqual(path_utils.basename_filtered("", "yes"), None)
        self.assertEqual(path_utils.basename_filtered("/", "yes"), None)
        self.assertEqual(path_utils.basename_filtered("/home", "yes"), "home")
        self.assertEqual(path_utils.basename_filtered("/home/", "yes"), "home")
        self.assertEqual(path_utils.basename_filtered("/home/user", "yes"), "user")
        self.assertEqual(path_utils.basename_filtered("home/user", "yes"), "user")
        self.assertEqual(path_utils.basename_filtered("/home/user/", "yes"), "user")
        self.assertEqual(path_utils.basename_filtered("home/user/", "yes"), "user")
        self.assertEqual(path_utils.basename_filtered("/home/user/more", "yes"), "more")
        self.assertEqual(path_utils.basename_filtered("/home/user/more/sub1/sub2", "yes"), "sub2")
        self.assertEqual(path_utils.basename_filtered("/home/user/more/sub1/sub2/", "yes"), "sub2")
        self.assertEqual(path_utils.basename_filtered("/home/user/more\\sub1/sub2", "yes"), "sub2")
        self.assertEqual(path_utils.basename_filtered("/home/user/more\\sub1/sub2", "yes"), "sub2")

        with mock.patch("get_platform.getplat", return_value=get_platform.PLAT_LINUX):
            self.assertEqual(path_utils.basename_filtered("/home/user/more\\sub1\\sub2", "auto"), "more\\sub1\\sub2")
            self.assertEqual(path_utils.basename_filtered("/home\\user/more\\sub1\\sub2", "auto"), "more\\sub1\\sub2")
            self.assertEqual(path_utils.basename_filtered("/home\\", "auto"), "home\\")
            self.assertEqual(path_utils.basename_filtered("/home\\more/", "auto"), "home\\more")

        with mock.patch("get_platform.getplat", return_value=get_platform.PLAT_WINDOWS):
            self.assertEqual(path_utils.basename_filtered("/home/user/more\\sub1\\sub2", "auto"), "sub2")
            self.assertEqual(path_utils.basename_filtered("/home\\user/more\\sub1\\sub2", "auto"), "sub2")
            self.assertEqual(path_utils.basename_filtered("/home\\more\\", "auto"), "more")

    def testDirnameFiltered(self):
        self.assertEqual(path_utils.dirname_filtered(None, "no"), None)
        self.assertEqual(path_utils.dirname_filtered("", "no"), None)
        self.assertEqual(path_utils.dirname_filtered("/", "no"), "/")
        self.assertEqual(path_utils.dirname_filtered("/home", "no"), "/")
        self.assertEqual(path_utils.dirname_filtered("home", "no"), None)
        self.assertEqual(path_utils.dirname_filtered("home/", "no"), None)
        self.assertEqual(path_utils.dirname_filtered("\\", "no"), None)
        self.assertEqual(path_utils.dirname_filtered("/home/user/", "no"), "/home")
        self.assertEqual(path_utils.dirname_filtered("/home/user", "no"), "/home")
        self.assertEqual(path_utils.dirname_filtered("/home/user/more/sub1/sub2/yetmore", "no"), "/home/user/more/sub1/sub2")
        self.assertEqual(path_utils.dirname_filtered("/home/user/more/sub1/sub2/yetmore/", "no"), "/home/user/more/sub1/sub2")
        self.assertEqual(path_utils.dirname_filtered("/home/user/more/sub1/sub2/yetmore/file.txt", "no"), "/home/user/more/sub1/sub2/yetmore")
        self.assertEqual(path_utils.dirname_filtered("home/user/more/sub1/sub2/yetmore/file.txt", "no"), "home/user/more/sub1/sub2/yetmore")
        self.assertEqual(path_utils.dirname_filtered("another/second.c", "no"), "another")
        self.assertEqual(path_utils.dirname_filtered("another/second.c/", "no"), "another")
        self.assertEqual(path_utils.dirname_filtered("/another/sub/folder/again", "no"), "/another/sub/folder")
        self.assertEqual(path_utils.dirname_filtered("/another/sub/folder/again/", "no"), "/another/sub/folder")
        self.assertEqual(path_utils.dirname_filtered("another/sub/folder/again", "no"), "another/sub/folder")
        self.assertEqual(path_utils.dirname_filtered("another/sub/folder/again/", "no"), "another/sub/folder")

        self.assertEqual(path_utils.dirname_filtered(None, "yes"), None)
        self.assertEqual(path_utils.dirname_filtered("", "yes"), None)
        self.assertEqual(path_utils.dirname_filtered("/", "yes"), None)
        self.assertEqual(path_utils.dirname_filtered("/home", "yes"), None)
        self.assertEqual(path_utils.dirname_filtered("home", "yes"), None)
        self.assertEqual(path_utils.dirname_filtered("home/", "yes"), None)
        self.assertEqual(path_utils.dirname_filtered("\\", "yes"), None)
        self.assertEqual(path_utils.dirname_filtered("/home/user/", "yes"), "/home")
        self.assertEqual(path_utils.dirname_filtered("/home/user", "yes"), "/home")
        self.assertEqual(path_utils.dirname_filtered("/home/user/more/sub1/sub2/yetmore", "yes"), "/home/user/more/sub1/sub2")
        self.assertEqual(path_utils.dirname_filtered("/home/user/more/sub1/sub2/yetmore/", "yes"), "/home/user/more/sub1/sub2")
        self.assertEqual(path_utils.dirname_filtered("/home/user/more/sub1/sub2/yetmore/file.txt", "yes"), "/home/user/more/sub1/sub2/yetmore")
        self.assertEqual(path_utils.dirname_filtered("home/user/more/sub1/sub2/yetmore/file.txt", "yes"), "home/user/more/sub1/sub2/yetmore")
        self.assertEqual(path_utils.dirname_filtered("another/second.c", "yes"), "another")
        self.assertEqual(path_utils.dirname_filtered("another/second.c/", "yes"), "another")
        self.assertEqual(path_utils.dirname_filtered("/another/sub/folder/again", "yes"), "/another/sub/folder")
        self.assertEqual(path_utils.dirname_filtered("/another/sub/folder/again/", "yes"), "/another/sub/folder")
        self.assertEqual(path_utils.dirname_filtered("another/sub/folder/again", "yes"), "another/sub/folder")
        self.assertEqual(path_utils.dirname_filtered("another/sub/folder/again/", "yes"), "another/sub/folder")

        with mock.patch("get_platform.getplat", return_value=get_platform.PLAT_LINUX):
            self.assertEqual(path_utils.dirname_filtered("/home\\user/more/sub1\\sub2/yetmore/file.txt", "auto"), "/home\\user/more/sub1\\sub2/yetmore")
            self.assertEqual(path_utils.dirname_filtered("/home\\user/more/sub1\\sub2/yetmore/file.txt/", "auto"), "/home\\user/more/sub1\\sub2/yetmore")
            self.assertEqual(path_utils.dirname_filtered("home\\user/more/sub1\\sub2/yetmore/file.txt/", "auto"), "home\\user/more/sub1\\sub2/yetmore")

        with mock.patch("get_platform.getplat", return_value=get_platform.PLAT_WINDOWS):
            self.assertEqual(path_utils.dirname_filtered("/home\\user/more/sub1\\sub2/yetmore/file.txt", "auto"), "/home/user/more/sub1/sub2/yetmore")
            self.assertEqual(path_utils.dirname_filtered("/home\\user/more/sub1\\sub2/yetmore/file.txt\\", "auto"), "/home/user/more/sub1/sub2/yetmore")
            self.assertEqual(path_utils.dirname_filtered("home\\user/more/sub1\\sub2/yetmore/file.txt\\", "auto"), "home/user/more/sub1/sub2/yetmore")

    def testCopyToFail1(self):

        folder1_nonexistent = path_utils.concat_path(self.folder1, "nonexistent.txt")
        folder2_nonexistent = path_utils.concat_path(self.folder2, "nonexistent.txt")

        self.assertFalse(path_utils.copy_to(folder1_nonexistent, self.folder2))
        self.assertFalse(os.path.exists(folder1_nonexistent))
        self.assertFalse(os.path.exists(folder2_nonexistent))

    def testCopyToFail2(self):

        folder1_file1 = path_utils.concat_path(self.folder1, "file1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(folder1_file1, "folder1, file1 contents"))
        self.assertTrue(os.path.exists(folder1_file1))

        self.assertFalse(path_utils.copy_to(folder1_file1, self.nonexistent))
        self.assertFalse(os.path.exists(self.nonexistent))

    def testCopyToFail3(self):

        folder1_file1 = path_utils.concat_path(self.folder1, "file1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(folder1_file1, "folder1, file1 contents"))
        self.assertTrue(os.path.exists(folder1_file1))

        folder1_file2 = path_utils.concat_path(self.folder1, "file2.txt")
        self.assertTrue(create_and_write_file.create_file_contents(folder1_file2, "folder1, file2 contents"))
        self.assertTrue(os.path.exists(folder1_file2))

        self.assertFalse(path_utils.copy_to(folder1_file1, folder1_file2))

    def testCopyToFail4(self):

        folder1_file1 = path_utils.concat_path(self.folder1, "file1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(folder1_file1, "folder1, file1 contents"))

        folder2_file1 = path_utils.concat_path(self.folder2, "file1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(folder2_file1, "folder2, file1 contents"))

        self.assertFalse(path_utils.copy_to(folder1_file1, self.folder2))
        folder2_file1 = path_utils.concat_path(self.folder2, "file1.txt")
        self.assertTrue(os.path.exists(folder2_file1))

    def testCopyToFail5(self):

        folder1_sub = path_utils.concat_path(self.folder1, "sub")
        os.mkdir(folder1_sub)
        self.assertTrue(os.path.exists(folder1_sub))

        self.assertFalse(path_utils.copy_to(folder1_sub, self.nonexistent))

    def testCopyToFail6(self):

        folder1_sub = path_utils.concat_path(self.folder1, "sub")
        os.mkdir(folder1_sub)
        self.assertTrue(os.path.exists(folder1_sub))

        folder2_file1 = path_utils.concat_path(self.folder2, "file1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(folder2_file1, "folder2, file1 contents"))
        self.assertTrue(os.path.exists(folder2_file1))

        self.assertFalse(path_utils.copy_to(folder1_sub, folder2_file1))

    def testCopyToFail7(self):

        folder1_sub = path_utils.concat_path(self.folder1, "sub")
        os.mkdir(folder1_sub)
        self.assertTrue(os.path.exists(folder1_sub))

        folder1_sub_file1 = path_utils.concat_path(folder1_sub, "file1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(folder1_sub_file1, "folder1, sub, file1 contents"))
        self.assertTrue(os.path.exists(folder1_sub_file1))

        folder2_sub = path_utils.concat_path(self.folder2, "sub")
        folder2_sub_sub = path_utils.concat_path(folder2_sub, "sub")
        os.mkdir(folder2_sub)
        self.assertTrue(os.path.exists(folder2_sub))
        self.assertFalse(os.path.exists(folder2_sub_sub))

        folder2_sub_file1 = path_utils.concat_path(folder2_sub, "file1.txt")
        self.assertFalse(os.path.exists(folder2_sub_file1))

        self.assertFalse(path_utils.copy_to(folder1_sub, self.folder2))
        self.assertTrue(os.path.exists(folder2_sub))
        self.assertFalse(os.path.exists(folder2_sub_sub))
        self.assertFalse(os.path.exists(folder2_sub_file1))

    def testCopyToFile(self):

        folder1_file1 = path_utils.concat_path(self.folder1, "file1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(folder1_file1, "file1 contents"))

        self.assertTrue(path_utils.copy_to(folder1_file1, self.folder2))
        folder2_file1 = path_utils.concat_path(self.folder2, "file1.txt")
        self.assertTrue(os.path.exists(folder2_file1))

    def testCopyToFileBlank(self):

        blank_folder = path_utils.concat_path(self.test_dir, " ")
        self.assertFalse(os.path.exists(blank_folder))
        os.mkdir(blank_folder)
        self.assertTrue(os.path.exists(blank_folder))

        blank_file = path_utils.concat_path(blank_folder, " ")
        self.assertFalse(os.path.exists(blank_file))
        self.assertTrue(create_and_write_file.create_file_contents(blank_file, "blank file contents"))
        self.assertTrue(os.path.exists(blank_file))

        folder2_blank_file = path_utils.concat_path(self.folder2, " ")
        self.assertFalse(os.path.exists(folder2_blank_file))
        self.assertTrue(path_utils.copy_to(blank_file, self.folder2))
        self.assertTrue(os.path.exists(folder2_blank_file))
        with open(folder2_blank_file, "r") as f:
            self.assertTrue("blank file contents" in f.read())

    def testCopyToFileBinary(self):

        folder1_file1 = path_utils.concat_path(self.folder1, "file1.bin")
        self.assertFalse(os.path.exists(folder1_file1))
        with open(folder1_file1, "wb") as f:
            f.write(b"\xff\xff\xff")
        self.assertTrue(os.path.exists(folder1_file1))

        self.assertTrue(path_utils.copy_to(folder1_file1, self.folder2))
        folder2_file1 = path_utils.concat_path(self.folder2, "file1.bin")
        self.assertTrue(os.path.exists(folder2_file1))

        contents = bytearray()
        with open(folder2_file1, "rb") as f:
            contents = f.read()
        self.assertEqual(contents, b"\xff\xff\xff")

    def testCopyToFolder(self):

        folder1_sub = path_utils.concat_path(self.folder1, "sub")
        os.mkdir(folder1_sub)
        self.assertTrue(os.path.exists(folder1_sub))

        folder1_sub_file1 = path_utils.concat_path(folder1_sub, "file1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(folder1_sub_file1, "file1 contents"))

        folder2_sub = path_utils.concat_path(self.folder2, "sub")
        folder2_sub_file1 = path_utils.concat_path(folder2_sub, "file1.txt")
        self.assertFalse(os.path.exists(folder2_sub))
        self.assertFalse(os.path.exists(folder2_sub_file1))

        self.assertTrue(path_utils.copy_to(folder1_sub, self.folder2))
        self.assertTrue(os.path.exists(folder2_sub))
        self.assertTrue(os.path.exists(folder2_sub_file1))

    def testCopyToFolderBlank(self):

        folder1_blank = path_utils.concat_path(self.folder1, " ")
        os.mkdir(folder1_blank)
        self.assertTrue(os.path.exists(folder1_blank))

        folder1_blank_file1 = path_utils.concat_path(folder1_blank, "file1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(folder1_blank_file1, "file1 contents"))

        folder2_blank = path_utils.concat_path(self.folder2, " ")
        folder2_blank_file1 = path_utils.concat_path(folder2_blank, "file1.txt")
        self.assertFalse(os.path.exists(folder2_blank))
        self.assertFalse(os.path.exists(folder2_blank_file1))

        self.assertTrue(path_utils.copy_to(folder1_blank, self.folder2))
        self.assertTrue(os.path.exists(folder2_blank))
        self.assertTrue(os.path.exists(folder2_blank_file1))

    def testBasedPathFindOutstandingPathFail1(self):

        v, r = path_utils.based_path_find_outstanding_path(None, None)
        self.assertFalse(v)

        v, r = path_utils.based_path_find_outstanding_path(None, "")
        self.assertFalse(v)

        v, r = path_utils.based_path_find_outstanding_path("", None)
        self.assertFalse(v)

        v, r = path_utils.based_path_find_outstanding_path("", "")
        self.assertFalse(v)

        v, r = path_utils.based_path_find_outstanding_path("/some/path", "/some/path")
        self.assertFalse(v)

        v, r = path_utils.based_path_find_outstanding_path("/some/path", "/some")
        self.assertFalse(v)

        v, r = path_utils.based_path_find_outstanding_path("/some/path/more", "/some/else/more")
        self.assertFalse(v)

        v, r = path_utils.based_path_find_outstanding_path("/some/path/more", "/some/else/more/almost")
        self.assertFalse(v)

        v, r = path_utils.based_path_find_outstanding_path("/", "some/else/more/almost/file1.txt")
        self.assertFalse(v)

    def testBasedPathFindOutstandingPath1(self):

        v, r = path_utils.based_path_find_outstanding_path("/some/path/more", "/some/path/more/stuff")
        self.assertTrue(v)
        self.assertEqual(r, "stuff")

        v, r = path_utils.based_path_find_outstanding_path("/some/path/more/yet/more", "/some/path/more/yet/more/sub/folder/file.txt")
        self.assertTrue(v)
        self.assertEqual(r, "sub/folder/file.txt")

        v, r = path_utils.based_path_find_outstanding_path("/", "/some/else/more/almost/file1.txt")
        self.assertTrue(v)
        self.assertEqual(r, "some/else/more/almost/file1.txt")

    def testBasedCopyToFail1(self):

        folder1_sub1 = path_utils.concat_path(self.folder1, "sub1")
        os.mkdir(folder1_sub1)
        folder1_sub1_file1 = path_utils.concat_path(folder1_sub1, "file1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(folder1_sub1_file1, "file1 contents"))

        folder1_sub2 = path_utils.concat_path(self.folder1, "sub2")
        os.mkdir(folder1_sub2)
        folder1_sub2_file1 = path_utils.concat_path(folder1_sub2, "file5.txt")
        self.assertTrue(create_and_write_file.create_file_contents(folder1_sub2_file1, "file1 contents"))

        good_base = self.folder1
        good_fullpath = folder1_sub1_file1
        good_target = self.folder2

        path_too_small1 = ""

        sample_base_1 = folder1_sub1
        sample_full_1 = path_utils.concat_path(good_base, "sub2", "file5.txt")

        self.assertFalse(path_utils.based_copy_to("", good_fullpath, good_target))
        self.assertFalse(path_utils.based_copy_to(good_base, "", good_target))
        self.assertFalse(path_utils.based_copy_to(good_base, good_fullpath, ""))

        self.assertFalse(path_utils.based_copy_to(None, good_fullpath, good_target))
        self.assertFalse(path_utils.based_copy_to(good_base, None, good_target))
        self.assertFalse(path_utils.based_copy_to(good_base, good_fullpath, None))

        self.assertFalse(path_utils.based_copy_to(self.nonexistent, good_fullpath, good_target))
        self.assertFalse(path_utils.based_copy_to(good_base, self.nonexistent, good_target))
        self.assertFalse(path_utils.based_copy_to(good_base, good_fullpath, self.nonexistent))

        self.assertFalse(path_utils.based_copy_to(path_too_small1, good_fullpath, good_target))
        self.assertFalse(path_utils.based_copy_to(good_base, path_too_small1, good_target))

        self.assertFalse(path_utils.based_copy_to(sample_base_1, sample_full_1, good_target))

    def testBasedCopyToFail2(self):

        folder1_sub1 = path_utils.concat_path(self.folder1, "sub1")
        os.mkdir(folder1_sub1)
        folder1_sub1_sub2 = path_utils.concat_path(folder1_sub1, "sub2")
        os.mkdir(folder1_sub1_sub2)
        folder1_sub1_sub2_file1 = path_utils.concat_path(folder1_sub1_sub2, "file1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(folder1_sub1_sub2_file1, "file1 contents"))
        self.assertTrue(os.path.exists(folder1_sub1_sub2_file1))

        folder2_sub1 = path_utils.concat_path(self.folder2, "sub1")
        os.mkdir(folder2_sub1)
        folder2_sub1_sub2 = path_utils.concat_path(folder2_sub1, "sub2")
        os.mkdir(folder2_sub1_sub2)
        folder2_sub1_sub2_file1 = path_utils.concat_path(folder2_sub1_sub2, "file1.txt")
        self.assertTrue(os.path.exists(folder2_sub1_sub2))
        self.assertTrue(create_and_write_file.create_file_contents(folder2_sub1_sub2_file1, "folder2 file1 contents"))
        self.assertTrue(os.path.exists(folder2_sub1_sub2_file1))

        self.assertFalse(path_utils.based_copy_to(folder1_sub1, folder1_sub1_sub2_file1, folder2_sub1))
        self.assertTrue(os.path.exists(folder2_sub1_sub2))
        self.assertTrue(os.path.exists(folder2_sub1_sub2_file1))

    def testBasedCopyToVanilla(self):

        folder1_sub1 = path_utils.concat_path(self.folder1, "sub1")
        os.mkdir(folder1_sub1)
        folder1_sub1_sub2 = path_utils.concat_path(folder1_sub1, "sub2")
        os.mkdir(folder1_sub1_sub2)
        folder1_sub1_sub2_file1 = path_utils.concat_path(folder1_sub1_sub2, "file1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(folder1_sub1_sub2_file1, "file1 contents"))
        self.assertTrue(os.path.exists(folder1_sub1_sub2_file1))

        folder2_sub1 = path_utils.concat_path(self.folder2, "sub1")
        os.mkdir(folder2_sub1)
        folder2_sub1_sub2 = path_utils.concat_path(folder2_sub1, "sub2")
        folder2_sub1_sub2_file1 = path_utils.concat_path(folder2_sub1_sub2, "file1.txt")
        self.assertFalse(os.path.exists(folder2_sub1_sub2))

        self.assertTrue(path_utils.based_copy_to(folder1_sub1, folder1_sub1_sub2_file1, folder2_sub1))
        self.assertTrue(os.path.exists(folder2_sub1_sub2))
        self.assertTrue(os.path.exists(folder2_sub1_sub2_file1))

    def testBasedCopyToFolder(self):

        folder1_sub1 = path_utils.concat_path(self.folder1, "sub1")
        os.mkdir(folder1_sub1)
        folder1_sub1_sub2 = path_utils.concat_path(folder1_sub1, "sub2")
        os.mkdir(folder1_sub1_sub2)
        folder1_sub1_sub2_file1 = path_utils.concat_path(folder1_sub1_sub2, "file1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(folder1_sub1_sub2_file1, "file1 contents"))
        self.assertTrue(os.path.exists(folder1_sub1_sub2_file1))

        folder2_sub1 = path_utils.concat_path(self.folder2, "sub1")
        os.mkdir(folder2_sub1)
        folder2_sub1_sub2 = path_utils.concat_path(folder2_sub1, "sub2")
        folder2_sub1_sub2_file1 = path_utils.concat_path(folder2_sub1_sub2, "file1.txt")
        self.assertFalse(os.path.exists(folder2_sub1_sub2))

        self.assertTrue(path_utils.based_copy_to(folder1_sub1, folder1_sub1_sub2, folder2_sub1))
        self.assertTrue(os.path.exists(folder2_sub1_sub2))
        self.assertTrue(os.path.exists(folder2_sub1_sub2_file1))

    def testBasedCopyToMidFolderExists(self):

        folder1_sub1 = path_utils.concat_path(self.folder1, "sub1")
        os.mkdir(folder1_sub1)
        folder1_sub1_sub2 = path_utils.concat_path(folder1_sub1, "sub2")
        os.mkdir(folder1_sub1_sub2)
        folder1_sub1_sub2_file1 = path_utils.concat_path(folder1_sub1_sub2, "file1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(folder1_sub1_sub2_file1, "file1 contents"))
        self.assertTrue(os.path.exists(folder1_sub1_sub2_file1))

        folder2_sub1 = path_utils.concat_path(self.folder2, "sub1")
        os.mkdir(folder2_sub1)
        folder2_sub1_sub2 = path_utils.concat_path(folder2_sub1, "sub2")
        folder2_sub1_sub2_file1 = path_utils.concat_path(folder2_sub1_sub2, "file1.txt")
        os.mkdir(folder2_sub1_sub2)
        self.assertTrue(os.path.exists(folder2_sub1_sub2))

        self.assertTrue(path_utils.based_copy_to(folder1_sub1, folder1_sub1_sub2_file1, folder2_sub1))
        self.assertTrue(os.path.exists(folder2_sub1_sub2))
        self.assertTrue(os.path.exists(folder2_sub1_sub2_file1))

    def testBasedCopyToDirectRootFile(self):

        folder1_file1 = path_utils.concat_path(self.folder1, "file1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(folder1_file1, "file1 contents"))

        folder2_file1 = path_utils.concat_path(self.folder2, "file1.txt")

        self.assertTrue(path_utils.based_copy_to(self.folder1, folder1_file1, self.folder2))
        self.assertTrue(os.path.exists(folder2_file1))

    def testBasedCopyToBrokenSymlink(self):

        folder1_sub1 = path_utils.concat_path(self.folder1, "sub1")
        os.mkdir(folder1_sub1)
        folder1_sub1_sub2 = path_utils.concat_path(folder1_sub1, "sub2")
        os.mkdir(folder1_sub1_sub2)
        folder1_sub1_sub2_file1 = path_utils.concat_path(folder1_sub1_sub2, "file1.txt")
        folder1_sub1_sub2_file2 = path_utils.concat_path(folder1_sub1_sub2, "file2.txt")
        self.assertTrue(create_and_write_file.create_file_contents(folder1_sub1_sub2_file1, "file1 contents"))
        self.assertTrue(os.path.exists(folder1_sub1_sub2_file1))
        os.symlink(folder1_sub1_sub2_file1, folder1_sub1_sub2_file2)
        self.assertTrue(os.path.exists(folder1_sub1_sub2_file2))
        os.unlink(folder1_sub1_sub2_file1)
        self.assertFalse(os.path.exists(folder1_sub1_sub2_file1))
        self.assertTrue(path_utils.is_path_broken_symlink(folder1_sub1_sub2_file2))

        folder2_sub1 = path_utils.concat_path(self.folder2, "sub1")
        os.mkdir(folder2_sub1)
        folder2_sub1_sub2 = path_utils.concat_path(folder2_sub1, "sub2")
        folder2_sub1_sub2_file2 = path_utils.concat_path(folder2_sub1_sub2, "file2.txt")
        self.assertFalse(os.path.exists(folder2_sub1_sub2))

        self.assertTrue(path_utils.based_copy_to(folder1_sub1, folder1_sub1_sub2_file2, folder2_sub1))
        self.assertTrue(os.path.exists(folder2_sub1_sub2))
        self.assertTrue(path_utils.is_path_broken_symlink(folder2_sub1_sub2_file2))

    def testBasedCopyToBinary(self):

        folder1_sub1 = path_utils.concat_path(self.folder1, "sub1")
        os.mkdir(folder1_sub1)
        folder1_sub1_sub2 = path_utils.concat_path(folder1_sub1, "sub2")
        os.mkdir(folder1_sub1_sub2)
        folder1_sub1_sub2_file1 = path_utils.concat_path(folder1_sub1_sub2, "file1.bin")

        self.assertFalse(os.path.exists(folder1_sub1_sub2_file1))
        with open(folder1_sub1_sub2_file1, "wb") as f:
            f.write(b"\xff\xff\xff")
        self.assertTrue(os.path.exists(folder1_sub1_sub2_file1))

        folder2_sub1 = path_utils.concat_path(self.folder2, "sub1")
        os.mkdir(folder2_sub1)
        folder2_sub1_sub2 = path_utils.concat_path(folder2_sub1, "sub2")
        folder2_sub1_sub2_file1 = path_utils.concat_path(folder2_sub1_sub2, "file1.bin")
        self.assertFalse(os.path.exists(folder2_sub1_sub2))

        self.assertTrue(path_utils.based_copy_to(folder1_sub1, folder1_sub1_sub2_file1, folder2_sub1))
        self.assertTrue(os.path.exists(folder2_sub1_sub2))
        self.assertTrue(os.path.exists(folder2_sub1_sub2_file1))

        contents = bytearray()
        with open(folder2_sub1_sub2_file1, "rb") as f:
            contents = f.read()
        self.assertEqual(contents, b"\xff\xff\xff")

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
        self.assertEqual(path_utils.find_middle_path_parts("/home/user", "/home/user/folder/another/path"), "folder/another")

    def testCopyToAndRename1(self):
        source_path = path_utils.concat_path(self.folder1, "source.txt")
        final_path = path_utils.concat_path(self.folder1, "target.txt")
        self.assertTrue(create_and_write_file.create_file_contents(source_path, "source"))
        self.assertTrue(os.path.exists(source_path))
        self.assertFalse(os.path.exists(final_path))
        self.assertTrue(path_utils.copy_to_and_rename(source_path, self.folder1, "target.txt"))
        self.assertTrue(os.path.exists(final_path))

    def testCopyToAndRename2(self):
        source_path = path_utils.concat_path(self.folder1, "source")
        final_path = path_utils.concat_path(self.folder1, "target")
        os.mkdir(source_path)
        self.assertTrue(os.path.exists(source_path))
        self.assertFalse(os.path.exists(final_path))
        self.assertTrue(path_utils.copy_to_and_rename(source_path, self.folder1, "target"))
        self.assertTrue(os.path.exists(final_path))

    def testCopyFileToAndRename1(self):
        source_path = path_utils.concat_path(self.folder1, "source.txt")
        final_path = path_utils.concat_path(self.folder1, "target.txt")
        self.assertTrue(create_and_write_file.create_file_contents(source_path, "source"))
        self.assertTrue(os.path.exists(source_path))
        self.assertFalse(os.path.exists(final_path))
        self.assertTrue(path_utils.copy_file_to_and_rename(source_path, self.folder1, "target.txt"))
        self.assertTrue(os.path.exists(final_path))

    def testCopyFileToAndRename2(self):
        source_path = path_utils.concat_path(self.folder1, "source.txt")
        self.assertTrue(create_and_write_file.create_file_contents(source_path, "source"))
        self.assertTrue(os.path.exists(source_path))
        self.assertFalse(path_utils.copy_file_to_and_rename(source_path, self.folder1, "source.txt"))

    def testCopyFileToAndRename3(self):
        source_path = path_utils.concat_path(self.folder1, "source.txt")
        self.assertTrue(create_and_write_file.create_file_contents(source_path, "source"))

        self.assertFalse(path_utils.copy_file_to_and_rename(None, self.folder1, "source.txt"))
        self.assertFalse(path_utils.copy_file_to_and_rename(source_path, None, "source.txt"))
        self.assertFalse(path_utils.copy_file_to_and_rename(source_path, self.folder1, None))

        self.assertFalse(path_utils.copy_file_to_and_rename(self.nonexistent, self.folder1, "target.txt"))
        self.assertFalse(path_utils.copy_file_to_and_rename(self.folder2, self.folder1, "target.txt"))
        self.assertFalse(path_utils.copy_file_to_and_rename(source_path, self.nonexistent, "target.txt"))
        self.assertFalse(path_utils.copy_file_to_and_rename(source_path, self.test_file, "target.txt"))
        self.assertFalse(path_utils.copy_file_to_and_rename(source_path, source_path, "target.txt"))
        self.assertFalse(path_utils.copy_file_to_and_rename(source_path, self.folder1, "sub/target.txt"))

        target_path = path_utils.concat_path(self.folder2, "target.txt")
        self.assertFalse(os.path.exists(target_path))
        self.assertTrue(create_and_write_file.create_file_contents(target_path, "target"))
        self.assertTrue(os.path.exists(target_path))
        self.assertFalse(path_utils.copy_file_to_and_rename(source_path, self.folder2, "target.txt"))

    def testCopyToAndRename4(self):
        source_path = path_utils.concat_path(self.folder1, " ")
        final_path = path_utils.concat_path(self.folder1, "target.txt")
        self.assertTrue(create_and_write_file.create_file_contents(source_path, "source contents"))
        self.assertTrue(os.path.exists(source_path))
        self.assertFalse(os.path.exists(final_path))
        self.assertTrue(path_utils.copy_to_and_rename(source_path, self.folder1, "target.txt"))
        self.assertTrue(os.path.exists(final_path))

    def testCopyToAndRename5(self):
        source_path = path_utils.concat_path(self.folder1, "source.txt")
        final_path = path_utils.concat_path(self.folder1, " ")
        self.assertTrue(create_and_write_file.create_file_contents(source_path, "source contents"))
        self.assertTrue(os.path.exists(source_path))
        self.assertFalse(os.path.exists(final_path))
        self.assertTrue(path_utils.copy_to_and_rename(source_path, self.folder1, " "))
        self.assertTrue(os.path.exists(final_path))

    def testCopyFileToAndRenameBinary(self):
        source_path = path_utils.concat_path(self.folder1, "source.bin")
        final_path = path_utils.concat_path(self.folder1, "target.bin")

        self.assertFalse(os.path.exists(source_path))
        with open(source_path, "wb") as f:
            f.write(b"\xff\xff\xff")
        self.assertTrue(os.path.exists(source_path))

        self.assertTrue(os.path.exists(source_path))
        self.assertFalse(os.path.exists(final_path))
        self.assertTrue(path_utils.copy_file_to_and_rename(source_path, self.folder1, "target.bin"))
        self.assertTrue(os.path.exists(final_path))

        contents = bytearray()
        with open(final_path, "rb") as f:
            contents = f.read()
        self.assertEqual(contents, b"\xff\xff\xff")

    def testCopyFolderToAndRename1(self):
        source_path = path_utils.concat_path(self.folder1, "source")
        final_path = path_utils.concat_path(self.folder1, "target")
        os.mkdir(source_path)
        source_path_file = path_utils.concat_path(source_path, "file1.txt")
        final_path_file = path_utils.concat_path(self.folder1, "target", "file1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(source_path_file, "test contents"))
        self.assertTrue(os.path.exists(source_path_file))
        self.assertFalse(os.path.exists(final_path_file))
        self.assertTrue(os.path.exists(source_path))
        self.assertFalse(os.path.exists(final_path))
        self.assertTrue(path_utils.copy_folder_to_and_rename(source_path, self.folder1, "target"))
        self.assertTrue(os.path.exists(final_path))
        self.assertTrue(os.path.exists(final_path_file))

    def testCopyFolderToAndRename2(self):
        source_path = path_utils.concat_path(self.folder1, "source")
        os.mkdir(source_path)
        self.assertTrue(os.path.exists(source_path))
        self.assertFalse(path_utils.copy_folder_to_and_rename(source_path, self.folder1, "source"))

    def testCopyFolderToAndRename3(self):
        source_path = path_utils.concat_path(self.folder1, "source")
        os.mkdir(source_path)

        self.assertFalse(path_utils.copy_folder_to_and_rename(None, self.folder1, "target"))
        self.assertFalse(path_utils.copy_folder_to_and_rename(source_path, None, "target"))
        self.assertFalse(path_utils.copy_folder_to_and_rename(source_path, self.folder1, None))

        self.assertFalse(path_utils.copy_folder_to_and_rename(self.nonexistent, self.folder1, "target"))
        self.assertFalse(path_utils.copy_folder_to_and_rename(self.test_file, self.folder1, "target"))
        self.assertFalse(path_utils.copy_folder_to_and_rename(source_path, self.nonexistent, "target"))
        self.assertFalse(path_utils.copy_folder_to_and_rename(source_path, self.test_file, "target"))
        self.assertFalse(path_utils.copy_folder_to_and_rename(source_path, source_path, "target"))
        self.assertFalse(path_utils.copy_folder_to_and_rename(source_path, self.folder1, "sub/target"))

        target_path = path_utils.concat_path(self.folder2, "target")
        self.assertFalse(os.path.exists(target_path))
        os.mkdir(target_path)
        self.assertTrue(os.path.exists(target_path))
        self.assertFalse(path_utils.copy_folder_to_and_rename(source_path, self.folder2, "target"))

    def testCopyFolderToAndRename4(self):
        source_path = path_utils.concat_path(self.folder1, " ")
        final_path = path_utils.concat_path(self.folder1, "target")
        os.mkdir(source_path)
        source_path_file = path_utils.concat_path(source_path, "file1.txt")
        final_path_file = path_utils.concat_path(self.folder1, "target", "file1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(source_path_file, "test contents"))
        self.assertTrue(os.path.exists(source_path_file))
        self.assertFalse(os.path.exists(final_path_file))
        self.assertTrue(os.path.exists(source_path))
        self.assertFalse(os.path.exists(final_path))
        self.assertTrue(path_utils.copy_folder_to_and_rename(source_path, self.folder1, "target"))
        self.assertTrue(os.path.exists(final_path))
        self.assertTrue(os.path.exists(final_path_file))

    def testCopyFolderToAndRename5(self):
        source_path = path_utils.concat_path(self.folder1, "source")
        final_path = path_utils.concat_path(self.folder1, " ")
        os.mkdir(source_path)
        source_path_file = path_utils.concat_path(source_path, "file1.txt")
        final_path_file = path_utils.concat_path(self.folder1, " ", "file1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(source_path_file, "test contents"))
        self.assertTrue(os.path.exists(source_path_file))
        self.assertFalse(os.path.exists(final_path_file))
        self.assertTrue(os.path.exists(source_path))
        self.assertFalse(os.path.exists(final_path))
        self.assertTrue(path_utils.copy_folder_to_and_rename(source_path, self.folder1, " "))
        self.assertTrue(os.path.exists(final_path))
        self.assertTrue(os.path.exists(final_path_file))

    def testCompatWindowsPath(self):
        self.assertEqual(path_utils.compat_windows_path(None), None)
        self.assertEqual(path_utils.compat_windows_path([]), None)
        self.assertEqual(path_utils.compat_windows_path(""), None)
        self.assertEqual(path_utils.compat_windows_path("nothing"), "nothing")
        self.assertEqual(path_utils.compat_windows_path("C:\\windows\\data"), "C:/windows/data")
        self.assertEqual(path_utils.compat_windows_path("windows\\data\\more"), "windows/data/more")
        self.assertEqual(path_utils.compat_windows_path("windows\\data\\another\\"), "windows/data/another/")
        self.assertEqual(path_utils.compat_windows_path("some/folders"), "some/folders")
        self.assertEqual(path_utils.compat_windows_path("/usr/local/more/folders"), "/usr/local/more/folders")
        self.assertEqual(path_utils.compat_windows_path("/usr/local/more/folders/yetmore/"), "/usr/local/more/folders/yetmore/")

    def testIsPathBrokenSymlinkFile(self):

        folder1_file1 = path_utils.concat_path(self.folder1, "file1.txt")
        folder1_file2 = path_utils.concat_path(self.folder1, "file2.txt")

        self.assertTrue(create_and_write_file.create_file_contents(folder1_file1, "file1"))
        os.symlink(folder1_file1, folder1_file2)
        self.assertFalse(path_utils.is_path_broken_symlink(folder1_file1))
        self.assertFalse(path_utils.is_path_broken_symlink(folder1_file2))
        self.assertTrue(os.path.exists(folder1_file1))
        self.assertTrue(os.path.exists(folder1_file2))
        os.unlink(folder1_file1)
        self.assertFalse(os.path.exists(folder1_file1))
        self.assertFalse(os.path.exists(folder1_file2))
        self.assertTrue(path_utils.is_path_broken_symlink(folder1_file2))
        self.assertFalse(path_utils.is_path_broken_symlink(self.folder1))
        self.assertFalse(path_utils.is_path_broken_symlink(self.nonexistent))

    def testIsPathBrokenSymlinkFolder(self):

        folder1_sub1 = path_utils.concat_path(self.folder1, "sub1")
        folder1_sub2 = path_utils.concat_path(self.folder1, "sub2")

        os.mkdir(folder1_sub1)
        self.assertTrue(os.path.exists(folder1_sub1))
        os.symlink(folder1_sub1, folder1_sub2)
        self.assertFalse(path_utils.is_path_broken_symlink(folder1_sub1))
        self.assertFalse(path_utils.is_path_broken_symlink(folder1_sub2))
        self.assertTrue(os.path.exists(folder1_sub1))
        self.assertTrue(os.path.exists(folder1_sub2))
        shutil.rmtree(folder1_sub1)
        self.assertFalse(os.path.exists(folder1_sub1))
        self.assertFalse(os.path.exists(folder1_sub2))
        self.assertTrue(path_utils.is_path_broken_symlink(folder1_sub2))
        self.assertFalse(path_utils.is_path_broken_symlink(self.folder1))
        self.assertFalse(path_utils.is_path_broken_symlink(self.nonexistent))

    def testCopyToBrokenSymLinkFile(self):

        folder1_file1 = path_utils.concat_path(self.folder1, "file1.txt")
        folder1_file2 = path_utils.concat_path(self.folder1, "file2.txt")
        folder2_file2 = path_utils.concat_path(self.folder2, "file2.txt")

        self.assertTrue(create_and_write_file.create_file_contents(folder1_file1, "file1"))
        os.symlink(folder1_file1, folder1_file2)
        self.assertTrue(os.path.exists(folder1_file2))
        os.unlink(folder1_file1)
        self.assertTrue(path_utils.is_path_broken_symlink(folder1_file2))

        self.assertTrue(path_utils.copy_to(folder1_file2, self.folder2))
        self.assertTrue(path_utils.is_path_broken_symlink(folder2_file2))

    def testCopyToBrokenSymLinkFolder(self):

        folder1_sub1 = path_utils.concat_path(self.folder1, "sub1")
        folder1_sub2 = path_utils.concat_path(self.folder1, "sub2")
        folder2_sub2 = path_utils.concat_path(self.folder2, "sub2")

        os.mkdir(folder1_sub1)
        self.assertTrue(os.path.exists(folder1_sub1))
        os.symlink(folder1_sub1, folder1_sub2)
        self.assertTrue(os.path.exists(folder1_sub2))
        shutil.rmtree(folder1_sub1)
        self.assertTrue(path_utils.is_path_broken_symlink(folder1_sub2))

        self.assertTrue(path_utils.copy_to(folder1_sub2, self.folder2))
        self.assertTrue(path_utils.is_path_broken_symlink(folder2_sub2))

    def testCopyToFolderContainingBrokenSymLinkFile(self):

        folder1_sub1 = path_utils.concat_path(self.folder1, "sub1")
        folder1_sub1_file1 = path_utils.concat_path(folder1_sub1, "file1.txt")
        folder1_sub1_file2 = path_utils.concat_path(folder1_sub1, "file2.txt")
        folder1_sub1_file3 = path_utils.concat_path(folder1_sub1, "file3.txt")
        folder2_sub1 = path_utils.concat_path(self.folder2, "sub1")
        folder2_sub1_file1 = path_utils.concat_path(folder2_sub1, "file1.txt")
        folder2_sub1_file2 = path_utils.concat_path(folder2_sub1, "file2.txt")
        folder2_sub1_file3 = path_utils.concat_path(folder2_sub1, "file3.txt")

        os.mkdir(folder1_sub1)
        self.assertTrue(os.path.isdir(folder1_sub1))
        self.assertTrue(create_and_write_file.create_file_contents(folder1_sub1_file1, "file1 contents"))
        self.assertTrue(create_and_write_file.create_file_contents(folder1_sub1_file2, "file2 contents"))
        os.symlink(folder1_sub1_file2, folder1_sub1_file3)
        os.unlink(folder1_sub1_file2)
        self.assertFalse(os.path.exists(folder1_sub1_file2))
        self.assertTrue(path_utils.is_path_broken_symlink(folder1_sub1_file3))

        self.assertTrue(path_utils.copy_to(folder1_sub1, self.folder2))
        self.assertTrue(os.path.isdir(folder2_sub1))
        self.assertTrue(os.path.exists(folder2_sub1_file1))
        self.assertFalse(os.path.exists(folder2_sub1_file2))
        self.assertTrue(path_utils.is_path_broken_symlink(folder2_sub1_file3))

    def testCopyToFolderContainingBrokenSymLinkFolder(self):

        folder1_sub1 = path_utils.concat_path(self.folder1, "sub1")
        folder1_sub1_subfolder1 = path_utils.concat_path(folder1_sub1, "subfolder1")
        folder1_sub1_subfolder2 = path_utils.concat_path(folder1_sub1, "subfolder2")
        folder1_sub1_subfolder3 = path_utils.concat_path(folder1_sub1, "subfolder3")
        folder2_sub1 = path_utils.concat_path(self.folder2, "sub1")
        folder2_sub1_subfolder1 = path_utils.concat_path(folder2_sub1, "subfolder1")
        folder2_sub1_subfolder2 = path_utils.concat_path(folder2_sub1, "subfolder2")
        folder2_sub1_subfolder3 = path_utils.concat_path(folder2_sub1, "subfolder3")

        os.mkdir(folder1_sub1)
        self.assertTrue(os.path.isdir(folder1_sub1))
        os.mkdir(folder1_sub1_subfolder1)
        os.mkdir(folder1_sub1_subfolder2)
        os.symlink(folder1_sub1_subfolder2, folder1_sub1_subfolder3)
        shutil.rmtree(folder1_sub1_subfolder2)
        self.assertFalse(os.path.exists(folder1_sub1_subfolder2))
        self.assertTrue(path_utils.is_path_broken_symlink(folder1_sub1_subfolder3))

        self.assertTrue(path_utils.copy_to(folder1_sub1, self.folder2))
        self.assertTrue(os.path.isdir(folder2_sub1))
        self.assertTrue(os.path.isdir(folder2_sub1_subfolder1))
        self.assertFalse(os.path.exists(folder2_sub1_subfolder2))
        self.assertTrue(path_utils.is_path_broken_symlink(folder2_sub1_subfolder3))

    def testCopyToAndRenameBrokenSymLinkFile(self):

        folder1_file1 = path_utils.concat_path(self.folder1, "file1.txt")
        folder1_file2 = path_utils.concat_path(self.folder1, "file2.txt")
        folder2_file3 = path_utils.concat_path(self.folder2, "file3.txt")

        self.assertTrue(create_and_write_file.create_file_contents(folder1_file1, "file1"))
        os.symlink(folder1_file1, folder1_file2)
        self.assertTrue(os.path.exists(folder1_file2))
        os.unlink(folder1_file1)
        self.assertTrue(path_utils.is_path_broken_symlink(folder1_file2))

        self.assertTrue(path_utils.copy_to_and_rename(folder1_file2, self.folder2, "file3.txt"))
        self.assertTrue(path_utils.is_path_broken_symlink(folder2_file3))

    def testCopyToAndRenameBrokenSymLinkFolder(self):

        folder1_sub1 = path_utils.concat_path(self.folder1, "sub1")
        folder1_sub2 = path_utils.concat_path(self.folder1, "sub2")
        folder2_sub3 = path_utils.concat_path(self.folder2, "sub3")

        os.mkdir(folder1_sub1)
        self.assertTrue(os.path.exists(folder1_sub1))
        os.symlink(folder1_sub1, folder1_sub2)
        self.assertTrue(os.path.exists(folder1_sub2))
        shutil.rmtree(folder1_sub1)
        self.assertTrue(path_utils.is_path_broken_symlink(folder1_sub2))

        self.assertTrue(path_utils.copy_to_and_rename(folder1_sub2, self.folder2, "sub3"))
        self.assertTrue(path_utils.is_path_broken_symlink(folder2_sub3))

    def testRemovePathFail(self):

        self.assertFalse(path_utils.remove_path(None))
        self.assertFalse(path_utils.remove_path(""))
        self.assertFalse(path_utils.remove_path(self.nonexistent))

    def testRemovePathFile(self):

        self.assertTrue(os.path.exists(self.test_file))
        self.assertTrue(path_utils.remove_path(self.test_file))
        self.assertFalse(os.path.exists(self.test_file))

    def testRemovePathFolder(self):

        self.assertTrue(os.path.exists(self.folder1))
        self.assertTrue(path_utils.remove_path(self.folder1))
        self.assertFalse(os.path.exists(self.folder1))

    def testRemovePathFileBrokenSymlink(self):

        self.assertTrue(os.path.exists(self.test_file))
        test_file_link = path_utils.concat_path(self.test_dir, "test_file_link.txt")
        self.assertFalse(os.path.exists(test_file_link))

        os.symlink(self.test_file, test_file_link)
        self.assertTrue(os.path.exists(test_file_link))

        os.unlink(self.test_file)
        self.assertFalse(os.path.exists(test_file_link))
        self.assertFalse(os.path.exists(self.test_file))

        self.assertTrue(path_utils.is_path_broken_symlink(test_file_link))
        self.assertTrue(path_utils.remove_path(test_file_link))
        self.assertFalse(path_utils.is_path_broken_symlink(test_file_link))

    def testRemovePathFolder(self):

        self.assertTrue(os.path.exists(self.folder1))
        folder1_link = path_utils.concat_path(self.test_dir, "folder1_link")
        self.assertFalse(os.path.exists(folder1_link))

        os.symlink(self.folder1, folder1_link)
        self.assertTrue(os.path.exists(folder1_link))

        shutil.rmtree(self.folder1)
        self.assertFalse(os.path.exists(folder1_link))
        self.assertFalse(os.path.exists(self.folder1))

        self.assertTrue(path_utils.is_path_broken_symlink(folder1_link))
        self.assertTrue(path_utils.remove_path(folder1_link))
        self.assertFalse(path_utils.is_path_broken_symlink(folder1_link))

    def testIsParentPath(self):

        self.assertEqual(path_utils.is_parentpath(None, "/home/user", True), None)
        self.assertEqual(path_utils.is_parentpath("/home/user", None, True), None)
        self.assertEqual(path_utils.is_parentpath("", "/home/user", True), None)
        self.assertEqual(path_utils.is_parentpath("/home/user", "", True), None)

        self.assertFalse(path_utils.is_parentpath("/home/user", "/home/user/", True))
        self.assertFalse(path_utils.is_parentpath("/home/user", "/home/user/", True))
        self.assertFalse(path_utils.is_parentpath("/home/user/", "/home/user", True))
        self.assertFalse(path_utils.is_parentpath("/home/user/", "/home/user/", True))

        self.assertTrue(path_utils.is_parentpath("/home", "/home/user/folder", True))
        self.assertTrue(path_utils.is_parentpath("/", "/home/user/folder", True))
        self.assertTrue(path_utils.is_parentpath("/", "/file.txt", True))
        self.assertTrue(path_utils.is_parentpath("/home/user", "/home/user/folder", True))
        self.assertTrue(path_utils.is_parentpath("/home/user", "/home/user/folder/sub/level/another", True))
        self.assertFalse(path_utils.is_parentpath("/home/client", "/home/user/folder/sub/level/another", True))
        self.assertTrue(path_utils.is_parentpath("/home/user/folder/sub", "/home/user/folder/sub/level/another", True))
        self.assertFalse(path_utils.is_parentpath("/base/user/folder/sub", "/home/user/folder/sub/level/another", True))
        self.assertFalse(path_utils.is_parentpath("/home/user/folder/sub/level/another", "/home/user/folder/sub/level/anothers", True))
        self.assertFalse(path_utils.is_parentpath("/base/user/folder/sub", "/home/user", True))
        self.assertFalse(path_utils.is_parentpath("/home/user/folder/sub", "/home/user", True))
        self.assertTrue(path_utils.is_parentpath("/home/user/folder", "/home/user/folder/somefile.txt", True))
        self.assertTrue(path_utils.is_parentpath("/home/user/folder/ /base", "/home/user/folder/ /base/file.bin", True))
        self.assertTrue(path_utils.is_parentpath("/home/user/folder/ /base", "/home/user/folder/ /base/ ", True))

        folder1_sub1 = path_utils.concat_path(self.folder1, "sub1")
        self.assertFalse(os.path.exists(folder1_sub1))
        self.assertTrue(path_utils.is_parentpath(self.folder1, folder1_sub1, True))
        os.symlink(self.folder2, folder1_sub1)
        self.assertTrue(os.path.exists(folder1_sub1))
        self.assertFalse(path_utils.is_parentpath(self.folder1, folder1_sub1, True))
        self.assertTrue(path_utils.is_parentpath(self.folder1, folder1_sub1, False))

        folder1_sub2 = path_utils.concat_path(self.folder1, "sub2")
        self.assertFalse(os.path.exists(folder1_sub2))
        os.mkdir(folder1_sub2)
        self.assertTrue(os.path.exists(folder1_sub2))

        folder1_sub2_another = path_utils.concat_path(folder1_sub2, "another")
        self.assertFalse(os.path.exists(folder1_sub2_another))
        os.symlink(self.folder2, folder1_sub2_another)
        self.assertTrue(os.path.exists(folder1_sub2_another))

        folder2_sub1 = path_utils.concat_path(self.folder2, "sub1")
        self.assertFalse(os.path.exists(folder2_sub1))
        os.mkdir(folder2_sub1)
        self.assertTrue(os.path.exists(folder2_sub1))

        self.assertTrue(path_utils.is_parentpath(folder1_sub2_another, folder2_sub1, True))
        self.assertFalse(path_utils.is_parentpath(folder1_sub2_another, folder2_sub1, False))

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            self.assertTrue(path_utils.is_parentpath("/home/user/sub/../..", "/home/file.txt", True))
            self.assertTrue(path_utils.is_parentpath("/home/user/sub/../../", "/home/file.txt", True))
            self.assertTrue(path_utils.is_parentpath("/home/user/sub/../../..", "/home/file.txt", True))
            self.assertTrue(path_utils.is_parentpath("/home/user/sub/../../..", "/clients/another/morefolders/file.txt", True))
        finally:
            os.chdir(saved_wd)

    def testIsSubPath(self):

        self.assertEqual(path_utils.is_subpath(None, "/home/user", True), None)
        self.assertEqual(path_utils.is_subpath("/home/user", None, True), None)
        self.assertEqual(path_utils.is_subpath("", "/home/user", True), None)
        self.assertEqual(path_utils.is_subpath("/home/user", "", True), None)

        self.assertFalse(path_utils.is_subpath("/home/user", "/home/user/", True))
        self.assertFalse(path_utils.is_subpath("/home/user", "/home/user/", True))
        self.assertFalse(path_utils.is_subpath("/home/user/", "/home/user", True))
        self.assertFalse(path_utils.is_subpath("/home/user/", "/home/user/", True))

        self.assertTrue(path_utils.is_subpath("/home/user/folder", "/home/user", True))
        self.assertFalse(path_utils.is_subpath("/home/user", "/home/user/folder", True))

    def testIsFolderEmptyFail(self):

        self.assertEqual(path_utils.is_folder_empty(None), None)
        self.assertEqual(path_utils.is_folder_empty(""), None)
        self.assertEqual(path_utils.is_folder_empty(self.nonexistent), None)
        self.assertEqual(path_utils.is_folder_empty(self.test_file), None)

        folder1_sub1 = path_utils.concat_path(self.folder1, "sub1")
        folder1_sub2 = path_utils.concat_path(self.folder1, "sub2")
        self.assertFalse(os.path.exists(folder1_sub1))
        self.assertFalse(os.path.exists(folder1_sub2))
        os.mkdir(folder1_sub1)
        os.symlink(folder1_sub1, folder1_sub2)
        self.assertTrue(os.path.exists(folder1_sub1))
        self.assertTrue(os.path.exists(folder1_sub2))

        folder1_sub1_file1 = path_utils.concat_path(folder1_sub1, "file1.txt")
        self.assertFalse(os.path.exists(folder1_sub1_file1))
        create_and_write_file.create_file_contents(folder1_sub1_file1, "test-sub-file")
        self.assertTrue(os.path.exists(folder1_sub1_file1))

        self.assertFalse(path_utils.is_folder_empty(folder1_sub1))
        self.assertFalse(path_utils.is_folder_empty(folder1_sub2))

        shutil.rmtree(folder1_sub1)
        self.assertFalse(os.path.exists(folder1_sub1))
        self.assertTrue(path_utils.is_path_broken_symlink(folder1_sub2))

        self.assertFalse(path_utils.is_folder_empty(folder1_sub2))

    def testIsFolderEmpty1(self):

        self.assertTrue(path_utils.is_folder_empty(self.folder1))
        folder1_sub = path_utils.concat_path(self.folder1, "sub")
        self.assertFalse(os.path.exists(folder1_sub))
        os.mkdir(folder1_sub)
        self.assertTrue(os.path.exists(folder1_sub))
        self.assertFalse(path_utils.is_folder_empty(self.folder1))

    def testIsFolderEmpty2(self):

        self.assertTrue(path_utils.is_folder_empty(self.folder1))
        folder1_file1 = path_utils.concat_path(self.folder1, "file1.txt")
        self.assertFalse(os.path.exists(folder1_file1))
        create_and_write_file.create_file_contents(folder1_file1, "test-file")
        self.assertTrue(os.path.exists(folder1_file1))
        self.assertFalse(path_utils.is_folder_empty(self.folder1))

    def testIsFolderEmpty3(self):

        self.assertTrue(path_utils.is_folder_empty(self.folder1))
        folder1_sub = path_utils.concat_path(self.folder1, ".sub")
        self.assertFalse(os.path.exists(folder1_sub))
        os.mkdir(folder1_sub)
        self.assertTrue(os.path.exists(folder1_sub))
        self.assertFalse(path_utils.is_folder_empty(self.folder1))

    def testIsFolderEmpty4(self):

        self.assertTrue(path_utils.is_folder_empty(self.folder1))
        folder1_file1 = path_utils.concat_path(self.folder1, ".hidden_file")
        self.assertFalse(os.path.exists(folder1_file1))
        create_and_write_file.create_file_contents(folder1_file1, "test-file")
        self.assertTrue(os.path.exists(folder1_file1))
        self.assertFalse(path_utils.is_folder_empty(self.folder1))

    def testIsFolderEmpty5(self):

        self.assertTrue(path_utils.is_folder_empty(self.folder1))
        folder1_file1 = path_utils.concat_path(self.folder1, " ")
        self.assertFalse(os.path.exists(folder1_file1))
        create_and_write_file.create_file_contents(folder1_file1, "test-file")
        self.assertTrue(os.path.exists(folder1_file1))
        self.assertFalse(path_utils.is_folder_empty(self.folder1))

    def testIsFolderEmpty6(self):

        self.assertTrue(path_utils.is_folder_empty(self.folder1))
        folder1_file1 = path_utils.concat_path(self.folder1, "file1.txt")
        folder1_file2 = path_utils.concat_path(self.folder1, "file2.txt")
        self.assertFalse(os.path.exists(folder1_file1))
        self.assertFalse(os.path.exists(folder1_file2))
        create_and_write_file.create_file_contents(folder1_file1, "test-file")
        self.assertTrue(os.path.exists(folder1_file1))
        self.assertFalse(path_utils.is_folder_empty(self.folder1))

        os.symlink(folder1_file1, folder1_file2)
        self.assertTrue(os.path.exists(folder1_file2))
        os.unlink(folder1_file1)
        self.assertFalse(os.path.exists(folder1_file1))
        self.assertTrue(path_utils.is_path_broken_symlink(folder1_file2))
        self.assertFalse(path_utils.is_folder_empty(self.folder1))
        os.unlink(folder1_file2)
        self.assertTrue(path_utils.is_folder_empty(self.folder1))

if __name__ == '__main__':
    unittest.main()
