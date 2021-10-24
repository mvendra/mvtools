#!/usr/bin/env python3

import sys
import os
import shutil
import unittest
from unittest import mock
from unittest.mock import patch

import mvtools_test_fixture
import git_test_fixture
import path_utils

import git_plugin

import git_wrapper
import git_lib

import port_git_repo
import reset_git_repo
import apply_git_patch

class AnyStringWith:
    def __init__(self, the_str):
        self.the_str = the_str
    def __eq__(self, other):
        return self.the_str in other

class GitPluginTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("git_plugin_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # the test task
        self.git_task = git_plugin.CustomTask()

        # existent path 1
        self.existent_path1 = path_utils.concat_path(self.test_dir, "existent_path1")
        os.mkdir(self.existent_path1)

        # existent path 2
        self.existent_path2 = path_utils.concat_path(self.test_dir, "existent_path2")
        os.mkdir(self.existent_path2)

        # nonexistent path 1
        self.nonexistent_path1 = path_utils.concat_path(self.test_dir, "nonexistent_path1")

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testGitPluginReadParams1(self):

        local_params = {}
        self.git_task.params = local_params

        v, r = self.git_task._read_params()
        self.assertFalse(v)

    def testGitPluginReadParams2(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        self.git_task.params = local_params

        v, r = self.git_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", None, None, None, None, False, False, None, False, None, False, False, None, False, None, None, None, None, None, None, None, False) )

    def testGitPluginReadParams3(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        local_params["source_url"] = "dummy_value3"
        self.git_task.params = local_params

        v, r = self.git_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", "dummy_value3", None, None, None, False, False, None, False, None, False, False, None, False, None, None, None, None, None, None, None, False) )

    def testGitPluginReadParams4(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        local_params["remote_name"] = "dummy_value3"
        self.git_task.params = local_params

        v, r = self.git_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", None, "dummy_value3", None, None, False, False, None, False, None, False, False, None, False, None, None, None, None, None, None, None, False) )

    def testGitPluginReadParams5(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        local_params["branch_name"] = "dummy_value3"
        self.git_task.params = local_params

        v, r = self.git_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", None, None, "dummy_value3", None, False, False, None, False, None, False, False, None, False, None, None, None, None, None, None, None, False) )

    def testGitPluginReadParams6(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        local_params["source_path"] = "dummy_value3"
        self.git_task.params = local_params

        v, r = self.git_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", None, None, None, "dummy_value3", False, False, None, False, None, False, False, None, False, None, None, None, None, None, None, None, False) )

    def testGitPluginReadParams7(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        local_params["port_repo_head"] = "dummy_value3"
        self.git_task.params = local_params

        v, r = self.git_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", None, None, None, None, True, False, None, False, None, False, False, None, False, None, None, None, None, None, None, None, False) )

    def testGitPluginReadParams8(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        local_params["port_repo_staged"] = "dummy_value3"
        self.git_task.params = local_params

        v, r = self.git_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", None, None, None, None, False, True, None, False, None, False, False, None, False, None, None, None, None, None, None, None, False) )

    def testGitPluginReadParams9(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        local_params["port_repo_stash_count"] = "dummy_value3"
        self.git_task.params = local_params

        v, r = self.git_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", None, None, None, None, False, False, "dummy_value3", False, None, False, False, None, False, None, None, None, None, None, None, None, False) )

    def testGitPluginReadParams10(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        local_params["port_repo_unversioned"] = "dummy_value3"
        self.git_task.params = local_params

        v, r = self.git_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", None, None, None, None, False, False, None, True, None, False, False, None, False, None, None, None, None, None, None, None, False) )

    def testGitPluginReadParams11(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        local_params["port_repo_previous_count"] = "dummy_value3"
        self.git_task.params = local_params

        v, r = self.git_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", None, None, None, None, False, False, None, False, "dummy_value3", False, False, None, False, None, None, None, None, None, None, None, False) )

    def testGitPluginReadParams12(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        local_params["reset_head"] = "dummy_value3"
        self.git_task.params = local_params

        v, r = self.git_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", None, None, None, None, False, False, None, False, None, True, False, None, False, None, None, None, None, None, None, None, False) )

    def testGitPluginReadParams13(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        local_params["reset_staged"] = "dummy_value3"
        self.git_task.params = local_params

        v, r = self.git_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", None, None, None, None, False, False, None, False, None, False, True, None, False, None, None, None, None, None, None, None, False) )

    def testGitPluginReadParams14(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        local_params["reset_stash_count"] = "dummy_value3"
        self.git_task.params = local_params

        v, r = self.git_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", None, None, None, None, False, False, None, False, None, False, False, "dummy_value3", False, None, None, None, None, None, None, None, False) )

    def testGitPluginReadParams15(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        local_params["reset_unversioned"] = "dummy_value3"
        self.git_task.params = local_params

        v, r = self.git_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", None, None, None, None, False, False, None, False, None, False, False, None, True, None, None, None, None, None, None, None, False) )

    def testGitPluginReadParams16(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        local_params["reset_previous_count"] = "dummy_value3"
        self.git_task.params = local_params

        v, r = self.git_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", None, None, None, None, False, False, None, False, None, False, False, None, False, "dummy_value3", None, None, None, None, None, None, False) )

    def testGitPluginReadParams17(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        local_params["patch_head_file"] = "dummy_value3"
        self.git_task.params = local_params

        v, r = self.git_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", None, None, None, None, False, False, None, False, None, False, False, None, False, None, "dummy_value3", None, None, None, None, None, False) )

    def testGitPluginReadParams18(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        local_params["patch_staged_file"] = "dummy_value3"
        self.git_task.params = local_params

        v, r = self.git_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", None, None, None, None, False, False, None, False, None, False, False, None, False, None, None, "dummy_value3", None, None, None, None, False) )

    def testGitPluginReadParams19(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        local_params["patch_stash_file"] = "dummy_value3"
        self.git_task.params = local_params

        v, r = self.git_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", None, None, None, None, False, False, None, False, None, False, False, None, False, None, None, None, "dummy_value3", None, None, None, False) )

    def testGitPluginReadParams20(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        local_params["patch_unversioned_base"] = "dummy_value3"
        self.git_task.params = local_params

        v, r = self.git_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", None, None, None, None, False, False, None, False, None, False, False, None, False, None, None, None, None, "dummy_value3", None, None, False) )

    def testGitPluginReadParams21(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        local_params["patch_unversioned_file"] = "dummy_value3"
        self.git_task.params = local_params

        v, r = self.git_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", None, None, None, None, False, False, None, False, None, False, False, None, False, None, None, None, None, None, "dummy_value3", None, False) )

    def testGitPluginReadParams22(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        local_params["rewind_to_hash"] = "dummy_value3"
        self.git_task.params = local_params

        v, r = self.git_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", None, None, None, None, False, False, None, False, None, False, False, None, False, None, None, None, None, None, None, "dummy_value3", False) )

    def testGitPluginReadParams23(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        local_params["rewind_like_source"] = "dummy_value3"
        self.git_task.params = local_params

        v, r = self.git_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", None, None, None, None, False, False, None, False, None, False, False, None, False, None, None, None, None, None, None, None, True) )

    def testGitPluginTaskCloneRepo1(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        with mock.patch("git_wrapper.clone_ext", return_value=(True, (True, "", ""))):
            with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value=None) as dummy:
                v, r = self.git_task.task_clone_repo(print, None, self.existent_path1, "dummy_value4")
                self.assertFalse(v)
                dummy.assert_not_called()

    def testGitPluginTaskCloneRepo2(self):

        self.assertFalse(os.path.exists(self.nonexistent_path1))

        with mock.patch("git_wrapper.clone_ext", return_value=(True, (True, "", ""))) as dummy1:
            with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value=None) as dummy2:
                v, r = self.git_task.task_clone_repo(print, "dummy_value3", self.nonexistent_path1, "dummy_value4")
                self.assertTrue(v)
                dummy1.assert_called_with(AnyStringWith("dummy_value3"), self.nonexistent_path1, "dummy_value4")
                out_list = [("git_plugin_stdout", "", "Git's stdout"), ("git_plugin_stderr", "", "Git's stderr")]
                dummy2.assert_called_with(True, print, out_list)

    def testGitPluginTaskCloneRepo3(self):

        self.assertFalse(os.path.exists(self.nonexistent_path1))

        with mock.patch("git_wrapper.clone_ext", return_value=(True, (False, "test-stdout", "test-stderr"))) as dummy1:
            with mock.patch("output_backup_helper.dump_outputs_autobackup", return_value=None) as dummy2:
                v, r = self.git_task.task_clone_repo(print, "dummy_value3", self.nonexistent_path1, "dummy_value4")
                self.assertFalse(v)
                dummy1.assert_called_with(AnyStringWith("dummy_value3"), self.nonexistent_path1, "dummy_value4")
                out_list = [("git_plugin_stdout", "test-stdout", "Git's stdout"), ("git_plugin_stderr", "test-stderr", "Git's stderr")]
                dummy2.assert_called_with(False, print, out_list)

    def testGitPluginTaskPullRepo1(self):

        self.assertFalse(os.path.exists(self.nonexistent_path1))

        with mock.patch("git_wrapper.pull_default", return_value=(True, None)):
            v, r = self.git_task.task_pull_repo(print, self.nonexistent_path1, None, None)
            self.assertFalse(v)

    def testGitPluginTaskPullRepo2(self):

        self.assertTrue(os.path.exists(self.existent_path1))
        valid_branch_name = "master"

        with mock.patch("git_wrapper.pull", return_value=(True, None)):
            v, r = self.git_task.task_pull_repo(print, self.existent_path1, None, valid_branch_name)
            self.assertFalse(v)

    def testGitPluginTaskPullRepo3(self):

        self.assertTrue(os.path.exists(self.existent_path1))
        valid_remote_name = "origin"

        with mock.patch("git_wrapper.pull", return_value=(True, None)):
            v, r = self.git_task.task_pull_repo(print, self.existent_path1, valid_remote_name, None)
            self.assertFalse(v)

    def testGitPluginTaskPullRepo4(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        with mock.patch("git_wrapper.pull_default", return_value=(True, None)) as dummy:
            v, r = self.git_task.task_pull_repo(print, self.existent_path1, None, None)
            self.assertTrue(v)
            dummy.assert_called_with(self.existent_path1)

    def testGitPluginTaskPullRepo5(self):

        self.assertTrue(os.path.exists(self.existent_path1))
        valid_remote_name = "origin"
        valid_branch_name = "master"

        with mock.patch("git_wrapper.pull", return_value=(True, None)) as dummy:
            v, r = self.git_task.task_pull_repo(print, self.existent_path1, valid_remote_name, valid_branch_name)
            self.assertTrue(v)
            dummy.assert_called_with(self.existent_path1, valid_remote_name, valid_branch_name)

    def testGitPluginTaskPortRepo1(self):

        self.assertTrue(os.path.exists(self.existent_path1))
        prev_count = "0"

        with mock.patch("port_git_repo.port_git_repo", return_value=(True, None)) as dummy:
            v, r = self.git_task.task_port_repo(print, None, self.existent_path1, False, False, False, False, prev_count)
            self.assertFalse(v)

    def testGitPluginTaskPortRepo2(self):

        self.assertFalse(os.path.exists(self.nonexistent_path1))
        self.assertTrue(os.path.exists(self.existent_path1))
        prev_count = "0"

        with mock.patch("port_git_repo.port_git_repo", return_value=(True, None)) as dummy:
            v, r = self.git_task.task_port_repo(print, self.nonexistent_path1, self.existent_path1, False, False, False, False, prev_count)
            self.assertFalse(v)

    def testGitPluginTaskPortRepo3(self):

        self.assertFalse(os.path.exists(self.nonexistent_path1))
        self.assertTrue(os.path.exists(self.existent_path1))
        prev_count = "0"

        with mock.patch("port_git_repo.port_git_repo", return_value=(True, None)) as dummy:
            v, r = self.git_task.task_port_repo(print, self.existent_path1, self.nonexistent_path1, False, False, False, False, prev_count)
            self.assertFalse(v)

    def testGitPluginTaskPortRepo4(self):

        self.assertTrue(os.path.exists(self.existent_path1))
        self.assertTrue(os.path.exists(self.existent_path2))
        prev_count = "a"

        with mock.patch("port_git_repo.port_git_repo", return_value=(True, None)) as dummy:
            v, r = self.git_task.task_port_repo(print, self.existent_path1, self.existent_path2, False, False, None, False, prev_count)
            self.assertFalse(v)

    def testGitPluginTaskPortRepo5(self):

        self.assertTrue(os.path.exists(self.existent_path1))
        self.assertTrue(os.path.exists(self.existent_path2))

        local_port_repo_head = False
        local_port_repo_staged = False
        local_port_repo_stash_count = "0"
        local_port_repo_unversioned = False
        local_prev_count = "0"

        with mock.patch("port_git_repo.port_git_repo", return_value=(True, None)) as dummy:
            v, r = self.git_task.task_port_repo(print, self.existent_path1, self.existent_path2, local_port_repo_head, local_port_repo_staged, local_port_repo_stash_count, local_port_repo_unversioned, local_prev_count)
            self.assertTrue(v)
            dummy.assert_called_with(self.existent_path1, self.existent_path2, False, False, 0, False, 0)

    def testGitPluginTaskPortRepo6(self):

        self.assertTrue(os.path.exists(self.existent_path1))
        self.assertTrue(os.path.exists(self.existent_path2))

        local_port_repo_head = True
        local_port_repo_staged = True
        local_port_repo_stash_count = "7"
        local_port_repo_unversioned = True
        local_prev_count = "5"

        with mock.patch("port_git_repo.port_git_repo", return_value=(True, None)) as dummy:
            v, r = self.git_task.task_port_repo(print, self.existent_path1, self.existent_path2, local_port_repo_head, local_port_repo_staged, local_port_repo_stash_count, local_port_repo_unversioned, local_prev_count)
            self.assertTrue(v)
            dummy.assert_called_with(self.existent_path1, self.existent_path2, True, True, 7, True, 5)

    def testGitPluginTaskPortRepo7(self):

        self.assertTrue(os.path.exists(self.existent_path1))
        self.assertTrue(os.path.exists(self.existent_path2))
        stash_count = "z"

        with mock.patch("port_git_repo.port_git_repo", return_value=(True, None)) as dummy:
            v, r = self.git_task.task_port_repo(print, self.existent_path1, self.existent_path2, False, False, stash_count, False, None)
            self.assertFalse(v)

    def testGitPluginTaskPortRepo8(self):

        self.assertTrue(os.path.exists(self.existent_path1))
        self.assertTrue(os.path.exists(self.existent_path2))

        local_port_repo_head = True
        local_port_repo_staged = True
        local_port_repo_stash_count = "-1"
        local_port_repo_unversioned = True
        local_prev_count = "5"

        with mock.patch("port_git_repo.port_git_repo", return_value=(True, None)) as dummy:
            v, r = self.git_task.task_port_repo(print, self.existent_path1, self.existent_path2, local_port_repo_head, local_port_repo_staged, local_port_repo_stash_count, local_port_repo_unversioned, local_prev_count)
            self.assertTrue(v)
            dummy.assert_called_with(self.existent_path1, self.existent_path2, True, True, -1, True, 5)

    def testGitPluginTaskResetRepo1(self):

        self.assertFalse(os.path.exists(self.nonexistent_path1))

        with mock.patch("reset_git_repo.reset_git_repo", return_value=(True, [])) as dummy:
            v, r = self.git_task.task_reset_repo(print, self.nonexistent_path1, False, False, None, False, None)
            self.assertFalse(v)

    def testGitPluginTaskResetRepo2(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        with mock.patch("reset_git_repo.reset_git_repo", return_value=(True, [])) as dummy:
            v, r = self.git_task.task_reset_repo(print, self.existent_path1, False, False, None, False, None)
            self.assertTrue(v)
            dummy.assert_called_with(self.existent_path1, "include", [], [], False, False, 0, False, 0) # mvtodo: wirings

    def testGitPluginTaskResetRepo3(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        with mock.patch("reset_git_repo.reset_git_repo", return_value=(True, [])) as dummy:
            v, r = self.git_task.task_reset_repo(print, self.existent_path1, True, False, None, False, None)
            self.assertTrue(v)
            dummy.assert_called_with(self.existent_path1, "include", [], [], True, False, 0, False, 0) # mvtodo: wirings

    def testGitPluginTaskResetRepo4(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        with mock.patch("reset_git_repo.reset_git_repo", return_value=(True, [])) as dummy:
            v, r = self.git_task.task_reset_repo(print, self.existent_path1, False, True, None, False, None)
            self.assertTrue(v)
            dummy.assert_called_with(self.existent_path1, "include", [], [], False, True, 0, False, 0) # mvtodo: wirings

    def testGitPluginTaskResetRepo5(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        with mock.patch("reset_git_repo.reset_git_repo", return_value=(True, [])) as dummy:
            v, r = self.git_task.task_reset_repo(print, self.existent_path1, False, False, "5", False, None)
            self.assertTrue(v)
            dummy.assert_called_with(self.existent_path1, "include", [], [], False, False, 5, False, 0) # mvtodo: wirings

    def testGitPluginTaskResetRepo6(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        with mock.patch("reset_git_repo.reset_git_repo", return_value=(True, [])) as dummy:
            v, r = self.git_task.task_reset_repo(print, self.existent_path1, False, False, "-1", False, None)
            self.assertTrue(v)
            dummy.assert_called_with(self.existent_path1, "include", [], [], False, False, -1, False, 0) # mvtodo: wirings

    def testGitPluginTaskResetRepo7(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        with mock.patch("reset_git_repo.reset_git_repo", return_value=(True, [])) as dummy:
            v, r = self.git_task.task_reset_repo(print, self.existent_path1, False, False, None, True, None)
            self.assertTrue(v)
            dummy.assert_called_with(self.existent_path1, "include", [], [], False, False, 0, True, 0) # mvtodo: wirings

    def testGitPluginTaskResetRepo8(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        with mock.patch("reset_git_repo.reset_git_repo", return_value=(True, [])) as dummy:
            v, r = self.git_task.task_reset_repo(print, self.existent_path1, False, False, None, False, "9")
            self.assertTrue(v)
            dummy.assert_called_with(self.existent_path1, "include", [], [], False, False, 0, False, 9) # mvtodo: wirings

    def testGitPluginTaskRewindRepo1(self):

        self.assertFalse(os.path.exists(self.nonexistent_path1))
        self.assertTrue(os.path.exists(self.existent_path2))

        with mock.patch("git_lib.get_head_hash", return_value=(True, "mock-head-hash")) as dummy1:
            with mock.patch("git_lib.get_previous_hash_list", return_value=(True, ["mock-head-hash", "another-hash"])) as dummy2:
                with mock.patch("reset_git_repo.reset_git_repo", return_value=(True, [])) as dummy3:
                    v, r = self.git_task.task_rewind_repo(print, self.nonexistent_path1, self.existent_path2, None, True)
                    self.assertFalse(v)
                    dummy1.assert_not_called()
                    dummy2.assert_not_called()
                    dummy3.assert_not_called()

    def testGitPluginTaskRewindRepo2(self):

        self.assertTrue(os.path.exists(self.existent_path1))
        self.assertTrue(os.path.exists(self.existent_path2))

        with mock.patch("git_lib.get_head_hash", return_value=(True, "mock-head-hash")) as dummy1:
            with mock.patch("git_lib.get_previous_hash_list", return_value=(True, ["mock-head-hash", "another-hash"])) as dummy2:
                with mock.patch("reset_git_repo.reset_git_repo", return_value=(True, [])) as dummy3:
                    v, r = self.git_task.task_rewind_repo(print, self.existent_path1, self.existent_path2, "mock-head-hash", True)
                    self.assertFalse(v)
                    dummy1.assert_not_called()
                    dummy2.assert_not_called()
                    dummy3.assert_not_called()

    def testGitPluginTaskRewindRepo3(self):

        self.assertTrue(os.path.exists(self.existent_path1))
        self.assertFalse(os.path.exists(self.nonexistent_path1))

        with mock.patch("git_lib.get_head_hash", return_value=(True, "mock-head-hash")) as dummy1:
            with mock.patch("git_lib.get_previous_hash_list", return_value=(True, ["mock-head-hash", "another-hash"])) as dummy2:
                with mock.patch("reset_git_repo.reset_git_repo", return_value=(True, [])) as dummy3:
                    v, r = self.git_task.task_rewind_repo(print, self.existent_path1, self.nonexistent_path1, None, True)
                    self.assertFalse(v)
                    dummy1.assert_not_called()
                    dummy2.assert_not_called()
                    dummy3.assert_not_called()

    def testGitPluginTaskRewindRepo4(self):

        self.assertTrue(os.path.exists(self.existent_path1))
        self.assertTrue(os.path.exists(self.existent_path2))

        with mock.patch("git_lib.get_head_hash", return_value=(True, "mock-head-hash")) as dummy1:
            with mock.patch("git_lib.get_previous_hash_list", return_value=(True, ["mock-head-hash", "another-hash"])) as dummy2:
                with mock.patch("reset_git_repo.reset_git_repo", return_value=(True, [])) as dummy3:
                    v, r = self.git_task.task_rewind_repo(print, self.existent_path1, None, None, True)
                    self.assertFalse(v)
                    dummy1.assert_not_called()
                    dummy2.assert_not_called()
                    dummy3.assert_not_called()

    def testGitPluginTaskRewindRepo5(self):

        self.assertTrue(os.path.exists(self.existent_path1))
        self.assertTrue(os.path.exists(self.existent_path2))

        with mock.patch("git_lib.get_head_hash", return_value=(True, "mock-head-hash")) as dummy1:
            with mock.patch("git_lib.get_previous_hash_list", return_value=(True, ["mock-head-hash", "another-hash"])) as dummy2:
                with mock.patch("reset_git_repo.reset_git_repo", return_value=(True, [])) as dummy3:
                    v, r = self.git_task.task_rewind_repo(print, self.existent_path1, self.existent_path2, None, False)
                    self.assertFalse(v)
                    dummy1.assert_not_called()
                    dummy2.assert_not_called()
                    dummy3.assert_not_called()

    def testGitPluginTaskRewindRepo6(self):

        self.assertTrue(os.path.exists(self.existent_path1))
        self.assertTrue(os.path.exists(self.existent_path2))

        with mock.patch("git_lib.get_head_hash", return_value=(True, "mock-head")) as dummy1:
            with mock.patch("git_lib.get_previous_hash_list", return_value=(True, ["wrong-hash", "yet-more-in-front", "and-even-more", "mock-head-hash", "another-hash"])) as dummy2:
                with mock.patch("reset_git_repo.reset_git_repo", return_value=(True, [])) as dummy3:
                    v, r = self.git_task.task_rewind_repo(print, self.existent_path1, self.existent_path2, None, True)
                    self.assertFalse(v)
                    dummy1.assert_called_with(self.existent_path2)
                    dummy2.assert_called_with(self.existent_path1)
                    dummy3.assert_not_called()

    def testGitPluginTaskRewindRepo7(self):

        self.assertTrue(os.path.exists(self.existent_path1))
        self.assertTrue(os.path.exists(self.existent_path2))

        with mock.patch("git_lib.get_head_hash", return_value=(True, "mock-head-hash")) as dummy1:
            with mock.patch("git_lib.get_previous_hash_list", return_value=(True, ["wrong-hash", "yet-more-in-front", "and-even-more", "mock-head", "another-hash"])) as dummy2:
                with mock.patch("reset_git_repo.reset_git_repo", return_value=(True, [])) as dummy3:
                    v, r = self.git_task.task_rewind_repo(print, self.existent_path1, self.existent_path2, None, True)
                    self.assertTrue(v)
                    dummy1.assert_called_with(self.existent_path2)
                    dummy2.assert_called_with(self.existent_path1)
                    dummy3.assert_called_with(self.existent_path1, "include", [], [], False, False, 0, False, 3) # mvtodo: wirings

    def testGitPluginTaskRewindRepo8(self):

        self.assertTrue(os.path.exists(self.existent_path1))
        self.assertTrue(os.path.exists(self.existent_path2))

        with mock.patch("git_lib.get_head_hash", return_value=(True, "mock-head-hash")) as dummy1:
            with mock.patch("git_lib.get_previous_hash_list", return_value=(True, ["wrong-hash", "yet-more-in-front", "and-even-more", "mock-herd-hash", "another-hash"])) as dummy2:
                with mock.patch("reset_git_repo.reset_git_repo", return_value=(True, [])) as dummy3:
                    v, r = self.git_task.task_rewind_repo(print, self.existent_path1, self.existent_path2, None, True)
                    self.assertFalse(v)
                    dummy1.assert_called_with(self.existent_path2)
                    dummy2.assert_called_with(self.existent_path1)
                    dummy3.assert_not_called()

    def testGitPluginTaskRewindRepo9(self):

        self.assertTrue(os.path.exists(self.existent_path1))
        self.assertTrue(os.path.exists(self.existent_path2))

        with mock.patch("git_lib.get_head_hash", return_value=(True, "mock-head-hash")) as dummy1:
            with mock.patch("git_lib.get_previous_hash_list", return_value=(True, ["wrong-hash", "yet-more-in-front", "and-even-more", "mock-head-hash", "another-hash"])) as dummy2:
                with mock.patch("reset_git_repo.reset_git_repo", return_value=(True, [])) as dummy3:
                    v, r = self.git_task.task_rewind_repo(print, self.existent_path1, self.existent_path2, None, True)
                    self.assertTrue(v)
                    dummy1.assert_called_with(self.existent_path2)
                    dummy2.assert_called_with(self.existent_path1)
                    dummy3.assert_called_with(self.existent_path1, "include", [], [], False, False, 0, False, 3) # mvtodo: wirings

    def testGitPluginTaskRewindRepo10(self):

        self.assertTrue(os.path.exists(self.existent_path1))
        self.assertTrue(os.path.exists(self.existent_path2))

        with mock.patch("git_lib.get_head_hash", return_value=(True, "mock-head-hash")) as dummy1:
            with mock.patch("git_lib.get_previous_hash_list", return_value=(True, ["wrong-hash", "mock-head-hash", "another-hash"])) as dummy2:
                with mock.patch("reset_git_repo.reset_git_repo", return_value=(True, [])) as dummy3:
                    v, r = self.git_task.task_rewind_repo(print, self.existent_path1, self.existent_path2, None, True)
                    self.assertTrue(v)
                    dummy1.assert_called_with(self.existent_path2)
                    dummy2.assert_called_with(self.existent_path1)
                    dummy3.assert_called_with(self.existent_path1, "include", [], [], False, False, 0, False, 1) # mvtodo: wirings

    def testGitPluginTaskRewindRepo11(self):

        self.assertTrue(os.path.exists(self.existent_path1))
        self.assertTrue(os.path.exists(self.existent_path2))

        with mock.patch("git_lib.get_head_hash", return_value=(True, "mock-head-hash")) as dummy1:
            with mock.patch("git_lib.get_previous_hash_list", return_value=(True, ["mock-head-hash", "another-hash"])) as dummy2:
                with mock.patch("reset_git_repo.reset_git_repo", return_value=(True, [])) as dummy3:
                    v, r = self.git_task.task_rewind_repo(print, self.existent_path1, self.existent_path2, None, True)
                    self.assertTrue(v)
                    dummy1.assert_called_with(self.existent_path2)
                    dummy2.assert_called_with(self.existent_path1)
                    dummy3.assert_called_with(self.existent_path1, "include", [], [], False, False, 0, False, 0) # mvtodo: wirings

    def testGitPluginTaskRewindRepo12(self):

        first_repo = path_utils.concat_path(self.test_dir, "first")
        second_repo = path_utils.concat_path(self.test_dir, "second")
        third_repo = path_utils.concat_path(self.test_dir, "third")

        self.assertFalse(os.path.exists(first_repo))
        self.assertFalse(os.path.exists(second_repo))
        self.assertFalse(os.path.exists(third_repo))

        v, r = git_wrapper.init(self.test_dir, "first", True)
        self.assertTrue(v)
        v, r = git_wrapper.clone(first_repo, second_repo)
        self.assertTrue(v)

        second_file1 = path_utils.concat_path(second_repo, "file1.txt")
        v, r = git_test_fixture.git_createAndCommit(second_repo, path_utils.basename_filtered(second_file1), "file1-content1", "init")
        self.assertTrue(v)

        second_file2 = path_utils.concat_path(second_repo, "file2.txt")
        v, r = git_test_fixture.git_createAndCommit(second_repo, path_utils.basename_filtered(second_file2), "file2-content1", "second commit")
        self.assertTrue(v)

        v, r = git_wrapper.push(second_repo, "origin", "master")
        self.assertTrue(v)

        v, r = git_wrapper.clone(first_repo, third_repo)
        self.assertTrue(v)

        self.assertTrue(os.path.exists(first_repo))
        self.assertTrue(os.path.exists(second_repo))
        self.assertTrue(os.path.exists(third_repo))

        v, r = git_lib.get_head_hash(second_repo)
        self.assertTrue(v)
        head_hash_second = r

        v, r = git_lib.get_head_hash(third_repo)
        self.assertTrue(v)
        head_hash_third = r

        self.assertEqual(head_hash_second, head_hash_third)

        v, r = self.git_task.task_rewind_repo(print, second_repo, third_repo, None, False)
        self.assertFalse(v)

    def testGitPluginTaskRewindRepo13(self):

        first_repo = path_utils.concat_path(self.test_dir, "first")
        second_repo = path_utils.concat_path(self.test_dir, "second")
        third_repo = path_utils.concat_path(self.test_dir, "third")

        self.assertFalse(os.path.exists(first_repo))
        self.assertFalse(os.path.exists(second_repo))
        self.assertFalse(os.path.exists(third_repo))

        v, r = git_wrapper.init(self.test_dir, "first", True)
        self.assertTrue(v)
        v, r = git_wrapper.clone(first_repo, second_repo)
        self.assertTrue(v)

        second_file1 = path_utils.concat_path(second_repo, "file1.txt")
        v, r = git_test_fixture.git_createAndCommit(second_repo, path_utils.basename_filtered(second_file1), "file1-content1", "init")
        self.assertTrue(v)

        second_file2 = path_utils.concat_path(second_repo, "file2.txt")
        v, r = git_test_fixture.git_createAndCommit(second_repo, path_utils.basename_filtered(second_file2), "file2-content1", "second commit")
        self.assertTrue(v)

        v, r = git_wrapper.push(second_repo, "origin", "master")
        self.assertTrue(v)

        v, r = git_wrapper.clone(first_repo, third_repo)
        self.assertTrue(v)

        self.assertTrue(os.path.exists(first_repo))
        self.assertTrue(os.path.exists(second_repo))
        self.assertTrue(os.path.exists(third_repo))

        v, r = git_lib.get_head_hash(second_repo)
        self.assertTrue(v)
        head_hash_second = r

        v, r = git_lib.get_head_hash(third_repo)
        self.assertTrue(v)
        head_hash_third = r

        self.assertEqual(head_hash_second, head_hash_third)

        second_file3 = path_utils.concat_path(second_repo, "file3.txt")
        v, r = git_test_fixture.git_createAndCommit(second_repo, path_utils.basename_filtered(second_file3), "file3-content1", "third commit")
        self.assertTrue(v)
        self.assertTrue(os.path.exists(second_file3))

        v, r = git_lib.get_head_hash(second_repo)
        self.assertTrue(v)
        head_hash_second = r

        v, r = git_lib.get_head_hash(third_repo)
        self.assertTrue(v)
        head_hash_third = r

        self.assertNotEqual(head_hash_second, head_hash_third)

        fixed_ts = "fixed_timestamp"
        temp_storage_base = path_utils.concat_path(self.test_dir, "patch_bk_storage")
        self.assertTrue(path_utils.guaranteefolder(temp_storage_base))
        patch_backup_full = path_utils.concat_path(temp_storage_base, ("second_reset_git_repo_backup_%s" % fixed_ts), "previous", "1_reset_git_repo_previous_%s.patch" % head_hash_second)

        self.assertFalse(os.path.exists(patch_backup_full))

        with mock.patch("maketimestamp.get_timestamp_now_compact", return_value=fixed_ts) as dummy1:
            with mock.patch("mvtools_envvars.mvtools_envvar_read_temp_path", return_value=(True, temp_storage_base)) as dummy2:
                v, r = self.git_task.task_rewind_repo(print, second_repo, third_repo, None, True)
                self.assertTrue(v)
                dummy1.assert_called()
                dummy2.assert_called()

        v, r = git_lib.get_head_hash(second_repo)
        self.assertTrue(v)
        head_hash_second = r

        v, r = git_lib.get_head_hash(third_repo)
        self.assertTrue(v)
        head_hash_third = r

        self.assertEqual(head_hash_second, head_hash_third)
        self.assertTrue(os.path.exists(patch_backup_full))
        self.assertFalse(os.path.exists(second_file3))

    def testGitPluginTaskRewindRepo14(self):

        first_repo = path_utils.concat_path(self.test_dir, "first")
        second_repo = path_utils.concat_path(self.test_dir, "second")

        self.assertFalse(os.path.exists(first_repo))
        self.assertFalse(os.path.exists(second_repo))

        v, r = git_wrapper.init(self.test_dir, "first", True)
        self.assertTrue(v)
        v, r = git_wrapper.clone(first_repo, second_repo)
        self.assertTrue(v)

        second_file1 = path_utils.concat_path(second_repo, "file1.txt")
        v, r = git_test_fixture.git_createAndCommit(second_repo, path_utils.basename_filtered(second_file1), "file1-content1", "init")
        self.assertTrue(v)

        second_file2 = path_utils.concat_path(second_repo, "file2.txt")
        v, r = git_test_fixture.git_createAndCommit(second_repo, path_utils.basename_filtered(second_file2), "file2-content1", "second commit")
        self.assertTrue(v)

        v, r = git_lib.get_head_hash(second_repo)
        self.assertTrue(v)
        head_hash_second_2ndcommit = r

        second_file3 = path_utils.concat_path(second_repo, "file3.txt")
        v, r = git_test_fixture.git_createAndCommit(second_repo, path_utils.basename_filtered(second_file3), "file3-content1", "third commit")
        self.assertTrue(v)

        v, r = git_wrapper.push(second_repo, "origin", "master")
        self.assertTrue(v)

        self.assertTrue(os.path.exists(first_repo))
        self.assertTrue(os.path.exists(second_repo))

        v, r = git_lib.get_head_hash(second_repo)
        self.assertTrue(v)
        head_hash_second_3rdcommit = r

        fixed_ts = "fixed_timestamp"
        temp_storage_base = path_utils.concat_path(self.test_dir, "patch_bk_storage")
        self.assertTrue(path_utils.guaranteefolder(temp_storage_base))
        patch_backup_full = path_utils.concat_path(temp_storage_base, ("second_reset_git_repo_backup_%s" % fixed_ts), "previous", "1_reset_git_repo_previous_%s.patch" % head_hash_second_3rdcommit)

        self.assertFalse(os.path.exists(patch_backup_full))

        with mock.patch("maketimestamp.get_timestamp_now_compact", return_value=fixed_ts) as dummy1:
            with mock.patch("mvtools_envvars.mvtools_envvar_read_temp_path", return_value=(True, temp_storage_base)) as dummy2:
                v, r = self.git_task.task_rewind_repo(print, second_repo, None, head_hash_second_2ndcommit, False)
                self.assertTrue(v)
                dummy1.assert_called()
                dummy2.assert_called()

        v, r = git_lib.get_head_hash(second_repo)
        self.assertTrue(v)
        head_hash_second = r

        self.assertTrue(os.path.exists(patch_backup_full))
        self.assertFalse(os.path.exists(second_file3))

    def testGitPluginTaskRewindRepo15(self):

        first_repo = path_utils.concat_path(self.test_dir, "first")
        second_repo = path_utils.concat_path(self.test_dir, "second")

        self.assertFalse(os.path.exists(first_repo))
        self.assertFalse(os.path.exists(second_repo))

        v, r = git_wrapper.init(self.test_dir, "first", True)
        self.assertTrue(v)
        v, r = git_wrapper.clone(first_repo, second_repo)
        self.assertTrue(v)

        second_file1 = path_utils.concat_path(second_repo, "file1.txt")
        v, r = git_test_fixture.git_createAndCommit(second_repo, path_utils.basename_filtered(second_file1), "file1-content1", "init")
        self.assertTrue(v)

        second_file2 = path_utils.concat_path(second_repo, "file2.txt")
        v, r = git_test_fixture.git_createAndCommit(second_repo, path_utils.basename_filtered(second_file2), "file2-content1", "second commit")
        self.assertTrue(v)

        v, r = git_lib.get_head_hash(second_repo)
        self.assertTrue(v)
        head_hash_second_2ndcommit = r

        second_file3 = path_utils.concat_path(second_repo, "file3.txt")
        v, r = git_test_fixture.git_createAndCommit(second_repo, path_utils.basename_filtered(second_file3), "file3-content1", "third commit")
        self.assertTrue(v)

        v, r = git_wrapper.push(second_repo, "origin", "master")
        self.assertTrue(v)

        self.assertTrue(os.path.exists(first_repo))
        self.assertTrue(os.path.exists(second_repo))

        v, r = git_lib.get_head_hash(second_repo)
        self.assertTrue(v)
        head_hash_second_3rdcommit = r

        fixed_ts = "fixed_timestamp"
        temp_storage_base = path_utils.concat_path(self.test_dir, "patch_bk_storage")
        self.assertTrue(path_utils.guaranteefolder(temp_storage_base))
        patch_backup_full = path_utils.concat_path(temp_storage_base, ("second_reset_git_repo_backup_%s" % fixed_ts), "previous", "1_reset_git_repo_previous_%s.patch" % head_hash_second_3rdcommit)

        self.assertFalse(os.path.exists(patch_backup_full))

        with mock.patch("maketimestamp.get_timestamp_now_compact", return_value=fixed_ts) as dummy1:
            with mock.patch("mvtools_envvars.mvtools_envvar_read_temp_path", return_value=(True, temp_storage_base)) as dummy2:
                v, r = self.git_task.task_rewind_repo(print, second_repo, None, "invalid-hash", False)
                self.assertFalse(v)
                dummy1.assert_not_called()
                dummy2.assert_not_called()

        v, r = git_lib.get_head_hash(second_repo)
        self.assertTrue(v)
        head_hash_second = r

        self.assertFalse(os.path.exists(patch_backup_full))
        self.assertTrue(os.path.exists(second_file3))

    def testGitPluginTaskRewindRepo16(self):

        first_repo = path_utils.concat_path(self.test_dir, "first")
        second_repo = path_utils.concat_path(self.test_dir, "second")
        third_repo = path_utils.concat_path(self.test_dir, "third")

        self.assertFalse(os.path.exists(first_repo))
        self.assertFalse(os.path.exists(second_repo))
        self.assertFalse(os.path.exists(third_repo))

        v, r = git_wrapper.init(self.test_dir, "first", True)
        self.assertTrue(v)
        v, r = git_wrapper.clone(first_repo, second_repo)
        self.assertTrue(v)

        second_file1 = path_utils.concat_path(second_repo, "file1.txt")
        v, r = git_test_fixture.git_createAndCommit(second_repo, path_utils.basename_filtered(second_file1), "file1-content1", "init")
        self.assertTrue(v)

        second_file2 = path_utils.concat_path(second_repo, "file2.txt")
        v, r = git_test_fixture.git_createAndCommit(second_repo, path_utils.basename_filtered(second_file2), "file2-content1", "second commit")
        self.assertTrue(v)

        v, r = git_wrapper.push(second_repo, "origin", "master")
        self.assertTrue(v)

        v, r = git_wrapper.clone(first_repo, third_repo)
        self.assertTrue(v)

        self.assertTrue(os.path.exists(first_repo))
        self.assertTrue(os.path.exists(second_repo))
        self.assertTrue(os.path.exists(third_repo))

        v, r = git_lib.get_head_hash(second_repo)
        self.assertTrue(v)
        head_hash_second = r

        v, r = git_lib.get_head_hash(third_repo)
        self.assertTrue(v)
        head_hash_third = r

        self.assertEqual(head_hash_second, head_hash_third)

        second_file3 = path_utils.concat_path(second_repo, "file3.txt")
        v, r = git_test_fixture.git_createAndCommit(second_repo, path_utils.basename_filtered(second_file3), "file3-content1", "third commit")
        self.assertTrue(v)

        v, r = git_lib.get_head_hash(second_repo)
        self.assertTrue(v)
        head_hash_3rdcomm = r

        second_file4 = path_utils.concat_path(second_repo, "file4.txt")
        v, r = git_test_fixture.git_createAndCommit(second_repo, path_utils.basename_filtered(second_file4), "file4-content1", "fourth commit")
        self.assertTrue(v)

        v, r = git_lib.get_head_hash(second_repo)
        self.assertTrue(v)
        head_hash_4thcomm = r

        second_file5 = path_utils.concat_path(second_repo, "file5.txt")
        v, r = git_test_fixture.git_createAndCommit(second_repo, path_utils.basename_filtered(second_file5), "file5-content1", "fifth commit")
        self.assertTrue(v)

        v, r = git_lib.get_head_hash(second_repo)
        self.assertTrue(v)
        head_hash_5thcomm = r

        v, r = git_lib.get_head_hash(second_repo)
        self.assertTrue(v)
        head_hash_second = r

        v, r = git_lib.get_head_hash(third_repo)
        self.assertTrue(v)
        head_hash_third = r

        self.assertNotEqual(head_hash_second, head_hash_third)

        fixed_ts = "fixed_timestamp"
        temp_storage_base = path_utils.concat_path(self.test_dir, "patch_bk_storage")
        self.assertTrue(path_utils.guaranteefolder(temp_storage_base))
        patch1_backup_full = path_utils.concat_path(temp_storage_base, ("second_reset_git_repo_backup_%s" % fixed_ts), "previous", "1_reset_git_repo_previous_%s.patch" % head_hash_5thcomm)
        patch2_backup_full = path_utils.concat_path(temp_storage_base, ("second_reset_git_repo_backup_%s" % fixed_ts), "previous", "2_reset_git_repo_previous_%s.patch" % head_hash_4thcomm)
        patch3_backup_full = path_utils.concat_path(temp_storage_base, ("second_reset_git_repo_backup_%s" % fixed_ts), "previous", "3_reset_git_repo_previous_%s.patch" % head_hash_3rdcomm)

        self.assertFalse(os.path.exists(patch1_backup_full))
        self.assertFalse(os.path.exists(patch2_backup_full))
        self.assertFalse(os.path.exists(patch3_backup_full))
        self.assertTrue(os.path.exists(second_file3))
        self.assertTrue(os.path.exists(second_file4))
        self.assertTrue(os.path.exists(second_file5))

        with mock.patch("maketimestamp.get_timestamp_now_compact", return_value=fixed_ts) as dummy1:
            with mock.patch("mvtools_envvars.mvtools_envvar_read_temp_path", return_value=(True, temp_storage_base)) as dummy2:
                v, r = self.git_task.task_rewind_repo(print, second_repo, third_repo, None, True)
                self.assertTrue(v)
                dummy1.assert_called()
                dummy2.assert_called()

        v, r = git_lib.get_head_hash(second_repo)
        self.assertTrue(v)
        head_hash_second = r

        v, r = git_lib.get_head_hash(third_repo)
        self.assertTrue(v)
        head_hash_third = r

        self.assertEqual(head_hash_second, head_hash_third)
        self.assertTrue(os.path.exists(patch1_backup_full))
        self.assertTrue(os.path.exists(patch2_backup_full))
        self.assertTrue(os.path.exists(patch3_backup_full))
        self.assertFalse(os.path.exists(second_file3))
        self.assertFalse(os.path.exists(second_file4))
        self.assertFalse(os.path.exists(second_file5))

    def testGitPluginTaskRewindRepo17(self):

        first_repo = path_utils.concat_path(self.test_dir, "first")
        second_repo = path_utils.concat_path(self.test_dir, "second")

        self.assertFalse(os.path.exists(first_repo))
        self.assertFalse(os.path.exists(second_repo))

        v, r = git_wrapper.init(self.test_dir, "first", True)
        self.assertTrue(v)
        v, r = git_wrapper.clone(first_repo, second_repo)
        self.assertTrue(v)

        second_file1 = path_utils.concat_path(second_repo, "file1.txt")
        v, r = git_test_fixture.git_createAndCommit(second_repo, path_utils.basename_filtered(second_file1), "file1-content1", "init")
        self.assertTrue(v)

        second_file2 = path_utils.concat_path(second_repo, "file2.txt")
        v, r = git_test_fixture.git_createAndCommit(second_repo, path_utils.basename_filtered(second_file2), "file2-content1", "second commit")
        self.assertTrue(v)

        v, r = git_wrapper.push(second_repo, "origin", "master")
        self.assertTrue(v)

        self.assertTrue(os.path.exists(first_repo))
        self.assertTrue(os.path.exists(second_repo))

        second_file3 = path_utils.concat_path(second_repo, "file3.txt")
        v, r = git_test_fixture.git_createAndCommit(second_repo, path_utils.basename_filtered(second_file3), "file3-content1", "third commit")
        self.assertTrue(v)

        v, r = git_lib.get_head_hash(second_repo)
        self.assertTrue(v)
        head_hash_3rdcomm = r

        second_file4 = path_utils.concat_path(second_repo, "file4.txt")
        v, r = git_test_fixture.git_createAndCommit(second_repo, path_utils.basename_filtered(second_file4), "file4-content1", "fourth commit")
        self.assertTrue(v)

        v, r = git_lib.get_head_hash(second_repo)
        self.assertTrue(v)
        head_hash_4thcomm = r

        second_file5 = path_utils.concat_path(second_repo, "file5.txt")
        v, r = git_test_fixture.git_createAndCommit(second_repo, path_utils.basename_filtered(second_file5), "file5-content1", "fifth commit")
        self.assertTrue(v)

        v, r = git_lib.get_head_hash(second_repo)
        self.assertTrue(v)
        head_hash_5thcomm = r

        fixed_ts = "fixed_timestamp"
        temp_storage_base = path_utils.concat_path(self.test_dir, "patch_bk_storage")
        self.assertTrue(path_utils.guaranteefolder(temp_storage_base))
        patch1_backup_full = path_utils.concat_path(temp_storage_base, ("second_reset_git_repo_backup_%s" % fixed_ts), "previous", "1_reset_git_repo_previous_%s.patch" % head_hash_5thcomm)
        patch2_backup_full = path_utils.concat_path(temp_storage_base, ("second_reset_git_repo_backup_%s" % fixed_ts), "previous", "2_reset_git_repo_previous_%s.patch" % head_hash_4thcomm)
        patch3_backup_full = path_utils.concat_path(temp_storage_base, ("second_reset_git_repo_backup_%s" % fixed_ts), "previous", "3_reset_git_repo_previous_%s.patch" % head_hash_3rdcomm)

        self.assertFalse(os.path.exists(patch1_backup_full))
        self.assertFalse(os.path.exists(patch2_backup_full))
        self.assertFalse(os.path.exists(patch3_backup_full))
        self.assertTrue(os.path.exists(second_file3))
        self.assertTrue(os.path.exists(second_file4))
        self.assertTrue(os.path.exists(second_file5))

        with mock.patch("maketimestamp.get_timestamp_now_compact", return_value=fixed_ts) as dummy1:
            with mock.patch("mvtools_envvars.mvtools_envvar_read_temp_path", return_value=(True, temp_storage_base)) as dummy2:
                v, r = self.git_task.task_rewind_repo(print, second_repo, None, head_hash_3rdcomm, False)
                self.assertTrue(v)
                dummy1.assert_called()
                dummy2.assert_called()

        v, r = git_lib.get_head_hash(second_repo)
        self.assertTrue(v)
        head_hash_second = r

        self.assertTrue(os.path.exists(patch1_backup_full))
        self.assertTrue(os.path.exists(patch2_backup_full))
        self.assertFalse(os.path.exists(patch3_backup_full))
        self.assertTrue(os.path.exists(second_file3))
        self.assertFalse(os.path.exists(second_file4))
        self.assertFalse(os.path.exists(second_file5))

    def testGitPluginTaskPatchRepo1(self):

        self.assertFalse(os.path.exists(self.nonexistent_path1))

        with mock.patch("apply_git_patch.apply_git_patch", return_value=(True, None)) as dummy:
            v, r = self.git_task.task_patch_repo(print, self.nonexistent_path1, None, None, None, None, None)
            self.assertFalse(v)

    def testGitPluginTaskPatchRepo2(self):

        self.assertTrue(os.path.exists(self.existent_path1))
        self.assertFalse(os.path.exists(self.nonexistent_path1))

        with mock.patch("apply_git_patch.apply_git_patch", return_value=(True, None)) as dummy:
            v, r = self.git_task.task_patch_repo(print, self.existent_path1, None, None, None, self.nonexistent_path1, None)
            self.assertFalse(v)

    def testGitPluginTaskPatchRepo3(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        with mock.patch("apply_git_patch.apply_git_patch", return_value=(True, None)) as dummy:
            v, r = self.git_task.task_patch_repo(print, self.existent_path1, None, None, None, None, None)
            self.assertTrue(v)
            dummy.assert_called_with(self.existent_path1, [], [], [], [])

    def testGitPluginTaskPatchRepo4(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        head_patch = path_utils.concat_path(self.existent_path1, "file1.txt")
        staged_patch = path_utils.concat_path(self.existent_path1, "file2.txt")
        stash_patch = path_utils.concat_path(self.existent_path1, "file3.txt")
        unversioned_base_folder = path_utils.concat_path(self.existent_path1, "unversioned")
        os.mkdir(unversioned_base_folder)
        self.assertTrue(os.path.exists(unversioned_base_folder))
        unversioned_file = "file4.txt"

        with mock.patch("apply_git_patch.apply_git_patch", return_value=(True, None)) as dummy:
            v, r = self.git_task.task_patch_repo(print, self.existent_path1, head_patch, staged_patch, stash_patch, unversioned_base_folder, unversioned_file)
            self.assertTrue(v)
            dummy.assert_called_with(self.existent_path1, [head_patch], [staged_patch], [stash_patch], [(unversioned_base_folder, path_utils.concat_path(unversioned_base_folder, unversioned_file))])

    def testGitPluginRunTask1(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        self.git_task.params = local_params

        v, r = self.git_task.run_task(print, "exe_name")
        self.assertFalse(v)

    def testGitPluginRunTask_CloneRepo1(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        local_params = {}
        local_params["target_path"] = self.existent_path1
        local_params["operation"] = "clone_repo"
        local_params["source_url"] = "dummy_value1"
        local_params["target_path"] = "dummy_value2"
        local_params["remote_name"] = "dummy_value3"
        self.git_task.params = local_params

        with mock.patch("git_plugin.CustomTask.task_clone_repo", return_value=(True, None)) as dummy:
            v, r = self.git_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(print, "dummy_value1", "dummy_value2", "dummy_value3")

    def testGitPluginRunTask_CloneRepo2(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        local_params = {}
        local_params["target_path"] = self.existent_path1
        local_params["operation"] = "clone_repo"
        self.git_task.params = local_params

        with mock.patch("git_plugin.CustomTask.task_clone_repo", return_value=(True, None)) as dummy:
            v, r = self.git_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(print, None, self.existent_path1, None)

    def testGitPluginRunTask_PullRepo1(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        local_params = {}
        local_params["target_path"] = self.existent_path1
        local_params["operation"] = "pull_repo"
        self.git_task.params = local_params

        with mock.patch("git_plugin.CustomTask.task_pull_repo", return_value=(True, None)) as dummy:
            v, r = self.git_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(print, self.existent_path1, None, None)

    def testGitPluginRunTask_PullRepo2(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        local_params = {}
        local_params["target_path"] = self.existent_path1
        local_params["operation"] = "pull_repo"
        local_params["remote_name"] = "dummy_value1"
        self.git_task.params = local_params

        with mock.patch("git_plugin.CustomTask.task_pull_repo", return_value=(True, None)) as dummy:
            v, r = self.git_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(print, self.existent_path1, "dummy_value1", None)

    def testGitPluginRunTask_PullRepo3(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        local_params = {}
        local_params["target_path"] = self.existent_path1
        local_params["operation"] = "pull_repo"
        local_params["branch_name"] = "dummy_value1"
        self.git_task.params = local_params

        with mock.patch("git_plugin.CustomTask.task_pull_repo", return_value=(True, None)) as dummy:
            v, r = self.git_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(print, self.existent_path1, None, "dummy_value1")

    def testGitPluginRunTask_PullRepo4(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        local_params = {}
        local_params["target_path"] = self.existent_path1
        local_params["operation"] = "pull_repo"
        local_params["remote_name"] = "dummy_value1"
        local_params["branch_name"] = "dummy_value2"
        self.git_task.params = local_params

        with mock.patch("git_plugin.CustomTask.task_pull_repo", return_value=(True, None)) as dummy:
            v, r = self.git_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(print, self.existent_path1, "dummy_value1", "dummy_value2")

    def testGitPluginRunTask_PortRepo1(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        local_params = {}
        local_params["target_path"] = self.existent_path1
        local_params["operation"] = "port_repo"
        local_params["source_path"] = "dummy_value1"
        local_params["port_repo_head"] = "dummy_value2"
        local_params["port_repo_staged"] = "dummy_value3"
        local_params["port_repo_stash_count"] = "dummy_value4"
        local_params["port_repo_unversioned"] = "dummy_value5"
        local_params["port_repo_previous_count"] = "dummy_value6"
        self.git_task.params = local_params

        with mock.patch("git_plugin.CustomTask.task_port_repo", return_value=(True, None)) as dummy:
            v, r = self.git_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(print, "dummy_value1", self.existent_path1, True, True, "dummy_value4", True, "dummy_value6")

    def testGitPluginRunTask_PortRepo2(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        local_params = {}
        local_params["target_path"] = self.existent_path1
        local_params["operation"] = "port_repo"
        self.git_task.params = local_params

        with mock.patch("git_plugin.CustomTask.task_port_repo", return_value=(True, None)) as dummy:
            v, r = self.git_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(print, None, self.existent_path1, False, False, None, False, None)

    def testGitPluginRunTask_ResetRepo1(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        local_params = {}
        local_params["target_path"] = self.existent_path1
        local_params["operation"] = "reset_repo"
        self.git_task.params = local_params

        with mock.patch("git_plugin.CustomTask.task_reset_repo", return_value=(True, None)) as dummy:
            v, r = self.git_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(print, self.existent_path1, False, False, None, False, None)

    def testGitPluginRunTask_ResetRepo2(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        local_params = {}
        local_params["target_path"] = self.existent_path1
        local_params["operation"] = "reset_repo"
        local_params["reset_head"] = "dummy_value1"
        self.git_task.params = local_params

        with mock.patch("git_plugin.CustomTask.task_reset_repo", return_value=(True, None)) as dummy:
            v, r = self.git_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(print, self.existent_path1, True, False, None, False, None)

    def testGitPluginRunTask_ResetRepo3(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        local_params = {}
        local_params["target_path"] = self.existent_path1
        local_params["operation"] = "reset_repo"
        local_params["reset_staged"] = "dummy_value1"
        self.git_task.params = local_params

        with mock.patch("git_plugin.CustomTask.task_reset_repo", return_value=(True, None)) as dummy:
            v, r = self.git_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(print, self.existent_path1, False, True, None, False, None)

    def testGitPluginRunTask_ResetRepo4(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        local_params = {}
        local_params["target_path"] = self.existent_path1
        local_params["operation"] = "reset_repo"
        local_params["reset_stash_count"] = "dummy_value1"
        self.git_task.params = local_params

        with mock.patch("git_plugin.CustomTask.task_reset_repo", return_value=(True, None)) as dummy:
            v, r = self.git_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(print, self.existent_path1, False, False, "dummy_value1", False, None)

    def testGitPluginRunTask_ResetRepo5(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        local_params = {}
        local_params["target_path"] = self.existent_path1
        local_params["operation"] = "reset_repo"
        local_params["reset_unversioned"] = "dummy_value1"
        self.git_task.params = local_params

        with mock.patch("git_plugin.CustomTask.task_reset_repo", return_value=(True, None)) as dummy:
            v, r = self.git_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(print, self.existent_path1, False, False, None, True, None)

    def testGitPluginRunTask_ResetRepo6(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        local_params = {}
        local_params["target_path"] = self.existent_path1
        local_params["operation"] = "reset_repo"
        local_params["reset_previous_count"] = "dummy_value1"
        self.git_task.params = local_params

        with mock.patch("git_plugin.CustomTask.task_reset_repo", return_value=(True, None)) as dummy:
            v, r = self.git_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(print, self.existent_path1, False, False, None, False, "dummy_value1")

    def testGitPluginRunTask_RewindRepo1(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        local_params = {}
        local_params["target_path"] = self.existent_path1
        local_params["operation"] = "rewind_repo"
        self.git_task.params = local_params

        with mock.patch("git_plugin.CustomTask.task_rewind_repo", return_value=(True, None)) as dummy:
            v, r = self.git_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(print, self.existent_path1, None, None, False)

    def testGitPluginRunTask_RewindRepo2(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        local_params = {}
        local_params["target_path"] = self.existent_path1
        local_params["operation"] = "rewind_repo"
        local_params["source_path"] = "dummy_value1"
        self.git_task.params = local_params

        with mock.patch("git_plugin.CustomTask.task_rewind_repo", return_value=(True, None)) as dummy:
            v, r = self.git_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(print, self.existent_path1, "dummy_value1", None, False)

    def testGitPluginRunTask_RewindRepo3(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        local_params = {}
        local_params["target_path"] = self.existent_path1
        local_params["operation"] = "rewind_repo"
        local_params["rewind_to_hash"] = "dummy_value1"
        self.git_task.params = local_params

        with mock.patch("git_plugin.CustomTask.task_rewind_repo", return_value=(True, None)) as dummy:
            v, r = self.git_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(print, self.existent_path1, None, "dummy_value1", False)

    def testGitPluginRunTask_RewindRepo4(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        local_params = {}
        local_params["target_path"] = self.existent_path1
        local_params["operation"] = "rewind_repo"
        local_params["rewind_like_source"] = "dummy_value1"
        self.git_task.params = local_params

        with mock.patch("git_plugin.CustomTask.task_rewind_repo", return_value=(True, None)) as dummy:
            v, r = self.git_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(print, self.existent_path1, None, None, True)

    def testGitPluginRunTask_PatchRepo1(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        local_params = {}
        local_params["target_path"] = self.existent_path1
        local_params["operation"] = "patch_repo"
        self.git_task.params = local_params

        with mock.patch("git_plugin.CustomTask.task_patch_repo", return_value=(True, None)) as dummy:
            v, r = self.git_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(print, self.existent_path1, None, None, None, None, None)

    def testGitPluginRunTask_PatchRepo2(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        local_params = {}
        local_params["target_path"] = self.existent_path1
        local_params["operation"] = "patch_repo"
        local_params["patch_head_file"] = "dummy_value1"
        local_params["patch_staged_file"] = "dummy_value2"
        local_params["patch_stash_file"] = "dummy_value3"
        local_params["patch_unversioned_base"] = "dummy_value4"
        local_params["patch_unversioned_file"] = "dummy_value5"
        self.git_task.params = local_params

        with mock.patch("git_plugin.CustomTask.task_patch_repo", return_value=(True, None)) as dummy:
            v, r = self.git_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(print, self.existent_path1, "dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4", "dummy_value5")

if __name__ == '__main__':
    unittest.main()
