#!/usr/bin/env python3

import sys
import os
import shutil
import unittest

import path_utils
import fsquery
import create_and_write_file

import mvtools_test_fixture
import git_test_fixture
import git_wrapper

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

    def testGeneral(self):

        v, r = collect_git_patch.collect_git_patch(self.nonexistent, self.storage_path, "include", [], [], False, False, False, False, 0, 0)
        self.assertFalse(v)

        v, r = collect_git_patch.collect_git_patch(self.first_repo, self.nonexistent, "include", [], [], False, False, False, False, 0, 0)
        self.assertFalse(v)

        v, r = collect_git_patch.collect_git_patch(self.first_repo, self.storage_path, "include", [], [], False, False, False, False, 0, 0)
        self.assertTrue(v)

    def testGeneralBestEffort(self):

        v, r = collect_git_patch.collect_git_patch(self.first_repo, self.storage_path, "include", [], [], True, False, False, False, 0, 0)
        self.assertFalse(v)
        first_head_patch_filename = path_utils.concat_path(self.storage_path, self.first_repo, "head.patch")
        first_head_id_patch_filename = path_utils.concat_path(self.storage_path, self.first_repo, "head_id.txt")
        self.assertFalse( os.path.exists( first_head_patch_filename ) )
        self.assertFalse( os.path.exists( first_head_id_patch_filename ) )

        v, r = collect_git_patch.collect_git_patch(self.first_repo, self.storage_path, "include", [], [], True, True, False, False, 0, 0)
        second_head_patch_filename = path_utils.concat_path(self.storage_path, self.first_repo, "head.patch")
        second_head_id_patch_filename = path_utils.concat_path(self.storage_path, self.first_repo, "head_id.txt")
        self.assertFalse(v)
        self.assertNotEqual(r[0], second_head_id_patch_filename)
        self.assertEqual(r[1], second_head_id_patch_filename)
        self.assertFalse( os.path.exists( second_head_patch_filename ) )
        self.assertTrue( os.path.exists( second_head_id_patch_filename ) )

    def testCollectPatchHeadFail(self):

        with open(self.first_file1, "a") as f:
            f.write("extra")

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path, "include", [], [])
        self.assertTrue(v)
        patch_file = path_utils.concat_path(self.storage_path, self.first_repo, "head.patch")
        self.assertEqual(r, patch_file)
        self.assertTrue(os.path.exists(patch_file))
        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path, "include", [], [])
        self.assertFalse(v)

    def testCollectPatchHead1(self):

        with open(self.first_file1, "a") as f:
            f.write("extra")

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path, "include", [], [])
        self.assertTrue(v)

        patch_file = path_utils.concat_path(self.storage_path, self.first_repo, "head.patch")
        self.assertTrue(os.path.exists(patch_file))
        self.assertEqual(r, patch_file)

        contents_read = ""
        with open(patch_file) as f:
            contents_read = f.read()

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

        with open(self.first_file1, "a") as f:
            f.write("extra")

        with open(self.first_file2, "a") as f:
            f.write("smore stuff")

        with open(first_file7, "a") as f:
            f.write("onto-the-seventh")

        self.assertTrue(os.path.exists(self.first_file3))
        os.unlink(self.first_file3)
        self.assertFalse(os.path.exists(self.first_file3))

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path, "include", [], [])
        self.assertTrue(v)

        patch_file = path_utils.concat_path(self.storage_path, self.first_repo, "head.patch")
        self.assertTrue(os.path.exists(patch_file))
        self.assertEqual(r, patch_file)

        contents_read = ""
        with open(patch_file) as f:
            contents_read = f.read()

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

        with open(self.first_file1, "a") as f:
            f.write("extra")

        with open(self.first_file2, "a") as f:
            f.write("smore stuff")

        with open(self.first_file3, "a") as f:
            f.write("modifying the third too")

        with open(first_file7, "a") as f:
            f.write("onto-the-seventh")

        with open(first_sub1_another_file10, "a") as f:
            f.write("appending to s1-f10")

        with open(first_sub1_another_file17, "a") as f:
            f.write("more stuff for s1-f17")

        with open(first_sub2_another_file10, "a") as f:
            f.write("yet more contents onto s2-f10")

        with open(first_sub2_another_file19, "a") as f:
            f.write("some additional text for s2-f19")

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path, "include", [], [])
        self.assertTrue(v)
        self.assertTrue(os.path.exists(r))

        patch_file = path_utils.concat_path(self.storage_path, self.first_repo, "head.patch")
        self.assertTrue(os.path.exists(patch_file))
        self.assertEqual(r, patch_file)

        contents_read = ""
        with open(patch_file) as f:
            contents_read = f.read()

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

    def testCollectPatchHeadSub(self):

        with open(self.second_sub_file1, "a") as f:
            f.write("extra_sub")

        v, r = collect_git_patch.collect_git_patch_head(self.second_sub, self.storage_path, "include", [], [])
        self.assertTrue(v)

        patch_file = path_utils.concat_path(self.storage_path, self.second_sub, "head.patch")
        self.assertTrue(os.path.exists(patch_file))
        self.assertEqual(r, patch_file)

        contents_read = ""
        with open(patch_file) as f:
            contents_read = f.read()

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

        with open(self.first_file1, "a") as f:
            f.write("extra")

        with open(self.first_file2, "a") as f:
            f.write("smore stuff")

        with open(self.first_file3, "a") as f:
            f.write("modifying the third too")

        with open(first_file7, "a") as f:
            f.write("onto-the-seventh")

        with open(first_sub1_another_file10, "a") as f:
            f.write("appending to s1-f10")

        with open(first_sub1_another_file17, "a") as f:
            f.write("more stuff for s1-f17")

        with open(first_sub2_another_file10, "a") as f:
            f.write("yet more contents onto s2-f10")

        with open(first_sub2_another_file19, "a") as f:
            f.write("some additional text for s2-f19")

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path, "exclude", ["*/another/*"], [])
        self.assertTrue(v)
        self.assertTrue(os.path.exists(r))

        patch_file = path_utils.concat_path(self.storage_path, self.first_repo, "head.patch")
        self.assertTrue(os.path.exists(patch_file))
        self.assertEqual(r, patch_file)

        contents_read = ""
        with open(patch_file) as f:
            contents_read = f.read()

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

        contents_read = ""
        with open(patch_file) as f:
            contents_read = f.read()

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

        with open(first_file6, "a") as f:
            f.write("adding to file6")

        with open(first_sub1_file9, "a") as f:
            f.write("adding to sub1-file9")

        with open(first_sub1_another_file17, "a") as f:
            f.write("adding to sub1-file17")

        with open(first_sub2_another_file19, "a") as f:
            f.write("adding to sub2-file19")

        v, r = git_wrapper.stash(self.first_repo)
        self.assertTrue(v)

        with open(first_file6, "a") as f:
            f.write("!incompatible! adding to file6")

        with open(first_sub1_file9, "a") as f:
            f.write("!incompatible! adding to sub1-file9")

        with open(first_sub1_another_file17, "a") as f:
            f.write("!incompatible! adding to sub1-file17")

        with open(first_sub2_another_file19, "a") as f:
            f.write("!incompatible! adding to sub2-file19")

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

        contents_read = ""
        with open(patch_file) as f:
            contents_read = f.read()

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

        contents_read = ""
        with open(patch_file) as f:
            contents_read = f.read()

        self.assertGreaterEqual(len(contents_read), 40)

    def testCollectPatchHeadIdSub(self):

        v, r = collect_git_patch.collect_git_patch_head_id(self.second_sub, self.storage_path)
        self.assertTrue(v)

        patch_file = path_utils.concat_path(self.storage_path, self.second_sub, "head_id.txt")
        self.assertTrue(os.path.exists(patch_file))
        self.assertEqual(r, patch_file)

        contents_read = ""
        with open(patch_file) as f:
            contents_read = f.read()

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

        contents_read = ""
        with open(patch_file_first) as f:
            contents_read = f.read()
        self.assertGreaterEqual(len(contents_read), 40)

        contents_read = ""
        with open(patch_file_second) as f:
            contents_read = f.read()
        self.assertGreaterEqual(len(contents_read), 40)

    def testCollectPatchStagedFail(self):

        newfile = path_utils.concat_path(self.first_repo, "newfile.txt")
        if not create_and_write_file.create_file_contents(newfile, "newfilecontents"):
            self.fail("create_and_write_file command failed. Can't proceed.")

        if not git_wrapper.stage(self.first_repo):
            self.fail("")

        v, r = collect_git_patch.collect_git_patch_staged(self.first_repo, self.storage_path, "include", [], [])
        self.assertTrue(v)

        patch_file = path_utils.concat_path(self.storage_path, self.first_repo, "staged.patch")
        self.assertTrue(os.path.exists(patch_file))
        self.assertEqual(r, patch_file)

        v, r = collect_git_patch.collect_git_patch_staged(self.first_repo, self.storage_path, "include", [], [])
        self.assertFalse(v)

    def testCollectPatchStaged1(self):

        newfile = path_utils.concat_path(self.first_repo, "newfile.txt")
        if not create_and_write_file.create_file_contents(newfile, "newfilecontents"):
            self.fail("create_and_write_file command failed. Can't proceed.")

        if not git_wrapper.stage(self.first_repo):
            self.fail("")

        v, r = collect_git_patch.collect_git_patch_staged(self.first_repo, self.storage_path, "include", [], [])
        self.assertTrue(v)

        patch_file = path_utils.concat_path(self.storage_path, self.first_repo, "staged.patch")
        self.assertTrue(os.path.exists(patch_file))
        self.assertEqual(r, patch_file)

        contents_read = ""
        with open(patch_file) as f:
            contents_read = f.read()

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

        with open(self.first_file1, "a") as f:
            f.write("more file1")

        with open(self.first_file3, "a") as f:
            f.write("more file3")

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
        self.assertTrue(create_and_write_file.create_file_contents(first_file25, "file25-contents"))

        first_sub1_another_file30 = path_utils.concat_path(first_sub1_another, "file30.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_sub1_another_file30, "file30-contents"))

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = collect_git_patch.collect_git_patch_staged(self.first_repo, self.storage_path, "include", [], [])
        self.assertTrue(v)
        self.assertTrue(os.path.exists(r))

        patch_file = path_utils.concat_path(self.storage_path, self.first_repo, "staged.patch")
        self.assertTrue(os.path.exists(patch_file))
        self.assertEqual(r, patch_file)

        contents_read = ""
        with open(patch_file) as f:
            contents_read = f.read()

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

        with open(self.first_file1, "a") as f:
            f.write("more file1")

        with open(self.first_file3, "a") as f:
            f.write("more file3")

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
        self.assertTrue(create_and_write_file.create_file_contents(first_file25, "file25-contents"))

        first_sub1_another_file30 = path_utils.concat_path(first_sub1_another, "file30.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_sub1_another_file30, "file30-contents"))

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        with open(first_file5, "a") as f:
            f.write("mod f5")

        v, r = collect_git_patch.collect_git_patch_staged(self.first_repo, self.storage_path, "include", [], [])
        self.assertTrue(v)
        self.assertTrue(os.path.exists(r))

        patch_file = path_utils.concat_path(self.storage_path, self.first_repo, "staged.patch")
        self.assertTrue(os.path.exists(patch_file))
        self.assertEqual(r, patch_file)

        contents_read = ""
        with open(patch_file) as f:
            contents_read = f.read()

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
        if not create_and_write_file.create_file_contents(newfile, "newfilecontents_secondsub"):
            self.fail("create_and_write_file command failed. Can't proceed.")

        if not git_wrapper.stage(self.second_sub):
            self.fail("")

        v, r = collect_git_patch.collect_git_patch_staged(self.second_sub, self.storage_path, "include", [], [])
        self.assertTrue(v)

        patch_file = path_utils.concat_path(self.storage_path, self.second_sub, "staged.patch")
        self.assertTrue(os.path.exists(patch_file))
        self.assertEqual(r, patch_file)

        contents_read = ""
        with open(patch_file) as f:
            contents_read = f.read()

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

        with open(self.first_file1, "a") as f:
            f.write("more file1")

        with open(self.first_file3, "a") as f:
            f.write("more file3")

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
        self.assertTrue(create_and_write_file.create_file_contents(first_file25, "file25-contents"))

        first_sub1_another_file30 = path_utils.concat_path(first_sub1_another, "file30.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_sub1_another_file30, "file30-contents"))

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = collect_git_patch.collect_git_patch_staged(self.first_repo, self.storage_path, "exclude", ["*/file19_renamed.txt"], [])
        self.assertTrue(v)
        self.assertTrue(os.path.exists(r))

        patch_file = path_utils.concat_path(self.storage_path, self.first_repo, "staged.patch")
        self.assertTrue(os.path.exists(patch_file))
        self.assertEqual(r, patch_file)

        contents_read = ""
        with open(patch_file) as f:
            contents_read = f.read()

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

        with open(self.first_file1, "a") as f:
            f.write("more file1")

        with open(self.first_file3, "a") as f:
            f.write("more file3")

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
        self.assertTrue(create_and_write_file.create_file_contents(first_file25, "file25-contents"))

        first_sub1_another_file30 = path_utils.concat_path(first_sub1_another, "file30.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_sub1_another_file30, "file30-contents"))

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = collect_git_patch.collect_git_patch_staged(self.first_repo, self.storage_path, "include", [], ["*/sub2/*"])
        self.assertTrue(v)
        self.assertTrue(os.path.exists(r))

        patch_file = path_utils.concat_path(self.storage_path, self.first_repo, "staged.patch")
        self.assertTrue(os.path.exists(patch_file))
        self.assertEqual(r, patch_file)

        contents_read = ""
        with open(patch_file) as f:
            contents_read = f.read()

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

        with open(self.first_file1, "a") as f:
            f.write("more file1")

        with open(self.first_file3, "a") as f:
            f.write("more file3")

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
        self.assertTrue(create_and_write_file.create_file_contents(first_file25, "file25-contents"))

        first_sub1_another_file30 = path_utils.concat_path(first_sub1_another, "file30.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_sub1_another_file30, "file30-contents"))

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = collect_git_patch.collect_git_patch_staged(self.first_repo, self.storage_path, "exclude", ["*/file25.txt", "*/file30.txt"], [])
        self.assertTrue(v)
        self.assertTrue(os.path.exists(r))

        patch_file = path_utils.concat_path(self.storage_path, self.first_repo, "staged.patch")
        self.assertTrue(os.path.exists(patch_file))
        self.assertEqual(r, patch_file)

        contents_read = ""
        with open(patch_file) as f:
            contents_read = f.read()

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

        with open(self.first_file1, "a") as f:
            f.write("more file1")

        with open(self.first_file3, "a") as f:
            f.write("more file3")

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
        self.assertTrue(create_and_write_file.create_file_contents(first_file25, "file25-contents"))

        first_sub1_another_file30 = path_utils.concat_path(first_sub1_another, "file30.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_sub1_another_file30, "file30-contents"))

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = collect_git_patch.collect_git_patch_staged(self.first_repo, self.storage_path, "exclude", ["*/file4.txt", "*/file7.txt"], [])
        self.assertTrue(v)
        self.assertTrue(os.path.exists(r))

        patch_file = path_utils.concat_path(self.storage_path, self.first_repo, "staged.patch")
        self.assertTrue(os.path.exists(patch_file))
        self.assertEqual(r, patch_file)

        contents_read = ""
        with open(patch_file) as f:
            contents_read = f.read()

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

        with open(self.first_file1, "a") as f:
            f.write("more file1")

        with open(self.first_file3, "a") as f:
            f.write("more file3")

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
        self.assertTrue(create_and_write_file.create_file_contents(first_file25, "file25-contents"))

        first_sub1_another_file30 = path_utils.concat_path(first_sub1_another, "file30.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_sub1_another_file30, "file30-contents"))

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = collect_git_patch.collect_git_patch_staged(self.first_repo, self.storage_path, "exclude", ["*/file1.txt"], [])
        self.assertTrue(v)
        self.assertTrue(os.path.exists(r))

        patch_file = path_utils.concat_path(self.storage_path, self.first_repo, "staged.patch")
        self.assertTrue(os.path.exists(patch_file))
        self.assertEqual(r, patch_file)

        contents_read = ""
        with open(patch_file) as f:
            contents_read = f.read()

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

    def testCollectPatchUnversionedFail(self):

        newfile = path_utils.concat_path(self.first_repo, "newfile.txt")
        if not create_and_write_file.create_file_contents(newfile, "newfilecontents"):
            self.fail("create_and_write_file command failed. Can't proceed.")

        v, r = collect_git_patch.collect_git_patch_unversioned(self.first_repo, self.storage_path)
        self.assertTrue(v)

        newfile_storage = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "newfile.txt")
        self.assertTrue(os.path.exists(newfile_storage))
        self.assertEqual(r[0], newfile_storage)

        v, r = collect_git_patch.collect_git_patch_unversioned(self.first_repo, self.storage_path)
        self.assertFalse(v)

    def testCollectPatchUnversioned1(self):

        newfile = path_utils.concat_path(self.first_repo, "newfile.txt")
        if not create_and_write_file.create_file_contents(newfile, "newfilecontents"):
            self.fail("create_and_write_file command failed. Can't proceed.")

        newfolder = path_utils.concat_path(self.first_repo, "newfolder")
        os.mkdir(newfolder)

        newfoldernewfile2 = path_utils.concat_path(newfolder, "newfile2.txt")
        if not create_and_write_file.create_file_contents(newfoldernewfile2, "newfilecontents2"):
            self.fail("create_and_write_file command failed. Can't proceed.")

        newfoldernewfile3 = path_utils.concat_path(newfolder, "newfile3.txt")
        if not create_and_write_file.create_file_contents(newfoldernewfile3, "newfilecontents3"):
            self.fail("create_and_write_file command failed. Can't proceed.")

        anotherfolder = path_utils.concat_path(newfolder, "anotherfolder")
        os.mkdir(anotherfolder)

        anotherfoldernewfile4 = path_utils.concat_path(anotherfolder, "newfile4.txt")
        if not create_and_write_file.create_file_contents(anotherfoldernewfile4, "newfilecontents4"):
            self.fail("create_and_write_file command failed. Can't proceed.")

        v, r = collect_git_patch.collect_git_patch_unversioned(self.first_repo, self.storage_path)
        self.assertTrue(v)

        newfile_storage = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "newfile.txt")
        self.assertTrue(os.path.exists(newfile_storage))
        self.assertTrue(newfile_storage in r)

        contents_read = ""
        with open(newfile_storage) as f:
            contents_read = f.read()
        self.assertEqual(contents_read, "newfilecontents")

        newfolder_storage = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "newfolder")
        self.assertTrue(os.path.exists(newfolder_storage))

        newfoldernewfile2_storage = path_utils.concat_path(newfolder_storage, "newfile2.txt")
        self.assertTrue(os.path.exists(newfoldernewfile2_storage))
        self.assertTrue(newfoldernewfile2_storage in r)

        contents_read = ""
        with open(newfoldernewfile2_storage) as f:
            contents_read = f.read()
        self.assertEqual(contents_read, "newfilecontents2")

        newfoldernewfile3_storage = path_utils.concat_path(newfolder_storage, "newfile3.txt")
        self.assertTrue(os.path.exists(newfoldernewfile3_storage))
        self.assertTrue(newfoldernewfile3_storage in r)

        contents_read = ""
        with open(newfoldernewfile3_storage) as f:
            contents_read = f.read()
        self.assertEqual(contents_read, "newfilecontents3")

        anotherfolder_storage = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "newfolder", "anotherfolder")
        self.assertTrue(os.path.exists(anotherfolder_storage))

        anotherfoldernewfile4_storage = path_utils.concat_path(anotherfolder_storage, "newfile4.txt")
        self.assertTrue(os.path.exists(anotherfoldernewfile4_storage))
        self.assertTrue(anotherfoldernewfile4_storage in r)

        contents_read = ""
        with open(anotherfoldernewfile4_storage) as f:
            contents_read = f.read()
        self.assertEqual(contents_read, "newfilecontents4")

    def testCollectPatchUnversioned2(self):

        newfolder1 = path_utils.concat_path(self.first_repo, "newfolder1")
        os.mkdir(newfolder1)
        newfolder2 = path_utils.concat_path(newfolder1, "newfolder2")
        os.mkdir(newfolder2)

        newfolder2newfile1 = path_utils.concat_path(newfolder2, "newfile_twolevels.txt")
        if not create_and_write_file.create_file_contents(newfolder2newfile1, "newfile_twolevels-contents"):
            self.fail("create_and_write_file command failed. Can't proceed.")

        v, r = collect_git_patch.collect_git_patch_unversioned(self.first_repo, self.storage_path)
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
        if not create_and_write_file.create_file_contents(newfolder1newfile, "newfile-contents"):
            self.fail("create_and_write_file command failed. Can't proceed.")

        newfolder2newfile = path_utils.concat_path(newfolder2, "newfile.txt")
        if not create_and_write_file.create_file_contents(newfolder2newfile, "newfile-contents"):
            self.fail("create_and_write_file command failed. Can't proceed.")

        v, r = collect_git_patch.collect_git_patch_unversioned(self.first_repo, self.storage_path)
        self.assertTrue(v)

        newfolder1newfile_storage = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "newfolder1", "newfile.txt")
        self.assertTrue(os.path.exists(newfolder1newfile_storage))
        self.assertEqual(r[0], newfolder1newfile_storage)

        newfolder2newfile_storage = path_utils.concat_path(self.storage_path, self.first_repo, "unversioned", "newfolder2", "newfile.txt")
        self.assertTrue(os.path.exists(newfolder2newfile_storage))
        self.assertEqual(r[1], newfolder2newfile_storage)

    def testCollectPatchUnversioned4(self):

        first_repo_unvfile73 = path_utils.concat_path(self.first_repo, "unvfile73.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_repo_unvfile73, "dummy contents, file73"))

        first_repo_sub = path_utils.concat_path(self.first_repo, "sub")
        self.assertFalse(os.path.exists(first_repo_sub))
        os.mkdir(first_repo_sub)
        self.assertTrue(os.path.exists(first_repo_sub))

        first_repo_sub_committed_file = path_utils.concat_path(first_repo_sub, "committed_file.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, path_utils.concat_path(path_utils.basename_filtered(first_repo_sub), path_utils.basename_filtered(first_repo_sub_committed_file)), "committed-file-content", "commit msg, keep subfolder")
        self.assertTrue(v)

        first_repo_sub_unvfile715 = path_utils.concat_path(first_repo_sub, "unvfile715.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_repo_sub_unvfile715, "dummy contents, file715"))

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
        self.assertTrue(create_and_write_file.create_file_contents(first_repo_anothersub_onemorelvl_evenmore_unvfile330, "dummy contents, file330"))

        first_repo_anothersub_onemorelvl_evenmore_unvfile333 = path_utils.concat_path(first_repo_anothersub_onemorelvl_evenmore, "unvfile333.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_repo_anothersub_onemorelvl_evenmore_unvfile333, "dummy contents, file333"))

        first_repo_anothersub_onemorelvl_evenmore_andyetmore_unvfile762 = path_utils.concat_path(first_repo_anothersub_onemorelvl_evenmore_andyetmore, "unvfile762.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_repo_anothersub_onemorelvl_evenmore_andyetmore_unvfile762, "dummy contents, file762"))

        first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe_unvfile308 = path_utils.concat_path(first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe, "unvfile308.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_repo_anothersub_onemorelvl_evenmore_andyetmore_leafmaybe_unvfile308, "dummy contents, file308"))

        first_repo_anothersub_unvfile99 = path_utils.concat_path(first_repo_anothersub, "unvfile99.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_repo_anothersub_unvfile99, "dummy contents, file99"))

        first_repo_anothersub_unvfile47 = path_utils.concat_path(first_repo_anothersub, "unvfile47.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_repo_anothersub_unvfile47, "dummy contents, file47"))

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

        v, r = collect_git_patch.collect_git_patch_unversioned(self.first_repo, self.storage_path)
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

    def testCollectPatchUnversionedSub(self):

        newfile = path_utils.concat_path(self.second_sub, "newfile.txt")
        if not create_and_write_file.create_file_contents(newfile, "newfilecontents"):
            self.fail("create_and_write_file command failed. Can't proceed.")

        v, r = collect_git_patch.collect_git_patch_unversioned(self.second_sub, self.storage_path)
        self.assertTrue(v)

        newfile_storage = path_utils.concat_path(self.storage_path, self.second_sub, "unversioned", "newfile.txt")
        self.assertTrue(os.path.exists(newfile_storage))
        self.assertEqual(r[0], newfile_storage)

        contents_read = ""
        with open(newfile_storage) as f:
            contents_read = f.read()
        self.assertEqual(contents_read, "newfilecontents")

    def testCollectPatchStashFail(self):

        with open(self.first_file1, "a") as f:
            f.write("stashcontent1")

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

        patches = fsquery.makecontentlist(self.storage_path, False, True, False, False, False, True, None)
        self.assertEqual(len(patches), 0)

    def testCollectPatchStash1(self):

        with open(self.first_file1, "a") as f:
            f.write("stashcontent1")

        git_wrapper.stash(self.first_repo)

        with open(self.first_file2, "a") as f:
            f.write("stashcontent2")

        git_wrapper.stash(self.first_repo)

        v, r = collect_git_patch.collect_git_patch_stash(self.first_repo, self.storage_path, -1)
        self.assertTrue(v)

        stash1_storage = path_utils.concat_path(self.storage_path, self.first_repo, "stash@{0}.patch")
        self.assertTrue(os.path.exists(stash1_storage))
        self.assertEqual(r[0], stash1_storage)

        contents_read = ""
        with open(stash1_storage) as f:
            contents_read = f.read()
        self.assertTrue("stashcontent2" in contents_read)

        stash2_storage = path_utils.concat_path(self.storage_path, self.first_repo, "stash@{1}.patch")
        self.assertTrue(os.path.exists(stash2_storage))
        self.assertEqual(r[1], stash2_storage)

        contents_read = ""
        with open(stash2_storage) as f:
            contents_read = f.read()
        self.assertTrue("stashcontent1" in contents_read)

    def testCollectPatchStash2(self):

        with open(self.first_file1, "a") as f:
            f.write("stashcontent1")

        git_wrapper.stash(self.first_repo)

        with open(self.first_file2, "a") as f:
            f.write("stashcontent2")

        git_wrapper.stash(self.first_repo)

        v, r = collect_git_patch.collect_git_patch_stash(self.first_repo, self.storage_path, 1)
        self.assertTrue(v)

        stash1_storage = path_utils.concat_path(self.storage_path, self.first_repo, "stash@{0}.patch")
        self.assertTrue(os.path.exists(stash1_storage))
        self.assertEqual(r[0], stash1_storage)

        contents_read = ""
        with open(stash1_storage) as f:
            contents_read = f.read()
        self.assertTrue("stashcontent2" in contents_read)

        stash2_storage = path_utils.concat_path(self.storage_path, self.first_repo, "stash@{1}.patch")
        self.assertFalse(os.path.exists(stash2_storage))
        self.assertEqual(len(r), 1)

    def testCollectPatchStashSub(self):

        with open(self.second_sub_file1, "a") as f:
            f.write("stashcontent-sub")

        git_wrapper.stash(self.second_sub)

        v, r = collect_git_patch.collect_git_patch_stash(self.second_sub, self.storage_path, -1)
        self.assertTrue(v)

        stash1_storage = path_utils.concat_path(self.storage_path, self.second_sub, "stash@{0}.patch")
        self.assertTrue(os.path.exists(stash1_storage))
        self.assertEqual(r[0], stash1_storage)

        contents_read = ""
        with open(stash1_storage) as f:
            contents_read = f.read()
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

        contents_read = ""
        with open(patches[0]) as f:
            contents_read = f.read()
        self.assertTrue("first-adding-submodule" in contents_read)

        contents_read = ""
        with open(patches[1]) as f:
            contents_read = f.read()
        self.assertTrue("first-file3-content" in contents_read)

    def testCollectPatchPreviousSub(self):

        v, r = collect_git_patch.collect_git_patch_previous(self.second_sub, self.storage_path, 1)
        self.assertTrue(v)

        patches = self.get_patches_in_order(self.storage_path, self.second_sub)
        self.assertEqual(len(patches), 1)
        self.assertTrue( os.path.exists(patches[0]) )
        self.assertEqual(r[0], patches[0])

        contents_read = ""
        with open(patches[0]) as f:
            contents_read = f.read()
        self.assertTrue("second-file1-content" in contents_read)

    def testCollectGitPatch(self):
        pass # mvtodo {test combinations and doubletap (detect overwrites)}

if __name__ == '__main__':
    unittest.main()
