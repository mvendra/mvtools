#!/usr/bin/env python3

import os
import shutil
import unittest

import mvtools_test_fixture
import create_and_write_file
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
        self.assertEqual(path_utils.basename_filtered(""), "")
        self.assertEqual(path_utils.basename_filtered("/home"), "home")
        self.assertEqual(path_utils.basename_filtered("/home/"), "home")
        self.assertEqual(path_utils.basename_filtered("/home/user"), "user")
        self.assertEqual(path_utils.basename_filtered("/home/user/"), "user")

    def testDirnameFiltered(self):
        self.assertEqual(path_utils.dirname_filtered(""), "")
        self.assertEqual(path_utils.dirname_filtered("/home/user"), "/home")
        self.assertEqual(path_utils.dirname_filtered("/home/user/"), "/home")
        self.assertEqual(path_utils.dirname_filtered("/"), "")

    def testCopyToFail1(self):

        folder1_file1 = path_utils.concat_path(self.folder1, "file1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(folder1_file1, "file1 contents"))

        folder2_file1 = path_utils.concat_path(self.folder2, "file1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(folder2_file1, "file1 contents"))

        self.assertFalse(path_utils.copy_to(folder1_file1, self.folder2))
        folder2_file1 = path_utils.concat_path(self.folder2, "file1.txt")
        self.assertTrue(os.path.exists(folder2_file1))

    def testCopyToFail2(self):

        folder1_sub = path_utils.concat_path(self.folder1, "sub")
        os.mkdir(folder1_sub)
        self.assertTrue(os.path.exists(folder1_sub))

        folder1_sub_file1 = path_utils.concat_path(self.folder1, "sub", "file1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(folder1_sub_file1, "file1 contents"))

        folder2_sub = path_utils.concat_path(self.folder2, "sub")
        os.mkdir(folder2_sub)
        self.assertTrue(os.path.exists(folder2_sub))

        self.assertFalse(path_utils.copy_to(folder1_sub, self.folder2))
        folder2_sub = path_utils.concat_path(self.folder2, "sub")
        self.assertTrue(os.path.exists(folder2_sub))
        folder2_sub_file1 = path_utils.concat_path(self.folder2, "sub", "file1.txt")
        self.assertFalse(os.path.exists(folder2_sub_file1))

    def testCopyToFail3(self):

        folder1_file1 = path_utils.concat_path(self.folder1, "file1")
        self.assertTrue(create_and_write_file.create_file_contents(folder1_file1, "file1 contents"))

        folder2_file1 = path_utils.concat_path(self.folder2, "file1")
        os.mkdir(folder2_file1)
        self.assertTrue(os.path.exists(folder2_file1))

        self.assertFalse(path_utils.copy_to(folder1_file1, self.folder2))
        folder2_file1_file1 = path_utils.concat_path(folder2_file1, "file1")
        self.assertFalse(os.path.exists(folder2_file1_file1))

    def testCopyToFail4(self):

        folder1_sub = path_utils.concat_path(self.folder1, "sub")
        os.mkdir(folder1_sub)
        self.assertTrue(os.path.exists(folder1_sub))

        folder2_sub = path_utils.concat_path(self.folder2, "sub")
        self.assertTrue(create_and_write_file.create_file_contents(folder2_sub, "folder2 sub fake folder"))
        self.assertTrue(os.path.exists(folder2_sub))

        self.assertFalse(path_utils.copy_to(folder1_sub, folder2_sub))

    def testCopyToVanilla(self):

        folder1_file1 = path_utils.concat_path(self.folder1, "file1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(folder1_file1, "file1 contents"))

        self.assertTrue(path_utils.copy_to(folder1_file1, self.folder2))
        folder2_file1 = path_utils.concat_path(self.folder2, "file1.txt")
        self.assertTrue(os.path.exists(folder2_file1))

    def testCopyToFullFilePath(self):

        folder1_file1 = path_utils.concat_path(self.folder1, "file1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(folder1_file1, "file1 contents"))

        folder2_file1 = path_utils.concat_path(self.folder2, "file1.txt")
        self.assertTrue(path_utils.copy_to(folder1_file1, folder2_file1))
        self.assertTrue(os.path.exists(folder2_file1))

    def testCopyToFolder(self):

        folder1_sub = path_utils.concat_path(self.folder1, "sub")
        os.mkdir(folder1_sub)
        self.assertTrue(os.path.exists(folder1_sub))

        folder1_sub_file1 = path_utils.concat_path(folder1_sub, "file1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(folder1_sub_file1, "file1 contents"))

        self.assertTrue(path_utils.copy_to(folder1_sub, self.folder2))
        folder2_sub_file1 = path_utils.concat_path(self.folder2, "sub", "file1.txt")
        self.assertTrue(os.path.exists(folder2_sub_file1))

    def testCopyToFolderToFolderRenaming(self):

        folder1_sub1 = path_utils.concat_path(self.folder1, "sub1")
        os.mkdir(folder1_sub1)
        self.assertTrue(os.path.exists(folder1_sub1))

        folder1_sub1_file1 = path_utils.concat_path(folder1_sub1, "file1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(folder1_sub1_file1, "file1 contents"))

        folder2_sub2 = path_utils.concat_path(self.folder2, "sub2")
        folder2_sub2_file1 = path_utils.concat_path(folder2_sub2, "file1.txt")
        self.assertTrue(path_utils.copy_to(folder1_sub1, folder2_sub2))
        self.assertTrue(os.path.exists(folder2_sub2_file1))

    def testBasedCopyToFail(self):

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

        path_too_small1 = "/"

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

        self.assertTrue(path_utils.based_copy_to(folder1_sub1, folder1_sub1_sub2, folder2_sub1))
        self.assertTrue(os.path.exists(folder2_sub1_sub2))
        self.assertTrue(os.path.exists(folder2_sub1_sub2_file1))

    def testBasedCopyToDirectRootFile(self):

        folder1_file1 = path_utils.concat_path(self.folder1, "file1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(folder1_file1, "file1 contents"))

        folder2_file1 = path_utils.concat_path(self.folder2, "file1.txt")

        self.assertTrue(path_utils.based_copy_to(self.folder1, folder1_file1, self.folder2))
        self.assertTrue(os.path.exists(folder2_file1))

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
