#!/usr/bin/env python3

import sys
import os
import shutil
import unittest
from unittest import mock
from unittest.mock import patch

import mvtools_test_fixture
import path_utils

import git_plugin

import git_wrapper
import port_git_repo
import reset_git_repo
import apply_git_patch

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
        self.assertEqual( r, ("dummy_value1", "dummy_value2", None, None, None, None, None, None, None, None, None, None) )

    def testGitPluginReadParams3(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        local_params["source_url"] = "dummy_value3"
        self.git_task.params = local_params

        v, r = self.git_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", "dummy_value3", None, None, None, None, None, None, None, None, None) )

    def testGitPluginReadParams4(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        local_params["remote_name"] = "dummy_value3"
        self.git_task.params = local_params

        v, r = self.git_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", None, "dummy_value3", None, None, None, None, None, None, None, None) )

    def testGitPluginReadParams5(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        local_params["source_path"] = "dummy_value3"
        self.git_task.params = local_params

        v, r = self.git_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", None, None, "dummy_value3", None, None, None, None, None, None, None) )

    def testGitPluginReadParams6(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        local_params["previous_count"] = "dummy_value3"
        self.git_task.params = local_params

        v, r = self.git_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", None, None, None, "dummy_value3", None, None, None, None, None, None) )

    def testGitPluginReadParams7(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        local_params["reset_file"] = "dummy_value3"
        self.git_task.params = local_params

        v, r = self.git_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", None, None, None, None, "dummy_value3", None, None, None, None, None) )

    def testGitPluginReadParams8(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        local_params["patch_head_file"] = "dummy_value3"
        self.git_task.params = local_params

        v, r = self.git_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", None, None, None, None, None, "dummy_value3", None, None, None, None) )

    def testGitPluginReadParams9(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        local_params["patch_staged_file"] = "dummy_value3"
        self.git_task.params = local_params

        v, r = self.git_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", None, None, None, None, None, None, "dummy_value3", None, None, None) )

    def testGitPluginReadParams10(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        local_params["patch_stash_file"] = "dummy_value3"
        self.git_task.params = local_params

        v, r = self.git_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", None, None, None, None, None, None, None, "dummy_value3", None, None) )

    def testGitPluginReadParams11(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        local_params["patch_unversioned_base"] = "dummy_value3"
        self.git_task.params = local_params

        v, r = self.git_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", None, None, None, None, None, None, None, None, "dummy_value3", None) )

    def testGitPluginReadParams12(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        local_params["patch_unversioned_file"] = "dummy_value3"
        self.git_task.params = local_params

        v, r = self.git_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", None, None, None, None, None, None, None, None, None, "dummy_value3") )

    def testGitPluginTaskCloneRepo1(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        self.git_task.params = local_params

        existent_path = path_utils.concat_path(self.test_dir, "existent_path")
        os.mkdir(existent_path)
        self.assertTrue(os.path.exists(existent_path))

        with mock.patch("git_wrapper.clone", return_value=(True, None)):
            v, r = self.git_task.task_clone_repo(print, None, existent_path, "dummy_value4")
            self.assertFalse(v)

    def testGitPluginTaskCloneRepo2(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        self.git_task.params = local_params

        nonexistent_path = path_utils.concat_path(self.test_dir, "nonexistent_path")
        self.assertFalse(os.path.exists(nonexistent_path))

        with mock.patch("git_wrapper.clone", return_value=(True, None)) as dummy:
            v, r = self.git_task.task_clone_repo(print, "dummy_value3", nonexistent_path, "dummy_value4")
            self.assertTrue(v)
            dummy.assert_called_with("dummy_value3", nonexistent_path, "dummy_value4")

    def testGitPluginTaskPullRepo1(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        self.git_task.params = local_params

        nonexistent_path = path_utils.concat_path(self.test_dir, "nonexistent_path")
        self.assertFalse(os.path.exists(nonexistent_path))

        with mock.patch("git_wrapper.pull_default", return_value=(True, None)):
            v, r = self.git_task.task_pull_repo(print, nonexistent_path)
            self.assertFalse(v)

    def testGitPluginTaskPullRepo2(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        self.git_task.params = local_params

        existent_path = path_utils.concat_path(self.test_dir, "existent_path")
        os.mkdir(existent_path)
        self.assertTrue(os.path.exists(existent_path))

        with mock.patch("git_wrapper.pull_default", return_value=(True, None)) as dummy:
            v, r = self.git_task.task_pull_repo(print, existent_path)
            self.assertTrue(v)
            dummy.assert_called_with(existent_path)

    def testGitPluginTaskPortRepo1(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        self.git_task.params = local_params

        existent_path2 = path_utils.concat_path(self.test_dir, "existent_path2")
        os.mkdir(existent_path2)
        self.assertTrue(os.path.exists(existent_path2))

        prev_count = "0"

        with mock.patch("port_git_repo.port_git_repo", return_value=(True, None)) as dummy:
            v, r = self.git_task.task_port_repo(print, None, existent_path2, prev_count)
            self.assertFalse(v)

    def testGitPluginTaskPortRepo2(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        self.git_task.params = local_params

        nonexistent_path1 = path_utils.concat_path(self.test_dir, "nonexistent_path1")
        self.assertFalse(os.path.exists(nonexistent_path1))

        existent_path2 = path_utils.concat_path(self.test_dir, "existent_path2")
        os.mkdir(existent_path2)
        self.assertTrue(os.path.exists(existent_path2))

        prev_count = "0"

        with mock.patch("port_git_repo.port_git_repo", return_value=(True, None)) as dummy:
            v, r = self.git_task.task_port_repo(print, nonexistent_path1, existent_path2, prev_count)
            self.assertFalse(v)

    def testGitPluginTaskPortRepo3(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        self.git_task.params = local_params

        nonexistent_path1 = path_utils.concat_path(self.test_dir, "nonexistent_path1")
        self.assertFalse(os.path.exists(nonexistent_path1))

        existent_path2 = path_utils.concat_path(self.test_dir, "existent_path2")
        os.mkdir(existent_path2)
        self.assertTrue(os.path.exists(existent_path2))

        prev_count = "0"

        with mock.patch("port_git_repo.port_git_repo", return_value=(True, None)) as dummy:
            v, r = self.git_task.task_port_repo(print, existent_path2, nonexistent_path1, prev_count)
            self.assertFalse(v)

    def testGitPluginTaskPortRepo4(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        self.git_task.params = local_params

        existent_path1 = path_utils.concat_path(self.test_dir, "existent_path1")
        os.mkdir(existent_path1)
        self.assertTrue(os.path.exists(existent_path1))

        existent_path2 = path_utils.concat_path(self.test_dir, "existent_path2")
        os.mkdir(existent_path2)
        self.assertTrue(os.path.exists(existent_path2))

        prev_count = "a"

        with mock.patch("port_git_repo.port_git_repo", return_value=(True, None)) as dummy:
            v, r = self.git_task.task_port_repo(print, existent_path1, existent_path2, prev_count)
            self.assertFalse(v)

    def testGitPluginTaskPortRepo5(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        self.git_task.params = local_params

        existent_path1 = path_utils.concat_path(self.test_dir, "existent_path1")
        os.mkdir(existent_path1)
        self.assertTrue(os.path.exists(existent_path1))

        existent_path2 = path_utils.concat_path(self.test_dir, "existent_path2")
        os.mkdir(existent_path2)
        self.assertTrue(os.path.exists(existent_path2))

        prev_count = "0"

        with mock.patch("port_git_repo.port_git_repo", return_value=(True, None)) as dummy:
            v, r = self.git_task.task_port_repo(print, existent_path1, existent_path2, prev_count)
            self.assertTrue(v)
            dummy.assert_called_with(existent_path1, existent_path2, True, True, False, True, 0) # mvtodo: adapt

    def testGitPluginTaskResetRepo1(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        self.git_task.params = local_params

        nonexistent_path1 = path_utils.concat_path(self.test_dir, "nonexistent_path1")
        self.assertFalse(os.path.exists(nonexistent_path1))

        with mock.patch("reset_git_repo.reset_git_repo", return_value=(True, [])) as dummy:
            v, r = self.git_task.task_reset_repo(print, nonexistent_path1)
            self.assertFalse(v)

    def testGitPluginTaskResetRepo2(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        self.git_task.params = local_params

        existent_path1 = path_utils.concat_path(self.test_dir, "existent_path1")
        os.mkdir(existent_path1)
        self.assertTrue(os.path.exists(existent_path1))

        with mock.patch("reset_git_repo.reset_git_repo", return_value=(True, [])) as dummy:
            v, r = self.git_task.task_reset_repo(print, existent_path1)
            self.assertTrue(v)
            dummy.assert_called_with(existent_path1, None)

    def testGitPluginTaskResetFile1(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        self.git_task.params = local_params

        nonexistent_path1 = path_utils.concat_path(self.test_dir, "nonexistent_path1")
        self.assertFalse(os.path.exists(nonexistent_path1))

        valid_file = path_utils.concat_path(nonexistent_path1, "file1.txt")

        with mock.patch("reset_git_repo.reset_git_repo", return_value=(True, [])) as dummy:
            v, r = self.git_task.task_reset_file(print, nonexistent_path1, valid_file)
            self.assertFalse(v)

    def testGitPluginTaskResetFile2(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        self.git_task.params = local_params

        existent_path1 = path_utils.concat_path(self.test_dir, "existent_path1")
        os.mkdir(existent_path1)
        self.assertTrue(os.path.exists(existent_path1))

        with mock.patch("reset_git_repo.reset_git_repo", return_value=(True, [])) as dummy:
            v, r = self.git_task.task_reset_file(print, existent_path1, None)
            self.assertFalse(v)

    def testGitPluginTaskResetFile3(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        self.git_task.params = local_params

        existent_path1 = path_utils.concat_path(self.test_dir, "existent_path1")
        os.mkdir(existent_path1)
        self.assertTrue(os.path.exists(existent_path1))

        valid_file = path_utils.concat_path(existent_path1, "file1.txt")

        with mock.patch("reset_git_repo.reset_git_repo", return_value=(True, [])) as dummy:
            v, r = self.git_task.task_reset_file(print, existent_path1, valid_file)
            self.assertTrue(v)
            dummy.assert_called_with(existent_path1, [valid_file])

    def testGitPluginTaskResetFile4(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        self.git_task.params = local_params

        existent_path1 = path_utils.concat_path(self.test_dir, "existent_path1")
        os.mkdir(existent_path1)
        self.assertTrue(os.path.exists(existent_path1))

        valid_file = path_utils.concat_path(existent_path1, "file1.txt")
        valid_file = [valid_file]

        with mock.patch("reset_git_repo.reset_git_repo", return_value=(True, [])) as dummy:
            v, r = self.git_task.task_reset_file(print, existent_path1, valid_file)
            self.assertTrue(v)
            dummy.assert_called_with(existent_path1, valid_file)

    def testGitPluginTaskPatchRepo1(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        self.git_task.params = local_params

        nonexistent_path1 = path_utils.concat_path(self.test_dir, "nonexistent_path1")
        self.assertFalse(os.path.exists(nonexistent_path1))

        with mock.patch("apply_git_patch.apply_git_patch", return_value=(True, None)) as dummy:
            v, r = self.git_task.task_patch_repo(print, nonexistent_path1, None, None, None, None, None)
            self.assertFalse(v)

    def testGitPluginTaskPatchRepo2(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        self.git_task.params = local_params

        existent_path1 = path_utils.concat_path(self.test_dir, "existent_path1")
        os.mkdir(existent_path1)
        self.assertTrue(os.path.exists(existent_path1))

        nonexistent_path1 = path_utils.concat_path(self.test_dir, "nonexistent_path1")
        self.assertFalse(os.path.exists(nonexistent_path1))

        with mock.patch("apply_git_patch.apply_git_patch", return_value=(True, None)) as dummy:
            v, r = self.git_task.task_patch_repo(print, existent_path1, None, None, None, nonexistent_path1, None)
            self.assertFalse(v)

    def testGitPluginTaskPatchRepo3(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        self.git_task.params = local_params

        existent_path1 = path_utils.concat_path(self.test_dir, "existent_path1")
        os.mkdir(existent_path1)
        self.assertTrue(os.path.exists(existent_path1))

        with mock.patch("apply_git_patch.apply_git_patch", return_value=(True, None)) as dummy:
            v, r = self.git_task.task_patch_repo(print, existent_path1, None, None, None, None, None)
            self.assertTrue(v)
            dummy.assert_called_with(existent_path1, [], [], [], [])

    def testGitPluginTaskPatchRepo4(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        self.git_task.params = local_params

        existent_path1 = path_utils.concat_path(self.test_dir, "existent_path1")
        os.mkdir(existent_path1)
        self.assertTrue(os.path.exists(existent_path1))

        head_patch = path_utils.concat_path(existent_path1, "file1.txt")
        staged_patch = path_utils.concat_path(existent_path1, "file2.txt")
        stash_patch = path_utils.concat_path(existent_path1, "file3.txt")
        unversioned_base_folder = path_utils.concat_path(existent_path1, "unversioned")
        os.mkdir(unversioned_base_folder)
        self.assertTrue(os.path.exists(unversioned_base_folder))
        unversioned_file = "file4.txt"

        with mock.patch("apply_git_patch.apply_git_patch", return_value=(True, None)) as dummy:
            v, r = self.git_task.task_patch_repo(print, existent_path1, head_patch, staged_patch, stash_patch, unversioned_base_folder, unversioned_file)
            self.assertTrue(v)
            dummy.assert_called_with(existent_path1, [head_patch], [staged_patch], [stash_patch], [(unversioned_base_folder, path_utils.concat_path(unversioned_base_folder, unversioned_file))])

    def testGitPluginRunTask1(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        self.git_task.params = local_params

        v, r = self.git_task.run_task(print, "exe_name")
        self.assertFalse(v)

    def testGitPluginRunTask_CloneRepo1(self):

        existent_path1 = path_utils.concat_path(self.test_dir, "existent_path1")
        os.mkdir(existent_path1)
        self.assertTrue(os.path.exists(existent_path1))

        local_params = {}
        local_params["target_path"] = existent_path1
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

        existent_path1 = path_utils.concat_path(self.test_dir, "existent_path1")
        os.mkdir(existent_path1)
        self.assertTrue(os.path.exists(existent_path1))

        local_params = {}
        local_params["target_path"] = existent_path1
        local_params["operation"] = "clone_repo"
        self.git_task.params = local_params

        with mock.patch("git_plugin.CustomTask.task_clone_repo", return_value=(True, None)) as dummy:
            v, r = self.git_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(print, None, existent_path1, None)

    def testGitPluginRunTask_PullRepo1(self):

        existent_path1 = path_utils.concat_path(self.test_dir, "existent_path1")
        os.mkdir(existent_path1)
        self.assertTrue(os.path.exists(existent_path1))

        local_params = {}
        local_params["target_path"] = existent_path1
        local_params["operation"] = "pull_repo"
        self.git_task.params = local_params

        with mock.patch("git_plugin.CustomTask.task_pull_repo", return_value=(True, None)) as dummy:
            v, r = self.git_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(print, existent_path1)

    def testGitPluginRunTask_PortRepo1(self):

        existent_path1 = path_utils.concat_path(self.test_dir, "existent_path1")
        os.mkdir(existent_path1)
        self.assertTrue(os.path.exists(existent_path1))

        local_params = {}
        local_params["target_path"] = existent_path1
        local_params["operation"] = "port_repo"
        local_params["source_path"] = "dummy_value1"
        local_params["previous_count"] = "dummy_value2"
        self.git_task.params = local_params

        with mock.patch("git_plugin.CustomTask.task_port_repo", return_value=(True, None)) as dummy:
            v, r = self.git_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(print, "dummy_value1", existent_path1, "dummy_value2")

    def testGitPluginRunTask_PortRepo2(self):

        existent_path1 = path_utils.concat_path(self.test_dir, "existent_path1")
        os.mkdir(existent_path1)
        self.assertTrue(os.path.exists(existent_path1))

        local_params = {}
        local_params["target_path"] = existent_path1
        local_params["operation"] = "port_repo"
        self.git_task.params = local_params

        with mock.patch("git_plugin.CustomTask.task_port_repo", return_value=(True, None)) as dummy:
            v, r = self.git_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(print, None, existent_path1, None)

    # mvtodo: extra port repo tests after new options are implemented {run_task related}

    def testGitPluginRunTask_ResetRepo1(self):

        existent_path1 = path_utils.concat_path(self.test_dir, "existent_path1")
        os.mkdir(existent_path1)
        self.assertTrue(os.path.exists(existent_path1))

        local_params = {}
        local_params["target_path"] = existent_path1
        local_params["operation"] = "reset_repo"
        self.git_task.params = local_params

        with mock.patch("git_plugin.CustomTask.task_reset_repo", return_value=(True, None)) as dummy:
            v, r = self.git_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(print, existent_path1)

    def testGitPluginRunTask_ResetFile1(self):

        existent_path1 = path_utils.concat_path(self.test_dir, "existent_path1")
        os.mkdir(existent_path1)
        self.assertTrue(os.path.exists(existent_path1))

        local_params = {}
        local_params["target_path"] = existent_path1
        local_params["operation"] = "reset_file"
        local_params["reset_file"] = "dummy_value1"
        self.git_task.params = local_params

        with mock.patch("git_plugin.CustomTask.task_reset_file", return_value=(True, None)) as dummy:
            v, r = self.git_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(print, existent_path1, "dummy_value1")

    def testGitPluginRunTask_ResetFile2(self):

        existent_path1 = path_utils.concat_path(self.test_dir, "existent_path1")
        os.mkdir(existent_path1)
        self.assertTrue(os.path.exists(existent_path1))

        local_params = {}
        local_params["target_path"] = existent_path1
        local_params["operation"] = "reset_file"
        local_params["reset_file"] = ["dummy_value1", "dummy_value2"]
        self.git_task.params = local_params

        with mock.patch("git_plugin.CustomTask.task_reset_file", return_value=(True, None)) as dummy:
            v, r = self.git_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(print, existent_path1, ["dummy_value1", "dummy_value2"])

    def testGitPluginRunTask_ResetFile3(self):

        existent_path1 = path_utils.concat_path(self.test_dir, "existent_path1")
        os.mkdir(existent_path1)
        self.assertTrue(os.path.exists(existent_path1))

        local_params = {}
        local_params["target_path"] = existent_path1
        local_params["operation"] = "reset_file"
        self.git_task.params = local_params

        with mock.patch("git_plugin.CustomTask.task_reset_file", return_value=(True, None)) as dummy:
            v, r = self.git_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(print, existent_path1, None)

    def testGitPluginRunTask_PatchRepo1(self):

        existent_path1 = path_utils.concat_path(self.test_dir, "existent_path1")
        os.mkdir(existent_path1)
        self.assertTrue(os.path.exists(existent_path1))

        local_params = {}
        local_params["target_path"] = existent_path1
        local_params["operation"] = "patch_repo"
        self.git_task.params = local_params

        with mock.patch("git_plugin.CustomTask.task_patch_repo", return_value=(True, None)) as dummy:
            v, r = self.git_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(print, existent_path1, None, None, None, None, None)

    def testGitPluginRunTask_PatchRepo2(self):

        existent_path1 = path_utils.concat_path(self.test_dir, "existent_path1")
        os.mkdir(existent_path1)
        self.assertTrue(os.path.exists(existent_path1))

        local_params = {}
        local_params["target_path"] = existent_path1
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
            dummy.assert_called_with(print, existent_path1, "dummy_value1", "dummy_value2", "dummy_value3", "dummy_value4", "dummy_value5")

if __name__ == '__main__':
    unittest.main()
