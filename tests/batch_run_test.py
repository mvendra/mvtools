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

        # third script
        self.test_script_third_content = "#!/usr/bin/env python3" + os.linesep
        self.test_script_third_content += "import os" + os.linesep
        self.test_script_third_content += "import sys" + os.linesep
        self.test_script_third_content += "import path_utils" + os.linesep
        self.test_script_third_content += "if __name__ == '__main__':" + os.linesep
        self.test_script_third_content += "    fn_full = path_utils.concat_path(\"%s\", \"counter.txt\")%s" % (self.data_folder, os.linesep)
        self.test_script_third_content += "    if not os.path.exists(fn_full):" + os.linesep
        self.test_script_third_content += "        with open(fn_full, \"w\") as f:" + os.linesep
        self.test_script_third_content += "            f.write(\"0\")" + os.linesep
        self.test_script_third_content += "        sys.exit(0)" + os.linesep
        self.test_script_third_content += "    contents = \"\"" + os.linesep
        self.test_script_third_content += "    with open(fn_full, \"r\") as f:" + os.linesep
        self.test_script_third_content += "        contents = f.read()" + os.linesep
        self.test_script_third_content += "    contents = str(int(contents)+1)" + os.linesep
        self.test_script_third_content += "    os.unlink(fn_full)" + os.linesep
        self.test_script_third_content += "    with open(fn_full, \"w\") as f:" + os.linesep
        self.test_script_third_content += "        f.write(contents)" + os.linesep
        self.test_script_third_content += "    if contents == \"3\" or contents == \"6\":" + os.linesep
        self.test_script_third_content += "        sys.stdout.write(\"script-stdout\")" + os.linesep
        self.test_script_third_content += "        sys.exit(1)" + os.linesep

        self.test_script_third_full = path_utils.concat_path(self.scripts_folder, "test_third.py")
        self.assertTrue(file_create_contents(self.test_script_third_full, self.test_script_third_content))
        os.chmod(self.test_script_third_full, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)

        # fourth script
        self.test_script_fourth_content = "#!/usr/bin/env python3" + os.linesep
        self.test_script_fourth_content += "import os" + os.linesep
        self.test_script_fourth_content += "import sys" + os.linesep
        self.test_script_fourth_content += "import path_utils" + os.linesep
        self.test_script_fourth_content += "if __name__ == '__main__':" + os.linesep
        self.test_script_fourth_content += "    fn_full = path_utils.concat_path(\"%s\", \"counter.txt\")%s" % (self.data_folder, os.linesep)
        self.test_script_fourth_content += "    if not os.path.exists(fn_full):" + os.linesep
        self.test_script_fourth_content += "        with open(fn_full, \"w\") as f:" + os.linesep
        self.test_script_fourth_content += "            f.write(\"0\")" + os.linesep
        self.test_script_fourth_content += "        sys.exit(0)" + os.linesep
        self.test_script_fourth_content += "    contents = \"\"" + os.linesep
        self.test_script_fourth_content += "    with open(fn_full, \"r\") as f:" + os.linesep
        self.test_script_fourth_content += "        contents = f.read()" + os.linesep
        self.test_script_fourth_content += "    contents = str(int(contents)+1)" + os.linesep
        self.test_script_fourth_content += "    os.unlink(fn_full)" + os.linesep
        self.test_script_fourth_content += "    with open(fn_full, \"w\") as f:" + os.linesep
        self.test_script_fourth_content += "        f.write(contents)" + os.linesep
        self.test_script_fourth_content += "    if contents == \"3\" or contents == \"6\":" + os.linesep
        self.test_script_fourth_content += "        sys.stdout.write(\"script-stdout\")" + os.linesep
        self.test_script_fourth_content += "        sys.stderr.write(\"script-stderr\")" + os.linesep
        self.test_script_fourth_content += "        sys.exit(1)" + os.linesep

        self.test_script_fourth_full = path_utils.concat_path(self.scripts_folder, "test_fourth.py")
        self.assertTrue(file_create_contents(self.test_script_fourth_full, self.test_script_fourth_content))
        os.chmod(self.test_script_fourth_full, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)

        # fifth script
        self.test_script_fifth_content = "#!/usr/bin/env python3" + os.linesep
        self.test_script_fifth_content += "import os" + os.linesep
        self.test_script_fifth_content += "import sys" + os.linesep
        self.test_script_fifth_content += "import path_utils" + os.linesep
        self.test_script_fifth_content += "import toolbus" + os.linesep
        self.test_script_fifth_content += "import mvtools_exception" + os.linesep
        self.test_script_fifth_content += "if __name__ == '__main__':" + os.linesep
        self.test_script_fifth_content += "    fn_full = path_utils.concat_path(\"%s\", \"counter.txt\")%s" % (self.data_folder, os.linesep)
        self.test_script_fifth_content += "    if not os.path.exists(fn_full):" + os.linesep
        self.test_script_fifth_content += "        with open(fn_full, \"w\") as f:" + os.linesep
        self.test_script_fifth_content += "            f.write(\"0\")" + os.linesep
        self.test_script_fifth_content += "        sys.exit(0)" + os.linesep
        self.test_script_fifth_content += "    contents = \"\"" + os.linesep
        self.test_script_fifth_content += "    with open(fn_full, \"r\") as f:" + os.linesep
        self.test_script_fifth_content += "        contents = f.read()" + os.linesep
        self.test_script_fifth_content += "    contents = str(int(contents)+1)" + os.linesep
        self.test_script_fifth_content += "    os.unlink(fn_full)" + os.linesep
        self.test_script_fifth_content += "    with open(fn_full, \"w\") as f:" + os.linesep
        self.test_script_fifth_content += "        f.write(contents)" + os.linesep
        self.test_script_fifth_content += "    if contents == \"1\" or contents == \"2\":" + os.linesep
        self.test_script_fifth_content += "        sys.stdout.write(\"script-stdout\")" + os.linesep
        self.test_script_fifth_content += "        sys.exit(1)" + os.linesep
        self.test_script_fifth_content += "    if contents == \"3\":" + os.linesep
        self.test_script_fifth_content += "        v, r = toolbus.set_signal(\"test-stop-sig\", \"test-stop-sig-val\")" + os.linesep
        self.test_script_fifth_content += "        if not v:" + os.linesep
        self.test_script_fifth_content += "            raise mvtools_exception.mvtools_exception(r)" + os.linesep

        self.test_script_fifth_full = path_utils.concat_path(self.scripts_folder, "test_fifth.py")
        self.assertTrue(file_create_contents(self.test_script_fifth_full, self.test_script_fifth_content))
        os.chmod(self.test_script_fifth_full, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)

        # sixth script
        self.test_script_sixth_content = "#!/usr/bin/env python3" + os.linesep
        self.test_script_sixth_content += "import os" + os.linesep
        self.test_script_sixth_content += "import sys" + os.linesep
        self.test_script_sixth_content += "import path_utils" + os.linesep
        self.test_script_sixth_content += "import toolbus" + os.linesep
        self.test_script_sixth_content += "import mvtools_exception" + os.linesep
        self.test_script_sixth_content += "if __name__ == '__main__':" + os.linesep
        self.test_script_sixth_content += "    fn_full = path_utils.concat_path(\"%s\", \"counter.txt\")%s" % (self.data_folder, os.linesep)
        self.test_script_sixth_content += "    if not os.path.exists(fn_full):" + os.linesep
        self.test_script_sixth_content += "        with open(fn_full, \"w\") as f:" + os.linesep
        self.test_script_sixth_content += "            f.write(\"0\")" + os.linesep
        self.test_script_sixth_content += "        sys.exit(0)" + os.linesep
        self.test_script_sixth_content += "    contents = \"\"" + os.linesep
        self.test_script_sixth_content += "    with open(fn_full, \"r\") as f:" + os.linesep
        self.test_script_sixth_content += "        contents = f.read()" + os.linesep
        self.test_script_sixth_content += "    contents = str(int(contents)+1)" + os.linesep
        self.test_script_sixth_content += "    os.unlink(fn_full)" + os.linesep
        self.test_script_sixth_content += "    with open(fn_full, \"w\") as f:" + os.linesep
        self.test_script_sixth_content += "        f.write(contents)" + os.linesep
        self.test_script_sixth_content += "    if contents == \"1\" or contents == \"2\":" + os.linesep
        self.test_script_sixth_content += "        sys.stdout.write(\"script-stdout\")" + os.linesep
        self.test_script_sixth_content += "        sys.stderr.write(\"script-stderr\")" + os.linesep
        self.test_script_sixth_content += "        sys.exit(1)" + os.linesep
        self.test_script_sixth_content += "    if contents == \"3\":" + os.linesep
        self.test_script_sixth_content += "        v, r = toolbus.set_signal(\"test-stop-sig\", \"test-stop-sig-val\")" + os.linesep
        self.test_script_sixth_content += "        if not v:" + os.linesep
        self.test_script_sixth_content += "            raise mvtools_exception.mvtools_exception(r)" + os.linesep

        self.test_script_sixth_full = path_utils.concat_path(self.scripts_folder, "test_sixth.py")
        self.assertTrue(file_create_contents(self.test_script_sixth_full, self.test_script_sixth_content))
        os.chmod(self.test_script_sixth_full, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)

        # seventh script
        self.test_script_seventh_content = "#!/usr/bin/env python3" + os.linesep
        self.test_script_seventh_content += "import os" + os.linesep
        self.test_script_seventh_content += "import sys" + os.linesep
        self.test_script_seventh_content += "import path_utils" + os.linesep
        self.test_script_seventh_content += "if __name__ == '__main__':" + os.linesep
        self.test_script_seventh_content += "    fn_full = path_utils.concat_path(\"%s\", \"counter.txt\")%s" % (self.data_folder, os.linesep)
        self.test_script_seventh_content += "    if not os.path.exists(fn_full):" + os.linesep
        self.test_script_seventh_content += "        with open(fn_full, \"w\") as f:" + os.linesep
        self.test_script_seventh_content += "            f.write(\"0\")" + os.linesep
        self.test_script_seventh_content += "        sys.exit(0)" + os.linesep
        self.test_script_seventh_content += "    contents = \"\"" + os.linesep
        self.test_script_seventh_content += "    with open(fn_full, \"r\") as f:" + os.linesep
        self.test_script_seventh_content += "        contents = f.read()" + os.linesep
        self.test_script_seventh_content += "    contents = str(int(contents)+1)" + os.linesep
        self.test_script_seventh_content += "    os.unlink(fn_full)" + os.linesep
        self.test_script_seventh_content += "    with open(fn_full, \"w\") as f:" + os.linesep
        self.test_script_seventh_content += "        f.write(contents)" + os.linesep
        self.test_script_seventh_content += "    if contents == \"2\" or contents == \"4\" or contents == \"6\" or contents == \"7\":" + os.linesep
        self.test_script_seventh_content += "        sys.stdout.write(\"script-stdout\")" + os.linesep
        self.test_script_seventh_content += "        sys.exit(1)" + os.linesep

        self.test_script_seventh_full = path_utils.concat_path(self.scripts_folder, "test_seventh.py")
        self.assertTrue(file_create_contents(self.test_script_seventh_full, self.test_script_seventh_content))
        os.chmod(self.test_script_seventh_full, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testStopFail(self):

        v, r = batch_run._stop_fail("3", 0, 1)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = batch_run._stop_fail("3", 0, 3)
        self.assertTrue(v)
        self.assertTrue(r)

    def testStopCount(self):

        v, r = batch_run._stop_count("3", 1, 0)
        self.assertTrue(v)
        self.assertFalse(r)

        v, r = batch_run._stop_count("3", 3, 0)
        self.assertTrue(v)
        self.assertTrue(r)

    def testStopTBSig(self):

        with mock.patch("toolbus.get_signal", return_value=(True, None)) as dummy:
            v, r = batch_run._stop_tb_sig("test-stop-sig", 0, 0)
            self.assertTrue(v)
            self.assertFalse(r)
            dummy.assert_called_with("test-stop-sig", False)

        with mock.patch("toolbus.get_signal", return_value=(True, "test-stop-sig-val")) as dummy:
            v, r = batch_run._stop_tb_sig("test-stop-sig", 0, 0)
            self.assertTrue(v)
            self.assertTrue(r)
            dummy.assert_called_with("test-stop-sig", False)

    def testSaveIter(self):

        os.mkdir(self.output_folder)

        batch_run._save_iter([self.dummy_taget_full], self.output_folder, 7, "dummy-stdout", "dummy-stderr")

        out_fn_full = path_utils.concat_path(self.output_folder, "dummy_target_stdout_7.txt")
        err_fn_full = path_utils.concat_path(self.output_folder, "dummy_target_stderr_7.txt")

        self.assertTrue(os.path.exists(out_fn_full))
        self.assertTrue(os.path.exists(err_fn_full))

        self.assertTrue(file_has_contents(out_fn_full, "dummy-stdout"))
        self.assertTrue(file_has_contents(err_fn_full, "dummy-stderr"))

    def testSaveSummary(self):

        os.mkdir(self.output_folder)

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

        os.mkdir(self.output_folder)
        dummy_gr_ret = generic_run.run_cmd_result(False, 1, "dummy-stdout", "dummy-stderr")

        with mock.patch("generic_run.run_cmd", return_value=(True, dummy_gr_ret)) as dummy1:
            with mock.patch("maketimestamp.get_timestamp_now", return_value="dummy-end-time") as dummy2:
                v, r = batch_run._run_until([self.dummy_taget_full], self.output_folder, [[batch_run._stop_fail, "1"]], "save-all", "dummy-started-time")
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

        os.mkdir(self.output_folder)

        with mock.patch("maketimestamp.get_timestamp_now", return_value="dummy-end-time") as dummy:
            v, r = batch_run._run_until([self.test_script_first_full], self.output_folder, [[batch_run._stop_fail, "1"]], "save-all", "dummy-started-time")
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

        os.mkdir(self.output_folder)

        with mock.patch("maketimestamp.get_timestamp_now", return_value="dummy-end-time") as dummy:
            v, r = batch_run._run_until([self.test_script_first_full], self.output_folder, [[batch_run._stop_fail, "1"]], "save-fail", "dummy-started-time")
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

        os.mkdir(self.output_folder)

        with mock.patch("maketimestamp.get_timestamp_now", return_value="dummy-end-time") as dummy:
            v, r = batch_run._run_until([self.test_script_second_full], self.output_folder, [[batch_run._stop_fail, "1"]], "save-fail", "dummy-started-time")
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

    def testRunUntil5(self):

        os.mkdir(self.output_folder)

        with mock.patch("maketimestamp.get_timestamp_now", return_value="dummy-end-time") as dummy:
            v, r = batch_run._run_until([self.test_script_seventh_full], self.output_folder, [[batch_run._stop_fail, "3"]], "save-all", "dummy-started-time")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called()

        out1_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_stdout_1.txt")
        out2_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_stdout_2.txt")
        out3_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_stdout_3.txt")
        out4_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_stdout_4.txt")
        out5_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_stdout_5.txt")
        out6_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_stdout_6.txt")
        out7_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_stdout_7.txt")

        err1_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_stderr_1.txt")
        err2_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_stderr_2.txt")
        err3_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_stderr_3.txt")
        err4_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_stderr_4.txt")
        err5_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_stderr_5.txt")
        err6_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_stderr_6.txt")
        err7_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_stderr_7.txt")

        self.assertTrue(os.path.exists(out1_fn_full))
        self.assertTrue(os.path.exists(out2_fn_full))
        self.assertTrue(os.path.exists(out3_fn_full))
        self.assertTrue(os.path.exists(out4_fn_full))
        self.assertTrue(os.path.exists(out5_fn_full))
        self.assertTrue(os.path.exists(out6_fn_full))
        self.assertTrue(os.path.exists(out7_fn_full))

        self.assertTrue(os.path.exists(err1_fn_full))
        self.assertTrue(os.path.exists(err2_fn_full))
        self.assertTrue(os.path.exists(err3_fn_full))
        self.assertTrue(os.path.exists(err4_fn_full))
        self.assertTrue(os.path.exists(err5_fn_full))
        self.assertTrue(os.path.exists(err6_fn_full))
        self.assertTrue(os.path.exists(err7_fn_full))

        self.assertTrue(file_has_contents(out3_fn_full, "script-stdout"))
        self.assertTrue(file_has_contents(out5_fn_full, "script-stdout"))
        self.assertTrue(file_has_contents(out7_fn_full, "script-stdout"))

        self.assertTrue(file_has_contents(err3_fn_full, ""))
        self.assertTrue(file_has_contents(err5_fn_full, ""))
        self.assertTrue(file_has_contents(err7_fn_full, ""))

        sum_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_summary.txt")

        self.assertTrue(os.path.exists(sum_fn_full))

        contents = file_get_contents(sum_fn_full)
        contents = contents.split("\n")

        contents_expected = []
        contents_expected.append("Run of [test_seventh.py] - summary:")
        contents_expected.append("-----------------------------------")
        contents_expected.append("")
        contents_expected.append("Number of total executions: [7]")
        contents_expected.append("Number of failed executions: [3]")
        contents_expected.append("Started time: [dummy-started-time]")
        contents_expected.append("End time: [dummy-end-time]")
        contents_expected.append("")

        line_num = 0
        for line in contents:
            self.assertEqual(line, contents_expected[line_num])
            line_num += 1

    def testRunUntil6(self):

        os.mkdir(self.output_folder)

        with mock.patch("maketimestamp.get_timestamp_now", return_value="dummy-end-time") as dummy:
            v, r = batch_run._run_until([self.test_script_third_full], self.output_folder, [[batch_run._stop_count, "9"]], "save-all", "dummy-started-time")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called()

        out1_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stdout_1.txt")
        out2_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stdout_2.txt")
        out3_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stdout_3.txt")
        out4_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stdout_4.txt")
        out5_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stdout_5.txt")
        out6_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stdout_6.txt")
        out7_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stdout_7.txt")
        out8_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stdout_8.txt")
        out9_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stdout_9.txt")

        err1_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stderr_1.txt")
        err2_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stderr_2.txt")
        err3_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stderr_3.txt")
        err4_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stderr_4.txt")
        err5_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stderr_5.txt")
        err6_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stderr_6.txt")
        err7_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stderr_7.txt")
        err8_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stderr_8.txt")
        err9_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stderr_9.txt")

        self.assertTrue(os.path.exists(out1_fn_full))
        self.assertTrue(os.path.exists(out2_fn_full))
        self.assertTrue(os.path.exists(out3_fn_full))
        self.assertTrue(os.path.exists(out4_fn_full))
        self.assertTrue(os.path.exists(out5_fn_full))
        self.assertTrue(os.path.exists(out6_fn_full))
        self.assertTrue(os.path.exists(out7_fn_full))
        self.assertTrue(os.path.exists(out8_fn_full))
        self.assertTrue(os.path.exists(out9_fn_full))

        self.assertTrue(os.path.exists(err1_fn_full))
        self.assertTrue(os.path.exists(err2_fn_full))
        self.assertTrue(os.path.exists(err3_fn_full))
        self.assertTrue(os.path.exists(err4_fn_full))
        self.assertTrue(os.path.exists(err5_fn_full))
        self.assertTrue(os.path.exists(err6_fn_full))
        self.assertTrue(os.path.exists(err7_fn_full))
        self.assertTrue(os.path.exists(err8_fn_full))
        self.assertTrue(os.path.exists(err9_fn_full))

        self.assertTrue(file_has_contents(out4_fn_full, "script-stdout"))
        self.assertTrue(file_has_contents(out7_fn_full, "script-stdout"))

        self.assertTrue(file_has_contents(err4_fn_full, ""))
        self.assertTrue(file_has_contents(err7_fn_full, ""))

        sum_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_summary.txt")

        self.assertTrue(os.path.exists(sum_fn_full))

        contents = file_get_contents(sum_fn_full)
        contents = contents.split("\n")

        contents_expected = []
        contents_expected.append("Run of [test_third.py] - summary:")
        contents_expected.append("---------------------------------")
        contents_expected.append("")
        contents_expected.append("Number of total executions: [9]")
        contents_expected.append("Number of failed executions: [2]")
        contents_expected.append("Started time: [dummy-started-time]")
        contents_expected.append("End time: [dummy-end-time]")
        contents_expected.append("")

        line_num = 0
        for line in contents:
            self.assertEqual(line, contents_expected[line_num])
            line_num += 1

    def testRunUntil7(self):

        os.mkdir(self.output_folder)

        with mock.patch("maketimestamp.get_timestamp_now", return_value="dummy-end-time") as dummy:
            v, r = batch_run._run_until([self.test_script_third_full], self.output_folder, [[batch_run._stop_count, "9"]], "save-fail", "dummy-started-time")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called()

        out1_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stdout_1.txt")
        out2_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stdout_2.txt")
        out3_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stdout_3.txt")
        out4_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stdout_4.txt")
        out5_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stdout_5.txt")
        out6_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stdout_6.txt")
        out7_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stdout_7.txt")
        out8_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stdout_8.txt")
        out9_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stdout_9.txt")

        err1_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stderr_1.txt")
        err2_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stderr_2.txt")
        err3_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stderr_3.txt")
        err4_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stderr_4.txt")
        err5_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stderr_5.txt")
        err6_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stderr_6.txt")
        err7_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stderr_7.txt")
        err8_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stderr_8.txt")
        err9_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stderr_9.txt")

        self.assertFalse(os.path.exists(out1_fn_full))
        self.assertFalse(os.path.exists(out2_fn_full))
        self.assertFalse(os.path.exists(out3_fn_full))
        self.assertTrue(os.path.exists(out4_fn_full))
        self.assertFalse(os.path.exists(out5_fn_full))
        self.assertFalse(os.path.exists(out6_fn_full))
        self.assertTrue(os.path.exists(out7_fn_full))
        self.assertFalse(os.path.exists(out8_fn_full))
        self.assertFalse(os.path.exists(out9_fn_full))

        self.assertFalse(os.path.exists(err1_fn_full))
        self.assertFalse(os.path.exists(err2_fn_full))
        self.assertFalse(os.path.exists(err3_fn_full))
        self.assertTrue(os.path.exists(err4_fn_full))
        self.assertFalse(os.path.exists(err5_fn_full))
        self.assertFalse(os.path.exists(err6_fn_full))
        self.assertTrue(os.path.exists(err7_fn_full))
        self.assertFalse(os.path.exists(err8_fn_full))
        self.assertFalse(os.path.exists(err9_fn_full))

        self.assertTrue(file_has_contents(out4_fn_full, "script-stdout"))
        self.assertTrue(file_has_contents(out7_fn_full, "script-stdout"))

        self.assertTrue(file_has_contents(err4_fn_full, ""))
        self.assertTrue(file_has_contents(err7_fn_full, ""))

        sum_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_summary.txt")

        self.assertTrue(os.path.exists(sum_fn_full))

        contents = file_get_contents(sum_fn_full)
        contents = contents.split("\n")

        contents_expected = []
        contents_expected.append("Run of [test_third.py] - summary:")
        contents_expected.append("---------------------------------")
        contents_expected.append("")
        contents_expected.append("Number of total executions: [9]")
        contents_expected.append("Number of failed executions: [2]")
        contents_expected.append("Started time: [dummy-started-time]")
        contents_expected.append("End time: [dummy-end-time]")
        contents_expected.append("")

        line_num = 0
        for line in contents:
            self.assertEqual(line, contents_expected[line_num])
            line_num += 1

    def testRunUntil8(self):

        os.mkdir(self.output_folder)

        with mock.patch("maketimestamp.get_timestamp_now", return_value="dummy-end-time") as dummy:
            v, r = batch_run._run_until([self.test_script_fourth_full], self.output_folder, [[batch_run._stop_count, "9"]], "save-fail", "dummy-started-time")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called()

        out1_fn_full = path_utils.concat_path(self.output_folder, "test_fourth.py_stdout_1.txt")
        out2_fn_full = path_utils.concat_path(self.output_folder, "test_fourth.py_stdout_2.txt")
        out3_fn_full = path_utils.concat_path(self.output_folder, "test_fourth.py_stdout_3.txt")
        out4_fn_full = path_utils.concat_path(self.output_folder, "test_fourth.py_stdout_4.txt")
        out5_fn_full = path_utils.concat_path(self.output_folder, "test_fourth.py_stdout_5.txt")
        out6_fn_full = path_utils.concat_path(self.output_folder, "test_fourth.py_stdout_6.txt")
        out7_fn_full = path_utils.concat_path(self.output_folder, "test_fourth.py_stdout_7.txt")
        out8_fn_full = path_utils.concat_path(self.output_folder, "test_fourth.py_stdout_8.txt")
        out9_fn_full = path_utils.concat_path(self.output_folder, "test_fourth.py_stdout_9.txt")

        err1_fn_full = path_utils.concat_path(self.output_folder, "test_fourth.py_stderr_1.txt")
        err2_fn_full = path_utils.concat_path(self.output_folder, "test_fourth.py_stderr_2.txt")
        err3_fn_full = path_utils.concat_path(self.output_folder, "test_fourth.py_stderr_3.txt")
        err4_fn_full = path_utils.concat_path(self.output_folder, "test_fourth.py_stderr_4.txt")
        err5_fn_full = path_utils.concat_path(self.output_folder, "test_fourth.py_stderr_5.txt")
        err6_fn_full = path_utils.concat_path(self.output_folder, "test_fourth.py_stderr_6.txt")
        err7_fn_full = path_utils.concat_path(self.output_folder, "test_fourth.py_stderr_7.txt")
        err8_fn_full = path_utils.concat_path(self.output_folder, "test_fourth.py_stderr_8.txt")
        err9_fn_full = path_utils.concat_path(self.output_folder, "test_fourth.py_stderr_9.txt")

        self.assertFalse(os.path.exists(out1_fn_full))
        self.assertFalse(os.path.exists(out2_fn_full))
        self.assertFalse(os.path.exists(out3_fn_full))
        self.assertTrue(os.path.exists(out4_fn_full))
        self.assertFalse(os.path.exists(out5_fn_full))
        self.assertFalse(os.path.exists(out6_fn_full))
        self.assertTrue(os.path.exists(out7_fn_full))
        self.assertFalse(os.path.exists(out8_fn_full))
        self.assertFalse(os.path.exists(out9_fn_full))

        self.assertFalse(os.path.exists(err1_fn_full))
        self.assertFalse(os.path.exists(err2_fn_full))
        self.assertFalse(os.path.exists(err3_fn_full))
        self.assertTrue(os.path.exists(err4_fn_full))
        self.assertFalse(os.path.exists(err5_fn_full))
        self.assertFalse(os.path.exists(err6_fn_full))
        self.assertTrue(os.path.exists(err7_fn_full))
        self.assertFalse(os.path.exists(err8_fn_full))
        self.assertFalse(os.path.exists(err9_fn_full))

        self.assertTrue(file_has_contents(out4_fn_full, "script-stdout"))
        self.assertTrue(file_has_contents(out7_fn_full, "script-stdout"))

        self.assertTrue(file_has_contents(err4_fn_full, "script-stderr"))
        self.assertTrue(file_has_contents(err7_fn_full, "script-stderr"))

        sum_fn_full = path_utils.concat_path(self.output_folder, "test_fourth.py_summary.txt")

        self.assertTrue(os.path.exists(sum_fn_full))

        contents = file_get_contents(sum_fn_full)
        contents = contents.split("\n")

        contents_expected = []
        contents_expected.append("Run of [test_fourth.py] - summary:")
        contents_expected.append("----------------------------------")
        contents_expected.append("")
        contents_expected.append("Number of total executions: [9]")
        contents_expected.append("Number of failed executions: [2]")
        contents_expected.append("Started time: [dummy-started-time]")
        contents_expected.append("End time: [dummy-end-time]")
        contents_expected.append("")

        line_num = 0
        for line in contents:
            self.assertEqual(line, contents_expected[line_num])
            line_num += 1

    def testRunUntil9(self):

        os.mkdir(self.output_folder)

        with mock.patch("maketimestamp.get_timestamp_now", return_value="dummy-end-time") as dummy:
            v, r = batch_run._run_until([self.test_script_fifth_full], self.output_folder, [[batch_run._stop_tb_sig, "test-stop-sig"]], "save-all", "dummy-started-time")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called()

        out1_fn_full = path_utils.concat_path(self.output_folder, "test_fifth.py_stdout_1.txt")
        out2_fn_full = path_utils.concat_path(self.output_folder, "test_fifth.py_stdout_2.txt")
        out3_fn_full = path_utils.concat_path(self.output_folder, "test_fifth.py_stdout_3.txt")
        out4_fn_full = path_utils.concat_path(self.output_folder, "test_fifth.py_stdout_4.txt")

        err1_fn_full = path_utils.concat_path(self.output_folder, "test_fifth.py_stderr_1.txt")
        err2_fn_full = path_utils.concat_path(self.output_folder, "test_fifth.py_stderr_2.txt")
        err3_fn_full = path_utils.concat_path(self.output_folder, "test_fifth.py_stderr_3.txt")
        err4_fn_full = path_utils.concat_path(self.output_folder, "test_fifth.py_stderr_4.txt")

        self.assertTrue(os.path.exists(out1_fn_full))
        self.assertTrue(os.path.exists(out2_fn_full))
        self.assertTrue(os.path.exists(out3_fn_full))
        self.assertTrue(os.path.exists(out4_fn_full))

        self.assertTrue(os.path.exists(err1_fn_full))
        self.assertTrue(os.path.exists(err2_fn_full))
        self.assertTrue(os.path.exists(err3_fn_full))
        self.assertTrue(os.path.exists(err4_fn_full))

        self.assertTrue(file_has_contents(out2_fn_full, "script-stdout"))
        self.assertTrue(file_has_contents(err2_fn_full, ""))

        self.assertTrue(file_has_contents(out3_fn_full, "script-stdout"))
        self.assertTrue(file_has_contents(err3_fn_full, ""))

        sum_fn_full = path_utils.concat_path(self.output_folder, "test_fifth.py_summary.txt")

        self.assertTrue(os.path.exists(sum_fn_full))

        contents = file_get_contents(sum_fn_full)
        contents = contents.split("\n")

        contents_expected = []
        contents_expected.append("Run of [test_fifth.py] - summary:")
        contents_expected.append("---------------------------------")
        contents_expected.append("")
        contents_expected.append("Number of total executions: [4]")
        contents_expected.append("Number of failed executions: [2]")
        contents_expected.append("Started time: [dummy-started-time]")
        contents_expected.append("End time: [dummy-end-time]")
        contents_expected.append("")

        line_num = 0
        for line in contents:
            self.assertEqual(line, contents_expected[line_num])
            line_num += 1

    def testRunUntil10(self):

        os.mkdir(self.output_folder)

        with mock.patch("maketimestamp.get_timestamp_now", return_value="dummy-end-time") as dummy:
            v, r = batch_run._run_until([self.test_script_fifth_full], self.output_folder, [[batch_run._stop_tb_sig, "test-stop-sig"]], "save-fail", "dummy-started-time")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called()

        out1_fn_full = path_utils.concat_path(self.output_folder, "test_fifth.py_stdout_1.txt")
        out2_fn_full = path_utils.concat_path(self.output_folder, "test_fifth.py_stdout_2.txt")
        out3_fn_full = path_utils.concat_path(self.output_folder, "test_fifth.py_stdout_3.txt")
        out4_fn_full = path_utils.concat_path(self.output_folder, "test_fifth.py_stdout_4.txt")

        err1_fn_full = path_utils.concat_path(self.output_folder, "test_fifth.py_stderr_1.txt")
        err2_fn_full = path_utils.concat_path(self.output_folder, "test_fifth.py_stderr_2.txt")
        err3_fn_full = path_utils.concat_path(self.output_folder, "test_fifth.py_stderr_3.txt")
        err4_fn_full = path_utils.concat_path(self.output_folder, "test_fifth.py_stderr_4.txt")

        self.assertFalse(os.path.exists(out1_fn_full))
        self.assertTrue(os.path.exists(out2_fn_full))
        self.assertTrue(os.path.exists(out3_fn_full))
        self.assertFalse(os.path.exists(out4_fn_full))

        self.assertFalse(os.path.exists(err1_fn_full))
        self.assertTrue(os.path.exists(err2_fn_full))
        self.assertTrue(os.path.exists(err3_fn_full))
        self.assertFalse(os.path.exists(err4_fn_full))

        self.assertTrue(file_has_contents(out2_fn_full, "script-stdout"))
        self.assertTrue(file_has_contents(err2_fn_full, ""))

        self.assertTrue(file_has_contents(out3_fn_full, "script-stdout"))
        self.assertTrue(file_has_contents(err3_fn_full, ""))

        sum_fn_full = path_utils.concat_path(self.output_folder, "test_fifth.py_summary.txt")

        self.assertTrue(os.path.exists(sum_fn_full))

        contents = file_get_contents(sum_fn_full)
        contents = contents.split("\n")

        contents_expected = []
        contents_expected.append("Run of [test_fifth.py] - summary:")
        contents_expected.append("---------------------------------")
        contents_expected.append("")
        contents_expected.append("Number of total executions: [4]")
        contents_expected.append("Number of failed executions: [2]")
        contents_expected.append("Started time: [dummy-started-time]")
        contents_expected.append("End time: [dummy-end-time]")
        contents_expected.append("")

        line_num = 0
        for line in contents:
            self.assertEqual(line, contents_expected[line_num])
            line_num += 1

    def testRunUntil11(self):

        os.mkdir(self.output_folder)

        with mock.patch("maketimestamp.get_timestamp_now", return_value="dummy-end-time") as dummy:
            v, r = batch_run._run_until([self.test_script_sixth_full], self.output_folder, [[batch_run._stop_tb_sig, "test-stop-sig"]], "save-fail", "dummy-started-time")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called()

        out1_fn_full = path_utils.concat_path(self.output_folder, "test_sixth.py_stdout_1.txt")
        out2_fn_full = path_utils.concat_path(self.output_folder, "test_sixth.py_stdout_2.txt")
        out3_fn_full = path_utils.concat_path(self.output_folder, "test_sixth.py_stdout_3.txt")
        out4_fn_full = path_utils.concat_path(self.output_folder, "test_sixth.py_stdout_4.txt")

        err1_fn_full = path_utils.concat_path(self.output_folder, "test_sixth.py_stderr_1.txt")
        err2_fn_full = path_utils.concat_path(self.output_folder, "test_sixth.py_stderr_2.txt")
        err3_fn_full = path_utils.concat_path(self.output_folder, "test_sixth.py_stderr_3.txt")
        err4_fn_full = path_utils.concat_path(self.output_folder, "test_sixth.py_stderr_4.txt")

        self.assertFalse(os.path.exists(out1_fn_full))
        self.assertTrue(os.path.exists(out2_fn_full))
        self.assertTrue(os.path.exists(out3_fn_full))
        self.assertFalse(os.path.exists(out4_fn_full))

        self.assertFalse(os.path.exists(err1_fn_full))
        self.assertTrue(os.path.exists(err2_fn_full))
        self.assertTrue(os.path.exists(err3_fn_full))
        self.assertFalse(os.path.exists(err4_fn_full))

        self.assertTrue(file_has_contents(out2_fn_full, "script-stdout"))
        self.assertTrue(file_has_contents(err2_fn_full, "script-stderr"))

        self.assertTrue(file_has_contents(out3_fn_full, "script-stdout"))
        self.assertTrue(file_has_contents(err3_fn_full, "script-stderr"))

        sum_fn_full = path_utils.concat_path(self.output_folder, "test_sixth.py_summary.txt")

        self.assertTrue(os.path.exists(sum_fn_full))

        contents = file_get_contents(sum_fn_full)
        contents = contents.split("\n")

        contents_expected = []
        contents_expected.append("Run of [test_sixth.py] - summary:")
        contents_expected.append("---------------------------------")
        contents_expected.append("")
        contents_expected.append("Number of total executions: [4]")
        contents_expected.append("Number of failed executions: [2]")
        contents_expected.append("Started time: [dummy-started-time]")
        contents_expected.append("End time: [dummy-end-time]")
        contents_expected.append("")

        line_num = 0
        for line in contents:
            self.assertEqual(line, contents_expected[line_num])
            line_num += 1

    def testRunUntil12(self):

        os.mkdir(self.output_folder)

        with mock.patch("maketimestamp.get_timestamp_now", return_value="dummy-end-time") as dummy:
            v, r = batch_run._run_until([self.test_script_seventh_full], self.output_folder, [[batch_run._stop_fail, "3"], [batch_run._stop_count, "2"]], "save-all", "dummy-started-time")
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called()

        out1_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_stdout_1.txt")
        out2_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_stdout_2.txt")
        out3_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_stdout_3.txt")
        out4_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_stdout_4.txt")
        out5_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_stdout_5.txt")
        out6_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_stdout_6.txt")
        out7_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_stdout_7.txt")

        err1_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_stderr_1.txt")
        err2_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_stderr_2.txt")
        err3_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_stderr_3.txt")
        err4_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_stderr_4.txt")
        err5_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_stderr_5.txt")
        err6_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_stderr_6.txt")
        err7_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_stderr_7.txt")

        self.assertTrue(os.path.exists(out1_fn_full))
        self.assertTrue(os.path.exists(out2_fn_full))
        self.assertFalse(os.path.exists(out3_fn_full))
        self.assertFalse(os.path.exists(out4_fn_full))
        self.assertFalse(os.path.exists(out5_fn_full))
        self.assertFalse(os.path.exists(out6_fn_full))
        self.assertFalse(os.path.exists(out7_fn_full))

        self.assertTrue(os.path.exists(err1_fn_full))
        self.assertTrue(os.path.exists(err2_fn_full))
        self.assertFalse(os.path.exists(err3_fn_full))
        self.assertFalse(os.path.exists(err4_fn_full))
        self.assertFalse(os.path.exists(err5_fn_full))
        self.assertFalse(os.path.exists(err6_fn_full))
        self.assertFalse(os.path.exists(err7_fn_full))

        sum_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_summary.txt")

        self.assertTrue(os.path.exists(sum_fn_full))

        contents = file_get_contents(sum_fn_full)
        contents = contents.split("\n")

        contents_expected = []
        contents_expected.append("Run of [test_seventh.py] - summary:")
        contents_expected.append("-----------------------------------")
        contents_expected.append("")
        contents_expected.append("Number of total executions: [2]")
        contents_expected.append("Number of failed executions: [0]")
        contents_expected.append("Started time: [dummy-started-time]")
        contents_expected.append("End time: [dummy-end-time]")
        contents_expected.append("")

        line_num = 0
        for line in contents:
            self.assertEqual(line, contents_expected[line_num])
            line_num += 1

    def testBatchRun1(self):

        dummy_gr_ret = generic_run.run_cmd_result(False, 1, "dummy-stdout", "dummy-stderr")

        with mock.patch("generic_run.run_cmd", return_value=(True, dummy_gr_ret)) as dummy1:
            with mock.patch("maketimestamp.get_timestamp_now", return_value="dummy-time") as dummy2:
                v, r = batch_run.batch_run(self.test_script_first_full, self.output_folder, [["until-fail", "1"]], "save-all", [])
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy1.assert_called_with([self.test_script_first_full])
                dummy2.assert_called()

        out_fn_full = path_utils.concat_path(self.output_folder, "test_first.py_stdout_1.txt")
        err_fn_full = path_utils.concat_path(self.output_folder, "test_first.py_stderr_1.txt")

        self.assertTrue(os.path.exists(out_fn_full))
        self.assertTrue(os.path.exists(err_fn_full))

        self.assertTrue(file_has_contents(out_fn_full, "dummy-stdout"))
        self.assertTrue(file_has_contents(err_fn_full, "dummy-stderr"))

        sum_fn_full = path_utils.concat_path(self.output_folder, "test_first.py_summary.txt")

        self.assertTrue(os.path.exists(sum_fn_full))

        contents = file_get_contents(sum_fn_full)
        contents = contents.split("\n")

        contents_expected = []
        contents_expected.append("Run of [test_first.py] - summary:")
        contents_expected.append("---------------------------------")
        contents_expected.append("")
        contents_expected.append("Number of total executions: [1]")
        contents_expected.append("Number of failed executions: [1]")
        contents_expected.append("Started time: [dummy-time]")
        contents_expected.append("End time: [dummy-time]")
        contents_expected.append("")

        line_num = 0
        for line in contents:
            self.assertEqual(line, contents_expected[line_num])
            line_num += 1

    def testBatchRun2(self):

        dummy_gr_ret = generic_run.run_cmd_result(False, 1, "dummy-stdout", "dummy-stderr")

        with mock.patch("generic_run.run_cmd", return_value=(True, dummy_gr_ret)) as dummy1:
            with mock.patch("maketimestamp.get_timestamp_now", return_value="dummy-time") as dummy2:
                v, r = batch_run.batch_run(self.test_script_first_full, self.output_folder, [["until-fail", "1"]], "save-all", ["test-param1", "test-param2"])
                self.assertTrue(v)
                self.assertEqual(r, None)
                dummy1.assert_called_with([self.test_script_first_full, "test-param1", "test-param2"])
                dummy2.assert_called()

        out_fn_full = path_utils.concat_path(self.output_folder, "test_first.py_stdout_1.txt")
        err_fn_full = path_utils.concat_path(self.output_folder, "test_first.py_stderr_1.txt")

        self.assertTrue(os.path.exists(out_fn_full))
        self.assertTrue(os.path.exists(err_fn_full))

        self.assertTrue(file_has_contents(out_fn_full, "dummy-stdout"))
        self.assertTrue(file_has_contents(err_fn_full, "dummy-stderr"))

        sum_fn_full = path_utils.concat_path(self.output_folder, "test_first.py_summary.txt")

        self.assertTrue(os.path.exists(sum_fn_full))

        contents = file_get_contents(sum_fn_full)
        contents = contents.split("\n")

        contents_expected = []
        contents_expected.append("Run of [test_first.py] - summary:")
        contents_expected.append("---------------------------------")
        contents_expected.append("")
        contents_expected.append("Number of total executions: [1]")
        contents_expected.append("Number of failed executions: [1]")
        contents_expected.append("Started time: [dummy-time]")
        contents_expected.append("End time: [dummy-time]")
        contents_expected.append("")

        line_num = 0
        for line in contents:
            self.assertEqual(line, contents_expected[line_num])
            line_num += 1

    def testBatchRun3(self):

        os.unlink(self.test_script_first_full)

        with mock.patch("maketimestamp.get_timestamp_now", return_value="dummy-time") as dummy:
            v, r = batch_run.batch_run(self.test_script_first_full, self.output_folder, [["until-fail", "1"]], "save-all", [])
            self.assertFalse(v)
            self.assertEqual(r, "Target [%s] does not exist." % self.test_script_first_full)
            dummy.assert_not_called()

    def testBatchRun4(self):

        os.mkdir(self.output_folder)

        with mock.patch("maketimestamp.get_timestamp_now", return_value="dummy-time") as dummy:
            v, r = batch_run.batch_run(self.test_script_first_full, self.output_folder, [["until-fail", "1"]], "save-all", [])
            self.assertFalse(v)
            self.assertEqual(r, "Output path [%s] already exists." % self.output_folder)
            dummy.assert_not_called()

    def testBatchRun5(self):

        with mock.patch("maketimestamp.get_timestamp_now", return_value="dummy-time") as dummy1:
            with mock.patch("path_utils.guaranteefolder", return_value=False) as dummy2:
                v, r = batch_run.batch_run(self.test_script_first_full, self.output_folder, [["until-fail", "1"]], "save-all", [])
                self.assertFalse(v)
                self.assertEqual(r, "Unable to create folder [%s]." % self.output_folder)
                dummy1.assert_not_called()
                dummy2.assert_called_with(self.output_folder)

    def testBatchRun6(self):

        with mock.patch("maketimestamp.get_timestamp_now", return_value="dummy-time") as dummy:
            v, r = batch_run.batch_run(self.test_script_first_full, self.output_folder, [], "save-all", [])
            self.assertFalse(v)
            self.assertEqual(r, "No operation modes specified.")
            dummy.assert_not_called()

    def testBatchRun7(self):

        with mock.patch("maketimestamp.get_timestamp_now", return_value="dummy-time") as dummy:
            v, r = batch_run.batch_run(self.test_script_first_full, self.output_folder, [["invalid-mode", "1"]], "save-all", [])
            self.assertFalse(v)
            self.assertEqual(r, "Operation mode [invalid-mode] is invalid.")
            dummy.assert_not_called()

    def testBatchRun8(self):

        with mock.patch("maketimestamp.get_timestamp_now", return_value="dummy-time") as dummy:
            v, r = batch_run.batch_run(self.test_script_first_full, self.output_folder, [["until-fail", None]], "save-all", [])
            self.assertFalse(v)
            self.assertEqual(r, "Operation mode [until-fail] - missing argument.")
            dummy.assert_not_called()

    def testBatchRun9(self):

        with mock.patch("maketimestamp.get_timestamp_now", return_value="dummy-time") as dummy:
            v, r = batch_run.batch_run(self.test_script_first_full, self.output_folder, [["until-fail", "1"]], "invalid-save-mode", [])
            self.assertFalse(v)
            self.assertEqual(r, "Invalid save mode: [invalid-save-mode].")
            dummy.assert_not_called()

    def testBatchRun10(self):

        with mock.patch("maketimestamp.get_timestamp_now", return_value="dummy-time") as dummy:
            v, r = batch_run.batch_run(self.test_script_first_full, self.output_folder, [["until-fail", "1"]], "save-all", [])
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
        contents_expected.append("Started time: [dummy-time]")
        contents_expected.append("End time: [dummy-time]")
        contents_expected.append("")

        line_num = 0
        for line in contents:
            self.assertEqual(line, contents_expected[line_num])
            line_num += 1

    def testBatchRun11(self):

        with mock.patch("maketimestamp.get_timestamp_now", return_value="dummy-time") as dummy:
            v, r = batch_run.batch_run(self.test_script_first_full, self.output_folder, [["until-fail", "1"]], "save-fail", [])
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
        contents_expected.append("Started time: [dummy-time]")
        contents_expected.append("End time: [dummy-time]")
        contents_expected.append("")

        line_num = 0
        for line in contents:
            self.assertEqual(line, contents_expected[line_num])
            line_num += 1

    def testBatchRun12(self):

        with mock.patch("maketimestamp.get_timestamp_now", return_value="dummy-time") as dummy:
            v, r = batch_run.batch_run(self.test_script_second_full, self.output_folder, [["until-fail", "1"]], "save-fail", [])
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
        contents_expected.append("Started time: [dummy-time]")
        contents_expected.append("End time: [dummy-time]")
        contents_expected.append("")

        line_num = 0
        for line in contents:
            self.assertEqual(line, contents_expected[line_num])
            line_num += 1

    def testBatchRun13(self):

        with mock.patch("maketimestamp.get_timestamp_now", return_value="dummy-time") as dummy:
            v, r = batch_run.batch_run(self.test_script_seventh_full, self.output_folder, [["until-fail", "3"]], "save-all", [])
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called()

        out1_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_stdout_1.txt")
        out2_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_stdout_2.txt")
        out3_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_stdout_3.txt")
        out4_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_stdout_4.txt")
        out5_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_stdout_5.txt")
        out6_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_stdout_6.txt")
        out7_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_stdout_7.txt")

        err1_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_stderr_1.txt")
        err2_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_stderr_2.txt")
        err3_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_stderr_3.txt")
        err4_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_stderr_4.txt")
        err5_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_stderr_5.txt")
        err6_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_stderr_6.txt")
        err7_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_stderr_7.txt")

        self.assertTrue(os.path.exists(out1_fn_full))
        self.assertTrue(os.path.exists(out2_fn_full))
        self.assertTrue(os.path.exists(out3_fn_full))
        self.assertTrue(os.path.exists(out4_fn_full))
        self.assertTrue(os.path.exists(out5_fn_full))
        self.assertTrue(os.path.exists(out6_fn_full))
        self.assertTrue(os.path.exists(out7_fn_full))

        self.assertTrue(os.path.exists(err1_fn_full))
        self.assertTrue(os.path.exists(err2_fn_full))
        self.assertTrue(os.path.exists(err3_fn_full))
        self.assertTrue(os.path.exists(err4_fn_full))
        self.assertTrue(os.path.exists(err5_fn_full))
        self.assertTrue(os.path.exists(err6_fn_full))
        self.assertTrue(os.path.exists(err7_fn_full))

        self.assertTrue(file_has_contents(out3_fn_full, "script-stdout"))
        self.assertTrue(file_has_contents(out5_fn_full, "script-stdout"))
        self.assertTrue(file_has_contents(out7_fn_full, "script-stdout"))

        self.assertTrue(file_has_contents(err3_fn_full, ""))
        self.assertTrue(file_has_contents(err5_fn_full, ""))
        self.assertTrue(file_has_contents(err7_fn_full, ""))

        sum_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_summary.txt")

        self.assertTrue(os.path.exists(sum_fn_full))

        contents = file_get_contents(sum_fn_full)
        contents = contents.split("\n")

        contents_expected = []
        contents_expected.append("Run of [test_seventh.py] - summary:")
        contents_expected.append("-----------------------------------")
        contents_expected.append("")
        contents_expected.append("Number of total executions: [7]")
        contents_expected.append("Number of failed executions: [3]")
        contents_expected.append("Started time: [dummy-time]")
        contents_expected.append("End time: [dummy-time]")
        contents_expected.append("")

        line_num = 0
        for line in contents:
            self.assertEqual(line, contents_expected[line_num])
            line_num += 1

    def testBatchRun14(self):

        with mock.patch("maketimestamp.get_timestamp_now", return_value="dummy-time") as dummy:
            v, r = batch_run.batch_run(self.test_script_third_full, self.output_folder, [["until-cnt", "9"]], "save-all", [])
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called()

        out1_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stdout_1.txt")
        out2_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stdout_2.txt")
        out3_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stdout_3.txt")
        out4_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stdout_4.txt")
        out5_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stdout_5.txt")
        out6_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stdout_6.txt")
        out7_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stdout_7.txt")
        out8_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stdout_8.txt")
        out9_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stdout_9.txt")

        err1_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stderr_1.txt")
        err2_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stderr_2.txt")
        err3_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stderr_3.txt")
        err4_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stderr_4.txt")
        err5_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stderr_5.txt")
        err6_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stderr_6.txt")
        err7_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stderr_7.txt")
        err8_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stderr_8.txt")
        err9_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stderr_9.txt")

        self.assertTrue(os.path.exists(out1_fn_full))
        self.assertTrue(os.path.exists(out2_fn_full))
        self.assertTrue(os.path.exists(out3_fn_full))
        self.assertTrue(os.path.exists(out4_fn_full))
        self.assertTrue(os.path.exists(out5_fn_full))
        self.assertTrue(os.path.exists(out6_fn_full))
        self.assertTrue(os.path.exists(out7_fn_full))
        self.assertTrue(os.path.exists(out8_fn_full))
        self.assertTrue(os.path.exists(out9_fn_full))

        self.assertTrue(os.path.exists(err1_fn_full))
        self.assertTrue(os.path.exists(err2_fn_full))
        self.assertTrue(os.path.exists(err3_fn_full))
        self.assertTrue(os.path.exists(err4_fn_full))
        self.assertTrue(os.path.exists(err5_fn_full))
        self.assertTrue(os.path.exists(err6_fn_full))
        self.assertTrue(os.path.exists(err7_fn_full))
        self.assertTrue(os.path.exists(err8_fn_full))
        self.assertTrue(os.path.exists(err9_fn_full))

        self.assertTrue(file_has_contents(out4_fn_full, "script-stdout"))
        self.assertTrue(file_has_contents(out7_fn_full, "script-stdout"))

        self.assertTrue(file_has_contents(err4_fn_full, ""))
        self.assertTrue(file_has_contents(err7_fn_full, ""))

        sum_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_summary.txt")

        self.assertTrue(os.path.exists(sum_fn_full))

        contents = file_get_contents(sum_fn_full)
        contents = contents.split("\n")

        contents_expected = []
        contents_expected.append("Run of [test_third.py] - summary:")
        contents_expected.append("---------------------------------")
        contents_expected.append("")
        contents_expected.append("Number of total executions: [9]")
        contents_expected.append("Number of failed executions: [2]")
        contents_expected.append("Started time: [dummy-time]")
        contents_expected.append("End time: [dummy-time]")
        contents_expected.append("")

        line_num = 0
        for line in contents:
            self.assertEqual(line, contents_expected[line_num])
            line_num += 1

    def testBatchRun15(self):

        with mock.patch("maketimestamp.get_timestamp_now", return_value="dummy-time") as dummy:
            v, r = batch_run.batch_run(self.test_script_third_full, self.output_folder, [["until-cnt", "9"]], "save-fail", [])
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called()

        out1_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stdout_1.txt")
        out2_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stdout_2.txt")
        out3_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stdout_3.txt")
        out4_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stdout_4.txt")
        out5_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stdout_5.txt")
        out6_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stdout_6.txt")
        out7_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stdout_7.txt")
        out8_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stdout_8.txt")
        out9_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stdout_9.txt")

        err1_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stderr_1.txt")
        err2_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stderr_2.txt")
        err3_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stderr_3.txt")
        err4_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stderr_4.txt")
        err5_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stderr_5.txt")
        err6_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stderr_6.txt")
        err7_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stderr_7.txt")
        err8_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stderr_8.txt")
        err9_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_stderr_9.txt")

        self.assertFalse(os.path.exists(out1_fn_full))
        self.assertFalse(os.path.exists(out2_fn_full))
        self.assertFalse(os.path.exists(out3_fn_full))
        self.assertTrue(os.path.exists(out4_fn_full))
        self.assertFalse(os.path.exists(out5_fn_full))
        self.assertFalse(os.path.exists(out6_fn_full))
        self.assertTrue(os.path.exists(out7_fn_full))
        self.assertFalse(os.path.exists(out8_fn_full))
        self.assertFalse(os.path.exists(out9_fn_full))

        self.assertFalse(os.path.exists(err1_fn_full))
        self.assertFalse(os.path.exists(err2_fn_full))
        self.assertFalse(os.path.exists(err3_fn_full))
        self.assertTrue(os.path.exists(err4_fn_full))
        self.assertFalse(os.path.exists(err5_fn_full))
        self.assertFalse(os.path.exists(err6_fn_full))
        self.assertTrue(os.path.exists(err7_fn_full))
        self.assertFalse(os.path.exists(err8_fn_full))
        self.assertFalse(os.path.exists(err9_fn_full))

        self.assertTrue(file_has_contents(out4_fn_full, "script-stdout"))
        self.assertTrue(file_has_contents(out7_fn_full, "script-stdout"))

        self.assertTrue(file_has_contents(err4_fn_full, ""))
        self.assertTrue(file_has_contents(err7_fn_full, ""))

        sum_fn_full = path_utils.concat_path(self.output_folder, "test_third.py_summary.txt")

        self.assertTrue(os.path.exists(sum_fn_full))

        contents = file_get_contents(sum_fn_full)
        contents = contents.split("\n")

        contents_expected = []
        contents_expected.append("Run of [test_third.py] - summary:")
        contents_expected.append("---------------------------------")
        contents_expected.append("")
        contents_expected.append("Number of total executions: [9]")
        contents_expected.append("Number of failed executions: [2]")
        contents_expected.append("Started time: [dummy-time]")
        contents_expected.append("End time: [dummy-time]")
        contents_expected.append("")

        line_num = 0
        for line in contents:
            self.assertEqual(line, contents_expected[line_num])
            line_num += 1

    def testBatchRun16(self):

        with mock.patch("maketimestamp.get_timestamp_now", return_value="dummy-time") as dummy:
            v, r = batch_run.batch_run(self.test_script_fourth_full, self.output_folder, [["until-cnt", "9"]], "save-fail", [])
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called()

        out1_fn_full = path_utils.concat_path(self.output_folder, "test_fourth.py_stdout_1.txt")
        out2_fn_full = path_utils.concat_path(self.output_folder, "test_fourth.py_stdout_2.txt")
        out3_fn_full = path_utils.concat_path(self.output_folder, "test_fourth.py_stdout_3.txt")
        out4_fn_full = path_utils.concat_path(self.output_folder, "test_fourth.py_stdout_4.txt")
        out5_fn_full = path_utils.concat_path(self.output_folder, "test_fourth.py_stdout_5.txt")
        out6_fn_full = path_utils.concat_path(self.output_folder, "test_fourth.py_stdout_6.txt")
        out7_fn_full = path_utils.concat_path(self.output_folder, "test_fourth.py_stdout_7.txt")
        out8_fn_full = path_utils.concat_path(self.output_folder, "test_fourth.py_stdout_8.txt")
        out9_fn_full = path_utils.concat_path(self.output_folder, "test_fourth.py_stdout_9.txt")

        err1_fn_full = path_utils.concat_path(self.output_folder, "test_fourth.py_stderr_1.txt")
        err2_fn_full = path_utils.concat_path(self.output_folder, "test_fourth.py_stderr_2.txt")
        err3_fn_full = path_utils.concat_path(self.output_folder, "test_fourth.py_stderr_3.txt")
        err4_fn_full = path_utils.concat_path(self.output_folder, "test_fourth.py_stderr_4.txt")
        err5_fn_full = path_utils.concat_path(self.output_folder, "test_fourth.py_stderr_5.txt")
        err6_fn_full = path_utils.concat_path(self.output_folder, "test_fourth.py_stderr_6.txt")
        err7_fn_full = path_utils.concat_path(self.output_folder, "test_fourth.py_stderr_7.txt")
        err8_fn_full = path_utils.concat_path(self.output_folder, "test_fourth.py_stderr_8.txt")
        err9_fn_full = path_utils.concat_path(self.output_folder, "test_fourth.py_stderr_9.txt")

        self.assertFalse(os.path.exists(out1_fn_full))
        self.assertFalse(os.path.exists(out2_fn_full))
        self.assertFalse(os.path.exists(out3_fn_full))
        self.assertTrue(os.path.exists(out4_fn_full))
        self.assertFalse(os.path.exists(out5_fn_full))
        self.assertFalse(os.path.exists(out6_fn_full))
        self.assertTrue(os.path.exists(out7_fn_full))
        self.assertFalse(os.path.exists(out8_fn_full))
        self.assertFalse(os.path.exists(out9_fn_full))

        self.assertFalse(os.path.exists(err1_fn_full))
        self.assertFalse(os.path.exists(err2_fn_full))
        self.assertFalse(os.path.exists(err3_fn_full))
        self.assertTrue(os.path.exists(err4_fn_full))
        self.assertFalse(os.path.exists(err5_fn_full))
        self.assertFalse(os.path.exists(err6_fn_full))
        self.assertTrue(os.path.exists(err7_fn_full))
        self.assertFalse(os.path.exists(err8_fn_full))
        self.assertFalse(os.path.exists(err9_fn_full))

        self.assertTrue(file_has_contents(out4_fn_full, "script-stdout"))
        self.assertTrue(file_has_contents(out7_fn_full, "script-stdout"))

        self.assertTrue(file_has_contents(err4_fn_full, "script-stderr"))
        self.assertTrue(file_has_contents(err7_fn_full, "script-stderr"))

        sum_fn_full = path_utils.concat_path(self.output_folder, "test_fourth.py_summary.txt")

        self.assertTrue(os.path.exists(sum_fn_full))

        contents = file_get_contents(sum_fn_full)
        contents = contents.split("\n")

        contents_expected = []
        contents_expected.append("Run of [test_fourth.py] - summary:")
        contents_expected.append("----------------------------------")
        contents_expected.append("")
        contents_expected.append("Number of total executions: [9]")
        contents_expected.append("Number of failed executions: [2]")
        contents_expected.append("Started time: [dummy-time]")
        contents_expected.append("End time: [dummy-time]")
        contents_expected.append("")

        line_num = 0
        for line in contents:
            self.assertEqual(line, contents_expected[line_num])
            line_num += 1

    def testBatchRun17(self):

        with mock.patch("maketimestamp.get_timestamp_now", return_value="dummy-time") as dummy:
            v, r = batch_run.batch_run(self.test_script_fifth_full, self.output_folder, [["until-sig", "test-stop-sig"]], "save-all", [])
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called()

        out1_fn_full = path_utils.concat_path(self.output_folder, "test_fifth.py_stdout_1.txt")
        out2_fn_full = path_utils.concat_path(self.output_folder, "test_fifth.py_stdout_2.txt")
        out3_fn_full = path_utils.concat_path(self.output_folder, "test_fifth.py_stdout_3.txt")
        out4_fn_full = path_utils.concat_path(self.output_folder, "test_fifth.py_stdout_4.txt")

        err1_fn_full = path_utils.concat_path(self.output_folder, "test_fifth.py_stderr_1.txt")
        err2_fn_full = path_utils.concat_path(self.output_folder, "test_fifth.py_stderr_2.txt")
        err3_fn_full = path_utils.concat_path(self.output_folder, "test_fifth.py_stderr_3.txt")
        err4_fn_full = path_utils.concat_path(self.output_folder, "test_fifth.py_stderr_4.txt")

        self.assertTrue(os.path.exists(out1_fn_full))
        self.assertTrue(os.path.exists(out2_fn_full))
        self.assertTrue(os.path.exists(out3_fn_full))
        self.assertTrue(os.path.exists(out4_fn_full))

        self.assertTrue(os.path.exists(err1_fn_full))
        self.assertTrue(os.path.exists(err2_fn_full))
        self.assertTrue(os.path.exists(err3_fn_full))
        self.assertTrue(os.path.exists(err4_fn_full))

        self.assertTrue(file_has_contents(out2_fn_full, "script-stdout"))
        self.assertTrue(file_has_contents(out3_fn_full, "script-stdout"))

        self.assertTrue(file_has_contents(err2_fn_full, ""))
        self.assertTrue(file_has_contents(err3_fn_full, ""))

        sum_fn_full = path_utils.concat_path(self.output_folder, "test_fifth.py_summary.txt")

        self.assertTrue(os.path.exists(sum_fn_full))

        contents = file_get_contents(sum_fn_full)
        contents = contents.split("\n")

        contents_expected = []
        contents_expected.append("Run of [test_fifth.py] - summary:")
        contents_expected.append("---------------------------------")
        contents_expected.append("")
        contents_expected.append("Number of total executions: [4]")
        contents_expected.append("Number of failed executions: [2]")
        contents_expected.append("Started time: [dummy-time]")
        contents_expected.append("End time: [dummy-time]")
        contents_expected.append("")

        line_num = 0
        for line in contents:
            self.assertEqual(line, contents_expected[line_num])
            line_num += 1

    def testBatchRun18(self):

        with mock.patch("maketimestamp.get_timestamp_now", return_value="dummy-time") as dummy:
            v, r = batch_run.batch_run(self.test_script_fifth_full, self.output_folder, [["until-sig", "test-stop-sig"]], "save-fail", [])
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called()

        out1_fn_full = path_utils.concat_path(self.output_folder, "test_fifth.py_stdout_1.txt")
        out2_fn_full = path_utils.concat_path(self.output_folder, "test_fifth.py_stdout_2.txt")
        out3_fn_full = path_utils.concat_path(self.output_folder, "test_fifth.py_stdout_3.txt")
        out4_fn_full = path_utils.concat_path(self.output_folder, "test_fifth.py_stdout_4.txt")

        err1_fn_full = path_utils.concat_path(self.output_folder, "test_fifth.py_stderr_1.txt")
        err2_fn_full = path_utils.concat_path(self.output_folder, "test_fifth.py_stderr_2.txt")
        err3_fn_full = path_utils.concat_path(self.output_folder, "test_fifth.py_stderr_3.txt")
        err4_fn_full = path_utils.concat_path(self.output_folder, "test_fifth.py_stderr_4.txt")

        self.assertFalse(os.path.exists(out1_fn_full))
        self.assertTrue(os.path.exists(out2_fn_full))
        self.assertTrue(os.path.exists(out3_fn_full))
        self.assertFalse(os.path.exists(out4_fn_full))

        self.assertFalse(os.path.exists(err1_fn_full))
        self.assertTrue(os.path.exists(err2_fn_full))
        self.assertTrue(os.path.exists(err3_fn_full))
        self.assertFalse(os.path.exists(err4_fn_full))

        self.assertTrue(file_has_contents(out2_fn_full, "script-stdout"))
        self.assertTrue(file_has_contents(out3_fn_full, "script-stdout"))

        self.assertTrue(file_has_contents(err2_fn_full, ""))
        self.assertTrue(file_has_contents(err3_fn_full, ""))

        sum_fn_full = path_utils.concat_path(self.output_folder, "test_fifth.py_summary.txt")

        self.assertTrue(os.path.exists(sum_fn_full))

        contents = file_get_contents(sum_fn_full)
        contents = contents.split("\n")

        contents_expected = []
        contents_expected.append("Run of [test_fifth.py] - summary:")
        contents_expected.append("---------------------------------")
        contents_expected.append("")
        contents_expected.append("Number of total executions: [4]")
        contents_expected.append("Number of failed executions: [2]")
        contents_expected.append("Started time: [dummy-time]")
        contents_expected.append("End time: [dummy-time]")
        contents_expected.append("")

        line_num = 0
        for line in contents:
            self.assertEqual(line, contents_expected[line_num])
            line_num += 1

    def testBatchRun19(self):

        with mock.patch("maketimestamp.get_timestamp_now", return_value="dummy-time") as dummy:
            v, r = batch_run.batch_run(self.test_script_sixth_full, self.output_folder, [["until-sig", "test-stop-sig"]], "save-fail", [])
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called()

        out1_fn_full = path_utils.concat_path(self.output_folder, "test_sixth.py_stdout_1.txt")
        out2_fn_full = path_utils.concat_path(self.output_folder, "test_sixth.py_stdout_2.txt")
        out3_fn_full = path_utils.concat_path(self.output_folder, "test_sixth.py_stdout_3.txt")
        out4_fn_full = path_utils.concat_path(self.output_folder, "test_sixth.py_stdout_4.txt")

        err1_fn_full = path_utils.concat_path(self.output_folder, "test_sixth.py_stderr_1.txt")
        err2_fn_full = path_utils.concat_path(self.output_folder, "test_sixth.py_stderr_2.txt")
        err3_fn_full = path_utils.concat_path(self.output_folder, "test_sixth.py_stderr_3.txt")
        err4_fn_full = path_utils.concat_path(self.output_folder, "test_sixth.py_stderr_4.txt")

        self.assertFalse(os.path.exists(out1_fn_full))
        self.assertTrue(os.path.exists(out2_fn_full))
        self.assertTrue(os.path.exists(out3_fn_full))
        self.assertFalse(os.path.exists(out4_fn_full))

        self.assertFalse(os.path.exists(err1_fn_full))
        self.assertTrue(os.path.exists(err2_fn_full))
        self.assertTrue(os.path.exists(err3_fn_full))
        self.assertFalse(os.path.exists(err4_fn_full))

        self.assertTrue(file_has_contents(out2_fn_full, "script-stdout"))
        self.assertTrue(file_has_contents(out3_fn_full, "script-stdout"))

        self.assertTrue(file_has_contents(err2_fn_full, "script-stderr"))
        self.assertTrue(file_has_contents(err3_fn_full, "script-stderr"))

        sum_fn_full = path_utils.concat_path(self.output_folder, "test_sixth.py_summary.txt")

        self.assertTrue(os.path.exists(sum_fn_full))

        contents = file_get_contents(sum_fn_full)
        contents = contents.split("\n")

        contents_expected = []
        contents_expected.append("Run of [test_sixth.py] - summary:")
        contents_expected.append("---------------------------------")
        contents_expected.append("")
        contents_expected.append("Number of total executions: [4]")
        contents_expected.append("Number of failed executions: [2]")
        contents_expected.append("Started time: [dummy-time]")
        contents_expected.append("End time: [dummy-time]")
        contents_expected.append("")

        line_num = 0
        for line in contents:
            self.assertEqual(line, contents_expected[line_num])
            line_num += 1

    def testBatchRun20(self):

        with mock.patch("maketimestamp.get_timestamp_now", return_value="dummy-time") as dummy:
            v, r = batch_run.batch_run(self.test_script_seventh_full, self.output_folder, [["until-fail", "3"], ["until-cnt", "2"]], "save-all", [])
            self.assertTrue(v)
            self.assertEqual(r, None)
            dummy.assert_called()

        out1_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_stdout_1.txt")
        out2_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_stdout_2.txt")
        out3_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_stdout_3.txt")
        out4_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_stdout_4.txt")
        out5_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_stdout_5.txt")
        out6_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_stdout_6.txt")
        out7_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_stdout_7.txt")

        err1_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_stderr_1.txt")
        err2_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_stderr_2.txt")
        err3_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_stderr_3.txt")
        err4_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_stderr_4.txt")
        err5_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_stderr_5.txt")
        err6_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_stderr_6.txt")
        err7_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_stderr_7.txt")

        self.assertTrue(os.path.exists(out1_fn_full))
        self.assertTrue(os.path.exists(out2_fn_full))
        self.assertFalse(os.path.exists(out3_fn_full))
        self.assertFalse(os.path.exists(out4_fn_full))
        self.assertFalse(os.path.exists(out5_fn_full))
        self.assertFalse(os.path.exists(out6_fn_full))
        self.assertFalse(os.path.exists(out7_fn_full))

        self.assertTrue(os.path.exists(err1_fn_full))
        self.assertTrue(os.path.exists(err2_fn_full))
        self.assertFalse(os.path.exists(err3_fn_full))
        self.assertFalse(os.path.exists(err4_fn_full))
        self.assertFalse(os.path.exists(err5_fn_full))
        self.assertFalse(os.path.exists(err6_fn_full))
        self.assertFalse(os.path.exists(err7_fn_full))

        sum_fn_full = path_utils.concat_path(self.output_folder, "test_seventh.py_summary.txt")

        self.assertTrue(os.path.exists(sum_fn_full))

        contents = file_get_contents(sum_fn_full)
        contents = contents.split("\n")

        contents_expected = []
        contents_expected.append("Run of [test_seventh.py] - summary:")
        contents_expected.append("-----------------------------------")
        contents_expected.append("")
        contents_expected.append("Number of total executions: [2]")
        contents_expected.append("Number of failed executions: [0]")
        contents_expected.append("Started time: [dummy-time]")
        contents_expected.append("End time: [dummy-time]")
        contents_expected.append("")

        line_num = 0
        for line in contents:
            self.assertEqual(line, contents_expected[line_num])
            line_num += 1

if __name__ == '__main__':
    unittest.main()
