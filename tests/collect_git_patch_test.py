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

import collect_git_patch

class CollectGitPatchTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("collect_git_patch_test_base")
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
        v, r = git_test_fixture.git_initRepo(self.test_dir, "first", False)
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
        v, r = git_test_fixture.git_initRepo(self.test_dir, "second", False)
        if not v:
            return v, r

        self.second_file1 = path_utils.concat_path(self.second_repo, "file1.txt")
        v, r = git_test_fixture.git_createAndCommit(self.second_repo, "file1.txt", "second-file1-content", "second-file1-msg")
        if not v:
            return v, r

        # set second as first's submodule
        v, r = git_test_fixture.git_addSubmodule(self.second_repo, self.first_repo)
        if not v:
            return v, r

        v, r = git_test_fixture.git_commit(self.first_repo, "first-adding-submodule")
        if not v:
            return v, r

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def get_patches_in_order(self, path, repo_path):

        ret = []
        patches_ranked = {}

        patches = fsquery.makecontentlist(path, False, True, False, False, False, True, None)
        for p in patches:
            min_s = len(path_utils.basename_filtered(repo_path)) + 10
            pn = path_utils.basename_filtered(p)
            pi = pn.find("_", min_s)
            if pi == -1:
                return None
            rank = pn[min_s:pi]
            patches_ranked[rank] = p

        for p in sorted(patches_ranked.keys()):
            ret.append(patches_ranked[p])

        return ret

    def testHelperFunctions(self):
        self.assertEqual(collect_git_patch.get_stash_name("stash@{0}: WIP on master: a44cc87 upd"), "stash@{0}")
        self.assertEqual(collect_git_patch.get_stash_name(""), None)
        self.assertEqual(collect_git_patch.get_stash_name(None), None)

        self.assertEqual(collect_git_patch.get_prev_hash("a44cc87 (HEAD -> master) upd"), "a44cc87")
        self.assertEqual(collect_git_patch.get_prev_hash(""), None)
        self.assertEqual(collect_git_patch.get_prev_hash(None), None)

    def testGeneral(self):

        v, r = collect_git_patch.collect_git_patch(self.nonexistent, self.storage_path, False, False, False, False, False, 0)
        self.assertFalse(v)

        v, r = collect_git_patch.collect_git_patch(self.first_repo, self.nonexistent, False, False, False, False, False, 0)
        self.assertFalse(v)

        v, r = collect_git_patch.collect_git_patch(self.first_repo, self.storage_path, False, False, False, False, False, 0)
        self.assertTrue(v)

    def testPatchHeadFail(self):

        with open(self.first_file1, "a") as f:
            f.write("extra")

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path)
        self.assertTrue(v)
        patch_file = path_utils.concat_path(self.storage_path, "first_head.patch")
        self.assertTrue(os.path.exists(patch_file))
        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path)
        self.assertFalse(v)

    def testPatchHead(self):

        with open(self.first_file1, "a") as f:
            f.write("extra")

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path)
        self.assertTrue(v)

        patch_file = path_utils.concat_path(self.storage_path, "first_head.patch")
        self.assertTrue(os.path.exists(patch_file))

        contents_read = ""
        with open(patch_file) as f:
            contents_read = f.read()

        self.assertTrue("extra" in contents_read)

    def testPatchHeadIdFail(self):

        v, r = collect_git_patch.collect_git_patch_head_id(self.first_repo, self.storage_path)
        self.assertTrue(v)

        patch_file = path_utils.concat_path(self.storage_path, "first_head_id.txt")
        self.assertTrue(os.path.exists(patch_file))

        v, r = collect_git_patch.collect_git_patch_head_id(self.first_repo, self.storage_path)
        self.assertFalse(v)

    def testPatchHeadId(self):

        v, r = collect_git_patch.collect_git_patch_head_id(self.first_repo, self.storage_path)
        self.assertTrue(v)

        patch_file = path_utils.concat_path(self.storage_path, "first_head_id.txt")
        self.assertTrue(os.path.exists(patch_file))

        contents_read = ""
        with open(patch_file) as f:
            contents_read = f.read()

        self.assertGreaterEqual(len(contents_read), 40)

    def testPatchHeadStagedFail(self):

        newfile = path_utils.concat_path(self.first_repo, "newfile.txt")
        if not create_and_write_file.create_file_contents(newfile, "newfilecontents"):
            self.fail("create_and_write_file command failed. Can't proceed.")

        if not git_test_fixture.git_stage(self.first_repo):
            self.fail("")

        v, r = collect_git_patch.collect_git_patch_head_staged(self.first_repo, self.storage_path)
        self.assertTrue(v)

        patch_file = path_utils.concat_path(self.storage_path, "first_head_staged.patch")
        self.assertTrue(os.path.exists(patch_file))

        v, r = collect_git_patch.collect_git_patch_head_staged(self.first_repo, self.storage_path)
        self.assertFalse(v)

    def testPatchHeadStaged(self):

        newfile = path_utils.concat_path(self.first_repo, "newfile.txt")
        if not create_and_write_file.create_file_contents(newfile, "newfilecontents"):
            self.fail("create_and_write_file command failed. Can't proceed.")

        if not git_test_fixture.git_stage(self.first_repo):
            self.fail("")

        v, r = collect_git_patch.collect_git_patch_head_staged(self.first_repo, self.storage_path)
        self.assertTrue(v)

        patch_file = path_utils.concat_path(self.storage_path, "first_head_staged.patch")
        self.assertTrue(os.path.exists(patch_file))

        contents_read = ""
        with open(patch_file) as f:
            contents_read = f.read()

        self.assertTrue("newfilecontents" in contents_read)

    def testPatchHeadUnversionedFail(self):

        newfile = path_utils.concat_path(self.first_repo, "newfile.txt")
        if not create_and_write_file.create_file_contents(newfile, "newfilecontents"):
            self.fail("create_and_write_file command failed. Can't proceed.")

        v, r = collect_git_patch.collect_git_patch_head_unversioned(self.first_repo, self.storage_path)
        self.assertTrue(v)

        newfile_storage = path_utils.concat_path(self.storage_path, "head_unversioned", "newfile.txt")
        self.assertTrue(os.path.exists(newfile_storage))

        v, r = collect_git_patch.collect_git_patch_head_unversioned(self.first_repo, self.storage_path)
        self.assertFalse(v)

    def testPatchHeadUnversioned(self):

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

        v, r = collect_git_patch.collect_git_patch_head_unversioned(self.first_repo, self.storage_path)
        self.assertTrue(v)

        newfile_storage = path_utils.concat_path(self.storage_path, "head_unversioned", "newfile.txt")
        self.assertTrue(os.path.exists(newfile_storage))

        contents_read = ""
        with open(newfile_storage) as f:
            contents_read = f.read()
        self.assertEqual(contents_read, "newfilecontents")

        newfolder_storage = path_utils.concat_path(self.storage_path, "head_unversioned", "newfolder")
        self.assertTrue(os.path.exists(newfolder_storage))

        newfoldernewfile2_storage = path_utils.concat_path(newfolder_storage, "newfile2.txt")
        self.assertTrue(os.path.exists(newfoldernewfile2_storage))

        contents_read = ""
        with open(newfoldernewfile2_storage) as f:
            contents_read = f.read()
        self.assertEqual(contents_read, "newfilecontents2")

        newfoldernewfile3_storage = path_utils.concat_path(newfolder_storage, "newfile3.txt")
        self.assertTrue(os.path.exists(newfoldernewfile3_storage))

        contents_read = ""
        with open(newfoldernewfile3_storage) as f:
            contents_read = f.read()
        self.assertEqual(contents_read, "newfilecontents3")

        anotherfolder_storage = path_utils.concat_path(self.storage_path, "head_unversioned", "newfolder", "anotherfolder")
        self.assertTrue(os.path.exists(anotherfolder_storage))

        anotherfoldernewfile4_storage = path_utils.concat_path(anotherfolder_storage, "newfile4.txt")
        self.assertTrue(os.path.exists(anotherfoldernewfile4_storage))

        contents_read = ""
        with open(anotherfoldernewfile4_storage) as f:
            contents_read = f.read()
        self.assertEqual(contents_read, "newfilecontents4")

    def testPatchStashFail(self):

        with open(self.first_file1, "a") as f:
            f.write("stashcontent1")

        git_test_fixture.git_stash(self.first_repo)

        v, r = collect_git_patch.collect_git_patch_stash(self.first_repo, self.storage_path)
        self.assertTrue(v)

        stash1_storage = path_utils.concat_path(self.storage_path, "first_stash@{0}.patch")
        self.assertTrue(os.path.exists(stash1_storage))

        v, r = collect_git_patch.collect_git_patch_stash(self.first_repo, self.storage_path)
        self.assertFalse(v)

    def testPatchStash(self):

        with open(self.first_file1, "a") as f:
            f.write("stashcontent1")

        git_test_fixture.git_stash(self.first_repo)

        with open(self.first_file2, "a") as f:
            f.write("stashcontent2")

        git_test_fixture.git_stash(self.first_repo)

        v, r = collect_git_patch.collect_git_patch_stash(self.first_repo, self.storage_path)
        self.assertTrue(v)

        stash1_storage = path_utils.concat_path(self.storage_path, "first_stash@{0}.patch")
        self.assertTrue(os.path.exists(stash1_storage))

        contents_read = ""
        with open(stash1_storage) as f:
            contents_read = f.read()
        self.assertTrue("stashcontent2" in contents_read)

        stash2_storage = path_utils.concat_path(self.storage_path, "first_stash@{1}.patch")
        self.assertTrue(os.path.exists(stash2_storage))

        contents_read = ""
        with open(stash2_storage) as f:
            contents_read = f.read()
        self.assertTrue("stashcontent1" in contents_read)

    def testPatchPreviousFail1(self):

        v, r = collect_git_patch.collect_git_patch_previous(self.first_repo, self.storage_path, 5)
        self.assertFalse(v)

    def testPatchPreviousFail2(self):

        v, r = collect_git_patch.collect_git_patch_previous(self.first_repo, self.storage_path, 1)
        self.assertTrue(v)

        patches = self.get_patches_in_order(self.storage_path, self.first_repo)
        self.assertEqual(len(patches), 1)
        self.assertTrue( os.path.exists(patches[0]) )

        v, r = collect_git_patch.collect_git_patch_previous(self.first_repo, self.storage_path, 1)
        self.assertFalse(v)

    def testPatchPrevious(self):

        v, r = collect_git_patch.collect_git_patch_previous(self.first_repo, self.storage_path, 2)
        self.assertTrue(v)

        patches = self.get_patches_in_order(self.storage_path, self.first_repo)
        self.assertEqual(len(patches), 2)

        self.assertTrue( os.path.exists(patches[0]) )
        self.assertTrue( os.path.exists(patches[1]) )

        contents_read = ""
        with open(patches[0]) as f:
            contents_read = f.read()
        self.assertTrue("first-adding-submodule" in contents_read)

        contents_read = ""
        with open(patches[1]) as f:
            contents_read = f.read()
        self.assertTrue("first-file3-content" in contents_read)

    def testCollectGitPatch(self):
        pass # mvtodo {test combinations}

    # mvtodo: test submodule too

    # mvtodo: also test the double tap
    # mvtodo: comb for other stuff to test too

if __name__ == '__main__':
    unittest.main()
