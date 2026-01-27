#!/usr/bin/env python

import sys
import os
import stat
import shutil
import unittest
from unittest import mock
from unittest.mock import patch

import mvtools_test_fixture
import create_and_write_file
import path_utils

import diff_plugin

class DiffPluginTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("diff_plugin_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # the test task
        self.diff_task = diff_plugin.CustomTask()

        # nonexistent
        self.nonexistent = "nonexistent_path"
        self.nonexistent_full = path_utils.concat_path(self.test_dir, self.nonexistent)

        # left path
        self.left_path = "left_path.txt"
        self.left_path_full = path_utils.concat_path(self.test_dir, self.left_path)

        # left_filter
        self.left_filter = "left_filter.py"
        self.left_filter_full = path_utils.concat_path(self.test_dir, self.left_filter)

        left_filter_contents = ""
        left_filter_contents = "#!/usr/bin/env python" + os.linesep + os.linesep
        left_filter_contents += "def filter_function(source_input, source_params):" + os.linesep
        left_filter_contents += "    return \"left filtered contents\"" + os.linesep
        create_and_write_file.create_file_contents(self.left_filter_full, left_filter_contents)
        os.chmod(self.left_filter_full, stat.S_IREAD | stat.S_IWRITE | stat.S_IXUSR)

        # right path
        self.right_path = "right_path.txt"
        self.right_path_full = path_utils.concat_path(self.test_dir, self.right_path)

        # right_filter
        self.right_filter = "right_filter.py"
        self.right_filter_full = path_utils.concat_path(self.test_dir, self.right_filter)

        right_filter_contents = ""
        right_filter_contents = "#!/usr/bin/env python" + os.linesep + os.linesep
        right_filter_contents += "def filter_function(source_input, source_params):" + os.linesep
        right_filter_contents += "    return \"right filtered contents\"" + os.linesep
        create_and_write_file.create_file_contents(self.right_filter_full, right_filter_contents)
        os.chmod(self.right_filter_full, stat.S_IREAD | stat.S_IWRITE | stat.S_IXUSR)

        # left / right
        create_and_write_file.create_file_contents(self.left_path_full, "test-left-contents")
        create_and_write_file.create_file_contents(self.right_path_full, "test-right-contents")

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testDiffPluginReadParams1(self):

        local_params = {}
        local_params["left_path"] = self.left_path_full
        self.diff_task.params = local_params

        v, r = self.diff_task._read_params()
        self.assertFalse(v)
        self.assertEqual(r, "right_path is a required parameter")

    def testDiffPluginReadParams2(self):

        local_params = {}
        local_params["left_path"] = self.left_path_full
        local_params["right_path"] = self.right_path_full
        self.diff_task.params = local_params

        v, r = self.diff_task._read_params()
        self.assertFalse(v)
        self.assertEqual(r, "mode is a required parameter")

    def testDiffPluginReadParams3(self):

        local_params = {}
        local_params["left_path"] = self.left_path_full
        local_params["right_path"] = self.right_path_full
        local_params["mode"] = "invalid"
        self.diff_task.params = local_params

        v, r = self.diff_task._read_params()
        self.assertFalse(v)
        self.assertEqual(r, "mode [invalid] is invalid")

    def testDiffPluginReadParams4(self):

        local_params = {}
        local_params["left_path"] = self.left_path
        local_params["right_path"] = self.right_path_full
        local_params["mode"] = "eq-fail"
        self.diff_task.params = local_params

        v, r = self.diff_task._read_params()
        self.assertFalse(v)
        self.assertEqual(r, "left source [%s] does not exist" % self.left_path)

    def testDiffPluginReadParams5(self):

        local_params = {}
        local_params["left_path"] = self.left_path_full
        local_params["right_path"] = self.right_path
        local_params["mode"] = "eq-fail"
        self.diff_task.params = local_params

        v, r = self.diff_task._read_params()
        self.assertFalse(v)
        self.assertEqual(r, "right source [%s] does not exist" % self.right_path)

    def testDiffPluginReadParams6(self):

        local_params = {}
        local_params["left_path"] = self.left_path_full
        local_params["left_filter"] = self.nonexistent_full
        local_params["right_path"] = self.right_path_full
        local_params["mode"] = "eq-fail"
        self.diff_task.params = local_params

        v, r = self.diff_task._read_params()
        self.assertFalse(v)
        self.assertEqual(r, "left filter script [%s] does not exist" % self.nonexistent_full)

    def testDiffPluginReadParams7(self):

        local_params = {}
        local_params["left_path"] = self.left_path_full
        local_params["right_path"] = self.right_path_full
        local_params["right_filter"] = self.nonexistent_full
        local_params["mode"] = "eq-fail"
        self.diff_task.params = local_params

        v, r = self.diff_task._read_params()
        self.assertFalse(v)
        self.assertEqual(r, "right filter script [%s] does not exist" % self.nonexistent_full)

    def testDiffPluginReadParams8(self):

        local_params = {}
        local_params["left_path"] = self.left_path_full
        local_params["left_filter"] = self.left_filter_full
        local_params["right_path"] = self.right_path_full
        local_params["mode"] = "eq-fail"
        self.diff_task.params = local_params

        v, r = self.diff_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, (self.left_path_full, [self.left_filter_full], self.right_path_full, None, "eq-fail"))

    def testDiffPluginReadParams9(self):

        local_params = {}
        local_params["left_path"] = self.left_path_full
        local_params["left_filter"] = [self.left_filter_full, "param1", "param2", "param3"]
        local_params["right_path"] = self.right_path_full
        local_params["mode"] = "eq-fail"
        self.diff_task.params = local_params

        v, r = self.diff_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, (self.left_path_full, [self.left_filter_full, "param1", "param2", "param3"], self.right_path_full, None, "eq-fail"))

    def testDiffPluginReadParams10(self):

        local_params = {}
        local_params["left_path"] = self.left_path_full
        local_params["right_path"] = self.right_path_full
        local_params["right_filter"] = self.right_filter_full
        local_params["mode"] = "eq-fail"
        self.diff_task.params = local_params

        v, r = self.diff_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, (self.left_path_full, None, self.right_path_full, [self.right_filter_full], "eq-fail"))

    def testDiffPluginReadParams11(self):

        local_params = {}
        local_params["left_path"] = self.left_path_full
        local_params["right_path"] = self.right_path_full
        local_params["right_filter"] = [self.right_filter_full, "param1", "param2", "param3"]
        local_params["mode"] = "eq-fail"
        self.diff_task.params = local_params

        v, r = self.diff_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, (self.left_path_full, None, self.right_path_full, [self.right_filter_full, "param1", "param2", "param3"], "eq-fail"))

    def testDiffPluginReadParams12(self):

        local_params = {}
        local_params["left_path"] = self.left_path_full
        local_params["right_path"] = self.right_path_full
        local_params["mode"] = "eq-fail"
        self.diff_task.params = local_params

        v, r = self.diff_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, (self.left_path_full, None, self.right_path_full, None, "eq-fail"))

    def testDiffPluginReadParams13(self):

        local_params = {}
        local_params["left_path"] = self.left_path_full
        local_params["right_path"] = self.right_path_full
        local_params["mode"] = "eq-warn"
        self.diff_task.params = local_params

        v, r = self.diff_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, (self.left_path_full, None, self.right_path_full, None, "eq-warn"))

    def testDiffPluginReadParams14(self):

        local_params = {}
        local_params["left_path"] = self.left_path_full
        local_params["right_path"] = self.right_path_full
        local_params["mode"] = "ne-fail"
        self.diff_task.params = local_params

        v, r = self.diff_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, (self.left_path_full, None, self.right_path_full, None, "ne-fail"))

    def testDiffPluginReadParams15(self):

        local_params = {}
        local_params["left_path"] = self.left_path_full
        local_params["right_path"] = self.right_path_full
        local_params["mode"] = "ne-warn"
        self.diff_task.params = local_params

        v, r = self.diff_task._read_params()
        self.assertTrue(v)
        self.assertEqual(r, (self.left_path_full, None, self.right_path_full, None, "ne-warn"))

    def testDiffPluginRunTask1(self):

        local_params = {}
        local_params["left_path"] = self.left_path_full
        local_params["left_filter"] = self.left_filter_full
        local_params["right_path"] = self.right_path_full
        local_params["mode"] = "eq-fail"
        self.diff_task.params = local_params

        with mock.patch("diff_wrapper.do_diff", return_value=(True, "mocked contents")) as dummy:
            v, r = self.diff_task.run_task(print, "exe_name")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with("left filtered contents", self.right_path_full)

    def testDiffPluginRunTask2(self):

        local_params = {}
        local_params["left_path"] = self.left_path_full
        local_params["right_path"] = self.right_path_full
        local_params["right_filter"] = self.right_filter_full
        local_params["mode"] = "eq-fail"
        self.diff_task.params = local_params

        with mock.patch("diff_wrapper.do_diff", return_value=(True, "mocked contents")) as dummy:
            v, r = self.diff_task.run_task(print, "exe_name")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(self.left_path_full, "right filtered contents")

    def testDiffPluginRunTask3(self):

        local_params = {}
        local_params["left_path"] = self.left_path_full
        local_params["right_path"] = self.right_path_full
        local_params["mode"] = "eq-fail"
        self.diff_task.params = local_params

        with mock.patch("diff_wrapper.do_diff", return_value=(True, "")) as dummy:
            v, r = self.diff_task.run_task(print, "exe_name")
            self.assertFalse(v)
            self.assertEqual(r, "contents of [%s] and [%s] are equal" % (self.left_path_full, self.right_path_full))
            dummy.assert_called_with(self.left_path_full, self.right_path_full)

    def testDiffPluginRunTask4(self):

        local_params = {}
        local_params["left_path"] = self.left_path_full
        local_params["left_filter"] = self.left_filter_full
        local_params["right_path"] = self.right_path_full
        local_params["mode"] = "eq-fail"
        self.diff_task.params = local_params

        with mock.patch("diff_wrapper.do_diff", return_value=(True, "")) as dummy:
            v, r = self.diff_task.run_task(print, "exe_name")
            self.assertFalse(v)
            self.assertEqual(r, "contents of [%s (filtered)] and [%s] are equal" % (self.left_path_full, self.right_path_full))
            dummy.assert_called_with("left filtered contents", self.right_path_full)

    def testDiffPluginRunTask5(self):

        local_params = {}
        local_params["left_path"] = self.left_path_full
        local_params["right_path"] = self.right_path_full
        local_params["right_filter"] = self.right_filter_full
        local_params["mode"] = "eq-fail"
        self.diff_task.params = local_params

        with mock.patch("diff_wrapper.do_diff", return_value=(True, "")) as dummy:
            v, r = self.diff_task.run_task(print, "exe_name")
            self.assertFalse(v)
            self.assertEqual(r, "contents of [%s] and [%s (filtered)] are equal" % (self.left_path_full, self.right_path_full))
            dummy.assert_called_with(self.left_path_full, "right filtered contents")

    def testDiffPluginRunTask6(self):

        local_params = {}
        local_params["left_path"] = self.left_path_full
        local_params["left_filter"] = self.left_filter_full
        local_params["right_path"] = self.right_path_full
        local_params["right_filter"] = self.right_filter_full
        local_params["mode"] = "eq-fail"
        self.diff_task.params = local_params

        with mock.patch("diff_wrapper.do_diff", return_value=(True, "")) as dummy:
            v, r = self.diff_task.run_task(print, "exe_name")
            self.assertFalse(v)
            self.assertEqual(r, "contents of [%s (filtered)] and [%s (filtered)] are equal" % (self.left_path_full, self.right_path_full))
            dummy.assert_called_with("left filtered contents", "right filtered contents")

    def testDiffPluginRunTask7(self):

        local_params = {}
        local_params["left_path"] = self.left_path_full
        local_params["right_path"] = self.right_path_full
        local_params["mode"] = "eq-fail"
        self.diff_task.params = local_params

        with mock.patch("diff_wrapper.do_diff", return_value=(True, "mocked contents")) as dummy:
            v, r = self.diff_task.run_task(print, "exe_name")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(self.left_path_full, self.right_path_full)

    def testDiffPluginRunTask8(self):

        local_params = {}
        local_params["left_path"] = self.left_path_full
        local_params["right_path"] = self.right_path_full
        local_params["mode"] = "eq-warn"
        self.diff_task.params = local_params

        with mock.patch("diff_wrapper.do_diff", return_value=(True, "")) as dummy:
            v, r = self.diff_task.run_task(print, "exe_name")
            self.assertTrue(v)
            self.assertEqual(r, "contents of [%s] and [%s] are equal" % (self.left_path_full, self.right_path_full))
            dummy.assert_called_with(self.left_path_full, self.right_path_full)

    def testDiffPluginRunTask9(self):

        local_params = {}
        local_params["left_path"] = self.left_path_full
        local_params["left_filter"] = self.left_filter_full
        local_params["right_path"] = self.right_path_full
        local_params["mode"] = "eq-warn"
        self.diff_task.params = local_params

        with mock.patch("diff_wrapper.do_diff", return_value=(True, "")) as dummy:
            v, r = self.diff_task.run_task(print, "exe_name")
            self.assertTrue(v)
            self.assertEqual(r, "contents of [%s (filtered)] and [%s] are equal" % (self.left_path_full, self.right_path_full))
            dummy.assert_called_with("left filtered contents", self.right_path_full)

    def testDiffPluginRunTask10(self):

        local_params = {}
        local_params["left_path"] = self.left_path_full
        local_params["right_path"] = self.right_path_full
        local_params["right_filter"] = self.right_filter_full
        local_params["mode"] = "eq-warn"
        self.diff_task.params = local_params

        with mock.patch("diff_wrapper.do_diff", return_value=(True, "")) as dummy:
            v, r = self.diff_task.run_task(print, "exe_name")
            self.assertTrue(v)
            self.assertEqual(r, "contents of [%s] and [%s (filtered)] are equal" % (self.left_path_full, self.right_path_full))
            dummy.assert_called_with(self.left_path_full, "right filtered contents")

    def testDiffPluginRunTask11(self):

        local_params = {}
        local_params["left_path"] = self.left_path_full
        local_params["left_filter"] = self.left_filter_full
        local_params["right_path"] = self.right_path_full
        local_params["right_filter"] = self.right_filter_full
        local_params["mode"] = "eq-warn"
        self.diff_task.params = local_params

        with mock.patch("diff_wrapper.do_diff", return_value=(True, "")) as dummy:
            v, r = self.diff_task.run_task(print, "exe_name")
            self.assertTrue(v)
            self.assertEqual(r, "contents of [%s (filtered)] and [%s (filtered)] are equal" % (self.left_path_full, self.right_path_full))
            dummy.assert_called_with("left filtered contents", "right filtered contents")

    def testDiffPluginRunTask12(self):

        local_params = {}
        local_params["left_path"] = self.left_path_full
        local_params["right_path"] = self.right_path_full
        local_params["mode"] = "eq-warn"
        self.diff_task.params = local_params

        with mock.patch("diff_wrapper.do_diff", return_value=(True, "mocked contents")) as dummy:
            v, r = self.diff_task.run_task(print, "exe_name")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(self.left_path_full, self.right_path_full)

    def testDiffPluginRunTask13(self):

        local_params = {}
        local_params["left_path"] = self.left_path_full
        local_params["right_path"] = self.right_path_full
        local_params["mode"] = "ne-fail"
        self.diff_task.params = local_params

        with mock.patch("diff_wrapper.do_diff", return_value=(True, "")) as dummy:
            v, r = self.diff_task.run_task(print, "exe_name")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(self.left_path_full, self.right_path_full)

    def testDiffPluginRunTask14(self):

        local_params = {}
        local_params["left_path"] = self.left_path_full
        local_params["right_path"] = self.right_path_full
        local_params["mode"] = "ne-fail"
        self.diff_task.params = local_params

        with mock.patch("diff_wrapper.do_diff", return_value=(True, "mocked contents")) as dummy:
            v, r = self.diff_task.run_task(print, "exe_name")
            self.assertFalse(v)
            self.assertEqual(r, "contents of [%s] and [%s] are not equal" % (self.left_path_full, self.right_path_full))
            dummy.assert_called_with(self.left_path_full, self.right_path_full)

    def testDiffPluginRunTask15(self):

        local_params = {}
        local_params["left_path"] = self.left_path_full
        local_params["left_filter"] = self.left_filter_full
        local_params["right_path"] = self.right_path_full
        local_params["mode"] = "ne-fail"
        self.diff_task.params = local_params

        with mock.patch("diff_wrapper.do_diff", return_value=(True, "mocked contents")) as dummy:
            v, r = self.diff_task.run_task(print, "exe_name")
            self.assertFalse(v)
            self.assertEqual(r, "contents of [%s (filtered)] and [%s] are not equal" % (self.left_path_full, self.right_path_full))
            dummy.assert_called_with("left filtered contents", self.right_path_full)

    def testDiffPluginRunTask16(self):

        local_params = {}
        local_params["left_path"] = self.left_path_full
        local_params["right_path"] = self.right_path_full
        local_params["right_filter"] = self.right_filter_full
        local_params["mode"] = "ne-fail"
        self.diff_task.params = local_params

        with mock.patch("diff_wrapper.do_diff", return_value=(True, "mocked contents")) as dummy:
            v, r = self.diff_task.run_task(print, "exe_name")
            self.assertFalse(v)
            self.assertEqual(r, "contents of [%s] and [%s (filtered)] are not equal" % (self.left_path_full, self.right_path_full))
            dummy.assert_called_with(self.left_path_full, "right filtered contents")

    def testDiffPluginRunTask17(self):

        local_params = {}
        local_params["left_path"] = self.left_path_full
        local_params["left_filter"] = self.left_filter_full
        local_params["right_path"] = self.right_path_full
        local_params["right_filter"] = self.right_filter_full
        local_params["mode"] = "ne-fail"
        self.diff_task.params = local_params

        with mock.patch("diff_wrapper.do_diff", return_value=(True, "mocked contents")) as dummy:
            v, r = self.diff_task.run_task(print, "exe_name")
            self.assertFalse(v)
            self.assertEqual(r, "contents of [%s (filtered)] and [%s (filtered)] are not equal" % (self.left_path_full, self.right_path_full))
            dummy.assert_called_with("left filtered contents", "right filtered contents")

    def testDiffPluginRunTask18(self):

        local_params = {}
        local_params["left_path"] = self.left_path_full
        local_params["right_path"] = self.right_path_full
        local_params["mode"] = "ne-warn"
        self.diff_task.params = local_params

        with mock.patch("diff_wrapper.do_diff", return_value=(True, "")) as dummy:
            v, r = self.diff_task.run_task(print, "exe_name")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called_with(self.left_path_full, self.right_path_full)

    def testDiffPluginRunTask19(self):

        local_params = {}
        local_params["left_path"] = self.left_path_full
        local_params["right_path"] = self.right_path_full
        local_params["mode"] = "ne-warn"
        self.diff_task.params = local_params

        with mock.patch("diff_wrapper.do_diff", return_value=(True, "mocked contents")) as dummy:
            v, r = self.diff_task.run_task(print, "exe_name")
            self.assertTrue(v)
            self.assertEqual(r, "contents of [%s] and [%s] are not equal" % (self.left_path_full, self.right_path_full))
            dummy.assert_called_with(self.left_path_full, self.right_path_full)

    def testDiffPluginRunTask20(self):

        local_params = {}
        local_params["left_path"] = self.left_path_full
        local_params["left_filter"] = self.left_filter_full
        local_params["right_path"] = self.right_path_full
        local_params["mode"] = "ne-warn"
        self.diff_task.params = local_params

        with mock.patch("diff_wrapper.do_diff", return_value=(True, "mocked contents")) as dummy:
            v, r = self.diff_task.run_task(print, "exe_name")
            self.assertTrue(v)
            self.assertEqual(r, "contents of [%s (filtered)] and [%s] are not equal" % (self.left_path_full, self.right_path_full))
            dummy.assert_called_with("left filtered contents", self.right_path_full)

    def testDiffPluginRunTask21(self):

        local_params = {}
        local_params["left_path"] = self.left_path_full
        local_params["right_path"] = self.right_path_full
        local_params["right_filter"] = self.right_filter_full
        local_params["mode"] = "ne-warn"
        self.diff_task.params = local_params

        with mock.patch("diff_wrapper.do_diff", return_value=(True, "mocked contents")) as dummy:
            v, r = self.diff_task.run_task(print, "exe_name")
            self.assertTrue(v)
            self.assertEqual(r, "contents of [%s] and [%s (filtered)] are not equal" % (self.left_path_full, self.right_path_full))
            dummy.assert_called_with(self.left_path_full, "right filtered contents")

    def testDiffPluginRunTask22(self):

        local_params = {}
        local_params["left_path"] = self.left_path_full
        local_params["left_filter"] = self.left_filter_full
        local_params["right_path"] = self.right_path_full
        local_params["right_filter"] = self.right_filter_full
        local_params["mode"] = "ne-warn"
        self.diff_task.params = local_params

        with mock.patch("diff_wrapper.do_diff", return_value=(True, "mocked contents")) as dummy:
            v, r = self.diff_task.run_task(print, "exe_name")
            self.assertTrue(v)
            self.assertEqual(r, "contents of [%s (filtered)] and [%s (filtered)] are not equal" % (self.left_path_full, self.right_path_full))
            dummy.assert_called_with("left filtered contents", "right filtered contents")

if __name__ == "__main__":
    unittest.main()
