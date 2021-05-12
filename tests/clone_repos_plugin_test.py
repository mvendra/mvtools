#!/usr/bin/env python3

import sys
import os
import shutil
import unittest

import create_and_write_file
import mvtools_test_fixture
import path_utils
import git_wrapper

import clone_repos_plugin

class CloneReposPluginTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("clone_repos_plugin_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        self.source_path = path_utils.concat_path(self.test_dir, "source_path")
        self.dest_path = path_utils.concat_path(self.test_dir, "dest_path")
        os.mkdir(self.source_path)
        os.mkdir(self.dest_path)
        if not os.path.exists(self.source_path):
            return False, "Failed creating test folder (source_path): [%s]" % self.source_path
        if not os.path.exists(self.dest_path):
            return False, "Failed creating test folder (dest_path): [%s]" % self.dest_path

        # first repo
        self.first_repo = path_utils.concat_path(self.source_path, "first")
        v, r = git_wrapper.init(self.source_path, "first", True)
        if not v:
            return v, r

        # second repo
        self.second_repo = path_utils.concat_path(self.source_path, "second")
        v, r = git_wrapper.clone(self.first_repo, self.second_repo)
        if not v:
            return v, r
        test_file = path_utils.concat_path(self.second_repo, "test_file.txt")
        if not create_and_write_file.create_file_contents(test_file, "test-contents"):
            return False, "Failed creating test file %s" % test_file
        v, r = git_wrapper.stage(self.second_repo, [path_utils.basename_filtered(test_file)])
        if not v:
            return False, r
        v, r = git_wrapper.commit(self.second_repo, "test commit msg1")
        if not v:
            return False, r
        v, r = git_wrapper.push(self.second_repo, "origin", "master")
        if not v:
            return False, r

        # third repo
        self.source_sub1 = path_utils.concat_path(self.source_path, "sub1")
        os.mkdir(self.source_sub1)
        if not os.path.exists(self.source_sub1):
            return False, "Failed creating test folder %s" % self.source_sub1
        self.source_sub2 = path_utils.concat_path(self.source_sub1, "sub2")
        os.mkdir(self.source_sub2)
        if not os.path.exists(self.source_sub2):
            return False, "Failed creating test folder %s" % self.source_sub2
        self.third_repo = path_utils.concat_path(self.source_sub2, "   third   ")
        v, r = git_wrapper.init(self.source_sub2, "   third   ", True)
        if not v:
            return v, r

        # the test task
        self.clone_repo_task = clone_repos_plugin.CustomTask()

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testCloneReposPluginEmptyFail1(self):

        local_params = {}
        self.clone_repo_task.params = local_params

        v, r = self.clone_repo_task.run_task(print, "exe_name")
        self.assertFalse(v)

    def testCloneReposPluginEmptyFail2(self):

        local_params = {}
        local_params["source_path"] = self.source_path
        self.clone_repo_task.params = local_params

        v, r = self.clone_repo_task.run_task(print, "exe_name")
        self.assertFalse(v)

    def testCloneReposPluginEmptyFail3(self):

        local_params = {}
        local_params["source_path"] = self.source_path
        local_params["dest_path"] = self.dest_path
        self.clone_repo_task.params = local_params

        v, r = self.clone_repo_task.run_task(print, "exe_name")
        self.assertFalse(v)

    def testCloneReposPluginEmptyFail4(self):

        local_params = {}
        local_params["source_path"] = self.source_path
        local_params["dest_path"] = self.dest_path
        local_params["accepted_repo_type"] = "git/bare"
        self.clone_repo_task.params = local_params

        v, r = self.clone_repo_task.run_task(print, "exe_name")
        self.assertFalse(v)

    def testCloneReposPluginEmptyFail5(self):

        local_params = {}
        local_params["source_path"] = self.source_path
        local_params["dest_path"] = self.dest_path
        local_params["accepted_repo_type"] = "git/bare"
        local_params["bare_clone"] = "no"
        self.clone_repo_task.params = local_params

        v, r = self.clone_repo_task.run_task(print, "exe_name")
        self.assertFalse(v)

    def testCloneReposPluginVanilla1(self):

        local_params = {}
        local_params["source_path"] = self.source_path
        local_params["dest_path"] = self.dest_path
        local_params["accepted_repo_type"] = "git/bare"
        local_params["bare_clone"] = "yes"
        self.clone_repo_task.params = local_params

        v, r = self.clone_repo_task.run_task(print, "exe_name")
        self.assertTrue(v)
        dest_first_objects = path_utils.concat_path(self.dest_path, path_utils.basename_filtered(self.first_repo), "objects")
        dest_third_objects = path_utils.concat_path(self.dest_path, path_utils.basename_filtered(self.source_sub1), path_utils.basename_filtered(self.source_sub2), path_utils.basename_filtered(self.third_repo), "objects")
        self.assertTrue( os.path.exists(dest_first_objects) )
        self.assertTrue( os.path.exists(dest_third_objects) )

    def testCloneReposPluginVanilla2(self):

        local_params = {}
        local_params["source_path"] = self.source_path
        local_params["dest_path"] = self.dest_path
        local_params["accepted_repo_type"] = "git/bare"
        local_params["bare_clone"] = "no"
        local_params["remote_name"] = "test_remote"
        self.clone_repo_task.params = local_params

        v, r = self.clone_repo_task.run_task(print, "exe_name")
        self.assertTrue(v)
        test_file_first_repo = path_utils.concat_path(self.dest_path, path_utils.basename_filtered(self.first_repo), "test_file.txt")
        print(test_file_first_repo)
        self.assertTrue( os.path.exists(test_file_first_repo) )

    def testCloneReposPluginCheckFail1(self):

        local_params = {}
        local_params["source_path"] = self.source_path
        local_params["dest_path"] = self.dest_path
        local_params["accepted_repo_type"] = "git/bare"
        local_params["bare_clone"] = "yes"
        self.clone_repo_task.params = local_params

        dest_third_sub1 = path_utils.concat_path(self.dest_path, path_utils.basename_filtered(self.source_sub1))
        self.assertFalse( os.path.exists(dest_third_sub1))
        os.mkdir(dest_third_sub1)
        self.assertTrue( os.path.exists(dest_third_sub1))

        v, r = self.clone_repo_task.run_task(print, "exe_name")
        self.assertFalse(v)

if __name__ == '__main__':
    unittest.main()
