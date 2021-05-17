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

        v, r = collect_git_patch.collect_git_patch(self.nonexistent, self.storage_path, False, False, False, False, False, 0)
        self.assertFalse(v)

        v, r = collect_git_patch.collect_git_patch(self.first_repo, self.nonexistent, False, False, False, False, False, 0)
        self.assertFalse(v)

        v, r = collect_git_patch.collect_git_patch(self.first_repo, self.storage_path, False, False, False, False, False, 0)
        self.assertTrue(v)

    def testGeneralBestEffort(self):

        v, r = collect_git_patch.collect_git_patch(self.first_repo, self.storage_path, True, False, False, False, False, 0)
        self.assertTrue(v)
        first_head_patch_filename = path_utils.concat_path(self.storage_path, self.first_repo, "head.patch")
        first_head_id_patch_filename = path_utils.concat_path(self.storage_path, self.first_repo, "head_id.txt")
        self.assertEqual(r[0], first_head_patch_filename)
        self.assertTrue( os.path.exists( first_head_patch_filename ) )
        self.assertFalse( os.path.exists( first_head_id_patch_filename ) )

        v, r = collect_git_patch.collect_git_patch(self.first_repo, self.storage_path, True, True, False, False, False, 0)
        second_head_patch_filename = path_utils.concat_path(self.storage_path, self.first_repo, "head.patch")
        second_head_id_patch_filename = path_utils.concat_path(self.storage_path, self.first_repo, "head_id.txt")
        self.assertFalse(v)
        self.assertNotEqual(r[0], second_head_id_patch_filename)
        self.assertEqual(r[1], second_head_id_patch_filename)
        self.assertTrue( os.path.exists( second_head_patch_filename ) )
        self.assertTrue( os.path.exists( second_head_id_patch_filename ) )

    def testPatchHeadFail(self):

        with open(self.first_file1, "a") as f:
            f.write("extra")

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path)
        self.assertTrue(v)
        patch_file = path_utils.concat_path(self.storage_path, self.first_repo, "head.patch")
        self.assertEqual(r, patch_file)
        self.assertTrue(os.path.exists(patch_file))
        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path)
        self.assertFalse(v)

    def testPatchHead(self):

        with open(self.first_file1, "a") as f:
            f.write("extra")

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path)
        self.assertTrue(v)

        patch_file = path_utils.concat_path(self.storage_path, self.first_repo, "head.patch")
        self.assertTrue(os.path.exists(patch_file))
        self.assertEqual(r, patch_file)

        contents_read = ""
        with open(patch_file) as f:
            contents_read = f.read()

        self.assertTrue("extra" in contents_read)

    def testPatchHeadSub(self):

        with open(self.second_sub_file1, "a") as f:
            f.write("extra_sub")

        v, r = collect_git_patch.collect_git_patch_head(self.second_sub, self.storage_path)
        self.assertTrue(v)

        patch_file = path_utils.concat_path(self.storage_path, self.second_sub, "head.patch")
        self.assertTrue(os.path.exists(patch_file))
        self.assertEqual(r, patch_file)

        contents_read = ""
        with open(patch_file) as f:
            contents_read = f.read()

        self.assertTrue("extra_sub" in contents_read)

    def testPatchHeadIdFail(self):

        v, r = collect_git_patch.collect_git_patch_head_id(self.first_repo, self.storage_path)
        self.assertTrue(v)

        patch_file = path_utils.concat_path(self.storage_path, self.first_repo, "head_id.txt")
        self.assertTrue(os.path.exists(patch_file))
        self.assertEqual(r, patch_file)

        v, r = collect_git_patch.collect_git_patch_head_id(self.first_repo, self.storage_path)
        self.assertFalse(v)

    def testPatchHeadId(self):

        v, r = collect_git_patch.collect_git_patch_head_id(self.first_repo, self.storage_path)
        self.assertTrue(v)

        patch_file = path_utils.concat_path(self.storage_path, self.first_repo, "head_id.txt")
        self.assertTrue(os.path.exists(patch_file))
        self.assertEqual(r, patch_file)

        contents_read = ""
        with open(patch_file) as f:
            contents_read = f.read()

        self.assertGreaterEqual(len(contents_read), 40)

    def testPatchHeadIdSub(self):

        v, r = collect_git_patch.collect_git_patch_head_id(self.second_sub, self.storage_path)
        self.assertTrue(v)

        patch_file = path_utils.concat_path(self.storage_path, self.second_sub, "head_id.txt")
        self.assertTrue(os.path.exists(patch_file))
        self.assertEqual(r, patch_file)

        contents_read = ""
        with open(patch_file) as f:
            contents_read = f.read()

        self.assertGreaterEqual(len(contents_read), 40)

    def testPatchHeadIdBoth(self):

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

    def testPatchStagedFail(self):

        newfile = path_utils.concat_path(self.first_repo, "newfile.txt")
        if not create_and_write_file.create_file_contents(newfile, "newfilecontents"):
            self.fail("create_and_write_file command failed. Can't proceed.")

        if not git_wrapper.stage(self.first_repo):
            self.fail("")

        v, r = collect_git_patch.collect_git_patch_staged(self.first_repo, self.storage_path)
        self.assertTrue(v)

        patch_file = path_utils.concat_path(self.storage_path, self.first_repo, "staged.patch")
        self.assertTrue(os.path.exists(patch_file))
        self.assertEqual(r, patch_file)

        v, r = collect_git_patch.collect_git_patch_staged(self.first_repo, self.storage_path)
        self.assertFalse(v)

    def testPatchStaged(self):

        newfile = path_utils.concat_path(self.first_repo, "newfile.txt")
        if not create_and_write_file.create_file_contents(newfile, "newfilecontents"):
            self.fail("create_and_write_file command failed. Can't proceed.")

        if not git_wrapper.stage(self.first_repo):
            self.fail("")

        v, r = collect_git_patch.collect_git_patch_staged(self.first_repo, self.storage_path)
        self.assertTrue(v)

        patch_file = path_utils.concat_path(self.storage_path, self.first_repo, "staged.patch")
        self.assertTrue(os.path.exists(patch_file))
        self.assertEqual(r, patch_file)

        contents_read = ""
        with open(patch_file) as f:
            contents_read = f.read()

        self.assertTrue("newfilecontents" in contents_read)

    def testPatchStagedSub(self):

        newfile = path_utils.concat_path(self.second_sub, "newfile_secondsub.txt")
        if not create_and_write_file.create_file_contents(newfile, "newfilecontents_secondsub"):
            self.fail("create_and_write_file command failed. Can't proceed.")

        if not git_wrapper.stage(self.second_sub):
            self.fail("")

        v, r = collect_git_patch.collect_git_patch_staged(self.second_sub, self.storage_path)
        self.assertTrue(v)

        patch_file = path_utils.concat_path(self.storage_path, self.second_sub, "staged.patch")
        self.assertTrue(os.path.exists(patch_file))
        self.assertEqual(r, patch_file)

        contents_read = ""
        with open(patch_file) as f:
            contents_read = f.read()

        self.assertTrue("newfilecontents_secondsub" in contents_read)

    def testPatchUnversionedFail(self):

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

    def testPatchUnversioned(self):

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

    def testPatchUnversioned2(self):

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

    def testPatchUnversioned3(self):

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

    def testPatchUnversionedSub(self):

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

    def testPatchStashFail(self):

        with open(self.first_file1, "a") as f:
            f.write("stashcontent1")

        git_wrapper.stash(self.first_repo)

        v, r = collect_git_patch.collect_git_patch_stash(self.first_repo, self.storage_path)
        self.assertTrue(v)

        stash1_storage = path_utils.concat_path(self.storage_path, self.first_repo, "stash@{0}.patch")
        self.assertTrue(os.path.exists(stash1_storage))
        self.assertEqual(r[0], stash1_storage)

        v, r = collect_git_patch.collect_git_patch_stash(self.first_repo, self.storage_path)
        self.assertFalse(v)


    def testPatchStashFail2(self):
        # no stash to collect
        git_wrapper.stash(self.first_repo)

        v, r = collect_git_patch.collect_git_patch_stash(self.first_repo, self.storage_path)
        self.assertTrue(v)

        patches = fsquery.makecontentlist(self.storage_path, False, True, False, False, False, True, None)
        self.assertEqual(len(patches), 0)

    def testPatchStash(self):

        with open(self.first_file1, "a") as f:
            f.write("stashcontent1")

        git_wrapper.stash(self.first_repo)

        with open(self.first_file2, "a") as f:
            f.write("stashcontent2")

        git_wrapper.stash(self.first_repo)

        v, r = collect_git_patch.collect_git_patch_stash(self.first_repo, self.storage_path)
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

    def testPatchStashSub(self):

        with open(self.second_sub_file1, "a") as f:
            f.write("stashcontent-sub")

        git_wrapper.stash(self.second_sub)

        v, r = collect_git_patch.collect_git_patch_stash(self.second_sub, self.storage_path)
        self.assertTrue(v)

        stash1_storage = path_utils.concat_path(self.storage_path, self.second_sub, "stash@{0}.patch")
        self.assertTrue(os.path.exists(stash1_storage))
        self.assertEqual(r[0], stash1_storage)

        contents_read = ""
        with open(stash1_storage) as f:
            contents_read = f.read()
        self.assertTrue("stashcontent-sub" in contents_read)

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

    def testPatchPreviousSub(self):

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
