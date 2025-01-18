#!/usr/bin/env python3

import sys
import os
import stat
import shutil
import unittest
from unittest import mock
from unittest.mock import patch

import path_utils
import mvtools_test_fixture
import generic_run
import batch_run

def file_get_contents(fn_full):
    contents = ""
    with open(fn_full, "r") as f:
        contents = f.read()
    return contents

def file_has_contents(fn_full, contents):
    return (file_get_contents(fn_full) == contents)

def file_create_contents(fn_full, contents):
    if os.path.exists(fn_full):
        return False
    with open(fn_full, "w") as f:
        f.write(contents)
    return True
    if not os.path.exists(fn_full):
        return False

class BatchRunTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("batch_run_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        self.scripts_folder = path_utils.concat_path(self.test_dir, "scripts_folder")
        os.mkdir(self.scripts_folder)

        self.output_folder = path_utils.concat_path(self.test_dir, "output_folder")
        os.mkdir(self.output_folder)

        self.data_folder = path_utils.concat_path(self.test_dir, "data_folder")
        os.mkdir(self.data_folder)

        self.dummy_taget = "dummy_target"
        self.dummy_taget_full = path_utils.concat_path(self.scripts_folder, self.dummy_taget)

        # first script
        self.test_script_first_content = "#!/usr/bin/env python3" + os.linesep
        self.test_script_first_content += "import os" + os.linesep
        self.test_script_first_content += "import sys" + os.linesep
        self.test_script_first_content += "import path_utils" + os.linesep
        self.test_script_first_content += "if __name__ == '__main__':" + os.linesep
        self.test_script_first_content += "    fn_full = path_utils.concat_path(\"%s\", \"counter.txt\")%s" % (self.data_folder, os.linesep)
        self.test_script_first_content += "    if not os.path.exists(fn_full):" + os.linesep
        self.test_script_first_content += "        with open(fn_full, \"w\") as f:" + os.linesep
        self.test_script_first_content += "            f.write(\"0\")" + os.linesep
        self.test_script_first_content += "        sys.exit(0)" + os.linesep
        self.test_script_first_content += "    contents = \"\"" + os.linesep
        self.test_script_first_content += "    with open(fn_full, \"r\") as f:" + os.linesep
        self.test_script_first_content += "        contents = f.read()" + os.linesep
        self.test_script_first_content += "    if contents == \"2\":" + os.linesep
        self.test_script_first_content += "        sys.stdout.write(\"script-stdout\")" + os.linesep
        self.test_script_first_content += "        sys.exit(1)" + os.linesep
        self.test_script_first_content += "    contents = str(int(contents)+1)" + os.linesep
        self.test_script_first_content += "    os.unlink(fn_full)" + os.linesep
        self.test_script_first_content += "    with open(fn_full, \"w\") as f:" + os.linesep
        self.test_script_first_content += "        f.write(contents)" + os.linesep

        self.test_script_first_full = path_utils.concat_path(self.scripts_folder, "test_first.py")
        self.assertTrue(file_create_contents(self.test_script_first_full, self.test_script_first_content))
        os.chmod(self.test_script_first_full, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)

        # second script
        self.test_script_second_content = "#!/usr/bin/env python3" + os.linesep
        self.test_script_second_content += "import os" + os.linesep
        self.test_script_second_content += "import sys" + os.linesep
        self.test_script_second_content += "import path_utils" + os.linesep
        self.test_script_second_content += "if __name__ == '__main__':" + os.linesep
        self.test_script_second_content += "    fn_full = path_utils.concat_path(\"%s\", \"counter.txt\")%s" % (self.data_folder, os.linesep)
        self.test_script_second_content += "    if not os.path.exists(fn_full):" + os.linesep
        self.test_script_second_content += "        with open(fn_full, \"w\") as f:" + os.linesep
        self.test_script_second_content += "            f.write(\"0\")" + os.linesep
        self.test_script_second_content += "        sys.exit(0)" + os.linesep
        self.test_script_second_content += "    contents = \"\"" + os.linesep
        self.test_script_second_content += "    with open(fn_full, \"r\") as f:" + os.linesep
        self.test_script_second_content += "        contents = f.read()" + os.linesep
        self.test_script_second_content += "    if contents == \"2\":" + os.linesep
        self.test_script_second_content += "        sys.stdout.write(\"script-stdout\")" + os.linesep
        self.test_script_second_content += "        sys.stderr.write(\"script-stderr\")" + os.linesep
        self.test_script_second_content += "        sys.exit(1)" + os.linesep
        self.test_script_second_content += "    contents = str(int(contents)+1)" + os.linesep
        self.test_script_second_content += "    os.unlink(fn_full)" + os.linesep
        self.test_script_second_content += "    with open(fn_full, \"w\") as f:" + os.linesep
        self.test_script_second_content += "        f.write(contents)" + os.linesep

        self.test_script_second_full = path_utils.concat_path(self.scripts_folder, "test_second.py")
        self.assertTrue(file_create_contents(self.test_script_second_full, self.test_script_second_content))
        os.chmod(self.test_script_second_full, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testStopUntilFail(self):
        self.assertEqual(batch_run._stop_until_fail(True), False)
        self.assertEqual(batch_run._stop_until_fail(False), True)

    def testSaveIter(self):

        batch_run._save_iter([self.dummy_taget_full], self.output_folder, 7, "dummy-stdout", "dummy-stderr")

        out_fn_full = path_utils.concat_path(self.output_folder, "dummy_target_stdout_7.txt")
        err_fn_full = path_utils.concat_path(self.output_folder, "dummy_target_stderr_7.txt")

        self.assertTrue(os.path.exists(out_fn_full))
        self.assertTrue(os.path.exists(err_fn_full))

        self.assertTrue(file_has_contents(out_fn_full, "dummy-stdout"))
        self.assertTrue(file_has_contents(err_fn_full, "dummy-stderr"))

    def testSaveSummary(self):

        with mock.patch("maketimestamp.get_timestamp_now", return_value="dummy-end-time") as dummy:
            batch_run._save_summary([self.dummy_taget_full], self.output_folder, 5, 2, "dummy-started-time")
            dummy.assert_called()

        sum_fn_full = path_utils.concat_path(self.output_folder, "dummy_target_summary.txt")

        self.assertTrue(os.path.exists(sum_fn_full))

        contents = file_get_contents(sum_fn_full)
        contents = contents.split("\n")

        contents_expected = []
        contents_expected.append("Run of [dummy_target] - summary:")
        contents_expected.append("--------------------------------")
        contents_expected.append("")
        contents_expected.append("Number of total executions: [5]")
        contents_expected.append("Number of failed executions: [2]")
        contents_expected.append("Started time: [dummy-started-time]")
        contents_expected.append("End time: [dummy-end-time]")
        contents_expected.append("")

        line_num = 0
        for line in contents:
            self.assertEqual(line, contents_expected[line_num])
            line_num += 1

    def testRunUntil1(self):

        dummy_gr_ret = generic_run.run_cmd_result(False, 1, "dummy-stdout", "dummy-stderr")

        with mock.patch("generic_run.run_cmd", return_value=(True, dummy_gr_ret)) as dummy1:
            with mock.patch("maketimestamp.get_timestamp_now", return_value="dummy-end-time") as dummy2:
                v, r = batch_run._run_until([self.dummy_taget_full], self.output_folder, "save-all", "dummy-started-time", batch_run._stop_until_fail)
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy1.assert_called_with([self.dummy_taget_full])
                dummy2.assert_called()

        out_fn_full = path_utils.concat_path(self.output_folder, "dummy_target_stdout_1.txt")
        err_fn_full = path_utils.concat_path(self.output_folder, "dummy_target_stderr_1.txt")

        self.assertTrue(os.path.exists(out_fn_full))
        self.assertTrue(os.path.exists(err_fn_full))

        self.assertTrue(file_has_contents(out_fn_full, "dummy-stdout"))
        self.assertTrue(file_has_contents(err_fn_full, "dummy-stderr"))

        sum_fn_full = path_utils.concat_path(self.output_folder, "dummy_target_summary.txt")

        self.assertTrue(os.path.exists(sum_fn_full))

        contents = file_get_contents(sum_fn_full)
        contents = contents.split("\n")

        contents_expected = []
        contents_expected.append("Run of [dummy_target] - summary:")
        contents_expected.append("--------------------------------")
        contents_expected.append("")
        contents_expected.append("Number of total executions: [1]")
        contents_expected.append("Number of failed executions: [1]")
        contents_expected.append("Started time: [dummy-started-time]")
        contents_expected.append("End time: [dummy-end-time]")
        contents_expected.append("")

        line_num = 0
        for line in contents:
            self.assertEqual(line, contents_expected[line_num])
            line_num += 1

    def testRunUntil2(self):

        with mock.patch("maketimestamp.get_timestamp_now", return_value="dummy-end-time") as dummy:
            v, r = batch_run._run_until([self.test_script_first_full], self.output_folder, "save-all", "dummy-started-time", batch_run._stop_until_fail)
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called()

        out1_fn_full = path_utils.concat_path(self.output_folder, "test_first.py_stdout_1.txt")
        out2_fn_full = path_utils.concat_path(self.output_folder, "test_first.py_stdout_2.txt")
        out3_fn_full = path_utils.concat_path(self.output_folder, "test_first.py_stdout_3.txt")
        out4_fn_full = path_utils.concat_path(self.output_folder, "test_first.py_stdout_4.txt")

        err1_fn_full = path_utils.concat_path(self.output_folder, "test_first.py_stderr_1.txt")
        err2_fn_full = path_utils.concat_path(self.output_folder, "test_first.py_stderr_2.txt")
        err3_fn_full = path_utils.concat_path(self.output_folder, "test_first.py_stderr_3.txt")
        err4_fn_full = path_utils.concat_path(self.output_folder, "test_first.py_stderr_4.txt")

        self.assertTrue(os.path.exists(out1_fn_full))
        self.assertTrue(os.path.exists(out2_fn_full))
        self.assertTrue(os.path.exists(out3_fn_full))
        self.assertTrue(os.path.exists(out4_fn_full))

        self.assertTrue(os.path.exists(err1_fn_full))
        self.assertTrue(os.path.exists(err2_fn_full))
        self.assertTrue(os.path.exists(err3_fn_full))
        self.assertTrue(os.path.exists(err4_fn_full))

        self.assertTrue(file_has_contents(out4_fn_full, "script-stdout"))
        self.assertTrue(file_has_contents(err4_fn_full, ""))

        sum_fn_full = path_utils.concat_path(self.output_folder, "test_first.py_summary.txt")

        self.assertTrue(os.path.exists(sum_fn_full))

        contents = file_get_contents(sum_fn_full)
        contents = contents.split("\n")

        contents_expected = []
        contents_expected.append("Run of [test_first.py] - summary:")
        contents_expected.append("---------------------------------")
        contents_expected.append("")
        contents_expected.append("Number of total executions: [4]")
        contents_expected.append("Number of failed executions: [1]")
        contents_expected.append("Started time: [dummy-started-time]")
        contents_expected.append("End time: [dummy-end-time]")
        contents_expected.append("")

        line_num = 0
        for line in contents:
            self.assertEqual(line, contents_expected[line_num])
            line_num += 1

    def testRunUntil3(self):

        with mock.patch("maketimestamp.get_timestamp_now", return_value="dummy-end-time") as dummy:
            v, r = batch_run._run_until([self.test_script_first_full], self.output_folder, "save-fail", "dummy-started-time", batch_run._stop_until_fail)
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called()

        out1_fn_full = path_utils.concat_path(self.output_folder, "test_first.py_stdout_1.txt")
        out2_fn_full = path_utils.concat_path(self.output_folder, "test_first.py_stdout_2.txt")
        out3_fn_full = path_utils.concat_path(self.output_folder, "test_first.py_stdout_3.txt")
        out4_fn_full = path_utils.concat_path(self.output_folder, "test_first.py_stdout_4.txt")

        err1_fn_full = path_utils.concat_path(self.output_folder, "test_first.py_stderr_1.txt")
        err2_fn_full = path_utils.concat_path(self.output_folder, "test_first.py_stderr_2.txt")
        err3_fn_full = path_utils.concat_path(self.output_folder, "test_first.py_stderr_3.txt")
        err4_fn_full = path_utils.concat_path(self.output_folder, "test_first.py_stderr_4.txt")

        self.assertFalse(os.path.exists(out1_fn_full))
        self.assertFalse(os.path.exists(out2_fn_full))
        self.assertFalse(os.path.exists(out3_fn_full))
        self.assertTrue(os.path.exists(out4_fn_full))

        self.assertFalse(os.path.exists(err1_fn_full))
        self.assertFalse(os.path.exists(err2_fn_full))
        self.assertFalse(os.path.exists(err3_fn_full))
        self.assertTrue(os.path.exists(err4_fn_full))

        self.assertTrue(file_has_contents(out4_fn_full, "script-stdout"))
        self.assertTrue(file_has_contents(err4_fn_full, ""))

        sum_fn_full = path_utils.concat_path(self.output_folder, "test_first.py_summary.txt")

        self.assertTrue(os.path.exists(sum_fn_full))

        contents = file_get_contents(sum_fn_full)
        contents = contents.split("\n")

        contents_expected = []
        contents_expected.append("Run of [test_first.py] - summary:")
        contents_expected.append("---------------------------------")
        contents_expected.append("")
        contents_expected.append("Number of total executions: [4]")
        contents_expected.append("Number of failed executions: [1]")
        contents_expected.append("Started time: [dummy-started-time]")
        contents_expected.append("End time: [dummy-end-time]")
        contents_expected.append("")

        line_num = 0
        for line in contents:
            self.assertEqual(line, contents_expected[line_num])
            line_num += 1

    def testRunUntil4(self):

        with mock.patch("maketimestamp.get_timestamp_now", return_value="dummy-end-time") as dummy:
            v, r = batch_run._run_until([self.test_script_second_full], self.output_folder, "save-fail", "dummy-started-time", batch_run._stop_until_fail)
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called()

        out1_fn_full = path_utils.concat_path(self.output_folder, "test_second.py_stdout_1.txt")
        out2_fn_full = path_utils.concat_path(self.output_folder, "test_second.py_stdout_2.txt")
        out3_fn_full = path_utils.concat_path(self.output_folder, "test_second.py_stdout_3.txt")
        out4_fn_full = path_utils.concat_path(self.output_folder, "test_second.py_stdout_4.txt")

        err1_fn_full = path_utils.concat_path(self.output_folder, "test_second.py_stderr_1.txt")
        err2_fn_full = path_utils.concat_path(self.output_folder, "test_second.py_stderr_2.txt")
        err3_fn_full = path_utils.concat_path(self.output_folder, "test_second.py_stderr_3.txt")
        err4_fn_full = path_utils.concat_path(self.output_folder, "test_second.py_stderr_4.txt")

        self.assertFalse(os.path.exists(out1_fn_full))
        self.assertFalse(os.path.exists(out2_fn_full))
        self.assertFalse(os.path.exists(out3_fn_full))
        self.assertTrue(os.path.exists(out4_fn_full))

        self.assertFalse(os.path.exists(err1_fn_full))
        self.assertFalse(os.path.exists(err2_fn_full))
        self.assertFalse(os.path.exists(err3_fn_full))
        self.assertTrue(os.path.exists(err4_fn_full))

        self.assertTrue(file_has_contents(out4_fn_full, "script-stdout"))
        self.assertTrue(file_has_contents(err4_fn_full, "script-stderr"))

        sum_fn_full = path_utils.concat_path(self.output_folder, "test_second.py_summary.txt")

        self.assertTrue(os.path.exists(sum_fn_full))

        contents = file_get_contents(sum_fn_full)
        contents = contents.split("\n")

        contents_expected = []
        contents_expected.append("Run of [test_second.py] - summary:")
        contents_expected.append("----------------------------------")
        contents_expected.append("")
        contents_expected.append("Number of total executions: [4]")
        contents_expected.append("Number of failed executions: [1]")
        contents_expected.append("Started time: [dummy-started-time]")
        contents_expected.append("End time: [dummy-end-time]")
        contents_expected.append("")

        line_num = 0
        for line in contents:
            self.assertEqual(line, contents_expected[line_num])
            line_num += 1

if __name__ == '__main__':
    unittest.main()
