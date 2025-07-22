#!/usr/bin/env python3

import sys
import os
import shutil
import unittest

import path_utils
import fsquery
import getcontents
import create_and_write_file
import open_and_update_file

import mvtools_test_fixture
import git_test_fixture
import git_wrapper
import git_lib

import collect_git_patch

class CollectGitPatchTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("collect_git_patch_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        self.nonexistent = path_utils.concat_path(self.test_dir, "nonexistent")

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

        # second repo
        self.second_repo = path_utils.concat_path(self.test_dir, "second")
        v, r = git_wrapper.init(self.test_dir, "second", False)
        if not v:
            return v, r

        self.second_file1 = path_utils.concat_path(self.second_repo, "file1.txt")
        v, r = git_test_fixture.git_createAndCommit(self.second_repo, "file1.txt", "second-file1-content", "second-file1-msg")
        if not v:
            return v, r

        # set second as first's submodule
        v, r = git_wrapper.submodule_add(self.second_repo, self.first_repo)
        if not v:
            return v, r

        self.second_sub = path_utils.concat_path(self.first_repo, path_utils.basename_filtered(self.second_repo))
        self.second_sub_file1 = path_utils.concat_path(self.second_sub, "file1.txt")

        v, r = git_wrapper.commit(self.first_repo, "first-adding-submodule")
        if not v:
            return v, r

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def get_patches_in_order(self, path, repo_path):

        ret = []
        patches_ranked = {}

        v, r = fsquery.makecontentlist(path_utils.concat_path(path, repo_path), False, False, True, False, False, False, True, None)
        self.assertTrue(v)
        patches = r
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

    def testGeneral(self):

        v, r = collect_git_patch.collect_git_patch(self.nonexistent, self.storage_path, "include", [], [], False, False, False, False, 0, 0, None)
        self.assertFalse(v)

        v, r = collect_git_patch.collect_git_patch(self.first_repo, self.nonexistent, "include", [], [], False, False, False, False, 0, 0, None)
        self.assertFalse(v)

        v, r = collect_git_patch.collect_git_patch(self.first_repo, self.storage_path, "include", [], [], False, False, False, False, 0, 0, None)
        self.assertTrue(v)

    def testGeneralBestEffort(self):

        v, r = collect_git_patch.collect_git_patch(self.first_repo, self.storage_path, "include", [], [], True, False, False, False, 0, 0, None)
        self.assertFalse(v)
        first_head_patch_filename = path_utils.concat_path(self.storage_path, self.first_repo, "head.patch")
        first_head_id_patch_filename = path_utils.concat_path(self.storage_path, self.first_repo, "head_id.txt")
        self.assertFalse( os.path.exists( first_head_patch_filename ) )
        self.assertFalse( os.path.exists( first_head_id_patch_filename ) )

        v, r = collect_git_patch.collect_git_patch(self.first_repo, self.storage_path, "include", [], [], True, True, False, False, 0, 0, None)
        second_head_patch_filename = path_utils.concat_path(self.storage_path, self.first_repo, "head.patch")
        second_head_id_patch_filename = path_utils.concat_path(self.storage_path, self.first_repo, "head_id.txt")
        self.assertFalse(v)
        self.assertNotEqual(r[0], second_head_id_patch_filename)
        self.assertEqual(r[1], second_head_id_patch_filename)
        self.assertFalse( os.path.exists( second_head_patch_filename ) )
        self.assertTrue( os.path.exists( second_head_id_patch_filename ) )

    def testCollectPatchHeadFail(self):

        open_and_update_file.update_file_contents(self.first_file1, "extra")

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path, "include", [], [])
        self.assertTrue(v)
        patch_file = path_utils.concat_path(self.storage_path, self.first_repo, "head.patch")
        self.assertEqual(r, patch_file)
        self.assertTrue(os.path.exists(patch_file))
        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path, "include", [], [])
        self.assertFalse(v)

    def testCollectPatchHead1(self):

        open_and_update_file.update_file_contents(self.first_file1, "extra")

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path, "include", [], [])
        self.assertTrue(v)

        patch_file = path_utils.concat_path(self.storage_path, self.first_repo, "head.patch")
        self.assertTrue(os.path.exists(patch_file))
        self.assertEqual(r, patch_file)

        contents_read = getcontents.getcontents(patch_file)

        self.assertTrue("extra" in contents_read)

    def testCollectPatchHead2(self):

        first_file4 = path_utils.concat_path(self.first_repo, "file4.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file4.txt", "first-file4-content", "first-file4-msg")
        self.assertTrue(v)

        first_file5 = path_utils.concat_path(self.first_repo, "file5.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file5.txt", "first-file5-content", "first-file5-msg")
        self.assertTrue(v)

        first_file6 = path_utils.concat_path(self.first_repo, "file6.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file6.txt", "first-file6-content", "first-file6-msg")
        self.assertTrue(v)

        first_file7 = path_utils.concat_path(self.first_repo, "file7.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file7.txt", "first-file7-content", "first-file7-msg")
        self.assertTrue(v)

        first_file8 = path_utils.concat_path(self.first_repo, "file8.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file8.txt", "first-file8-content", "first-file8-msg")
        self.assertTrue(v)

        open_and_update_file.update_file_contents(self.first_file1, "extra")
        open_and_update_file.update_file_contents(self.first_file2, "smore stuff")
        open_and_update_file.update_file_contents(first_file7, "onto-the-seventh")

        self.assertTrue(os.path.exists(self.first_file3))
        os.unlink(self.first_file3)
        self.assertFalse(os.path.exists(self.first_file3))

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path, "include", [], [])
        self.assertTrue(v)

        patch_file = path_utils.concat_path(self.storage_path, self.first_repo, "head.patch")
        self.assertTrue(os.path.exists(patch_file))
        self.assertEqual(r, patch_file)

        contents_read = getcontents.getcontents(patch_file)

        self.assertTrue("extra" in contents_read)
        self.assertTrue("smore stuff" in contents_read)
        self.assertTrue("deleted file mode" in contents_read)
        self.assertTrue("onto-the-seventh" in contents_read)
        self.assertTrue(path_utils.basename_filtered(self.first_file1) in contents_read)
        self.assertTrue(path_utils.basename_filtered(self.first_file2) in contents_read)
        self.assertTrue(path_utils.basename_filtered(self.first_file3) in contents_read)
        self.assertFalse(path_utils.basename_filtered(first_file4) in contents_read)
        self.assertFalse(path_utils.basename_filtered(first_file5) in contents_read)
        self.assertFalse(path_utils.basename_filtered(first_file6) in contents_read)
        self.assertTrue(path_utils.basename_filtered(first_file7) in contents_read)
        self.assertFalse(path_utils.basename_filtered(first_file8) in contents_read)

    def testCollectPatchHead3(self):

        first_file4 = path_utils.concat_path(self.first_repo, "file4.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file4.txt", "first-file4-content", "first-file4-msg")
        self.assertTrue(v)

        first_file5 = path_utils.concat_path(self.first_repo, "file5.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file5.txt", "first-file5-content", "first-file5-msg")
        self.assertTrue(v)

        first_file6 = path_utils.concat_path(self.first_repo, "file6.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file6.txt", "first-file6-content", "first-file6-msg")
        self.assertTrue(v)

        first_file7 = path_utils.concat_path(self.first_repo, "file7.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file7.txt", "first-file7-content", "first-file7-msg")
        self.assertTrue(v)

        first_file8 = path_utils.concat_path(self.first_repo, "file8.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file8.txt", "first-file8-content", "first-file8-msg")
        self.assertTrue(v)

        first_sub1 = path_utils.concat_path(self.first_repo, "sub1")
        self.assertFalse(os.path.exists(first_sub1))
        os.mkdir(first_sub1)
        self.assertTrue(os.path.exists(first_sub1))

        first_sub1_file9 = path_utils.concat_path(first_sub1, "file9.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub1/file9.txt", "first-sub1-file9-content", "first-sub1-file9-msg")
        self.assertTrue(v)

        first_sub1_another = path_utils.concat_path(first_sub1, "another")
        self.assertFalse(os.path.exists(first_sub1_another))
        os.mkdir(first_sub1_another)
        self.assertTrue(os.path.exists(first_sub1_another))

        first_sub1_another_file10 = path_utils.concat_path(first_sub1_another, "file10.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub1/another/file10.txt", "first-sub1-another-file10-content", "first-sub1-another-file10-msg")
        self.assertTrue(v)

        first_sub1_another_file17 = path_utils.concat_path(first_sub1_another, "file17.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub1/another/file17.txt", "first-sub1-another-file17-content", "first-sub1-another-file17-msg")
        self.assertTrue(v)

        first_sub2 = path_utils.concat_path(self.first_repo, "sub2")
        self.assertFalse(os.path.exists(first_sub2))
        os.mkdir(first_sub2)
        self.assertTrue(os.path.exists(first_sub2))

        first_sub2_file9 = path_utils.concat_path(first_sub2, "file9.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub2/file9.txt", "first-sub2-file9-content", "first-sub2-file9-msg")
        self.assertTrue(v)

        first_sub2_another = path_utils.concat_path(first_sub2, "another")
        self.assertFalse(os.path.exists(first_sub2_another))
        os.mkdir(first_sub2_another)
        self.assertTrue(os.path.exists(first_sub2_another))

        first_sub2_another_file10 = path_utils.concat_path(first_sub2_another, "file10.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub2/another/file10.txt", "first-sub2-another-file10-content", "first-sub2-another-file10-msg")
        self.assertTrue(v)

        first_sub2_another_file19 = path_utils.concat_path(first_sub2_another, "file19.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub2/another/file19.txt", "first-sub2-another-file19-content", "first-sub2-another-file19-msg")
        self.assertTrue(v)

        open_and_update_file.update_file_contents(self.first_file1, "extra")
        open_and_update_file.update_file_contents(self.first_file2, "smore stuff")
        open_and_update_file.update_file_contents(self.first_file3, "modifying the third too")
        open_and_update_file.update_file_contents(first_file7, "onto-the-seventh")
        open_and_update_file.update_file_contents(first_sub1_another_file10, "appending to s1-f10")
        open_and_update_file.update_file_contents(first_sub1_another_file17, "more stuff for s1-f17")
        open_and_update_file.update_file_contents(first_sub2_another_file10, "yet more contents onto s2-f10")
        open_and_update_file.update_file_contents(first_sub2_another_file19, "some additional text for s2-f19")

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path, "include", [], [])
        self.assertTrue(v)
        self.assertTrue(os.path.exists(r))

        patch_file = path_utils.concat_path(self.storage_path, self.first_repo, "head.patch")
        self.assertTrue(os.path.exists(patch_file))
        self.assertEqual(r, patch_file)

        contents_read = getcontents.getcontents(patch_file)

        self.assertTrue("extra" in contents_read)
        self.assertTrue("smore stuff" in contents_read)
        self.assertTrue("modifying the third too" in contents_read)
        self.assertTrue("onto-the-seventh" in contents_read)
        self.assertTrue("appending to s1-f10" in contents_read)
        self.assertTrue("more stuff for s1-f17" in contents_read)
        self.assertTrue("yet more contents onto s2-f10" in contents_read)
        self.assertTrue("some additional text for s2-f19" in contents_read)
        self.assertTrue(path_utils.basename_filtered(self.first_file1) in contents_read)
        self.assertTrue(path_utils.basename_filtered(self.first_file2) in contents_read)
        self.assertTrue(path_utils.basename_filtered(self.first_file3) in contents_read)
        self.assertFalse(path_utils.basename_filtered(first_file4) in contents_read)
        self.assertFalse(path_utils.basename_filtered(first_file5) in contents_read)
        self.assertFalse(path_utils.basename_filtered(first_file6) in contents_read)
        self.assertTrue(path_utils.basename_filtered(first_file7) in contents_read)
        self.assertFalse(path_utils.basename_filtered(first_file8) in contents_read)
        self.assertFalse(path_utils.basename_filtered(first_file8) in contents_read)
        self.assertFalse(path_utils.concat_path(path_utils.basename_filtered(first_sub1), path_utils.basename_filtered(first_sub1_file9)) in contents_read)
        self.assertTrue(path_utils.concat_path(path_utils.basename_filtered(first_sub1), path_utils.basename_filtered(first_sub1_another), path_utils.basename_filtered(first_sub1_another_file10)) in contents_read)
        self.assertTrue(path_utils.concat_path(path_utils.basename_filtered(first_sub1), path_utils.basename_filtered(first_sub1_another), path_utils.basename_filtered(first_sub1_another_file17)) in contents_read)
        self.assertFalse(path_utils.concat_path(path_utils.basename_filtered(first_sub2), path_utils.basename_filtered(first_sub2_file9)) in contents_read)
        self.assertTrue(path_utils.concat_path(path_utils.basename_filtered(first_sub2), path_utils.basename_filtered(first_sub2_another), path_utils.basename_filtered(first_sub2_another_file10)) in contents_read)
        self.assertTrue(path_utils.concat_path(path_utils.basename_filtered(first_sub2), path_utils.basename_filtered(first_sub2_another), path_utils.basename_filtered(first_sub2_another_file19)) in contents_read)

    def testCollectPatchHead4(self):

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v and r)

        open_and_update_file.update_file_contents(self.first_file1, "actual modification")

        v, r = git_wrapper.stage(self.first_repo, [self.first_file1])
        self.assertTrue(v)

        open_and_update_file.update_file_contents(self.first_file1, "actual modification, again")

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path, "include", [], [])
        self.assertTrue(v)

        patch_file = path_utils.concat_path(self.storage_path, self.first_repo, "head.patch")
        self.assertTrue(os.path.exists(patch_file))
        self.assertEqual(r, patch_file)

        contents_read = getcontents.getcontents(patch_file)
        self.assertTrue("actual modification, again" in contents_read)

    def testCollectPatchHead5(self):

        first_more1 = path_utils.concat_path(self.first_repo, "more1.txt")
        self.assertFalse(os.path.exists(first_more1))
        create_and_write_file.create_file_contents(first_more1, "more1-contents")
        self.assertTrue(os.path.exists(first_more1))

        v, r = git_wrapper.stage(self.first_repo, [first_more1])
        self.assertTrue(v)

        open_and_update_file.update_file_contents(first_more1, "actual modification, again")

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path, "include", [], [])
        self.assertTrue(v)

        patch_file = path_utils.concat_path(self.storage_path, self.first_repo, "head.patch")
        self.assertTrue(os.path.exists(patch_file))
        self.assertEqual(r, patch_file)

        contents_read = getcontents.getcontents(patch_file)
        self.assertTrue("actual modification, again" in contents_read)

    def testCollectPatchHeadSub(self):

        open_and_update_file.update_file_contents(self.second_sub_file1, "extra_sub")

        v, r = collect_git_patch.collect_git_patch_head(self.second_sub, self.storage_path, "include", [], [])
        self.assertTrue(v)

        patch_file = path_utils.concat_path(self.storage_path, self.second_sub, "head.patch")
        self.assertTrue(os.path.exists(patch_file))
        self.assertEqual(r, patch_file)

        contents_read = getcontents.getcontents(patch_file)

        self.assertTrue("extra_sub" in contents_read)

    def testCollectPatchHead_Filtering1(self):

        first_file4 = path_utils.concat_path(self.first_repo, "file4.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file4.txt", "first-file4-content", "first-file4-msg")
        self.assertTrue(v)

        first_file5 = path_utils.concat_path(self.first_repo, "file5.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file5.txt", "first-file5-content", "first-file5-msg")
        self.assertTrue(v)

        first_file6 = path_utils.concat_path(self.first_repo, "file6.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file6.txt", "first-file6-content", "first-file6-msg")
        self.assertTrue(v)

        first_file7 = path_utils.concat_path(self.first_repo, "file7.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file7.txt", "first-file7-content", "first-file7-msg")
        self.assertTrue(v)

        first_file8 = path_utils.concat_path(self.first_repo, "file8.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file8.txt", "first-file8-content", "first-file8-msg")
        self.assertTrue(v)

        first_sub1 = path_utils.concat_path(self.first_repo, "sub1")
        self.assertFalse(os.path.exists(first_sub1))
        os.mkdir(first_sub1)
        self.assertTrue(os.path.exists(first_sub1))

        first_sub1_file9 = path_utils.concat_path(first_sub1, "file9.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub1/file9.txt", "first-sub1-file9-content", "first-sub1-file9-msg")
        self.assertTrue(v)

        first_sub1_another = path_utils.concat_path(first_sub1, "another")
        self.assertFalse(os.path.exists(first_sub1_another))
        os.mkdir(first_sub1_another)
        self.assertTrue(os.path.exists(first_sub1_another))

        first_sub1_another_file10 = path_utils.concat_path(first_sub1_another, "file10.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub1/another/file10.txt", "first-sub1-another-file10-content", "first-sub1-another-file10-msg")
        self.assertTrue(v)

        first_sub1_another_file17 = path_utils.concat_path(first_sub1_another, "file17.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub1/another/file17.txt", "first-sub1-another-file17-content", "first-sub1-another-file17-msg")
        self.assertTrue(v)

        first_sub2 = path_utils.concat_path(self.first_repo, "sub2")
        self.assertFalse(os.path.exists(first_sub2))
        os.mkdir(first_sub2)
        self.assertTrue(os.path.exists(first_sub2))

        first_sub2_file9 = path_utils.concat_path(first_sub2, "file9.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub2/file9.txt", "first-sub2-file9-content", "first-sub2-file9-msg")
        self.assertTrue(v)

        first_sub2_another = path_utils.concat_path(first_sub2, "another")
        self.assertFalse(os.path.exists(first_sub2_another))
        os.mkdir(first_sub2_another)
        self.assertTrue(os.path.exists(first_sub2_another))

        first_sub2_another_file10 = path_utils.concat_path(first_sub2_another, "file10.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub2/another/file10.txt", "first-sub2-another-file10-content", "first-sub2-another-file10-msg")
        self.assertTrue(v)

        first_sub2_another_file19 = path_utils.concat_path(first_sub2_another, "file19.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub2/another/file19.txt", "first-sub2-another-file19-content", "first-sub2-another-file19-msg")
        self.assertTrue(v)

        open_and_update_file.update_file_contents(self.first_file1, "extra")
        open_and_update_file.update_file_contents(self.first_file2, "smore stuff")
        open_and_update_file.update_file_contents(self.first_file3, "modifying the third too")
        open_and_update_file.update_file_contents(first_file7, "onto-the-seventh")
        open_and_update_file.update_file_contents(first_sub1_another_file10, "appending to s1-f10")
        open_and_update_file.update_file_contents(first_sub1_another_file17, "more stuff for s1-f17")
        open_and_update_file.update_file_contents(first_sub2_another_file10, "yet more contents onto s2-f10")
        open_and_update_file.update_file_contents(first_sub2_another_file19, "some additional text for s2-f19")

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path, "exclude", ["*/another/*"], [])
        self.assertTrue(v)
        self.assertTrue(os.path.exists(r))

        patch_file = path_utils.concat_path(self.storage_path, self.first_repo, "head.patch")
        self.assertTrue(os.path.exists(patch_file))
        self.assertEqual(r, patch_file)

        contents_read = getcontents.getcontents(patch_file)

        self.assertFalse("extra" in contents_read)
        self.assertFalse("smore stuff" in contents_read)
        self.assertFalse("modifying the third too" in contents_read)
        self.assertFalse("onto-the-seventh" in contents_read)
        self.assertTrue("appending to s1-f10" in contents_read)
        self.assertTrue("more stuff for s1-f17" in contents_read)
        self.assertTrue("yet more contents onto s2-f10" in contents_read)
        self.assertTrue("some additional text for s2-f19" in contents_read)
        self.assertFalse(path_utils.basename_filtered(self.first_file1) in contents_read)
        self.assertFalse(path_utils.basename_filtered(self.first_file2) in contents_read)
        self.assertFalse(path_utils.basename_filtered(self.first_file3) in contents_read)
        self.assertFalse(path_utils.basename_filtered(first_file4) in contents_read)
        self.assertFalse(path_utils.basename_filtered(first_file5) in contents_read)
        self.assertFalse(path_utils.basename_filtered(first_file6) in contents_read)
        self.assertFalse(path_utils.basename_filtered(first_file7) in contents_read)
        self.assertFalse(path_utils.basename_filtered(first_file8) in contents_read)
        self.assertFalse(path_utils.basename_filtered(first_file8) in contents_read)
        self.assertFalse(path_utils.concat_path(path_utils.basename_filtered(first_sub1), path_utils.basename_filtered(first_sub1_file9)) in contents_read)
        self.assertTrue(path_utils.concat_path(path_utils.basename_filtered(first_sub1), path_utils.basename_filtered(first_sub1_another), path_utils.basename_filtered(first_sub1_another_file10)) in contents_read)
        self.assertTrue(path_utils.concat_path(path_utils.basename_filtered(first_sub1), path_utils.basename_filtered(first_sub1_another), path_utils.basename_filtered(first_sub1_another_file17)) in contents_read)
        self.assertFalse(path_utils.concat_path(path_utils.basename_filtered(first_sub2), path_utils.basename_filtered(first_sub2_file9)) in contents_read)
        self.assertTrue(path_utils.concat_path(path_utils.basename_filtered(first_sub2), path_utils.basename_filtered(first_sub2_another), path_utils.basename_filtered(first_sub2_another_file10)) in contents_read)
        self.assertTrue(path_utils.concat_path(path_utils.basename_filtered(first_sub2), path_utils.basename_filtered(first_sub2_another), path_utils.basename_filtered(first_sub2_another_file19)) in contents_read)

    def testCollectPatchHead_Filtering2(self):

        first_file4 = path_utils.concat_path(self.first_repo, "file4.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file4.txt", "first-file4-content", "first-file4-msg")
        self.assertTrue(v)

        first_file5 = path_utils.concat_path(self.first_repo, "file5.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file5.txt", "first-file5-content", "first-file5-msg")
        self.assertTrue(v)

        first_file6 = path_utils.concat_path(self.first_repo, "file6.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file6.txt", "first-file6-content", "first-file6-msg")
        self.assertTrue(v)

        first_file7 = path_utils.concat_path(self.first_repo, "file7.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file7.txt", "first-file7-content", "first-file7-msg")
        self.assertTrue(v)

        first_file8 = path_utils.concat_path(self.first_repo, "file8.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file8.txt", "first-file8-content", "first-file8-msg")
        self.assertTrue(v)

        first_sub1 = path_utils.concat_path(self.first_repo, "sub1")
        self.assertFalse(os.path.exists(first_sub1))
        os.mkdir(first_sub1)
        self.assertTrue(os.path.exists(first_sub1))

        first_sub1_file9 = path_utils.concat_path(first_sub1, "file9.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub1/file9.txt", "first-sub1-file9-content", "first-sub1-file9-msg")
        self.assertTrue(v)

        first_sub1_another = path_utils.concat_path(first_sub1, "another")
        self.assertFalse(os.path.exists(first_sub1_another))
        os.mkdir(first_sub1_another)
        self.assertTrue(os.path.exists(first_sub1_another))

        first_sub1_another_file10 = path_utils.concat_path(first_sub1_another, "file10.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub1/another/file10.txt", "first-sub1-another-file10-content", "first-sub1-another-file10-msg")
        self.assertTrue(v)

        first_sub1_another_file17 = path_utils.concat_path(first_sub1_another, "file17.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub1/another/file17.txt", "first-sub1-another-file17-content", "first-sub1-another-file17-msg")
        self.assertTrue(v)

        first_sub2 = path_utils.concat_path(self.first_repo, "sub2")
        self.assertFalse(os.path.exists(first_sub2))
        os.mkdir(first_sub2)
        self.assertTrue(os.path.exists(first_sub2))

        first_sub2_file9 = path_utils.concat_path(first_sub2, "file9.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub2/file9.txt", "first-sub2-file9-content", "first-sub2-file9-msg")
        self.assertTrue(v)

        first_sub2_another = path_utils.concat_path(first_sub2, "another")
        self.assertFalse(os.path.exists(first_sub2_another))
        os.mkdir(first_sub2_another)
        self.assertTrue(os.path.exists(first_sub2_another))

        first_sub2_another_file10 = path_utils.concat_path(first_sub2_another, "file10.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub2/another/file10.txt", "first-sub2-another-file10-content", "first-sub2-another-file10-msg")
        self.assertTrue(v)

        first_sub2_another_file19 = path_utils.concat_path(first_sub2_another, "file19.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub2/another/file19.txt", "first-sub2-another-file19-content", "first-sub2-another-file19-msg")
        self.assertTrue(v)

        self.assertTrue(os.path.exists(first_sub1_file9))
        os.unlink(first_sub1_file9)
        self.assertFalse(os.path.exists(first_sub1_file9))

        self.assertTrue(os.path.exists(first_sub1_another_file10))
        os.unlink(first_sub1_another_file10)
        self.assertFalse(os.path.exists(first_sub1_another_file10))

        self.assertTrue(os.path.exists(first_sub1_another_file17))
        os.unlink(first_sub1_another_file17)
        self.assertFalse(os.path.exists(first_sub1_another_file17))

        self.assertTrue(os.path.exists(first_sub2_file9))
        os.unlink(first_sub2_file9)
        self.assertFalse(os.path.exists(first_sub2_file9))

        self.assertTrue(os.path.exists(first_sub2_another_file10))
        os.unlink(first_sub2_another_file10)
        self.assertFalse(os.path.exists(first_sub2_another_file10))

        self.assertTrue(os.path.exists(first_sub2_another_file19))
        os.unlink(first_sub2_another_file19)
        self.assertFalse(os.path.exists(first_sub2_another_file19))

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path, "exclude", ["*/sub1/*"], [])
        self.assertTrue(v)
        self.assertTrue(os.path.exists(r))

        patch_file = path_utils.concat_path(self.storage_path, self.first_repo, "head.patch")
        self.assertTrue(os.path.exists(patch_file))
        self.assertEqual(r, patch_file)

        contents_read = getcontents.getcontents(patch_file)

        self.assertEqual(contents_read.count("deleted file mode"), 3)
        self.assertFalse(path_utils.basename_filtered(self.first_file1) in contents_read)
        self.assertFalse(path_utils.basename_filtered(self.first_file2) in contents_read)
        self.assertFalse(path_utils.basename_filtered(self.first_file3) in contents_read)
        self.assertFalse(path_utils.basename_filtered(first_file4) in contents_read)
        self.assertFalse(path_utils.basename_filtered(first_file5) in contents_read)
        self.assertFalse(path_utils.basename_filtered(first_file6) in contents_read)
        self.assertFalse(path_utils.basename_filtered(first_file7) in contents_read)
        self.assertFalse(path_utils.basename_filtered(first_file8) in contents_read)
        self.assertFalse(path_utils.basename_filtered(first_file8) in contents_read)
        self.assertTrue(path_utils.concat_path(path_utils.basename_filtered(first_sub1), path_utils.basename_filtered(first_sub1_file9)) in contents_read)
        self.assertTrue(path_utils.concat_path(path_utils.basename_filtered(first_sub1), path_utils.basename_filtered(first_sub1_another), path_utils.basename_filtered(first_sub1_another_file10)) in contents_read)
        self.assertTrue(path_utils.concat_path(path_utils.basename_filtered(first_sub1), path_utils.basename_filtered(first_sub1_another), path_utils.basename_filtered(first_sub1_another_file17)) in contents_read)
        self.assertFalse(path_utils.concat_path(path_utils.basename_filtered(first_sub2), path_utils.basename_filtered(first_sub2_file9)) in contents_read)
        self.assertFalse(path_utils.concat_path(path_utils.basename_filtered(first_sub2), path_utils.basename_filtered(first_sub2_another), path_utils.basename_filtered(first_sub2_another_file10)) in contents_read)
        self.assertFalse(path_utils.concat_path(path_utils.basename_filtered(first_sub2), path_utils.basename_filtered(first_sub2_another), path_utils.basename_filtered(first_sub2_another_file19)) in contents_read)

    def testCollectPatchHead_Filtering3(self):

        first_file4 = path_utils.concat_path(self.first_repo, "file4.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file4.txt", "first-file4-content", "first-file4-msg")
        self.assertTrue(v)

        first_file5 = path_utils.concat_path(self.first_repo, "file5.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file5.txt", "first-file5-content", "first-file5-msg")
        self.assertTrue(v)

        first_file6 = path_utils.concat_path(self.first_repo, "file6.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file6.txt", "first-file6-content", "first-file6-msg")
        self.assertTrue(v)

        first_file7 = path_utils.concat_path(self.first_repo, "file7.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file7.txt", "first-file7-content", "first-file7-msg")
        self.assertTrue(v)

        first_file8 = path_utils.concat_path(self.first_repo, "file8.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file8.txt", "first-file8-content", "first-file8-msg")
        self.assertTrue(v)

        first_sub1 = path_utils.concat_path(self.first_repo, "sub1")
        self.assertFalse(os.path.exists(first_sub1))
        os.mkdir(first_sub1)
        self.assertTrue(os.path.exists(first_sub1))

        first_sub1_file9 = path_utils.concat_path(first_sub1, "file9.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub1/file9.txt", "first-sub1-file9-content", "first-sub1-file9-msg")
        self.assertTrue(v)

        first_sub1_another = path_utils.concat_path(first_sub1, "another")
        self.assertFalse(os.path.exists(first_sub1_another))
        os.mkdir(first_sub1_another)
        self.assertTrue(os.path.exists(first_sub1_another))

        first_sub1_another_file10 = path_utils.concat_path(first_sub1_another, "file10.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub1/another/file10.txt", "first-sub1-another-file10-content", "first-sub1-another-file10-msg")
        self.assertTrue(v)

        first_sub1_another_file17 = path_utils.concat_path(first_sub1_another, "file17.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub1/another/file17.txt", "first-sub1-another-file17-content", "first-sub1-another-file17-msg")
        self.assertTrue(v)

        first_sub2 = path_utils.concat_path(self.first_repo, "sub2")
        self.assertFalse(os.path.exists(first_sub2))
        os.mkdir(first_sub2)
        self.assertTrue(os.path.exists(first_sub2))

        first_sub2_file9 = path_utils.concat_path(first_sub2, "file9.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub2/file9.txt", "first-sub2-file9-content", "first-sub2-file9-msg")
        self.assertTrue(v)

        first_sub2_another = path_utils.concat_path(first_sub2, "another")
        self.assertFalse(os.path.exists(first_sub2_another))
        os.mkdir(first_sub2_another)
        self.assertTrue(os.path.exists(first_sub2_another))

        first_sub2_another_file10 = path_utils.concat_path(first_sub2_another, "file10.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub2/another/file10.txt", "first-sub2-another-file10-content", "first-sub2-another-file10-msg")
        self.assertTrue(v)

        first_sub2_another_file19 = path_utils.concat_path(first_sub2_another, "file19.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub2/another/file19.txt", "first-sub2-another-file19-content", "first-sub2-another-file19-msg")
        self.assertTrue(v)

        open_and_update_file.update_file_contents(first_file6, "adding to file6")
        open_and_update_file.update_file_contents(first_sub1_file9, "adding to sub1-file9")
        open_and_update_file.update_file_contents(first_sub1_another_file17, "adding to sub1-file17")
        open_and_update_file.update_file_contents(first_sub2_another_file19, "adding to sub2-file19")

        v, r = git_wrapper.stash(self.first_repo)
        self.assertTrue(v)

        open_and_update_file.update_file_contents(first_file6, "!incompatible! adding to file6")
        open_and_update_file.update_file_contents(first_sub1_file9, "!incompatible! adding to sub1-file9")
        open_and_update_file.update_file_contents(first_sub1_another_file17, "!incompatible! adding to sub1-file17")
        open_and_update_file.update_file_contents(first_sub2_another_file19, "!incompatible! adding to sub2-file19")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.first_repo, "conflict-causing commit")
        self.assertTrue(v)

        v, r = git_wrapper.stash_pop(self.first_repo)
        self.assertFalse(v) # fails because of conflict

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path, "include", [], ["*/file19.txt"])
        self.assertTrue(v)
        self.assertTrue(os.path.exists(r))

        patch_file = path_utils.concat_path(self.storage_path, self.first_repo, "head.patch")
        self.assertTrue(os.path.exists(patch_file))
        self.assertEqual(r, patch_file)

        contents_read = getcontents.getcontents(patch_file)

        self.assertFalse(path_utils.basename_filtered(self.first_file1) in contents_read)
        self.assertFalse(path_utils.basename_filtered(self.first_file2) in contents_read)
        self.assertFalse(path_utils.basename_filtered(self.first_file3) in contents_read)
        self.assertFalse(path_utils.basename_filtered(first_file4) in contents_read)
        self.assertFalse(path_utils.basename_filtered(first_file5) in contents_read)
        self.assertTrue(path_utils.basename_filtered(first_file6) in contents_read)
        self.assertFalse(path_utils.basename_filtered(first_file7) in contents_read)
        self.assertFalse(path_utils.basename_filtered(first_file8) in contents_read)
        self.assertFalse(path_utils.basename_filtered(first_file8) in contents_read)
        self.assertTrue(path_utils.concat_path(path_utils.basename_filtered(first_sub1), path_utils.basename_filtered(first_sub1_file9)) in contents_read)
        self.assertFalse(path_utils.concat_path(path_utils.basename_filtered(first_sub1), path_utils.basename_filtered(first_sub1_another), path_utils.basename_filtered(first_sub1_another_file10)) in contents_read)
        self.assertTrue(path_utils.concat_path(path_utils.basename_filtered(first_sub1), path_utils.basename_filtered(first_sub1_another), path_utils.basename_filtered(first_sub1_another_file17)) in contents_read)
        self.assertFalse(path_utils.concat_path(path_utils.basename_filtered(first_sub2), path_utils.basename_filtered(first_sub2_file9)) in contents_read)
        self.assertFalse(path_utils.concat_path(path_utils.basename_filtered(first_sub2), path_utils.basename_filtered(first_sub2_another), path_utils.basename_filtered(first_sub2_another_file10)) in contents_read)
        self.assertFalse(path_utils.concat_path(path_utils.basename_filtered(first_sub2), path_utils.basename_filtered(first_sub2_another), path_utils.basename_filtered(first_sub2_another_file19)) in contents_read)

    def testCollectPatchHead_Filtering4(self):

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v and r)

        open_and_update_file.update_file_contents(self.first_file1, "actual modification, file1")
        open_and_update_file.update_file_contents(self.first_file2, "actual modification, file2")

        v, r = git_wrapper.stage(self.first_repo, [self.first_file1, self.first_file2])
        self.assertTrue(v)

        open_and_update_file.update_file_contents(self.first_file1, "actual modification, again, file1")
        open_and_update_file.update_file_contents(self.first_file2, "actual modification, again, file2")

        patch_file = path_utils.concat_path(self.storage_path, self.first_repo, "head.patch")
        self.assertFalse(os.path.exists(patch_file))

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path, "include", [], ["*/file2.txt"])
        self.assertTrue(v)
        self.assertTrue(os.path.exists(r))
        self.assertTrue(os.path.exists(patch_file))

        contents_read = getcontents.getcontents(patch_file)
        self.assertTrue("actual modification, again, file1" in contents_read)
        self.assertFalse("actual modification, again, file2" in contents_read)

    def testCollectPatchHead_Filtering5(self):

        first_more1 = path_utils.concat_path(self.first_repo, "more1.txt")
        self.assertFalse(os.path.exists(first_more1))
        create_and_write_file.create_file_contents(first_more1, "more1-contents")
        self.assertTrue(os.path.exists(first_more1))

        first_more2 = path_utils.concat_path(self.first_repo, "more2.txt")
        self.assertFalse(os.path.exists(first_more2))
        create_and_write_file.create_file_contents(first_more2, "more2-contents")
        self.assertTrue(os.path.exists(first_more2))

        v, r = git_wrapper.stage(self.first_repo, [first_more1, first_more2])
        self.assertTrue(v)

        open_and_update_file.update_file_contents(first_more1, "actual modification, again, more1")
        open_and_update_file.update_file_contents(first_more2, "actual modification, again, more2")

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path, "include", [], ["*/more2.txt"])
        self.assertTrue(v)

        patch_file = path_utils.concat_path(self.storage_path, self.first_repo, "head.patch")
        self.assertTrue(os.path.exists(patch_file))
        self.assertEqual(r, patch_file)

        contents_read = getcontents.getcontents(patch_file)
        self.assertTrue("actual modification, again, more1" in contents_read)
        self.assertFalse("actual modification, again, more2" in contents_read)

    def testCollectPatchHead_Filtering6(self):

        first_more1 = path_utils.concat_path(self.first_repo, "more1.txt")
        self.assertFalse(os.path.exists(first_more1))
        create_and_write_file.create_file_contents(first_more1, "more1-contents")
        self.assertTrue(os.path.exists(first_more1))

        first_more2 = path_utils.concat_path(self.first_repo, "more2.txt")
        self.assertFalse(os.path.exists(first_more2))
        create_and_write_file.create_file_contents(first_more2, "more2-contents")
        self.assertTrue(os.path.exists(first_more2))

        v, r = git_wrapper.stage(self.first_repo, [first_more1, first_more2])
        self.assertTrue(v)

        open_and_update_file.update_file_contents(first_more1, "actual modification, again, more1")
        open_and_update_file.update_file_contents(first_more2, "actual modification, again, more2")

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path, "exclude", [], [])
        self.assertFalse(v)
        self.assertEqual(r, collect_git_patch.ERRMSG_EMPTY)

        patch_file = path_utils.concat_path(self.storage_path, self.first_repo, "head.patch")
        self.assertFalse(os.path.exists(patch_file))

    def testCollectPatchHeadIdFail(self):

        v, r = collect_git_patch.collect_git_patch_head_id(self.first_repo, self.storage_path)
        self.assertTrue(v)

        patch_file = path_utils.concat_path(self.storage_path, self.first_repo, "head_id.txt")
        self.assertTrue(os.path.exists(patch_file))
        self.assertEqual(r, patch_file)

        v, r = collect_git_patch.collect_git_patch_head_id(self.first_repo, self.storage_path)
        self.assertFalse(v)

    def testCollectPatchHeadId(self):

        v, r = collect_git_patch.collect_git_patch_head_id(self.first_repo, self.storage_path)
        self.assertTrue(v)

        patch_file = path_utils.concat_path(self.storage_path, self.first_repo, "head_id.txt")
        self.assertTrue(os.path.exists(patch_file))
        self.assertEqual(r, patch_file)

        contents_read = getcontents.getcontents(patch_file)

        self.assertGreaterEqual(len(contents_read), 40)

    def testCollectPatchHeadIdSub(self):

        v, r = collect_git_patch.collect_git_patch_head_id(self.second_sub, self.storage_path)
        self.assertTrue(v)

        patch_file = path_utils.concat_path(self.storage_path, self.second_sub, "head_id.txt")
        self.assertTrue(os.path.exists(patch_file))
        self.assertEqual(r, patch_file)

        contents_read = getcontents.getcontents(patch_file)

        self.assertGreaterEqual(len(contents_read), 40)

    def testCollectPatchHeadIdBoth(self):

        v, r = collect_git_patch.collect_git_patch_head_id(self.first_repo, self.storage_path)
        self.assertTrue(v)
        patch_file_first = path_utils.concat_path(self.storage_path, self.first_repo, "head_id.txt")
        self.assertTrue(os.path.exists(patch_file_first))
        self.assertEqual(r, patch_file_first)

        v, r = collect_git_patch.collect_git_patch_head_id(self.second_repo, self.storage_path)
        self.assertTrue(v)
        patch_file_second = path_utils.concat_path(self.storage_path, self.second_repo, "head_id.txt")
        self.assertTrue(os.path.exists(patch_file_second))
        self.assertEqual(r, patch_file_second)

        contents_read = getcontents.getcontents(patch_file_first)
        self.assertGreaterEqual(len(contents_read), 40)

        contents_read = getcontents.getcontents(patch_file_second)
        self.assertGreaterEqual(len(contents_read), 40)

    def testCollectPatchStagedFail(self):

        newfile = path_utils.concat_path(self.first_repo, "newfile.txt")
        create_and_write_file.create_file_contents(newfile, "newfilecontents")

        self.assertTrue(git_wrapper.stage(self.first_repo))

        v, r = collect_git_patch.collect_git_patch_staged(self.first_repo, self.storage_path, "include", [], [])
        self.assertTrue(v)

        patch_file = path_utils.concat_path(self.storage_path, self.first_repo, "staged.patch")
        self.assertTrue(os.path.exists(patch_file))
        self.assertEqual(r, patch_file)

        v, r = collect_git_patch.collect_git_patch_staged(self.first_repo, self.storage_path, "include", [], [])
        self.assertFalse(v)

    def testCollectPatchStaged1(self):

        newfile = path_utils.concat_path(self.first_repo, "newfile.txt")
        create_and_write_file.create_file_contents(newfile, "newfilecontents")

        self.assertTrue(git_wrapper.stage(self.first_repo))

        v, r = collect_git_patch.collect_git_patch_staged(self.first_repo, self.storage_path, "include", [], [])
        self.assertTrue(v)

        patch_file = path_utils.concat_path(self.storage_path, self.first_repo, "staged.patch")
        self.assertTrue(os.path.exists(patch_file))
        self.assertEqual(r, patch_file)

        contents_read = getcontents.getcontents(patch_file)

        self.assertTrue("newfilecontents" in contents_read)

    def testCollectPatchStaged2(self):

        first_file4 = path_utils.concat_path(self.first_repo, "file4.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file4.txt", "first-file4-content", "first-file4-msg")
        self.assertTrue(v)

        first_file5 = path_utils.concat_path(self.first_repo, "file5.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file5.txt", "first-file5-content", "first-file5-msg")
        self.assertTrue(v)

        first_file6 = path_utils.concat_path(self.first_repo, "file6.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file6.txt", "first-file6-content", "first-file6-msg")
        self.assertTrue(v)

        first_file7 = path_utils.concat_path(self.first_repo, "file7.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file7.txt", "first-file7-content", "first-file7-msg")
        self.assertTrue(v)

        first_file8 = path_utils.concat_path(self.first_repo, "file8.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file8.txt", "first-file8-content", "first-file8-msg")
        self.assertTrue(v)

        first_sub1 = path_utils.concat_path(self.first_repo, "sub1")
        self.assertFalse(os.path.exists(first_sub1))
        os.mkdir(first_sub1)
        self.assertTrue(os.path.exists(first_sub1))

        first_sub1_file9 = path_utils.concat_path(first_sub1, "file9.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub1/file9.txt", "first-sub1-file9-content", "first-sub1-file9-msg")
        self.assertTrue(v)

        first_sub1_another = path_utils.concat_path(first_sub1, "another")
        self.assertFalse(os.path.exists(first_sub1_another))
        os.mkdir(first_sub1_another)
        self.assertTrue(os.path.exists(first_sub1_another))

        first_sub1_another_file10 = path_utils.concat_path(first_sub1_another, "file10.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub1/another/file10.txt", "first-sub1-another-file10-content", "first-sub1-another-file10-msg")
        self.assertTrue(v)

        first_sub1_another_file17 = path_utils.concat_path(first_sub1_another, "file17.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub1/another/file17.txt", "first-sub1-another-file17-content", "first-sub1-another-file17-msg")
        self.assertTrue(v)

        first_sub2 = path_utils.concat_path(self.first_repo, "sub2")
        self.assertFalse(os.path.exists(first_sub2))
        os.mkdir(first_sub2)
        self.assertTrue(os.path.exists(first_sub2))

        first_sub2_file9 = path_utils.concat_path(first_sub2, "file9.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub2/file9.txt", "first-sub2-file9-content", "first-sub2-file9-msg")
        self.assertTrue(v)

        first_sub2_another = path_utils.concat_path(first_sub2, "another")
        self.assertFalse(os.path.exists(first_sub2_another))
        os.mkdir(first_sub2_another)
        self.assertTrue(os.path.exists(first_sub2_another))

        first_sub2_another_file10 = path_utils.concat_path(first_sub2_another, "file10.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub2/another/file10.txt", "first-sub2-another-file10-content", "first-sub2-another-file10-msg")
        self.assertTrue(v)

        first_sub2_another_file19 = path_utils.concat_path(first_sub2_another, "file19.txt")
        first_sub2_another_file19_renamed = path_utils.concat_path(first_sub2_another, "file19_renamed.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub2/another/file19.txt", "first-sub2-another-file19-content", "first-sub2-another-file19-msg")
        self.assertTrue(v)

        open_and_update_file.update_file_contents(self.first_file1, "more file1")
        open_and_update_file.update_file_contents(self.first_file3, "more file3")

        self.assertTrue(os.path.exists(first_file4))
        os.unlink(first_file4)
        self.assertFalse(os.path.exists(first_file4))

        self.assertTrue(os.path.exists(first_file7))
        os.unlink(first_file7)
        self.assertFalse(os.path.exists(first_file7))

        self.assertTrue(os.path.exists(first_sub1_another_file17))
        os.unlink(first_sub1_another_file17)
        self.assertFalse(os.path.exists(first_sub1_another_file17))

        self.assertTrue(path_utils.copy_to_and_rename(first_sub2_another_file19, path_utils.dirname_filtered(first_sub2_another_file19_renamed), path_utils.basename_filtered(first_sub2_another_file19_renamed)))
        os.unlink(first_sub2_another_file19)

        first_file25 = path_utils.concat_path(self.first_repo, "file25.txt")
        create_and_write_file.create_file_contents(first_file25, "file25-contents")

        first_sub1_another_file30 = path_utils.concat_path(first_sub1_another, "file30.txt")
        create_and_write_file.create_file_contents(first_sub1_another_file30, "file30-contents")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = collect_git_patch.collect_git_patch_staged(self.first_repo, self.storage_path, "include", [], [])
        self.assertTrue(v)
        self.assertTrue(os.path.exists(r))

        patch_file = path_utils.concat_path(self.storage_path, self.first_repo, "staged.patch")
        self.assertTrue(os.path.exists(patch_file))
        self.assertEqual(r, patch_file)

        contents_read = getcontents.getcontents(patch_file)

        self.assertTrue(path_utils.basename_filtered(self.first_file1) in contents_read)
        self.assertFalse(path_utils.basename_filtered(self.first_file2) in contents_read)
        self.assertTrue(path_utils.basename_filtered(self.first_file3) in contents_read)
        self.assertTrue(path_utils.basename_filtered(first_file4) in contents_read)
        self.assertFalse(path_utils.basename_filtered(first_file5) in contents_read)
        self.assertFalse(path_utils.basename_filtered(first_file6) in contents_read)
        self.assertTrue(path_utils.basename_filtered(first_file7) in contents_read)
        self.assertFalse(path_utils.basename_filtered(first_file8) in contents_read)
        self.assertTrue(path_utils.basename_filtered(first_file25) in contents_read)
        self.assertFalse(path_utils.concat_path(path_utils.basename_filtered(first_sub1), path_utils.basename_filtered(first_sub1_file9)) in contents_read)
        self.assertFalse(path_utils.concat_path(path_utils.basename_filtered(first_sub1), path_utils.basename_filtered(first_sub1_another), path_utils.basename_filtered(first_sub1_another_file10)) in contents_read)
        self.assertTrue(path_utils.concat_path(path_utils.basename_filtered(first_sub1), path_utils.basename_filtered(first_sub1_another), path_utils.basename_filtered(first_sub1_another_file17)) in contents_read)
        self.assertTrue(path_utils.concat_path(path_utils.basename_filtered(first_sub1), path_utils.basename_filtered(first_sub1_another), path_utils.basename_filtered(first_sub1_another_file30)) in contents_read)
        self.assertFalse(path_utils.concat_path(path_utils.basename_filtered(first_sub2), path_utils.basename_filtered(first_sub2_file9)) in contents_read)
        self.assertFalse(path_utils.concat_path(path_utils.basename_filtered(first_sub2), path_utils.basename_filtered(first_sub2_another), path_utils.basename_filtered(first_sub2_another_file10)) in contents_read)
        self.assertTrue(path_utils.concat_path(path_utils.basename_filtered(first_sub2), path_utils.basename_filtered(first_sub2_another), path_utils.basename_filtered(first_sub2_another_file19)) in contents_read)
        self.assertTrue(path_utils.concat_path(path_utils.basename_filtered(first_sub2), path_utils.basename_filtered(first_sub2_another), path_utils.basename_filtered(first_sub2_another_file19_renamed)) in contents_read)
        self.assertEqual(contents_read.count("new file mode"), 2)
        self.assertEqual(contents_read.count("deleted file mode"), 3)
        self.assertEqual(contents_read.count("rename from"), 1)
        self.assertEqual(contents_read.count("rename to"), 1)

    def testCollectPatchStaged3(self):

        first_file4 = path_utils.concat_path(self.first_repo, "file4.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file4.txt", "first-file4-content", "first-file4-msg")
        self.assertTrue(v)

        first_file5 = path_utils.concat_path(self.first_repo, "file5.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file5.txt", "first-file5-content", "first-file5-msg")
        self.assertTrue(v)

        first_file6 = path_utils.concat_path(self.first_repo, "file6.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file6.txt", "first-file6-content", "first-file6-msg")
        self.assertTrue(v)

        first_file7 = path_utils.concat_path(self.first_repo, "file7.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file7.txt", "first-file7-content", "first-file7-msg")
        self.assertTrue(v)

        first_file8 = path_utils.concat_path(self.first_repo, "file8.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file8.txt", "first-file8-content", "first-file8-msg")
        self.assertTrue(v)

        first_sub1 = path_utils.concat_path(self.first_repo, "sub1")
        self.assertFalse(os.path.exists(first_sub1))
        os.mkdir(first_sub1)
        self.assertTrue(os.path.exists(first_sub1))

        first_sub1_file9 = path_utils.concat_path(first_sub1, "file9.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub1/file9.txt", "first-sub1-file9-content", "first-sub1-file9-msg")
        self.assertTrue(v)

        first_sub1_another = path_utils.concat_path(first_sub1, "another")
        self.assertFalse(os.path.exists(first_sub1_another))
        os.mkdir(first_sub1_another)
        self.assertTrue(os.path.exists(first_sub1_another))

        first_sub1_another_file10 = path_utils.concat_path(first_sub1_another, "file10.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub1/another/file10.txt", "first-sub1-another-file10-content", "first-sub1-another-file10-msg")
        self.assertTrue(v)

        first_sub1_another_file17 = path_utils.concat_path(first_sub1_another, "file17.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub1/another/file17.txt", "first-sub1-another-file17-content", "first-sub1-another-file17-msg")
        self.assertTrue(v)

        first_sub2 = path_utils.concat_path(self.first_repo, "sub2")
        self.assertFalse(os.path.exists(first_sub2))
        os.mkdir(first_sub2)
        self.assertTrue(os.path.exists(first_sub2))

        first_sub2_file9 = path_utils.concat_path(first_sub2, "file9.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub2/file9.txt", "first-sub2-file9-content", "first-sub2-file9-msg")
        self.assertTrue(v)

        first_sub2_another = path_utils.concat_path(first_sub2, "another")
        self.assertFalse(os.path.exists(first_sub2_another))
        os.mkdir(first_sub2_another)
        self.assertTrue(os.path.exists(first_sub2_another))

        first_sub2_another_file10 = path_utils.concat_path(first_sub2_another, "file10.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub2/another/file10.txt", "first-sub2-another-file10-content", "first-sub2-another-file10-msg")
        self.assertTrue(v)

        first_sub2_another_file19 = path_utils.concat_path(first_sub2_another, "file19.txt")
        first_sub2_another_file19_renamed = path_utils.concat_path(first_sub2_another, "file19_renamed.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub2/another/file19.txt", "first-sub2-another-file19-content", "first-sub2-another-file19-msg")
        self.assertTrue(v)

        open_and_update_file.update_file_contents(self.first_file1, "more file1")
        open_and_update_file.update_file_contents(self.first_file3, "more file3")

        self.assertTrue(os.path.exists(first_file4))
        os.unlink(first_file4)
        self.assertFalse(os.path.exists(first_file4))

        self.assertTrue(os.path.exists(first_file7))
        os.unlink(first_file7)
        self.assertFalse(os.path.exists(first_file7))

        self.assertTrue(os.path.exists(first_sub1_another_file17))
        os.unlink(first_sub1_another_file17)
        self.assertFalse(os.path.exists(first_sub1_another_file17))

        self.assertTrue(path_utils.copy_to_and_rename(first_sub2_another_file19, path_utils.dirname_filtered(first_sub2_another_file19_renamed), path_utils.basename_filtered(first_sub2_another_file19_renamed)))
        os.unlink(first_sub2_another_file19)

        first_file25 = path_utils.concat_path(self.first_repo, "file25.txt")
        create_and_write_file.create_file_contents(first_file25, "file25-contents")

        first_sub1_another_file30 = path_utils.concat_path(first_sub1_another, "file30.txt")
        create_and_write_file.create_file_contents(first_sub1_another_file30, "file30-contents")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        open_and_update_file.update_file_contents(first_file5, "mod f5")

        v, r = collect_git_patch.collect_git_patch_staged(self.first_repo, self.storage_path, "include", [], [])
        self.assertTrue(v)
        self.assertTrue(os.path.exists(r))

        patch_file = path_utils.concat_path(self.storage_path, self.first_repo, "staged.patch")
        self.assertTrue(os.path.exists(patch_file))
        self.assertEqual(r, patch_file)

        contents_read = getcontents.getcontents(patch_file)

        self.assertTrue(os.path.exists(first_sub2_file9))
        os.unlink(first_sub2_file9)
        self.assertFalse(os.path.exists(first_sub2_file9))

        first_sub1_another_file10_renamed = path_utils.concat_path(first_sub1_another, "file10_renamed.txt")
        self.assertTrue(path_utils.copy_to_and_rename(first_sub1_another_file10, path_utils.dirname_filtered(first_sub1_another_file10_renamed), path_utils.basename_filtered(first_sub1_another_file10_renamed)))
        os.unlink(first_sub1_another_file10)

        self.assertTrue(path_utils.basename_filtered(self.first_file1) in contents_read)
        self.assertFalse(path_utils.basename_filtered(self.first_file2) in contents_read)
        self.assertTrue(path_utils.basename_filtered(self.first_file3) in contents_read)
        self.assertTrue(path_utils.basename_filtered(first_file4) in contents_read)
        self.assertFalse(path_utils.basename_filtered(first_file5) in contents_read)
        self.assertFalse(path_utils.basename_filtered(first_file6) in contents_read)
        self.assertTrue(path_utils.basename_filtered(first_file7) in contents_read)
        self.assertFalse(path_utils.basename_filtered(first_file8) in contents_read)
        self.assertTrue(path_utils.basename_filtered(first_file25) in contents_read)
        self.assertFalse(path_utils.concat_path(path_utils.basename_filtered(first_sub1), path_utils.basename_filtered(first_sub1_file9)) in contents_read)
        self.assertFalse(path_utils.concat_path(path_utils.basename_filtered(first_sub1), path_utils.basename_filtered(first_sub1_another), path_utils.basename_filtered(first_sub1_another_file10)) in contents_read)
        self.assertTrue(path_utils.concat_path(path_utils.basename_filtered(first_sub1), path_utils.basename_filtered(first_sub1_another), path_utils.basename_filtered(first_sub1_another_file17)) in contents_read)
        self.assertTrue(path_utils.concat_path(path_utils.basename_filtered(first_sub1), path_utils.basename_filtered(first_sub1_another), path_utils.basename_filtered(first_sub1_another_file30)) in contents_read)
        self.assertFalse(path_utils.concat_path(path_utils.basename_filtered(first_sub2), path_utils.basename_filtered(first_sub2_file9)) in contents_read)
        self.assertFalse(path_utils.concat_path(path_utils.basename_filtered(first_sub2), path_utils.basename_filtered(first_sub2_another), path_utils.basename_filtered(first_sub2_another_file10)) in contents_read)
        self.assertTrue(path_utils.concat_path(path_utils.basename_filtered(first_sub2), path_utils.basename_filtered(first_sub2_another), path_utils.basename_filtered(first_sub2_another_file19)) in contents_read)
        self.assertTrue(path_utils.concat_path(path_utils.basename_filtered(first_sub2), path_utils.basename_filtered(first_sub2_another), path_utils.basename_filtered(first_sub2_another_file19_renamed)) in contents_read)
        self.assertFalse(path_utils.concat_path(path_utils.basename_filtered(first_sub2), path_utils.basename_filtered(first_sub2_another), path_utils.basename_filtered(first_sub1_another_file10_renamed)) in contents_read)
        self.assertEqual(contents_read.count("new file mode"), 2)
        self.assertEqual(contents_read.count("deleted file mode"), 3)
        self.assertEqual(contents_read.count("rename from"), 1)
        self.assertEqual(contents_read.count("rename to"), 1)

    def testCollectPatchStagedSub(self):

        newfile = path_utils.concat_path(self.second_sub, "newfile_secondsub.txt")
        create_and_write_file.create_file_contents(newfile, "newfilecontents_secondsub")

        self.assertTrue(git_wrapper.stage(self.second_sub))

        v, r = collect_git_patch.collect_git_patch_staged(self.second_sub, self.storage_path, "include", [], [])
        self.assertTrue(v)

        patch_file = path_utils.concat_path(self.storage_path, self.second_sub, "staged.patch")
        self.assertTrue(os.path.exists(patch_file))
        self.assertEqual(r, patch_file)

        contents_read = getcontents.getcontents(patch_file)

        self.assertTrue("newfilecontents_secondsub" in contents_read)

    def testCollectPatchStaged_Filtering1(self):

        first_file4 = path_utils.concat_path(self.first_repo, "file4.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file4.txt", "first-file4-content", "first-file4-msg")
        self.assertTrue(v)

        first_file5 = path_utils.concat_path(self.first_repo, "file5.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file5.txt", "first-file5-content", "first-file5-msg")
        self.assertTrue(v)

        first_file6 = path_utils.concat_path(self.first_repo, "file6.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file6.txt", "first-file6-content", "first-file6-msg")
        self.assertTrue(v)

        first_file7 = path_utils.concat_path(self.first_repo, "file7.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file7.txt", "first-file7-content", "first-file7-msg")
        self.assertTrue(v)

        first_file8 = path_utils.concat_path(self.first_repo, "file8.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file8.txt", "first-file8-content", "first-file8-msg")
        self.assertTrue(v)

        first_sub1 = path_utils.concat_path(self.first_repo, "sub1")
        self.assertFalse(os.path.exists(first_sub1))
        os.mkdir(first_sub1)
        self.assertTrue(os.path.exists(first_sub1))

        first_sub1_file9 = path_utils.concat_path(first_sub1, "file9.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub1/file9.txt", "first-sub1-file9-content", "first-sub1-file9-msg")
        self.assertTrue(v)

        first_sub1_another = path_utils.concat_path(first_sub1, "another")
        self.assertFalse(os.path.exists(first_sub1_another))
        os.mkdir(first_sub1_another)
        self.assertTrue(os.path.exists(first_sub1_another))

        first_sub1_another_file10 = path_utils.concat_path(first_sub1_another, "file10.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub1/another/file10.txt", "first-sub1-another-file10-content", "first-sub1-another-file10-msg")
        self.assertTrue(v)

        first_sub1_another_file17 = path_utils.concat_path(first_sub1_another, "file17.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub1/another/file17.txt", "first-sub1-another-file17-content", "first-sub1-another-file17-msg")
        self.assertTrue(v)

        first_sub2 = path_utils.concat_path(self.first_repo, "sub2")
        self.assertFalse(os.path.exists(first_sub2))
        os.mkdir(first_sub2)
        self.assertTrue(os.path.exists(first_sub2))

        first_sub2_file9 = path_utils.concat_path(first_sub2, "file9.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub2/file9.txt", "first-sub2-file9-content", "first-sub2-file9-msg")
        self.assertTrue(v)

        first_sub2_another = path_utils.concat_path(first_sub2, "another")
        self.assertFalse(os.path.exists(first_sub2_another))
        os.mkdir(first_sub2_another)
        self.assertTrue(os.path.exists(first_sub2_another))

        first_sub2_another_file10 = path_utils.concat_path(first_sub2_another, "file10.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub2/another/file10.txt", "first-sub2-another-file10-content", "first-sub2-another-file10-msg")
        self.assertTrue(v)

        first_sub2_another_file19 = path_utils.concat_path(first_sub2_another, "file19.txt")
        first_sub2_another_file19_renamed = path_utils.concat_path(first_sub2_another, "file19_renamed.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub2/another/file19.txt", "first-sub2-another-file19-content", "first-sub2-another-file19-msg")
        self.assertTrue(v)

        open_and_update_file.update_file_contents(self.first_file1, "more file1")
        open_and_update_file.update_file_contents(self.first_file3, "more file3")

        self.assertTrue(os.path.exists(first_file4))
        os.unlink(first_file4)
        self.assertFalse(os.path.exists(first_file4))

        self.assertTrue(os.path.exists(first_file7))
        os.unlink(first_file7)
        self.assertFalse(os.path.exists(first_file7))

        self.assertTrue(os.path.exists(first_sub1_another_file17))
        os.unlink(first_sub1_another_file17)
        self.assertFalse(os.path.exists(first_sub1_another_file17))

        self.assertTrue(path_utils.copy_to_and_rename(first_sub2_another_file19, path_utils.dirname_filtered(first_sub2_another_file19_renamed), path_utils.basename_filtered(first_sub2_another_file19_renamed)))
        os.unlink(first_sub2_another_file19)

        first_file25 = path_utils.concat_path(self.first_repo, "file25.txt")
        create_and_write_file.create_file_contents(first_file25, "file25-contents")

        first_sub1_another_file30 = path_utils.concat_path(first_sub1_another, "file30.txt")
        create_and_write_file.create_file_contents(first_sub1_another_file30, "file30-contents")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = collect_git_patch.collect_git_patch_staged(self.first_repo, self.storage_path, "exclude", ["*/file19_renamed.txt"], [])
        self.assertTrue(v)
        self.assertTrue(os.path.exists(r))

        patch_file = path_utils.concat_path(self.storage_path, self.first_repo, "staged.patch")
        self.assertTrue(os.path.exists(patch_file))
        self.assertEqual(r, patch_file)

        contents_read = getcontents.getcontents(patch_file)

        self.assertFalse(path_utils.basename_filtered(self.first_file1) in contents_read)
        self.assertFalse(path_utils.basename_filtered(self.first_file2) in contents_read)
        self.assertFalse(path_utils.basename_filtered(self.first_file3) in contents_read)
        self.assertFalse(path_utils.basename_filtered(first_file4) in contents_read)
        self.assertFalse(path_utils.basename_filtered(first_file5) in contents_read)
        self.assertFalse(path_utils.basename_filtered(first_file6) in contents_read)
        self.assertFalse(path_utils.basename_filtered(first_file7) in contents_read)
        self.assertFalse(path_utils.basename_filtered(first_file8) in contents_read)
        self.assertFalse(path_utils.basename_filtered(first_file25) in contents_read)
        self.assertFalse(path_utils.concat_path(path_utils.basename_filtered(first_sub1), path_utils.basename_filtered(first_sub1_file9)) in contents_read)
        self.assertFalse(path_utils.concat_path(path_utils.basename_filtered(first_sub1), path_utils.basename_filtered(first_sub1_another), path_utils.basename_filtered(first_sub1_another_file10)) in contents_read)
        self.assertFalse(path_utils.concat_path(path_utils.basename_filtered(first_sub1), path_utils.basename_filtered(first_sub1_another), path_utils.basename_filtered(first_sub1_another_file17)) in contents_read)
        self.assertFalse(path_utils.concat_path(path_utils.basename_filtered(first_sub1), path_utils.basename_filtered(first_sub1_another), path_utils.basename_filtered(first_sub1_another_file30)) in contents_read)
        self.assertFalse(path_utils.concat_path(path_utils.basename_filtered(first_sub2), path_utils.basename_filtered(first_sub2_file9)) in contents_read)
        self.assertFalse(path_utils.concat_path(path_utils.basename_filtered(first_sub2), path_utils.basename_filtered(first_sub2_another), path_utils.basename_filtered(first_sub2_another_file10)) in contents_read)
        self.assertTrue(path_utils.concat_path(path_utils.basename_filtered(first_sub2), path_utils.basename_filtered(first_sub2_another), path_utils.basename_filtered(first_sub2_another_file19)) in contents_read)
        self.assertTrue(path_utils.concat_path(path_utils.basename_filtered(first_sub2), path_utils.basename_filtered(first_sub2_another), path_utils.basename_filtered(first_sub2_another_file19_renamed)) in contents_read)
        self.assertEqual(contents_read.count("new file mode"), 0)
        self.assertEqual(contents_read.count("deleted file mode"), 0)
        self.assertEqual(contents_read.count("rename from"), 1)
        self.assertEqual(contents_read.count("rename to"), 1)

    def testCollectPatchStaged_Filtering2(self):

        first_file4 = path_utils.concat_path(self.first_repo, "file4.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file4.txt", "first-file4-content", "first-file4-msg")
        self.assertTrue(v)

        first_file5 = path_utils.concat_path(self.first_repo, "file5.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file5.txt", "first-file5-content", "first-file5-msg")
        self.assertTrue(v)

        first_file6 = path_utils.concat_path(self.first_repo, "file6.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file6.txt", "first-file6-content", "first-file6-msg")
        self.assertTrue(v)

        first_file7 = path_utils.concat_path(self.first_repo, "file7.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file7.txt", "first-file7-content", "first-file7-msg")
        self.assertTrue(v)

        first_file8 = path_utils.concat_path(self.first_repo, "file8.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file8.txt", "first-file8-content", "first-file8-msg")
        self.assertTrue(v)

        first_sub1 = path_utils.concat_path(self.first_repo, "sub1")
        self.assertFalse(os.path.exists(first_sub1))
        os.mkdir(first_sub1)
        self.assertTrue(os.path.exists(first_sub1))

        first_sub1_file9 = path_utils.concat_path(first_sub1, "file9.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub1/file9.txt", "first-sub1-file9-content", "first-sub1-file9-msg")
        self.assertTrue(v)

        first_sub1_another = path_utils.concat_path(first_sub1, "another")
        self.assertFalse(os.path.exists(first_sub1_another))
        os.mkdir(first_sub1_another)
        self.assertTrue(os.path.exists(first_sub1_another))

        first_sub1_another_file10 = path_utils.concat_path(first_sub1_another, "file10.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub1/another/file10.txt", "first-sub1-another-file10-content", "first-sub1-another-file10-msg")
        self.assertTrue(v)

        first_sub1_another_file17 = path_utils.concat_path(first_sub1_another, "file17.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub1/another/file17.txt", "first-sub1-another-file17-content", "first-sub1-another-file17-msg")
        self.assertTrue(v)

        first_sub2 = path_utils.concat_path(self.first_repo, "sub2")
        self.assertFalse(os.path.exists(first_sub2))
        os.mkdir(first_sub2)
        self.assertTrue(os.path.exists(first_sub2))

        first_sub2_file9 = path_utils.concat_path(first_sub2, "file9.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub2/file9.txt", "first-sub2-file9-content", "first-sub2-file9-msg")
        self.assertTrue(v)

        first_sub2_another = path_utils.concat_path(first_sub2, "another")
        self.assertFalse(os.path.exists(first_sub2_another))
        os.mkdir(first_sub2_another)
        self.assertTrue(os.path.exists(first_sub2_another))

        first_sub2_another_file10 = path_utils.concat_path(first_sub2_another, "file10.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub2/another/file10.txt", "first-sub2-another-file10-content", "first-sub2-another-file10-msg")
        self.assertTrue(v)

        first_sub2_another_file19 = path_utils.concat_path(first_sub2_another, "file19.txt")
        first_sub2_another_file19_renamed = path_utils.concat_path(first_sub2_another, "file19_renamed.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub2/another/file19.txt", "first-sub2-another-file19-content", "first-sub2-another-file19-msg")
        self.assertTrue(v)

        open_and_update_file.update_file_contents(self.first_file1, "more file1")
        open_and_update_file.update_file_contents(self.first_file3, "more file3")

        self.assertTrue(os.path.exists(first_file4))
        os.unlink(first_file4)
        self.assertFalse(os.path.exists(first_file4))

        self.assertTrue(os.path.exists(first_file7))
        os.unlink(first_file7)
        self.assertFalse(os.path.exists(first_file7))

        self.assertTrue(os.path.exists(first_sub1_another_file17))
        os.unlink(first_sub1_another_file17)
        self.assertFalse(os.path.exists(first_sub1_another_file17))

        self.assertTrue(path_utils.copy_to_and_rename(first_sub2_another_file19, path_utils.dirname_filtered(first_sub2_another_file19_renamed), path_utils.basename_filtered(first_sub2_another_file19_renamed)))
        os.unlink(first_sub2_another_file19)

        first_file25 = path_utils.concat_path(self.first_repo, "file25.txt")
        create_and_write_file.create_file_contents(first_file25, "file25-contents")

        first_sub1_another_file30 = path_utils.concat_path(first_sub1_another, "file30.txt")
        create_and_write_file.create_file_contents(first_sub1_another_file30, "file30-contents")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = collect_git_patch.collect_git_patch_staged(self.first_repo, self.storage_path, "include", [], ["*/sub2/*"])
        self.assertTrue(v)
        self.assertTrue(os.path.exists(r))

        patch_file = path_utils.concat_path(self.storage_path, self.first_repo, "staged.patch")
        self.assertTrue(os.path.exists(patch_file))
        self.assertEqual(r, patch_file)

        contents_read = getcontents.getcontents(patch_file)

        self.assertTrue(path_utils.basename_filtered(self.first_file1) in contents_read)
        self.assertFalse(path_utils.basename_filtered(self.first_file2) in contents_read)
        self.assertTrue(path_utils.basename_filtered(self.first_file3) in contents_read)
        self.assertTrue(path_utils.basename_filtered(first_file4) in contents_read)
        self.assertFalse(path_utils.basename_filtered(first_file5) in contents_read)
        self.assertFalse(path_utils.basename_filtered(first_file6) in contents_read)
        self.assertTrue(path_utils.basename_filtered(first_file7) in contents_read)
        self.assertFalse(path_utils.basename_filtered(first_file8) in contents_read)
        self.assertTrue(path_utils.basename_filtered(first_file25) in contents_read)
        self.assertFalse(path_utils.concat_path(path_utils.basename_filtered(first_sub1), path_utils.basename_filtered(first_sub1_file9)) in contents_read)
        self.assertFalse(path_utils.concat_path(path_utils.basename_filtered(first_sub1), path_utils.basename_filtered(first_sub1_another), path_utils.basename_filtered(first_sub1_another_file10)) in contents_read)
        self.assertTrue(path_utils.concat_path(path_utils.basename_filtered(first_sub1), path_utils.basename_filtered(first_sub1_another), path_utils.basename_filtered(first_sub1_another_file17)) in contents_read)
        self.assertTrue(path_utils.concat_path(path_utils.basename_filtered(first_sub1), path_utils.basename_filtered(first_sub1_another), path_utils.basename_filtered(first_sub1_another_file30)) in contents_read)
        self.assertFalse(path_utils.concat_path(path_utils.basename_filtered(first_sub2), path_utils.basename_filtered(first_sub2_file9)) in contents_read)
        self.assertFalse(path_utils.concat_path(path_utils.basename_filtered(first_sub2), path_utils.basename_filtered(first_sub2_another), path_utils.basename_filtered(first_sub2_another_file10)) in contents_read)
        self.assertFalse(path_utils.concat_path(path_utils.basename_filtered(first_sub2), path_utils.basename_filtered(first_sub2_another), path_utils.basename_filtered(first_sub2_another_file19)) in contents_read)
        self.assertFalse(path_utils.concat_path(path_utils.basename_filtered(first_sub2), path_utils.basename_filtered(first_sub2_another), path_utils.basename_filtered(first_sub2_another_file19_renamed)) in contents_read)
        self.assertEqual(contents_read.count("new file mode"), 2)
        self.assertEqual(contents_read.count("deleted file mode"), 3)
        self.assertEqual(contents_read.count("rename from"), 0)
        self.assertEqual(contents_read.count("rename to"), 0)

    def testCollectPatchStaged_Filtering3(self):

        first_file4 = path_utils.concat_path(self.first_repo, "file4.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file4.txt", "first-file4-content", "first-file4-msg")
        self.assertTrue(v)

        first_file5 = path_utils.concat_path(self.first_repo, "file5.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file5.txt", "first-file5-content", "first-file5-msg")
        self.assertTrue(v)

        first_file6 = path_utils.concat_path(self.first_repo, "file6.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file6.txt", "first-file6-content", "first-file6-msg")
        self.assertTrue(v)

        first_file7 = path_utils.concat_path(self.first_repo, "file7.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file7.txt", "first-file7-content", "first-file7-msg")
        self.assertTrue(v)

        first_file8 = path_utils.concat_path(self.first_repo, "file8.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file8.txt", "first-file8-content", "first-file8-msg")
        self.assertTrue(v)

        first_sub1 = path_utils.concat_path(self.first_repo, "sub1")
        self.assertFalse(os.path.exists(first_sub1))
        os.mkdir(first_sub1)
        self.assertTrue(os.path.exists(first_sub1))

        first_sub1_file9 = path_utils.concat_path(first_sub1, "file9.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub1/file9.txt", "first-sub1-file9-content", "first-sub1-file9-msg")
        self.assertTrue(v)

        first_sub1_another = path_utils.concat_path(first_sub1, "another")
        self.assertFalse(os.path.exists(first_sub1_another))
        os.mkdir(first_sub1_another)
        self.assertTrue(os.path.exists(first_sub1_another))

        first_sub1_another_file10 = path_utils.concat_path(first_sub1_another, "file10.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub1/another/file10.txt", "first-sub1-another-file10-content", "first-sub1-another-file10-msg")
        self.assertTrue(v)

        first_sub1_another_file17 = path_utils.concat_path(first_sub1_another, "file17.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub1/another/file17.txt", "first-sub1-another-file17-content", "first-sub1-another-file17-msg")
        self.assertTrue(v)

        first_sub2 = path_utils.concat_path(self.first_repo, "sub2")
        self.assertFalse(os.path.exists(first_sub2))
        os.mkdir(first_sub2)
        self.assertTrue(os.path.exists(first_sub2))

        first_sub2_file9 = path_utils.concat_path(first_sub2, "file9.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub2/file9.txt", "first-sub2-file9-content", "first-sub2-file9-msg")
        self.assertTrue(v)

        first_sub2_another = path_utils.concat_path(first_sub2, "another")
        self.assertFalse(os.path.exists(first_sub2_another))
        os.mkdir(first_sub2_another)
        self.assertTrue(os.path.exists(first_sub2_another))

        first_sub2_another_file10 = path_utils.concat_path(first_sub2_another, "file10.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub2/another/file10.txt", "first-sub2-another-file10-content", "first-sub2-another-file10-msg")
        self.assertTrue(v)

        first_sub2_another_file19 = path_utils.concat_path(first_sub2_another, "file19.txt")
        first_sub2_another_file19_renamed = path_utils.concat_path(first_sub2_another, "file19_renamed.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub2/another/file19.txt", "first-sub2-another-file19-content", "first-sub2-another-file19-msg")
        self.assertTrue(v)

        open_and_update_file.update_file_contents(self.first_file1, "more file1")
        open_and_update_file.update_file_contents(self.first_file3, "more file3")

        self.assertTrue(os.path.exists(first_file4))
        os.unlink(first_file4)
        self.assertFalse(os.path.exists(first_file4))

        self.assertTrue(os.path.exists(first_file7))
        os.unlink(first_file7)
        self.assertFalse(os.path.exists(first_file7))

        self.assertTrue(os.path.exists(first_sub1_another_file17))
        os.unlink(first_sub1_another_file17)
        self.assertFalse(os.path.exists(first_sub1_another_file17))

        self.assertTrue(path_utils.copy_to_and_rename(first_sub2_another_file19, path_utils.dirname_filtered(first_sub2_another_file19_renamed), path_utils.basename_filtered(first_sub2_another_file19_renamed)))
        os.unlink(first_sub2_another_file19)

        first_file25 = path_utils.concat_path(self.first_repo, "file25.txt")
        create_and_write_file.create_file_contents(first_file25, "file25-contents")

        first_sub1_another_file30 = path_utils.concat_path(first_sub1_another, "file30.txt")
        create_and_write_file.create_file_contents(first_sub1_another_file30, "file30-contents")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = collect_git_patch.collect_git_patch_staged(self.first_repo, self.storage_path, "exclude", ["*/file25.txt", "*/file30.txt"], [])
        self.assertTrue(v)
        self.assertTrue(os.path.exists(r))

        patch_file = path_utils.concat_path(self.storage_path, self.first_repo, "staged.patch")
        self.assertTrue(os.path.exists(patch_file))
        self.assertEqual(r, patch_file)

        contents_read = getcontents.getcontents(patch_file)

        self.assertFalse(path_utils.basename_filtered(self.first_file1) in contents_read)
        self.assertFalse(path_utils.basename_filtered(self.first_file2) in contents_read)
        self.assertFalse(path_utils.basename_filtered(self.first_file3) in contents_read)
        self.assertFalse(path_utils.basename_filtered(first_file4) in contents_read)
        self.assertFalse(path_utils.basename_filtered(first_file5) in contents_read)
        self.assertFalse(path_utils.basename_filtered(first_file6) in contents_read)
        self.assertFalse(path_utils.basename_filtered(first_file7) in contents_read)
        self.assertFalse(path_utils.basename_filtered(first_file8) in contents_read)
        self.assertTrue(path_utils.basename_filtered(first_file25) in contents_read)
        self.assertFalse(path_utils.concat_path(path_utils.basename_filtered(first_sub1), path_utils.basename_filtered(first_sub1_file9)) in contents_read)
        self.assertFalse(path_utils.concat_path(path_utils.basename_filtered(first_sub1), path_utils.basename_filtered(first_sub1_another), path_utils.basename_filtered(first_sub1_another_file10)) in contents_read)
        self.assertFalse(path_utils.concat_path(path_utils.basename_filtered(first_sub1), path_utils.basename_filtered(first_sub1_another), path_utils.basename_filtered(first_sub1_another_file17)) in contents_read)
        self.assertTrue(path_utils.concat_path(path_utils.basename_filtered(first_sub1), path_utils.basename_filtered(first_sub1_another), path_utils.basename_filtered(first_sub1_another_file30)) in contents_read)
        self.assertFalse(path_utils.concat_path(path_utils.basename_filtered(first_sub2), path_utils.basename_filtered(first_sub2_file9)) in contents_read)
        self.assertFalse(path_utils.concat_path(path_utils.basename_filtered(first_sub2), path_utils.basename_filtered(first_sub2_another), path_utils.basename_filtered(first_sub2_another_file10)) in contents_read)
        self.assertFalse(path_utils.concat_path(path_utils.basename_filtered(first_sub2), path_utils.basename_filtered(first_sub2_another), path_utils.basename_filtered(first_sub2_another_file19)) in contents_read)
        self.assertFalse(path_utils.concat_path(path_utils.basename_filtered(first_sub2), path_utils.basename_filtered(first_sub2_another), path_utils.basename_filtered(first_sub2_another_file19_renamed)) in contents_read)
        self.assertEqual(contents_read.count("new file mode"), 2)
        self.assertEqual(contents_read.count("deleted file mode"), 0)
        self.assertEqual(contents_read.count("rename from"), 0)
        self.assertEqual(contents_read.count("rename to"), 0)

    def testCollectPatchStaged_Filtering4(self):

        first_file4 = path_utils.concat_path(self.first_repo, "file4.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file4.txt", "first-file4-content", "first-file4-msg")
        self.assertTrue(v)

        first_file5 = path_utils.concat_path(self.first_repo, "file5.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file5.txt", "first-file5-content", "first-file5-msg")
        self.assertTrue(v)

        first_file6 = path_utils.concat_path(self.first_repo, "file6.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file6.txt", "first-file6-content", "first-file6-msg")
        self.assertTrue(v)

        first_file7 = path_utils.concat_path(self.first_repo, "file7.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file7.txt", "first-file7-content", "first-file7-msg")
        self.assertTrue(v)

        first_file8 = path_utils.concat_path(self.first_repo, "file8.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file8.txt", "first-file8-content", "first-file8-msg")
        self.assertTrue(v)

        first_sub1 = path_utils.concat_path(self.first_repo, "sub1")
        self.assertFalse(os.path.exists(first_sub1))
        os.mkdir(first_sub1)
        self.assertTrue(os.path.exists(first_sub1))

        first_sub1_file9 = path_utils.concat_path(first_sub1, "file9.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub1/file9.txt", "first-sub1-file9-content", "first-sub1-file9-msg")
        self.assertTrue(v)

        first_sub1_another = path_utils.concat_path(first_sub1, "another")
        self.assertFalse(os.path.exists(first_sub1_another))
        os.mkdir(first_sub1_another)
        self.assertTrue(os.path.exists(first_sub1_another))

        first_sub1_another_file10 = path_utils.concat_path(first_sub1_another, "file10.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub1/another/file10.txt", "first-sub1-another-file10-content", "first-sub1-another-file10-msg")
        self.assertTrue(v)

        first_sub1_another_file17 = path_utils.concat_path(first_sub1_another, "file17.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub1/another/file17.txt", "first-sub1-another-file17-content", "first-sub1-another-file17-msg")
        self.assertTrue(v)

        first_sub2 = path_utils.concat_path(self.first_repo, "sub2")
        self.assertFalse(os.path.exists(first_sub2))
        os.mkdir(first_sub2)
        self.assertTrue(os.path.exists(first_sub2))

        first_sub2_file9 = path_utils.concat_path(first_sub2, "file9.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub2/file9.txt", "first-sub2-file9-content", "first-sub2-file9-msg")
        self.assertTrue(v)

        first_sub2_another = path_utils.concat_path(first_sub2, "another")
        self.assertFalse(os.path.exists(first_sub2_another))
        os.mkdir(first_sub2_another)
        self.assertTrue(os.path.exists(first_sub2_another))

        first_sub2_another_file10 = path_utils.concat_path(first_sub2_another, "file10.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub2/another/file10.txt", "first-sub2-another-file10-content", "first-sub2-another-file10-msg")
        self.assertTrue(v)

        first_sub2_another_file19 = path_utils.concat_path(first_sub2_another, "file19.txt")
        first_sub2_another_file19_renamed = path_utils.concat_path(first_sub2_another, "file19_renamed.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub2/another/file19.txt", "first-sub2-another-file19-content", "first-sub2-another-file19-msg")
        self.assertTrue(v)

        open_and_update_file.update_file_contents(self.first_file1, "more file1")
        open_and_update_file.update_file_contents(self.first_file3, "more file3")

        self.assertTrue(os.path.exists(first_file4))
        os.unlink(first_file4)
        self.assertFalse(os.path.exists(first_file4))

        self.assertTrue(os.path.exists(first_file7))
        os.unlink(first_file7)
        self.assertFalse(os.path.exists(first_file7))

        self.assertTrue(os.path.exists(first_sub1_another_file17))
        os.unlink(first_sub1_another_file17)
        self.assertFalse(os.path.exists(first_sub1_another_file17))

        self.assertTrue(path_utils.copy_to_and_rename(first_sub2_another_file19, path_utils.dirname_filtered(first_sub2_another_file19_renamed), path_utils.basename_filtered(first_sub2_another_file19_renamed)))
        os.unlink(first_sub2_another_file19)

        first_file25 = path_utils.concat_path(self.first_repo, "file25.txt")
        create_and_write_file.create_file_contents(first_file25, "file25-contents")

        first_sub1_another_file30 = path_utils.concat_path(first_sub1_another, "file30.txt")
        create_and_write_file.create_file_contents(first_sub1_another_file30, "file30-contents")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = collect_git_patch.collect_git_patch_staged(self.first_repo, self.storage_path, "exclude", ["*/file4.txt", "*/file7.txt"], [])
        self.assertTrue(v)
        self.assertTrue(os.path.exists(r))

        patch_file = path_utils.concat_path(self.storage_path, self.first_repo, "staged.patch")
        self.assertTrue(os.path.exists(patch_file))
        self.assertEqual(r, patch_file)

        contents_read = getcontents.getcontents(patch_file)

        self.assertFalse(path_utils.basename_filtered(self.first_file1) in contents_read)
        self.assertFalse(path_utils.basename_filtered(self.first_file2) in contents_read)
        self.assertFalse(path_utils.basename_filtered(self.first_file3) in contents_read)
        self.assertTrue(path_utils.basename_filtered(first_file4) in contents_read)
        self.assertFalse(path_utils.basename_filtered(first_file5) in contents_read)
        self.assertFalse(path_utils.basename_filtered(first_file6) in contents_read)
        self.assertTrue(path_utils.basename_filtered(first_file7) in contents_read)
        self.assertFalse(path_utils.basename_filtered(first_file8) in contents_read)
        self.assertFalse(path_utils.basename_filtered(first_file25) in contents_read)
        self.assertFalse(path_utils.concat_path(path_utils.basename_filtered(first_sub1), path_utils.basename_filtered(first_sub1_file9)) in contents_read)
        self.assertFalse(path_utils.concat_path(path_utils.basename_filtered(first_sub1), path_utils.basename_filtered(first_sub1_another), path_utils.basename_filtered(first_sub1_another_file10)) in contents_read)
        self.assertFalse(path_utils.concat_path(path_utils.basename_filtered(first_sub1), path_utils.basename_filtered(first_sub1_another), path_utils.basename_filtered(first_sub1_another_file17)) in contents_read)
        self.assertFalse(path_utils.concat_path(path_utils.basename_filtered(first_sub1), path_utils.basename_filtered(first_sub1_another), path_utils.basename_filtered(first_sub1_another_file30)) in contents_read)
        self.assertFalse(path_utils.concat_path(path_utils.basename_filtered(first_sub2), path_utils.basename_filtered(first_sub2_file9)) in contents_read)
        self.assertFalse(path_utils.concat_path(path_utils.basename_filtered(first_sub2), path_utils.basename_filtered(first_sub2_another), path_utils.basename_filtered(first_sub2_another_file10)) in contents_read)
        self.assertFalse(path_utils.concat_path(path_utils.basename_filtered(first_sub2), path_utils.basename_filtered(first_sub2_another), path_utils.basename_filtered(first_sub2_another_file19)) in contents_read)
        self.assertFalse(path_utils.concat_path(path_utils.basename_filtered(first_sub2), path_utils.basename_filtered(first_sub2_another), path_utils.basename_filtered(first_sub2_another_file19_renamed)) in contents_read)
        self.assertEqual(contents_read.count("new file mode"), 0)
        self.assertEqual(contents_read.count("deleted file mode"), 2)
        self.assertEqual(contents_read.count("rename from"), 0)
        self.assertEqual(contents_read.count("rename to"), 0)

    def testCollectPatchStaged_Filtering5(self):

        first_file4 = path_utils.concat_path(self.first_repo, "file4.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file4.txt", "first-file4-content", "first-file4-msg")
        self.assertTrue(v)

        first_file5 = path_utils.concat_path(self.first_repo, "file5.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file5.txt", "first-file5-content", "first-file5-msg")
        self.assertTrue(v)

        first_file6 = path_utils.concat_path(self.first_repo, "file6.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file6.txt", "first-file6-content", "first-file6-msg")
        self.assertTrue(v)

        first_file7 = path_utils.concat_path(self.first_repo, "file7.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file7.txt", "first-file7-content", "first-file7-msg")
        self.assertTrue(v)

        first_file8 = path_utils.concat_path(self.first_repo, "file8.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "file8.txt", "first-file8-content", "first-file8-msg")
        self.assertTrue(v)

        first_sub1 = path_utils.concat_path(self.first_repo, "sub1")
        self.assertFalse(os.path.exists(first_sub1))
        os.mkdir(first_sub1)
        self.assertTrue(os.path.exists(first_sub1))

        first_sub1_file9 = path_utils.concat_path(first_sub1, "file9.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub1/file9.txt", "first-sub1-file9-content", "first-sub1-file9-msg")
        self.assertTrue(v)

        first_sub1_another = path_utils.concat_path(first_sub1, "another")
        self.assertFalse(os.path.exists(first_sub1_another))
        os.mkdir(first_sub1_another)
        self.assertTrue(os.path.exists(first_sub1_another))

        first_sub1_another_file10 = path_utils.concat_path(first_sub1_another, "file10.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub1/another/file10.txt", "first-sub1-another-file10-content", "first-sub1-another-file10-msg")
        self.assertTrue(v)

        first_sub1_another_file17 = path_utils.concat_path(first_sub1_another, "file17.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub1/another/file17.txt", "first-sub1-another-file17-content", "first-sub1-another-file17-msg")
        self.assertTrue(v)

        first_sub2 = path_utils.concat_path(self.first_repo, "sub2")
        self.assertFalse(os.path.exists(first_sub2))
        os.mkdir(first_sub2)
        self.assertTrue(os.path.exists(first_sub2))

        first_sub2_file9 = path_utils.concat_path(first_sub2, "file9.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub2/file9.txt", "first-sub2-file9-content", "first-sub2-file9-msg")
        self.assertTrue(v)

        first_sub2_another = path_utils.concat_path(first_sub2, "another")
        self.assertFalse(os.path.exists(first_sub2_another))
        os.mkdir(first_sub2_another)
        self.assertTrue(os.path.exists(first_sub2_another))

        first_sub2_another_file10 = path_utils.concat_path(first_sub2_another, "file10.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub2/another/file10.txt", "first-sub2-another-file10-content", "first-sub2-another-file10-msg")
        self.assertTrue(v)

        first_sub2_another_file19 = path_utils.concat_path(first_sub2_another, "file19.txt")
        first_sub2_another_file19_renamed = path_utils.concat_path(first_sub2_another, "file19_renamed.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, "sub2/another/file19.txt", "first-sub2-another-file19-content", "first-sub2-another-file19-msg")
        self.assertTrue(v)

        open_and_update_file.update_file_contents(self.first_file1, "more file1")
        open_and_update_file.update_file_contents(self.first_file3, "more file3")

        self.assertTrue(os.path.exists(first_file4))
        os.unlink(first_file4)
        self.assertFalse(os.path.exists(first_file4))

        self.assertTrue(os.path.exists(first_file7))
        os.unlink(first_file7)
        self.assertFalse(os.path.exists(first_file7))

        self.assertTrue(os.path.exists(first_sub1_another_file17))
        os.unlink(first_sub1_another_file17)
        self.assertFalse(os.path.exists(first_sub1_another_file17))

        self.assertTrue(path_utils.copy_to_and_rename(first_sub2_another_file19, path_utils.dirname_filtered(first_sub2_another_file19_renamed), path_utils.basename_filtered(first_sub2_another_file19_renamed)))
        os.unlink(first_sub2_another_file19)

        first_file25 = path_utils.concat_path(self.first_repo, "file25.txt")
        create_and_write_file.create_file_contents(first_file25, "file25-contents")

        first_sub1_another_file30 = path_utils.concat_path(first_sub1_another, "file30.txt")
        create_and_write_file.create_file_contents(first_sub1_another_file30, "file30-contents")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = collect_git_patch.collect_git_patch_staged(self.first_repo, self.storage_path, "exclude", ["*/file1.txt"], [])
        self.assertTrue(v)
        self.assertTrue(os.path.exists(r))

        patch_file = path_utils.concat_path(self.storage_path, self.first_repo, "staged.patch")
        self.assertTrue(os.path.exists(patch_file))
        self.assertEqual(r, patch_file)

        contents_read = getcontents.getcontents(patch_file)

        self.assertTrue(path_utils.basename_filtered(self.first_file1) in contents_read)
        self.assertFalse(path_utils.basename_filtered(self.first_file2) in contents_read)
        self.assertFalse(path_utils.basename_filtered(self.first_file3) in contents_read)
        self.assertFalse(path_utils.basename_filtered(first_file4) in contents_read)
        self.assertFalse(path_utils.basename_filtered(first_file5) in contents_read)
        self.assertFalse(path_utils.basename_filtered(first_file6) in contents_read)
        self.assertFalse(path_utils.basename_filtered(first_file7) in contents_read)
        self.assertFalse(path_utils.basename_filtered(first_file8) in contents_read)
        self.assertFalse(path_utils.basename_filtered(first_file25) in contents_read)
        self.assertFalse(path_utils.concat_path(path_utils.basename_filtered(first_sub1), path_utils.basename_filtered(first_sub1_file9)) in contents_read)
        self.assertFalse(path_utils.concat_path(path_utils.basename_filtered(first_sub1), path_utils.basename_filtered(first_sub1_another), path_utils.basename_filtered(first_sub1_another_file10)) in contents_read)
        self.assertFalse(path_utils.concat_path(path_utils.basename_filtered(first_sub1), path_utils.basename_filtered(first_sub1_another), path_utils.basename_filtered(first_sub1_another_file17)) in contents_read)
        self.assertFalse(path_utils.concat_path(path_utils.basename_filtered(first_sub1), path_utils.basename_filtered(first_sub1_another), path_utils.basename_filtered(first_sub1_another_file30)) in contents_read)
        self.assertFalse(path_utils.concat_path(path_utils.basename_filtered(first_sub2), path_utils.basename_filtered(first_sub2_file9)) in contents_read)
        self.assertFalse(path_utils.concat_path(path_utils.basename_filtered(first_sub2), path_utils.basename_filtered(first_sub2_another), path_utils.basename_filtered(first_sub2_another_file10)) in contents_read)
        self.assertFalse(path_utils.concat_path(path_utils.basename_filtered(first_sub2), path_utils.basename_filtered(first_sub2_another), path_utils.basename_filtered(first_sub2_another_file19)) in contents_read)
        self.assertFalse(path_utils.concat_path(path_utils.basename_filtered(first_sub2), path_utils.basename_filtered(first_sub2_another), path_utils.basename_filtered(first_sub2_another_file19_renamed)) in contents_read)
        self.assertEqual(contents_read.count("new file mode"), 0)
        self.assertEqual(contents_read.count("deleted file mode"), 0)
        self.assertEqual(contents_read.count("rename from"), 0)
        self.assertEqual(contents_read.count("rename to"), 0)

    def testCollectPatchStaged_Filtering6(self):

        first_more1 = path_utils.concat_path(self.first_repo, "more1.txt")
        self.assertFalse(os.path.exists(first_more1))
        create_and_write_file.create_file_contents(first_more1, "more1-contents")
        self.assertTrue(os.path.exists(first_more1))

        first_more2 = path_utils.concat_path(self.first_repo, "more2.txt")
        self.assertFalse(os.path.exists(first_more2))
        create_and_write_file.create_file_contents(first_more2, "more2-contents")
        self.assertTrue(os.path.exists(first_more2))

        open_and_update_file.update_file_contents(self.first_file1, "actual modification, again, file1")
        open_and_update_file.update_file_contents(self.first_file2, "actual modification, again, file2")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 4)
        self.assertTrue(any(first_more1 in s for s in r))
        self.assertTrue(any(first_more2 in s for s in r))
        self.assertTrue(any(self.first_file1 in s for s in r))
        self.assertTrue(any(self.first_file2 in s for s in r))

        v, r = collect_git_patch.collect_git_patch_staged(self.first_repo, self.storage_path, "exclude", [], [])
        self.assertFalse(v)
        self.assertEqual(r, collect_git_patch.ERRMSG_EMPTY)

        patch_file = path_utils.concat_path(self.storage_path, self.first_repo, "staged.patch")
        self.assertFalse(os.path.exists(patch_file))

    def testCollectPatchUnversionedFail(self):

        newfile = path_utils.concat_path(self.first_repo, "newfile.txt")
        create_and_write_file.create_file_contents(newfile, "newfilecontents")

        v, r = collect_git_patch.collect_git_patch_unversioned(self.first_repo, self.storage_path, "include", [], [])
        self.assertTrue(v)

        newfile_storage = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "newfile.txt")
        self.assertTrue(os.path.exists(newfile_storage))
        self.assertEqual(r[0], newfile_storage)

        v, r = collect_git_patch.collect_git_patch_unversioned(self.first_repo, self.storage_path, "include", [], [])
        self.assertFalse(v)

    def testCollectPatchUnversioned1(self):

        newfile = path_utils.concat_path(self.first_repo, "newfile.txt")
        create_and_write_file.create_file_contents(newfile, "newfilecontents")

        newfolder = path_utils.concat_path(self.first_repo, "newfolder")
        os.mkdir(newfolder)

        newfoldernewfile2 = path_utils.concat_path(newfolder, "newfile2.txt")
        create_and_write_file.create_file_contents(newfoldernewfile2, "newfilecontents2")

        newfoldernewfile3 = path_utils.concat_path(newfolder, "newfile3.txt")
        create_and_write_file.create_file_contents(newfoldernewfile3, "newfilecontents3")

        anotherfolder = path_utils.concat_path(newfolder, "anotherfolder")
        os.mkdir(anotherfolder)

        anotherfoldernewfile4 = path_utils.concat_path(anotherfolder, "newfile4.txt")
        create_and_write_file.create_file_contents(anotherfoldernewfile4, "newfilecontents4")

        v, r = collect_git_patch.collect_git_patch_unversioned(self.first_repo, self.storage_path, "include", [], [])
        self.assertTrue(v)

        newfile_storage = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "newfile.txt")
        self.assertTrue(os.path.exists(newfile_storage))
        self.assertTrue(newfile_storage in r)

        contents_read = getcontents.getcontents(newfile_storage)
        self.assertEqual(contents_read, "newfilecontents")

        newfolder_storage = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "newfolder")
        self.assertTrue(os.path.exists(newfolder_storage))

        newfoldernewfile2_storage = path_utils.concat_path(newfolder_storage, "newfile2.txt")
        self.assertTrue(os.path.exists(newfoldernewfile2_storage))
        self.assertTrue(newfoldernewfile2_storage in r)

        contents_read = getcontents.getcontents(newfoldernewfile2_storage)
        self.assertEqual(contents_read, "newfilecontents2")

        newfoldernewfile3_storage = path_utils.concat_path(newfolder_storage, "newfile3.txt")
        self.assertTrue(os.path.exists(newfoldernewfile3_storage))
        self.assertTrue(newfoldernewfile3_storage in r)

        contents_read = getcontents.getcontents(newfoldernewfile3_storage)
        self.assertEqual(contents_read, "newfilecontents3")

        anotherfolder_storage = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "newfolder", "anotherfolder")
        self.assertTrue(os.path.exists(anotherfolder_storage))

        anotherfoldernewfile4_storage = path_utils.concat_path(anotherfolder_storage, "newfile4.txt")
        self.assertTrue(os.path.exists(anotherfoldernewfile4_storage))
        self.assertTrue(anotherfoldernewfile4_storage in r)

        contents_read = getcontents.getcontents(anotherfoldernewfile4_storage)
        self.assertEqual(contents_read, "newfilecontents4")

    def testCollectPatchUnversioned2(self):

        newfolder1 = path_utils.concat_path(self.first_repo, "newfolder1")
        os.mkdir(newfolder1)
        newfolder2 = path_utils.concat_path(newfolder1, "newfolder2")
        os.mkdir(newfolder2)

        newfolder2newfile1 = path_utils.concat_path(newfolder2, "newfile_twolevels.txt")
        create_and_write_file.create_file_contents(newfolder2newfile1, "newfile_twolevels-contents")

        v, r = collect_git_patch.collect_git_patch_unversioned(self.first_repo, self.storage_path, "include", [], [])
        self.assertTrue(v)

        newfile_storage = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "newfolder1", "newfolder2", "newfile_twolevels.txt")
        self.assertTrue(os.path.exists(newfile_storage))
        self.assertEqual(r[0], newfile_storage)

    def testCollectPatchUnversioned3(self):

        newfolder1 = path_utils.concat_path(self.first_repo, "newfolder1")
        os.mkdir(newfolder1)
        newfolder2 = path_utils.concat_path(self.first_repo, "newfolder2")
        os.mkdir(newfolder2)

        newfolder1newfile = path_utils.concat_path(newfolder1, "newfile.txt")
        create_and_write_file.create_file_contents(newfolder1newfile, "newfile-contents")

        newfolder2newfile = path_utils.concat_path(newfolder2, "newfile.txt")
        create_and_write_file.create_file_contents(newfolder2newfile, "newfile-contents")

        v, r = collect_git_patch.collect_git_patch_unversioned(self.first_repo, self.storage_path, "include", [], [])
        self.assertTrue(v)

        newfolder1newfile_storage = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "newfolder1", "newfile.txt")
        self.assertTrue(os.path.exists(newfolder1newfile_storage))
        self.assertEqual(r[0], newfolder1newfile_storage)

        newfolder2newfile_storage = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "newfolder2", "newfile.txt")
        self.assertTrue(os.path.exists(newfolder2newfile_storage))
        self.assertEqual(r[1], newfolder2newfile_storage)

    def testCollectPatchUnversioned4(self):

        first_repo_unvfile73 = path_utils.concat_path(self.first_repo, "unvfile73.txt")
        create_and_write_file.create_file_contents(first_repo_unvfile73, "dummy contents, file73")

        first_repo_sub = path_utils.concat_path(self.first_repo, "sub")
        self.assertFalse(os.path.exists(first_repo_sub))
        os.mkdir(first_repo_sub)
        self.assertTrue(os.path.exists(first_repo_sub))

        first_repo_sub_committed_file = path_utils.concat_path(first_repo_sub, "committed_file.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, path_utils.concat_path(path_utils.basename_filtered(first_repo_sub), path_utils.basename_filtered(first_repo_sub_committed_file)), "committed-file-content", "commit msg, keep subfolder")
        self.assertTrue(v)

        first_repo_sub_unvfile715 = path_utils.concat_path(first_repo_sub, "unvfile715.txt")
        create_and_write_file.create_file_contents(first_repo_sub_unvfile715, "dummy contents, file715")

        first_repo_anothersub = path_utils.concat_path(self.first_repo, "anothersub")
        self.assertFalse(os.path.exists(first_repo_anothersub))
        os.mkdir(first_repo_anothersub)
        self.assertTrue(os.path.exists(first_repo_anothersub))

        first_repo_anothersub_onemorelvl = path_utils.concat_path(first_repo_anothersub, "onemorelvl")
        self.assertFalse(os.path.exists(first_repo_anothersub_onemorelvl))
        os.mkdir(first_repo_anothersub_onemorelvl)
        self.assertTrue(os.path.exists(first_repo_anothersub_onemorelvl))

        first_repo_anothersub_onemorelvl_evenmore = path_utils.concat_path(first_repo_anothersub_onemorelvl, "evenmore")
        self.assertFalse(os.path.exists(first_repo_anothersub_onemorelvl_evenmore))
        os.mkdir(first_repo_anothersub_onemorelvl_evenmore)
        self.assertTrue(os.path.exists(first_repo_anothersub_onemorelvl_evenmore))

        first_repo_anothersub_onemorelvl_evenmore_andyetmore = path_utils.concat_path(first_repo_anothersub_onemorelvl_evenmore, "andyetmore")
        self.assertFalse(os.path.exists(first_repo_anothersub_onemorelvl_evenmore_andyetmore))
        os.mkdir(first_repo_anothersub_onemorelvl_evenmore_andyetmore)
        self.assertTrue(os.path.exists(first_repo_anothersub_onemorelvl_evenmore_andyetmore))

        first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe = path_utils.concat_path(first_repo_anothersub_onemorelvl_evenmore_andyetmore, "leafmaybe")
        self.assertFalse(os.path.exists(first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe))
        os.mkdir(first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe)
        self.assertTrue(os.path.exists(first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe))

        first_repo_anothersub_onemorelvl_evenmore_unvfile330 = path_utils.concat_path(first_repo_anothersub_onemorelvl_evenmore, "unvfile330.txt")
        create_and_write_file.create_file_contents(first_repo_anothersub_onemorelvl_evenmore_unvfile330, "dummy contents, file330")

        first_repo_anothersub_onemorelvl_evenmore_unvfile333 = path_utils.concat_path(first_repo_anothersub_onemorelvl_evenmore, "unvfile333.txt")
        create_and_write_file.create_file_contents(first_repo_anothersub_onemorelvl_evenmore_unvfile333, "dummy contents, file333")

        first_repo_anothersub_onemorelvl_evenmore_andyetmore_unvfile762 = path_utils.concat_path(first_repo_anothersub_onemorelvl_evenmore_andyetmore, "unvfile762.txt")
        create_and_write_file.create_file_contents(first_repo_anothersub_onemorelvl_evenmore_andyetmore_unvfile762, "dummy contents, file762")

        first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe_unvfile308 = path_utils.concat_path(first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe, "unvfile308.txt")
        create_and_write_file.create_file_contents(first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe_unvfile308, "dummy contents, file308")

        first_repo_anothersub_unvfile99 = path_utils.concat_path(first_repo_anothersub, "unvfile99.txt")
        create_and_write_file.create_file_contents(first_repo_anothersub_unvfile99, "dummy contents, file99")

        first_repo_anothersub_unvfile47 = path_utils.concat_path(first_repo_anothersub, "unvfile47.txt")
        create_and_write_file.create_file_contents(first_repo_anothersub_unvfile47, "dummy contents, file47")

        self.assertTrue(os.path.exists(self.first_file1))
        self.assertTrue(os.path.exists(self.first_file2))
        self.assertTrue(os.path.exists(self.first_file3))
        self.assertTrue(os.path.exists(first_repo_sub_committed_file))
        self.assertTrue(os.path.exists(first_repo_unvfile73))
        self.assertTrue(os.path.exists(first_repo_sub_unvfile715))
        self.assertTrue(os.path.exists(first_repo_anothersub_onemorelvl_evenmore_unvfile330))
        self.assertTrue(os.path.exists(first_repo_anothersub_onemorelvl_evenmore_unvfile333))
        self.assertTrue(os.path.exists(first_repo_anothersub_onemorelvl_evenmore_andyetmore_unvfile762))
        self.assertTrue(os.path.exists(first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe_unvfile308))
        self.assertTrue(os.path.exists(first_repo_anothersub_unvfile99))
        self.assertTrue(os.path.exists(first_repo_anothersub_unvfile47))

        stored_first_file1 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", path_utils.basename_filtered(self.first_file1))
        stored_first_file2 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", path_utils.basename_filtered(self.first_file2))
        stored_first_file3 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", path_utils.basename_filtered( self.first_file3))
        stored_first_repo_sub_committed_file = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "sub", path_utils.basename_filtered(first_repo_sub_committed_file))
        stored_first_repo_unvfile73 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", path_utils.basename_filtered(first_repo_unvfile73))
        stored_first_repo_sub_unvfile715 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "sub", path_utils.basename_filtered(first_repo_sub_unvfile715))
        stored_first_repo_anothersub_onemorelvl_evenmore_unvfile330 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "anothersub", "onemorelvl", "evenmore", path_utils.basename_filtered(first_repo_anothersub_onemorelvl_evenmore_unvfile330))
        stored_first_repo_anothersub_onemorelvl_evenmore_unvfile333 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "anothersub", "onemorelvl", "evenmore", path_utils.basename_filtered(first_repo_anothersub_onemorelvl_evenmore_unvfile333))
        stored_first_repo_anothersub_onemorelvl_evenmore_andyetmore_unvfile762 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "anothersub", "onemorelvl", "evenmore", "andyetmore", path_utils.basename_filtered(first_repo_anothersub_onemorelvl_evenmore_andyetmore_unvfile762))
        stored_first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe_unvfile308 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "anothersub", "onemorelvl", "evenmore", "andyetmore", "leafmaybe", path_utils.basename_filtered(first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe_unvfile308))
        stored_first_repo_anothersub_unvfile99 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "anothersub", path_utils.basename_filtered(first_repo_anothersub_unvfile99))
        stored_first_repo_anothersub_unvfile47 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "anothersub", path_utils.basename_filtered(first_repo_anothersub_unvfile47))

        self.assertFalse(os.path.exists(stored_first_file1))
        self.assertFalse(os.path.exists(stored_first_file2))
        self.assertFalse(os.path.exists(stored_first_file3))
        self.assertFalse(os.path.exists(stored_first_repo_sub_committed_file))
        self.assertFalse(os.path.exists(stored_first_repo_unvfile73))
        self.assertFalse(os.path.exists(stored_first_repo_sub_unvfile715))
        self.assertFalse(os.path.exists(stored_first_repo_anothersub_onemorelvl_evenmore_unvfile330))
        self.assertFalse(os.path.exists(stored_first_repo_anothersub_onemorelvl_evenmore_unvfile333))
        self.assertFalse(os.path.exists(stored_first_repo_anothersub_onemorelvl_evenmore_andyetmore_unvfile762))
        self.assertFalse(os.path.exists(stored_first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe_unvfile308))
        self.assertFalse(os.path.exists(stored_first_repo_anothersub_unvfile99))
        self.assertFalse(os.path.exists(stored_first_repo_anothersub_unvfile47))

        v, r = collect_git_patch.collect_git_patch_unversioned(self.first_repo, self.storage_path, "include", [], [])
        self.assertTrue(v)

        self.assertFalse(os.path.exists(stored_first_file1))
        self.assertFalse(os.path.exists(stored_first_file2))
        self.assertFalse(os.path.exists(stored_first_file3))
        self.assertFalse(os.path.exists(stored_first_repo_sub_committed_file))
        self.assertTrue(os.path.exists(stored_first_repo_unvfile73))
        self.assertTrue(os.path.exists(stored_first_repo_sub_unvfile715))
        self.assertTrue(os.path.exists(stored_first_repo_anothersub_onemorelvl_evenmore_unvfile330))
        self.assertTrue(os.path.exists(stored_first_repo_anothersub_onemorelvl_evenmore_unvfile333))
        self.assertTrue(os.path.exists(stored_first_repo_anothersub_onemorelvl_evenmore_andyetmore_unvfile762))
        self.assertTrue(os.path.exists(stored_first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe_unvfile308))
        self.assertTrue(os.path.exists(stored_first_repo_anothersub_unvfile99))
        self.assertTrue(os.path.exists(stored_first_repo_anothersub_unvfile47))

    def testCollectPatchUnversioned_Filtering1(self):

        first_repo_unvfile73 = path_utils.concat_path(self.first_repo, "unvfile73.txt")
        create_and_write_file.create_file_contents(first_repo_unvfile73, "dummy contents, file73")

        first_repo_sub = path_utils.concat_path(self.first_repo, "sub")
        self.assertFalse(os.path.exists(first_repo_sub))
        os.mkdir(first_repo_sub)
        self.assertTrue(os.path.exists(first_repo_sub))

        first_repo_sub_committed_file = path_utils.concat_path(first_repo_sub, "committed_file.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, path_utils.concat_path(path_utils.basename_filtered(first_repo_sub), path_utils.basename_filtered(first_repo_sub_committed_file)), "committed-file-content", "commit msg, keep subfolder")
        self.assertTrue(v)

        first_repo_sub_unvfile715 = path_utils.concat_path(first_repo_sub, "unvfile715.txt")
        create_and_write_file.create_file_contents(first_repo_sub_unvfile715, "dummy contents, file715")

        first_repo_anothersub = path_utils.concat_path(self.first_repo, "anothersub")
        self.assertFalse(os.path.exists(first_repo_anothersub))
        os.mkdir(first_repo_anothersub)
        self.assertTrue(os.path.exists(first_repo_anothersub))

        first_repo_anothersub_onemorelvl = path_utils.concat_path(first_repo_anothersub, "onemorelvl")
        self.assertFalse(os.path.exists(first_repo_anothersub_onemorelvl))
        os.mkdir(first_repo_anothersub_onemorelvl)
        self.assertTrue(os.path.exists(first_repo_anothersub_onemorelvl))

        first_repo_anothersub_onemorelvl_evenmore = path_utils.concat_path(first_repo_anothersub_onemorelvl, "evenmore")
        self.assertFalse(os.path.exists(first_repo_anothersub_onemorelvl_evenmore))
        os.mkdir(first_repo_anothersub_onemorelvl_evenmore)
        self.assertTrue(os.path.exists(first_repo_anothersub_onemorelvl_evenmore))

        first_repo_anothersub_onemorelvl_evenmore_andyetmore = path_utils.concat_path(first_repo_anothersub_onemorelvl_evenmore, "andyetmore")
        self.assertFalse(os.path.exists(first_repo_anothersub_onemorelvl_evenmore_andyetmore))
        os.mkdir(first_repo_anothersub_onemorelvl_evenmore_andyetmore)
        self.assertTrue(os.path.exists(first_repo_anothersub_onemorelvl_evenmore_andyetmore))

        first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe = path_utils.concat_path(first_repo_anothersub_onemorelvl_evenmore_andyetmore, "leafmaybe")
        self.assertFalse(os.path.exists(first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe))
        os.mkdir(first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe)
        self.assertTrue(os.path.exists(first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe))

        first_repo_anothersub_onemorelvl_evenmore_unvfile330 = path_utils.concat_path(first_repo_anothersub_onemorelvl_evenmore, "unvfile330.txt")
        create_and_write_file.create_file_contents(first_repo_anothersub_onemorelvl_evenmore_unvfile330, "dummy contents, file330")

        first_repo_anothersub_onemorelvl_evenmore_unvfile333 = path_utils.concat_path(first_repo_anothersub_onemorelvl_evenmore, "unvfile333.txt")
        create_and_write_file.create_file_contents(first_repo_anothersub_onemorelvl_evenmore_unvfile333, "dummy contents, file333")

        first_repo_anothersub_onemorelvl_evenmore_andyetmore_unvfile762 = path_utils.concat_path(first_repo_anothersub_onemorelvl_evenmore_andyetmore, "unvfile762.txt")
        create_and_write_file.create_file_contents(first_repo_anothersub_onemorelvl_evenmore_andyetmore_unvfile762, "dummy contents, file762")

        first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe_unvfile308 = path_utils.concat_path(first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe, "unvfile308.txt")
        create_and_write_file.create_file_contents(first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe_unvfile308, "dummy contents, file308")

        first_repo_anothersub_unvfile99 = path_utils.concat_path(first_repo_anothersub, "unvfile99.txt")
        create_and_write_file.create_file_contents(first_repo_anothersub_unvfile99, "dummy contents, file99")

        first_repo_anothersub_unvfile47 = path_utils.concat_path(first_repo_anothersub, "unvfile47.txt")
        create_and_write_file.create_file_contents(first_repo_anothersub_unvfile47, "dummy contents, file47")

        self.assertTrue(os.path.exists(self.first_file1))
        self.assertTrue(os.path.exists(self.first_file2))
        self.assertTrue(os.path.exists(self.first_file3))
        self.assertTrue(os.path.exists(first_repo_sub_committed_file))
        self.assertTrue(os.path.exists(first_repo_unvfile73))
        self.assertTrue(os.path.exists(first_repo_sub_unvfile715))
        self.assertTrue(os.path.exists(first_repo_anothersub_onemorelvl_evenmore_unvfile330))
        self.assertTrue(os.path.exists(first_repo_anothersub_onemorelvl_evenmore_unvfile333))
        self.assertTrue(os.path.exists(first_repo_anothersub_onemorelvl_evenmore_andyetmore_unvfile762))
        self.assertTrue(os.path.exists(first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe_unvfile308))
        self.assertTrue(os.path.exists(first_repo_anothersub_unvfile99))
        self.assertTrue(os.path.exists(first_repo_anothersub_unvfile47))

        stored_first_file1 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", path_utils.basename_filtered(self.first_file1))
        stored_first_file2 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", path_utils.basename_filtered(self.first_file2))
        stored_first_file3 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", path_utils.basename_filtered( self.first_file3))
        stored_first_repo_sub_committed_file = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "sub", path_utils.basename_filtered(first_repo_sub_committed_file))
        stored_first_repo_unvfile73 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", path_utils.basename_filtered(first_repo_unvfile73))
        stored_first_repo_sub_unvfile715 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "sub", path_utils.basename_filtered(first_repo_sub_unvfile715))
        stored_first_repo_anothersub_onemorelvl_evenmore_unvfile330 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "anothersub", "onemorelvl", "evenmore", path_utils.basename_filtered(first_repo_anothersub_onemorelvl_evenmore_unvfile330))
        stored_first_repo_anothersub_onemorelvl_evenmore_unvfile333 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "anothersub", "onemorelvl", "evenmore", path_utils.basename_filtered(first_repo_anothersub_onemorelvl_evenmore_unvfile333))
        stored_first_repo_anothersub_onemorelvl_evenmore_andyetmore_unvfile762 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "anothersub", "onemorelvl", "evenmore", "andyetmore", path_utils.basename_filtered(first_repo_anothersub_onemorelvl_evenmore_andyetmore_unvfile762))
        stored_first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe_unvfile308 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "anothersub", "onemorelvl", "evenmore", "andyetmore", "leafmaybe", path_utils.basename_filtered(first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe_unvfile308))
        stored_first_repo_anothersub_unvfile99 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "anothersub", path_utils.basename_filtered(first_repo_anothersub_unvfile99))
        stored_first_repo_anothersub_unvfile47 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "anothersub", path_utils.basename_filtered(first_repo_anothersub_unvfile47))

        self.assertFalse(os.path.exists(stored_first_file1))
        self.assertFalse(os.path.exists(stored_first_file2))
        self.assertFalse(os.path.exists(stored_first_file3))
        self.assertFalse(os.path.exists(stored_first_repo_sub_committed_file))
        self.assertFalse(os.path.exists(stored_first_repo_unvfile73))
        self.assertFalse(os.path.exists(stored_first_repo_sub_unvfile715))
        self.assertFalse(os.path.exists(stored_first_repo_anothersub_onemorelvl_evenmore_unvfile330))
        self.assertFalse(os.path.exists(stored_first_repo_anothersub_onemorelvl_evenmore_unvfile333))
        self.assertFalse(os.path.exists(stored_first_repo_anothersub_onemorelvl_evenmore_andyetmore_unvfile762))
        self.assertFalse(os.path.exists(stored_first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe_unvfile308))
        self.assertFalse(os.path.exists(stored_first_repo_anothersub_unvfile99))
        self.assertFalse(os.path.exists(stored_first_repo_anothersub_unvfile47))

        v, r = collect_git_patch.collect_git_patch_unversioned(self.first_repo, self.storage_path, "include", [], ["*/unvfile308.txt"])
        self.assertTrue(v)

        self.assertFalse(os.path.exists(stored_first_file1))
        self.assertFalse(os.path.exists(stored_first_file2))
        self.assertFalse(os.path.exists(stored_first_file3))
        self.assertFalse(os.path.exists(stored_first_repo_sub_committed_file))
        self.assertTrue(os.path.exists(stored_first_repo_unvfile73))
        self.assertTrue(os.path.exists(stored_first_repo_sub_unvfile715))
        self.assertTrue(os.path.exists(stored_first_repo_anothersub_onemorelvl_evenmore_unvfile330))
        self.assertTrue(os.path.exists(stored_first_repo_anothersub_onemorelvl_evenmore_unvfile333))
        self.assertTrue(os.path.exists(stored_first_repo_anothersub_onemorelvl_evenmore_andyetmore_unvfile762))
        self.assertFalse(os.path.exists(stored_first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe_unvfile308))
        self.assertTrue(os.path.exists(stored_first_repo_anothersub_unvfile99))
        self.assertTrue(os.path.exists(stored_first_repo_anothersub_unvfile47))

    def testCollectPatchUnversioned_Filtering2(self):

        first_repo_unvfile73 = path_utils.concat_path(self.first_repo, "unvfile73.txt")
        create_and_write_file.create_file_contents(first_repo_unvfile73, "dummy contents, file73")

        first_repo_sub = path_utils.concat_path(self.first_repo, "sub")
        self.assertFalse(os.path.exists(first_repo_sub))
        os.mkdir(first_repo_sub)
        self.assertTrue(os.path.exists(first_repo_sub))

        first_repo_sub_committed_file = path_utils.concat_path(first_repo_sub, "committed_file.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, path_utils.concat_path(path_utils.basename_filtered(first_repo_sub), path_utils.basename_filtered(first_repo_sub_committed_file)), "committed-file-content", "commit msg, keep subfolder")
        self.assertTrue(v)

        first_repo_sub_unvfile715 = path_utils.concat_path(first_repo_sub, "unvfile715.txt")
        create_and_write_file.create_file_contents(first_repo_sub_unvfile715, "dummy contents, file715")

        first_repo_anothersub = path_utils.concat_path(self.first_repo, "anothersub")
        self.assertFalse(os.path.exists(first_repo_anothersub))
        os.mkdir(first_repo_anothersub)
        self.assertTrue(os.path.exists(first_repo_anothersub))

        first_repo_anothersub_onemorelvl = path_utils.concat_path(first_repo_anothersub, "onemorelvl")
        self.assertFalse(os.path.exists(first_repo_anothersub_onemorelvl))
        os.mkdir(first_repo_anothersub_onemorelvl)
        self.assertTrue(os.path.exists(first_repo_anothersub_onemorelvl))

        first_repo_anothersub_onemorelvl_evenmore = path_utils.concat_path(first_repo_anothersub_onemorelvl, "evenmore")
        self.assertFalse(os.path.exists(first_repo_anothersub_onemorelvl_evenmore))
        os.mkdir(first_repo_anothersub_onemorelvl_evenmore)
        self.assertTrue(os.path.exists(first_repo_anothersub_onemorelvl_evenmore))

        first_repo_anothersub_onemorelvl_evenmore_andyetmore = path_utils.concat_path(first_repo_anothersub_onemorelvl_evenmore, "andyetmore")
        self.assertFalse(os.path.exists(first_repo_anothersub_onemorelvl_evenmore_andyetmore))
        os.mkdir(first_repo_anothersub_onemorelvl_evenmore_andyetmore)
        self.assertTrue(os.path.exists(first_repo_anothersub_onemorelvl_evenmore_andyetmore))

        first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe = path_utils.concat_path(first_repo_anothersub_onemorelvl_evenmore_andyetmore, "leafmaybe")
        self.assertFalse(os.path.exists(first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe))
        os.mkdir(first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe)
        self.assertTrue(os.path.exists(first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe))

        first_repo_anothersub_onemorelvl_evenmore_unvfile330 = path_utils.concat_path(first_repo_anothersub_onemorelvl_evenmore, "unvfile330.txt")
        create_and_write_file.create_file_contents(first_repo_anothersub_onemorelvl_evenmore_unvfile330, "dummy contents, file330")

        first_repo_anothersub_onemorelvl_evenmore_unvfile333 = path_utils.concat_path(first_repo_anothersub_onemorelvl_evenmore, "unvfile333.txt")
        create_and_write_file.create_file_contents(first_repo_anothersub_onemorelvl_evenmore_unvfile333, "dummy contents, file333")

        first_repo_anothersub_onemorelvl_evenmore_andyetmore_unvfile762 = path_utils.concat_path(first_repo_anothersub_onemorelvl_evenmore_andyetmore, "unvfile762.txt")
        create_and_write_file.create_file_contents(first_repo_anothersub_onemorelvl_evenmore_andyetmore_unvfile762, "dummy contents, file762")

        first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe_unvfile308 = path_utils.concat_path(first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe, "unvfile308.txt")
        create_and_write_file.create_file_contents(first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe_unvfile308, "dummy contents, file308")

        first_repo_anothersub_unvfile99 = path_utils.concat_path(first_repo_anothersub, "unvfile99.txt")
        create_and_write_file.create_file_contents(first_repo_anothersub_unvfile99, "dummy contents, file99")

        first_repo_anothersub_unvfile47 = path_utils.concat_path(first_repo_anothersub, "unvfile47.txt")
        create_and_write_file.create_file_contents(first_repo_anothersub_unvfile47, "dummy contents, file47")

        self.assertTrue(os.path.exists(self.first_file1))
        self.assertTrue(os.path.exists(self.first_file2))
        self.assertTrue(os.path.exists(self.first_file3))
        self.assertTrue(os.path.exists(first_repo_sub_committed_file))
        self.assertTrue(os.path.exists(first_repo_unvfile73))
        self.assertTrue(os.path.exists(first_repo_sub_unvfile715))
        self.assertTrue(os.path.exists(first_repo_anothersub_onemorelvl_evenmore_unvfile330))
        self.assertTrue(os.path.exists(first_repo_anothersub_onemorelvl_evenmore_unvfile333))
        self.assertTrue(os.path.exists(first_repo_anothersub_onemorelvl_evenmore_andyetmore_unvfile762))
        self.assertTrue(os.path.exists(first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe_unvfile308))
        self.assertTrue(os.path.exists(first_repo_anothersub_unvfile99))
        self.assertTrue(os.path.exists(first_repo_anothersub_unvfile47))

        stored_first_file1 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", path_utils.basename_filtered(self.first_file1))
        stored_first_file2 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", path_utils.basename_filtered(self.first_file2))
        stored_first_file3 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", path_utils.basename_filtered( self.first_file3))
        stored_first_repo_sub_committed_file = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "sub", path_utils.basename_filtered(first_repo_sub_committed_file))
        stored_first_repo_unvfile73 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", path_utils.basename_filtered(first_repo_unvfile73))
        stored_first_repo_sub_unvfile715 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "sub", path_utils.basename_filtered(first_repo_sub_unvfile715))
        stored_first_repo_anothersub_onemorelvl_evenmore_unvfile330 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "anothersub", "onemorelvl", "evenmore", path_utils.basename_filtered(first_repo_anothersub_onemorelvl_evenmore_unvfile330))
        stored_first_repo_anothersub_onemorelvl_evenmore_unvfile333 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "anothersub", "onemorelvl", "evenmore", path_utils.basename_filtered(first_repo_anothersub_onemorelvl_evenmore_unvfile333))
        stored_first_repo_anothersub_onemorelvl_evenmore_andyetmore_unvfile762 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "anothersub", "onemorelvl", "evenmore", "andyetmore", path_utils.basename_filtered(first_repo_anothersub_onemorelvl_evenmore_andyetmore_unvfile762))
        stored_first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe_unvfile308 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "anothersub", "onemorelvl", "evenmore", "andyetmore", "leafmaybe", path_utils.basename_filtered(first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe_unvfile308))
        stored_first_repo_anothersub_unvfile99 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "anothersub", path_utils.basename_filtered(first_repo_anothersub_unvfile99))
        stored_first_repo_anothersub_unvfile47 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "anothersub", path_utils.basename_filtered(first_repo_anothersub_unvfile47))

        self.assertFalse(os.path.exists(stored_first_file1))
        self.assertFalse(os.path.exists(stored_first_file2))
        self.assertFalse(os.path.exists(stored_first_file3))
        self.assertFalse(os.path.exists(stored_first_repo_sub_committed_file))
        self.assertFalse(os.path.exists(stored_first_repo_unvfile73))
        self.assertFalse(os.path.exists(stored_first_repo_sub_unvfile715))
        self.assertFalse(os.path.exists(stored_first_repo_anothersub_onemorelvl_evenmore_unvfile330))
        self.assertFalse(os.path.exists(stored_first_repo_anothersub_onemorelvl_evenmore_unvfile333))
        self.assertFalse(os.path.exists(stored_first_repo_anothersub_onemorelvl_evenmore_andyetmore_unvfile762))
        self.assertFalse(os.path.exists(stored_first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe_unvfile308))
        self.assertFalse(os.path.exists(stored_first_repo_anothersub_unvfile99))
        self.assertFalse(os.path.exists(stored_first_repo_anothersub_unvfile47))

        v, r = collect_git_patch.collect_git_patch_unversioned(self.first_repo, self.storage_path, "include", [], ["*/anothersub/*"])
        self.assertTrue(v)

        self.assertFalse(os.path.exists(stored_first_file1))
        self.assertFalse(os.path.exists(stored_first_file2))
        self.assertFalse(os.path.exists(stored_first_file3))
        self.assertFalse(os.path.exists(stored_first_repo_sub_committed_file))
        self.assertTrue(os.path.exists(stored_first_repo_unvfile73))
        self.assertTrue(os.path.exists(stored_first_repo_sub_unvfile715))
        self.assertFalse(os.path.exists(stored_first_repo_anothersub_onemorelvl_evenmore_unvfile330))
        self.assertFalse(os.path.exists(stored_first_repo_anothersub_onemorelvl_evenmore_unvfile333))
        self.assertFalse(os.path.exists(stored_first_repo_anothersub_onemorelvl_evenmore_andyetmore_unvfile762))
        self.assertFalse(os.path.exists(stored_first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe_unvfile308))
        self.assertFalse(os.path.exists(stored_first_repo_anothersub_unvfile99))
        self.assertFalse(os.path.exists(stored_first_repo_anothersub_unvfile47))

    def testCollectPatchUnversioned_Filtering3(self):

        first_repo_unvfile73 = path_utils.concat_path(self.first_repo, "unvfile73.txt")
        create_and_write_file.create_file_contents(first_repo_unvfile73, "dummy contents, file73")

        first_repo_sub = path_utils.concat_path(self.first_repo, "sub")
        self.assertFalse(os.path.exists(first_repo_sub))
        os.mkdir(first_repo_sub)
        self.assertTrue(os.path.exists(first_repo_sub))

        first_repo_sub_committed_file = path_utils.concat_path(first_repo_sub, "committed_file.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, path_utils.concat_path(path_utils.basename_filtered(first_repo_sub), path_utils.basename_filtered(first_repo_sub_committed_file)), "committed-file-content", "commit msg, keep subfolder")
        self.assertTrue(v)

        first_repo_sub_unvfile715 = path_utils.concat_path(first_repo_sub, "unvfile715.txt")
        create_and_write_file.create_file_contents(first_repo_sub_unvfile715, "dummy contents, file715")

        first_repo_anothersub = path_utils.concat_path(self.first_repo, "anothersub")
        self.assertFalse(os.path.exists(first_repo_anothersub))
        os.mkdir(first_repo_anothersub)
        self.assertTrue(os.path.exists(first_repo_anothersub))

        first_repo_anothersub_onemorelvl = path_utils.concat_path(first_repo_anothersub, "onemorelvl")
        self.assertFalse(os.path.exists(first_repo_anothersub_onemorelvl))
        os.mkdir(first_repo_anothersub_onemorelvl)
        self.assertTrue(os.path.exists(first_repo_anothersub_onemorelvl))

        first_repo_anothersub_onemorelvl_evenmore = path_utils.concat_path(first_repo_anothersub_onemorelvl, "evenmore")
        self.assertFalse(os.path.exists(first_repo_anothersub_onemorelvl_evenmore))
        os.mkdir(first_repo_anothersub_onemorelvl_evenmore)
        self.assertTrue(os.path.exists(first_repo_anothersub_onemorelvl_evenmore))

        first_repo_anothersub_onemorelvl_evenmore_andyetmore = path_utils.concat_path(first_repo_anothersub_onemorelvl_evenmore, "andyetmore")
        self.assertFalse(os.path.exists(first_repo_anothersub_onemorelvl_evenmore_andyetmore))
        os.mkdir(first_repo_anothersub_onemorelvl_evenmore_andyetmore)
        self.assertTrue(os.path.exists(first_repo_anothersub_onemorelvl_evenmore_andyetmore))

        first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe = path_utils.concat_path(first_repo_anothersub_onemorelvl_evenmore_andyetmore, "leafmaybe")
        self.assertFalse(os.path.exists(first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe))
        os.mkdir(first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe)
        self.assertTrue(os.path.exists(first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe))

        first_repo_anothersub_onemorelvl_evenmore_unvfile330 = path_utils.concat_path(first_repo_anothersub_onemorelvl_evenmore, "unvfile330.txt")
        create_and_write_file.create_file_contents(first_repo_anothersub_onemorelvl_evenmore_unvfile330, "dummy contents, file330")

        first_repo_anothersub_onemorelvl_evenmore_unvfile333 = path_utils.concat_path(first_repo_anothersub_onemorelvl_evenmore, "unvfile333.txt")
        create_and_write_file.create_file_contents(first_repo_anothersub_onemorelvl_evenmore_unvfile333, "dummy contents, file333")

        first_repo_anothersub_onemorelvl_evenmore_andyetmore_unvfile762 = path_utils.concat_path(first_repo_anothersub_onemorelvl_evenmore_andyetmore, "unvfile762.txt")
        create_and_write_file.create_file_contents(first_repo_anothersub_onemorelvl_evenmore_andyetmore_unvfile762, "dummy contents, file762")

        first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe_unvfile308 = path_utils.concat_path(first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe, "unvfile308.txt")
        create_and_write_file.create_file_contents(first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe_unvfile308, "dummy contents, file308")

        first_repo_anothersub_unvfile99 = path_utils.concat_path(first_repo_anothersub, "unvfile99.txt")
        create_and_write_file.create_file_contents(first_repo_anothersub_unvfile99, "dummy contents, file99")

        first_repo_anothersub_unvfile47 = path_utils.concat_path(first_repo_anothersub, "unvfile47.txt")
        create_and_write_file.create_file_contents(first_repo_anothersub_unvfile47, "dummy contents, file47")

        self.assertTrue(os.path.exists(self.first_file1))
        self.assertTrue(os.path.exists(self.first_file2))
        self.assertTrue(os.path.exists(self.first_file3))
        self.assertTrue(os.path.exists(first_repo_sub_committed_file))
        self.assertTrue(os.path.exists(first_repo_unvfile73))
        self.assertTrue(os.path.exists(first_repo_sub_unvfile715))
        self.assertTrue(os.path.exists(first_repo_anothersub_onemorelvl_evenmore_unvfile330))
        self.assertTrue(os.path.exists(first_repo_anothersub_onemorelvl_evenmore_unvfile333))
        self.assertTrue(os.path.exists(first_repo_anothersub_onemorelvl_evenmore_andyetmore_unvfile762))
        self.assertTrue(os.path.exists(first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe_unvfile308))
        self.assertTrue(os.path.exists(first_repo_anothersub_unvfile99))
        self.assertTrue(os.path.exists(first_repo_anothersub_unvfile47))

        stored_first_file1 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", path_utils.basename_filtered(self.first_file1))
        stored_first_file2 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", path_utils.basename_filtered(self.first_file2))
        stored_first_file3 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", path_utils.basename_filtered( self.first_file3))
        stored_first_repo_sub_committed_file = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "sub", path_utils.basename_filtered(first_repo_sub_committed_file))
        stored_first_repo_unvfile73 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", path_utils.basename_filtered(first_repo_unvfile73))
        stored_first_repo_sub_unvfile715 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "sub", path_utils.basename_filtered(first_repo_sub_unvfile715))
        stored_first_repo_anothersub_onemorelvl_evenmore_unvfile330 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "anothersub", "onemorelvl", "evenmore", path_utils.basename_filtered(first_repo_anothersub_onemorelvl_evenmore_unvfile330))
        stored_first_repo_anothersub_onemorelvl_evenmore_unvfile333 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "anothersub", "onemorelvl", "evenmore", path_utils.basename_filtered(first_repo_anothersub_onemorelvl_evenmore_unvfile333))
        stored_first_repo_anothersub_onemorelvl_evenmore_andyetmore_unvfile762 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "anothersub", "onemorelvl", "evenmore", "andyetmore", path_utils.basename_filtered(first_repo_anothersub_onemorelvl_evenmore_andyetmore_unvfile762))
        stored_first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe_unvfile308 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "anothersub", "onemorelvl", "evenmore", "andyetmore", "leafmaybe", path_utils.basename_filtered(first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe_unvfile308))
        stored_first_repo_anothersub_unvfile99 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "anothersub", path_utils.basename_filtered(first_repo_anothersub_unvfile99))
        stored_first_repo_anothersub_unvfile47 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "anothersub", path_utils.basename_filtered(first_repo_anothersub_unvfile47))

        self.assertFalse(os.path.exists(stored_first_file1))
        self.assertFalse(os.path.exists(stored_first_file2))
        self.assertFalse(os.path.exists(stored_first_file3))
        self.assertFalse(os.path.exists(stored_first_repo_sub_committed_file))
        self.assertFalse(os.path.exists(stored_first_repo_unvfile73))
        self.assertFalse(os.path.exists(stored_first_repo_sub_unvfile715))
        self.assertFalse(os.path.exists(stored_first_repo_anothersub_onemorelvl_evenmore_unvfile330))
        self.assertFalse(os.path.exists(stored_first_repo_anothersub_onemorelvl_evenmore_unvfile333))
        self.assertFalse(os.path.exists(stored_first_repo_anothersub_onemorelvl_evenmore_andyetmore_unvfile762))
        self.assertFalse(os.path.exists(stored_first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe_unvfile308))
        self.assertFalse(os.path.exists(stored_first_repo_anothersub_unvfile99))
        self.assertFalse(os.path.exists(stored_first_repo_anothersub_unvfile47))

        v, r = collect_git_patch.collect_git_patch_unversioned(self.first_repo, self.storage_path, "include", [], ["*/sub/*"])
        self.assertTrue(v)

        self.assertFalse(os.path.exists(stored_first_file1))
        self.assertFalse(os.path.exists(stored_first_file2))
        self.assertFalse(os.path.exists(stored_first_file3))
        self.assertFalse(os.path.exists(stored_first_repo_sub_committed_file))
        self.assertTrue(os.path.exists(stored_first_repo_unvfile73))
        self.assertFalse(os.path.exists(stored_first_repo_sub_unvfile715))
        self.assertTrue(os.path.exists(stored_first_repo_anothersub_onemorelvl_evenmore_unvfile330))
        self.assertTrue(os.path.exists(stored_first_repo_anothersub_onemorelvl_evenmore_unvfile333))
        self.assertTrue(os.path.exists(stored_first_repo_anothersub_onemorelvl_evenmore_andyetmore_unvfile762))
        self.assertTrue(os.path.exists(stored_first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe_unvfile308))
        self.assertTrue(os.path.exists(stored_first_repo_anothersub_unvfile99))
        self.assertTrue(os.path.exists(stored_first_repo_anothersub_unvfile47))

    def testCollectPatchUnversioned_Filtering4(self):

        first_repo_unvfile73 = path_utils.concat_path(self.first_repo, "unvfile73.txt")
        create_and_write_file.create_file_contents(first_repo_unvfile73, "dummy contents, file73")

        first_repo_sub = path_utils.concat_path(self.first_repo, "sub")
        self.assertFalse(os.path.exists(first_repo_sub))
        os.mkdir(first_repo_sub)
        self.assertTrue(os.path.exists(first_repo_sub))

        first_repo_sub_committed_file = path_utils.concat_path(first_repo_sub, "committed_file.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, path_utils.concat_path(path_utils.basename_filtered(first_repo_sub), path_utils.basename_filtered(first_repo_sub_committed_file)), "committed-file-content", "commit msg, keep subfolder")
        self.assertTrue(v)

        first_repo_sub_unvfile715 = path_utils.concat_path(first_repo_sub, "unvfile715.txt")
        create_and_write_file.create_file_contents(first_repo_sub_unvfile715, "dummy contents, file715")

        first_repo_anothersub = path_utils.concat_path(self.first_repo, "anothersub")
        self.assertFalse(os.path.exists(first_repo_anothersub))
        os.mkdir(first_repo_anothersub)
        self.assertTrue(os.path.exists(first_repo_anothersub))

        first_repo_anothersub_onemorelvl = path_utils.concat_path(first_repo_anothersub, "onemorelvl")
        self.assertFalse(os.path.exists(first_repo_anothersub_onemorelvl))
        os.mkdir(first_repo_anothersub_onemorelvl)
        self.assertTrue(os.path.exists(first_repo_anothersub_onemorelvl))

        first_repo_anothersub_onemorelvl_evenmore = path_utils.concat_path(first_repo_anothersub_onemorelvl, "evenmore")
        self.assertFalse(os.path.exists(first_repo_anothersub_onemorelvl_evenmore))
        os.mkdir(first_repo_anothersub_onemorelvl_evenmore)
        self.assertTrue(os.path.exists(first_repo_anothersub_onemorelvl_evenmore))

        first_repo_anothersub_onemorelvl_evenmore_andyetmore = path_utils.concat_path(first_repo_anothersub_onemorelvl_evenmore, "andyetmore")
        self.assertFalse(os.path.exists(first_repo_anothersub_onemorelvl_evenmore_andyetmore))
        os.mkdir(first_repo_anothersub_onemorelvl_evenmore_andyetmore)
        self.assertTrue(os.path.exists(first_repo_anothersub_onemorelvl_evenmore_andyetmore))

        first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe = path_utils.concat_path(first_repo_anothersub_onemorelvl_evenmore_andyetmore, "leafmaybe")
        self.assertFalse(os.path.exists(first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe))
        os.mkdir(first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe)
        self.assertTrue(os.path.exists(first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe))

        first_repo_anothersub_onemorelvl_evenmore_unvfile330 = path_utils.concat_path(first_repo_anothersub_onemorelvl_evenmore, "unvfile330.txt")
        create_and_write_file.create_file_contents(first_repo_anothersub_onemorelvl_evenmore_unvfile330, "dummy contents, file330")

        first_repo_anothersub_onemorelvl_evenmore_unvfile333 = path_utils.concat_path(first_repo_anothersub_onemorelvl_evenmore, "unvfile333.txt")
        create_and_write_file.create_file_contents(first_repo_anothersub_onemorelvl_evenmore_unvfile333, "dummy contents, file333")

        first_repo_anothersub_onemorelvl_evenmore_andyetmore_unvfile762 = path_utils.concat_path(first_repo_anothersub_onemorelvl_evenmore_andyetmore, "unvfile762.txt")
        create_and_write_file.create_file_contents(first_repo_anothersub_onemorelvl_evenmore_andyetmore_unvfile762, "dummy contents, file762")

        first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe_unvfile308 = path_utils.concat_path(first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe, "unvfile308.txt")
        create_and_write_file.create_file_contents(first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe_unvfile308, "dummy contents, file308")

        first_repo_anothersub_unvfile99 = path_utils.concat_path(first_repo_anothersub, "unvfile99.txt")
        create_and_write_file.create_file_contents(first_repo_anothersub_unvfile99, "dummy contents, file99")

        first_repo_anothersub_unvfile47 = path_utils.concat_path(first_repo_anothersub, "unvfile47.txt")
        create_and_write_file.create_file_contents(first_repo_anothersub_unvfile47, "dummy contents, file47")

        self.assertTrue(os.path.exists(self.first_file1))
        self.assertTrue(os.path.exists(self.first_file2))
        self.assertTrue(os.path.exists(self.first_file3))
        self.assertTrue(os.path.exists(first_repo_sub_committed_file))
        self.assertTrue(os.path.exists(first_repo_unvfile73))
        self.assertTrue(os.path.exists(first_repo_sub_unvfile715))
        self.assertTrue(os.path.exists(first_repo_anothersub_onemorelvl_evenmore_unvfile330))
        self.assertTrue(os.path.exists(first_repo_anothersub_onemorelvl_evenmore_unvfile333))
        self.assertTrue(os.path.exists(first_repo_anothersub_onemorelvl_evenmore_andyetmore_unvfile762))
        self.assertTrue(os.path.exists(first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe_unvfile308))
        self.assertTrue(os.path.exists(first_repo_anothersub_unvfile99))
        self.assertTrue(os.path.exists(first_repo_anothersub_unvfile47))

        stored_first_file1 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", path_utils.basename_filtered(self.first_file1))
        stored_first_file2 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", path_utils.basename_filtered(self.first_file2))
        stored_first_file3 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", path_utils.basename_filtered( self.first_file3))
        stored_first_repo_sub_committed_file = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "sub", path_utils.basename_filtered(first_repo_sub_committed_file))
        stored_first_repo_unvfile73 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", path_utils.basename_filtered(first_repo_unvfile73))
        stored_first_repo_sub_unvfile715 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "sub", path_utils.basename_filtered(first_repo_sub_unvfile715))
        stored_first_repo_anothersub_onemorelvl_evenmore_unvfile330 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "anothersub", "onemorelvl", "evenmore", path_utils.basename_filtered(first_repo_anothersub_onemorelvl_evenmore_unvfile330))
        stored_first_repo_anothersub_onemorelvl_evenmore_unvfile333 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "anothersub", "onemorelvl", "evenmore", path_utils.basename_filtered(first_repo_anothersub_onemorelvl_evenmore_unvfile333))
        stored_first_repo_anothersub_onemorelvl_evenmore_andyetmore_unvfile762 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "anothersub", "onemorelvl", "evenmore", "andyetmore", path_utils.basename_filtered(first_repo_anothersub_onemorelvl_evenmore_andyetmore_unvfile762))
        stored_first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe_unvfile308 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "anothersub", "onemorelvl", "evenmore", "andyetmore", "leafmaybe", path_utils.basename_filtered(first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe_unvfile308))
        stored_first_repo_anothersub_unvfile99 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "anothersub", path_utils.basename_filtered(first_repo_anothersub_unvfile99))
        stored_first_repo_anothersub_unvfile47 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "anothersub", path_utils.basename_filtered(first_repo_anothersub_unvfile47))

        self.assertFalse(os.path.exists(stored_first_file1))
        self.assertFalse(os.path.exists(stored_first_file2))
        self.assertFalse(os.path.exists(stored_first_file3))
        self.assertFalse(os.path.exists(stored_first_repo_sub_committed_file))
        self.assertFalse(os.path.exists(stored_first_repo_unvfile73))
        self.assertFalse(os.path.exists(stored_first_repo_sub_unvfile715))
        self.assertFalse(os.path.exists(stored_first_repo_anothersub_onemorelvl_evenmore_unvfile330))
        self.assertFalse(os.path.exists(stored_first_repo_anothersub_onemorelvl_evenmore_unvfile333))
        self.assertFalse(os.path.exists(stored_first_repo_anothersub_onemorelvl_evenmore_andyetmore_unvfile762))
        self.assertFalse(os.path.exists(stored_first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe_unvfile308))
        self.assertFalse(os.path.exists(stored_first_repo_anothersub_unvfile99))
        self.assertFalse(os.path.exists(stored_first_repo_anothersub_unvfile47))

        v, r = collect_git_patch.collect_git_patch_unversioned(self.first_repo, self.storage_path, "include", [], ["*/andyetmore/*"])
        self.assertTrue(v)

        self.assertFalse(os.path.exists(stored_first_file1))
        self.assertFalse(os.path.exists(stored_first_file2))
        self.assertFalse(os.path.exists(stored_first_file3))
        self.assertFalse(os.path.exists(stored_first_repo_sub_committed_file))
        self.assertTrue(os.path.exists(stored_first_repo_unvfile73))
        self.assertTrue(os.path.exists(stored_first_repo_sub_unvfile715))
        self.assertTrue(os.path.exists(stored_first_repo_anothersub_onemorelvl_evenmore_unvfile330))
        self.assertTrue(os.path.exists(stored_first_repo_anothersub_onemorelvl_evenmore_unvfile333))
        self.assertFalse(os.path.exists(stored_first_repo_anothersub_onemorelvl_evenmore_andyetmore_unvfile762))
        self.assertFalse(os.path.exists(stored_first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe_unvfile308))
        self.assertTrue(os.path.exists(stored_first_repo_anothersub_unvfile99))
        self.assertTrue(os.path.exists(stored_first_repo_anothersub_unvfile47))

    def testCollectPatchUnversioned_Filtering5(self):

        first_repo_unvfile73 = path_utils.concat_path(self.first_repo, "unvfile73.txt")
        create_and_write_file.create_file_contents(first_repo_unvfile73, "dummy contents, file73")

        first_repo_sub = path_utils.concat_path(self.first_repo, "sub")
        self.assertFalse(os.path.exists(first_repo_sub))
        os.mkdir(first_repo_sub)
        self.assertTrue(os.path.exists(first_repo_sub))

        first_repo_sub_committed_file = path_utils.concat_path(first_repo_sub, "committed_file.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, path_utils.concat_path(path_utils.basename_filtered(first_repo_sub), path_utils.basename_filtered(first_repo_sub_committed_file)), "committed-file-content", "commit msg, keep subfolder")
        self.assertTrue(v)

        first_repo_sub_unvfile715 = path_utils.concat_path(first_repo_sub, "unvfile715.txt")
        create_and_write_file.create_file_contents(first_repo_sub_unvfile715, "dummy contents, file715")

        first_repo_anothersub = path_utils.concat_path(self.first_repo, "anothersub")
        self.assertFalse(os.path.exists(first_repo_anothersub))
        os.mkdir(first_repo_anothersub)
        self.assertTrue(os.path.exists(first_repo_anothersub))

        first_repo_anothersub_onemorelvl = path_utils.concat_path(first_repo_anothersub, "onemorelvl")
        self.assertFalse(os.path.exists(first_repo_anothersub_onemorelvl))
        os.mkdir(first_repo_anothersub_onemorelvl)
        self.assertTrue(os.path.exists(first_repo_anothersub_onemorelvl))

        first_repo_anothersub_onemorelvl_evenmore = path_utils.concat_path(first_repo_anothersub_onemorelvl, "evenmore")
        self.assertFalse(os.path.exists(first_repo_anothersub_onemorelvl_evenmore))
        os.mkdir(first_repo_anothersub_onemorelvl_evenmore)
        self.assertTrue(os.path.exists(first_repo_anothersub_onemorelvl_evenmore))

        first_repo_anothersub_onemorelvl_evenmore_andyetmore = path_utils.concat_path(first_repo_anothersub_onemorelvl_evenmore, "andyetmore")
        self.assertFalse(os.path.exists(first_repo_anothersub_onemorelvl_evenmore_andyetmore))
        os.mkdir(first_repo_anothersub_onemorelvl_evenmore_andyetmore)
        self.assertTrue(os.path.exists(first_repo_anothersub_onemorelvl_evenmore_andyetmore))

        first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe = path_utils.concat_path(first_repo_anothersub_onemorelvl_evenmore_andyetmore, "leafmaybe")
        self.assertFalse(os.path.exists(first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe))
        os.mkdir(first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe)
        self.assertTrue(os.path.exists(first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe))

        first_repo_anothersub_onemorelvl_evenmore_unvfile330 = path_utils.concat_path(first_repo_anothersub_onemorelvl_evenmore, "unvfile330.txt")
        create_and_write_file.create_file_contents(first_repo_anothersub_onemorelvl_evenmore_unvfile330, "dummy contents, file330")

        first_repo_anothersub_onemorelvl_evenmore_unvfile333 = path_utils.concat_path(first_repo_anothersub_onemorelvl_evenmore, "unvfile333.txt")
        create_and_write_file.create_file_contents(first_repo_anothersub_onemorelvl_evenmore_unvfile333, "dummy contents, file333")

        first_repo_anothersub_onemorelvl_evenmore_andyetmore_unvfile762 = path_utils.concat_path(first_repo_anothersub_onemorelvl_evenmore_andyetmore, "unvfile762.txt")
        create_and_write_file.create_file_contents(first_repo_anothersub_onemorelvl_evenmore_andyetmore_unvfile762, "dummy contents, file762")

        first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe_unvfile308 = path_utils.concat_path(first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe, "unvfile308.txt")
        create_and_write_file.create_file_contents(first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe_unvfile308, "dummy contents, file308")

        first_repo_anothersub_unvfile99 = path_utils.concat_path(first_repo_anothersub, "unvfile99.txt")
        create_and_write_file.create_file_contents(first_repo_anothersub_unvfile99, "dummy contents, file99")

        first_repo_anothersub_unvfile47 = path_utils.concat_path(first_repo_anothersub, "unvfile47.txt")
        create_and_write_file.create_file_contents(first_repo_anothersub_unvfile47, "dummy contents, file47")

        self.assertTrue(os.path.exists(self.first_file1))
        self.assertTrue(os.path.exists(self.first_file2))
        self.assertTrue(os.path.exists(self.first_file3))
        self.assertTrue(os.path.exists(first_repo_sub_committed_file))
        self.assertTrue(os.path.exists(first_repo_unvfile73))
        self.assertTrue(os.path.exists(first_repo_sub_unvfile715))
        self.assertTrue(os.path.exists(first_repo_anothersub_onemorelvl_evenmore_unvfile330))
        self.assertTrue(os.path.exists(first_repo_anothersub_onemorelvl_evenmore_unvfile333))
        self.assertTrue(os.path.exists(first_repo_anothersub_onemorelvl_evenmore_andyetmore_unvfile762))
        self.assertTrue(os.path.exists(first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe_unvfile308))
        self.assertTrue(os.path.exists(first_repo_anothersub_unvfile99))
        self.assertTrue(os.path.exists(first_repo_anothersub_unvfile47))

        stored_first_file1 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", path_utils.basename_filtered(self.first_file1))
        stored_first_file2 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", path_utils.basename_filtered(self.first_file2))
        stored_first_file3 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", path_utils.basename_filtered( self.first_file3))
        stored_first_repo_sub_committed_file = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "sub", path_utils.basename_filtered(first_repo_sub_committed_file))
        stored_first_repo_unvfile73 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", path_utils.basename_filtered(first_repo_unvfile73))
        stored_first_repo_sub_unvfile715 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "sub", path_utils.basename_filtered(first_repo_sub_unvfile715))
        stored_first_repo_anothersub_onemorelvl_evenmore_unvfile330 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "anothersub", "onemorelvl", "evenmore", path_utils.basename_filtered(first_repo_anothersub_onemorelvl_evenmore_unvfile330))
        stored_first_repo_anothersub_onemorelvl_evenmore_unvfile333 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "anothersub", "onemorelvl", "evenmore", path_utils.basename_filtered(first_repo_anothersub_onemorelvl_evenmore_unvfile333))
        stored_first_repo_anothersub_onemorelvl_evenmore_andyetmore_unvfile762 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "anothersub", "onemorelvl", "evenmore", "andyetmore", path_utils.basename_filtered(first_repo_anothersub_onemorelvl_evenmore_andyetmore_unvfile762))
        stored_first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe_unvfile308 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "anothersub", "onemorelvl", "evenmore", "andyetmore", "leafmaybe", path_utils.basename_filtered(first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe_unvfile308))
        stored_first_repo_anothersub_unvfile99 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "anothersub", path_utils.basename_filtered(first_repo_anothersub_unvfile99))
        stored_first_repo_anothersub_unvfile47 = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "anothersub", path_utils.basename_filtered(first_repo_anothersub_unvfile47))

        self.assertFalse(os.path.exists(stored_first_file1))
        self.assertFalse(os.path.exists(stored_first_file2))
        self.assertFalse(os.path.exists(stored_first_file3))
        self.assertFalse(os.path.exists(stored_first_repo_sub_committed_file))
        self.assertFalse(os.path.exists(stored_first_repo_unvfile73))
        self.assertFalse(os.path.exists(stored_first_repo_sub_unvfile715))
        self.assertFalse(os.path.exists(stored_first_repo_anothersub_onemorelvl_evenmore_unvfile330))
        self.assertFalse(os.path.exists(stored_first_repo_anothersub_onemorelvl_evenmore_unvfile333))
        self.assertFalse(os.path.exists(stored_first_repo_anothersub_onemorelvl_evenmore_andyetmore_unvfile762))
        self.assertFalse(os.path.exists(stored_first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe_unvfile308))
        self.assertFalse(os.path.exists(stored_first_repo_anothersub_unvfile99))
        self.assertFalse(os.path.exists(stored_first_repo_anothersub_unvfile47))

        v, r = collect_git_patch.collect_git_patch_unversioned(self.first_repo, self.storage_path, "exclude", ["*/onemorelvl/evenmore/*"], [])
        self.assertTrue(v)

        self.assertFalse(os.path.exists(stored_first_file1))
        self.assertFalse(os.path.exists(stored_first_file2))
        self.assertFalse(os.path.exists(stored_first_file3))
        self.assertFalse(os.path.exists(stored_first_repo_sub_committed_file))
        self.assertFalse(os.path.exists(stored_first_repo_unvfile73))
        self.assertFalse(os.path.exists(stored_first_repo_sub_unvfile715))
        self.assertTrue(os.path.exists(stored_first_repo_anothersub_onemorelvl_evenmore_unvfile330))
        self.assertTrue(os.path.exists(stored_first_repo_anothersub_onemorelvl_evenmore_unvfile333))
        self.assertTrue(os.path.exists(stored_first_repo_anothersub_onemorelvl_evenmore_andyetmore_unvfile762))
        self.assertTrue(os.path.exists(stored_first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe_unvfile308))
        self.assertFalse(os.path.exists(stored_first_repo_anothersub_unvfile99))
        self.assertFalse(os.path.exists(stored_first_repo_anothersub_unvfile47))

    def testCollectPatchUnversionedSub(self):

        newfile = path_utils.concat_path(self.second_sub, "newfile.txt")
        create_and_write_file.create_file_contents(newfile, "newfilecontents")

        v, r = collect_git_patch.collect_git_patch_unversioned(self.second_sub, self.storage_path, "include", [], [])
        self.assertTrue(v)

        newfile_storage = path_utils.concat_path(self.storage_path, self.second_sub, "unversioned", "newfile.txt")
        self.assertTrue(os.path.exists(newfile_storage))
        self.assertEqual(r[0], newfile_storage)

        contents_read = getcontents.getcontents(newfile_storage)
        self.assertEqual(contents_read, "newfilecontents")

    def testCollectPatchStashFail(self):

        open_and_update_file.update_file_contents(self.first_file1, "stashcontent1")

        git_wrapper.stash(self.first_repo)

        v, r = collect_git_patch.collect_git_patch_stash(self.first_repo, self.storage_path, -1)
        self.assertTrue(v)

        stash1_storage = path_utils.concat_path(self.storage_path, self.first_repo, "stash@{0}.patch")
        self.assertTrue(os.path.exists(stash1_storage))
        self.assertEqual(r[0], stash1_storage)

        v, r = collect_git_patch.collect_git_patch_stash(self.first_repo, self.storage_path, -1)
        self.assertFalse(v)

    def testCollectPatchStashFail2(self):
        # no stash to collect
        git_wrapper.stash(self.first_repo)

        v, r = collect_git_patch.collect_git_patch_stash(self.first_repo, self.storage_path, -1)
        self.assertFalse(v)

        v, r = fsquery.makecontentlist(self.storage_path, False, False, True, False, False, False, True, None)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

    def testCollectPatchStash1(self):

        open_and_update_file.update_file_contents(self.first_file1, "stashcontent1")

        git_wrapper.stash(self.first_repo)

        open_and_update_file.update_file_contents(self.first_file2, "stashcontent2")

        git_wrapper.stash(self.first_repo)

        v, r = collect_git_patch.collect_git_patch_stash(self.first_repo, self.storage_path, -1)
        self.assertTrue(v)

        stash1_storage = path_utils.concat_path(self.storage_path, self.first_repo, "stash@{0}.patch")
        self.assertTrue(os.path.exists(stash1_storage))
        self.assertEqual(r[0], stash1_storage)

        contents_read = getcontents.getcontents(stash1_storage)
        self.assertTrue("stashcontent2" in contents_read)

        stash2_storage = path_utils.concat_path(self.storage_path, self.first_repo, "stash@{1}.patch")
        self.assertTrue(os.path.exists(stash2_storage))
        self.assertEqual(r[1], stash2_storage)

        contents_read = getcontents.getcontents(stash2_storage)
        self.assertTrue("stashcontent1" in contents_read)

    def testCollectPatchStash2(self):

        open_and_update_file.update_file_contents(self.first_file1, "stashcontent1")

        git_wrapper.stash(self.first_repo)

        open_and_update_file.update_file_contents(self.first_file2, "stashcontent2")

        git_wrapper.stash(self.first_repo)

        v, r = collect_git_patch.collect_git_patch_stash(self.first_repo, self.storage_path, 1)
        self.assertTrue(v)

        stash1_storage = path_utils.concat_path(self.storage_path, self.first_repo, "stash@{0}.patch")
        self.assertTrue(os.path.exists(stash1_storage))
        self.assertEqual(r[0], stash1_storage)

        contents_read = getcontents.getcontents(stash1_storage)
        self.assertTrue("stashcontent2" in contents_read)

        stash2_storage = path_utils.concat_path(self.storage_path, self.first_repo, "stash@{1}.patch")
        self.assertFalse(os.path.exists(stash2_storage))
        self.assertEqual(len(r), 1)

    def testCollectPatchStashSub(self):

        open_and_update_file.update_file_contents(self.second_sub_file1, "stashcontent-sub")

        git_wrapper.stash(self.second_sub)

        v, r = collect_git_patch.collect_git_patch_stash(self.second_sub, self.storage_path, -1)
        self.assertTrue(v)

        stash1_storage = path_utils.concat_path(self.storage_path, self.second_sub, "stash@{0}.patch")
        self.assertTrue(os.path.exists(stash1_storage))
        self.assertEqual(r[0], stash1_storage)

        contents_read = getcontents.getcontents(stash1_storage)
        self.assertTrue("stashcontent-sub" in contents_read)

    def testCollectPatchPreviousFail1(self):

        v, r = collect_git_patch.collect_git_patch_previous(self.first_repo, self.storage_path, 5)
        self.assertFalse(v)

    def testCollectPatchPreviousFail2(self):

        v, r = collect_git_patch.collect_git_patch_previous(self.first_repo, self.storage_path, 1)
        self.assertTrue(v)

        patches = self.get_patches_in_order(self.storage_path, self.first_repo)
        self.assertEqual(len(patches), 1)
        self.assertTrue( os.path.exists(patches[0]) )

        v, r = collect_git_patch.collect_git_patch_previous(self.first_repo, self.storage_path, 1)
        self.assertFalse(v)

    def testCollectPatchPrevious(self):

        v, r = collect_git_patch.collect_git_patch_previous(self.first_repo, self.storage_path, 2)
        self.assertTrue(v)

        patches = self.get_patches_in_order(self.storage_path, self.first_repo)
        self.assertEqual(len(patches), 2)

        self.assertTrue( os.path.exists(patches[0]) )
        self.assertEqual(r[0], patches[0])
        self.assertTrue( os.path.exists(patches[1]) )
        self.assertEqual(r[1], patches[1])

        contents_read = getcontents.getcontents(patches[0])
        self.assertTrue("first-adding-submodule" in contents_read)

        contents_read = getcontents.getcontents(patches[1])
        self.assertTrue("first-file3-content" in contents_read)

    def testCollectPatchPreviousSub(self):

        v, r = collect_git_patch.collect_git_patch_previous(self.second_sub, self.storage_path, 1)
        self.assertTrue(v)

        patches = self.get_patches_in_order(self.storage_path, self.second_sub)
        self.assertEqual(len(patches), 1)
        self.assertTrue( os.path.exists(patches[0]) )
        self.assertEqual(r[0], patches[0])

        contents_read = getcontents.getcontents(patches[0])
        self.assertTrue("second-file1-content" in contents_read)

    def testCollectPatchCherryPickPreviousFail1(self):

        v, r = collect_git_patch.collect_git_patch_cherry_pick_previous(self.nonexistent, self.storage_path, "aabb")
        self.assertFalse(v)

    def testCollectPatchCherryPickPreviousFail2(self):

        v, r = collect_git_patch.collect_git_patch_cherry_pick_previous(self.first_repo, self.storage_path, "tttt")
        self.assertFalse(v)

    def testCollectPatchCherryPickPrevious1(self):

        v, r = git_lib.get_head_hash(self.first_repo)
        self.assertTrue(v)
        hash_head = r

        v, r = collect_git_patch.collect_git_patch_cherry_pick_previous(self.first_repo, self.storage_path, hash_head)
        self.assertTrue(v)

    def testCollectPatchCherryPickPrevious2(self):

        open_and_update_file.update_file_contents(self.first_file1, "content to be cherry picked later")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.first_repo, "commitmsg")
        self.assertTrue(v)

        v, r = git_lib.get_head_hash(self.first_repo)
        self.assertTrue(v)
        stored_hash = r

        open_and_update_file.update_file_contents(self.first_file1, "nondetectful")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.first_repo, "commitmsg")
        self.assertTrue(v)

        open_and_update_file.update_file_contents(self.first_file1, "ship-of-the-line")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.first_repo, "commitmsg")
        self.assertTrue(v)

        v, r = collect_git_patch.collect_git_patch_cherry_pick_previous(self.first_repo, self.storage_path, stored_hash)
        self.assertTrue(v)
        generated_patch = r

        contents = getcontents.getcontents(generated_patch)

        self.assertTrue("content to be cherry picked later" in contents)
        self.assertFalse("nondetectful" in contents)
        self.assertFalse("ship-of-the-line" in contents)

    def testCollectGitPatch(self):
        pass # mvtodo {test combinations and doubletap (detect overwrites)}

    def testCollectGitPatch_CollectGitPatch_HeadForbiddenStatus1(self):

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v and r)

        open_and_update_file.update_file_contents(self.first_file1, "actual modification, second")

        v, r = git_wrapper.stash(self.first_repo)
        self.assertTrue(v)

        self.assertTrue(os.path.exists(self.first_file1))
        os.unlink(self.first_file1)
        self.assertFalse(os.path.exists(self.first_file1))

        v, r = git_wrapper.stage(self.first_repo, [self.first_file1])
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.first_repo, "conflict commit")
        self.assertTrue(v)

        v, r = git_wrapper.stash_pop(self.first_repo)
        self.assertFalse(v) # should fail because of conflict

        v, r = git_lib.get_head_deleted_updated_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertTrue(self.first_file1 in r[0])

        v, r = collect_git_patch._test_repo_status(self.first_repo)
        self.assertFalse(v)

        v, r = collect_git_patch.collect_git_patch(self.first_repo, self.storage_path, "include", [], [], True, False, False, 0, False, 0, None)
        self.assertFalse(v)

        v, r = git_lib.get_head_deleted_updated_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

    def testCollectGitPatch_CollectGitPatch_HeadForbiddenStatus2(self):

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        self.assertTrue(os.path.exists(self.first_file1))
        os.unlink(self.first_file1)
        self.assertFalse(os.path.exists(self.first_file1))

        v, r = git_wrapper.stash(self.first_repo)
        self.assertTrue(v)

        open_and_update_file.update_file_contents(self.first_file1, "stuff of extra")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.first_repo, "commit msg latest")
        self.assertTrue(v)

        v, r = git_wrapper.stash_pop(self.first_repo)
        self.assertFalse(v) # fails because of conflict

        v, r = git_lib.get_head_updated_deleted_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        v, r = collect_git_patch._test_repo_status(self.first_repo)
        self.assertFalse(v)

        v, r = collect_git_patch.collect_git_patch(self.first_repo, self.storage_path, "include", [], [], True, False, False, 0, False, 0, None)
        self.assertFalse(v)

        v, r = git_lib.get_head_updated_deleted_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

    def testCollectGitPatch_CollectGitPatch_HeadForbiddenStatus3(self):

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v and r)

        first_file1_renamed1 = path_utils.concat_path(self.first_repo, "file1_renamed1.txt")
        first_file1_renamed2 = path_utils.concat_path(self.first_repo, "file1_renamed2.txt")

        self.assertTrue(os.path.exists(self.first_file1))
        self.assertFalse(os.path.exists(first_file1_renamed1))
        self.assertFalse(os.path.exists(first_file1_renamed2))

        self.assertTrue(path_utils.copy_to_and_rename(self.first_file1, self.first_repo, path_utils.basename_filtered(first_file1_renamed1)))
        os.unlink(self.first_file1)
        self.assertFalse(os.path.exists(self.first_file1))
        self.assertTrue(os.path.exists(first_file1_renamed1))

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.stash(self.first_repo)
        self.assertTrue(v)

        self.assertTrue(os.path.exists(self.first_file1))
        self.assertFalse(os.path.exists(first_file1_renamed1))

        self.assertTrue(path_utils.copy_to_and_rename(self.first_file1, self.first_repo, path_utils.basename_filtered(first_file1_renamed2)))
        os.unlink(self.first_file1)
        self.assertFalse(os.path.exists(self.first_file1))
        self.assertTrue(os.path.exists(first_file1_renamed2))

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.stash_pop(self.first_repo)
        self.assertFalse(v) # should fail because of conflict

        v, r = git_lib.get_head_deleted_deleted_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertTrue(self.first_file1 in r[0])

        v, r = git_lib.get_head_updated_added_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertTrue(first_file1_renamed1 in r[0])

        v, r = git_lib.get_head_added_updated_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertTrue(first_file1_renamed2 in r[0])

        v, r = git_lib.soft_reset(self.first_repo, [first_file1_renamed1, first_file1_renamed2])
        self.assertTrue(v)
        os.unlink(first_file1_renamed1)
        os.unlink(first_file1_renamed2)

        v, r = git_lib.get_head_updated_added_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = git_lib.get_head_added_updated_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = git_lib.get_head_deleted_deleted_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertTrue(self.first_file1 in r[0])

        v, r = collect_git_patch._test_repo_status(self.first_repo)
        self.assertFalse(v)

        v, r = collect_git_patch.collect_git_patch(self.first_repo, self.storage_path, "include", [], [], True, False, False, 0, False, 0, None)
        self.assertFalse(v)

        v, r = git_lib.get_head_deleted_deleted_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertTrue(self.first_file1 in r[0])

    def testCollectGitPatch_CollectGitPatch_HeadForbiddenStatus4(self):

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v and r)

        first_file1_renamed1 = path_utils.concat_path(self.first_repo, "file1_renamed1.txt")
        first_file1_renamed2 = path_utils.concat_path(self.first_repo, "file1_renamed2.txt")

        self.assertTrue(os.path.exists(self.first_file1))
        self.assertFalse(os.path.exists(first_file1_renamed1))
        self.assertFalse(os.path.exists(first_file1_renamed2))

        self.assertTrue(path_utils.copy_to_and_rename(self.first_file1, self.first_repo, path_utils.basename_filtered(first_file1_renamed1)))
        os.unlink(self.first_file1)
        self.assertFalse(os.path.exists(self.first_file1))
        self.assertTrue(os.path.exists(first_file1_renamed1))

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.stash(self.first_repo)
        self.assertTrue(v)

        self.assertTrue(os.path.exists(self.first_file1))
        self.assertFalse(os.path.exists(first_file1_renamed1))

        self.assertTrue(path_utils.copy_to_and_rename(self.first_file1, self.first_repo, path_utils.basename_filtered(first_file1_renamed2)))
        os.unlink(self.first_file1)
        self.assertFalse(os.path.exists(self.first_file1))
        self.assertTrue(os.path.exists(first_file1_renamed2))

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.stash_pop(self.first_repo)
        self.assertFalse(v) # should fail because of conflict

        v, r = git_lib.get_head_deleted_deleted_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertTrue(self.first_file1 in r[0])

        v, r = git_lib.get_head_updated_added_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertTrue(first_file1_renamed1 in r[0])

        v, r = git_lib.get_head_added_updated_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertTrue(first_file1_renamed2 in r[0])

        v, r = git_lib.soft_reset(self.first_repo, [self.first_file1, first_file1_renamed2])
        self.assertTrue(v)
        os.unlink(first_file1_renamed2)

        v, r = git_lib.get_head_deleted_deleted_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = git_lib.get_head_added_updated_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = git_lib.get_head_updated_added_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertTrue(first_file1_renamed1 in r[0])

        v, r = collect_git_patch._test_repo_status(self.first_repo)
        self.assertFalse(v)

        v, r = collect_git_patch.collect_git_patch(self.first_repo, self.storage_path, "include", [], [], True, False, False, 0, False, 0, None)
        self.assertFalse(v)

        v, r = git_lib.get_head_deleted_deleted_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = git_lib.get_head_added_updated_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = git_lib.get_head_updated_added_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertTrue(first_file1_renamed1 in r[0])

    def testCollectGitPatch_CollectGitPatch_HeadForbiddenStatus5(self):

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v and r)

        first_file1_renamed1 = path_utils.concat_path(self.first_repo, "file1_renamed1.txt")
        first_file1_renamed2 = path_utils.concat_path(self.first_repo, "file1_renamed2.txt")

        self.assertTrue(os.path.exists(self.first_file1))
        self.assertFalse(os.path.exists(first_file1_renamed1))
        self.assertFalse(os.path.exists(first_file1_renamed2))

        self.assertTrue(path_utils.copy_to_and_rename(self.first_file1, self.first_repo, path_utils.basename_filtered(first_file1_renamed1)))
        os.unlink(self.first_file1)
        self.assertFalse(os.path.exists(self.first_file1))
        self.assertTrue(os.path.exists(first_file1_renamed1))

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.stash(self.first_repo)
        self.assertTrue(v)

        self.assertTrue(os.path.exists(self.first_file1))
        self.assertFalse(os.path.exists(first_file1_renamed1))

        self.assertTrue(path_utils.copy_to_and_rename(self.first_file1, self.first_repo, path_utils.basename_filtered(first_file1_renamed2)))
        os.unlink(self.first_file1)
        self.assertFalse(os.path.exists(self.first_file1))
        self.assertTrue(os.path.exists(first_file1_renamed2))

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.stash_pop(self.first_repo)
        self.assertFalse(v) # should fail because of conflict

        v, r = git_lib.get_head_deleted_deleted_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertTrue(self.first_file1 in r[0])

        v, r = git_lib.get_head_updated_added_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertTrue(first_file1_renamed1 in r[0])

        v, r = git_lib.get_head_added_updated_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertTrue(first_file1_renamed2 in r[0])

        v, r = git_lib.soft_reset(self.first_repo, [self.first_file1, first_file1_renamed1])
        self.assertTrue(v)
        os.unlink(first_file1_renamed1)

        v, r = git_lib.get_head_deleted_deleted_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = git_lib.get_head_added_updated_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertTrue(first_file1_renamed2 in r[0])

        v, r = git_lib.get_head_updated_added_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = collect_git_patch._test_repo_status(self.first_repo)
        self.assertFalse(v)

        v, r = collect_git_patch.collect_git_patch(self.first_repo, self.storage_path, "include", [], [], True, False, False, 0, False, 0, None)
        self.assertFalse(v)

        v, r = git_lib.get_head_deleted_deleted_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = git_lib.get_head_added_updated_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertTrue(first_file1_renamed2 in r[0])

        v, r = git_lib.get_head_updated_added_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

    def testCollectGitPatch_CollectGitPatch_HeadForbiddenStatus6(self):

        first_more1 = path_utils.concat_path(self.first_repo, "more1.txt")
        self.assertFalse(os.path.exists(first_more1))
        create_and_write_file.create_file_contents(first_more1, "more1-contents")
        self.assertTrue(os.path.exists(first_more1))

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.stash(self.first_repo)
        self.assertTrue(v)

        self.assertFalse(os.path.exists(first_more1))
        create_and_write_file.create_file_contents(first_more1, "more1-conflicting-contents")
        self.assertTrue(os.path.exists(first_more1))

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.stash_pop(self.first_repo)
        self.assertFalse(v) # should fail because of conflict

        v, r = git_lib.get_head_added_added_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertTrue(first_more1 in r[0])

        v, r = collect_git_patch._test_repo_status(self.first_repo)
        self.assertFalse(v)

        v, r = collect_git_patch.collect_git_patch(self.first_repo, self.storage_path, "include", [], [], True, False, False, 0, False, 0, None)
        self.assertFalse(v)

        v, r = git_lib.get_head_added_added_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertTrue(first_more1 in r[0])

    def testCollectGitPatch_CollectGitPatch_HeadForbiddenStatus7(self):

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v and r)

        first_file1_renamed = path_utils.concat_path(self.first_repo, "file1_renamed.txt")
        self.assertFalse(os.path.exists(first_file1_renamed))
        self.assertTrue(path_utils.copy_to_and_rename(self.first_file1, self.first_repo, path_utils.basename_filtered(first_file1_renamed)))
        self.assertTrue(os.path.exists(first_file1_renamed))
        os.unlink(self.first_file1)
        self.assertFalse(os.path.exists(self.first_file1))

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        open_and_update_file.update_file_contents(first_file1_renamed, "actual modification, again")

        v, r = git_lib.get_head_renamed_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertTrue(any(self.first_file1 in s for s in r))
        self.assertTrue(any(first_file1_renamed in s for s in r))

        v, r = collect_git_patch._test_repo_status(self.first_repo)
        self.assertFalse(v)

        v, r = collect_git_patch.collect_git_patch(self.first_repo, self.storage_path, "include", [], [], True, False, False, 0, False, 0, None)
        self.assertFalse(v)

        v, r = git_lib.get_head_renamed_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertTrue(any(self.first_file1 in s for s in r))
        self.assertTrue(any(first_file1_renamed in s for s in r))

if __name__ == "__main__":
    unittest.main()
