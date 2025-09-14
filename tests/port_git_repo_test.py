#!/usr/bin/env python

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
import port_git_repo

class PortGitRepoTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("port_git_repo_test")
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

    def testPortGitRepoBasicChecks(self):

        v, r = port_git_repo.port_git_repo(self.nonexistent, self.second_repo, "include", [], [], False, False, False, False, 0, None)
        self.assertFalse(v)

        v, r = port_git_repo.port_git_repo(self.first_repo, self.nonexistent, "include", [], [], False, False, False, False, 0, None)
        self.assertFalse(v)

        v, r = port_git_repo.port_git_repo(self.nonrepo, self.second_repo, "include", [], [], False, False, False, False, 0, None)
        self.assertFalse(v)

        v, r = port_git_repo.port_git_repo(self.first_repo, self.nonrepo, "include", [], [], False, False, False, False, 0, None)
        self.assertFalse(v)

        v, r = port_git_repo.port_git_repo(self.first_repo, self.second_repo, "include", [], [], False, False, False, False, 0, None)
        self.assertTrue(v)

    def testPortGitRepoStashFail(self):

        v, r = git_lib.get_stash_list(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = git_lib.get_stash_list(self.second_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = port_git_repo.port_git_repo_stash(self.storage_path, self.first_repo, self.second_repo, -1)
        self.assertFalse(v)

        v, r = git_lib.get_stash_list(self.second_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

    def testPortGitRepoStash1(self):

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

        v, r = port_git_repo.port_git_repo_stash(self.storage_path, self.first_repo, self.second_repo, -1)
        self.assertTrue(v)

        v, r = git_lib.get_stash_list(self.second_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

    def testPortGitRepoStash2(self):

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

        v, r = port_git_repo.port_git_repo_stash(self.storage_path, self.first_repo, self.second_repo, -1)
        self.assertTrue(v)

        v, r = git_lib.get_stash_list(self.second_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)

    def testPortGitRepoStash3(self):

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

        v, r = port_git_repo.port_git_repo_stash(self.storage_path, self.first_repo, self.second_repo, 1)
        self.assertTrue(v)

        v, r = git_lib.get_stash_list(self.second_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

    def testPortGitRepoPreviousFail1(self):

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertTrue(r)

        v, r = git_lib.is_head_clear(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(r)

        v, r = port_git_repo.port_git_repo_previous(self.storage_path, self.first_repo, self.second_repo, 4)
        self.assertFalse(v)

        v, r = git_lib.is_head_clear(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(r)

    def testPortGitRepoPreviousFail2(self):

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

        v, r = port_git_repo.port_git_repo_previous(self.storage_path, empty_repo, empty_repo_clone, 1)
        self.assertFalse(v)

        v, r = git_lib.is_head_clear(empty_repo_clone)
        self.assertTrue(v)
        self.assertTrue(r)

    def testPortGitRepoPrevious1(self):

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

        v, r = port_git_repo.port_git_repo_previous(self.storage_path, self.first_repo, self.second_repo, 1)
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.second_repo)
        self.assertTrue(v)
        self.assertFalse(r)

    def testPortGitRepoCherryPickPreviousFail1(self):

        v, r = port_git_repo.port_git_repo_cherry_pick_previous(self.storage_path, self.first_repo, self.second_repo, "tttt")
        self.assertFalse(v)

    def testPortGitRepoCherryPickPrevious1(self):

        with open(self.first_file1, "a") as f:
            f.write("target-of-cherry-picking")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.first_repo, "newmsg1")
        self.assertTrue(v)

        v, r = git_lib.get_head_hash(self.first_repo)
        self.assertTrue(v)
        head_hash = r

        v, r = port_git_repo.port_git_repo_cherry_pick_previous(self.storage_path, self.first_repo, self.second_repo, head_hash)
        self.assertTrue(v)

        second_file1 = path_utils.concat_path(self.second_repo, path_utils.basename_filtered(self.first_file1))

        contents = None
        with open(second_file1, "r") as f:
            contents = f.read()

        self.assertTrue("target-of-cherry-picking" in contents)

    def testPortGitRepoCherryPickPrevious2(self):

        with open(self.first_file1, "a") as f:
            f.write("target-of-cherry-picking")
        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)
        v, r = git_wrapper.commit(self.first_repo, "newmsg1")
        self.assertTrue(v)

        v, r = git_lib.get_head_hash(self.first_repo)
        self.assertTrue(v)
        stored_hash = r

        with open(self.first_file1, "a") as f:
            f.write("nondetectful")
        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)
        v, r = git_wrapper.commit(self.first_repo, "newmsg10")
        self.assertTrue(v)

        with open(self.first_file1, "a") as f:
            f.write("airlifting")
        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)
        v, r = git_wrapper.commit(self.first_repo, "newmsg100")
        self.assertTrue(v)

        v, r = port_git_repo.port_git_repo_cherry_pick_previous(self.storage_path, self.first_repo, self.second_repo, stored_hash)
        self.assertTrue(v)

        second_file1 = path_utils.concat_path(self.second_repo, path_utils.basename_filtered(self.first_file1))

        contents = None
        with open(second_file1, "r") as f:
            contents = f.read()

        self.assertTrue("target-of-cherry-picking" in contents)
        self.assertFalse("nondetectful" in contents)
        self.assertFalse("airlifting" in contents)

    def testPortGitRepoPrevious2(self):

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

        v, r = port_git_repo.port_git_repo_previous(self.storage_path, self.first_repo, self.second_repo, 2)
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.second_repo)
        self.assertTrue(v)
        self.assertFalse(r)

    def testPortGitRepoStaged1(self):

        with open(self.first_file1, "a") as f:
            f.write("latest1")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(r)

        v, r = port_git_repo.port_git_repo_staged(self.storage_path, self.first_repo, self.second_repo, "include", [], [])
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.second_repo)
        self.assertTrue(v)
        self.assertFalse(r)

    def testPortGitRepoStaged2(self):

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

        v, r = port_git_repo.port_git_repo_staged(self.storage_path, self.first_repo, self.second_repo, "include", [], [])
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.second_repo)
        self.assertTrue(v)
        self.assertFalse(r)

    def testPortGitRepoStaged3(self):

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertTrue(r)

        v, r = git_lib.is_head_clear(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(r)

        v, r = port_git_repo.port_git_repo_staged(self.storage_path, self.first_repo, self.second_repo, "include", [], [])
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(r)

    def testPortGitRepoHead1(self):

        with open(self.first_file1, "a") as f:
            f.write("latest1")

        v, r = git_lib.is_head_clear(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(r)

        v, r = port_git_repo.port_git_repo_head(self.storage_path, self.first_repo, self.second_repo, "include", [], [])
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.second_repo)
        self.assertTrue(v)
        self.assertFalse(r)

    def testPortGitRepoHead2(self):

        with open(self.first_file1, "a") as f:
            f.write("latest1")

        with open(self.first_file2, "a") as f:
            f.write("latest2")

        v, r = git_lib.is_head_clear(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(r)

        v, r = port_git_repo.port_git_repo_head(self.storage_path, self.first_repo, self.second_repo, "include", [], [])
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.second_repo)
        self.assertTrue(v)
        self.assertFalse(r)

    def testPortGitRepoHead3(self):

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertTrue(r)

        v, r = git_lib.is_head_clear(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(r)

        v, r = port_git_repo.port_git_repo_head(self.storage_path, self.first_repo, self.second_repo, "include", [], [])
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(r)

    def testPortGitRepoUnversionedFail(self):

        first_file4 = path_utils.concat_path(self.first_repo, "file4.txt")
        create_and_write_file.create_file_contents(first_file4, "file4-contents")

        first_sub1 = path_utils.concat_path(self.first_repo, "sub1")
        os.mkdir(first_sub1)

        first_sub1_sub2 = path_utils.concat_path(first_sub1, "sub2")
        os.mkdir(first_sub1_sub2)

        first_sub1_sub2_file5 = path_utils.concat_path(first_sub1_sub2, "file5.txt")
        create_and_write_file.create_file_contents(first_sub1_sub2_file5, "file5-contents")

        v, r = git_lib.is_head_clear(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(r)

        second_file4 = path_utils.concat_path(self.second_repo, "file4.txt")
        second_sub1 = path_utils.concat_path(self.second_repo, "sub1")
        second_sub1_sub2 = path_utils.concat_path(second_sub1, "sub2")
        second_sub1_sub2_file5 = path_utils.concat_path(second_sub1_sub2, "file5.txt")

        create_and_write_file.create_file_contents(second_file4, "file4-contents-dupe")

        v, r = port_git_repo.port_git_repo_unversioned(self.storage_path, self.first_repo, self.second_repo, "include", [], [])
        self.assertFalse(v)

        v, r = git_lib.is_head_clear(self.second_repo)
        self.assertTrue(v)
        self.assertFalse(r)

        self.assertTrue(os.path.exists(second_file4))
        self.assertFalse(os.path.exists(second_sub1))
        self.assertFalse(os.path.exists(second_sub1_sub2))
        self.assertFalse(os.path.exists(second_sub1_sub2_file5))

    def testPortGitRepoUnversioned(self):

        first_file4 = path_utils.concat_path(self.first_repo, "file4.txt")
        create_and_write_file.create_file_contents(first_file4, "file4-contents")

        first_sub1 = path_utils.concat_path(self.first_repo, "sub1")
        os.mkdir(first_sub1)

        first_sub1_sub2 = path_utils.concat_path(first_sub1, "sub2")
        os.mkdir(first_sub1_sub2)

        first_sub1_sub2_file5 = path_utils.concat_path(first_sub1_sub2, "file5.txt")
        create_and_write_file.create_file_contents(first_sub1_sub2_file5, "file5-contents")

        v, r = git_lib.is_head_clear(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(r)

        v, r = port_git_repo.port_git_repo_unversioned(self.storage_path, self.first_repo, self.second_repo, "include", [], [])
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

    def testPortGitRepo_Filtering1(self):

        with open(self.first_file1, "a") as f:
            f.write("modif - file1")

        with open(self.first_file2, "a") as f:
            f.write("modif - file2")

        self.assertTrue(os.path.exists(self.first_file3))
        os.unlink(self.first_file3)
        self.assertFalse(os.path.exists(self.first_file3))

        first_file4 = path_utils.concat_path(self.first_repo, "file4.txt")
        create_and_write_file.create_file_contents(first_file4, "file4-contents")

        first_file5 = path_utils.concat_path(self.first_repo, "file5.txt")
        create_and_write_file.create_file_contents(first_file5, "file5-contents")

        v, r = git_wrapper.stage(self.first_repo, [self.first_file2, first_file4])
        self.assertTrue(v)

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertTrue(self.first_file1 in r)
        self.assertTrue(self.first_file3 in r)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertTrue(self.first_file2 in r)
        self.assertTrue(first_file4 in r)

        v, r = git_lib.get_unversioned_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertTrue(first_file5 in r)

        v, r = git_lib.get_head_files(self.second_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = git_lib.get_staged_files(self.second_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = git_lib.get_unversioned_files(self.second_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = port_git_repo.port_git_repo(self.first_repo, self.second_repo, "include", [], [], True, True, False, True, 0, None)
        self.assertTrue(v)

        second_file1 = path_utils.concat_path(self.second_repo, "file1.txt")
        second_file2 = path_utils.concat_path(self.second_repo, "file2.txt")
        second_file3 = path_utils.concat_path(self.second_repo, "file3.txt")
        second_file4 = path_utils.concat_path(self.second_repo, "file4.txt")
        second_file5 = path_utils.concat_path(self.second_repo, "file5.txt")

        v, r = git_lib.get_head_files(self.second_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertTrue(second_file1 in r)
        self.assertTrue(second_file3 in r)

        v, r = git_lib.get_staged_files(self.second_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertTrue(second_file2 in r)
        self.assertTrue(second_file4 in r)

        v, r = git_lib.get_unversioned_files(self.second_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertTrue(second_file5 in r)

    def testPortGitRepo_Filtering2(self):

        with open(self.first_file1, "a") as f:
            f.write("modif - file1")

        with open(self.first_file2, "a") as f:
            f.write("modif - file2")

        self.assertTrue(os.path.exists(self.first_file3))
        os.unlink(self.first_file3)
        self.assertFalse(os.path.exists(self.first_file3))

        first_file4 = path_utils.concat_path(self.first_repo, "file4.txt")
        create_and_write_file.create_file_contents(first_file4, "file4-contents")

        first_file5 = path_utils.concat_path(self.first_repo, "file5.txt")
        create_and_write_file.create_file_contents(first_file5, "file5-contents")

        v, r = git_wrapper.stage(self.first_repo, [self.first_file2, first_file4])
        self.assertTrue(v)

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertTrue(self.first_file1 in r)
        self.assertTrue(self.first_file3 in r)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertTrue(self.first_file2 in r)
        self.assertTrue(first_file4 in r)

        v, r = git_lib.get_unversioned_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertTrue(first_file5 in r)

        v, r = git_lib.get_head_files(self.second_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = git_lib.get_staged_files(self.second_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = git_lib.get_unversioned_files(self.second_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = port_git_repo.port_git_repo(self.first_repo, self.second_repo, "include", [], ["*/file3.txt"], True, True, False, True, 0, None)
        self.assertTrue(v)

        second_file1 = path_utils.concat_path(self.second_repo, "file1.txt")
        second_file2 = path_utils.concat_path(self.second_repo, "file2.txt")
        second_file3 = path_utils.concat_path(self.second_repo, "file3.txt")
        second_file4 = path_utils.concat_path(self.second_repo, "file4.txt")
        second_file5 = path_utils.concat_path(self.second_repo, "file5.txt")

        v, r = git_lib.get_head_files(self.second_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertTrue(second_file1 in r)
        self.assertFalse(second_file3 in r)

        v, r = git_lib.get_staged_files(self.second_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertTrue(second_file2 in r)
        self.assertTrue(second_file4 in r)

        v, r = git_lib.get_unversioned_files(self.second_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertTrue(second_file5 in r)

    def testPortGitRepo_Filtering3(self):

        with open(self.first_file1, "a") as f:
            f.write("modif - file1")

        with open(self.first_file2, "a") as f:
            f.write("modif - file2")

        self.assertTrue(os.path.exists(self.first_file3))
        os.unlink(self.first_file3)
        self.assertFalse(os.path.exists(self.first_file3))

        first_file4 = path_utils.concat_path(self.first_repo, "file4.txt")
        create_and_write_file.create_file_contents(first_file4, "file4-contents")

        first_file5 = path_utils.concat_path(self.first_repo, "file5.txt")
        create_and_write_file.create_file_contents(first_file5, "file5-contents")

        v, r = git_wrapper.stage(self.first_repo, [self.first_file2, first_file4])
        self.assertTrue(v)

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertTrue(self.first_file1 in r)
        self.assertTrue(self.first_file3 in r)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertTrue(self.first_file2 in r)
        self.assertTrue(first_file4 in r)

        v, r = git_lib.get_unversioned_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertTrue(first_file5 in r)

        v, r = git_lib.get_head_files(self.second_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = git_lib.get_staged_files(self.second_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = git_lib.get_unversioned_files(self.second_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = port_git_repo.port_git_repo(self.first_repo, self.second_repo, "exclude", ["*/file5.txt"], [], True, True, False, True, 0, None)
        self.assertTrue(v)

        second_file1 = path_utils.concat_path(self.second_repo, "file1.txt")
        second_file2 = path_utils.concat_path(self.second_repo, "file2.txt")
        second_file3 = path_utils.concat_path(self.second_repo, "file3.txt")
        second_file4 = path_utils.concat_path(self.second_repo, "file4.txt")
        second_file5 = path_utils.concat_path(self.second_repo, "file5.txt")

        v, r = git_lib.get_head_files(self.second_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = git_lib.get_staged_files(self.second_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = git_lib.get_unversioned_files(self.second_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertTrue(second_file5 in r)

    def testPortGitRepo_Filtering4(self):

        with open(self.first_file1, "a") as f:
            f.write("modif - file1")

        with open(self.first_file2, "a") as f:
            f.write("modif - file2")

        self.assertTrue(os.path.exists(self.first_file3))
        os.unlink(self.first_file3)
        self.assertFalse(os.path.exists(self.first_file3))

        first_file4 = path_utils.concat_path(self.first_repo, "file4.txt")
        create_and_write_file.create_file_contents(first_file4, "file4-contents")

        first_file5 = path_utils.concat_path(self.first_repo, "file5.txt")
        create_and_write_file.create_file_contents(first_file5, "file5-contents")

        v, r = git_wrapper.stage(self.first_repo, [self.first_file2, first_file4])
        self.assertTrue(v)

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertTrue(self.first_file1 in r)
        self.assertTrue(self.first_file3 in r)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertTrue(self.first_file2 in r)
        self.assertTrue(first_file4 in r)

        v, r = git_lib.get_unversioned_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertTrue(first_file5 in r)

        v, r = git_lib.get_head_files(self.second_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = git_lib.get_staged_files(self.second_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = git_lib.get_unversioned_files(self.second_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = port_git_repo.port_git_repo(self.first_repo, self.second_repo, "exclude", ["*/file1.txt"], [], True, True, False, True, 0, None)
        self.assertTrue(v)

        second_file1 = path_utils.concat_path(self.second_repo, "file1.txt")
        second_file2 = path_utils.concat_path(self.second_repo, "file2.txt")
        second_file3 = path_utils.concat_path(self.second_repo, "file3.txt")
        second_file4 = path_utils.concat_path(self.second_repo, "file4.txt")
        second_file5 = path_utils.concat_path(self.second_repo, "file5.txt")

        v, r = git_lib.get_head_files(self.second_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertTrue(second_file1 in r)
        self.assertFalse(second_file3 in r)

        v, r = git_lib.get_staged_files(self.second_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = git_lib.get_unversioned_files(self.second_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

    def testPortGitRepo_Filtering5(self):

        with open(self.first_file1, "a") as f:
            f.write("modif - file1")

        with open(self.first_file2, "a") as f:
            f.write("modif - file2")

        self.assertTrue(os.path.exists(self.first_file3))
        os.unlink(self.first_file3)
        self.assertFalse(os.path.exists(self.first_file3))

        first_file4 = path_utils.concat_path(self.first_repo, "file4.txt")
        create_and_write_file.create_file_contents(first_file4, "file4-contents")

        first_file5 = path_utils.concat_path(self.first_repo, "file5.txt")
        create_and_write_file.create_file_contents(first_file5, "file5-contents")

        v, r = git_wrapper.stage(self.first_repo, [self.first_file2, first_file4])
        self.assertTrue(v)

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertTrue(self.first_file1 in r)
        self.assertTrue(self.first_file3 in r)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertTrue(self.first_file2 in r)
        self.assertTrue(first_file4 in r)

        v, r = git_lib.get_unversioned_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertTrue(first_file5 in r)

        v, r = git_lib.get_head_files(self.second_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = git_lib.get_staged_files(self.second_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = git_lib.get_unversioned_files(self.second_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = port_git_repo.port_git_repo(self.first_repo, self.second_repo, "exclude", [], [], True, True, False, True, 0, None)
        self.assertTrue(v)

        second_file1 = path_utils.concat_path(self.second_repo, "file1.txt")
        second_file2 = path_utils.concat_path(self.second_repo, "file2.txt")
        second_file3 = path_utils.concat_path(self.second_repo, "file3.txt")
        second_file4 = path_utils.concat_path(self.second_repo, "file4.txt")
        second_file5 = path_utils.concat_path(self.second_repo, "file5.txt")

        v, r = git_lib.get_head_files(self.second_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = git_lib.get_staged_files(self.second_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = git_lib.get_unversioned_files(self.second_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

if __name__ == "__main__":
    unittest.main()
