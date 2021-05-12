#!/usr/bin/env python3

import sys
import os
import shutil
import unittest

import mvtools_test_fixture
import path_utils
import mvtools_envvars

import check_envvars_plugin

class CheckEnvvarsPluginTest(unittest.TestCase):

    def setUp(self):
        self.mvtools_envvars_inst = mvtools_envvars.Mvtools_Envvars()
        v, r = self.mvtools_envvars_inst.make_copy_environ()
        if not v:
            self.tearDown()
            self.fail(r)
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("check_envvars_plugin_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # envvars
        v, r = mvtools_envvars.mvtools_envvar_read_test_check_envvars_plugin_reserved_1()
        if v:
            return False, "Check_Envvars_Plugin's first test envvar is defined. This test requires it to be undefined."
        self.reserved_test_env_var_1 = "$MVTOOLS_TEST_CHECK_ENVVARS_PLUGIN_RESERVED_1"

        v, r = mvtools_envvars.mvtools_envvar_read_test_check_envvars_plugin_reserved_2()
        if v:
            return False, "Check_Envvars_Plugin's second test envvar is defined. This test requires it to be undefined."
        self.reserved_test_env_var_2 = "$MVTOOLS_TEST_CHECK_ENVVARS_PLUGIN_RESERVED_2"

        # the test task
        self.check_envvars_task = check_envvars_plugin.CustomTask()

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)
        v, r = self.mvtools_envvars_inst.restore_copy_environ()
        if not v:
            self.fail(r)

    def testCheckEnvvarsPluginFail1(self):

        local_params = {}
        self.check_envvars_task.params = local_params

        v, r = self.check_envvars_task.run_task(print, "exe_name")
        self.assertFalse(v)

    def testCheckEnvvarsPluginFail2(self):

        local_params = {}
        local_params["envvar"] = (self.reserved_test_env_var_1)[1:]
        self.check_envvars_task.params = local_params

        v, r = self.check_envvars_task.run_task(print, "exe_name")
        self.assertFalse(v)

    def testCheckEnvvarsPluginFail3(self):

        local_params = {}
        local_params["envvar"] = (self.reserved_test_env_var_2)[1:]
        os.environ[ (self.reserved_test_env_var_1[1:]) ] = "test-value-1"
        self.check_envvars_task.params = local_params

        v, r = self.check_envvars_task.run_task(print, "exe_name")
        self.assertFalse(v)

    def testCheckEnvvarsPluginFail4(self):

        local_params = {}
        local_params["envvar"] = (self.reserved_test_env_var_1)[1:]
        local_params["envvar"] = (self.reserved_test_env_var_2)[1:]

        os.environ[ (self.reserved_test_env_var_1[1:]) ] = "test-value-1"

        self.check_envvars_task.params = local_params

        v, r = self.check_envvars_task.run_task(print, "exe_name")
        self.assertFalse(v)

    def testCheckEnvvarsPluginVanilla(self):

        local_params = {}
        local_params["envvar"] = (self.reserved_test_env_var_1)[1:]
        os.environ[ (self.reserved_test_env_var_1[1:]) ] = "test-value-1"
        self.check_envvars_task.params = local_params

        v, r = self.check_envvars_task.run_task(print, "exe_name")
        self.assertTrue(v)

    def testCheckEnvvarsPluginMultipleChecks(self):

        local_params = {}
        local_params["envvar"] = (self.reserved_test_env_var_1)[1:]
        local_params["envvar"] = (self.reserved_test_env_var_2)[1:]

        os.environ[ (self.reserved_test_env_var_1[1:]) ] = "test-value-1"
        os.environ[ (self.reserved_test_env_var_2[1:]) ] = "test-value-1"

        self.check_envvars_task.params = local_params

        v, r = self.check_envvars_task.run_task(print, "exe_name")
        self.assertTrue(v)

if __name__ == '__main__':
    unittest.main()
