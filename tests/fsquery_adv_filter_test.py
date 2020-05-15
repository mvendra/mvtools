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

def func_all_positive(path, params):
    return True

def func_all_negative(path, params):
    return False

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

        self.assertEqual(fsquery_adv_filter.filter_path_list([], [(1, 2)]), [])

        self.assertEqual(fsquery_adv_filter.filter_path_list("string", []), None)
        self.assertEqual(fsquery_adv_filter.filter_path_list(None, []), None)
        self.assertEqual(fsquery_adv_filter.filter_path_list([], "string"), None)
        self.assertEqual(fsquery_adv_filter.filter_path_list([], None), None)
        self.assertEqual(fsquery_adv_filter.filter_path_list([], [(1)]), None)
        self.assertEqual(fsquery_adv_filter.filter_path_list([], [(1, 2, 3)]), None)

    def testFilterBasic(self):

        paths = ["/user/home/file1.txt", "/user/home/file2.txt", "/user/home/file3.txt"]
        paths_returned = fsquery_adv_filter.filter_path_list(paths, [(func_save_context, "test-filter-basic")])
        self.assertEqual(paths_returned, paths)
        self.assertEqual(escape_context_1, ["/user/home/file1.txt@test-filter-basic", "/user/home/file2.txt@test-filter-basic", "/user/home/file3.txt@test-filter-basic"])

    def testFilterNegative(self):

        paths = ["/user/home/file1.txt", "/user/home/file2.txt", "/user/home/file3.txt"]
        paths_returned = fsquery_adv_filter.filter_path_list(paths, [(func_all_negative, "test-filter-basic")])
        self.assertEqual(paths_returned, [])

    def testFilterRepos(self):

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
        paths_returned = fsquery_adv_filter.filter_path_list(paths, [(fsquery_adv_filter.filter_is_repo, "not-used")])
        self.assertEqual(paths_returned, [first_repo, second_repo])

    def testFilterLastEqual(self):

        paths = ["/user/home/file1.txt", "/user/home/file2.txt", "/user/home/file3.txt"]
        filters = [(func_all_positive, "not-used"), (fsquery_adv_filter.filter_is_last_equal_to, "file2.txt")]
        paths_returned = fsquery_adv_filter.filter_path_list(paths, filters)
        self.assertEqual(paths_returned, ["/user/home/file2.txt"])

    def testFilterLastEqualButAbortedByAllNegative(self):

        paths = ["/user/home/file1.txt", "/user/home/file2.txt", "/user/home/file3.txt"]
        filters = [(func_all_negative, "not-used"), (fsquery_adv_filter.filter_is_last_equal_to, "file2.txt")]
        paths_returned = fsquery_adv_filter.filter_path_list(paths, filters)
        self.assertEqual(paths_returned, [])

    def testFilterLastNotEqual(self):

        paths = ["/user/home/file1.txt", "/user/home/file2.txt", "/user/home/file3.txt"]
        filters = [(func_all_positive, "not-used"), (fsquery_adv_filter.filter_is_last_not_equal_to, "file2.txt")]
        paths_returned = fsquery_adv_filter.filter_path_list(paths, filters)
        self.assertEqual(paths_returned, ["/user/home/file1.txt", "/user/home/file3.txt"])

if __name__ == '__main__':
    unittest.main()
