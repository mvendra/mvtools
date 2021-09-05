#!/usr/bin/env python3

import sys
import os
import shutil
import unittest
from unittest import mock
from unittest.mock import patch

import mvtools_test_fixture
import path_utils

import svn_plugin

def _helper_task_checkout_svn_lib_checkout_autoretry(feedback_object, source_url, target_path, autobackups):
    os.mkdir(target_path)
    return True, None

class SvnPluginTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("svn_plugin_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # the test task
        self.svn_task = svn_plugin.CustomTask()

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

    def testSvnPluginReadParams1(self):

        local_params = {}
        self.svn_task.params = local_params

        v, r = self.svn_task._read_params()
        self.assertFalse(v)

    def testSvnPluginReadParams2(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        self.svn_task.params = local_params

        v, r = self.svn_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", None, None, False, False, None, None, None, None, None) )

    def testSvnPluginReadParams3(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        local_params["source_url"] = "dummy_value3"
        self.svn_task.params = local_params

        v, r = self.svn_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", "dummy_value3", None, False, False, None, None, None, None, None) )

    def testSvnPluginReadParams4(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        local_params["source_path"] = "dummy_value3"
        self.svn_task.params = local_params

        v, r = self.svn_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", None, "dummy_value3", False, False, None, None, None, None, None) )

    def testSvnPluginReadParams5(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        local_params["port_repo_head"] = "dummy_value3"
        self.svn_task.params = local_params

        v, r = self.svn_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", None, None, True, False, None, None, None, None, None) )

    def testSvnPluginReadParams6(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        local_params["port_repo_unversioned"] = "dummy_value3"
        self.svn_task.params = local_params

        v, r = self.svn_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", None, None, False, True, None, None, None, None, None) )

    def testSvnPluginReadParams7(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        local_params["port_repo_previous_count"] = "dummy_value3"
        self.svn_task.params = local_params

        v, r = self.svn_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", None, None, False, False, "dummy_value3", None, None, None, None) )

    def testSvnPluginReadParams8(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        local_params["reset_file"] = "dummy_value3"
        self.svn_task.params = local_params

        v, r = self.svn_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", None, None, False, False, None, "dummy_value3", None, None, None) )

    def testSvnPluginReadParams9(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        local_params["patch_head_file"] = "dummy_value3"
        self.svn_task.params = local_params

        v, r = self.svn_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", None, None, False, False, None, None, "dummy_value3", None, None) )

    def testSvnPluginReadParams10(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        local_params["patch_unversioned_base"] = "dummy_value3"
        self.svn_task.params = local_params

        v, r = self.svn_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", None, None, False, False, None, None, None, "dummy_value3", None) )

    def testSvnPluginReadParams11(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        local_params["patch_unversioned_file"] = "dummy_value3"
        self.svn_task.params = local_params

        v, r = self.svn_task._read_params()
        self.assertTrue(v)
        self.assertEqual( r, ("dummy_value1", "dummy_value2", None, None, False, False, None, None, None, None, "dummy_value3") )

    def testSvnPluginTaskCheckoutRepo1(self):

        self.assertFalse(os.path.exists(self.nonexistent_path1))

        with mock.patch("svn_lib.checkout_autoretry", return_value=(True, None)) as dummy:
            dummy.side_effect = _helper_task_checkout_svn_lib_checkout_autoretry
            v, r = self.svn_task.task_checkout_repo(print, None, self.nonexistent_path1)
            self.assertFalse(v)

    def testSvnPluginTaskCheckoutRepo2(self):

        source_url = "valid_url"
        self.assertTrue(os.path.exists(self.existent_path1))

        with mock.patch("svn_lib.checkout_autoretry", return_value=(True, None)) as dummy:
            dummy.side_effect = _helper_task_checkout_svn_lib_checkout_autoretry
            v, r = self.svn_task.task_checkout_repo(print, source_url, self.existent_path1)
            self.assertFalse(v)

    def testSvnPluginTaskCheckoutRepo3(self):

        source_url = "valid_url"
        self.assertFalse(os.path.exists(self.nonexistent_path1))

        with mock.patch("svn_lib.checkout_autoretry", return_value=(True, None)) as dummy:
            v, r = self.svn_task.task_checkout_repo(print, source_url, self.nonexistent_path1)
            self.assertFalse(v)

    def testSvnPluginTaskCheckoutRepo4(self):

        source_url = "valid_url"
        self.assertFalse(os.path.exists(self.nonexistent_path1))

        with mock.patch("svn_lib.checkout_autoretry", return_value=(True, None)) as dummy:
            dummy.side_effect = _helper_task_checkout_svn_lib_checkout_autoretry
            v, r = self.svn_task.task_checkout_repo(print, source_url, self.nonexistent_path1)
            self.assertTrue(v)
            dummy.assert_called_with(print, source_url, self.nonexistent_path1, True)

    def testSvnPluginTaskUpdateRepo1(self):

        self.assertFalse(os.path.exists(self.nonexistent_path1))

        with mock.patch("svn_lib.update_autorepair", return_value=(True, None)) as dummy:
            v, r = self.svn_task.task_update_repo(print, self.nonexistent_path1)
            self.assertFalse(v)

    def testSvnPluginTaskUpdateRepo2(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        with mock.patch("svn_lib.update_autorepair", return_value=(True, None)) as dummy:
            v, r = self.svn_task.task_update_repo(print, self.existent_path1)
            self.assertTrue(v)
            dummy.assert_called_with(print, self.existent_path1, True, True)

    def testSvnPluginTaskPortRepo1(self):

        self.assertTrue(os.path.exists(self.existent_path2))

        with mock.patch("port_svn_repo.port_svn_repo", return_value=(True, None)) as dummy:
            v, r = self.svn_task.task_port_repo(print, None, self.existent_path2, False, False, "0")
            self.assertFalse(v)

    def testSvnPluginTaskPortRepo2(self):

        self.assertFalse(os.path.exists(self.nonexistent_path1))
        self.assertTrue(os.path.exists(self.existent_path2))

        with mock.patch("port_svn_repo.port_svn_repo", return_value=(True, None)) as dummy:
            v, r = self.svn_task.task_port_repo(print, self.nonexistent_path1, self.existent_path2, False, False, "0")
            self.assertFalse(v)

    def testSvnPluginTaskPortRepo3(self):

        self.assertTrue(os.path.exists(self.existent_path1))
        self.assertFalse(os.path.exists(self.nonexistent_path1))

        with mock.patch("port_svn_repo.port_svn_repo", return_value=(True, None)) as dummy:
            v, r = self.svn_task.task_port_repo(print, self.existent_path1, self.nonexistent_path1, False, False, "0")
            self.assertFalse(v)

    def testSvnPluginTaskPortRepo4(self):

        self.assertTrue(os.path.exists(self.existent_path1))
        self.assertTrue(os.path.exists(self.existent_path2))

        with mock.patch("port_svn_repo.port_svn_repo", return_value=(True, None)) as dummy:
            v, r = self.svn_task.task_port_repo(print, self.existent_path1, self.existent_path2, False, False, "a")
            self.assertFalse(v)

    def testSvnPluginTaskPortRepo5(self):

        self.assertTrue(os.path.exists(self.existent_path1))
        self.assertTrue(os.path.exists(self.existent_path2))

        with mock.patch("port_svn_repo.port_svn_repo", return_value=(True, None)) as dummy:
            v, r = self.svn_task.task_port_repo(print, self.existent_path1, self.existent_path2, False, False, "0")
            self.assertTrue(v)
            dummy.assert_called_with(self.existent_path1, self.existent_path2, False, False, 0)

    def testSvnPluginTaskPortRepo6(self):

        self.assertTrue(os.path.exists(self.existent_path1))
        self.assertTrue(os.path.exists(self.existent_path2))

        with mock.patch("port_svn_repo.port_svn_repo", return_value=(True, None)) as dummy:
            v, r = self.svn_task.task_port_repo(print, self.existent_path1, self.existent_path2, True, True, "7")
            self.assertTrue(v)
            dummy.assert_called_with(self.existent_path1, self.existent_path2, True, True, 7)

    def testSvnPluginTaskResetRepo1(self):

        self.assertFalse(os.path.exists(self.nonexistent_path1))

        with mock.patch("reset_svn_repo.reset_svn_repo", return_value=(True, [])) as dummy:
            v, r = self.svn_task.task_reset_repo(print, self.nonexistent_path1)
            self.assertFalse(v)

    def testSvnPluginTaskResetRepo2(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        with mock.patch("reset_svn_repo.reset_svn_repo", return_value=(True, [])) as dummy:
            v, r = self.svn_task.task_reset_repo(print, self.existent_path1)
            self.assertTrue(v)
            dummy.assert_called_with(self.existent_path1, None)

    def testSvnPluginTaskResetFile1(self):

        self.assertFalse(os.path.exists(self.nonexistent_path1))
        valid_file = path_utils.concat_path(self.existent_path1, "fake_file.txt")

        with mock.patch("reset_svn_repo.reset_svn_repo", return_value=(True, [])) as dummy:
            v, r = self.svn_task.task_reset_file(print, self.nonexistent_path1, valid_file)
            self.assertFalse(v)

    def testSvnPluginTaskResetFile2(self):

        self.assertTrue(os.path.exists(self.existent_path1))
        valid_file = path_utils.concat_path(self.existent_path1, "fake_file.txt")

        with mock.patch("reset_svn_repo.reset_svn_repo", return_value=(True, [])) as dummy:
            v, r = self.svn_task.task_reset_file(print, self.existent_path1, None)
            self.assertFalse(v)

    def testSvnPluginTaskResetFile3(self):

        self.assertTrue(os.path.exists(self.existent_path1))
        valid_file = path_utils.concat_path(self.existent_path1, "fake_file.txt")

        with mock.patch("reset_svn_repo.reset_svn_repo", return_value=(True, [])) as dummy:
            v, r = self.svn_task.task_reset_file(print, self.existent_path1, valid_file)
            self.assertTrue(v)
            dummy.assert_called_with(self.existent_path1, [valid_file])

    def testSvnPluginTaskResetFile4(self):

        self.assertTrue(os.path.exists(self.existent_path1))
        valid_file = path_utils.concat_path(self.existent_path1, "fake_file.txt")

        with mock.patch("reset_svn_repo.reset_svn_repo", return_value=(True, [])) as dummy:
            v, r = self.svn_task.task_reset_file(print, self.existent_path1, [valid_file])
            self.assertTrue(v)
            dummy.assert_called_with(self.existent_path1, [valid_file])

    def testSvnPluginTaskPatchRepo1(self):

        self.assertFalse(os.path.exists(self.nonexistent_path1))

        with mock.patch("apply_svn_patch.apply_svn_patch", return_value=(True, [])) as dummy:
            v, r = self.svn_task.task_patch_repo(print, self.nonexistent_path1, [], None, [])
            self.assertFalse(v)

    def testSvnPluginTaskPatchRepo2(self):

        self.assertTrue(os.path.exists(self.existent_path1))
        valid_file = path_utils.concat_path(self.existent_path1, "fake_file.txt")
        uv_base = path_utils.concat_path(self.existent_path1, "uv_base_folder")
        self.assertFalse(os.path.exists(uv_base))
        uv_file = "uv_file.txt"

        with mock.patch("apply_svn_patch.apply_svn_patch", return_value=(True, [])) as dummy:
            v, r = self.svn_task.task_patch_repo(print, self.existent_path1, [valid_file], uv_base, [uv_file])
            self.assertFalse(v)

    def testSvnPluginTaskPatchRepo3(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        with mock.patch("apply_svn_patch.apply_svn_patch", return_value=(True, [])) as dummy:
            v, r = self.svn_task.task_patch_repo(print, self.existent_path1, [], None, [])
            self.assertTrue(v)
            dummy.assert_called_with(self.existent_path1, [], [])

    def testSvnPluginTaskPatchRepo4(self):

        self.assertTrue(os.path.exists(self.existent_path1))
        valid_file = path_utils.concat_path(self.existent_path1, "fake_file.txt")
        uv_base = path_utils.concat_path(self.existent_path1, "uv_base_folder")
        os.mkdir(uv_base)
        self.assertTrue(os.path.exists(uv_base))
        uv_file = "uv_file.txt"

        with mock.patch("apply_svn_patch.apply_svn_patch", return_value=(True, [])) as dummy:
            v, r = self.svn_task.task_patch_repo(print, self.existent_path1, [valid_file], uv_base, [uv_file])
            self.assertTrue(v)
            dummy.assert_called_with(self.existent_path1, [valid_file], [(uv_base, path_utils.concat_path(uv_base, uv_file))])

    def testSvnPluginTaskCheckRepo1(self):

        self.assertFalse(os.path.exists(self.nonexistent_path1))

        with mock.patch("svn_lib.is_head_clear", return_value=(True, True)) as dummy:
            v, r = self.svn_task.task_check_repo(print, self.nonexistent_path1)
            self.assertFalse(v)

    def testSvnPluginTaskCheckRepo2(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        with mock.patch("svn_lib.is_head_clear", return_value=(False, "the-err-msg")) as dummy:
            v, r = self.svn_task.task_check_repo(print, self.existent_path1)
            self.assertFalse(v)
            self.assertTrue("the-err-msg" in r)

    def testSvnPluginTaskCheckRepo3(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        with mock.patch("svn_lib.is_head_clear", return_value=(True, False)) as dummy:
            v, r = self.svn_task.task_check_repo(print, self.existent_path1)
            self.assertFalse(v)

    def testSvnPluginTaskCheckRepo4(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        with mock.patch("svn_lib.is_head_clear", return_value=(True, True)) as dummy:
            v, r = self.svn_task.task_check_repo(print, self.existent_path1)
            self.assertTrue(v)
            dummy.assert_called_with(self.existent_path1, True)

    def testSvnPluginRunTask1(self):

        local_params = {}
        local_params["target_path"] = "dummy_value1"
        local_params["operation"] = "dummy_value2"
        self.svn_task.params = local_params

        v, r = self.svn_task.run_task(print, "exe_name")
        self.assertFalse(v)

    def testSvnPluginRunTask_CheckoutRepo1(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        local_params = {}
        local_params["target_path"] = self.existent_path1
        local_params["operation"] = "checkout_repo"
        self.svn_task.params = local_params

        with mock.patch("svn_plugin.CustomTask.task_checkout_repo", return_value=(True, None)) as dummy:
            v, r = self.svn_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(print, None, self.existent_path1)

    def testSvnPluginRunTask_CheckoutRepo2(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        local_params = {}
        local_params["target_path"] = self.existent_path1
        local_params["operation"] = "checkout_repo"
        local_params["source_url"] = "dummy_value1"
        self.svn_task.params = local_params

        with mock.patch("svn_plugin.CustomTask.task_checkout_repo", return_value=(True, None)) as dummy:
            v, r = self.svn_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(print, "dummy_value1", self.existent_path1)

    def testSvnPluginRunTask_UpdateRepo1(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        local_params = {}
        local_params["target_path"] = self.existent_path1
        local_params["operation"] = "update_repo"
        self.svn_task.params = local_params

        with mock.patch("svn_plugin.CustomTask.task_update_repo", return_value=(True, None)) as dummy:
            v, r = self.svn_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(print, self.existent_path1)

    def testSvnPluginRunTask_PortRepo1(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        local_params = {}
        local_params["target_path"] = self.existent_path1
        local_params["operation"] = "port_repo"

        self.svn_task.params = local_params

        with mock.patch("svn_plugin.CustomTask.task_port_repo", return_value=(True, None)) as dummy:
            v, r = self.svn_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(print, None, self.existent_path1, False, False, None)

    def testSvnPluginRunTask_PortRepo2(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        local_params = {}
        local_params["target_path"] = self.existent_path1
        local_params["operation"] = "port_repo"
        local_params["source_path"] = "dummy_value1"
        local_params["port_repo_head"] = "dummy_value2"
        local_params["port_repo_unversioned"] = "dummy_value3"
        local_params["port_repo_previous_count"] = "dummy_value4"

        self.svn_task.params = local_params

        with mock.patch("svn_plugin.CustomTask.task_port_repo", return_value=(True, None)) as dummy:
            v, r = self.svn_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(print, "dummy_value1", self.existent_path1, True, True, "dummy_value4")

    def testSvnPluginRunTask_ResetRepo1(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        local_params = {}
        local_params["target_path"] = self.existent_path1
        local_params["operation"] = "reset_repo"

        self.svn_task.params = local_params

        with mock.patch("svn_plugin.CustomTask.task_reset_repo", return_value=(True, None)) as dummy:
            v, r = self.svn_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(print, self.existent_path1)

    def testSvnPluginRunTask_ResetFile1(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        local_params = {}
        local_params["target_path"] = self.existent_path1
        local_params["operation"] = "reset_file"

        self.svn_task.params = local_params

        with mock.patch("svn_plugin.CustomTask.task_reset_file", return_value=(True, None)) as dummy:
            v, r = self.svn_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(print, self.existent_path1, None)

    def testSvnPluginRunTask_ResetFile2(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        local_params = {}
        local_params["target_path"] = self.existent_path1
        local_params["operation"] = "reset_file"
        local_params["reset_file"] = "dummy_value1"

        self.svn_task.params = local_params

        with mock.patch("svn_plugin.CustomTask.task_reset_file", return_value=(True, None)) as dummy:
            v, r = self.svn_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(print, self.existent_path1, "dummy_value1")

    def testSvnPluginRunTask_ResetFile3(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        local_params = {}
        local_params["target_path"] = self.existent_path1
        local_params["operation"] = "reset_file"
        local_params["reset_file"] = ["dummy_value1", "dummy_value2"]

        self.svn_task.params = local_params

        with mock.patch("svn_plugin.CustomTask.task_reset_file", return_value=(True, None)) as dummy:
            v, r = self.svn_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(print, self.existent_path1, ["dummy_value1", "dummy_value2"])

    def testSvnPluginRunTask_PatchRepo1(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        local_params = {}
        local_params["target_path"] = self.existent_path1
        local_params["operation"] = "patch_repo"
        local_params["patch_head_file"] = "dummy_value1"
        local_params["patch_unversioned_base"] = "dummy_value2"
        local_params["patch_unversioned_file"] = "dummy_value3"

        self.svn_task.params = local_params

        with mock.patch("svn_plugin.CustomTask.task_patch_repo", return_value=(True, None)) as dummy:
            v, r = self.svn_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(print, self.existent_path1, "dummy_value1", "dummy_value2", "dummy_value3")

    def testSvnPluginRunTask_PatchRepo2(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        local_params = {}
        local_params["target_path"] = self.existent_path1
        local_params["operation"] = "patch_repo"

        self.svn_task.params = local_params

        with mock.patch("svn_plugin.CustomTask.task_patch_repo", return_value=(True, None)) as dummy:
            v, r = self.svn_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(print, self.existent_path1, None, None, None)

    def testSvnPluginRunTask_CheckRepo1(self):

        self.assertTrue(os.path.exists(self.existent_path1))

        local_params = {}
        local_params["target_path"] = self.existent_path1
        local_params["operation"] = "check_repo"

        self.svn_task.params = local_params

        with mock.patch("svn_plugin.CustomTask.task_check_repo", return_value=(True, None)) as dummy:
            v, r = self.svn_task.run_task(print, "exe_name")
            self.assertTrue(v)
            dummy.assert_called_with(print, self.existent_path1)

if __name__ == '__main__':
    unittest.main()
