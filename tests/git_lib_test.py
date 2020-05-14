#!/usr/bin/env python3

import sys
import os
import shutil
import unittest

import git_test_fixture
import git_wrapper
import path_utils
import git_lib
import mvtools_test_fixture
import create_and_write_file

class GitLibTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("git_lib_test_base")
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

    def testHelperFunctions(self):
        self.assertEqual(git_lib.get_stash_name("stash@{0}: WIP on master: a44cc87 upd"), "stash@{0}")
        self.assertEqual(git_lib.get_stash_name(""), None)
        self.assertEqual(git_lib.get_stash_name(None), None)

        self.assertEqual(git_lib.get_prev_hash("a44cc87 (HEAD -> master) upd"), "a44cc87")
        self.assertEqual(git_lib.get_prev_hash(""), None)
        self.assertEqual(git_lib.get_prev_hash(None), None)

    def testIsGitWorkTree(self):
        self.assertTrue(git_lib.is_git_work_tree(self.first_repo))
        self.assertFalse(git_lib.is_git_work_tree(self.fourth_notrepo))

    def testGetRemotes(self):

        self.assertEqual(git_lib.get_remotes(self.fourth_notrepo), None)

        v, r = git_wrapper.remote_add(self.first_repo, "latest-addition", self.third_repo)
        if not v:
            self.fail(r)

        ret = git_lib.get_remotes(self.first_repo)
        self.assertEqual(self.second_repo, ret["origin"]["fetch"])
        self.assertEqual(self.third_repo, ret["latest-addition"]["fetch"])

        v, r = git_wrapper.remote_add(self.first_repo, "latest-addition", self.third_repo)
        self.assertFalse(v) # disallow duplicates

        v, r = git_wrapper.remote_add(self.first_repo, "リモート", self.third_repo)
        if not v:
            self.fail(r)

        ret = git_lib.get_remotes(self.first_repo)
        self.assertEqual(self.third_repo, ret["リモート"]["fetch"])

    def testGetBranches(self):

        self.assertEqual(git_lib.get_branches(self.fifth_repo), None)
        self.assertEqual(git_lib.get_branches(self.fourth_notrepo), None)

        ret = git_lib.get_branches(self.first_repo)
        self.assertEqual(len(ret), 1)
        self.assertEqual(ret[0], "master")

        v, r = git_wrapper.branch_create_and_switch(self.first_repo, "new-branch")
        if not v:
            self.fail(r)

        ret = git_lib.get_branches(self.first_repo)
        self.assertEqual(len(ret), 2)
        self.assertTrue("master" in ret)
        self.assertTrue("new-branch" in ret)

        v, r = git_wrapper.branch_create_and_switch(self.first_repo, "ブランチ")
        if not v:
            self.fail(r)

        self.assertTrue("ブランチ" in git_lib.get_branches(self.first_repo))

    def testGetCurrentBranch(self):

        self.assertEqual(git_lib.get_current_branch(self.fifth_repo), None)
        self.assertEqual(git_lib.get_current_branch(self.fourth_notrepo), None)

        self.assertEqual(git_lib.get_current_branch(self.first_repo), "master")

        v, r = git_wrapper.branch_create_and_switch(self.first_repo, "another-branch")
        if not v:
            self.fail(r)

        self.assertEqual(git_lib.get_current_branch(self.first_repo), "another-branch")

    def testGetStagedFiles(self):

        self.assertEqual(git_lib.get_staged_files(self.fourth_notrepo), None)

        self.assertEqual(git_lib.get_staged_files(self.first_repo), "")

        first_more1 = path_utils.concat_path(self.first_repo, "more1.txt")
        if not create_and_write_file.create_file_contents(first_more1, "more1-contents"):
            self.fail("Failed creating file %s" % first_more1)

        first_more2 = path_utils.concat_path(self.first_repo, "more2.txt")
        if not create_and_write_file.create_file_contents(first_more2, "more2-contents"):
            self.fail("Failed creating file %s" % first_more2)

        first_more3 = path_utils.concat_path(self.first_repo, "more3.txt")
        if not create_and_write_file.create_file_contents(first_more3, "more3-contents"):
            self.fail("Failed creating file %s" % first_more3)

        first_more4 = path_utils.concat_path(self.first_repo, "more4.txt")
        if not create_and_write_file.create_file_contents(first_more4, "more4-contents"):
            self.fail("Failed creating file %s" % first_more4)

        first_more5 = path_utils.concat_path(self.first_repo, "アーカイブ.txt")
        if not create_and_write_file.create_file_contents(first_more5, "アーカイブ-contents"):
            self.fail("Failed creating file %s" % first_more5)

        v, r = git_wrapper.stage(self.first_repo, [first_more1])
        if not v:
            self.fail(r)

        self.assertEqual(git_lib.get_staged_files(self.first_repo), [first_more1])

        v, r = git_wrapper.stage(self.first_repo, [first_more2, first_more3])
        if not v:
            self.fail(r)

        ret = git_lib.get_staged_files(self.first_repo)
        self.assertEqual(len(ret), 3)
        self.assertTrue(first_more1 in ret)
        self.assertTrue(first_more2 in ret)
        self.assertTrue(first_more3 in ret)

        v, r = git_wrapper.stage(self.first_repo, None)
        if not v:
            self.fail(r)

        ret = git_lib.get_staged_files(self.first_repo)

        self.assertEqual(len(ret), 5)
        self.assertTrue(first_more1 in ret)
        self.assertTrue(first_more2 in ret)
        self.assertTrue(first_more3 in ret)
        self.assertTrue(first_more4 in ret)
        #self.assertTrue(first_more5 in ret) # mvtodo: might require extra system config or ...

    def testGetUnstagedFiles(self):

        self.assertEqual(git_lib.get_unstaged_files(self.fourth_notrepo), None)

        self.assertEqual(git_lib.get_unstaged_files(self.first_repo), "")

        first_more1 = path_utils.concat_path(self.first_repo, "more1.txt")
        if not create_and_write_file.create_file_contents(first_more1, "more1-contents"):
            self.fail("Failed creating file %s" % first_more1)

        first_more2 = path_utils.concat_path(self.first_repo, "more2.txt")
        if not create_and_write_file.create_file_contents(first_more2, "more2-contents"):
            self.fail("Failed creating file %s" % first_more2)

        first_more3 = path_utils.concat_path(self.first_repo, "アーカイブ.txt")
        if not create_and_write_file.create_file_contents(first_more3, "more3-contents"):
            self.fail("Failed creating file %s" % first_more3)

        ret = git_lib.get_unstaged_files(self.first_repo)
        self.assertEqual(len(ret), 3)
        self.assertTrue(first_more1 in ret)
        self.assertTrue(first_more2 in ret)
        #self.assertTrue(first_more3 in ret) # mvtodo: might require extra system config or ...

        v, r = git_wrapper.stage(self.first_repo, [first_more1])
        if not v:
            self.fail(r)

        ret = git_lib.get_unstaged_files(self.first_repo)
        self.assertEqual(len(ret), 2)
        self.assertTrue(first_more2 in ret)
        #self.assertTrue(first_more3 in ret) # mvtodo: might require extra system config or ...

    def testRemoveGitlogDecorations(self):

        self.first_file = path_utils.concat_path(self.first_repo, "file.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, path_utils.basename_filtered(self.first_file), "file1-content", "commit_msg_file")
        if not v:
            self.fail(r)

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

    def testDiscoverRepoRoot(self):

        folder1 = path_utils.concat_path(self.first_repo, "folder1")
        os.mkdir(folder1)

        self.first_folder1_file2 = path_utils.concat_path(folder1, "file2.txt")
        v, r = git_test_fixture.git_createAndCommit(folder1, path_utils.basename_filtered(self.first_folder1_file2), "file2-content", "commit_msg_file-2")
        if not v:
            self.fail(r)

        folder2 = path_utils.concat_path(folder1, "folder2")
        os.mkdir(folder2)

        folder3 = path_utils.concat_path(self.first_repo, "one", "two", "three")
        path_utils.guaranteefolder(folder3)

        self.assertEqual(git_lib.discover_repo_root(self.first_repo), self.first_repo)
        self.assertEqual(git_lib.discover_repo_root(self.nonexistent_repo), None)
        self.assertEqual(git_lib.discover_repo_root(self.nonexistent_repo), None)
        self.assertEqual(git_lib.discover_repo_root(folder1), self.first_repo)
        self.assertEqual(git_lib.discover_repo_root(folder2), self.first_repo)
        self.assertEqual(git_lib.discover_repo_root(folder3), self.first_repo)

if __name__ == '__main__':
    unittest.main()
