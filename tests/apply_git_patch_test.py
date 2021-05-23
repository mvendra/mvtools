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

    def testApplyGitPatchStashFail(self):

        v, r = git_lib.get_stash_list(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = git_lib.get_stash_list(self.second_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = apply_git_patch.apply_git_patch_stash(self.storage_path, self.first_repo, self.second_repo)
        self.assertFalse(v)

        v, r = git_lib.get_stash_list(self.second_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

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

    def testApplyGitPatchPreviousFail1(self):

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertTrue(r)

        v, r = git_lib.is_head_clear(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(r)

        v, r = apply_git_patch.apply_git_patch_previous(self.storage_path, self.first_repo, self.second_repo, 4)
        self.assertFalse(v)

        v, r = git_lib.is_head_clear(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(r)

    def testApplyGitPatchPreviousFail2(self):

        empty_repo = path_utils.concat_path(self.test_dir, "empty_repo")
        v, r = git_wrapper.init(self.test_dir, "empty_repo", False)
        self.assertTrue(v)

        empty_repo_clone = path_utils.concat_path(self.test_dir, "empty_repo_clone")
        v, r = git_wrapper.clone(empty_repo, empty_repo_clone, "origin")
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(empty_repo)
        self.assertTrue(v)
        self.assertTrue(r)

        v, r = git_lib.is_head_clear(empty_repo_clone)
        self.assertTrue(v)
        self.assertTrue(r)

        v, r = apply_git_patch.apply_git_patch_previous(self.storage_path, empty_repo, empty_repo_clone, 1)
        self.assertFalse(v)

        v, r = git_lib.is_head_clear(empty_repo_clone)
        self.assertTrue(v)
        self.assertTrue(r)

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

    def testApplyGitPatchStagedFail(self):

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertTrue(r)

        v, r = git_lib.is_head_clear(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(r)

        v, r = apply_git_patch.apply_git_patch_staged(self.storage_path, self.first_repo, self.second_repo)
        self.assertFalse(v)

        v, r = git_lib.is_head_clear(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(r)

    def testApplyGitPatchStaged1(self):

        with open(self.first_file1, "a") as f:
            f.write("latest1")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(r)

        v, r = apply_git_patch.apply_git_patch_staged(self.storage_path, self.first_repo, self.second_repo)
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.second_repo)
        self.assertTrue(v)
        self.assertFalse(r)

    def testApplyGitPatchStaged2(self):

        with open(self.first_file1, "a") as f:
            f.write("latest1")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        with open(self.first_file2, "a") as f:
            f.write("latest2")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(r)

        v, r = apply_git_patch.apply_git_patch_staged(self.storage_path, self.first_repo, self.second_repo)
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.second_repo)
        self.assertTrue(v)
        self.assertFalse(r)

    def testApplyGitPatchHeadFail(self):

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertTrue(r)

        v, r = git_lib.is_head_clear(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(r)

        v, r = apply_git_patch.apply_git_patch_staged(self.storage_path, self.first_repo, self.second_repo)
        self.assertFalse(v)

        v, r = git_lib.is_head_clear(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(r)

    def testApplyGitPatchHead1(self):

        with open(self.first_file1, "a") as f:
            f.write("latest1")

        v, r = git_lib.is_head_clear(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(r)

        v, r = apply_git_patch.apply_git_patch_head(self.storage_path, self.first_repo, self.second_repo)
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.second_repo)
        self.assertTrue(v)
        self.assertFalse(r)

    def testApplyGitPatchHead2(self):

        with open(self.first_file1, "a") as f:
            f.write("latest1")

        with open(self.first_file2, "a") as f:
            f.write("latest2")

        v, r = git_lib.is_head_clear(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(r)

        v, r = apply_git_patch.apply_git_patch_head(self.storage_path, self.first_repo, self.second_repo)
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.second_repo)
        self.assertTrue(v)
        self.assertFalse(r)

    def testApplyGitPatchUnversionedFail(self):

        first_file4 = path_utils.concat_path(self.first_repo, "file4.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_file4, "file4-contents"))

        first_sub1 = path_utils.concat_path(self.first_repo, "sub1")
        os.mkdir(first_sub1)

        first_sub1_sub2 = path_utils.concat_path(first_sub1, "sub2")
        os.mkdir(first_sub1_sub2)

        first_sub1_sub2_file5 = path_utils.concat_path(first_sub1_sub2, "file5.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_sub1_sub2_file5, "file5-contents"))

        v, r = git_lib.is_head_clear(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(r)

        second_file4 = path_utils.concat_path(self.second_repo, "file4.txt")
        second_sub1 = path_utils.concat_path(self.second_repo, "sub1")
        second_sub1_sub2 = path_utils.concat_path(second_sub1, "sub2")
        second_sub1_sub2_file5 = path_utils.concat_path(second_sub1_sub2, "file5.txt")

        self.assertTrue(create_and_write_file.create_file_contents(second_file4, "file4-contents-dupe"))

        v, r = apply_git_patch.apply_git_patch_unversioned(self.storage_path, self.first_repo, self.second_repo)
        self.assertFalse(v)

        v, r = git_lib.is_head_clear(self.second_repo)
        self.assertTrue(v)
        self.assertFalse(r)

        self.assertTrue(os.path.exists(second_file4))
        self.assertFalse(os.path.exists(second_sub1))
        self.assertFalse(os.path.exists(second_sub1_sub2))
        self.assertFalse(os.path.exists(second_sub1_sub2_file5))

    def testApplyGitPatchUnversioned(self):

        first_file4 = path_utils.concat_path(self.first_repo, "file4.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_file4, "file4-contents"))

        first_sub1 = path_utils.concat_path(self.first_repo, "sub1")
        os.mkdir(first_sub1)

        first_sub1_sub2 = path_utils.concat_path(first_sub1, "sub2")
        os.mkdir(first_sub1_sub2)

        first_sub1_sub2_file5 = path_utils.concat_path(first_sub1_sub2, "file5.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_sub1_sub2_file5, "file5-contents"))

        v, r = git_lib.is_head_clear(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(r)

        v, r = apply_git_patch.apply_git_patch_unversioned(self.storage_path, self.first_repo, self.second_repo)
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.second_repo)
        self.assertTrue(v)
        self.assertFalse(r)

        second_file4 = path_utils.concat_path(self.second_repo, "file4.txt")
        second_sub1 = path_utils.concat_path(self.second_repo, "sub1")
        second_sub1_sub2 = path_utils.concat_path(second_sub1, "sub2")
        second_sub1_sub2_file5 = path_utils.concat_path(second_sub1_sub2, "file5.txt")

        self.assertTrue(os.path.exists(second_file4))
        self.assertTrue(os.path.exists(second_sub1))
        self.assertTrue(os.path.exists(second_sub1_sub2))
        self.assertTrue(os.path.exists(second_sub1_sub2_file5))

if __name__ == '__main__':
    unittest.main()
