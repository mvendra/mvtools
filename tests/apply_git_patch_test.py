#!/usr/bin/env python3

import sys
import os
import shutil
import unittest

import mvtools_test_fixture
import git_test_fixture
import create_and_write_file
import path_utils

import git_wrapper
import git_lib
import apply_git_patch

class ApplyGitPatchTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("apply_git_patch_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        self.nonexistent = path_utils.concat_path(self.test_dir, "nonexistent")

        self.nonrepo = path_utils.concat_path(self.test_dir, "nonrepo")
        os.mkdir(self.nonrepo)

        # storage path
        self.storage_path = path_utils.concat_path(self.test_dir, "collect_patch_git_storage")
        os.mkdir(self.storage_path)

        # first repo
        self.first_repo = path_utils.concat_path(self.test_dir, "first")
        v, r = git_wrapper.init(self.test_dir, "first", False)
        if not v:
            return v, r

        self.first_file1 = path_utils.concat_path(self.first_repo, "file1.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file1.txt", "first-file1-content", "first-file1-msg")
        if not v:
            return v, r

        self.first_file2 = path_utils.concat_path(self.first_repo, "file2.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file2.txt", "first-file2-content", "first-file2-msg")
        if not v:
            return v, r

        self.first_file3 = path_utils.concat_path(self.first_repo, "file3.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file3.txt", "first-file3-content", "first-file3-msg")
        if not v:
            return v, r

        # second repo - clone of first
        self.second_repo = path_utils.concat_path(self.test_dir, "second")
        v, r = git_wrapper.clone(self.first_repo, self.second_repo, "origin")
        if not v:
            return v, r

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    """
    # mvtodo: maybe I should keep this. ifso, then (re)import fsquery
    def get_patches_in_order(self, path, repo_path):

        ret = []
        patches_ranked = {}

        patches = fsquery.makecontentlist(path_utils.concat_path(path, repo_path), False, True, False, False, False, True, None)
        for p in patches:
            min_s = 9
            pn = path_utils.basename_filtered(p)
            pi = pn.find("_", min_s)
            if pi == -1:
                return None
            rank = pn[min_s:pi]
            patches_ranked[rank] = p

        for p in sorted(patches_ranked.keys()):
            ret.append(patches_ranked[p])

        return ret
    """

    def testApplyGitPatchBasicChecks(self):

        v, r = apply_git_patch.apply_git_patch(self.nonexistent, self.second_repo, False, False, False, False, 0)
        self.assertFalse(v)

        v, r = apply_git_patch.apply_git_patch(self.first_repo, self.nonexistent, False, False, False, False, 0)
        self.assertFalse(v)

        v, r = apply_git_patch.apply_git_patch(self.nonrepo, self.second_repo, False, False, False, False, 0)
        self.assertFalse(v)

        v, r = apply_git_patch.apply_git_patch(self.first_repo, self.nonrepo, False, False, False, False, 0)
        self.assertFalse(v)

        v, r = apply_git_patch.apply_git_patch(self.first_repo, self.second_repo, False, False, False, False, 0)
        self.assertTrue(v)

    def testApplyGitPatchStash1(self):

        with open(self.first_file1, "a") as f:
            f.write("latest1")

        v, r = git_wrapper.stash(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_stash_list(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        v, r = git_lib.get_stash_list(self.second_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = apply_git_patch.apply_git_patch_stash(self.storage_path, self.first_repo, self.second_repo)
        self.assertTrue(v)

        v, r = git_lib.get_stash_list(self.second_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

    def testApplyGitPatchStash2(self):

        with open(self.first_file1, "a") as f:
            f.write("latest1")

        v, r = git_wrapper.stash(self.first_repo)
        self.assertTrue(v)

        with open(self.first_file2, "a") as f:
            f.write("latest2")

        v, r = git_wrapper.stash(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_stash_list(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)

        v, r = git_lib.get_stash_list(self.second_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = apply_git_patch.apply_git_patch_stash(self.storage_path, self.first_repo, self.second_repo)
        self.assertTrue(v)

        v, r = git_lib.get_stash_list(self.second_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)

    def testApplyGitPatchPrevious1(self):

        with open(self.first_file1, "a") as f:
            f.write("latest1")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.first_repo, "newmsg1")
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertTrue(r)

        v, r = git_lib.is_head_clear(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(r)

        v, r = apply_git_patch.apply_git_patch_previous(self.storage_path, self.first_repo, self.second_repo, 1)
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.second_repo)
        self.assertTrue(v)
        self.assertFalse(r)

    def testApplyGitPatchPrevious2(self):

        with open(self.first_file1, "a") as f:
            f.write("latest1")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.first_repo, "newmsg1")
        self.assertTrue(v)

        with open(self.first_file2, "a") as f:
            f.write("latest2")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.first_repo, "newmsg2")
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertTrue(r)

        v, r = git_lib.is_head_clear(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(r)

        v, r = apply_git_patch.apply_git_patch_previous(self.storage_path, self.first_repo, self.second_repo, 2)
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.second_repo)
        self.assertTrue(v)
        self.assertFalse(r)

if __name__ == '__main__':
    unittest.main()
