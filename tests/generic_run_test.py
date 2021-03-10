#!/usr/bin/env python3

import sys
import os
import stat
import shutil
import unittest

import path_utils
import mvtools_test_fixture
import create_and_write_file
import mvtools_envvars
import generic_run

class GenericRunTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("generic_run_test_base")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # where to store the test scripts
        self.scripts_folder = path_utils.concat_path(self.test_dir, "scripts_folder")
        os.mkdir(self.scripts_folder)

        # secondary test folder, for testing using different cwds
        self.secondary_folder = path_utils.concat_path(self.test_dir, "secondary_folder")
        os.mkdir(self.secondary_folder)

        # test file, not pre-created
        self.file_test_filename = "test_file.txt"
        self.file_test_content = "the test file contents"

        v, r = mvtools_envvars.mvtools_envvar_read_test_generic_run_reserved_1()
        if v:
            return False, "Mvtool's generic_run's test envvar is defined. This test requires is to be undefined."
        self.reserved_test_env_var_1 = r

        # first script
        self.test_script_ret_0_content = "#!/usr/bin/env python3" + os.linesep
        self.test_script_ret_0_content += "import sys" + os.linesep
        self.test_script_ret_0_content += "if __name__ == '__main__':" + os.linesep
        self.test_script_ret_0_content += "    sys.exit(0)"

        self.test_script_ret_0_filename = path_utils.concat_path(self.scripts_folder, "test_ret_0.py")
        if not create_and_write_file.create_file_contents(self.test_script_ret_0_filename, self.test_script_ret_0_content):
            self.fail("create_and_write_file command failed. Can't proceed.")
        os.chmod(self.test_script_ret_0_filename, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)

        # second script
        self.test_script_ret_1_content = "#!/usr/bin/env python3" + os.linesep
        self.test_script_ret_1_content += "import sys" + os.linesep
        self.test_script_ret_1_content += "if __name__ == '__main__':" + os.linesep
        self.test_script_ret_1_content += "    sys.exit(1)"

        self.test_script_ret_1_filename = path_utils.concat_path(self.scripts_folder, "test_ret_1.py")
        if not create_and_write_file.create_file_contents(self.test_script_ret_1_filename, self.test_script_ret_1_content):
            self.fail("create_and_write_file command failed. Can't proceed.")
        os.chmod(self.test_script_ret_1_filename, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)

        # third script
        self.test_script_fail_content = "#!/usr/bin/env python3" + os.linesep
        self.test_script_fail_content += "if __name__ == '__main__':" + os.linesep
        self.test_script_fail_content += "    print..." # malformed instruction

        self.test_script_fail_filename = path_utils.concat_path(self.scripts_folder, "test_fail.py")
        if not create_and_write_file.create_file_contents(self.test_script_fail_filename, self.test_script_fail_content):
            self.fail("create_and_write_file command failed. Can't proceed.")
        os.chmod(self.test_script_fail_filename, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)

        # fourth script
        self.test_script_print_content = "#!/usr/bin/env python3" + os.linesep
        self.test_script_print_content += "if __name__ == '__main__':" + os.linesep
        self.test_script_print_content += "    print(\"the test output\")"

        self.test_script_print_filename = path_utils.concat_path(self.scripts_folder, "test_print.py")
        if not create_and_write_file.create_file_contents(self.test_script_print_filename, self.test_script_print_content):
            self.fail("create_and_write_file command failed. Can't proceed.")
        os.chmod(self.test_script_print_filename, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)

        # fifth script
        self.test_script_print_err_content = "#!/usr/bin/env python3" + os.linesep
        self.test_script_print_err_content += "import sys" + os.linesep
        self.test_script_print_err_content += "if __name__ == '__main__':" + os.linesep
        self.test_script_print_err_content += "    sys.stderr.write(\"the test error\")"

        self.test_script_print_err_filename = path_utils.concat_path(self.scripts_folder, "test_print_err.py")
        if not create_and_write_file.create_file_contents(self.test_script_print_err_filename, self.test_script_print_err_content):
            self.fail("create_and_write_file command failed. Can't proceed.")
        os.chmod(self.test_script_print_err_filename, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)

        # sixth script
        self.test_script_print_err_ret_1_content = "#!/usr/bin/env python3" + os.linesep
        self.test_script_print_err_ret_1_content += "import sys" + os.linesep
        self.test_script_print_err_ret_1_content += "if __name__ == '__main__':" + os.linesep
        self.test_script_print_err_ret_1_content += "    sys.stderr.write(\"the test error\")" + os.linesep
        self.test_script_print_err_ret_1_content += "    sys.exit(1)"

        self.test_script_print_err_ret_1_filename = path_utils.concat_path(self.scripts_folder, "test_print_err_ret_1.py")
        if not create_and_write_file.create_file_contents(self.test_script_print_err_ret_1_filename, self.test_script_print_err_ret_1_content):
            self.fail("create_and_write_file command failed. Can't proceed.")
        os.chmod(self.test_script_print_err_ret_1_filename, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)

        # seventh script
        self.test_script_print_input_content = "#!/usr/bin/env python3" + os.linesep
        self.test_script_print_input_content += "if __name__ == '__main__':" + os.linesep
        self.test_script_print_input_content += "    p = input(\"asking for input\")" + os.linesep
        self.test_script_print_input_content += "    print(\"echoing back: {%s}\" % p)"

        self.test_script_print_input_filename = path_utils.concat_path(self.scripts_folder, "test_input_print.py")
        if not create_and_write_file.create_file_contents(self.test_script_print_input_filename, self.test_script_print_input_content):
            self.fail("create_and_write_file command failed. Can't proceed.")
        os.chmod(self.test_script_print_input_filename, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)

        # eight script
        self.test_script_print_cmdlineargs_content = "#!/usr/bin/env python3" + os.linesep
        self.test_script_print_cmdlineargs_content += "import sys" + os.linesep
        self.test_script_print_cmdlineargs_content += "if __name__ == '__main__':" + os.linesep
        self.test_script_print_cmdlineargs_content += "    v = sys.argv[1]" + os.linesep
        self.test_script_print_cmdlineargs_content += "    print(v)"

        self.test_script_print_cmdlineargs_filename = path_utils.concat_path(self.scripts_folder, "test_print_cmdlineargs.py")
        if not create_and_write_file.create_file_contents(self.test_script_print_cmdlineargs_filename, self.test_script_print_cmdlineargs_content):
            self.fail("create_and_write_file command failed. Can't proceed.")
        os.chmod(self.test_script_print_cmdlineargs_filename, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)

        # ninth script
        self.test_script_print_utf8_content = "#!/usr/bin/env python3" + os.linesep
        self.test_script_print_utf8_content += "import sys" + os.linesep
        self.test_script_print_utf8_content += "if __name__ == '__main__':" + os.linesep
        self.test_script_print_utf8_content += "    print(\"おはようございます\")" + os.linesep
        self.test_script_print_utf8_content += "    sys.stderr.write(\"こんばんは\")"

        self.test_script_print_utf8_filename = path_utils.concat_path(self.scripts_folder, "test_print_utf8.py")
        if not create_and_write_file.create_file_contents(self.test_script_print_utf8_filename, self.test_script_print_utf8_content):
            self.fail("create_and_write_file command failed. Can't proceed.")
        os.chmod(self.test_script_print_utf8_filename, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)

        # tenth script
        self.test_print_file_cwd_content = "#!/usr/bin/env python3" + os.linesep
        self.test_print_file_cwd_content += "if __name__ == '__main__':" + os.linesep
        self.test_print_file_cwd_content += ("    fn = \"./%s\"" + os.linesep) % self.file_test_filename
        self.test_print_file_cwd_content += "    with open(fn) as f:"  + os.linesep
        self.test_print_file_cwd_content += "        print(f.read())"  + os.linesep

        self.test_print_file_cwd_filename = path_utils.concat_path(self.scripts_folder, "test_print_file_cwd.py")
        if not create_and_write_file.create_file_contents(self.test_print_file_cwd_filename, self.test_print_file_cwd_content):
            self.fail("create_and_write_file command failed. Can't proceed.")
        os.chmod(self.test_print_file_cwd_filename, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)

        # eleventh script
        self.test_custom_env_content = "#!/usr/bin/env python3" + os.linesep
        self.test_custom_env_content += "import os" + os.linesep
        self.test_custom_env_content += "if __name__ == '__main__':" + os.linesep
        self.test_custom_env_content += ("    print(os.environ[\"%s\"])" + os.linesep) % self.reserved_test_env_var_1

        self.test_custom_env_filename = path_utils.concat_path(self.scripts_folder, "test_print_custom_env.py")
        if not create_and_write_file.create_file_contents(self.test_custom_env_filename, self.test_custom_env_content):
            self.fail("create_and_write_file command failed. Can't proceed.")
        os.chmod(self.test_custom_env_filename, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)

        # twelvth script
        self.test_malformed_output_content = "#!/usr/bin/env python3" + os.linesep
        self.test_malformed_output_content += "import sys" + os.linesep
        self.test_malformed_output_content += "if __name__ == '__main__':" + os.linesep
        self.test_malformed_output_content += "    sys.stdout.buffer.write(b\"\\xff\")"

        self.test_malformed_output_filename = path_utils.concat_path(self.scripts_folder, "test_malformed_print.py")
        if not create_and_write_file.create_file_contents(self.test_malformed_output_filename, self.test_malformed_output_content):
            self.fail("create_and_write_file command failed. Can't proceed.")
        os.chmod(self.test_malformed_output_filename, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)

        # thirteenth script
        self.test_sleepy_content = "#!/usr/bin/env python3" + os.linesep
        self.test_sleepy_content += "import time" + os.linesep
        self.test_sleepy_content += "if __name__ == '__main__':" + os.linesep
        self.test_sleepy_content += "    time.sleep(2)" + os.linesep

        self.test_sleepy_filename = path_utils.concat_path(self.scripts_folder, "test_sleepy.py")
        if not create_and_write_file.create_file_contents(self.test_sleepy_filename, self.test_sleepy_content):
            self.fail("create_and_write_file command failed. Can't proceed.")
        os.chmod(self.test_sleepy_filename, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testSanity(self):

        ret = generic_run.run_cmd(None)
        self.assertEqual(len(ret), 3)
        self.assertFalse(ret[0])

        ret = generic_run.run_cmd("")
        self.assertEqual(len(ret), 3)
        self.assertFalse(ret[0])

        ret = generic_run.run_cmd([])
        self.assertEqual(len(ret), 3)
        self.assertFalse(ret[0])

    def testBasic(self):

        ret = generic_run.run_cmd(["echo", "ohce"])
        self.assertEqual(len(ret), 3)
        self.assertTrue(ret[0])
        self.assertTrue(ret[1], "OK")

        cmd_ret = ret[2]
        self.assertTrue(cmd_ret.success)
        self.assertEqual(cmd_ret.returncode, 0)
        self.assertTrue("ohce" in cmd_ret.stdout)
        self.assertEqual(cmd_ret.stderr, "")

    def testBasicScriptRet0(self):

        ret = generic_run.run_cmd([self.test_script_ret_0_filename])
        self.assertEqual(len(ret), 3)
        self.assertTrue(ret[0])
        self.assertTrue(ret[1], "OK")

        cmd_ret = ret[2]
        self.assertTrue(cmd_ret.success)
        self.assertEqual(cmd_ret.returncode, 0)
        self.assertEqual(cmd_ret.stdout, "")
        self.assertEqual(cmd_ret.stderr, "")

    def testBasicScriptRet1(self):

        ret = generic_run.run_cmd([self.test_script_ret_1_filename])
        self.assertEqual(len(ret), 3)
        self.assertTrue(ret[0])
        self.assertTrue(ret[1], "OK")

        cmd_ret = ret[2]
        self.assertFalse(cmd_ret.success)
        self.assertEqual(cmd_ret.returncode, 1)
        self.assertEqual(cmd_ret.stdout, "")
        self.assertEqual(cmd_ret.stderr, "")

    def testBasicScriptFail(self):

        ret = generic_run.run_cmd([self.test_script_fail_filename])
        self.assertEqual(len(ret), 3)
        self.assertTrue(ret[0])
        self.assertTrue(ret[1], "OK")

        cmd_ret = ret[2]
        self.assertFalse(cmd_ret.success)
        self.assertEqual(cmd_ret.returncode, 1)
        self.assertEqual(cmd_ret.stdout, "")
        self.assertTrue( "SyntaxError" in cmd_ret.stderr )

    def testPrintStdout(self):

        ret = generic_run.run_cmd([self.test_script_print_filename])
        self.assertEqual(len(ret), 3)
        self.assertTrue(ret[0])
        self.assertTrue(ret[1], "OK")

        cmd_ret = ret[2]
        self.assertTrue(cmd_ret.success)
        self.assertEqual(cmd_ret.returncode, 0)
        self.assertEqual(cmd_ret.stdout, "the test output" + os.linesep)
        self.assertEqual(cmd_ret.stderr, "")

    def testPrintStderr(self):

        ret = generic_run.run_cmd([self.test_script_print_err_filename])
        self.assertEqual(len(ret), 3)
        self.assertTrue(ret[0])
        self.assertTrue(ret[1], "OK")

        cmd_ret = ret[2]
        self.assertTrue(cmd_ret.success)
        self.assertEqual(cmd_ret.returncode, 0)
        self.assertEqual(cmd_ret.stdout, "")
        self.assertEqual(cmd_ret.stderr, "the test error")

    def testPrintInput(self):

        test_input = "input to be passed"

        ret = generic_run.run_cmd([self.test_script_print_input_filename], test_input)
        self.assertEqual(len(ret), 3)
        self.assertTrue(ret[0])
        self.assertTrue(ret[1], "OK")

        cmd_ret = ret[2]
        self.assertTrue(cmd_ret.success)
        self.assertEqual(cmd_ret.returncode, 0)
        self.assertEqual(cmd_ret.stdout, ("asking for inputechoing back: {%s}" + os.linesep) % test_input)
        self.assertEqual(cmd_ret.stderr, "")

    def testPrintCmdlineargs(self):

        test_input = "the cmdline argument"

        ret = generic_run.run_cmd([self.test_script_print_cmdlineargs_filename, test_input])
        self.assertEqual(len(ret), 3)
        self.assertTrue(ret[0])
        self.assertTrue(ret[1], "OK")

        cmd_ret = ret[2]
        self.assertTrue(cmd_ret.success)
        self.assertEqual(cmd_ret.returncode, 0)
        self.assertEqual(cmd_ret.stdout, test_input + os.linesep)
        self.assertEqual(cmd_ret.stderr, "")

    def testPrintUtf8(self):

        ret = generic_run.run_cmd([self.test_script_print_utf8_filename])
        self.assertEqual(len(ret), 3)
        self.assertTrue(ret[0])
        self.assertTrue(ret[1], "OK")

        cmd_ret = ret[2]
        self.assertTrue(cmd_ret.success)
        self.assertEqual(cmd_ret.returncode, 0)
        self.assertEqual(cmd_ret.stdout, "おはようございます" + os.linesep)
        self.assertEqual(cmd_ret.stderr, "こんばんは")

    def testPrintFileCwd(self):

        if not create_and_write_file.create_file_contents(path_utils.concat_path(self.secondary_folder, self.file_test_filename), self.file_test_content):
            self.fail("create_and_write_file command failed. Can't proceed.")

        ret = generic_run.run_cmd([self.test_print_file_cwd_filename], use_cwd=self.secondary_folder)
        self.assertEqual(len(ret), 3)
        self.assertTrue(ret[0])
        self.assertTrue(ret[1], "OK")

        cmd_ret = ret[2]
        self.assertTrue(cmd_ret.success)
        self.assertEqual(cmd_ret.returncode, 0)
        self.assertEqual(cmd_ret.stdout, self.file_test_content + os.linesep)
        self.assertEqual(cmd_ret.stderr, "")

    def testPrintFileCwdFail(self):

        if not create_and_write_file.create_file_contents(path_utils.concat_path(self.scripts_folder, self.file_test_filename), self.file_test_content):
            self.fail("create_and_write_file command failed. Can't proceed.")

        ret = generic_run.run_cmd([self.test_print_file_cwd_filename], use_cwd=self.secondary_folder)
        self.assertEqual(len(ret), 3)
        self.assertTrue(ret[0])
        self.assertTrue(ret[1], "OK")

        cmd_ret = ret[2]
        self.assertFalse(cmd_ret.success)
        self.assertEqual(cmd_ret.returncode, 1)
        self.assertEqual(cmd_ret.stdout, "")
        self.assertTrue( "FileNotFoundError" in cmd_ret.stderr )

    def testPrintCustomEnv(self):

        custom_env_content = "test environment value"
        custom_env = os.environ.copy()
        custom_env[self.reserved_test_env_var_1] = custom_env_content

        ret = generic_run.run_cmd([self.test_custom_env_filename], use_env=custom_env)
        self.assertEqual(len(ret), 3)
        self.assertTrue(ret[0])
        self.assertTrue(ret[1], "OK")

        cmd_ret = ret[2]
        self.assertTrue(cmd_ret.success)
        self.assertEqual(cmd_ret.returncode, 0)

        self.assertEqual(cmd_ret.stdout, custom_env_content + os.linesep)
        self.assertEqual(cmd_ret.stderr, "")

    def testRunCmdSimple(self):

        v, r = generic_run.run_cmd_simple(["echo", "test-for-echo"])
        self.assertTrue(v)
        self.assertEqual(r, "test-for-echo" + os.linesep)

    def testRunCmdSimpleFail1(self):

        v, r = generic_run.run_cmd_simple(["ocho"])
        self.assertFalse(v)
        self.assertTrue("No such file or directory" in r)

    def testRunCmdSimpleFail2(self):

        v, r = generic_run.run_cmd_simple([self.test_script_print_err_ret_1_filename])
        self.assertFalse(v)
        self.assertTrue( "the test error" in r )

    def testRunCmdSimpleFail3(self):

        v, r = generic_run.run_cmd_simple([])
        self.assertFalse(v)
        self.assertTrue( "Nothing to run" in r )

    def testRunCmdSimpleFail4(self):

        v, r = generic_run.run_cmd_simple(512)
        self.assertFalse(v)
        self.assertTrue( "is not a list" in r )

    def testPrintStdoutMalformedFail(self):

        ret = generic_run.run_cmd([self.test_malformed_output_filename], use_errors=None)
        self.assertEqual(len(ret), 3)
        self.assertFalse(ret[0])
        self.assertEqual(ret[1], "'utf-8' codec can't decode byte 0xff in position 0: invalid start byte")

    def testPrintStdoutMalformed(self):

        ret = generic_run.run_cmd([self.test_malformed_output_filename])
        self.assertEqual(len(ret), 3)
        self.assertTrue(ret[0])
        self.assertTrue(ret[1], "OK")

        cmd_ret = ret[2]
        self.assertTrue(cmd_ret.success)
        self.assertEqual(cmd_ret.returncode, 0)
        self.assertEqual(cmd_ret.stdout, "")
        self.assertEqual(cmd_ret.stderr, "")

    def testSleepyNoTimeout(self):

        ret = generic_run.run_cmd([self.test_sleepy_filename])
        self.assertEqual(len(ret), 3)
        self.assertTrue(ret[0])
        self.assertTrue(ret[1], "OK")

        cmd_ret = ret[2]
        self.assertTrue(cmd_ret.success)
        self.assertEqual(cmd_ret.returncode, 0)
        self.assertEqual(cmd_ret.stdout, "")
        self.assertEqual(cmd_ret.stderr, "")

    def testSleepyTimeoutFail(self):

        ret = generic_run.run_cmd([self.test_sleepy_filename], use_timeout=1)
        self.assertEqual(len(ret), 3)
        self.assertFalse(ret[0])
        self.assertTrue("timed out after 1 second" in ret[1])

    def testSleepyTimeoutPass(self):

        ret = generic_run.run_cmd([self.test_sleepy_filename], use_timeout=3)
        self.assertEqual(len(ret), 3)
        self.assertTrue(ret[0])
        self.assertTrue(ret[1], "OK")

        cmd_ret = ret[2]
        self.assertTrue(cmd_ret.success)
        self.assertEqual(cmd_ret.returncode, 0)
        self.assertEqual(cmd_ret.stdout, "")
        self.assertEqual(cmd_ret.stderr, "")

if __name__ == '__main__':
    unittest.main()
