#!/usr/bin/env python3

import sys
import os
import shutil
import unittest

import path_utils
import git_wrapper
import mvtools_test_fixture
import fsquery_adv_filter

escape_context_1 = []

def func_save_context(path, params):
    escape_context_1.append("%s@%s" % (path, params))
    return True

class FsqueryAdvFilterTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("fsquery_adv_filter_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # reset globals
        global escape_context_1
        escape_context_1 = []

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testFilterSanityCheck(self):

        self.assertEqual(fsquery_adv_filter.filter_path_list([], [(1, 2)], None), [])

        self.assertEqual(fsquery_adv_filter.filter_path_list("string", [], None), None)
        self.assertEqual(fsquery_adv_filter.filter_path_list(None, [], None), None)
        self.assertEqual(fsquery_adv_filter.filter_path_list([], "string", None), None)
        self.assertEqual(fsquery_adv_filter.filter_path_list([], None, None), None)
        self.assertEqual(fsquery_adv_filter.filter_path_list([], [(1)], None), None)
        self.assertEqual(fsquery_adv_filter.filter_path_list([], [(1, 2, 3)], None), None)

    def testFilterBasic_And(self):

        paths = ["/user/home/file1.txt", "/user/home/file2.txt", "/user/home/file3.txt"]
        paths_returned = fsquery_adv_filter.filter_path_list_and(paths, [(func_save_context, "test-filter-basic")])
        self.assertEqual(paths_returned, paths)
        self.assertEqual(escape_context_1, ["/user/home/file1.txt@test-filter-basic", "/user/home/file2.txt@test-filter-basic", "/user/home/file3.txt@test-filter-basic"])

    def testFilterBasic_Or(self):

        paths = ["/user/home/file1.txt", "/user/home/file2.txt", "/user/home/file3.txt"]
        paths_returned = fsquery_adv_filter.filter_path_list_or(paths, [(func_save_context, "test-filter-basic")])
        self.assertEqual(paths_returned, paths)
        self.assertEqual(escape_context_1, ["/user/home/file1.txt@test-filter-basic", "/user/home/file2.txt@test-filter-basic", "/user/home/file3.txt@test-filter-basic"])

    def testFilterNegative_And(self):

        paths = ["/user/home/file1.txt", "/user/home/file2.txt", "/user/home/file3.txt"]
        paths_returned = fsquery_adv_filter.filter_path_list_and(paths, [(fsquery_adv_filter.filter_all_negative, "test-filter-basic")])
        self.assertEqual(paths_returned, [])

    def testFilterNegative_Or(self):

        paths = ["/user/home/file1.txt", "/user/home/file2.txt", "/user/home/file3.txt"]
        paths_returned = fsquery_adv_filter.filter_path_list_or(paths, [(fsquery_adv_filter.filter_all_negative, "test-filter-basic")])
        self.assertEqual(paths_returned, [])

    def testFilterRepos_And(self):

        first_repo = path_utils.concat_path(self.test_dir, "first")
        v, r = git_wrapper.init(self.test_dir, "first", True)
        if not v:
            self.fail(r)

        second_repo = path_utils.concat_path(self.test_dir, "second")
        v, r = git_wrapper.init(self.test_dir, "second", False)
        if not v:
            self.fail(r)

        third_notrepo = path_utils.concat_path(self.test_dir, "third")
        os.mkdir(third_notrepo)

        paths = [first_repo, second_repo, third_notrepo]
        paths_returned = fsquery_adv_filter.filter_path_list_and(paths, [(fsquery_adv_filter.filter_is_repo, "not-used")])
        self.assertEqual(paths_returned, [first_repo, second_repo])

    def testFilterRepos_Or(self):

        first_repo = path_utils.concat_path(self.test_dir, "first")
        v, r = git_wrapper.init(self.test_dir, "first", True)
        if not v:
            self.fail(r)

        second_repo = path_utils.concat_path(self.test_dir, "second")
        v, r = git_wrapper.init(self.test_dir, "second", False)
        if not v:
            self.fail(r)

        third_notrepo = path_utils.concat_path(self.test_dir, "third")
        os.mkdir(third_notrepo)

        paths = [first_repo, second_repo, third_notrepo]
        paths_returned = fsquery_adv_filter.filter_path_list_or(paths, [(fsquery_adv_filter.filter_all_negative, "not-used"), (fsquery_adv_filter.filter_is_repo, "not-used")])
        self.assertEqual(paths_returned, [first_repo, second_repo])

        paths_returned = fsquery_adv_filter.filter_path_list_or(paths, [(fsquery_adv_filter.filter_all_positive, "not-used"), (fsquery_adv_filter.filter_is_repo, "not-used")])
        self.assertEqual(paths_returned, paths)

    def testFilterNotRepos_And(self):

        first_repo = path_utils.concat_path(self.test_dir, "first")
        v, r = git_wrapper.init(self.test_dir, "first", True)
        if not v:
            self.fail(r)

        second_repo = path_utils.concat_path(self.test_dir, "second")
        v, r = git_wrapper.init(self.test_dir, "second", False)
        if not v:
            self.fail(r)

        third_notrepo = path_utils.concat_path(self.test_dir, "third")
        os.mkdir(third_notrepo)

        paths = [first_repo, second_repo, third_notrepo]
        paths_returned = fsquery_adv_filter.filter_path_list_and(paths, [(fsquery_adv_filter.filter_is_not_repo, "not-used")])
        self.assertEqual(paths_returned, [third_notrepo])

    def testFilterReposMiddle_And(self):

        first_repo = path_utils.concat_path(self.test_dir, "first")
        v, r = git_wrapper.init(self.test_dir, "first", True)
        if not v:
            self.fail(r)

        first_repo_objects = path_utils.concat_path(first_repo, "objects")
        self.assertTrue( os.path.exists(first_repo_objects) )

        first_repo_subfolder = path_utils.concat_path(first_repo, "first_sub")
        os.mkdir(first_repo_subfolder)
        self.assertTrue( os.path.exists(first_repo_subfolder) )

        second_repo = path_utils.concat_path(self.test_dir, "second")
        v, r = git_wrapper.init(self.test_dir, "second", False)
        if not v:
            self.fail(r)

        third_notrepo = path_utils.concat_path(self.test_dir, "third")
        os.mkdir(third_notrepo)

        paths = [first_repo, first_repo_objects, first_repo_subfolder, second_repo, third_notrepo]
        paths_returned = fsquery_adv_filter.filter_path_list_and(paths, [(fsquery_adv_filter.filter_has_middle_repos, "not-used" )])
        self.assertEqual(paths_returned, [first_repo_objects, first_repo_subfolder])

    def testFilterReposNotMiddle_And(self):

        first_repo = path_utils.concat_path(self.test_dir, "first")
        v, r = git_wrapper.init(self.test_dir, "first", True)
        if not v:
            self.fail(r)

        first_repo_objects = path_utils.concat_path(first_repo, "objects")
        self.assertTrue( os.path.exists(first_repo_objects) )

        first_repo_subfolder = path_utils.concat_path(first_repo, "first_sub")
        os.mkdir(first_repo_subfolder)
        self.assertTrue( os.path.exists(first_repo_subfolder) )

        second_repo = path_utils.concat_path(self.test_dir, "second")
        v, r = git_wrapper.init(self.test_dir, "second", False)
        if not v:
            self.fail(r)

        third_notrepo = path_utils.concat_path(self.test_dir, "third")
        os.mkdir(third_notrepo)

        paths = [first_repo, first_repo_objects, first_repo_subfolder, second_repo, third_notrepo]
        paths_returned = fsquery_adv_filter.filter_path_list_and(paths, [(fsquery_adv_filter.filter_has_not_middle_repos, "not-used" )])
        self.assertEqual(paths_returned, [first_repo, second_repo, third_notrepo])

    def testFilterReposMiddle_Or(self):

        first_repo = path_utils.concat_path(self.test_dir, "first")
        v, r = git_wrapper.init(self.test_dir, "first", True)
        if not v:
            self.fail(r)

        first_repo_objects = path_utils.concat_path(first_repo, "objects")
        self.assertTrue( os.path.exists(first_repo_objects) )

        first_repo_subfolder = path_utils.concat_path(first_repo, "first_sub")
        os.mkdir(first_repo_subfolder)
        self.assertTrue( os.path.exists(first_repo_subfolder) )

        second_repo = path_utils.concat_path(self.test_dir, "second")
        v, r = git_wrapper.init(self.test_dir, "second", False)
        if not v:
            self.fail(r)

        third_notrepo = path_utils.concat_path(self.test_dir, "third")
        os.mkdir(third_notrepo)

        paths = [first_repo, first_repo_objects, first_repo_subfolder, second_repo, third_notrepo]
        paths_returned = fsquery_adv_filter.filter_path_list_or(paths, [(fsquery_adv_filter.filter_has_middle_repos, "not-used" )])
        self.assertEqual(paths_returned, [first_repo_objects, first_repo_subfolder])

    def testFilterReposNotMiddle_Or(self):

        first_repo = path_utils.concat_path(self.test_dir, "first")
        v, r = git_wrapper.init(self.test_dir, "first", True)
        if not v:
            self.fail(r)

        first_repo_objects = path_utils.concat_path(first_repo, "objects")
        self.assertTrue( os.path.exists(first_repo_objects) )

        first_repo_subfolder = path_utils.concat_path(first_repo, "first_sub")
        os.mkdir(first_repo_subfolder)
        self.assertTrue( os.path.exists(first_repo_subfolder) )

        second_repo = path_utils.concat_path(self.test_dir, "second")
        v, r = git_wrapper.init(self.test_dir, "second", False)
        if not v:
            self.fail(r)

        third_notrepo = path_utils.concat_path(self.test_dir, "third")
        os.mkdir(third_notrepo)

        paths = [first_repo, first_repo_objects, first_repo_subfolder, second_repo, third_notrepo]
        paths_returned = fsquery_adv_filter.filter_path_list_or(paths, [(fsquery_adv_filter.filter_has_not_middle_repos, "not-used" )])
        self.assertEqual(paths_returned, [first_repo, second_repo, third_notrepo])

    def testFilterLastEqual_And(self):

        paths = ["/user/home/file1.txt", "/user/home/file2.txt", "/user/home/file3.txt"]
        filters = [(fsquery_adv_filter.filter_all_positive, "not-used"), (fsquery_adv_filter.filter_is_last_equal_to, "file2.txt")]
        paths_returned = fsquery_adv_filter.filter_path_list_and(paths, filters)
        self.assertEqual(paths_returned, ["/user/home/file2.txt"])

    def testFilterLastEqual_Or(self):

        paths = ["/user/home/file1.txt", "/user/home/file2.txt", "/user/home/file3.txt"]
        filters = [(fsquery_adv_filter.filter_all_positive, "not-used"), (fsquery_adv_filter.filter_is_last_equal_to, "file2.txt")]
        paths_returned = fsquery_adv_filter.filter_path_list_or(paths, filters)
        self.assertEqual(paths_returned, paths)

    def testFilterLastEqualButAbortedByAllNegative_And(self):

        paths = ["/user/home/file1.txt", "/user/home/file2.txt", "/user/home/file3.txt"]
        filters = [(fsquery_adv_filter.filter_all_negative, "not-used"), (fsquery_adv_filter.filter_is_last_equal_to, "file2.txt")]
        paths_returned = fsquery_adv_filter.filter_path_list_and(paths, filters)
        self.assertEqual(paths_returned, [])

    def testFilterLastEqualButAbortedByAllNegative_Or(self):

        paths = ["/user/home/file1.txt", "/user/home/file2.txt", "/user/home/file3.txt"]
        filters = [(fsquery_adv_filter.filter_all_negative, "not-used"), (fsquery_adv_filter.filter_is_last_equal_to, "file2.txt")]
        paths_returned = fsquery_adv_filter.filter_path_list_or(paths, filters)
        self.assertEqual(paths_returned, ["/user/home/file2.txt"])

    def testFilterLastNotEqual_And(self):

        paths = ["/user/home/file1.txt", "/user/home/file2.txt", "/user/home/file3.txt"]
        filters = [(fsquery_adv_filter.filter_all_positive, "not-used"), (fsquery_adv_filter.filter_is_last_not_equal_to, "file2.txt")]
        paths_returned = fsquery_adv_filter.filter_path_list_and(paths, filters)
        self.assertEqual(paths_returned, ["/user/home/file1.txt", "/user/home/file3.txt"])

    def testFilterLastNotEqual_Or(self):

        paths = ["/user/home/file1.txt", "/user/home/file2.txt", "/user/home/file3.txt"]
        filters = [(fsquery_adv_filter.filter_all_negative, "not-used"), (fsquery_adv_filter.filter_is_last_not_equal_to, "file2.txt")]
        paths_returned = fsquery_adv_filter.filter_path_list_or(paths, filters)
        self.assertEqual(paths_returned, ["/user/home/file1.txt", "/user/home/file3.txt"])

    def testFilterPathExists_And(self):

        local_folder = path_utils.concat_path(self.test_dir, "local_folder")
        paths = ["/user/home/folder1", "/user/home/folder2", "/user/home/folder3", local_folder]
        filters = [(fsquery_adv_filter.filter_path_exists, "not-used")]
        paths_returned = fsquery_adv_filter.filter_path_list_and(paths, filters)
        self.assertEqual(paths_returned, [])

        os.mkdir(local_folder)
        self.assertTrue(os.path.exists(local_folder))

        paths_returned = fsquery_adv_filter.filter_path_list_and(paths, filters)
        self.assertEqual(paths_returned, [local_folder])

    def testFilterPathExists_Or(self):

        local_folder = path_utils.concat_path(self.test_dir, "local_folder")
        paths = ["/user/home/folder1", "/user/home/folder2", "/user/home/folder3", local_folder]
        filters = [(fsquery_adv_filter.filter_path_exists, "not-used")]
        paths_returned = fsquery_adv_filter.filter_path_list_or(paths, filters)
        self.assertEqual(paths_returned, [])

        os.mkdir(local_folder)
        self.assertTrue(os.path.exists(local_folder))

        paths_returned = fsquery_adv_filter.filter_path_list_or(paths, filters)
        self.assertEqual(paths_returned, [local_folder])

    def testFilterPathNotExists_And(self):

        local_folder = path_utils.concat_path(self.test_dir, "local_folder")
        paths = ["/user/home/folder1", "/user/home/folder2", "/user/home/folder3", local_folder]
        filters = [(fsquery_adv_filter.filter_path_not_exists, "not-used")]
        paths_returned = fsquery_adv_filter.filter_path_list_and(paths, filters)
        self.assertEqual(paths_returned, paths)

        os.mkdir(local_folder)
        self.assertTrue(os.path.exists(local_folder))

        paths_returned = fsquery_adv_filter.filter_path_list_and(paths, filters)
        self.assertEqual(paths_returned, ["/user/home/folder1", "/user/home/folder2", "/user/home/folder3"])

    def testFilterHasMiddlePieces1_And(self):

        paths = ["/user/home/sub/folder1", "/user/home/sub/folder2", "/user/home/sub/folder3", "/user"]
        filters = [(fsquery_adv_filter.filter_has_middle_pieces, ["/", "user"])]
        paths_returned = fsquery_adv_filter.filter_path_list_and(paths, filters)
        self.assertEqual(paths_returned, ["/user"])

    def testFilterHasMiddlePieces2_And(self):

        paths = ["/local/home/sub/folder1", "/user/home/sub/folder2", "/user/home/sub/folder3"]
        filters = [(fsquery_adv_filter.filter_has_middle_pieces, ["local"])]
        paths_returned = fsquery_adv_filter.filter_path_list_and(paths, filters)
        self.assertEqual(paths_returned, [])

    def testFilterHasMiddlePieces3_And(self):

        paths = ["/user/home/sub/folder1", "/user/home/soob/folder2", "/user/home/sub/folder3"]
        filters = [(fsquery_adv_filter.filter_has_middle_pieces, ["soob"])]
        paths_returned = fsquery_adv_filter.filter_path_list_and(paths, filters)
        self.assertEqual(paths_returned, [])

    def testFilterHasMiddlePieces4_And(self):

        paths = ["/user/home/sub/folder1", "/user/home/sub/folder2", "/user/home/sub/folder3"]
        filters = [(fsquery_adv_filter.filter_has_middle_pieces, ["*"])]
        paths_returned = fsquery_adv_filter.filter_path_list_and(paths, filters)
        self.assertEqual(paths_returned, paths)

    def testFilterHasMiddlePieces5_And(self):

        paths = ["/user/home/sub/folder1", "/user/home/sub/folder2", "/user/home/sub/folder3"]
        filters = [(fsquery_adv_filter.filter_has_middle_pieces, ["*", "*"])]
        paths_returned = fsquery_adv_filter.filter_path_list_and(paths, filters)
        self.assertEqual(paths_returned, paths)

    def testFilterHasMiddlePieces6_And(self):

        paths = ["/user/home/sub/folder1", "/user/home/soob/folder2", "/user/home/sub/folder3"]
        filters = [(fsquery_adv_filter.filter_has_middle_pieces, ["*", "soob", "*"])]
        paths_returned = fsquery_adv_filter.filter_path_list_and(paths, filters)
        self.assertEqual(paths_returned, ["/user/home/soob/folder2"])

    def testFilterHasMiddlePieces7_And(self):
        paths = ["/user/home/sub/folder1", "/user/home/soob/folder2", "/user/home/sub/folder3", "/user/home/sub/folder4/soob", "/user/home/soob/folder5"]
        filters = [(fsquery_adv_filter.filter_has_middle_pieces, ["*", "soob"])]
        paths_returned = fsquery_adv_filter.filter_path_list_and(paths, filters)
        self.assertEqual(paths_returned, ["/user/home/sub/folder4/soob"])

    def testFilterHasMiddlePieces8_And(self):
        paths = ["/user/home/sub/folder1", "/user/home/soob/folder2", "/user/home/sub/folder3", "/user/home/soob/folder4/soob/morestuff", "/user/home/soob/folder5/soob/another/yetmore/soob/excess", "/user/home/soob/folder6/soob/another/yetmore/soob/excess/soob", "/user/home/soob/folder_x/excess/soob", "soob/folder_y/excess/soob"]
        filters = [(fsquery_adv_filter.filter_has_middle_pieces, ["soob", "*", "soob"])]
        paths_returned = fsquery_adv_filter.filter_path_list_and(paths, filters)
        self.assertEqual(paths_returned, ["soob/folder_y/excess/soob"])

    def testFilterHasMiddlePieces9_And(self):
        paths = ["/user/home/sub/folder1", "sub/folder2/bus"]
        filters = [(fsquery_adv_filter.filter_has_middle_pieces, ["sub", "*", "bus"])]
        paths_returned = fsquery_adv_filter.filter_path_list_and(paths, filters)
        self.assertEqual(paths_returned, ["sub/folder2/bus"])

    def testFilterHasMiddlePieces10_And(self):
        paths = ["/user/home/sub/folder1", "sub/sub"]
        filters = [(fsquery_adv_filter.filter_has_middle_pieces, ["sub", "*", "sub"])]
        paths_returned = fsquery_adv_filter.filter_path_list_and(paths, filters)
        self.assertEqual(paths_returned, ["sub/sub"])

    def testFilterHasMiddlePieces11_And(self):

        paths = ["/user/home/sub/folder1", "/user/home/soob/folder2", "/user/home/sub/folder3"]
        filters = [(fsquery_adv_filter.filter_has_middle_pieces, ["*", "nothere"])]
        paths_returned = fsquery_adv_filter.filter_path_list_and(paths, filters)
        self.assertEqual(paths_returned, [])

    def testFilterHasMiddlePieces12_And(self):

        paths = ["/user/home/sub/extra/folder1", "/user/home/sub/extra", "/user/home/sub/extra/folder2", "/user/home/sub/exter/folder3", "/user/home/sub/extra/more/extra"]
        filters = [(fsquery_adv_filter.filter_has_middle_pieces, ["*", "home", "*", "extra"])]
        paths_returned = fsquery_adv_filter.filter_path_list_and(paths, filters)
        self.assertEqual(paths_returned, ["/user/home/sub/extra"])

    def testFilterHasMiddlePieces13_And(self):

        paths = ["/system/home/sub/extra/folder0", "/user/home/sub/extra/folder1", "/user/home/sub/extra/folder2", "/user/home/sub/exter/folder3"]
        filters = [(fsquery_adv_filter.filter_has_middle_pieces, ["*", "user", "*", "extra", "*"])]
        paths_returned = fsquery_adv_filter.filter_path_list_and(paths, filters)
        self.assertEqual(paths_returned, ["/user/home/sub/extra/folder1", "/user/home/sub/extra/folder2"])

    def testFilterHasMiddlePieces14_And(self):

        paths = ["/system/home1", "/system/home2", "/user/home", "/system"]
        filters = [(fsquery_adv_filter.filter_has_middle_pieces, ["/", "system", "*"])]
        paths_returned = fsquery_adv_filter.filter_path_list_and(paths, filters)
        self.assertEqual(paths_returned, ["/system/home1", "/system/home2", "/system"])

    def testFilterHasMiddlePieces15_And(self):

        paths = ["/system/home/sub/extra/spaced part/folder0", "/system/home/sub/extra/spaced part/folder1", "/user/home/sub/extra/spaced part/folder2", "/user/home/sub/exter/spaced part/folder3"]
        filters = [(fsquery_adv_filter.filter_has_middle_pieces, ["*", "spaced part", "folder1"])]
        paths_returned = fsquery_adv_filter.filter_path_list_and(paths, filters)
        self.assertEqual(paths_returned, ["/system/home/sub/extra/spaced part/folder1"])

    def testFilterHasMiddlePieces16_And(self):

        paths = ["one/two/three", "one/folder/three", "another/extra/more", "yetmore/folder", "folder", "folder/whatever"]
        filters = [(fsquery_adv_filter.filter_has_middle_pieces, ["*", "folder", "*"])]
        paths_returned = fsquery_adv_filter.filter_path_list_and(paths, filters)
        self.assertEqual(paths_returned, ["one/folder/three", "yetmore/folder", "folder", "folder/whatever"])

    def testFilterHasNotMiddlePieces1_And(self):

        paths = ["/user/home/sub/folder1", "/user/home/sub/folder2", "/user/home/sub/folder3", "/user"]
        filters = [(fsquery_adv_filter.filter_has_not_middle_pieces, ["/", "user"])]
        paths_returned = fsquery_adv_filter.filter_path_list_and(paths, filters)
        self.assertEqual(paths_returned, ["/user/home/sub/folder1", "/user/home/sub/folder2", "/user/home/sub/folder3"])

    def testFilterHasNotMiddlePieces2_And(self):

        paths = ["/local/home/sub/folder1", "/user/home/sub/folder2", "/user/home/sub/folder3"]
        filters = [(fsquery_adv_filter.filter_has_not_middle_pieces, ["local"])]
        paths_returned = fsquery_adv_filter.filter_path_list_and(paths, filters)
        self.assertEqual(paths_returned, paths)

    def testFilterHasNotMiddlePieces3_And(self):

        paths = ["/user/home/sub/folder1", "/user/home/soob/folder2", "/user/home/sub/folder3"]
        filters = [(fsquery_adv_filter.filter_has_not_middle_pieces, ["soob"])]
        paths_returned = fsquery_adv_filter.filter_path_list_and(paths, filters)
        self.assertEqual(paths_returned, paths)

    def testFilterHasNotMiddlePieces4_And(self):

        paths = ["/user/home/sub/folder1", "/user/home/sub/folder2", "/user/home/sub/folder3"]
        filters = [(fsquery_adv_filter.filter_has_not_middle_pieces, ["*"])]
        paths_returned = fsquery_adv_filter.filter_path_list_and(paths, filters)
        self.assertEqual(paths_returned, [])

    def testFilterHasNotMiddlePieces5_And(self):

        paths = ["/user/home/sub/folder1", "/user/home/sub/folder2", "/user/home/sub/folder3"]
        filters = [(fsquery_adv_filter.filter_has_not_middle_pieces, ["*", "*"])]
        paths_returned = fsquery_adv_filter.filter_path_list_and(paths, filters)
        self.assertEqual(paths_returned, [])

    def testFilterHasNotMiddlePieces6_And(self):

        paths = ["/user/home/sub/folder1", "/user/home/soob/folder2", "/user/home/sub/folder3"]
        filters = [(fsquery_adv_filter.filter_has_not_middle_pieces, ["*", "soob", "*"])]
        paths_returned = fsquery_adv_filter.filter_path_list_and(paths, filters)
        self.assertEqual(paths_returned, ["/user/home/sub/folder1", "/user/home/sub/folder3"])

    def testFilterHasNotMiddlePieces7_And(self):
        paths = ["/user/home/sub/folder1", "/user/home/soob/folder2", "/user/home/sub/folder3", "/user/home/sub/folder4/soob", "/user/home/soob/folder5"]
        filters = [(fsquery_adv_filter.filter_has_not_middle_pieces, ["*", "soob"])]
        paths_returned = fsquery_adv_filter.filter_path_list_and(paths, filters)
        self.assertEqual(paths_returned, ["/user/home/sub/folder1", "/user/home/soob/folder2", "/user/home/sub/folder3", "/user/home/soob/folder5"])

    def testFilterHasNotMiddlePieces8_And(self):
        paths = ["/user/home/sub/folder1", "/user/home/soob/folder2", "/user/home/sub/folder3", "/user/home/soob/folder4/soob/morestuff", "/user/home/soob/folder5/soob/another/yetmore/soob/excess", "/user/home/soob/folder6/soob/another/yetmore/soob/excess/soob", "/user/home/soob/folder_x/excess/soob", "soob/folder_y/excess/soob"]
        filters = [(fsquery_adv_filter.filter_has_not_middle_pieces, ["soob", "*", "soob"])]
        paths_returned = fsquery_adv_filter.filter_path_list_and(paths, filters)
        self.assertEqual(paths_returned, ["/user/home/sub/folder1", "/user/home/soob/folder2", "/user/home/sub/folder3", "/user/home/soob/folder4/soob/morestuff", "/user/home/soob/folder5/soob/another/yetmore/soob/excess", "/user/home/soob/folder6/soob/another/yetmore/soob/excess/soob", "/user/home/soob/folder_x/excess/soob"])

    def testFilterHasNotMiddlePieces9_And(self):
        paths = ["/user/home/sub/folder1", "sub/folder2/bus"]
        filters = [(fsquery_adv_filter.filter_has_not_middle_pieces, ["sub", "*", "bus"])]
        paths_returned = fsquery_adv_filter.filter_path_list_and(paths, filters)
        self.assertEqual(paths_returned, ["/user/home/sub/folder1"])

    def testFilterHasNotMiddlePieces10_And(self):
        paths = ["/user/home/sub/folder1", "sub/sub"]
        filters = [(fsquery_adv_filter.filter_has_not_middle_pieces, ["sub", "*", "sub"])]
        paths_returned = fsquery_adv_filter.filter_path_list_and(paths, filters)
        self.assertEqual(paths_returned, ["/user/home/sub/folder1"])

    def testFilterHasNotMiddlePieces11_And(self):

        paths = ["/user/home/sub/folder1", "/user/home/soob/folder2", "/user/home/sub/folder3"]
        filters = [(fsquery_adv_filter.filter_has_not_middle_pieces, ["*", "nothere"])]
        paths_returned = fsquery_adv_filter.filter_path_list_and(paths, filters)
        self.assertEqual(paths_returned, paths)

    def testFilterHasNotMiddlePieces12_And(self):

        paths = ["/user/home/sub/extra/folder1", "/user/home/sub/extra", "/user/home/sub/extra/folder2", "/user/home/sub/exter/folder3", "/user/home/sub/extra/more/extra"]
        filters = [(fsquery_adv_filter.filter_has_not_middle_pieces, ["*", "home", "*", "extra"])]
        paths_returned = fsquery_adv_filter.filter_path_list_and(paths, filters)
        self.assertEqual(paths_returned, ["/user/home/sub/extra/folder1", "/user/home/sub/extra/folder2", "/user/home/sub/exter/folder3", "/user/home/sub/extra/more/extra"])

    def testFilterHasNotMiddlePieces13_And(self):

        paths = ["/system/home/sub/extra/folder0", "/user/home/sub/extra/folder1", "/user/home/sub/extra/folder2", "/user/home/sub/exter/folder3"]
        filters = [(fsquery_adv_filter.filter_has_not_middle_pieces, ["/", "user", "*", "extra", "*"])]
        paths_returned = fsquery_adv_filter.filter_path_list_and(paths, filters)
        self.assertEqual(paths_returned, ["/system/home/sub/extra/folder0", "/user/home/sub/exter/folder3"])

    def testFilterHasNotMiddlePieces14_And(self):

        paths = ["/system/home1", "/system/home2", "/user/home", "/system"]
        filters = [(fsquery_adv_filter.filter_has_not_middle_pieces, ["/", "system", "*"])]
        paths_returned = fsquery_adv_filter.filter_path_list_and(paths, filters)
        self.assertEqual(paths_returned, ["/user/home"])

    def testFilterHasNotMiddlePieces15_And(self):

        paths = ["/system/home/sub/extra/spaced part/folder0", "/system/home/sub/extra/spaced part/folder1", "/user/home/sub/extra/spaced part/folder2", "/user/home/sub/exter/spaced part/folder3"]
        filters = [(fsquery_adv_filter.filter_has_not_middle_pieces, ["*", "spaced part", "folder1"])]
        paths_returned = fsquery_adv_filter.filter_path_list_and(paths, filters)
        self.assertEqual(paths_returned, ["/system/home/sub/extra/spaced part/folder0", "/user/home/sub/extra/spaced part/folder2", "/user/home/sub/exter/spaced part/folder3"])

    def testFilterHasNotMiddlePieces16_And(self):

        paths = ["one/two/three", "one/folder/three", "another/extra/more", "yetmore/folder", "folder", "folder/whatever"]
        filters = [(fsquery_adv_filter.filter_has_not_middle_pieces, ["*", "folder", "*"])]
        paths_returned = fsquery_adv_filter.filter_path_list_and(paths, filters)
        self.assertEqual(paths_returned, ["one/two/three", "another/extra/more"])

    def testFilterExtensionIs_Or(self):

        paths = ["one/two/three.txt", "one/folder/three.png", "another/extra/more", "folder/whatever.nfo"]
        filters = [(fsquery_adv_filter.filter_extension_is, ["txt"])]
        paths_returned = fsquery_adv_filter.filter_path_list_or(paths, filters)
        self.assertEqual(paths_returned, ["one/two/three.txt"])

    def testFilterExtensionIs_And(self):

        paths = ["one/two/three.txt", "one/folder/three.png", "another/extra/more", "folder/whatever.nfo"]
        filters = [(fsquery_adv_filter.filter_extension_is, ["txt"])]
        paths_returned = fsquery_adv_filter.filter_path_list_and(paths, filters)
        self.assertEqual(paths_returned, ["one/two/three.txt"])

    def testFilterExtensionIsNot_Or(self):

        paths = ["one/two/three.txt", "one/folder/three.png", "another/extra/more", "folder/whatever.nfo"]
        filters = [(fsquery_adv_filter.filter_extension_is_not, ["txt"])]
        paths_returned = fsquery_adv_filter.filter_path_list_or(paths, filters)
        self.assertEqual(paths_returned, ["one/folder/three.png", "another/extra/more", "folder/whatever.nfo"])

    def testFilterExtensionIsNot_And(self):

        paths = ["one/two/three.txt", "one/folder/three.png", "another/extra/more", "folder/whatever.nfo"]
        filters = [(fsquery_adv_filter.filter_extension_is_not, ["png"])]
        paths_returned = fsquery_adv_filter.filter_path_list_and(paths, filters)
        self.assertEqual(paths_returned, ["one/two/three.txt", "another/extra/more", "folder/whatever.nfo"])

if __name__ == "__main__":
    unittest.main()
