#!/usr/bin/env python3

import sys
import os
import shutil
import unittest
from unittest import mock
from unittest.mock import patch

import mvtools_test_fixture
import git_test_fixture
import create_and_write_file
import path_utils
import string_utils

import git_wrapper
import collect_git_patch
import git_lib

class GitLibTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("git_lib_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # test repos paths
        self.first_repo = path_utils.concat_path(self.test_dir, "first")
        self.second_repo = path_utils.concat_path(self.test_dir, "second")
        self.third_repo = path_utils.concat_path(self.test_dir, "third")

        self.nonexistent_repo = path_utils.concat_path(self.test_dir, "nonexistent")

        self.fourth_notrepo = path_utils.concat_path(self.test_dir, "fourth")
        os.mkdir(self.fourth_notrepo)

        self.fifth_repo = path_utils.concat_path(self.test_dir, "fifth")

        self.storage_path = path_utils.concat_path(self.test_dir, "storage_path")
        os.mkdir(self.storage_path)

        # creates test repos
        v, r = git_wrapper.init(self.test_dir, "second", True)
        if not v:
            return v, r

        v, r = git_wrapper.clone(self.second_repo, self.first_repo, "origin")
        if not v:
            return v, r

        v, r = git_wrapper.clone(self.second_repo, self.third_repo, "origin")
        if not v:
            return v, r

        v, r = git_wrapper.init(self.test_dir, "fifth", False)
        if not v:
            return v, r

        # create a file with rubbish on first, and push it to its remote (second)
        self.first_file1 = path_utils.concat_path(self.first_repo, "file1.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, path_utils.basename_filtered(self.first_file1), "file1-content1", "commit_msg_file1")
        if not v:
            return v, r

        v, r = git_wrapper.push(self.first_repo, "origin", "master")
        if not v:
            return v, r

        # pull changes from first into third, through second
        v, r = git_wrapper.pull(self.third_repo, "origin", "master")
        if not v:
            return v, r

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testRemoveGitstatusSimpleDecorations(self):

        self.assertEqual(git_lib.remove_gitstatus_simple_decorations(None), None)
        self.assertEqual(git_lib.remove_gitstatus_simple_decorations("?? anothersub/"), "anothersub/")
        self.assertEqual(git_lib.remove_gitstatus_simple_decorations("?? file5.txt"), "file5.txt")
        self.assertEqual(git_lib.remove_gitstatus_simple_decorations("?? f"), "f")
        self.assertEqual(git_lib.remove_gitstatus_simple_decorations("A  subfolder/more4.txt"), "subfolder/more4.txt")
        self.assertEqual(git_lib.remove_gitstatus_simple_decorations("A   subfolder/more4.txt"), " subfolder/more4.txt")
        self.assertEqual(git_lib.remove_gitstatus_simple_decorations("A       subfolder/more4.txt"), "     subfolder/more4.txt")
        self.assertEqual(git_lib.remove_gitstatus_simple_decorations("? file5.txt"), None)
        self.assertEqual(git_lib.remove_gitstatus_simple_decorations("??? file5.txt"), None)

    def testChangeStashIndex(self):

        self.assertEqual(git_lib.change_stash_index(None, None), None)
        self.assertEqual(git_lib.change_stash_index("stash@{0}", None), None)
        self.assertEqual(git_lib.change_stash_index("stash@[0}", 1), None)
        self.assertEqual(git_lib.change_stash_index("stash@{0]", 1), None)
        self.assertEqual(git_lib.change_stash_index("{stash@0}", 1), None)
        self.assertEqual(git_lib.change_stash_index("}stash@{0", 1), None)
        self.assertEqual(git_lib.change_stash_index("stash@}{0", 1), None)
        self.assertEqual(git_lib.change_stash_index("stash@{0}", 1), "stash@{1}")
        self.assertEqual(git_lib.change_stash_index("stash@{0}", 25), "stash@{25}")

    def testGetStashName(self):

        self.assertEqual(git_lib.get_stash_name("stash@{0}: WIP on master: a44cc87 upd"), "stash@{0}")
        self.assertEqual(git_lib.get_stash_name(""), None)
        self.assertEqual(git_lib.get_stash_name(None), None)

    def testGetPrevHash(self):

        self.assertEqual(git_lib.get_prev_hash("a44cc87 (HEAD -> master) upd"), "a44cc87")
        self.assertEqual(git_lib.get_prev_hash(""), None)
        self.assertEqual(git_lib.get_prev_hash(None), None)

    def testGetRenamedDetails(self):

        self.assertEqual(None, None)
        self.assertEqual(git_lib.get_renamed_details(""), None)
        self.assertEqual(git_lib.get_renamed_details("->"), None)
        self.assertEqual(git_lib.get_renamed_details("/home/user/nuke/mvtools_tests/git_lib_test/first/more6.txt -+ more6_renamed.txt"), None)
        self.assertEqual(git_lib.get_renamed_details("/home/user/nuke/mvtools_tests/git_lib_test/first/more6.txt -> more6_renamed.txt"), ("/home/user/nuke/mvtools_tests/git_lib_test/first/more6.txt", "more6_renamed.txt"))

    def testGetRemotes(self):

        v, r = git_lib.get_remotes(self.fourth_notrepo)
        self.assertFalse(v)

        v, r = git_wrapper.remote_add(self.first_repo, "latest-addition", self.third_repo)
        self.assertTrue(v)

        v, r = git_lib.get_remotes(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(self.second_repo, r["origin"]["fetch"])
        self.assertEqual(self.third_repo, r["latest-addition"]["fetch"])

        v, r = git_wrapper.remote_add(self.first_repo, "latest-addition", self.third_repo)
        self.assertFalse(v) # disallow duplicates

        v, r = git_wrapper.remote_add(self.first_repo, "リモート", self.third_repo)
        self.assertTrue(v)

        v, r = git_lib.get_remotes(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(self.third_repo, r["リモート"]["fetch"])

    def testGetRemotesRelativePath(self):

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)

            v, r = git_lib.get_remotes("./fourth")
            self.assertFalse(v)

            v, r = git_wrapper.remote_add(self.first_repo, "latest-addition", self.third_repo)
            self.assertTrue(v)

            v, r = git_lib.get_remotes("./first")
            self.assertTrue(v)
            self.assertEqual(self.second_repo, r["origin"]["fetch"])
            self.assertEqual(self.third_repo, r["latest-addition"]["fetch"])

            v, r = git_wrapper.remote_add(self.first_repo, "latest-addition", self.third_repo)
            self.assertFalse(v) # disallow duplicates

            v, r = git_wrapper.remote_add(self.first_repo, "リモート", self.third_repo)
            self.assertTrue(v)

            v, r = git_lib.get_remotes("./first")
            self.assertTrue(v)
            self.assertEqual(self.third_repo, r["リモート"]["fetch"])

        finally:
            os.chdir(saved_wd)

    def testGetBranches(self):

        v, r = git_lib.get_branches(self.fifth_repo)
        self.assertTrue(v)
        self.assertEqual(r, [])
        v, r = git_lib.get_branches(self.fourth_notrepo)
        self.assertFalse(v)

        v, r = git_lib.get_branches(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0], "master")

        v, r = git_wrapper.branch_create_and_switch(self.first_repo, "new-branch")
        self.assertTrue(v)

        v, r = git_lib.get_branches(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertTrue("master" in r)
        self.assertTrue("new-branch" in r)

        v, r = git_wrapper.branch_create_and_switch(self.first_repo, "ブランチ")
        self.assertTrue(v)

        v, r = git_lib.get_branches(self.first_repo)
        self.assertTrue(v)
        self.assertTrue("ブランチ" in r)

    def testGetBranchesRelativePath(self):

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)

            v, r = git_lib.get_branches("./fifth")
            self.assertTrue(v)
            self.assertEqual(r, [])
            v, r = git_lib.get_branches("./fourth")
            self.assertFalse(v)

            v, r = git_lib.get_branches("./first")
            self.assertTrue(v)
            self.assertEqual(len(r), 1)
            self.assertEqual(r[0], "master")

            v, r = git_wrapper.branch_create_and_switch(self.first_repo, "new-branch")
            self.assertTrue(v)

            v, r = git_lib.get_branches("./first")
            self.assertTrue(v)
            self.assertEqual(len(r), 2)
            self.assertTrue("master" in r)
            self.assertTrue("new-branch" in r)

            v, r = git_wrapper.branch_create_and_switch(self.first_repo, "ブランチ")
            self.assertTrue(v)

            v, r = git_lib.get_branches("./first")
            self.assertTrue(v)
            self.assertTrue("ブランチ" in r)

        finally:
            os.chdir(saved_wd)

    def testGetCurrentBranch(self):

        v, r = git_lib.get_current_branch(self.fifth_repo)
        self.assertTrue(v)
        self.assertEqual(r, None)

        v, r = git_lib.get_current_branch(self.fourth_notrepo)
        self.assertFalse(v)
        self.assertNotEqual(r, None)

        v, r = git_lib.get_current_branch(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(r, "master")

        v, r = git_wrapper.branch_create_and_switch(self.first_repo, "another-branch")
        self.assertTrue(v)

        v, r = git_lib.get_current_branch(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(r, "another-branch")

    def testGetCurrentBranchRelativePath(self):

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)

            v, r = git_lib.get_current_branch("./fifth")
            self.assertTrue(v)
            self.assertEqual(r, None)

            v, r = git_lib.get_current_branch("./fourth")
            self.assertFalse(v)
            self.assertNotEqual(r, None)

            v, r = git_lib.get_current_branch("./first")
            self.assertTrue(v)
            self.assertEqual(r, "master")

            v, r = git_wrapper.branch_create_and_switch(self.first_repo, "another-branch")
            self.assertTrue(v)

            v, r = git_lib.get_current_branch("./first")
            self.assertTrue(v)
            self.assertEqual(r, "another-branch")

        finally:
            os.chdir(saved_wd)

    def testGetHeadFiles1(self):

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v and r)

        first_more1 = path_utils.concat_path(self.first_repo, "more1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_more1, "more1-contents"))

        first_more2 = path_utils.concat_path(self.first_repo, "more2.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_more2, "more2-contents"))

        first_more3 = path_utils.concat_path(self.first_repo, "more3.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, path_utils.basename_filtered(first_more3), "file3-content3", "commit_msg_file3")
        self.assertTrue(v)

        first_more4 = path_utils.concat_path(self.first_repo, "more4.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, path_utils.basename_filtered(first_more4), "file4-content4", "commit_msg_file4")
        self.assertTrue(v)

        v, r = git_wrapper.stage(self.first_repo, [first_more1])
        self.assertTrue(v)

        with open(self.first_file1, "a") as f:
            f.write("actual modification")

        v, r = git_wrapper.stage(self.first_repo, [self.first_file1])
        self.assertTrue(v)

        with open(first_more3, "a") as f:
            f.write("actual modification, again")

        self.assertTrue(os.path.exists(first_more4))
        os.unlink(first_more4)
        self.assertFalse(os.path.exists(first_more4))

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertTrue(first_more3 in r)
        self.assertTrue(first_more4 in r)
        self.assertFalse(first_more2 in r)

    def testGetHeadFiles2(self):

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v and r)

        with open(self.first_file1, "a") as f:
            f.write("morestuff")

        v, r = git_wrapper.stash(self.first_repo)
        self.assertTrue(v)

        with open(self.first_file1, "a") as f:
            f.write("differentmodif")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.first_repo, "modif-commit-msg")
        self.assertTrue(v)

        v, r = git_wrapper.stash_pop(self.first_repo)
        self.assertFalse(v) # failure because of conflict

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertTrue(self.first_repo in r[0])

    def testGetHeadFiles3(self):

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v and r)

        os.unlink(self.first_file1)
        self.assertFalse(os.path.exists(self.first_file1))

        v, r = git_wrapper.stash(self.first_repo)
        self.assertTrue(v)

        with open(self.first_file1, "a") as f:
            f.write("differentmodif")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.first_repo, "modif-commit-msg")
        self.assertTrue(v)

        v, r = git_wrapper.stash_pop(self.first_repo)
        self.assertFalse(v) # failure because of conflict

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertTrue(self.first_repo in r[0])

    def testGetHeadFilesRelativePath(self):

        sub1 = path_utils.concat_path(self.test_dir, "sub1")
        self.assertFalse(os.path.exists(sub1))
        os.mkdir(sub1)
        self.assertTrue(os.path.exists(sub1))

        sub1_testrepo = path_utils.concat_path(sub1, "testrepo")
        v, r = git_wrapper.init(sub1, "testrepo", False)
        self.assertTrue(v)
        self.assertTrue(os.path.exists(sub1_testrepo))

        testrepo_file1 = path_utils.concat_path(sub1_testrepo, "file1.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file1), "file1-content1", "commit_msg_file1")
        self.assertTrue(v)

        testrepo_file2 = path_utils.concat_path(sub1_testrepo, "file2.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file2), "file2-content1", "commit_msg_file2")
        self.assertTrue(v)

        testrepo_file3 = path_utils.concat_path(sub1_testrepo, "file3.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file3), "file3-content1", "commit_msg_file3")
        self.assertTrue(v)

        sub1_testrepo_sub2 = path_utils.concat_path(sub1_testrepo, "sub2")
        os.mkdir(sub1_testrepo_sub2)
        sub1_testrepo_sub3 = path_utils.concat_path(sub1_testrepo, "sub3")
        os.symlink(sub1_testrepo_sub2, sub1_testrepo_sub3)

        sub1_testrepo_sub2_file4 = path_utils.concat_path(sub1_testrepo_sub2, "file4.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo_sub2, path_utils.basename_filtered(sub1_testrepo_sub2_file4), "file4-content1", "commit_msg_file4")
        self.assertTrue(v)
        sub1_testrepo_sub3_file4 = path_utils.concat_path(sub1_testrepo_sub3, "file4.txt")

        self.assertTrue(os.path.exists(sub1_testrepo_sub2_file4))
        self.assertTrue(os.path.exists(sub1_testrepo_sub3_file4))

        with open(testrepo_file1, "a") as f:
            f.write("additional content f1")

        with open(testrepo_file3, "a") as f:
            f.write("additional content f3")

        os.unlink(sub1_testrepo_sub3_file4)
        self.assertFalse(os.path.exists(sub1_testrepo_sub3_file4))

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            v, r = git_lib.get_head_files("./sub1/testrepo")
            self.assertTrue(v)
            self.assertTrue(testrepo_file1 in r)
            self.assertFalse(testrepo_file2 in r)
            self.assertTrue(testrepo_file3 in r)
            self.assertTrue(sub1_testrepo_sub2_file4 in r)
            self.assertFalse(sub1_testrepo_sub3_file4 in r) # git resolves symlinks
        finally:
            os.chdir(saved_wd)

    def testGetHeadFilesRelativePathSymlinkRepo(self):

        sub2 = path_utils.concat_path(self.test_dir, "sub2")
        self.assertFalse(os.path.exists(sub2))
        os.mkdir(sub2)
        self.assertTrue(os.path.exists(sub2))

        sub1 = path_utils.concat_path(self.test_dir, "sub1")
        self.assertFalse(os.path.exists(sub1))
        os.symlink(sub2, sub1)
        self.assertTrue(os.path.exists(sub1))

        sub1_testrepo = path_utils.concat_path(sub1, "testrepo")
        v, r = git_wrapper.init(sub1, "testrepo", False)
        self.assertTrue(v)
        self.assertTrue(os.path.exists(sub1_testrepo))

        testrepo_file1 = path_utils.concat_path(sub1_testrepo, "file1.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file1), "file1-content1", "commit_msg_file1")
        self.assertTrue(v)

        testrepo_file2 = path_utils.concat_path(sub1_testrepo, "file2.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file2), "file2-content1", "commit_msg_file2")
        self.assertTrue(v)

        testrepo_file3 = path_utils.concat_path(sub1_testrepo, "file3.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file3), "file3-content1", "commit_msg_file3")
        self.assertTrue(v)

        sub1_testrepo_sub2 = path_utils.concat_path(sub1_testrepo, "sub2")
        os.mkdir(sub1_testrepo_sub2)
        sub1_testrepo_sub3 = path_utils.concat_path(sub1_testrepo, "sub3")
        os.symlink(sub1_testrepo_sub2, sub1_testrepo_sub3)

        sub1_testrepo_sub2_file4 = path_utils.concat_path(sub1_testrepo_sub2, "file4.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo_sub2, path_utils.basename_filtered(sub1_testrepo_sub2_file4), "file4-content1", "commit_msg_file4")
        self.assertTrue(v)
        sub1_testrepo_sub3_file4 = path_utils.concat_path(sub1_testrepo_sub3, "file4.txt")

        self.assertTrue(os.path.exists(sub1_testrepo_sub2_file4))
        self.assertTrue(os.path.exists(sub1_testrepo_sub3_file4))

        with open(testrepo_file1, "a") as f:
            f.write("additional content f1")

        with open(testrepo_file3, "a") as f:
            f.write("additional content f3")

        os.unlink(sub1_testrepo_sub3_file4)
        self.assertFalse(os.path.exists(sub1_testrepo_sub3_file4))

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            v, r = git_lib.get_head_files("./sub1/testrepo")
            self.assertTrue(v)
            self.assertTrue(testrepo_file1 in r)
            self.assertFalse(testrepo_file2 in r)
            self.assertTrue(testrepo_file3 in r)
            self.assertTrue(sub1_testrepo_sub2_file4 in r)
            self.assertFalse(sub1_testrepo_sub3_file4 in r) # git resolves symlinks
        finally:
            os.chdir(saved_wd)

    def testGetHeadModifiedFiles(self):

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v and r)

        first_more1 = path_utils.concat_path(self.first_repo, "more1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_more1, "more1-contents"))

        first_more2 = path_utils.concat_path(self.first_repo, "more2.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_more2, "more2-contents"))

        first_more3 = path_utils.concat_path(self.first_repo, "more3.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, path_utils.basename_filtered(first_more3), "file3-content3", "commit_msg_file3")
        self.assertTrue(v)

        v, r = git_wrapper.stage(self.first_repo, [first_more1])
        self.assertTrue(v)

        with open(self.first_file1, "a") as f:
            f.write("actual modification")

        v, r = git_wrapper.stage(self.first_repo, [self.first_file1])
        self.assertTrue(v)

        with open(first_more3, "a") as f:
            f.write("actual modification, again")

        v, r = git_lib.get_head_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(r, [first_more3])

    def testGetHeadUpdatedFiles(self):

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v and r)

        with open(self.first_file1, "a") as f:
            f.write("actual modification, first")

        v, r = git_wrapper.stash(self.first_repo)
        self.assertTrue(v)

        with open(self.first_file1, "a") as f:
            f.write("actual modification, second")

        v, r = git_wrapper.stage(self.first_repo, [self.first_file1])
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.first_repo, "conflict commit")
        self.assertTrue(v)

        v, r = git_wrapper.stash_pop(self.first_repo)
        self.assertFalse(v) # should fail because of conflict

        v, r = git_lib.get_head_updated_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertTrue(self.first_file1 in r[0])

    def testGetHeadUpdatedDeletedFiles(self):

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v and r)

        self.assertTrue(os.path.exists(self.first_file1))
        os.unlink(self.first_file1)
        self.assertFalse(os.path.exists(self.first_file1))

        v, r = git_wrapper.stash(self.first_repo)
        self.assertTrue(v)

        with open(self.first_file1, "a") as f:
            f.write("actual modification, second")

        v, r = git_wrapper.stage(self.first_repo, [self.first_file1])
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.first_repo, "conflict commit")
        self.assertTrue(v)

        v, r = git_wrapper.stash_pop(self.first_repo)
        self.assertFalse(v) # should fail because of conflict

        v, r = git_lib.get_head_updated_deleted_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertTrue(self.first_file1 in r[0])

    def testGetHeadDeletedUpdatedFiles(self):

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v and r)

        with open(self.first_file1, "a") as f:
            f.write("actual modification, second")

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

    def testGetHeadModifiedFilesRelativePath(self):

        sub1 = path_utils.concat_path(self.test_dir, "sub1")
        self.assertFalse(os.path.exists(sub1))
        os.mkdir(sub1)
        self.assertTrue(os.path.exists(sub1))

        sub1_testrepo = path_utils.concat_path(sub1, "testrepo")
        v, r = git_wrapper.init(sub1, "testrepo", False)
        self.assertTrue(v)
        self.assertTrue(os.path.exists(sub1_testrepo))

        testrepo_file1 = path_utils.concat_path(sub1_testrepo, "file1.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file1), "file1-content1", "commit_msg_file1")
        self.assertTrue(v)

        testrepo_file2 = path_utils.concat_path(sub1_testrepo, "file2.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file2), "file2-content1", "commit_msg_file2")
        self.assertTrue(v)

        testrepo_file3 = path_utils.concat_path(sub1_testrepo, "file3.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file3), "file3-content1", "commit_msg_file3")
        self.assertTrue(v)

        sub1_testrepo_sub2 = path_utils.concat_path(sub1_testrepo, "sub2")
        os.mkdir(sub1_testrepo_sub2)
        sub1_testrepo_sub3 = path_utils.concat_path(sub1_testrepo, "sub3")
        os.symlink(sub1_testrepo_sub2, sub1_testrepo_sub3)

        sub1_testrepo_sub2_file4 = path_utils.concat_path(sub1_testrepo_sub2, "file4.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo_sub2, path_utils.basename_filtered(sub1_testrepo_sub2_file4), "file4-content1", "commit_msg_file4")
        self.assertTrue(v)
        sub1_testrepo_sub3_file4 = path_utils.concat_path(sub1_testrepo_sub3, "file4.txt")

        self.assertTrue(os.path.exists(sub1_testrepo_sub2_file4))
        self.assertTrue(os.path.exists(sub1_testrepo_sub3_file4))

        with open(testrepo_file1, "a") as f:
            f.write("additional content f1")

        with open(testrepo_file3, "a") as f:
            f.write("additional content f3")

        with open(sub1_testrepo_sub3_file4, "a") as f:
            f.write("additional content f4")

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            v, r = git_lib.get_head_modified_files("./sub1/testrepo")
            self.assertTrue(v)
            self.assertTrue(testrepo_file1 in r)
            self.assertFalse(testrepo_file2 in r)
            self.assertTrue(testrepo_file3 in r)
            self.assertTrue(sub1_testrepo_sub2_file4 in r)
            self.assertFalse(sub1_testrepo_sub3_file4 in r) # git resolves symlinks
        finally:
            os.chdir(saved_wd)

    def testGetHeadModifiedFilesRelativePathSymlinkRepo(self):

        sub2 = path_utils.concat_path(self.test_dir, "sub2")
        self.assertFalse(os.path.exists(sub2))
        os.mkdir(sub2)
        self.assertTrue(os.path.exists(sub2))

        sub1 = path_utils.concat_path(self.test_dir, "sub1")
        self.assertFalse(os.path.exists(sub1))
        os.symlink(sub2, sub1)
        self.assertTrue(os.path.exists(sub1))

        sub1_testrepo = path_utils.concat_path(sub1, "testrepo")
        v, r = git_wrapper.init(sub1, "testrepo", False)
        self.assertTrue(v)
        self.assertTrue(os.path.exists(sub1_testrepo))

        testrepo_file1 = path_utils.concat_path(sub1_testrepo, "file1.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file1), "file1-content1", "commit_msg_file1")
        self.assertTrue(v)

        testrepo_file2 = path_utils.concat_path(sub1_testrepo, "file2.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file2), "file2-content1", "commit_msg_file2")
        self.assertTrue(v)

        testrepo_file3 = path_utils.concat_path(sub1_testrepo, "file3.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file3), "file3-content1", "commit_msg_file3")
        self.assertTrue(v)

        sub1_testrepo_sub2 = path_utils.concat_path(sub1_testrepo, "sub2")
        os.mkdir(sub1_testrepo_sub2)
        sub1_testrepo_sub3 = path_utils.concat_path(sub1_testrepo, "sub3")
        os.symlink(sub1_testrepo_sub2, sub1_testrepo_sub3)

        sub1_testrepo_sub2_file4 = path_utils.concat_path(sub1_testrepo_sub2, "file4.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo_sub2, path_utils.basename_filtered(sub1_testrepo_sub2_file4), "file4-content1", "commit_msg_file4")
        self.assertTrue(v)
        sub1_testrepo_sub3_file4 = path_utils.concat_path(sub1_testrepo_sub3, "file4.txt")

        self.assertTrue(os.path.exists(sub1_testrepo_sub2_file4))
        self.assertTrue(os.path.exists(sub1_testrepo_sub3_file4))

        with open(testrepo_file1, "a") as f:
            f.write("additional content f1")

        with open(testrepo_file3, "a") as f:
            f.write("additional content f3")

        with open(sub1_testrepo_sub3_file4, "a") as f:
            f.write("additional content f4")

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            v, r = git_lib.get_head_modified_files("./sub1/testrepo")
            self.assertTrue(v)
            self.assertTrue(testrepo_file1 in r)
            self.assertFalse(testrepo_file2 in r)
            self.assertTrue(testrepo_file3 in r)
            self.assertTrue(sub1_testrepo_sub2_file4 in r)
            self.assertFalse(sub1_testrepo_sub3_file4 in r) # git resolves symlinks
        finally:
            os.chdir(saved_wd)

    def testGetHeadDeletedFiles(self):

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v and r)

        first_more1 = path_utils.concat_path(self.first_repo, "more1.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, path_utils.basename_filtered(first_more1), "file1-content1", "commit_msg_file1")
        self.assertTrue(v)

        first_more2 = path_utils.concat_path(self.first_repo, "more2.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_more2, "more2-contents"))

        first_more3 = path_utils.concat_path(self.first_repo, "more3.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, path_utils.basename_filtered(first_more3), "file3-content3", "commit_msg_file3")
        self.assertTrue(v)

        os.unlink(first_more1)
        self.assertFalse(os.path.exists(first_more1))

        os.unlink(first_more2)
        self.assertFalse(os.path.exists(first_more2))

        v, r = git_lib.get_head_deleted_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(r, [first_more1])

    def testGetHeadDeletedFilesRelativePath(self):

        sub1 = path_utils.concat_path(self.test_dir, "sub1")
        self.assertFalse(os.path.exists(sub1))
        os.mkdir(sub1)
        self.assertTrue(os.path.exists(sub1))

        sub1_testrepo = path_utils.concat_path(sub1, "testrepo")
        v, r = git_wrapper.init(sub1, "testrepo", False)
        self.assertTrue(v)
        self.assertTrue(os.path.exists(sub1_testrepo))

        testrepo_file1 = path_utils.concat_path(sub1_testrepo, "file1.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file1), "file1-content1", "commit_msg_file1")
        self.assertTrue(v)

        testrepo_file2 = path_utils.concat_path(sub1_testrepo, "file2.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file2), "file2-content1", "commit_msg_file2")
        self.assertTrue(v)

        testrepo_file3 = path_utils.concat_path(sub1_testrepo, "file3.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file3), "file3-content1", "commit_msg_file3")
        self.assertTrue(v)

        sub1_testrepo_sub2 = path_utils.concat_path(sub1_testrepo, "sub2")
        os.mkdir(sub1_testrepo_sub2)
        sub1_testrepo_sub3 = path_utils.concat_path(sub1_testrepo, "sub3")
        os.symlink(sub1_testrepo_sub2, sub1_testrepo_sub3)

        sub1_testrepo_sub2_file4 = path_utils.concat_path(sub1_testrepo_sub2, "file4.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo_sub2, path_utils.basename_filtered(sub1_testrepo_sub2_file4), "file4-content1", "commit_msg_file4")
        self.assertTrue(v)
        sub1_testrepo_sub3_file4 = path_utils.concat_path(sub1_testrepo_sub3, "file4.txt")

        self.assertTrue(os.path.exists(sub1_testrepo_sub2_file4))
        self.assertTrue(os.path.exists(sub1_testrepo_sub3_file4))

        os.unlink(testrepo_file1)
        self.assertFalse(os.path.exists(testrepo_file1))
        os.unlink(sub1_testrepo_sub3_file4)
        self.assertFalse(os.path.exists(sub1_testrepo_sub3_file4))

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            v, r = git_lib.get_head_deleted_files("./sub1/testrepo")
            self.assertTrue(v)
            self.assertTrue(testrepo_file1 in r)
            self.assertFalse(testrepo_file2 in r)
            self.assertFalse(testrepo_file3 in r)
            self.assertTrue(sub1_testrepo_sub2_file4 in r)
            self.assertFalse(sub1_testrepo_sub3_file4 in r) # git resolves symlinks
        finally:
            os.chdir(saved_wd)

    def testGetHeadDeletedFilesRelativePathSymlinkRepo(self):

        sub2 = path_utils.concat_path(self.test_dir, "sub2")
        self.assertFalse(os.path.exists(sub2))
        os.mkdir(sub2)
        self.assertTrue(os.path.exists(sub2))

        sub1 = path_utils.concat_path(self.test_dir, "sub1")
        self.assertFalse(os.path.exists(sub1))
        os.symlink(sub2, sub1)
        self.assertTrue(os.path.exists(sub1))

        sub1_testrepo = path_utils.concat_path(sub1, "testrepo")
        v, r = git_wrapper.init(sub1, "testrepo", False)
        self.assertTrue(v)
        self.assertTrue(os.path.exists(sub1_testrepo))

        testrepo_file1 = path_utils.concat_path(sub1_testrepo, "file1.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file1), "file1-content1", "commit_msg_file1")
        self.assertTrue(v)

        testrepo_file2 = path_utils.concat_path(sub1_testrepo, "file2.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file2), "file2-content1", "commit_msg_file2")
        self.assertTrue(v)

        testrepo_file3 = path_utils.concat_path(sub1_testrepo, "file3.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file3), "file3-content1", "commit_msg_file3")
        self.assertTrue(v)

        sub1_testrepo_sub2 = path_utils.concat_path(sub1_testrepo, "sub2")
        os.mkdir(sub1_testrepo_sub2)
        sub1_testrepo_sub3 = path_utils.concat_path(sub1_testrepo, "sub3")
        os.symlink(sub1_testrepo_sub2, sub1_testrepo_sub3)

        sub1_testrepo_sub2_file4 = path_utils.concat_path(sub1_testrepo_sub2, "file4.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo_sub2, path_utils.basename_filtered(sub1_testrepo_sub2_file4), "file4-content1", "commit_msg_file4")
        self.assertTrue(v)
        sub1_testrepo_sub3_file4 = path_utils.concat_path(sub1_testrepo_sub3, "file4.txt")

        self.assertTrue(os.path.exists(sub1_testrepo_sub2_file4))
        self.assertTrue(os.path.exists(sub1_testrepo_sub3_file4))

        os.unlink(testrepo_file1)
        os.unlink(testrepo_file3)
        os.unlink(sub1_testrepo_sub3_file4)

        self.assertFalse(os.path.exists(testrepo_file1))
        self.assertFalse(os.path.exists(testrepo_file3))
        self.assertFalse(os.path.exists(sub1_testrepo_sub3_file4))

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            v, r = git_lib.get_head_deleted_files("./sub1/testrepo")
            self.assertTrue(v)
            self.assertTrue(testrepo_file1 in r)
            self.assertFalse(testrepo_file2 in r)
            self.assertTrue(testrepo_file3 in r)
            self.assertTrue(sub1_testrepo_sub2_file4 in r)
            self.assertFalse(sub1_testrepo_sub3_file4 in r) # git resolves symlinks
        finally:
            os.chdir(saved_wd)

    def testGetStagedFiles(self):

        v, r = git_lib.get_staged_files(self.fourth_notrepo)
        self.assertFalse(v)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(r, [])

        first_more1 = path_utils.concat_path(self.first_repo, "more1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_more1, "more1-contents"))

        first_more2 = path_utils.concat_path(self.first_repo, "more2.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_more2, "more2-contents"))

        first_more3 = path_utils.concat_path(self.first_repo, "more3.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_more3, "more3-contents"))

        first_more4 = path_utils.concat_path(self.first_repo, "more4.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_more4, "more4-contents"))

        first_more5 = path_utils.concat_path(self.first_repo, "アーカイブ.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_more5, "アーカイブ-contents"))

        first_more6 = path_utils.concat_path(self.first_repo, "more6.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, path_utils.basename_filtered(first_more6), "more6-content6", "commit_msg_more6")
        self.assertTrue(v)

        first_more7 = path_utils.concat_path(self.first_repo, "more7.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, path_utils.basename_filtered(first_more7), "more7-content7", "commit_msg_more7")
        self.assertTrue(v)

        first_more8 = path_utils.concat_path(self.first_repo, "more8.txt")
        first_more8_renamed = path_utils.concat_path(self.first_repo, "more8_renamed.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, path_utils.basename_filtered(first_more8), "more8-content8", "commit_msg_more8")
        self.assertTrue(v)
        self.assertFalse(os.path.exists(first_more8_renamed))

        self.assertTrue(os.path.exists(first_more6))
        self.assertTrue(os.path.exists(first_more7))
        os.unlink(first_more6)
        os.unlink(first_more7)
        self.assertFalse(os.path.exists(first_more6))
        self.assertFalse(os.path.exists(first_more7))

        self.assertTrue(path_utils.copy_to_and_rename(first_more8, self.first_repo, path_utils.basename_filtered(first_more8_renamed)))
        os.unlink(first_more8)
        self.assertFalse(os.path.exists(first_more8))
        self.assertTrue(os.path.exists(first_more8_renamed))

        v, r = git_wrapper.stage(self.first_repo, [first_more1, first_more8, first_more8_renamed])
        self.assertTrue(v)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(r, [first_more1, first_more8_renamed])

        v, r = git_wrapper.stage(self.first_repo, [first_more2, first_more3, first_more6])
        self.assertTrue(v)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 5)
        self.assertTrue(first_more1 in r)
        self.assertTrue(first_more2 in r)
        self.assertTrue(first_more3 in r)
        self.assertTrue(first_more6 in r)
        self.assertFalse(first_more7 in r)
        self.assertTrue(first_more8_renamed in r)

        with open(self.first_file1, "a") as f:
            f.write("additional contents")

        v, r = git_wrapper.stage(self.first_repo, None)
        self.assertTrue(v)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)

        self.assertEqual(len(r), 9)
        self.assertTrue(self.first_file1 in r)
        self.assertTrue(first_more1 in r)
        self.assertTrue(first_more2 in r)
        self.assertTrue(first_more3 in r)
        self.assertTrue(first_more4 in r)
        #self.assertTrue(first_more5 in r) # mvtodo: might require extra system config or ...
        self.assertTrue(first_more6 in r)
        self.assertTrue(first_more7 in r)
        self.assertTrue(first_more8_renamed in r)

    def testGetStagedFilesRelativePath(self):

        sub1 = path_utils.concat_path(self.test_dir, "sub1")
        self.assertFalse(os.path.exists(sub1))
        os.mkdir(sub1)
        self.assertTrue(os.path.exists(sub1))

        sub1_testrepo = path_utils.concat_path(sub1, "testrepo")
        v, r = git_wrapper.init(sub1, "testrepo", False)
        self.assertTrue(v)
        self.assertTrue(os.path.exists(sub1_testrepo))

        testrepo_file1 = path_utils.concat_path(sub1_testrepo, "file1.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file1), "file1-content1", "commit_msg_file1")
        self.assertTrue(v)

        testrepo_file2 = path_utils.concat_path(sub1_testrepo, "file2.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file2), "file2-content1", "commit_msg_file2")
        self.assertTrue(v)

        testrepo_file3 = path_utils.concat_path(sub1_testrepo, "file3.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file3), "file3-content1", "commit_msg_file3")
        self.assertTrue(v)

        sub1_testrepo_sub2 = path_utils.concat_path(sub1_testrepo, "sub2")
        os.mkdir(sub1_testrepo_sub2)
        sub1_testrepo_sub3 = path_utils.concat_path(sub1_testrepo, "sub3")
        os.symlink(sub1_testrepo_sub2, sub1_testrepo_sub3)

        sub1_testrepo_sub2_file4 = path_utils.concat_path(sub1_testrepo_sub2, "file4.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo_sub2, path_utils.basename_filtered(sub1_testrepo_sub2_file4), "file4-content1", "commit_msg_file4")
        self.assertTrue(v)
        sub1_testrepo_sub3_file4 = path_utils.concat_path(sub1_testrepo_sub3, "file4.txt")

        self.assertTrue(os.path.exists(sub1_testrepo_sub2_file4))
        self.assertTrue(os.path.exists(sub1_testrepo_sub3_file4))

        with open(testrepo_file1, "a") as f:
            f.write("additional content f1")

        with open(testrepo_file3, "a") as f:
            f.write("additional content f3")

        with open(sub1_testrepo_sub3_file4, "a") as f:
            f.write("additional content f4")

        v, r = git_wrapper.stage(sub1_testrepo)
        self.assertTrue(v)

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            v, r = git_lib.get_staged_files("./sub1/testrepo")
            self.assertTrue(v)
            self.assertTrue(testrepo_file1 in r)
            self.assertFalse(testrepo_file2 in r)
            self.assertTrue(testrepo_file3 in r)
            self.assertTrue(sub1_testrepo_sub2_file4 in r)
            self.assertFalse(sub1_testrepo_sub3_file4 in r) # git resolves symlinks
        finally:
            os.chdir(saved_wd)

    def testGetStagedFilesRelativePathSymlinkRepo(self):

        sub2 = path_utils.concat_path(self.test_dir, "sub2")
        self.assertFalse(os.path.exists(sub2))
        os.mkdir(sub2)
        self.assertTrue(os.path.exists(sub2))

        sub1 = path_utils.concat_path(self.test_dir, "sub1")
        self.assertFalse(os.path.exists(sub1))
        os.symlink(sub2, sub1)
        self.assertTrue(os.path.exists(sub1))

        sub1_testrepo = path_utils.concat_path(sub1, "testrepo")
        v, r = git_wrapper.init(sub1, "testrepo", False)
        self.assertTrue(v)
        self.assertTrue(os.path.exists(sub1_testrepo))

        testrepo_file1 = path_utils.concat_path(sub1_testrepo, "file1.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file1), "file1-content1", "commit_msg_file1")
        self.assertTrue(v)

        testrepo_file2 = path_utils.concat_path(sub1_testrepo, "file2.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file2), "file2-content1", "commit_msg_file2")
        self.assertTrue(v)

        testrepo_file3 = path_utils.concat_path(sub1_testrepo, "file3.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file3), "file3-content1", "commit_msg_file3")
        self.assertTrue(v)

        sub1_testrepo_sub2 = path_utils.concat_path(sub1_testrepo, "sub2")
        os.mkdir(sub1_testrepo_sub2)
        sub1_testrepo_sub3 = path_utils.concat_path(sub1_testrepo, "sub3")
        os.symlink(sub1_testrepo_sub2, sub1_testrepo_sub3)

        sub1_testrepo_sub2_file4 = path_utils.concat_path(sub1_testrepo_sub2, "file4.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo_sub2, path_utils.basename_filtered(sub1_testrepo_sub2_file4), "file4-content1", "commit_msg_file4")
        self.assertTrue(v)
        sub1_testrepo_sub3_file4 = path_utils.concat_path(sub1_testrepo_sub3, "file4.txt")

        self.assertTrue(os.path.exists(sub1_testrepo_sub2_file4))
        self.assertTrue(os.path.exists(sub1_testrepo_sub3_file4))

        with open(testrepo_file1, "a") as f:
            f.write("additional content f1")

        with open(testrepo_file3, "a") as f:
            f.write("additional content f3")

        with open(sub1_testrepo_sub3_file4, "a") as f:
            f.write("additional content f4")

        v, r = git_wrapper.stage(sub1_testrepo)
        self.assertTrue(v)

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            v, r = git_lib.get_staged_files("./sub1/testrepo")
            self.assertTrue(v)
            self.assertTrue(testrepo_file1 in r)
            self.assertFalse(testrepo_file2 in r)
            self.assertTrue(testrepo_file3 in r)
            self.assertTrue(sub1_testrepo_sub2_file4 in r)
            self.assertFalse(sub1_testrepo_sub3_file4 in r) # git resolves symlinks
        finally:
            os.chdir(saved_wd)

    def testGetStagedDeletedFiles(self):

        v, r = git_lib.get_staged_deleted_files(self.fourth_notrepo)
        self.assertFalse(v)

        v, r = git_lib.get_staged_deleted_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(r, [])

        first_more1 = path_utils.concat_path(self.first_repo, "more1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_more1, "more1-contents"))

        first_more2 = path_utils.concat_path(self.first_repo, "more2.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_more2, "more2-contents"))

        first_more3 = path_utils.concat_path(self.first_repo, "more3.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_more3, "more3-contents"))

        first_more4 = path_utils.concat_path(self.first_repo, "more4.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_more4, "more4-contents"))

        first_more5 = path_utils.concat_path(self.first_repo, "アーカイブ.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_more5, "アーカイブ-contents"))

        first_more6 = path_utils.concat_path(self.first_repo, "more6.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, path_utils.basename_filtered(first_more6), "more6-content6", "commit_msg_more6")
        self.assertTrue(v)

        first_more7 = path_utils.concat_path(self.first_repo, "more7.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, path_utils.basename_filtered(first_more7), "more7-content7", "commit_msg_more7")
        self.assertTrue(v)

        self.assertTrue(os.path.exists(first_more6))
        self.assertTrue(os.path.exists(first_more7))
        os.unlink(first_more6)
        os.unlink(first_more7)
        self.assertFalse(os.path.exists(first_more6))
        self.assertFalse(os.path.exists(first_more7))

        v, r = git_wrapper.stage(self.first_repo, [first_more6])
        self.assertTrue(v)

        v, r = git_lib.get_staged_deleted_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(r, [first_more6])

        with open(first_more2, "a") as f:
            f.write("yet more contents")

        v, r = git_wrapper.stage(self.first_repo, [first_more7, first_more2])
        self.assertTrue(v)

        v, r = git_lib.get_staged_deleted_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertFalse(first_more1 in r)
        self.assertFalse(first_more2 in r)
        self.assertFalse(first_more3 in r)
        self.assertFalse(first_more4 in r)
        self.assertTrue(first_more6 in r)
        self.assertTrue(first_more7 in r)

    def testGetStagedDeletedFilesRelativePath(self):

        sub1 = path_utils.concat_path(self.test_dir, "sub1")
        self.assertFalse(os.path.exists(sub1))
        os.mkdir(sub1)
        self.assertTrue(os.path.exists(sub1))

        sub1_testrepo = path_utils.concat_path(sub1, "testrepo")
        v, r = git_wrapper.init(sub1, "testrepo", False)
        self.assertTrue(v)
        self.assertTrue(os.path.exists(sub1_testrepo))

        testrepo_file1 = path_utils.concat_path(sub1_testrepo, "file1.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file1), "file1-content1", "commit_msg_file1")
        self.assertTrue(v)

        testrepo_file2 = path_utils.concat_path(sub1_testrepo, "file2.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file2), "file2-content1", "commit_msg_file2")
        self.assertTrue(v)

        testrepo_file3 = path_utils.concat_path(sub1_testrepo, "file3.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file3), "file3-content1", "commit_msg_file3")
        self.assertTrue(v)

        sub1_testrepo_sub2 = path_utils.concat_path(sub1_testrepo, "sub2")
        os.mkdir(sub1_testrepo_sub2)
        sub1_testrepo_sub3 = path_utils.concat_path(sub1_testrepo, "sub3")
        os.symlink(sub1_testrepo_sub2, sub1_testrepo_sub3)

        sub1_testrepo_sub2_file4 = path_utils.concat_path(sub1_testrepo_sub2, "file4.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo_sub2, path_utils.basename_filtered(sub1_testrepo_sub2_file4), "file4-content1", "commit_msg_file4")
        self.assertTrue(v)
        sub1_testrepo_sub3_file4 = path_utils.concat_path(sub1_testrepo_sub3, "file4.txt")

        self.assertTrue(os.path.exists(sub1_testrepo_sub2_file4))
        self.assertTrue(os.path.exists(sub1_testrepo_sub3_file4))

        os.unlink(testrepo_file1)
        os.unlink(testrepo_file3)
        os.unlink(sub1_testrepo_sub2_file4)

        v, r = git_wrapper.stage(sub1_testrepo)
        self.assertTrue(v)

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            v, r = git_lib.get_staged_deleted_files("./sub1/testrepo")
            self.assertTrue(v)
            self.assertTrue(testrepo_file1 in r)
            self.assertFalse(testrepo_file2 in r)
            self.assertTrue(testrepo_file3 in r)
            self.assertTrue(sub1_testrepo_sub2_file4 in r)
            self.assertFalse(sub1_testrepo_sub3_file4 in r) # git resolves symlinks
        finally:
            os.chdir(saved_wd)

    def testGetStagedDeletedFilesRelativePathSymlinkRepo(self):

        sub2 = path_utils.concat_path(self.test_dir, "sub2")
        self.assertFalse(os.path.exists(sub2))
        os.mkdir(sub2)
        self.assertTrue(os.path.exists(sub2))

        sub1 = path_utils.concat_path(self.test_dir, "sub1")
        self.assertFalse(os.path.exists(sub1))
        os.symlink(sub2, sub1)
        self.assertTrue(os.path.exists(sub1))

        sub1_testrepo = path_utils.concat_path(sub1, "testrepo")
        v, r = git_wrapper.init(sub1, "testrepo", False)
        self.assertTrue(v)
        self.assertTrue(os.path.exists(sub1_testrepo))

        testrepo_file1 = path_utils.concat_path(sub1_testrepo, "file1.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file1), "file1-content1", "commit_msg_file1")
        self.assertTrue(v)

        testrepo_file2 = path_utils.concat_path(sub1_testrepo, "file2.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file2), "file2-content1", "commit_msg_file2")
        self.assertTrue(v)

        testrepo_file3 = path_utils.concat_path(sub1_testrepo, "file3.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file3), "file3-content1", "commit_msg_file3")
        self.assertTrue(v)

        sub1_testrepo_sub2 = path_utils.concat_path(sub1_testrepo, "sub2")
        os.mkdir(sub1_testrepo_sub2)
        sub1_testrepo_sub3 = path_utils.concat_path(sub1_testrepo, "sub3")
        os.symlink(sub1_testrepo_sub2, sub1_testrepo_sub3)

        sub1_testrepo_sub2_file4 = path_utils.concat_path(sub1_testrepo_sub2, "file4.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo_sub2, path_utils.basename_filtered(sub1_testrepo_sub2_file4), "file4-content1", "commit_msg_file4")
        self.assertTrue(v)
        sub1_testrepo_sub3_file4 = path_utils.concat_path(sub1_testrepo_sub3, "file4.txt")

        self.assertTrue(os.path.exists(sub1_testrepo_sub2_file4))
        self.assertTrue(os.path.exists(sub1_testrepo_sub3_file4))

        os.unlink(testrepo_file1)
        os.unlink(testrepo_file3)
        os.unlink(sub1_testrepo_sub3_file4)

        v, r = git_wrapper.stage(sub1_testrepo)
        self.assertTrue(v)

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            v, r = git_lib.get_staged_deleted_files("./sub1/testrepo")
            self.assertTrue(v)
            self.assertTrue(testrepo_file1 in r)
            self.assertFalse(testrepo_file2 in r)
            self.assertTrue(testrepo_file3 in r)
            self.assertTrue(sub1_testrepo_sub2_file4 in r)
            self.assertFalse(sub1_testrepo_sub3_file4 in r) # git resolves symlinks
        finally:
            os.chdir(saved_wd)

    def testGetStagedModifiedFiles(self):

        v, r = git_lib.get_staged_modified_files(self.fourth_notrepo)
        self.assertFalse(v)

        v, r = git_lib.get_staged_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(r, [])

        first_more1 = path_utils.concat_path(self.first_repo, "more1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_more1, "more1-contents"))

        first_more2 = path_utils.concat_path(self.first_repo, "more2.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_more2, "more2-contents"))

        first_more3 = path_utils.concat_path(self.first_repo, "more3.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_more3, "more3-contents"))

        first_more4 = path_utils.concat_path(self.first_repo, "more4.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_more4, "more4-contents"))

        first_more5 = path_utils.concat_path(self.first_repo, "アーカイブ.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_more5, "アーカイブ-contents"))

        first_more6 = path_utils.concat_path(self.first_repo, "more6.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, path_utils.basename_filtered(first_more6), "more6-content6", "commit_msg_more6")
        self.assertTrue(v)

        first_more7 = path_utils.concat_path(self.first_repo, "more7.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, path_utils.basename_filtered(first_more7), "more7-content7", "commit_msg_more7")
        self.assertTrue(v)

        v, r = git_lib.get_staged_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        self.assertTrue(os.path.exists(first_more6))
        self.assertTrue(os.path.exists(first_more7))
        os.unlink(first_more6)
        os.unlink(first_more7)
        self.assertFalse(os.path.exists(first_more6))
        self.assertFalse(os.path.exists(first_more7))

        with open(first_more2, "a") as f:
            f.write("yet more contents")

        with open(first_more5, "a") as f:
            f.write("yet more contents")

        with open(self.first_file1, "a") as f:
            f.write("adding stuff")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_staged_modified_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertTrue(self.first_file1 in r)
        self.assertFalse(first_more1 in r)
        self.assertFalse(first_more2 in r)
        self.assertFalse(first_more3 in r)
        self.assertFalse(first_more4 in r)
        self.assertFalse(first_more6 in r)
        self.assertFalse(first_more7 in r)

    def testGetStagedModifiedFilesRelativePath(self):

        sub1 = path_utils.concat_path(self.test_dir, "sub1")
        self.assertFalse(os.path.exists(sub1))
        os.mkdir(sub1)
        self.assertTrue(os.path.exists(sub1))

        sub1_testrepo = path_utils.concat_path(sub1, "testrepo")
        v, r = git_wrapper.init(sub1, "testrepo", False)
        self.assertTrue(v)
        self.assertTrue(os.path.exists(sub1_testrepo))

        testrepo_file1 = path_utils.concat_path(sub1_testrepo, "file1.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file1), "file1-content1", "commit_msg_file1")
        self.assertTrue(v)

        testrepo_file2 = path_utils.concat_path(sub1_testrepo, "file2.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file2), "file2-content1", "commit_msg_file2")
        self.assertTrue(v)

        testrepo_file3 = path_utils.concat_path(sub1_testrepo, "file3.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file3), "file3-content1", "commit_msg_file3")
        self.assertTrue(v)

        sub1_testrepo_sub2 = path_utils.concat_path(sub1_testrepo, "sub2")
        os.mkdir(sub1_testrepo_sub2)
        sub1_testrepo_sub3 = path_utils.concat_path(sub1_testrepo, "sub3")
        os.symlink(sub1_testrepo_sub2, sub1_testrepo_sub3)

        sub1_testrepo_sub2_file4 = path_utils.concat_path(sub1_testrepo_sub2, "file4.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo_sub2, path_utils.basename_filtered(sub1_testrepo_sub2_file4), "file4-content1", "commit_msg_file4")
        self.assertTrue(v)
        sub1_testrepo_sub3_file4 = path_utils.concat_path(sub1_testrepo_sub3, "file4.txt")

        self.assertTrue(os.path.exists(sub1_testrepo_sub2_file4))
        self.assertTrue(os.path.exists(sub1_testrepo_sub3_file4))

        os.unlink(testrepo_file1)
        os.unlink(testrepo_file3)

        with open(sub1_testrepo_sub2_file4, "a") as f:
            f.write("extra unexpected info")

        v, r = git_wrapper.stage(sub1_testrepo)
        self.assertTrue(v)

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            v, r = git_lib.get_staged_modified_files("./sub1/testrepo")
            self.assertTrue(v)
            self.assertFalse(testrepo_file1 in r)
            self.assertFalse(testrepo_file2 in r)
            self.assertFalse(testrepo_file3 in r)
            self.assertTrue(sub1_testrepo_sub2_file4 in r)
            self.assertFalse(sub1_testrepo_sub3_file4 in r) # git resolves symlinks
        finally:
            os.chdir(saved_wd)

    def testGetStagedModifiedFilesRelativePathSymlinkRepo(self):

        sub2 = path_utils.concat_path(self.test_dir, "sub2")
        self.assertFalse(os.path.exists(sub2))
        os.mkdir(sub2)
        self.assertTrue(os.path.exists(sub2))

        sub1 = path_utils.concat_path(self.test_dir, "sub1")
        self.assertFalse(os.path.exists(sub1))
        os.symlink(sub2, sub1)
        self.assertTrue(os.path.exists(sub1))

        sub1_testrepo = path_utils.concat_path(sub1, "testrepo")
        v, r = git_wrapper.init(sub1, "testrepo", False)
        self.assertTrue(v)
        self.assertTrue(os.path.exists(sub1_testrepo))

        testrepo_file1 = path_utils.concat_path(sub1_testrepo, "file1.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file1), "file1-content1", "commit_msg_file1")
        self.assertTrue(v)

        testrepo_file2 = path_utils.concat_path(sub1_testrepo, "file2.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file2), "file2-content1", "commit_msg_file2")
        self.assertTrue(v)

        testrepo_file3 = path_utils.concat_path(sub1_testrepo, "file3.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file3), "file3-content1", "commit_msg_file3")
        self.assertTrue(v)

        sub1_testrepo_sub2 = path_utils.concat_path(sub1_testrepo, "sub2")
        os.mkdir(sub1_testrepo_sub2)
        sub1_testrepo_sub3 = path_utils.concat_path(sub1_testrepo, "sub3")
        os.symlink(sub1_testrepo_sub2, sub1_testrepo_sub3)

        sub1_testrepo_sub2_file4 = path_utils.concat_path(sub1_testrepo_sub2, "file4.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo_sub2, path_utils.basename_filtered(sub1_testrepo_sub2_file4), "file4-content1", "commit_msg_file4")
        self.assertTrue(v)
        sub1_testrepo_sub3_file4 = path_utils.concat_path(sub1_testrepo_sub3, "file4.txt")

        self.assertTrue(os.path.exists(sub1_testrepo_sub2_file4))
        self.assertTrue(os.path.exists(sub1_testrepo_sub3_file4))

        os.unlink(testrepo_file1)
        os.unlink(testrepo_file3)
        with open(sub1_testrepo_sub3_file4, "a") as f:
            f.write("more onto the file")

        v, r = git_wrapper.stage(sub1_testrepo)
        self.assertTrue(v)

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            v, r = git_lib.get_staged_modified_files("./sub1/testrepo")
            self.assertTrue(v)
            self.assertFalse(testrepo_file1 in r)
            self.assertFalse(testrepo_file2 in r)
            self.assertFalse(testrepo_file3 in r)
            self.assertTrue(sub1_testrepo_sub2_file4 in r)
            self.assertFalse(sub1_testrepo_sub3_file4 in r) # git resolves symlinks
        finally:
            os.chdir(saved_wd)

    def testGetStagedAddedFiles(self):

        v, r = git_lib.get_staged_added_files(self.fourth_notrepo)
        self.assertFalse(v)

        v, r = git_lib.get_staged_added_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(r, [])

        first_more1 = path_utils.concat_path(self.first_repo, "more1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_more1, "more1-contents"))

        first_more2 = path_utils.concat_path(self.first_repo, "more2.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_more2, "more2-contents"))

        first_more3 = path_utils.concat_path(self.first_repo, "more3.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_more3, "more3-contents"))

        first_more4 = path_utils.concat_path(self.first_repo, "more4.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_more4, "more4-contents"))

        first_more5 = path_utils.concat_path(self.first_repo, "アーカイブ.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_more5, "アーカイブ-contents"))

        first_more6 = path_utils.concat_path(self.first_repo, "more6.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, path_utils.basename_filtered(first_more6), "more6-content6", "commit_msg_more6")
        self.assertTrue(v)

        first_more7 = path_utils.concat_path(self.first_repo, "more7.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, path_utils.basename_filtered(first_more7), "more7-content7", "commit_msg_more7")
        self.assertTrue(v)

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.first_repo, "commitmsg")
        self.assertTrue(v)

        v, r = git_lib.get_staged_added_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        self.assertTrue(os.path.exists(first_more6))
        self.assertTrue(os.path.exists(first_more7))
        os.unlink(first_more6)
        os.unlink(first_more7)
        self.assertFalse(os.path.exists(first_more6))
        self.assertFalse(os.path.exists(first_more7))

        with open(first_more2, "a") as f:
            f.write("yet more contents")

        with open(first_more5, "a") as f:
            f.write("yet more contents")

        with open(self.first_file1, "a") as f:
            f.write("adding stuff")

        first_more8 = path_utils.concat_path(self.first_repo, "more8.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_more8, "more8-contents"))

        first_more88 = path_utils.concat_path(self.first_repo, "more88.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_more88, "more88-contents"))

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_staged_added_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertFalse(self.first_file1 in r)
        self.assertFalse(first_more1 in r)
        self.assertFalse(first_more2 in r)
        self.assertFalse(first_more3 in r)
        self.assertFalse(first_more4 in r)
        self.assertFalse(first_more6 in r)
        self.assertFalse(first_more7 in r)
        self.assertTrue(first_more8 in r)
        self.assertTrue(first_more88 in r)

    def testGetStagedAddedFilesRelativePath(self):

        sub1 = path_utils.concat_path(self.test_dir, "sub1")
        self.assertFalse(os.path.exists(sub1))
        os.mkdir(sub1)
        self.assertTrue(os.path.exists(sub1))

        sub1_testrepo = path_utils.concat_path(sub1, "testrepo")
        v, r = git_wrapper.init(sub1, "testrepo", False)
        self.assertTrue(v)
        self.assertTrue(os.path.exists(sub1_testrepo))

        testrepo_file1 = path_utils.concat_path(sub1_testrepo, "file1.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file1), "file1-content1", "commit_msg_file1")
        self.assertTrue(v)

        testrepo_file2 = path_utils.concat_path(sub1_testrepo, "file2.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file2), "file2-content1", "commit_msg_file2")
        self.assertTrue(v)

        testrepo_file3 = path_utils.concat_path(sub1_testrepo, "file3.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file3), "file3-content1", "commit_msg_file3")
        self.assertTrue(v)

        sub1_testrepo_sub2 = path_utils.concat_path(sub1_testrepo, "sub2")
        os.mkdir(sub1_testrepo_sub2)
        sub1_testrepo_sub3 = path_utils.concat_path(sub1_testrepo, "sub3")
        os.symlink(sub1_testrepo_sub2, sub1_testrepo_sub3)

        sub1_testrepo_sub2_file4 = path_utils.concat_path(sub1_testrepo_sub2, "file4.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo_sub2, path_utils.basename_filtered(sub1_testrepo_sub2_file4), "file4-content1", "commit_msg_file4")
        self.assertTrue(v)
        sub1_testrepo_sub3_file4 = path_utils.concat_path(sub1_testrepo_sub3, "file4.txt")

        v, r = git_wrapper.stage(sub1_testrepo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(sub1_testrepo, "commitmsg")
        self.assertTrue(v)

        v, r = git_lib.get_staged_added_files(sub1_testrepo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        self.assertTrue(os.path.exists(sub1_testrepo_sub2_file4))
        self.assertTrue(os.path.exists(sub1_testrepo_sub3_file4))
        os.unlink(testrepo_file1)
        os.unlink(testrepo_file3)

        with open(sub1_testrepo_sub2_file4, "a") as f:
            f.write("extra unexpected info")

        sub1_testrepo_sub2_file8 = path_utils.concat_path(sub1_testrepo_sub2, "file8.txt")
        self.assertTrue(create_and_write_file.create_file_contents(sub1_testrepo_sub2_file8, "file8-contents"))
        sub1_testrepo_sub3_file8 = path_utils.concat_path(sub1_testrepo_sub3, "file8.txt")

        v, r = git_wrapper.stage(sub1_testrepo, [sub1_testrepo_sub3_file8])
        self.assertFalse(v) # cant add symlinks

        v, r = git_wrapper.stage(sub1_testrepo, [sub1_testrepo_sub2_file8])
        self.assertTrue(v) # cant add symlinks

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            v, r = git_lib.get_staged_added_files("./sub1/testrepo")
            self.assertTrue(v)
            self.assertFalse(testrepo_file1 in r)
            self.assertFalse(testrepo_file2 in r)
            self.assertFalse(testrepo_file3 in r)
            self.assertFalse(sub1_testrepo_sub2_file4 in r)
            self.assertFalse(sub1_testrepo_sub3_file4 in r) # git resolves symlinks
            self.assertTrue(sub1_testrepo_sub2_file8 in r)
            self.assertFalse(sub1_testrepo_sub3_file8 in r) # git resolves symlinks
        finally:
            os.chdir(saved_wd)

    def testGetStagedAddedFilesRelativePathSymlinkRepo(self):

        sub2 = path_utils.concat_path(self.test_dir, "sub2")
        self.assertFalse(os.path.exists(sub2))
        os.mkdir(sub2)
        self.assertTrue(os.path.exists(sub2))

        sub1 = path_utils.concat_path(self.test_dir, "sub1")
        self.assertFalse(os.path.exists(sub1))
        os.symlink(sub2, sub1)
        self.assertTrue(os.path.exists(sub1))

        sub1_testrepo = path_utils.concat_path(sub1, "testrepo")
        v, r = git_wrapper.init(sub1, "testrepo", False)
        self.assertTrue(v)
        self.assertTrue(os.path.exists(sub1_testrepo))

        testrepo_file1 = path_utils.concat_path(sub1_testrepo, "file1.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file1), "file1-content1", "commit_msg_file1")
        self.assertTrue(v)

        testrepo_file2 = path_utils.concat_path(sub1_testrepo, "file2.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file2), "file2-content1", "commit_msg_file2")
        self.assertTrue(v)

        testrepo_file3 = path_utils.concat_path(sub1_testrepo, "file3.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file3), "file3-content1", "commit_msg_file3")
        self.assertTrue(v)

        sub1_testrepo_sub2 = path_utils.concat_path(sub1_testrepo, "sub2")
        os.mkdir(sub1_testrepo_sub2)
        sub1_testrepo_sub3 = path_utils.concat_path(sub1_testrepo, "sub3")
        os.symlink(sub1_testrepo_sub2, sub1_testrepo_sub3)

        sub1_testrepo_sub2_file4 = path_utils.concat_path(sub1_testrepo_sub2, "file4.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo_sub2, path_utils.basename_filtered(sub1_testrepo_sub2_file4), "file4-content1", "commit_msg_file4")
        self.assertTrue(v)
        sub1_testrepo_sub3_file4 = path_utils.concat_path(sub1_testrepo_sub3, "file4.txt")

        self.assertTrue(os.path.exists(sub1_testrepo_sub2_file4))
        self.assertTrue(os.path.exists(sub1_testrepo_sub3_file4))

        os.unlink(testrepo_file1)
        os.unlink(testrepo_file3)
        with open(sub1_testrepo_sub3_file4, "a") as f:
            f.write("more onto the file")

        sub1_testrepo_sub2_file8 = path_utils.concat_path(sub1_testrepo_sub2, "file8.txt")
        self.assertTrue(create_and_write_file.create_file_contents(sub1_testrepo_sub2_file8, "file8-contents"))
        sub1_testrepo_sub3_file8 = path_utils.concat_path(sub1_testrepo_sub3, "file8.txt")

        sub1_testrepo_sub2_file9 = path_utils.concat_path(sub1_testrepo_sub2, "file9.txt")
        self.assertTrue(create_and_write_file.create_file_contents(sub1_testrepo_sub2_file9, "file9-contents"))
        sub1_testrepo_sub3_file9 = path_utils.concat_path(sub1_testrepo_sub3, "file9.txt")

        v, r = git_wrapper.stage(sub1_testrepo)
        self.assertTrue(v)

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            v, r = git_lib.get_staged_added_files("./sub1/testrepo")
            self.assertTrue(v)
            self.assertFalse(testrepo_file1 in r)
            self.assertFalse(testrepo_file2 in r)
            self.assertFalse(testrepo_file3 in r)
            self.assertFalse(sub1_testrepo_sub2_file4 in r)
            self.assertFalse(sub1_testrepo_sub3_file4 in r) # git resolves symlinks
            self.assertTrue(sub1_testrepo_sub2_file8 in r)
            self.assertFalse(sub1_testrepo_sub3_file8 in r) # git resolves symlinks
            self.assertTrue(sub1_testrepo_sub2_file9 in r)
            self.assertFalse(sub1_testrepo_sub3_file9 in r) # git resolves symlinks
        finally:
            os.chdir(saved_wd)

    def testGetStagedRenamedFiles(self):

        v, r = git_lib.get_staged_renamed_files(self.fourth_notrepo)
        self.assertFalse(v)

        v, r = git_lib.get_staged_renamed_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(r, [])

        first_more1 = path_utils.concat_path(self.first_repo, "more1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_more1, "more1-contents"))

        first_more2 = path_utils.concat_path(self.first_repo, "more2.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_more2, "more2-contents"))

        first_more3 = path_utils.concat_path(self.first_repo, "more3.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_more3, "more3-contents"))

        first_more4 = path_utils.concat_path(self.first_repo, "more4.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_more4, "more4-contents"))

        first_more5 = path_utils.concat_path(self.first_repo, "アーカイブ.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_more5, "アーカイブ-contents"))

        first_more6 = path_utils.concat_path(self.first_repo, "more6.txt")
        first_more6_renamed = path_utils.concat_path(self.first_repo, "more6_renamed.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, path_utils.basename_filtered(first_more6), "more6-content6", "commit_msg_more6")
        self.assertTrue(v)
        self.assertFalse(os.path.exists(first_more6_renamed))

        first_more7 = path_utils.concat_path(self.first_repo, "more7.txt")
        first_more7_renamed = path_utils.concat_path(self.first_repo, "more7_renamed.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, path_utils.basename_filtered(first_more7), "more7-content7", "commit_msg_more7")
        self.assertTrue(v)
        self.assertFalse(os.path.exists(first_more7_renamed))

        self.assertTrue(os.path.exists(first_more6))
        self.assertTrue(os.path.exists(first_more7))
        self.assertTrue(path_utils.copy_to_and_rename(first_more6, self.first_repo, path_utils.basename_filtered(first_more6_renamed)))
        self.assertTrue(path_utils.copy_to_and_rename(first_more7, self.first_repo, path_utils.basename_filtered(first_more7_renamed)))
        os.unlink(first_more6)
        os.unlink(first_more7)
        self.assertFalse(os.path.exists(first_more6))
        self.assertFalse(os.path.exists(first_more7))
        self.assertTrue(os.path.exists(first_more6_renamed))
        self.assertTrue(os.path.exists(first_more7_renamed))

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_staged_renamed_files(self.first_repo)
        self.assertTrue(v)
        self.assertTrue(any(first_more6 in s for s in r))
        self.assertTrue(any(first_more6_renamed in s for s in r))
        self.assertTrue(any(first_more7 in s for s in r))
        self.assertTrue(any(first_more7_renamed in s for s in r))
        for x in r:
            self.assertTrue(os.path.exists(x[1]))

    def testGetStagedRenamedFilesRelativePath(self):

        sub1 = path_utils.concat_path(self.test_dir, "sub1")
        self.assertFalse(os.path.exists(sub1))
        os.mkdir(sub1)
        self.assertTrue(os.path.exists(sub1))

        sub1_testrepo = path_utils.concat_path(sub1, "testrepo")
        v, r = git_wrapper.init(sub1, "testrepo", False)
        self.assertTrue(v)
        self.assertTrue(os.path.exists(sub1_testrepo))

        testrepo_file1 = path_utils.concat_path(sub1_testrepo, "file1.txt")
        testrepo_file1_renamed = path_utils.concat_path(sub1_testrepo, "file1_renamed.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file1), "file1-content1", "commit_msg_file1")
        self.assertTrue(v)
        self.assertFalse(os.path.exists(testrepo_file1_renamed))

        testrepo_file2 = path_utils.concat_path(sub1_testrepo, "file2.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file2), "file2-content1", "commit_msg_file2")
        self.assertTrue(v)

        testrepo_file3 = path_utils.concat_path(sub1_testrepo, "file3.txt")
        testrepo_file3_renamed = path_utils.concat_path(sub1_testrepo, "file3_renamed.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file3), "file3-content1", "commit_msg_file3")
        self.assertTrue(v)
        self.assertFalse(os.path.exists(testrepo_file3_renamed))

        sub1_testrepo_sub2 = path_utils.concat_path(sub1_testrepo, "sub2")
        os.mkdir(sub1_testrepo_sub2)
        sub1_testrepo_sub3 = path_utils.concat_path(sub1_testrepo, "sub3")
        os.symlink(sub1_testrepo_sub2, sub1_testrepo_sub3)

        sub1_testrepo_sub2_file4 = path_utils.concat_path(sub1_testrepo_sub2, "file4.txt")
        sub1_testrepo_sub2_file4_renamed = path_utils.concat_path(sub1_testrepo_sub2, "file4_renamed.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo_sub2, path_utils.basename_filtered(sub1_testrepo_sub2_file4), "file4-content1", "commit_msg_file4")
        self.assertTrue(v)
        self.assertFalse(os.path.exists(sub1_testrepo_sub2_file4_renamed))
        sub1_testrepo_sub3_file4 = path_utils.concat_path(sub1_testrepo_sub3, "file4.txt")
        sub1_testrepo_sub3_file4_renamed = path_utils.concat_path(sub1_testrepo_sub3, "file4_renamed.txt")
        self.assertFalse(os.path.exists(sub1_testrepo_sub3_file4_renamed))

        self.assertTrue(os.path.exists(sub1_testrepo_sub2_file4))
        self.assertTrue(os.path.exists(sub1_testrepo_sub3_file4))

        self.assertTrue(path_utils.copy_to_and_rename(testrepo_file1, path_utils.dirname_filtered(testrepo_file1), path_utils.basename_filtered(testrepo_file1_renamed)))
        self.assertTrue(path_utils.copy_to_and_rename(testrepo_file3, path_utils.dirname_filtered(testrepo_file3), path_utils.basename_filtered(testrepo_file3_renamed)))
        self.assertTrue(path_utils.copy_to_and_rename(sub1_testrepo_sub2_file4, path_utils.dirname_filtered(sub1_testrepo_sub2_file4), path_utils.basename_filtered(sub1_testrepo_sub2_file4_renamed)))

        os.unlink(testrepo_file1)
        os.unlink(testrepo_file3)
        os.unlink(sub1_testrepo_sub2_file4)

        v, r = git_wrapper.stage(sub1_testrepo)
        self.assertTrue(v)

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            v, r = git_lib.get_staged_renamed_files("./sub1/testrepo")
            self.assertTrue(v)
            self.assertTrue(any(testrepo_file1 in s for s in r))
            self.assertTrue(any(testrepo_file1_renamed in s for s in r))
            self.assertTrue(any(testrepo_file3 in s for s in r))
            self.assertTrue(any(testrepo_file3_renamed in s for s in r))
            self.assertTrue(any(sub1_testrepo_sub2_file4 in s for s in r))
            self.assertTrue(any(sub1_testrepo_sub2_file4_renamed in s for s in r))
            self.assertFalse(any(testrepo_file2 in s for s in r))
            for x in r:
                self.assertTrue(os.path.exists(x[1]))

        finally:
            os.chdir(saved_wd)

    def testGetStagedRenamedFilesRelativePathSymlinkRepo(self):

        sub2 = path_utils.concat_path(self.test_dir, "sub2")
        self.assertFalse(os.path.exists(sub2))
        os.mkdir(sub2)
        self.assertTrue(os.path.exists(sub2))

        sub1 = path_utils.concat_path(self.test_dir, "sub1")
        self.assertFalse(os.path.exists(sub1))
        os.symlink(sub2, sub1)
        self.assertTrue(os.path.exists(sub1))

        sub1_testrepo = path_utils.concat_path(sub1, "testrepo")
        v, r = git_wrapper.init(sub1, "testrepo", False)
        self.assertTrue(v)
        self.assertTrue(os.path.exists(sub1_testrepo))

        testrepo_file1 = path_utils.concat_path(sub1_testrepo, "file1.txt")
        testrepo_file1_renamed = path_utils.concat_path(sub1_testrepo, "file1_renamed.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file1), "file1-content1", "commit_msg_file1")
        self.assertTrue(v)
        self.assertFalse(os.path.exists(testrepo_file1_renamed))

        testrepo_file2 = path_utils.concat_path(sub1_testrepo, "file2.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file2), "file2-content1", "commit_msg_file2")
        self.assertTrue(v)

        testrepo_file3 = path_utils.concat_path(sub1_testrepo, "file3.txt")
        testrepo_file3_renamed = path_utils.concat_path(sub1_testrepo, "file3_renamed.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file3), "file3-content1", "commit_msg_file3")
        self.assertTrue(v)
        self.assertFalse(os.path.exists(testrepo_file3_renamed))

        sub1_testrepo_sub2 = path_utils.concat_path(sub1_testrepo, "sub2")
        os.mkdir(sub1_testrepo_sub2)
        sub1_testrepo_sub3 = path_utils.concat_path(sub1_testrepo, "sub3")
        os.symlink(sub1_testrepo_sub2, sub1_testrepo_sub3)

        sub1_testrepo_sub2_file4 = path_utils.concat_path(sub1_testrepo_sub2, "file4.txt")
        sub1_testrepo_sub2_file4_renamed = path_utils.concat_path(sub1_testrepo_sub2, "file4_renamed.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo_sub2, path_utils.basename_filtered(sub1_testrepo_sub2_file4), "file4-content1", "commit_msg_file4")
        self.assertTrue(v)
        self.assertFalse(os.path.exists(sub1_testrepo_sub2_file4_renamed))
        sub1_testrepo_sub3_file4 = path_utils.concat_path(sub1_testrepo_sub3, "file4.txt")
        sub1_testrepo_sub3_file4_renamed = path_utils.concat_path(sub1_testrepo_sub3, "file4_renamed.txt")
        self.assertFalse(os.path.exists(sub1_testrepo_sub3_file4_renamed))

        self.assertTrue(os.path.exists(sub1_testrepo_sub2_file4))
        self.assertTrue(os.path.exists(sub1_testrepo_sub3_file4))

        self.assertTrue(path_utils.copy_to_and_rename(testrepo_file1, path_utils.dirname_filtered(testrepo_file1), path_utils.basename_filtered(testrepo_file1_renamed)))
        self.assertTrue(path_utils.copy_to_and_rename(testrepo_file3, path_utils.dirname_filtered(testrepo_file3), path_utils.basename_filtered(testrepo_file3_renamed)))
        self.assertTrue(path_utils.copy_to_and_rename(sub1_testrepo_sub2_file4, path_utils.dirname_filtered(sub1_testrepo_sub2_file4), path_utils.basename_filtered(sub1_testrepo_sub2_file4_renamed)))

        os.unlink(testrepo_file1)
        os.unlink(testrepo_file3)
        os.unlink(sub1_testrepo_sub3_file4)

        v, r = git_wrapper.stage(sub1_testrepo)
        self.assertTrue(v)

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            v, r = git_lib.get_staged_renamed_files("./sub1/testrepo")
            self.assertTrue(v)
            self.assertTrue(any(testrepo_file1 in s for s in r))
            self.assertTrue(any(testrepo_file1_renamed in s for s in r))
            self.assertTrue(any(testrepo_file3 in s for s in r))
            self.assertTrue(any(testrepo_file3_renamed in s for s in r))
            self.assertTrue(any(sub1_testrepo_sub2_file4 in s for s in r))
            self.assertTrue(any(sub1_testrepo_sub2_file4_renamed in s for s in r))
            self.assertFalse(any(testrepo_file2 in s for s in r))
            for x in r:
                self.assertTrue(os.path.exists(x[1]))
        finally:
            os.chdir(saved_wd)

    def testGetUnversionedFiles(self):

        v, r = git_lib.get_unversioned_files(self.fourth_notrepo)
        self.assertFalse(v)

        v, r = git_lib.get_unversioned_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(r, [])

        first_zero1 = path_utils.concat_path(self.first_repo, " ") # filename consisting of a single char (space)
        self.assertTrue(create_and_write_file.create_file_contents(first_zero1, "zero1-contents"))
        first_more1 = path_utils.concat_path(self.first_repo, "more1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_more1, "more1-contents"))
        first_more2 = path_utils.concat_path(self.first_repo, "more2.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_more2, "more2-contents"))
        first_more3 = path_utils.concat_path(self.first_repo, "アーカイブ.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_more3, "more3-contents"))

        first_sub = path_utils.concat_path(self.first_repo, "subfolder")
        os.mkdir(first_sub)
        self.assertTrue(os.path.exists(first_sub))
        first_sub_more4 = path_utils.concat_path(first_sub, "more4.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_sub_more4, "more4-contents"))

        v, r = git_lib.get_unversioned_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 5)
        self.assertTrue(first_zero1 in r)
        self.assertTrue(first_more1 in r)
        self.assertTrue(first_more2 in r)
        #self.assertTrue(first_more3 in r) # mvtodo: might require extra system config or ...
        self.assertTrue(first_sub_more4 in r)

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_unversioned_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

    def testGetUnversionedFilesRelativePath(self):

        sub1 = path_utils.concat_path(self.test_dir, "sub1")
        self.assertFalse(os.path.exists(sub1))
        os.mkdir(sub1)
        self.assertTrue(os.path.exists(sub1))

        sub1_testrepo = path_utils.concat_path(sub1, "testrepo")
        v, r = git_wrapper.init(sub1, "testrepo", False)
        self.assertTrue(v)
        self.assertTrue(os.path.exists(sub1_testrepo))

        testrepo_file1 = path_utils.concat_path(sub1_testrepo, "file1.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file1), "file1-content1", "commit_msg_file1")
        self.assertTrue(v)

        v, r = git_wrapper.stage(sub1_testrepo)
        self.assertTrue(v)

        testrepo_file2 = path_utils.concat_path(sub1_testrepo, "file2.txt")
        self.assertTrue(create_and_write_file.create_file_contents(testrepo_file2, "file2-content1"))

        testrepo_file3 = path_utils.concat_path(sub1_testrepo, "file3.txt")
        self.assertTrue(create_and_write_file.create_file_contents(testrepo_file3, "file3-content1"))

        sub1_testrepo_sub2 = path_utils.concat_path(sub1_testrepo, "sub2")
        os.mkdir(sub1_testrepo_sub2)
        sub1_testrepo_sub3 = path_utils.concat_path(sub1_testrepo, "sub3")
        os.symlink(sub1_testrepo_sub2, sub1_testrepo_sub3)

        sub1_testrepo_sub2_file4 = path_utils.concat_path(sub1_testrepo_sub2, "file4.txt")
        self.assertTrue(create_and_write_file.create_file_contents(sub1_testrepo_sub2_file4, "file4-content1"))
        self.assertTrue(v)
        sub1_testrepo_sub3_file4 = path_utils.concat_path(sub1_testrepo_sub3, "file4.txt")

        self.assertTrue(os.path.exists(sub1_testrepo_sub2_file4))
        self.assertTrue(os.path.exists(sub1_testrepo_sub3_file4))

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            v, r = git_lib.get_unversioned_files("./sub1/testrepo")
            self.assertTrue(v)
            self.assertFalse(testrepo_file1 in r)
            self.assertTrue(testrepo_file2 in r)
            self.assertTrue(testrepo_file3 in r)
            self.assertTrue(sub1_testrepo_sub2_file4 in r)
            self.assertTrue(path_utils.dirname_filtered(sub1_testrepo_sub3_file4) in r) # git will return a single entry for a symlink that points to a folder
        finally:
            os.chdir(saved_wd)

    def testGetUnversionedFilesRelativePathSymlinkRepo(self):

        sub2 = path_utils.concat_path(self.test_dir, "sub2")
        self.assertFalse(os.path.exists(sub2))
        os.mkdir(sub2)
        self.assertTrue(os.path.exists(sub2))

        sub1 = path_utils.concat_path(self.test_dir, "sub1")
        self.assertFalse(os.path.exists(sub1))
        os.symlink(sub2, sub1)
        self.assertTrue(os.path.exists(sub1))

        sub1_testrepo = path_utils.concat_path(sub1, "testrepo")
        v, r = git_wrapper.init(sub1, "testrepo", False)
        self.assertTrue(v)
        self.assertTrue(os.path.exists(sub1_testrepo))

        testrepo_file1 = path_utils.concat_path(sub1_testrepo, "file1.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file1), "file1-content1", "commit_msg_file1")
        self.assertTrue(v)

        v, r = git_wrapper.stage(sub1_testrepo)
        self.assertTrue(v)

        testrepo_file2 = path_utils.concat_path(sub1_testrepo, "file2.txt")
        self.assertTrue(create_and_write_file.create_file_contents(testrepo_file2, "file2-content1"))

        testrepo_file3 = path_utils.concat_path(sub1_testrepo, "file3.txt")
        self.assertTrue(create_and_write_file.create_file_contents(testrepo_file3, "file3-content1"))

        sub1_testrepo_sub2 = path_utils.concat_path(sub1_testrepo, "sub2")
        os.mkdir(sub1_testrepo_sub2)
        sub1_testrepo_sub3 = path_utils.concat_path(sub1_testrepo, "sub3")
        os.symlink(sub1_testrepo_sub2, sub1_testrepo_sub3)

        sub1_testrepo_sub2_file4 = path_utils.concat_path(sub1_testrepo_sub2, "file4.txt")
        self.assertTrue(create_and_write_file.create_file_contents(sub1_testrepo_sub2_file4, "file4-content1"))
        self.assertTrue(v)
        sub1_testrepo_sub3_file4 = path_utils.concat_path(sub1_testrepo_sub3, "file4.txt")

        self.assertTrue(os.path.exists(sub1_testrepo_sub2_file4))
        self.assertTrue(os.path.exists(sub1_testrepo_sub3_file4))

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            v, r = git_lib.get_unversioned_files("./sub1/testrepo")
            self.assertTrue(v)
            self.assertFalse(testrepo_file1 in r)
            self.assertTrue(testrepo_file2 in r)
            self.assertTrue(testrepo_file3 in r)
            self.assertTrue(sub1_testrepo_sub2_file4 in r)
            self.assertTrue(path_utils.dirname_filtered(sub1_testrepo_sub3_file4) in r) # git resolves symlinks
        finally:
            os.chdir(saved_wd)

    def testGetUnversionedFilesAndFolders(self):

        v, r = git_lib.get_unversioned_files_and_folders(self.fourth_notrepo)
        self.assertFalse(v)

        v, r = git_lib.get_unversioned_files_and_folders(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(r, [])

        first_zero1 = path_utils.concat_path(self.first_repo, " ") # filename consisting of a single char (space)
        self.assertTrue(create_and_write_file.create_file_contents(first_zero1, "zero1-contents"))
        first_more1 = path_utils.concat_path(self.first_repo, "more1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_more1, "more1-contents"))
        first_more2 = path_utils.concat_path(self.first_repo, "more2.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_more2, "more2-contents"))
        first_more3 = path_utils.concat_path(self.first_repo, "アーカイブ.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_more3, "more3-contents"))

        first_sub = path_utils.concat_path(self.first_repo, "subfolder")
        os.mkdir(first_sub)
        self.assertTrue(os.path.exists(first_sub))
        first_sub_more4 = path_utils.concat_path(first_sub, "more4.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_sub_more4, "more4-contents"))

        v, r = git_lib.get_unversioned_files_and_folders(self.first_repo)

        self.assertTrue(v)
        self.assertEqual(len(r), 5)
        self.assertTrue(first_zero1 in r)
        self.assertTrue(first_more1 in r)
        self.assertTrue(first_more2 in r)
        #self.assertTrue(first_more3 in r) # mvtodo: might require extra system config or ...
        self.assertTrue(first_sub in r)

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_unversioned_files_and_folders(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

    def testGetUnversionedFilesAndFoldersRelativePath(self):

        sub1 = path_utils.concat_path(self.test_dir, "sub1")
        self.assertFalse(os.path.exists(sub1))
        os.mkdir(sub1)
        self.assertTrue(os.path.exists(sub1))

        sub1_testrepo = path_utils.concat_path(sub1, "testrepo")
        v, r = git_wrapper.init(sub1, "testrepo", False)
        self.assertTrue(v)
        self.assertTrue(os.path.exists(sub1_testrepo))

        testrepo_file1 = path_utils.concat_path(sub1_testrepo, "file1.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file1), "file1-content1", "commit_msg_file1")
        self.assertTrue(v)

        v, r = git_wrapper.stage(sub1_testrepo)
        self.assertTrue(v)

        testrepo_file2 = path_utils.concat_path(sub1_testrepo, "file2.txt")
        self.assertTrue(create_and_write_file.create_file_contents(testrepo_file2, "file2-content1"))

        testrepo_file3 = path_utils.concat_path(sub1_testrepo, "file3.txt")
        self.assertTrue(create_and_write_file.create_file_contents(testrepo_file3, "file3-content1"))

        sub1_testrepo_sub2 = path_utils.concat_path(sub1_testrepo, "sub2")
        os.mkdir(sub1_testrepo_sub2)
        sub1_testrepo_sub3 = path_utils.concat_path(sub1_testrepo, "sub3")
        os.symlink(sub1_testrepo_sub2, sub1_testrepo_sub3)

        sub1_testrepo_sub2_file4 = path_utils.concat_path(sub1_testrepo_sub2, "file4.txt")
        self.assertTrue(create_and_write_file.create_file_contents(sub1_testrepo_sub2_file4, "file4-content1"))
        self.assertTrue(v)
        sub1_testrepo_sub3_file4 = path_utils.concat_path(sub1_testrepo_sub3, "file4.txt")

        self.assertTrue(os.path.exists(sub1_testrepo_sub2_file4))
        self.assertTrue(os.path.exists(sub1_testrepo_sub3_file4))

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            v, r = git_lib.get_unversioned_files_and_folders("./sub1/testrepo")
            self.assertTrue(v)
            self.assertFalse(testrepo_file1 in r)
            self.assertTrue(testrepo_file2 in r)
            self.assertTrue(testrepo_file3 in r)
            self.assertTrue(sub1_testrepo_sub2 in r)
            self.assertTrue(path_utils.dirname_filtered(sub1_testrepo_sub3_file4) in r) # git will return a single entry for a symlink that points to a folder
        finally:
            os.chdir(saved_wd)

    def testGetUnversionedFilesAndFoldersRelativePathSymlinkRepo(self):

        sub2 = path_utils.concat_path(self.test_dir, "sub2")
        self.assertFalse(os.path.exists(sub2))
        os.mkdir(sub2)
        self.assertTrue(os.path.exists(sub2))

        sub1 = path_utils.concat_path(self.test_dir, "sub1")
        self.assertFalse(os.path.exists(sub1))
        os.symlink(sub2, sub1)
        self.assertTrue(os.path.exists(sub1))

        sub1_testrepo = path_utils.concat_path(sub1, "testrepo")
        v, r = git_wrapper.init(sub1, "testrepo", False)
        self.assertTrue(v)
        self.assertTrue(os.path.exists(sub1_testrepo))

        testrepo_file1 = path_utils.concat_path(sub1_testrepo, "file1.txt")
        v, r = git_test_fixture.git_createAndCommit(sub1_testrepo, path_utils.basename_filtered(testrepo_file1), "file1-content1", "commit_msg_file1")
        self.assertTrue(v)

        v, r = git_wrapper.stage(sub1_testrepo)
        self.assertTrue(v)

        testrepo_file2 = path_utils.concat_path(sub1_testrepo, "file2.txt")
        self.assertTrue(create_and_write_file.create_file_contents(testrepo_file2, "file2-content1"))

        testrepo_file3 = path_utils.concat_path(sub1_testrepo, "file3.txt")
        self.assertTrue(create_and_write_file.create_file_contents(testrepo_file3, "file3-content1"))

        sub1_testrepo_sub2 = path_utils.concat_path(sub1_testrepo, "sub2")
        os.mkdir(sub1_testrepo_sub2)
        sub1_testrepo_sub3 = path_utils.concat_path(sub1_testrepo, "sub3")
        os.symlink(sub1_testrepo_sub2, sub1_testrepo_sub3)

        sub1_testrepo_sub2_file4 = path_utils.concat_path(sub1_testrepo_sub2, "file4.txt")
        self.assertTrue(create_and_write_file.create_file_contents(sub1_testrepo_sub2_file4, "file4-content1"))
        self.assertTrue(v)
        sub1_testrepo_sub3_file4 = path_utils.concat_path(sub1_testrepo_sub3, "file4.txt")

        self.assertTrue(os.path.exists(sub1_testrepo_sub2_file4))
        self.assertTrue(os.path.exists(sub1_testrepo_sub3_file4))

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            v, r = git_lib.get_unversioned_files_and_folders("./sub1/testrepo")
            self.assertTrue(v)
            self.assertFalse(testrepo_file1 in r)
            self.assertTrue(testrepo_file2 in r)
            self.assertTrue(testrepo_file3 in r)
            self.assertTrue(sub1_testrepo_sub2 in r)
            self.assertTrue(path_utils.dirname_filtered(sub1_testrepo_sub3_file4) in r) # git resolves symlinks
        finally:
            os.chdir(saved_wd)

    def testRemoveGitlogDecorations(self):

        self.first_file = path_utils.concat_path(self.first_repo, "file.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, path_utils.basename_filtered(self.first_file), "file1-content", "commit_msg_file")
        self.assertTrue(v)

        v, r = git_wrapper.log(self.first_repo, 1)
        self.assertTrue(v)

        self.assertEqual( len(r.strip().split(os.linesep)), 5 )
        self.assertTrue("commit_msg_file" in r)
        commit_msg_oneliner = git_lib.remove_gitlog_decorations(r)
        self.assertEqual( len(commit_msg_oneliner.strip().split(os.linesep)), 1 )
        self.assertEqual("commit_msg_file", commit_msg_oneliner)

    def testIsRepoRoot(self):
        self.assertTrue(git_lib.is_repo_root(path_utils.concat_path(self.first_repo, ".git")))
        self.assertFalse(git_lib.is_repo_root(path_utils.concat_path(self.first_repo, ".anythingelse")))
        self.assertFalse(git_lib.is_repo_root(None))
        self.assertFalse(git_lib.is_repo_root(self.nonexistent_repo))

    def testIsRepoRootRelativePath(self):

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            self.assertTrue(git_lib.is_repo_root(path_utils.concat_path("./first", ".git")))
            self.assertFalse(git_lib.is_repo_root(path_utils.concat_path("./first", ".anythingelse")))
            self.assertFalse(git_lib.is_repo_root(None))
            self.assertFalse(git_lib.is_repo_root("./nonexistent"))
        finally:
            os.chdir(saved_wd)

    def testDiscoverRepoRoot(self):

        folder1 = path_utils.concat_path(self.first_repo, "folder1")
        os.mkdir(folder1)

        self.first_folder1_file2 = path_utils.concat_path(folder1, "file2.txt")
        v, r = git_test_fixture.git_createAndCommit(folder1, path_utils.basename_filtered(self.first_folder1_file2), "file2-content", "commit_msg_file-2")
        self.assertTrue(v)

        folder2 = path_utils.concat_path(folder1, "folder2")
        os.mkdir(folder2)

        folder3 = path_utils.concat_path(self.first_repo, "one", "two", "three")
        self.assertTrue(path_utils.guaranteefolder(folder3))

        self.assertEqual(git_lib.discover_repo_root(self.first_repo), self.first_repo)
        self.assertEqual(git_lib.discover_repo_root(self.nonexistent_repo), None)
        self.assertEqual(git_lib.discover_repo_root(folder1), self.first_repo)
        self.assertEqual(git_lib.discover_repo_root(folder2), self.first_repo)
        self.assertEqual(git_lib.discover_repo_root(folder3), self.first_repo)

    def testDiscoverRepoRootRelativePath(self):

        folder1 = path_utils.concat_path(self.first_repo, "folder1")
        os.mkdir(folder1)

        self.first_folder1_file2 = path_utils.concat_path(folder1, "file2.txt")
        v, r = git_test_fixture.git_createAndCommit(folder1, path_utils.basename_filtered(self.first_folder1_file2), "file2-content", "commit_msg_file-2")
        self.assertTrue(v)

        folder2 = path_utils.concat_path(folder1, "folder2")
        os.mkdir(folder2)

        folder3 = path_utils.concat_path(self.first_repo, "one", "two", "three")
        self.assertTrue(path_utils.guaranteefolder(folder3))

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            self.assertEqual(git_lib.discover_repo_root("./first"), self.first_repo)
            self.assertEqual(git_lib.discover_repo_root("./nonexistent"), None)
            self.assertEqual(git_lib.discover_repo_root("./first/folder1"), self.first_repo)
            self.assertEqual(git_lib.discover_repo_root("./first/folder2"), self.first_repo)
            self.assertEqual(git_lib.discover_repo_root("./first/folder3"), self.first_repo)
        finally:
            os.chdir(saved_wd)

    def testIsRepoWorkingTree(self):

        v, r = git_lib.is_repo_working_tree(self.first_repo)
        self.assertTrue(v)
        self.assertTrue(r)

        first_git_folder = path_utils.concat_path(self.first_repo, ".git")
        self.assertTrue(os.path.exists(first_git_folder))
        v, r = git_lib.is_repo_working_tree(first_git_folder)
        self.assertTrue(v)
        self.assertFalse(r)

        folder = path_utils.concat_path(self.first_repo, "one", "two", "three")
        self.assertTrue(path_utils.guaranteefolder(folder))

        v, r = git_lib.is_repo_working_tree(folder)
        self.assertTrue(v)
        self.assertTrue(r)

        # bare repos are not working trees
        v, r = git_lib.is_repo_working_tree(self.second_repo)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = git_lib.is_repo_working_tree(self.nonexistent_repo)
        self.assertFalse(v)

        v, r = git_lib.is_repo_working_tree(self.fourth_notrepo)
        self.assertTrue(v)
        self.assertFalse(r)

    def testIsRepoWorkingTreeRelativePath(self):

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)

            v, r = git_lib.is_repo_working_tree("./first")
            self.assertTrue(v)
            self.assertTrue(r)

            v, r = git_lib.is_repo_working_tree("./first/.git")
            self.assertTrue(v)
            self.assertFalse(r)

            folder = path_utils.concat_path("./first", "one", "two", "three")
            self.assertTrue(path_utils.guaranteefolder(folder))

            v, r = git_lib.is_repo_working_tree(folder)
            self.assertTrue(v)
            self.assertTrue(r)

            # bare repos are not working trees
            v, r = git_lib.is_repo_working_tree("./second")
            self.assertTrue(v)
            self.assertFalse(r)

            v, r = git_lib.is_repo_working_tree("./nonexistent")
            self.assertFalse(v)

            v, r = git_lib.is_repo_working_tree("./fourth")
            self.assertTrue(v)
            self.assertFalse(r)

        finally:
            os.chdir(saved_wd)

    def testIsRepoBare(self):

        v, r = git_lib.is_repo_bare(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(r)

        second_repo_objects = path_utils.concat_path(self.second_repo, "objects")
        v, r = git_lib.is_repo_bare(second_repo_objects)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = git_lib.is_repo_bare(self.first_repo)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = git_lib.is_repo_bare(self.nonexistent_repo)
        self.assertFalse(v)

    def testIsRepoBareRelativePath(self):

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)

            v, r = git_lib.is_repo_bare("./second")
            self.assertTrue(v)
            self.assertTrue(r)

            second_repo_objects = path_utils.concat_path("./second", "objects")
            v, r = git_lib.is_repo_bare(second_repo_objects)
            self.assertTrue(v)
            self.assertFalse(r)

            v, r = git_lib.is_repo_bare("./first")
            self.assertTrue(v)
            self.assertFalse(r)

            v, r = git_lib.is_repo_bare("./nonexistent")
            self.assertFalse(v)

        finally:
            os.chdir(saved_wd)

    def testIsRepoStandard(self):

        v, r = git_lib.is_repo_standard(self.first_repo)
        self.assertTrue(v)
        self.assertTrue(r)

        v, r = git_lib.is_repo_standard(self.second_repo)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = git_lib.is_repo_standard(self.nonexistent_repo)
        self.assertFalse(v)

        v, r = git_lib.is_repo_standard(self.fourth_notrepo)
        self.assertTrue(v)
        self.assertFalse(r)

        sub_repo = path_utils.concat_path(self.first_repo, "third")
        v, r = git_wrapper.submodule_add(self.third_repo, self.first_repo)
        self.assertTrue(v)
        self.assertTrue(os.path.exists(sub_repo))

        v, r = git_lib.is_repo_standard(sub_repo)
        self.assertTrue(v)
        self.assertFalse(r)

    def testIsRepoStandardRelativePath(self):

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)

            v, r = git_lib.is_repo_standard("./first")
            self.assertTrue(v)
            self.assertTrue(r)

            v, r = git_lib.is_repo_standard("./second")
            self.assertTrue(v)
            self.assertFalse(r)

            v, r = git_lib.is_repo_standard("./nonexistent")
            self.assertFalse(v)

            v, r = git_lib.is_repo_standard("./fourth")
            self.assertTrue(v)
            self.assertFalse(r)

            sub_repo = path_utils.concat_path("./first", "third")
            v, r = git_wrapper.submodule_add(self.third_repo, self.first_repo)
            self.assertTrue(v)
            self.assertTrue(os.path.exists(os.path.abspath(sub_repo)))

            v, r = git_lib.is_repo_standard(sub_repo)
            self.assertTrue(v)
            self.assertFalse(r)

        finally:
            os.chdir(saved_wd)

    def testIsRepoSubmodule(self):

        v, r = git_lib.is_repo_submodule(self.first_repo)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = git_lib.is_repo_submodule(self.second_repo)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = git_lib.is_repo_submodule(self.nonexistent_repo)
        self.assertFalse(v)

        v, r = git_lib.is_repo_submodule(self.fourth_notrepo)
        self.assertTrue(v)
        self.assertFalse(r)

        sub_repo = path_utils.concat_path(self.first_repo, "third")
        v, r = git_wrapper.submodule_add(self.third_repo, self.first_repo)
        self.assertTrue(v)
        self.assertTrue(os.path.exists(sub_repo))

        v, r = git_lib.is_repo_submodule(sub_repo)
        self.assertTrue(v)
        self.assertTrue(r)

    def testIsRepoSubmoduleRelativePath(self):

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)

            v, r = git_lib.is_repo_submodule("./first")
            self.assertTrue(v)
            self.assertFalse(r)

            v, r = git_lib.is_repo_submodule("./second")
            self.assertTrue(v)
            self.assertFalse(r)

            v, r = git_lib.is_repo_submodule("./nonexistent")
            self.assertFalse(v)

            v, r = git_lib.is_repo_submodule("./fourth")
            self.assertTrue(v)
            self.assertFalse(r)

            sub_repo = path_utils.concat_path("./first", "third")
            v, r = git_wrapper.submodule_add(self.third_repo, self.first_repo)
            self.assertTrue(v)
            self.assertTrue(os.path.exists(os.path.abspath(sub_repo)))

            v, r = git_lib.is_repo_submodule(sub_repo)
            self.assertTrue(v)
            self.assertTrue(r)

        finally:
            os.chdir(saved_wd)

    def testIsHeadClearSimpleMod(self):

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertTrue(r)

        with open(self.first_file1, "a") as f:
            f.write("extra content")

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertFalse(r)

    def testIsHeadClearStaged(self):

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertTrue(r)

        with open(self.first_file1, "a") as f:
            f.write("extra content")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertFalse(r)

    def testIsHeadClearUnversioned(self):

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertTrue(r)

        unv_file = path_utils.concat_path(self.first_repo, "unvfile")
        self.assertFalse(os.path.exists(unv_file))
        self.assertTrue(create_and_write_file.create_file_contents(unv_file, "more1-contents"))
        self.assertTrue(os.path.exists(unv_file))

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertFalse(r)

    def testIsHeadClearHeadDeleted(self):

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertTrue(r)

        os.unlink(self.first_file1)
        self.assertFalse(os.path.exists(self.first_file1))

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertFalse(r)

    def testIsHeadClearStagedDeleted(self):

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertTrue(r)

        os.unlink(self.first_file1)
        self.assertFalse(os.path.exists(self.first_file1))

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertFalse(r)

    def testIsHeadClearStagedRenamed(self):

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertTrue(r)

        renamed_file = path_utils.concat_path(self.first_repo, "file1_renamed.txt")
        self.assertFalse(os.path.exists(renamed_file))
        self.assertTrue(path_utils.copy_to_and_rename(self.first_file1, self.first_repo, path_utils.basename_filtered(renamed_file)))
        self.assertTrue(os.path.exists(renamed_file))
        os.unlink(self.first_file1)
        self.assertFalse(os.path.exists(self.first_file1))

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertFalse(r)

    def testIsHeadClearUpdated(self):

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertTrue(r)

        with open(self.first_file1, "a") as f:
            f.write("extra content")

        v, r = git_wrapper.stash(self.first_repo)
        self.assertTrue(v)

        with open(self.first_file1, "a") as f:
            f.write("different-extra")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.first_repo, "latest commit")
        self.assertTrue(v)

        v, r = git_wrapper.stash_pop(self.first_repo)
        self.assertFalse(v) # failure because of conflict

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertFalse(r)

    def testIsHeadClearUnversionedStaged(self):

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertTrue(r)

        unv_file = path_utils.concat_path(self.first_repo, "unvfile")
        self.assertFalse(os.path.exists(unv_file))
        self.assertTrue(create_and_write_file.create_file_contents(unv_file, "more1-contents"))
        self.assertTrue(os.path.exists(unv_file))

        v, r = git_wrapper.stage(self.first_repo, [unv_file])
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertFalse(r)

    def testIsHeadClearRelativePath(self):

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)

            v, r = git_lib.is_head_clear("./first")
            self.assertTrue(v)
            self.assertTrue(r)

            with open(self.first_file1, "a") as f:
                f.write("extra content")

            v, r = git_lib.is_head_clear("./first")
            self.assertTrue(v)
            self.assertFalse(r)

        finally:
            os.chdir(saved_wd)

    def testIsHeadClearFail1(self):

        with open(self.first_file1, "a") as f:
            f.write("extra content")

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertFalse(r)

    def testIsHeadClearFail2(self):

        with open(self.first_file1, "a") as f:
            f.write("extra content")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertFalse(r)

    def testIsHeadClearFail3(self):

        first_file2 = path_utils.concat_path(self.first_repo, "file2.txt")
        with open(first_file2, "a") as f:
            f.write("latest file")

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertFalse(r)

    def testIsHeadClearStashed(self):

        with open(self.first_file1, "a") as f:
            f.write("extra content")

        v, r = git_wrapper.stash(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertTrue(r)

    def testPatchAsHead(self):

        first_mirror = path_utils.concat_path(self.test_dir, "first_mirror")
        v, r = git_wrapper.clone(self.first_repo, first_mirror, "origin")
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v and r)
        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v and r)

        with open(self.first_file1, "a") as f:
            f.write("changes")

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path, "include", [], [])
        self.assertTrue(v)
        generated_patch_file = r
        self.assertTrue(os.path.exists(generated_patch_file))

        v, r = git_lib.patch_as_head(first_mirror, generated_patch_file, False)
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = git_lib.get_head_modified_files(self.first_repo)
        self.assertTrue(v)
        mod_first = r

        v, r = git_lib.get_head_modified_files(first_mirror)
        self.assertTrue(v)
        mod_first_mirror = r

        self.assertEqual(path_utils.basename_filtered(mod_first[0]), path_utils.basename_filtered(mod_first_mirror[0]))

    def testPatchAsHeadRelativePath(self):

        first_mirror = path_utils.concat_path(self.test_dir, "first_mirror")
        v, r = git_wrapper.clone(self.first_repo, first_mirror, "origin")
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v and r)
        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v and r)

        with open(self.first_file1, "a") as f:
            f.write("changes")

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path, "include", [], [])
        self.assertTrue(v)
        generated_patch_file = r
        self.assertTrue(os.path.exists(generated_patch_file))
        generated_patch_file_rel_path = path_utils.concat_path("./", path_utils.basename_filtered(self.storage_path), self.first_repo, path_utils.basename_filtered(generated_patch_file))

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            self.assertTrue(os.path.exists(generated_patch_file_rel_path))
            v, r = git_lib.patch_as_head("./first_mirror", generated_patch_file_rel_path, False)
            self.assertTrue(v)
        finally:
            os.chdir(saved_wd)

        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = git_lib.get_head_modified_files(self.first_repo)
        self.assertTrue(v)
        mod_first = r

        v, r = git_lib.get_head_modified_files(first_mirror)
        self.assertTrue(v)
        mod_first_mirror = r

        self.assertEqual(path_utils.basename_filtered(mod_first[0]), path_utils.basename_filtered(mod_first_mirror[0]))

    def testPatchAsHeadFail1(self):

        first_mirror = path_utils.concat_path(self.test_dir, "first_mirror")
        v, r = git_wrapper.clone(self.first_repo, first_mirror, "origin")
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v and r)
        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v and r)

        with open(self.first_file1, "a") as f:
            f.write("changes")

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path, "include", [], [])
        self.assertTrue(v)
        generated_patch_file = r
        self.assertTrue(os.path.exists(generated_patch_file))

        first_mirror_more1 = path_utils.concat_path(first_mirror, "more1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_mirror_more1, "more1-contents"))

        v, r = git_lib.patch_as_head(first_mirror, generated_patch_file, False)
        self.assertFalse(v)

        v, r = git_lib.get_head_modified_files(first_mirror)
        self.assertTrue(v)
        self.assertEqual(r, [])

        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v)
        self.assertFalse(r)

    def testPatchAsHeadFail2(self):

        first_mirror = path_utils.concat_path(self.test_dir, "first_mirror")
        v, r = git_wrapper.clone(self.first_repo, first_mirror, "origin")
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v and r)
        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v and r)

        with open(self.first_file1, "a") as f:
            f.write("changes")

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path, "include", [], [])
        self.assertTrue(v)
        generated_patch_file = r
        self.assertTrue(os.path.exists(generated_patch_file))

        first_mirror_more1 = path_utils.concat_path(first_mirror, "more1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_mirror_more1, "more1-contents"))

        v, r = git_wrapper.stage(first_mirror, [first_mirror_more1])
        self.assertTrue(v)

        v, r = git_lib.patch_as_head(first_mirror, generated_patch_file, False)
        self.assertFalse(v)

        v, r = git_lib.get_head_modified_files(first_mirror)
        self.assertTrue(v)
        self.assertEqual(r, [])

        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v)
        self.assertFalse(r)

    def testPatchAsHeadOverrideFail1(self):

        first_mirror = path_utils.concat_path(self.test_dir, "first_mirror")
        v, r = git_wrapper.clone(self.first_repo, first_mirror, "origin")
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v and r)
        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v and r)

        with open(self.first_file1, "a") as f:
            f.write("changes")

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path, "include", [], [])
        self.assertTrue(v)
        generated_patch_file = r
        self.assertTrue(os.path.exists(generated_patch_file))

        first_mirror_more1 = path_utils.concat_path(first_mirror, "more1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_mirror_more1, "more1-contents"))

        v, r = git_lib.patch_as_head(first_mirror, generated_patch_file, True)
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = git_lib.get_head_modified_files(self.first_repo)
        self.assertTrue(v)
        mod_first = r

        v, r = git_lib.get_head_modified_files(first_mirror)
        self.assertTrue(v)
        mod_first_mirror = r

        self.assertEqual(path_utils.basename_filtered(mod_first[0]), path_utils.basename_filtered(mod_first_mirror[0]))

    def testPatchAsHeadOverrideFail2(self):

        first_mirror = path_utils.concat_path(self.test_dir, "first_mirror")
        v, r = git_wrapper.clone(self.first_repo, first_mirror, "origin")
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v and r)
        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v and r)

        with open(self.first_file1, "a") as f:
            f.write("changes")

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path, "include", [], [])
        self.assertTrue(v)
        generated_patch_file = r
        self.assertTrue(os.path.exists(generated_patch_file))

        first_mirror_more1 = path_utils.concat_path(first_mirror, "more1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_mirror_more1, "more1-contents"))

        v, r = git_wrapper.stage(first_mirror, [first_mirror_more1])
        self.assertTrue(v)

        v, r = git_lib.patch_as_head(first_mirror, generated_patch_file, True)
        self.assertTrue(v)

        v, r = git_lib.get_head_modified_files(self.first_repo)
        self.assertTrue(v)
        mod_first = r

        v, r = git_lib.get_head_modified_files(first_mirror)
        self.assertTrue(v)
        mod_first_mirror = r

        self.assertEqual(path_utils.basename_filtered(mod_first[0]), path_utils.basename_filtered(mod_first_mirror[0]))

    def testPatchAsStaged(self):

        first_mirror = path_utils.concat_path(self.test_dir, "first_mirror")
        v, r = git_wrapper.clone(self.first_repo, first_mirror, "origin")
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v and r)
        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v and r)

        with open(self.first_file1, "a") as f:
            f.write("changes")

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path, "include", [], [])
        self.assertTrue(v)
        generated_patch_file = r
        self.assertTrue(os.path.exists(generated_patch_file))

        v, r = git_lib.patch_as_staged(first_mirror, generated_patch_file, False)
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = git_lib.get_head_modified_files(self.first_repo)
        self.assertTrue(v)
        mod_first = r

        v, r = git_lib.get_staged_files(first_mirror)
        self.assertTrue(v)
        mod_first_mirror = r

        self.assertEqual(path_utils.basename_filtered(mod_first[0]), path_utils.basename_filtered(mod_first_mirror[0]))

    def testPatchAsStagedRelativePath(self):

        first_mirror = path_utils.concat_path(self.test_dir, "first_mirror")
        v, r = git_wrapper.clone(self.first_repo, first_mirror, "origin")
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v and r)
        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v and r)

        with open(self.first_file1, "a") as f:
            f.write("changes")

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path, "include", [], [])
        self.assertTrue(v)
        generated_patch_file = r
        self.assertTrue(os.path.exists(generated_patch_file))
        generated_patch_file_rel_path = path_utils.concat_path("./", path_utils.basename_filtered(self.storage_path), self.first_repo, path_utils.basename_filtered(generated_patch_file))

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            self.assertTrue(os.path.exists(generated_patch_file_rel_path))

            v, r = git_lib.patch_as_staged("./first_mirror", generated_patch_file_rel_path, False)
            self.assertTrue(v)

        finally:
            os.chdir(saved_wd)

        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = git_lib.get_head_modified_files(self.first_repo)
        self.assertTrue(v)
        mod_first = r

        v, r = git_lib.get_staged_files(first_mirror)
        self.assertTrue(v)
        mod_first_mirror = r

        self.assertEqual(path_utils.basename_filtered(mod_first[0]), path_utils.basename_filtered(mod_first_mirror[0]))

    def testPatchAsStagedFail1(self):

        first_mirror = path_utils.concat_path(self.test_dir, "first_mirror")
        v, r = git_wrapper.clone(self.first_repo, first_mirror, "origin")
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v and r)
        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v and r)

        with open(self.first_file1, "a") as f:
            f.write("changes")

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path, "include", [], [])
        self.assertTrue(v)
        generated_patch_file = r
        self.assertTrue(os.path.exists(generated_patch_file))

        first_mirror_more1 = path_utils.concat_path(first_mirror, "more1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_mirror_more1, "more1-contents"))

        v, r = git_lib.patch_as_staged(first_mirror, generated_patch_file, False)
        self.assertFalse(v)

        v, r = git_lib.get_staged_files(first_mirror)
        self.assertTrue(v)
        self.assertEqual(r, [])

        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v)
        self.assertFalse(r)

    def testPatchAsStagedFail2(self):

        first_mirror = path_utils.concat_path(self.test_dir, "first_mirror")
        v, r = git_wrapper.clone(self.first_repo, first_mirror, "origin")
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v and r)
        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v and r)

        with open(self.first_file1, "a") as f:
            f.write("changes")

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path, "include", [], [])
        self.assertTrue(v)
        generated_patch_file = r
        self.assertTrue(os.path.exists(generated_patch_file))

        first_mirror_more1 = path_utils.concat_path(first_mirror, "more1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_mirror_more1, "more1-contents"))

        v, r = git_wrapper.stage(first_mirror, [first_mirror_more1])
        self.assertTrue(v)

        v, r = git_lib.patch_as_staged(first_mirror, generated_patch_file, False)
        self.assertFalse(v)

        v, r = git_lib.get_staged_files(first_mirror)
        self.assertTrue(v)
        staged_list_first_mirror = r
        self.assertEqual(path_utils.basename_filtered(staged_list_first_mirror[0]), path_utils.basename_filtered(first_mirror_more1))

        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v)
        self.assertFalse(r)

    def testPatchAsStagedOverrideFail1(self):

        first_mirror = path_utils.concat_path(self.test_dir, "first_mirror")
        v, r = git_wrapper.clone(self.first_repo, first_mirror, "origin")
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v and r)
        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v and r)

        with open(self.first_file1, "a") as f:
            f.write("changes")

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path, "include", [], [])
        self.assertTrue(v)
        generated_patch_file = r
        self.assertTrue(os.path.exists(generated_patch_file))

        first_mirror_more1 = path_utils.concat_path(first_mirror, "more1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_mirror_more1, "more1-contents"))

        v, r = git_lib.patch_as_staged(first_mirror, generated_patch_file, True)
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = git_lib.get_head_modified_files(self.first_repo)
        self.assertTrue(v)
        mod_first = r

        v, r = git_lib.get_staged_files(first_mirror)
        self.assertTrue(v)
        mod_first_mirror = r

        self.assertEqual(path_utils.basename_filtered(mod_first[0]), path_utils.basename_filtered(mod_first_mirror[0]))

    def testPatchAsStagedOverrideFail2(self):

        first_mirror = path_utils.concat_path(self.test_dir, "first_mirror")
        v, r = git_wrapper.clone(self.first_repo, first_mirror, "origin")
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v and r)
        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v and r)

        with open(self.first_file1, "a") as f:
            f.write("changes")

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path, "include", [], [])
        self.assertTrue(v)
        generated_patch_file = r
        self.assertTrue(os.path.exists(generated_patch_file))

        first_mirror_more1 = path_utils.concat_path(first_mirror, "more1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_mirror_more1, "more1-contents"))

        v, r = git_wrapper.stage(first_mirror, [first_mirror_more1])
        self.assertTrue(v)

        v, r = git_lib.patch_as_staged(first_mirror, generated_patch_file, True)
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = git_lib.get_head_modified_files(self.first_repo)
        self.assertTrue(v)
        mod_first = r

        v, r = git_lib.get_staged_files(first_mirror)
        self.assertTrue(v)
        mod_first_mirror = r

        self.assertEqual(path_utils.basename_filtered(mod_first[0]), path_utils.basename_filtered(mod_first_mirror[0]))

    def testPatchAsStash(self):

        first_mirror = path_utils.concat_path(self.test_dir, "first_mirror")
        v, r = git_wrapper.clone(self.first_repo, first_mirror, "origin")
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v and r)
        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v and r)

        with open(self.first_file1, "a") as f:
            f.write("changes")

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path, "include", [], [])
        self.assertTrue(v)
        generated_patch_file = r
        self.assertTrue(os.path.exists(generated_patch_file))

        v, r = git_lib.patch_as_stash(first_mirror, generated_patch_file, False, False)
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v)
        self.assertTrue(r)

        v, r = git_lib.get_stash_list(first_mirror)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

    def testPatchAsStashRelativePath(self):

        first_mirror = path_utils.concat_path(self.test_dir, "first_mirror")
        v, r = git_wrapper.clone(self.first_repo, first_mirror, "origin")
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v and r)
        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v and r)

        with open(self.first_file1, "a") as f:
            f.write("changes")

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path, "include", [], [])
        self.assertTrue(v)
        generated_patch_file = r
        self.assertTrue(os.path.exists(generated_patch_file))
        generated_patch_file_rel_path = path_utils.concat_path("./", path_utils.basename_filtered(self.storage_path), self.first_repo, path_utils.basename_filtered(generated_patch_file))

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            self.assertTrue(os.path.exists(generated_patch_file_rel_path))

            v, r = git_lib.patch_as_stash("./first_mirror", generated_patch_file_rel_path, False, False)
            self.assertTrue(v)

            v, r = git_lib.is_head_clear(first_mirror)
            self.assertTrue(v)
            self.assertTrue(r)

            v, r = git_lib.get_stash_list("./first_mirror")
            self.assertTrue(v)
            self.assertEqual(len(r), 1)

        finally:
            os.chdir(saved_wd)

    def testPatchAsStashFail1(self):

        first_mirror = path_utils.concat_path(self.test_dir, "first_mirror")
        v, r = git_wrapper.clone(self.first_repo, first_mirror, "origin")
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v and r)
        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v and r)

        with open(self.first_file1, "a") as f:
            f.write("changes")

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path, "include", [], [])
        self.assertTrue(v)
        generated_patch_file = r
        self.assertTrue(os.path.exists(generated_patch_file))

        first_mirror_more1 = path_utils.concat_path(first_mirror, "more1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_mirror_more1, "more1-contents"))

        v, r = git_lib.patch_as_stash(first_mirror, generated_patch_file, False, False)
        self.assertFalse(v)

        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v)
        self.assertFalse(r)

    def testPatchAsStashFail2(self):

        first_mirror = path_utils.concat_path(self.test_dir, "first_mirror")
        v, r = git_wrapper.clone(self.first_repo, first_mirror, "origin")
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v and r)
        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v and r)

        with open(self.first_file1, "a") as f:
            f.write("changes")

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path, "include", [], [])
        self.assertTrue(v)
        generated_patch_file = r
        self.assertTrue(os.path.exists(generated_patch_file))

        self.first_mirror_file1 = path_utils.concat_path(first_mirror, "file1.txt")
        with open(self.first_mirror_file1, "a") as f:
            f.write("additional content")

        v, r = git_lib.patch_as_stash(first_mirror, generated_patch_file, False, False)
        self.assertFalse(v)

        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = git_lib.get_stash_list(first_mirror)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

    def testPatchAsStashFail3(self):

        first_mirror = path_utils.concat_path(self.test_dir, "first_mirror")
        v, r = git_wrapper.clone(self.first_repo, first_mirror, "origin")
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v and r)
        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v and r)

        with open(self.first_file1, "a") as f:
            f.write("changes")

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path, "include", [], [])
        self.assertTrue(v)
        generated_patch_file = r
        self.assertTrue(os.path.exists(generated_patch_file))

        self.first_mirror_file1 = path_utils.concat_path(first_mirror, "file1.txt")
        with open(self.first_mirror_file1, "a") as f:
            f.write("additional content")

        v, r = git_wrapper.stash(first_mirror)
        self.assertTrue(v)

        v, r = git_lib.patch_as_stash(first_mirror, generated_patch_file, False, False)
        self.assertFalse(v)

        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v)
        self.assertTrue(r)

        v, r = git_lib.get_stash_list(first_mirror)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

    def testPatchAsStashOverrideFail1(self):

        first_mirror = path_utils.concat_path(self.test_dir, "first_mirror")
        v, r = git_wrapper.clone(self.first_repo, first_mirror, "origin")
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v and r)
        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v and r)

        with open(self.first_file1, "a") as f:
            f.write("changes")

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path, "include", [], [])
        self.assertTrue(v)
        generated_patch_file = r
        self.assertTrue(os.path.exists(generated_patch_file))

        first_mirror_more1 = path_utils.concat_path(first_mirror, "more1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(first_mirror_more1, "more1-contents"))

        v, r = git_lib.patch_as_stash(first_mirror, generated_patch_file, True, True)
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v)
        self.assertFalse(r)

    def testPatchAsStashOverrideFail2(self):

        first_mirror = path_utils.concat_path(self.test_dir, "first_mirror")
        v, r = git_wrapper.clone(self.first_repo, first_mirror, "origin")
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v and r)
        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v and r)

        with open(self.first_file1, "a") as f:
            f.write("changes")

        v, r = git_lib.is_head_clear(self.first_repo)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = collect_git_patch.collect_git_patch_head(self.first_repo, self.storage_path, "include", [], [])
        self.assertTrue(v)
        generated_patch_file = r
        self.assertTrue(os.path.exists(generated_patch_file))

        self.first_mirror_file1 = path_utils.concat_path(first_mirror, "file1.txt")
        with open(self.first_mirror_file1, "a") as f:
            f.write("additional content")

        v, r = git_wrapper.stash(first_mirror)
        self.assertTrue(v)

        v, r = git_lib.patch_as_stash(first_mirror, generated_patch_file, True, True)
        self.assertTrue(v)

        v, r = git_lib.is_head_clear(first_mirror)
        self.assertTrue(v)
        self.assertTrue(r)

        v, r = git_lib.get_stash_list(first_mirror)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)

    def testUnstageFail1(self):

        first_file2 = path_utils.concat_path(self.first_repo, "file2.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, path_utils.basename_filtered(first_file2), "file2-content1", "commit_msg_file2")
        self.assertTrue(v)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "a") as f:
            f.write("smore")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        v, r = git_lib.unstage(self.first_repo, [first_file2])
        self.assertFalse(v)

        v, r = git_lib.unstage(self.first_repo, [self.first_file1, first_file2])
        self.assertFalse(v)

    def testUnstageFail2(self):

        first_file2 = path_utils.concat_path(self.first_repo, "file2.txt")

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "a") as f:
            f.write("smore")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        v, r = git_lib.unstage(self.first_repo, [first_file2])
        self.assertFalse(v)

    def testUnstageFail3(self):

        first_file2 = path_utils.concat_path(self.first_repo, "file2.txt")

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "a") as f:
            f.write("smore")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        self.assertTrue(create_and_write_file.create_file_contents(first_file2, "more1-contents"))

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        v, r = git_lib.unstage(self.first_repo, [first_file2])
        self.assertFalse(v)

    def testUnstage1(self):

        first_file2 = path_utils.concat_path(self.first_repo, "file2.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, path_utils.basename_filtered(first_file2), "file2-content1", "commit_msg_file2")
        self.assertTrue(v)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "a") as f:
            f.write("smore")

        with open(first_file2, "a") as f:
            f.write("smore")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)

        v, r = git_lib.unstage(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

    def testUnstage2(self):

        first_file2 = path_utils.concat_path(self.first_repo, "file2.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, path_utils.basename_filtered(first_file2), "file2-content1", "commit_msg_file2")
        self.assertTrue(v)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "a") as f:
            f.write("smore")

        with open(first_file2, "a") as f:
            f.write("smore")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)

        v, r = git_lib.unstage(self.first_repo, [self.first_file1])
        self.assertTrue(v)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertFalse(self.first_file1 in r)
        self.assertTrue(first_file2 in r)

    def testUnstageRelativePath1(self):

        first_file2 = path_utils.concat_path(self.first_repo, "file2.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, path_utils.basename_filtered(first_file2), "file2-content1", "commit_msg_file2")
        self.assertTrue(v)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "a") as f:
            f.write("smore")

        with open(first_file2, "a") as f:
            f.write("smore")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            v, r = git_lib.unstage("./first")
            self.assertTrue(v)
        finally:
            os.chdir(saved_wd)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

    def testUnstageRelativePath2(self):

        first_file2 = path_utils.concat_path(self.first_repo, "file2.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, path_utils.basename_filtered(first_file2), "file2-content1", "commit_msg_file2")
        self.assertTrue(v)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "a") as f:
            f.write("smore")

        with open(first_file2, "a") as f:
            f.write("smore")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            first_file_rel_path = path_utils.concat_path("./", path_utils.basename_filtered(self.first_repo), path_utils.basename_filtered(self.first_file1))
            self.assertTrue(os.path.exists(first_file_rel_path))

            v, r = git_lib.unstage("./first", [first_file_rel_path])
            self.assertTrue(v)
        finally:
            os.chdir(saved_wd)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertFalse(self.first_file1 in r)
        self.assertTrue(first_file2 in r)

    def testSoftReset1(self):

        first_file2 = path_utils.concat_path(self.first_repo, "file2.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, path_utils.basename_filtered(first_file2), "file2-content1", "commit_msg_file2")
        self.assertTrue(v)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "a") as f:
            f.write("smore")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        v, r = git_lib.soft_reset(self.first_repo, [first_file2])
        self.assertTrue(v)

        v, r = git_lib.soft_reset(self.first_repo, [self.first_file1, first_file2])
        self.assertTrue(v)

    def testSoftReset2(self):

        first_file2 = path_utils.concat_path(self.first_repo, "file2.txt")

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "a") as f:
            f.write("smore")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        v, r = git_lib.soft_reset(self.first_repo, [first_file2])
        self.assertTrue(v)

    def testSoftReset3(self):

        first_file2 = path_utils.concat_path(self.first_repo, "file2.txt")

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "a") as f:
            f.write("smore")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        self.assertTrue(create_and_write_file.create_file_contents(first_file2, "more1-contents"))

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        v, r = git_lib.soft_reset(self.first_repo, [first_file2])
        self.assertTrue(v)

    def testSoftReset4(self):

        first_file2 = path_utils.concat_path(self.first_repo, "file2.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, path_utils.basename_filtered(first_file2), "file2-content1", "commit_msg_file2")
        self.assertTrue(v)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "a") as f:
            f.write("smore")

        with open(first_file2, "a") as f:
            f.write("smore")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)

        v, r = git_lib.soft_reset(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

    def testSoftReset5(self):

        first_file2 = path_utils.concat_path(self.first_repo, "file2.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, path_utils.basename_filtered(first_file2), "file2-content1", "commit_msg_file2")
        self.assertTrue(v)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "a") as f:
            f.write("smore")

        with open(first_file2, "a") as f:
            f.write("smore")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)

        v, r = git_lib.soft_reset(self.first_repo, [self.first_file1])
        self.assertTrue(v)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertFalse(self.first_file1 in r)
        self.assertTrue(first_file2 in r)

    def testSoftReset6(self):

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "a") as f:
            f.write("more stuff")

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        v, r = git_wrapper.stash(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        self.assertTrue(os.path.exists(self.first_file1))
        os.unlink(self.first_file1)
        self.assertFalse(os.path.exists(self.first_file1))

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.first_repo, "commit msg")
        self.assertTrue(v)

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = git_wrapper.stash_pop(self.first_repo)
        self.assertFalse(v) # fails because of conflict

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        v, r = git_lib.soft_reset(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

    def testSoftReset7(self):

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        self.assertTrue(os.path.exists(self.first_file1))
        os.unlink(self.first_file1)
        self.assertFalse(os.path.exists(self.first_file1))

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        v, r = git_wrapper.stash(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "a") as f:
            f.write("more stuff")

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.first_repo, "commit msg")
        self.assertTrue(v)

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        v, r = git_wrapper.stash_pop(self.first_repo)
        self.assertFalse(v) # fails because of conflict

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        v, r = git_lib.soft_reset(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_head_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

    def testSoftResetRelativePath1(self):

        first_file2 = path_utils.concat_path(self.first_repo, "file2.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, path_utils.basename_filtered(first_file2), "file2-content1", "commit_msg_file2")
        self.assertTrue(v)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "a") as f:
            f.write("smore")

        with open(first_file2, "a") as f:
            f.write("smore")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            v, r = git_lib.soft_reset("./first")
            self.assertTrue(v)
        finally:
            os.chdir(saved_wd)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

    def testSoftResetRelativePath2(self):

        first_file2 = path_utils.concat_path(self.first_repo, "file2.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, path_utils.basename_filtered(first_file2), "file2-content1", "commit_msg_file2")
        self.assertTrue(v)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

        with open(self.first_file1, "a") as f:
            f.write("smore")

        with open(first_file2, "a") as f:
            f.write("smore")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            first_file_rel_path = path_utils.concat_path("./", path_utils.basename_filtered(self.first_repo), path_utils.basename_filtered(self.first_file1))
            self.assertTrue(os.path.exists(first_file_rel_path))

            v, r = git_lib.soft_reset("./first", [first_file_rel_path])
            self.assertTrue(v)
        finally:
            os.chdir(saved_wd)

        v, r = git_lib.get_staged_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertFalse(self.first_file1 in r)
        self.assertTrue(first_file2 in r)

    def testGetPreviousHashListFail1(self):

        v, r = git_lib.get_previous_hash_list(None, 1)
        self.assertFalse(v)

    def testGetPreviousHashList1(self):

        first_file2 = path_utils.concat_path(self.first_repo, "file2.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, path_utils.basename_filtered(first_file2), "file2-content1", "commit_msg_file2")
        self.assertTrue(v)

        with open(self.first_file1, "a") as f:
            f.write("smore")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.first_repo, "commit_msg_file3")
        self.assertTrue(v)

        with open(first_file2, "a") as f:
            f.write("smore")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.first_repo, "commit_msg_file4")
        self.assertTrue(v)

        v, r = git_lib.get_previous_hash_list(self.first_repo, 1)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertTrue(string_utils.is_hex_string(r[0]))
        self.assertEqual(len(r[0]), 7)

    def testGetPreviousHashList2(self):

        first_file2 = path_utils.concat_path(self.first_repo, "file2.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, path_utils.basename_filtered(first_file2), "file2-content1", "commit_msg_file2")
        self.assertTrue(v)

        with open(self.first_file1, "a") as f:
            f.write("smore")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.first_repo, "commit_msg_file3")
        self.assertTrue(v)

        with open(first_file2, "a") as f:
            f.write("smore")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.first_repo, "commit_msg_file4")
        self.assertTrue(v)

        v, r = git_lib.get_previous_hash_list(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 4)
        for x in r:
            self.assertTrue(string_utils.is_hex_string(x))
            self.assertEqual(len(x), 7)

    def testGetPreviousHashList3(self):

        first_file2 = path_utils.concat_path(self.first_repo, "file2.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, path_utils.basename_filtered(first_file2), "file2-content1", "commit_msg_file2")
        self.assertTrue(v)

        with open(self.first_file1, "a") as f:
            f.write("smore")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.first_repo, "commit_msg_file3")
        self.assertTrue(v)

        with open(first_file2, "a") as f:
            f.write("smore")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.first_repo, "commit_msg_file4")
        self.assertTrue(v)

        v, r = git_lib.get_previous_hash_list(self.first_repo, 8)
        self.assertTrue(v)
        self.assertEqual(len(r), 4)
        for x in r:
            self.assertTrue(string_utils.is_hex_string(x))
            self.assertEqual(len(x), 7)

    def testGetPreviousHashListRelativePath1(self):

        first_file2 = path_utils.concat_path(self.first_repo, "file2.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, path_utils.basename_filtered(first_file2), "file2-content1", "commit_msg_file2")
        self.assertTrue(v)

        with open(self.first_file1, "a") as f:
            f.write("smore")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.first_repo, "commit_msg_file3")
        self.assertTrue(v)

        with open(first_file2, "a") as f:
            f.write("smore")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.first_repo, "commit_msg_file4")
        self.assertTrue(v)

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            v, r = git_lib.get_previous_hash_list("./first")
            self.assertTrue(v)
            self.assertEqual(len(r), 4)
            for x in r:
                self.assertTrue(string_utils.is_hex_string(x))
                self.assertEqual(len(x), 7)
        finally:
            os.chdir(saved_wd)

    def testGetHeadHash(self):

        v, r = git_lib.get_previous_hash_list(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)

        v, r = git_lib.get_head_hash(self.first_repo)
        self.assertTrue(v)
        self.assertTrue(string_utils.is_hex_string(r))

    def testGetHeadHashRelativePath(self):

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            v, r = git_lib.get_head_hash("./first")
            self.assertTrue(v)
            self.assertTrue(string_utils.is_hex_string(r))
        finally:
            os.chdir(saved_wd)

    def testCloneBareRepo(self):

        with mock.patch("git_wrapper.clone_bare", return_value=(True, None)) as dummy:
            v, r = git_lib.clone_bare(self.first_repo, self.nonexistent_repo)
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(self.first_repo, self.nonexistent_repo)

        with mock.patch("git_wrapper.clone_bare", return_value=(True, None)) as dummy:
            v, r = git_lib.clone_bare(None, self.nonexistent_repo)
            self.assertFalse(v)
            dummy.assert_not_called()

        with mock.patch("git_wrapper.clone_bare", return_value=(True, None)) as dummy:
            v, r = git_lib.clone_bare(self.first_repo, None)
            self.assertFalse(v)
            dummy.assert_not_called()

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)

            first_rel_path = path_utils.concat_path("./", os.path.basename(self.first_repo))
            with mock.patch("git_wrapper.clone_bare", return_value=(True, None)) as dummy:
                v, r = git_lib.clone_bare(first_rel_path, self.nonexistent_repo)
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy.assert_called_with(self.first_repo, self.nonexistent_repo)

            nonexistent_rel_path = path_utils.concat_path("./", os.path.basename(self.nonexistent_repo))
            with mock.patch("git_wrapper.clone_bare", return_value=(True, None)) as dummy:
                v, r = git_lib.clone_bare(self.first_repo, nonexistent_rel_path)
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy.assert_called_with(self.first_repo, self.nonexistent_repo)

        finally:
            os.chdir(saved_wd)

    def testCloneRepo(self):

        with mock.patch("git_wrapper.clone", return_value=(True, None)) as dummy:
            v, r = git_lib.clone(self.first_repo, self.nonexistent_repo)
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(self.first_repo, self.nonexistent_repo, None)

        with mock.patch("git_wrapper.clone", return_value=(True, None)) as dummy:
            v, r = git_lib.clone(self.first_repo, self.nonexistent_repo, "remotename")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(self.first_repo, self.nonexistent_repo, "remotename")

        with mock.patch("git_wrapper.clone", return_value=(True, None)) as dummy:
            v, r = git_lib.clone(None, self.nonexistent_repo)
            self.assertFalse(v)
            dummy.assert_not_called()

        with mock.patch("git_wrapper.clone", return_value=(True, None)) as dummy:
            v, r = git_lib.clone(self.first_repo, None)
            self.assertFalse(v)
            dummy.assert_not_called()

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)

            first_rel_path = path_utils.concat_path("./", os.path.basename(self.first_repo))
            with mock.patch("git_wrapper.clone", return_value=(True, None)) as dummy:
                v, r = git_lib.clone(first_rel_path, self.nonexistent_repo)
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy.assert_called_with(self.first_repo, self.nonexistent_repo, None)

            nonexistent_rel_path = path_utils.concat_path("./", os.path.basename(self.nonexistent_repo))
            with mock.patch("git_wrapper.clone", return_value=(True, None)) as dummy:
                v, r = git_lib.clone(self.first_repo, nonexistent_rel_path)
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy.assert_called_with(self.first_repo, self.nonexistent_repo, None)

        finally:
            os.chdir(saved_wd)

    def testCloneRepoExt(self):

        with mock.patch("git_wrapper.clone_ext", return_value=(True, None)) as dummy:
            v, r = git_lib.clone_ext(self.first_repo, self.nonexistent_repo)
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(self.first_repo, self.nonexistent_repo, None)

        with mock.patch("git_wrapper.clone_ext", return_value=(True, None)) as dummy:
            v, r = git_lib.clone_ext(self.first_repo, self.nonexistent_repo, "remotename")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(self.first_repo, self.nonexistent_repo, "remotename")

        with mock.patch("git_wrapper.clone_ext", return_value=(True, None)) as dummy:
            v, r = git_lib.clone_ext(None, self.nonexistent_repo)
            self.assertFalse(v)
            dummy.assert_not_called()

        with mock.patch("git_wrapper.clone_ext", return_value=(True, None)) as dummy:
            v, r = git_lib.clone_ext(self.first_repo, None)
            self.assertFalse(v)
            dummy.assert_not_called()

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)

            first_rel_path = path_utils.concat_path("./", os.path.basename(self.first_repo))
            with mock.patch("git_wrapper.clone_ext", return_value=(True, None)) as dummy:
                v, r = git_lib.clone_ext(first_rel_path, self.nonexistent_repo)
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy.assert_called_with(self.first_repo, self.nonexistent_repo, None)

            nonexistent_rel_path = path_utils.concat_path("./", os.path.basename(self.nonexistent_repo))
            with mock.patch("git_wrapper.clone_ext", return_value=(True, None)) as dummy:
                v, r = git_lib.clone_ext(self.first_repo, nonexistent_rel_path)
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy.assert_called_with(self.first_repo, self.nonexistent_repo, None)

        finally:
            os.chdir(saved_wd)

    def testPullDefault(self):

        with mock.patch("git_wrapper.pull_default", return_value=(True, None)) as dummy:
            v, r = git_lib.pull_default(self.first_repo)
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(self.first_repo)

        with mock.patch("git_wrapper.pull_default", return_value=(True, None)) as dummy:
            v, r = git_lib.pull_default(None)
            self.assertFalse(v)
            dummy.assert_not_called()

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)

            first_rel_path = path_utils.concat_path("./", os.path.basename(self.first_repo))
            with mock.patch("git_wrapper.pull_default", return_value=(True, None)) as dummy:
                v, r = git_lib.pull_default(first_rel_path)
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy.assert_called_with(self.first_repo)

        finally:
            os.chdir(saved_wd)

    def testPull(self):

        with mock.patch("git_wrapper.pull", return_value=(True, None)) as dummy:
            v, r = git_lib.pull(self.first_repo, "remotename", "branchname")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(self.first_repo, "remotename", "branchname")

        with mock.patch("git_wrapper.pull", return_value=(True, None)) as dummy:
            v, r = git_lib.pull(None, "remotename", "branchname")
            self.assertFalse(v)
            dummy.assert_not_called()

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)

            first_rel_path = path_utils.concat_path("./", os.path.basename(self.first_repo))
            with mock.patch("git_wrapper.pull", return_value=(True, None)) as dummy:
                v, r = git_lib.pull(first_rel_path, "remotename", "branchname")
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy.assert_called_with(self.first_repo, "remotename", "branchname")

        finally:
            os.chdir(saved_wd)

    def testPush(self):

        with mock.patch("git_wrapper.push", return_value=(True, None)) as dummy:
            v, r = git_lib.push(self.first_repo, "remotename", "branchname")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(self.first_repo, "remotename", "branchname")

        with mock.patch("git_wrapper.push", return_value=(True, None)) as dummy:
            v, r = git_lib.push(None, "remotename", "branchname")
            self.assertFalse(v)
            dummy.assert_not_called()

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)

            first_rel_path = path_utils.concat_path("./", os.path.basename(self.first_repo))
            with mock.patch("git_wrapper.push", return_value=(True, None)) as dummy:
                v, r = git_lib.push(first_rel_path, "remotename", "branchname")
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy.assert_called_with(self.first_repo, "remotename", "branchname")

        finally:
            os.chdir(saved_wd)

    def testLog(self):

        with mock.patch("git_wrapper.log", return_value=(True, None)) as dummy:
            v, r = git_lib.log(self.first_repo)
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(self.first_repo, None)

        with mock.patch("git_wrapper.log", return_value=(True, None)) as dummy:
            v, r = git_lib.log(self.first_repo, 2112)
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(self.first_repo, 2112)

        with mock.patch("git_wrapper.log", return_value=(True, None)) as dummy:
            v, r = git_lib.log(None)
            self.assertFalse(v)
            dummy.assert_not_called()

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)

            first_rel_path = path_utils.concat_path("./", os.path.basename(self.first_repo))
            with mock.patch("git_wrapper.log", return_value=(True, None)) as dummy:
                v, r = git_lib.log(first_rel_path)
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy.assert_called_with(self.first_repo, None)

        finally:
            os.chdir(saved_wd)

    def testFetchMultiple(self):

        with mock.patch("git_wrapper.fetch_multiple", return_value=(True, None)) as dummy:
            v, r = git_lib.fetch_multiple(self.first_repo, ["remotes"])
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(self.first_repo, ["remotes"])

        with mock.patch("git_wrapper.fetch_multiple", return_value=(True, None)) as dummy:
            v, r = git_lib.fetch_multiple(None, ["remotes"])
            self.assertFalse(v)
            dummy.assert_not_called()

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)

            first_rel_path = path_utils.concat_path("./", os.path.basename(self.first_repo))
            with mock.patch("git_wrapper.fetch_multiple", return_value=(True, None)) as dummy:
                v, r = git_lib.fetch_multiple(first_rel_path, ["remotes"])
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy.assert_called_with(self.first_repo, ["remotes"])

        finally:
            os.chdir(saved_wd)

    def testFetchAll(self):

        with mock.patch("git_wrapper.fetch_all", return_value=(True, None)) as dummy:
            v, r = git_lib.fetch_all(self.first_repo)
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(self.first_repo)

        with mock.patch("git_wrapper.fetch_all", return_value=(True, None)) as dummy:
            v, r = git_lib.fetch_all(None)
            self.assertFalse(v)
            dummy.assert_not_called()

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)

            first_rel_path = path_utils.concat_path("./", os.path.basename(self.first_repo))
            with mock.patch("git_wrapper.fetch_all", return_value=(True, None)) as dummy:
                v, r = git_lib.fetch_all(first_rel_path)
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy.assert_called_with(self.first_repo)

        finally:
            os.chdir(saved_wd)

    def testRevParseHead(self):

        with mock.patch("git_wrapper.rev_parse_head", return_value=(True, None)) as dummy:
            v, r = git_lib.rev_parse_head(self.first_repo)
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(self.first_repo)

        with mock.patch("git_wrapper.rev_parse_head", return_value=(True, None)) as dummy:
            v, r = git_lib.rev_parse_head(None)
            self.assertFalse(v)
            dummy.assert_not_called()

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)

            first_rel_path = path_utils.concat_path("./", os.path.basename(self.first_repo))
            with mock.patch("git_wrapper.rev_parse_head", return_value=(True, None)) as dummy:
                v, r = git_lib.rev_parse_head(first_rel_path)
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy.assert_called_with(self.first_repo)

        finally:
            os.chdir(saved_wd)

    def testCommitEditor(self):

        with mock.patch("git_wrapper.commit_editor", return_value=(True, None)) as dummy:
            v, r = git_lib.commit_editor(self.first_repo)
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(self.first_repo)

        with mock.patch("git_wrapper.commit_editor", return_value=(True, None)) as dummy:
            v, r = git_lib.commit_editor(None)
            self.assertFalse(v)
            dummy.assert_not_called()

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)

            first_rel_path = path_utils.concat_path("./", os.path.basename(self.first_repo))
            with mock.patch("git_wrapper.commit_editor", return_value=(True, None)) as dummy:
                v, r = git_lib.commit_editor(first_rel_path)
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy.assert_called_with(self.first_repo)

        finally:
            os.chdir(saved_wd)

    def testCommitDirect(self):

        with mock.patch("git_wrapper.commit_direct", return_value=(True, None)) as dummy:
            v, r = git_lib.commit_direct(self.first_repo, "the-params")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(self.first_repo, "the-params")

        with mock.patch("git_wrapper.commit_direct", return_value=(True, None)) as dummy:
            v, r = git_lib.commit_direct(None, "the-params")
            self.assertFalse(v)
            dummy.assert_not_called()

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)

            first_rel_path = path_utils.concat_path("./", os.path.basename(self.first_repo))
            with mock.patch("git_wrapper.commit_direct", return_value=(True, None)) as dummy:
                v, r = git_lib.commit_direct(first_rel_path, "the-params")
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy.assert_called_with(self.first_repo, "the-params")

        finally:
            os.chdir(saved_wd)

    def testStatusSimple(self):

        with mock.patch("git_wrapper.status_simple", return_value=(True, None)) as dummy:
            v, r = git_lib.status_simple(self.first_repo)
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(self.first_repo)

        with mock.patch("git_wrapper.status_simple", return_value=(True, None)) as dummy:
            v, r = git_lib.status_simple(None)
            self.assertFalse(v)
            dummy.assert_not_called()

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)

            first_rel_path = path_utils.concat_path("./", os.path.basename(self.first_repo))
            with mock.patch("git_wrapper.status_simple", return_value=(True, None)) as dummy:
                v, r = git_lib.status_simple(first_rel_path)
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy.assert_called_with(self.first_repo)

        finally:
            os.chdir(saved_wd)

    def testShow(self):

        with mock.patch("git_wrapper.show", return_value=(True, None)) as dummy:
            v, r = git_lib.show(self.first_repo, "the-commit-id")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(self.first_repo, "the-commit-id")

        with mock.patch("git_wrapper.show", return_value=(True, None)) as dummy:
            v, r = git_lib.show(None, "the-commit-id")
            self.assertFalse(v)
            dummy.assert_not_called()

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)

            first_rel_path = path_utils.concat_path("./", os.path.basename(self.first_repo))
            with mock.patch("git_wrapper.show", return_value=(True, None)) as dummy:
                v, r = git_lib.show(first_rel_path, "the-commit-id")
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy.assert_called_with(self.first_repo, "the-commit-id")

        finally:
            os.chdir(saved_wd)

    def testStashShow(self):

        with mock.patch("git_wrapper.stash_show", return_value=(True, None)) as dummy:
            v, r = git_lib.stash_show(self.first_repo, "the-stash-name")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(self.first_repo, "the-stash-name")

        with mock.patch("git_wrapper.stash_show", return_value=(True, None)) as dummy:
            v, r = git_lib.stash_show(None, "the-stash-name")
            self.assertFalse(v)
            dummy.assert_not_called()

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)

            first_rel_path = path_utils.concat_path("./", os.path.basename(self.first_repo))
            with mock.patch("git_wrapper.stash_show", return_value=(True, None)) as dummy:
                v, r = git_lib.stash_show(first_rel_path, "the-stash-name")
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy.assert_called_with(self.first_repo, "the-stash-name")

        finally:
            os.chdir(saved_wd)

    def testStashShowDiff(self):

        with mock.patch("git_wrapper.stash_show_diff", return_value=(True, None)) as dummy:
            v, r = git_lib.stash_show_diff(self.first_repo, "the-stash-name")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(self.first_repo, "the-stash-name")

        with mock.patch("git_wrapper.stash_show_diff", return_value=(True, None)) as dummy:
            v, r = git_lib.stash_show_diff(None, "the-stash-name")
            self.assertFalse(v)
            dummy.assert_not_called()

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)

            first_rel_path = path_utils.concat_path("./", os.path.basename(self.first_repo))
            with mock.patch("git_wrapper.stash_show_diff", return_value=(True, None)) as dummy:
                v, r = git_lib.stash_show_diff(first_rel_path, "the-stash-name")
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy.assert_called_with(self.first_repo, "the-stash-name")

        finally:
            os.chdir(saved_wd)

    def testStashClear(self):

        with mock.patch("git_wrapper.stash_clear", return_value=(True, None)) as dummy:
            v, r = git_lib.stash_clear(self.first_repo)
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(self.first_repo)

        with mock.patch("git_wrapper.stash_clear", return_value=(True, None)) as dummy:
            v, r = git_lib.stash_clear(None)
            self.assertFalse(v)
            dummy.assert_not_called()

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)

            first_rel_path = path_utils.concat_path("./", os.path.basename(self.first_repo))
            with mock.patch("git_wrapper.stash_clear", return_value=(True, None)) as dummy:
                v, r = git_lib.stash_clear(first_rel_path)
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy.assert_called_with(self.first_repo)

        finally:
            os.chdir(saved_wd)

    def testStashDrop(self):

        with mock.patch("git_wrapper.stash_drop", return_value=(True, None)) as dummy:
            v, r = git_lib.stash_drop(self.first_repo)
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(self.first_repo, None)

        with mock.patch("git_wrapper.stash_drop", return_value=(True, None)) as dummy:
            v, r = git_lib.stash_drop(None)
            self.assertFalse(v)
            dummy.assert_not_called()

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)

            first_rel_path = path_utils.concat_path("./", os.path.basename(self.first_repo))
            with mock.patch("git_wrapper.stash_drop", return_value=(True, None)) as dummy:
                v, r = git_lib.stash_drop(first_rel_path)
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy.assert_called_with(self.first_repo, None)

        finally:
            os.chdir(saved_wd)

    def testStashPop(self):

        with mock.patch("git_wrapper.stash_pop", return_value=(True, None)) as dummy:
            v, r = git_lib.stash_pop(self.first_repo)
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(self.first_repo)

        with mock.patch("git_wrapper.stash_pop", return_value=(True, None)) as dummy:
            v, r = git_lib.stash_pop(None)
            self.assertFalse(v)
            dummy.assert_not_called()

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)

            first_rel_path = path_utils.concat_path("./", os.path.basename(self.first_repo))
            with mock.patch("git_wrapper.stash_pop", return_value=(True, None)) as dummy:
                v, r = git_lib.stash_pop(first_rel_path)
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy.assert_called_with(self.first_repo)

        finally:
            os.chdir(saved_wd)

    def testRemoteChangeUrl(self):

        with mock.patch("git_wrapper.remote_change_url", return_value=(True, None)) as dummy:
            v, r = git_lib.remote_change_url(self.first_repo, "remotename", "new-url")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(self.first_repo, "remotename", "new-url")

        with mock.patch("git_wrapper.remote_change_url", return_value=(True, None)) as dummy:
            v, r = git_lib.remote_change_url(None, "remotename", "new-url")
            self.assertFalse(v)
            dummy.assert_not_called()

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)

            first_rel_path = path_utils.concat_path("./", os.path.basename(self.first_repo))
            with mock.patch("git_wrapper.remote_change_url", return_value=(True, None)) as dummy:
                v, r = git_lib.remote_change_url(first_rel_path, "remotename", "new-url")
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy.assert_called_with(self.first_repo, "remotename", "new-url")

        finally:
            os.chdir(saved_wd)

    def testConfig(self):

        with mock.patch("git_wrapper.config", return_value=(True, None)) as dummy:
            v, r = git_lib.config("the-key", "the-value")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with("the-key", "the-value", True)

        with mock.patch("git_wrapper.config", return_value=(True, None)) as dummy:
            v, r = git_lib.config("the-key", "the-value", False)
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with("the-key", "the-value", False)

        with mock.patch("git_wrapper.config", return_value=(True, None)) as dummy:
            v, r = git_lib.config(None, "the-value")
            self.assertFalse(v)
            dummy.assert_not_called()

    def testCheckout(self):

        with mock.patch("git_wrapper.checkout", return_value=(True, None)) as dummy:
            v, r = git_lib.checkout(self.first_repo, [self.first_file1])
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(self.first_repo, [self.first_file1])

        with mock.patch("git_wrapper.checkout", return_value=(True, None)) as dummy:
            v, r = git_lib.checkout(self.first_repo)
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(self.first_repo, None)

        with mock.patch("git_wrapper.checkout", return_value=(True, None)) as dummy:
            v, r = git_lib.checkout(None, [self.first_file1])
            self.assertFalse(v)
            dummy.assert_not_called()

        with mock.patch("git_wrapper.checkout", return_value=(True, None)) as dummy:
            v, r = git_lib.checkout(None, 123)
            self.assertFalse(v)
            dummy.assert_not_called()

        with mock.patch("git_wrapper.checkout", return_value=(True, None)) as dummy:
            v, r = git_lib.checkout(self.first_repo, self.first_file1)
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(self.first_repo, [self.first_file1])

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            first_rel_path = path_utils.concat_path("./", os.path.basename(self.first_repo))
            first_file1_rel_path = path_utils.concat_path("./", os.path.basename(self.first_repo), os.path.basename(self.first_file1))

            with mock.patch("git_wrapper.checkout", return_value=(True, None)) as dummy:
                v, r = git_lib.checkout(first_rel_path)
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy.assert_called_with(self.first_repo, None)

            with mock.patch("git_wrapper.checkout", return_value=(True, None)) as dummy:
                v, r = git_lib.checkout(self.first_repo, [first_file1_rel_path])
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy.assert_called_with(self.first_repo, [self.first_file1])

            with mock.patch("git_wrapper.checkout", return_value=(True, None)) as dummy:
                v, r = git_lib.checkout(self.first_repo, first_file1_rel_path)
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy.assert_called_with(self.first_repo, [self.first_file1])

        finally:
            os.chdir(saved_wd)

    def testDiff(self):

        with mock.patch("git_wrapper.diff", return_value=(True, None)) as dummy:
            v, r = git_lib.diff(self.first_repo, [self.first_file1])
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(self.first_repo, [self.first_file1])

        with mock.patch("git_wrapper.diff", return_value=(True, None)) as dummy:
            v, r = git_lib.diff(self.first_repo)
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(self.first_repo, None)

        with mock.patch("git_wrapper.diff", return_value=(True, None)) as dummy:
            v, r = git_lib.diff(None, [self.first_file1])
            self.assertFalse(v)
            dummy.assert_not_called()

        with mock.patch("git_wrapper.diff", return_value=(True, None)) as dummy:
            v, r = git_lib.diff(None, 123)
            self.assertFalse(v)
            dummy.assert_not_called()

        with mock.patch("git_wrapper.diff", return_value=(True, None)) as dummy:
            v, r = git_lib.diff(self.first_repo, self.first_file1)
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(self.first_repo, [self.first_file1])

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            first_rel_path = path_utils.concat_path("./", os.path.basename(self.first_repo))
            first_file1_rel_path = path_utils.concat_path("./", os.path.basename(self.first_repo), os.path.basename(self.first_file1))

            with mock.patch("git_wrapper.diff", return_value=(True, None)) as dummy:
                v, r = git_lib.diff(first_rel_path)
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy.assert_called_with(self.first_repo, None)

            with mock.patch("git_wrapper.diff", return_value=(True, None)) as dummy:
                v, r = git_lib.diff(self.first_repo, [first_file1_rel_path])
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy.assert_called_with(self.first_repo, [self.first_file1])

            with mock.patch("git_wrapper.diff", return_value=(True, None)) as dummy:
                v, r = git_lib.diff(self.first_repo, first_file1_rel_path)
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy.assert_called_with(self.first_repo, [self.first_file1])

        finally:
            os.chdir(saved_wd)

    def testDiffIndexed(self):

        with mock.patch("git_wrapper.diff_indexed", return_value=(True, None)) as dummy:
            v, r = git_lib.diff_indexed(self.first_repo, [self.first_file1])
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(self.first_repo, [self.first_file1])

        with mock.patch("git_wrapper.diff_indexed", return_value=(True, None)) as dummy:
            v, r = git_lib.diff_indexed(None, [self.first_file1])
            self.assertFalse(v)
            dummy.assert_not_called()

        with mock.patch("git_wrapper.diff_indexed", return_value=(True, None)) as dummy:
            v, r = git_lib.diff_indexed(None, 123)
            self.assertFalse(v)
            dummy.assert_not_called()

        with mock.patch("git_wrapper.diff_indexed", return_value=(True, None)) as dummy:
            v, r = git_lib.diff_indexed(self.first_repo, self.first_file1)
            self.assertFalse(v)
            dummy.assert_not_called()

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            first_rel_path = path_utils.concat_path("./", os.path.basename(self.first_repo))
            first_file1_rel_path = path_utils.concat_path("./", os.path.basename(self.first_repo), os.path.basename(self.first_file1))

            with mock.patch("git_wrapper.diff_indexed", return_value=(True, None)) as dummy:
                v, r = git_lib.diff_indexed(first_rel_path, [self.first_file1])
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy.assert_called_with(self.first_repo, [self.first_file1])

            with mock.patch("git_wrapper.diff_indexed", return_value=(True, None)) as dummy:
                v, r = git_lib.diff_indexed(self.first_repo, [first_file1_rel_path])
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy.assert_called_with(self.first_repo, [self.first_file1])

        finally:
            os.chdir(saved_wd)

    def testDiffCached(self):

        with mock.patch("git_wrapper.diff_cached", return_value=(True, None)) as dummy:
            v, r = git_lib.diff_cached(self.first_repo, [self.first_file1])
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(self.first_repo, [self.first_file1])

        with mock.patch("git_wrapper.diff_cached", return_value=(True, None)) as dummy:
            v, r = git_lib.diff_cached(self.first_repo)
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(self.first_repo, None)

        with mock.patch("git_wrapper.diff_cached", return_value=(True, None)) as dummy:
            v, r = git_lib.diff_cached(None, [self.first_file1])
            self.assertFalse(v)
            dummy.assert_not_called()

        with mock.patch("git_wrapper.diff_cached", return_value=(True, None)) as dummy:
            v, r = git_lib.diff_cached(None, 123)
            self.assertFalse(v)
            dummy.assert_not_called()

        with mock.patch("git_wrapper.diff_cached", return_value=(True, None)) as dummy:
            v, r = git_lib.diff_cached(self.first_repo, self.first_file1)
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(self.first_repo, [self.first_file1])

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            first_rel_path = path_utils.concat_path("./", os.path.basename(self.first_repo))
            first_file1_rel_path = path_utils.concat_path("./", os.path.basename(self.first_repo), os.path.basename(self.first_file1))

            with mock.patch("git_wrapper.diff_cached", return_value=(True, None)) as dummy:
                v, r = git_lib.diff_cached(first_rel_path)
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy.assert_called_with(self.first_repo, None)

            with mock.patch("git_wrapper.diff_cached", return_value=(True, None)) as dummy:
                v, r = git_lib.diff_cached(self.first_repo, [first_file1_rel_path])
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy.assert_called_with(self.first_repo, [self.first_file1])

            with mock.patch("git_wrapper.diff_cached", return_value=(True, None)) as dummy:
                v, r = git_lib.diff_cached(self.first_repo, first_file1_rel_path)
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy.assert_called_with(self.first_repo, [self.first_file1])

        finally:
            os.chdir(saved_wd)

    def testDiffCachedIndexed(self):

        with mock.patch("git_wrapper.diff_cached_indexed", return_value=(True, None)) as dummy:
            v, r = git_lib.diff_cached_indexed(self.first_repo, [self.first_file1])
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(self.first_repo, [self.first_file1])

        with mock.patch("git_wrapper.diff_cached_indexed", return_value=(True, None)) as dummy:
            v, r = git_lib.diff_cached_indexed(self.first_repo)
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(self.first_repo, None)

        with mock.patch("git_wrapper.diff_cached_indexed", return_value=(True, None)) as dummy:
            v, r = git_lib.diff_cached_indexed(None, [self.first_file1])
            self.assertFalse(v)
            dummy.assert_not_called()

        with mock.patch("git_wrapper.diff_cached_indexed", return_value=(True, None)) as dummy:
            v, r = git_lib.diff_cached_indexed(None, 123)
            self.assertFalse(v)
            dummy.assert_not_called()

        with mock.patch("git_wrapper.diff_cached_indexed", return_value=(True, None)) as dummy:
            v, r = git_lib.diff_cached_indexed(self.first_repo, self.first_file1)
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(self.first_repo, [self.first_file1])

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            first_rel_path = path_utils.concat_path("./", os.path.basename(self.first_repo))
            first_file1_rel_path = path_utils.concat_path("./", os.path.basename(self.first_repo), os.path.basename(self.first_file1))

            with mock.patch("git_wrapper.diff_cached_indexed", return_value=(True, None)) as dummy:
                v, r = git_lib.diff_cached_indexed(first_rel_path)
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy.assert_called_with(self.first_repo, None)

            with mock.patch("git_wrapper.diff_cached_indexed", return_value=(True, None)) as dummy:
                v, r = git_lib.diff_cached_indexed(self.first_repo, [first_file1_rel_path])
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy.assert_called_with(self.first_repo, [self.first_file1])

            with mock.patch("git_wrapper.diff_cached_indexed", return_value=(True, None)) as dummy:
                v, r = git_lib.diff_cached_indexed(self.first_repo, first_file1_rel_path)
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy.assert_called_with(self.first_repo, [self.first_file1])

        finally:
            os.chdir(saved_wd)

    def testKillPrevious(self):

        with mock.patch("git_wrapper.reset_hard_head", return_value=(True, None)) as dummy:
            v, r = git_lib.kill_previous(self.first_repo, 1)
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(self.first_repo, 1)

        with mock.patch("git_wrapper.reset_hard_head", return_value=(True, None)) as dummy:
            v, r = git_lib.kill_previous(None, 1)
            self.assertFalse(v)
            dummy.assert_not_called()

        with mock.patch("git_wrapper.reset_hard_head", return_value=(True, None)) as dummy:
            v, r = git_lib.kill_previous(self.first_repo, None)
            self.assertFalse(v)
            dummy.assert_not_called()

        saved_wd = os.getcwd()
        try:
            os.chdir(self.test_dir)

            first_rel_path = path_utils.concat_path("./", os.path.basename(self.first_repo))
            with mock.patch("git_wrapper.reset_hard_head", return_value=(True, None)) as dummy:
                v, r = git_lib.kill_previous(first_rel_path, 1)
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy.assert_called_with(self.first_repo, 1)

        finally:
            os.chdir(saved_wd)

if __name__ == '__main__':
    unittest.main()
