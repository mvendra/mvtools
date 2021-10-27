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
import collect_git_patch
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
        self.storage_path = path_utils.concat_path(self.test_dir, "storage_path")
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

        v, r = apply_git_patch.apply_git_patch(self.nonexistent, [], [], [], [])
        self.assertFalse(v)

        v, r = apply_git_patch.apply_git_patch(self.nonrepo, [], [], [], [])
        self.assertFalse(v)

    def testApplyGitApplyUnversionedFail(self):

        first_sub = path_utils.concat_path(self.first_repo, "sub")
        os.mkdir(first_sub)
        self.assertTrue(os.path.exists(first_sub))
        second_sub = path_utils.concat_path(self.second_repo, "sub")
        os.mkdir(second_sub)
        self.assertTrue(os.path.exists(second_sub))

        first_sub_file4 = path_utils.concat_path(first_sub, "file4.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_sub_file4, "first, sub, file4, contents"))
        second_sub_file4 = path_utils.concat_path(second_sub, "file4.txt")
        self.assertTrue(create_and_write_file.create_file_contents(second_sub_file4, "second, sub, file4, contents"))

        first_file5 = path_utils.concat_path(self.first_repo, "file5.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_file5, "first, file5, contents"))
        second_file5 = path_utils.concat_path(self.second_repo, "file5.txt")
        self.assertFalse( os.path.exists(second_file5) )

        v, r = collect_git_patch.collect_git_patch_unversioned(self.first_repo, self.storage_path, "include", [], [])
        self.assertTrue(v)
        generated_patches = r

        unversioned_param = []
        unversioned_base = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned")
        for gp in generated_patches:
            unversioned_param.append( (unversioned_base, gp) )
        v, r = apply_git_patch.apply_git_patch_unversioned(self.second_repo, unversioned_param)
        self.assertFalse(v)

    def testApplyGitApplyUnversioned(self):

        first_sub = path_utils.concat_path(self.first_repo, "sub")
        os.mkdir(first_sub)
        self.assertTrue(os.path.exists(first_sub))
        second_sub = path_utils.concat_path(self.second_repo, "sub")
        self.assertFalse(os.path.exists(second_sub))

        first_sub_file4 = path_utils.concat_path(first_sub, "file4.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_sub_file4, "first, sub, file4, contents"))
        second_sub_file4 = path_utils.concat_path(second_sub, "file4.txt")
        self.assertFalse(os.path.exists(second_sub_file4))

        first_file5 = path_utils.concat_path(self.first_repo, "file5.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_file5, "first, file5, contents"))
        second_file5 = path_utils.concat_path(self.second_repo, "file5.txt")
        self.assertFalse( os.path.exists(second_file5) )

        v, r = collect_git_patch.collect_git_patch_unversioned(self.first_repo, self.storage_path, "include", [], [])
        self.assertTrue(v)
        generated_patches = r

        unversioned_param = []
        unversioned_base = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned")
        for gp in generated_patches:
            unversioned_param.append( (unversioned_base, gp) )
        v, r = apply_git_patch.apply_git_patch_unversioned(self.second_repo, unversioned_param)
        self.assertTrue(v)

        self.assertTrue(os.path.exists(second_sub))
        self.assertTrue(os.path.exists(second_sub_file4))
        self.assertTrue( os.path.exists(second_file5) )

    def testApplyGitPatchHead(self):

        second_file1 = path_utils.concat_path(self.second_repo, "file1.txt")
        self.assertTrue(os.path.exists(second_file1))

        with open(self.first_file1, "a") as f:
            f.write("more stuff")

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path, "include", [], [])
        self.assertTrue(v)
        generated_patches = [r]

        v, r = apply_git_patch.apply_git_patch_head(self.second_repo, generated_patches)
        self.assertTrue(v)

        contents = ""
        with open(second_file1, "r") as f:
            contents = f.read()
        self.assertTrue("more stuff" in contents)

    def testApplyGitPatchStaged(self):

        second_file1 = path_utils.concat_path(self.second_repo, "file1.txt")
        self.assertTrue(os.path.exists(second_file1))

        with open(self.first_file1, "a") as f:
            f.write("more stuff")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = collect_git_patch.collect_git_patch_staged(self.first_repo, self.storage_path, "include", [], [])
        self.assertTrue(v)
        generated_patches = [r]

        v, r = apply_git_patch.apply_git_patch_staged(self.second_repo, generated_patches)
        self.assertTrue(v)

        contents = ""
        with open(second_file1, "r") as f:
            contents = f.read()
        self.assertTrue("more stuff" in contents)

        v, r = git_lib.get_staged_files(self.second_repo)
        self.assertTrue(v)
        sf = r

        self.assertTrue(sf is not None)
        self.assertTrue(second_file1 in sf)

    def testApplyGitPatchStash(self):

        with open(self.first_file1, "a") as f:
            f.write("more stuff")

        v, r = git_lib.get_stash_list(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = git_wrapper.stash(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_stash_list(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        v, r = git_lib.get_stash_list(self.second_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = collect_git_patch.collect_git_patch_stash(self.first_repo, self.storage_path, -1)
        self.assertTrue(v)
        generated_patches = r

        v, r = apply_git_patch.apply_git_patch_stash(self.second_repo, generated_patches)
        self.assertTrue(v)

        v, r = git_lib.get_stash_list(self.second_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

if __name__ == '__main__':
    unittest.main()
