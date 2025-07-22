#!/usr/bin/env python3

import sys
import os
import shutil
import unittest

import mvtools_test_fixture
import create_and_write_file
import path_utils

import check_path_plugin

class CheckPathPluginTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("check_path_plugin_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # test paths

        # existent file 1
        self.existent_file1 = path_utils.concat_path(self.test_dir, "existent_file1.txt")
        create_and_write_file.create_file_contents(self.existent_file1, "contents")

        # existent file 2
        self.existent_file2 = path_utils.concat_path(self.test_dir, "existent_file2.txt")
        create_and_write_file.create_file_contents(self.existent_file2, "contents")

        # existent dir 1
        self.existent_dir1 = path_utils.concat_path(self.test_dir, "existent_dir1")
        os.mkdir(self.existent_dir1)

        # existent dir 2
        self.existent_dir2 = path_utils.concat_path(self.test_dir, "existent_dir2")
        os.mkdir(self.existent_dir2)

        # nonexistent path 1
        self.nonexistent_path1 = path_utils.concat_path(self.test_dir, "nonexistent_path1")

        # nonexistent path 2
        self.nonexistent_path2 = path_utils.concat_path(self.test_dir, "nonexistent_path2")

        # the test task
        self.check_path_task = check_path_plugin.CustomTask()

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testCheckPathReadParams1(self):

        local_params = {}
        self.check_path_task.params = local_params

        v, r = self.check_path_task._read_params()
        self.assertFalse(v)

    def testCheckPathReadParams2(self):

        local_params = {}
        local_params["path_file_exist"] = "dummy_value1"
        self.check_path_task.params = local_params

        v, r = self.check_path_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, (["dummy_value1"], None, None))

    def testCheckPathReadParams3(self):

        local_params = {}
        local_params["path_file_exist"] = ["dummy_value1", "dummy_value2"]
        self.check_path_task.params = local_params

        v, r = self.check_path_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, (["dummy_value1", "dummy_value2"], None, None))

    def testCheckPathReadParams4(self):

        local_params = {}
        local_params["path_file_exist"] = ["dummy_value1", "dummy_value2"]
        local_params["path_dir_exist"] = "dummy_value3"
        self.check_path_task.params = local_params

        v, r = self.check_path_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, (["dummy_value1", "dummy_value2"], ["dummy_value3"], None))

    def testCheckPathReadParams5(self):

        local_params = {}
        local_params["path_file_exist"] = ["dummy_value1", "dummy_value2"]
        local_params["path_dir_exist"] = ["dummy_value3", "dummy_value4"]
        self.check_path_task.params = local_params

        v, r = self.check_path_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, (["dummy_value1", "dummy_value2"], ["dummy_value3", "dummy_value4"], None))

    def testCheckPathReadParams6(self):

        local_params = {}
        local_params["path_file_exist"] = ["dummy_value1", "dummy_value2"]
        local_params["path_dir_exist"] = ["dummy_value3", "dummy_value4"]
        local_params["path_not_exist"] = "dummy_value5"
        self.check_path_task.params = local_params

        v, r = self.check_path_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, (["dummy_value1", "dummy_value2"], ["dummy_value3", "dummy_value4"], ["dummy_value5"]))

    def testCheckPathReadParams7(self):

        local_params = {}
        local_params["path_file_exist"] = ["dummy_value1", "dummy_value2"]
        local_params["path_dir_exist"] = ["dummy_value3", "dummy_value4"]
        local_params["path_not_exist"] = ["dummy_value5", "dummy_value6"]
        self.check_path_task.params = local_params

        v, r = self.check_path_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, (["dummy_value1", "dummy_value2"], ["dummy_value3", "dummy_value4"], ["dummy_value5", "dummy_value6"]))

    def testCheckPathPluginRunTask1(self):

        local_params = {}
        self.check_path_task.params = local_params

        v, r = self.check_path_task.run_task(print, "exe_name")
        self.assertFalse(v)

    def testCheckPathPluginRunTask2(self):

        local_params = {}
        local_params["path_file_exist"] = self.existent_file1
        self.check_path_task.params = local_params

        v, r = self.check_path_task.run_task(print, "exe_name")
        self.assertTrue(v)
        self.assertEqual(r, None)

    def testCheckPathPluginRunTask3(self):

        local_params = {}
        local_params["path_file_exist"] = [self.existent_file1, self.existent_file2]
        self.check_path_task.params = local_params

        v, r = self.check_path_task.run_task(print, "exe_name")
        self.assertTrue(v)
        self.assertEqual(r, None)

    def testCheckPathPluginRunTask4(self):

        local_params = {}
        local_params["path_file_exist"] = self.nonexistent_path1
        self.check_path_task.params = local_params

        v, r = self.check_path_task.run_task(print, "exe_name")
        self.assertFalse(v)
        self.assertEqual(len(r), 1)

    def testCheckPathPluginRunTask5(self):

        local_params = {}
        local_params["path_file_exist"] = [self.nonexistent_path1, self.nonexistent_path2]
        self.check_path_task.params = local_params

        v, r = self.check_path_task.run_task(print, "exe_name")
        self.assertFalse(v)
        self.assertEqual(len(r), 2)

    def testCheckPathPluginRunTask6(self):

        local_params = {}
        local_params["path_file_exist"] = [self.existent_file1, self.nonexistent_path2]
        self.check_path_task.params = local_params

        v, r = self.check_path_task.run_task(print, "exe_name")
        self.assertFalse(v)
        self.assertEqual(len(r), 1)

    def testCheckPathPluginRunTask7(self):

        local_params = {}
        local_params["path_file_exist"] = self.existent_dir1
        self.check_path_task.params = local_params

        v, r = self.check_path_task.run_task(print, "exe_name")
        self.assertFalse(v)
        self.assertEqual(len(r), 1)

    def testCheckPathPluginRunTask8(self):

        local_params = {}
        local_params["path_file_exist"] = [self.existent_dir1, self.existent_dir2]
        self.check_path_task.params = local_params

        v, r = self.check_path_task.run_task(print, "exe_name")
        self.assertFalse(v)
        self.assertEqual(len(r), 2)

    def testCheckPathPluginRunTask9(self):

        local_params = {}
        local_params["path_file_exist"] = [self.existent_file1, self.existent_dir2]
        self.check_path_task.params = local_params

        v, r = self.check_path_task.run_task(print, "exe_name")
        self.assertFalse(v)
        self.assertEqual(len(r), 1)

    def testCheckPathPluginRunTask10(self):

        local_params = {}
        local_params["path_dir_exist"] = self.existent_file1
        self.check_path_task.params = local_params

        v, r = self.check_path_task.run_task(print, "exe_name")
        self.assertFalse(v)
        self.assertEqual(len(r), 1)

    def testCheckPathPluginRunTask11(self):

        local_params = {}
        local_params["path_dir_exist"] = [self.existent_file1, self.existent_file2]
        self.check_path_task.params = local_params

        v, r = self.check_path_task.run_task(print, "exe_name")
        self.assertFalse(v)
        self.assertEqual(len(r), 2)

    def testCheckPathPluginRunTask12(self):

        local_params = {}
        local_params["path_dir_exist"] = self.nonexistent_path1
        self.check_path_task.params = local_params

        v, r = self.check_path_task.run_task(print, "exe_name")
        self.assertFalse(v)
        self.assertEqual(len(r), 1)

    def testCheckPathPluginRunTask13(self):

        local_params = {}
        local_params["path_dir_exist"] = [self.nonexistent_path1, self.nonexistent_path2]
        self.check_path_task.params = local_params

        v, r = self.check_path_task.run_task(print, "exe_name")
        self.assertFalse(v)
        self.assertEqual(len(r), 2)

    def testCheckPathPluginRunTask14(self):

        local_params = {}
        local_params["path_dir_exist"] = [self.existent_file1, self.nonexistent_path2]
        self.check_path_task.params = local_params

        v, r = self.check_path_task.run_task(print, "exe_name")
        self.assertFalse(v)
        self.assertEqual(len(r), 2)

    def testCheckPathPluginRunTask15(self):

        local_params = {}
        local_params["path_dir_exist"] = self.existent_dir1
        self.check_path_task.params = local_params

        v, r = self.check_path_task.run_task(print, "exe_name")
        self.assertTrue(v)
        self.assertEqual(r, None)

    def testCheckPathPluginRunTask16(self):

        local_params = {}
        local_params["path_dir_exist"] = [self.existent_dir1, self.existent_dir2]
        self.check_path_task.params = local_params

        v, r = self.check_path_task.run_task(print, "exe_name")
        self.assertTrue(v)
        self.assertEqual(r, None)

    def testCheckPathPluginRunTask17(self):

        local_params = {}
        local_params["path_dir_exist"] = [self.existent_file1, self.existent_dir2]
        self.check_path_task.params = local_params

        v, r = self.check_path_task.run_task(print, "exe_name")
        self.assertFalse(v)
        self.assertEqual(len(r), 1)

    def testCheckPathPluginRunTask18(self):

        local_params = {}
        local_params["path_not_exist"] = self.existent_file1
        self.check_path_task.params = local_params

        v, r = self.check_path_task.run_task(print, "exe_name")
        self.assertFalse(v)
        self.assertEqual(len(r), 1)

    def testCheckPathPluginRunTask19(self):

        local_params = {}
        local_params["path_not_exist"] = [self.existent_file1, self.existent_file2]
        self.check_path_task.params = local_params

        v, r = self.check_path_task.run_task(print, "exe_name")
        self.assertFalse(v)
        self.assertEqual(len(r), 2)

    def testCheckPathPluginRunTask20(self):

        local_params = {}
        local_params["path_not_exist"] = self.nonexistent_path1
        self.check_path_task.params = local_params

        v, r = self.check_path_task.run_task(print, "exe_name")
        self.assertTrue(v)
        self.assertEqual(r, None)

    def testCheckPathPluginRunTask21(self):

        local_params = {}
        local_params["path_not_exist"] = [self.nonexistent_path1, self.nonexistent_path2]
        self.check_path_task.params = local_params

        v, r = self.check_path_task.run_task(print, "exe_name")
        self.assertTrue(v)
        self.assertEqual(r, None)

    def testCheckPathPluginRunTask22(self):

        local_params = {}
        local_params["path_not_exist"] = [self.existent_file1, self.nonexistent_path2]
        self.check_path_task.params = local_params

        v, r = self.check_path_task.run_task(print, "exe_name")
        self.assertFalse(v)
        self.assertEqual(len(r), 1)

    def testCheckPathPluginRunTask23(self):

        local_params = {}
        local_params["path_not_exist"] = self.existent_dir1
        self.check_path_task.params = local_params

        v, r = self.check_path_task.run_task(print, "exe_name")
        self.assertFalse(v)
        self.assertEqual(len(r), 1)

    def testCheckPathPluginRunTask24(self):

        local_params = {}
        local_params["path_not_exist"] = [self.existent_dir1, self.existent_dir2]
        self.check_path_task.params = local_params

        v, r = self.check_path_task.run_task(print, "exe_name")
        self.assertFalse(v)
        self.assertEqual(len(r), 2)

    def testCheckPathPluginRunTask25(self):

        local_params = {}
        local_params["path_not_exist"] = [self.existent_file1, self.existent_dir2]
        self.check_path_task.params = local_params

        v, r = self.check_path_task.run_task(print, "exe_name")
        self.assertFalse(v)
        self.assertEqual(len(r), 2)

if __name__ == "__main__":
    unittest.main()
