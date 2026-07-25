#!/usr/bin/env python

import os
import shutil
import unittest

import create_and_write_file
import mvtools_test_fixture
import path_utils
import mvtools_envvars
import getcontents

import dsl_type20
import miniparse
import mvtools_exception

def var_fmt_helper(var_list):
    v, r = var_list
    if not v:
        raise mvtools_exception.mvtools_exception("Failed test")
    return dsl_type20.convert_var_obj_list_to_neutral_format(r)

def opt_fmt_helper(opt_list):
    v, r = opt_list
    if not v:
        raise mvtools_exception.mvtools_exception("Failed test")
    return dsl_type20.convert_opt_obj_list_to_neutral_format(r)

def find_context_callback_report_chain(node_ptr, node_data):

    if node_ptr is None:
        raise mvtools_exception.mvtools_exception("Failed test")

    if not isinstance(node_data, list):
        raise mvtools_exception.mvtools_exception("Failed test")

    sentinel = 0
    current = node_ptr
    while (current != None):
        sentinel += 1
        if sentinel > 100:
            break
        node_data.append(current.get_name())
        current = current.get_parent_ptr()

    return True, None

def find_context_callback_positive(node_ptr, node_data):

    if node_ptr is None:
        raise mvtools_exception.mvtools_exception("Failed test")

    if node_data != "dummy-data":
        raise mvtools_exception.mvtools_exception("Failed test")

    return True, None

def find_context_callback_negative(node_ptr, node_data):
    return False, "Test error"

class DSLType20Test(unittest.TestCase):

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

        v, r = mvtools_test_fixture.makeAndGetTestFolder("dsl_type20_test")
        if not v:
            return v, r
        self.test_base_dir = r[0]
        self.test_dir = r[1]

        v, r = mvtools_envvars.mvtools_envvar_read_test_dsltype20_reserved_1()
        if v:
            return False, "DSLType20's first test envvar is defined. This test requires it to be undefined."
        self.reserved_test_env_var_1 = "$MVTOOLS_TEST_DSLTYPE20_RESERVED_1"

        v, r = mvtools_envvars.mvtools_envvar_read_test_dsltype20_reserved_2()
        if v:
            return False, "DSLType20's second test envvar is defined. This test requires it to be undefined."
        self.reserved_test_env_var_2 = "$MVTOOLS_TEST_DSLTYPE20_RESERVED_2"

        self.reserved_path_with_user_1 = "/tmp/folder"

        self.contents_cfg_test_ok_1 = "var1 = \"val1\"\n"
        self.contents_cfg_test_ok_1 += "var2 {opt1} = \"val2\"\n"
        self.contents_cfg_test_ok_1 += "var3 {opt2: \"val3\"} = \"val4\"\n"
        self.contents_cfg_test_ok_1 += "var4 {opt3: \"val5\" / opt4: \"val6\"} = \"val7\"\n"
        self.contents_cfg_test_ok_1 += "var5 {opt5 / opt6: \"val8\" / opt7: \"val9\"} = \"val10\"\n"
        self.cfg_test_ok_1 = path_utils.concat_path(self.test_dir, "test_ok_1.t20")

        self.contents_cfg_test_ok_2 = "var1 = \"val1\"\n"
        self.contents_cfg_test_ok_2 += "var2 = \"a/path/valid1\"\n"
        self.contents_cfg_test_ok_2 += "var3 {opt1 / opt2: \"a/path/valid2\"} = \"a/path/valid3\"\n"
        self.contents_cfg_test_ok_2 += "var4 = \"$SOME_ENV_VAR\"\n"
        self.contents_cfg_test_ok_2 += "var5 {r1: \"\" / r2} = \"opts\"\n"
        self.contents_cfg_test_ok_2 += "var5 {r1 / r2} = \"more-opts\"\n"
        self.cfg_test_ok_2 = path_utils.concat_path(self.test_dir, "test_ok_2.t20")

        self.contents_cfg_test_ok_3 = "var1 = \"val1\"\n"
        self.contents_cfg_test_ok_3 += "var2 = \"val2\"\n"
        self.cfg_test_ok_3 = path_utils.concat_path(self.test_dir, "test_ok_3.t20")

        self.contents_cfg_test_ok_4 = ("var1 = \"%s\"\n") % self.reserved_test_env_var_1 # mvtodo
        self.contents_cfg_test_ok_4 += ("var2 {opt1: \"%s\"} = \"val1\"\n") % self.reserved_test_env_var_2 # mvtodo
        self.contents_cfg_test_ok_4 += ("var3 = \"%s\"\n") % self.reserved_path_with_user_1
        self.cfg_test_ok_4 = path_utils.concat_path(self.test_dir, "test_ok_4.t20")

        self.contents_cfg_test_ok_5 = "var1 = \"val1\" # comment\n"
        self.cfg_test_ok_5 = path_utils.concat_path(self.test_dir, "test_ok_5.t20")

        self.contents_cfg_test_ok_6 = "var1\n"
        self.cfg_test_ok_6 = path_utils.concat_path(self.test_dir, "test_ok_6.t20")

        self.contents_cfg_test_ok_7 = "var1 {opt1}\n"
        self.cfg_test_ok_7 = path_utils.concat_path(self.test_dir, "test_ok_7.t20")

        self.contents_cfg_test_ok_8 = "var1 {opt1 / opt2}\n"
        self.cfg_test_ok_8 = path_utils.concat_path(self.test_dir, "test_ok_8.t20")

        self.contents_cfg_test_ok_9 = "var1 {opt1: \"val1\" / opt2}\n"
        self.cfg_test_ok_9 = path_utils.concat_path(self.test_dir, "test_ok_9.t20")

        self.contents_cfg_test_ok_10 = "var1 {opt1 / opt2: \"val1\"}\n"
        self.cfg_test_ok_10 = path_utils.concat_path(self.test_dir, "test_ok_10.t20")

        self.contents_cfg_test_ok_11 = "[\n"
        self.contents_cfg_test_ok_11 += "@ctx\n"
        self.contents_cfg_test_ok_11 += "var1\n"
        self.contents_cfg_test_ok_11 += "]\n"
        self.cfg_test_ok_11 = path_utils.concat_path(self.test_dir, "test_ok_11.t20")

        self.contents_cfg_test_ok_12 = "[\n"
        self.contents_cfg_test_ok_12 += "@ctx\n"
        self.contents_cfg_test_ok_12 += "var1 {opt1}\n"
        self.contents_cfg_test_ok_12 += "]\n"
        self.cfg_test_ok_12 = path_utils.concat_path(self.test_dir, "test_ok_12.t20")

        self.contents_cfg_test_ok_13 = "[\n"
        self.contents_cfg_test_ok_13 += "@ctx\n"
        self.contents_cfg_test_ok_13 += "var1 {opt1 / opt2}\n"
        self.contents_cfg_test_ok_13 += "]\n"
        self.cfg_test_ok_13 = path_utils.concat_path(self.test_dir, "test_ok_13.t20")

        self.contents_cfg_test_ok_14 = "[\n"
        self.contents_cfg_test_ok_14 += "@ctx\n"
        self.contents_cfg_test_ok_14 += "var1 {opt1: \"val1\" / opt2}\n"
        self.contents_cfg_test_ok_14 += "]\n"
        self.cfg_test_ok_14 = path_utils.concat_path(self.test_dir, "test_ok_14.t20")

        self.contents_cfg_test_ok_15 = "[\n"
        self.contents_cfg_test_ok_15 += "@ctx\n"
        self.contents_cfg_test_ok_15 += "var1 {opt1 / opt2: \"val1\"}\n"
        self.contents_cfg_test_ok_15 += "]\n"
        self.cfg_test_ok_15 = path_utils.concat_path(self.test_dir, "test_ok_15.t20")

        self.contents_cfg_test_ok_16 = "[\n"
        self.contents_cfg_test_ok_16 += "@ctx {opt1: \"val1\"}\n"
        self.contents_cfg_test_ok_16 += "var1 {opt1: \"val2\"}\n"
        self.contents_cfg_test_ok_16 += "]\n"
        self.cfg_test_ok_16 = path_utils.concat_path(self.test_dir, "test_ok_16.t20")

        self.contents_cfg_test_ok_17 = "[\n"
        self.contents_cfg_test_ok_17 += "@ctx\n"
        self.contents_cfg_test_ok_17 += "var1 {opt1: \"val2\"}\n"
        self.contents_cfg_test_ok_17 += "]\n"
        self.cfg_test_ok_17 = path_utils.concat_path(self.test_dir, "test_ok_17.t20")

        self.contents_cfg_test_ok_18 = "[\n"
        self.contents_cfg_test_ok_18 += "@ctx {opt1: \"val1\"}\n"
        self.contents_cfg_test_ok_18 += "var1 {opt1}\n"
        self.contents_cfg_test_ok_18 += "]\n"
        self.cfg_test_ok_18 = path_utils.concat_path(self.test_dir, "test_ok_18.t20")

        self.contents_cfg_test_ok_19 = "[\n"
        self.contents_cfg_test_ok_19 += "@ctx {opt1}\n"
        self.contents_cfg_test_ok_19 += "var1 {opt1}\n"
        self.contents_cfg_test_ok_19 += "]\n"
        self.cfg_test_ok_19 = path_utils.concat_path(self.test_dir, "test_ok_19.t20")

        self.contents_cfg_test_ok_20 = "[\n"
        self.contents_cfg_test_ok_20 += "@ctx1 {opt1 / opt2}\n"
        self.contents_cfg_test_ok_20 += "var1 {opt2 / opt3}\n"
        self.contents_cfg_test_ok_20 += "[\n"
        self.contents_cfg_test_ok_20 += "@ctx2 {opt4 / opt5}\n"
        self.contents_cfg_test_ok_20 += "var2 {opt6 / opt7}\n"
        self.contents_cfg_test_ok_20 += "[\n"
        self.contents_cfg_test_ok_20 += "@ctx3\n"
        self.contents_cfg_test_ok_20 += "var3\n"
        self.contents_cfg_test_ok_20 += "]\n"
        self.contents_cfg_test_ok_20 += "]\n"
        self.contents_cfg_test_ok_20 += "[\n"
        self.contents_cfg_test_ok_20 += "@ctx4\n"
        self.contents_cfg_test_ok_20 += "var4\n"
        self.contents_cfg_test_ok_20 += "]\n"
        self.contents_cfg_test_ok_20 += "]\n"
        self.contents_cfg_test_ok_20 += "[\n"
        self.contents_cfg_test_ok_20 += "@ctx5\n"
        self.contents_cfg_test_ok_20 += "var5\n"
        self.contents_cfg_test_ok_20 += "]\n"
        self.cfg_test_ok_20 = path_utils.concat_path(self.test_dir, "test_ok_20.t20")

        self.contents_cfg_test_ok_21 = "[\n"
        self.contents_cfg_test_ok_21 += "]\n"
        self.contents_cfg_test_ok_21 += "\n"
        self.contents_cfg_test_ok_21 += "[\n"
        self.contents_cfg_test_ok_21 += "]\n"
        self.contents_cfg_test_ok_21 += "\n"
        self.contents_cfg_test_ok_21 += "[\n"
        self.contents_cfg_test_ok_21 += "\n"
        self.contents_cfg_test_ok_21 += "    [\n"
        self.contents_cfg_test_ok_21 += "\n"
        self.contents_cfg_test_ok_21 += "        [\n"
        self.contents_cfg_test_ok_21 += "\n"
        self.contents_cfg_test_ok_21 += "\n"
        self.contents_cfg_test_ok_21 += "        ]\n"
        self.contents_cfg_test_ok_21 += "\n"
        self.contents_cfg_test_ok_21 += "    ]\n"
        self.contents_cfg_test_ok_21 += "\n"
        self.contents_cfg_test_ok_21 += "]\n"
        self.cfg_test_ok_21 = path_utils.concat_path(self.test_dir, "test_ok_21.t20")

        self.contents_cfg_test_ok_22 = "[\n"
        self.contents_cfg_test_ok_22 += "@ctx1 {opt1: (\"abc\", \"def\")}\n"
        self.contents_cfg_test_ok_22 += "var1 {opt2: (\"first\", \"second\")} = (\"123\", \"357\")\n"
        self.contents_cfg_test_ok_22 += "]\n"
        self.cfg_test_ok_22 = path_utils.concat_path(self.test_dir, "test_ok_22.t20")

        self.contents_cfg_test_ok_23 = "[\n"
        self.contents_cfg_test_ok_23 += "@ctx1 {opt1: (\"abc\", \"def\")}\n"
        self.contents_cfg_test_ok_23 += "var1 {opt1: (\"first\", \"second\")} = (\"123\", \"357\")\n"
        self.contents_cfg_test_ok_23 += "]\n"
        self.cfg_test_ok_23 = path_utils.concat_path(self.test_dir, "test_ok_23.t20")

        self.contents_cfg_test_fail_1 = "var1 = val1\n"
        self.cfg_test_fail_1 = path_utils.concat_path(self.test_dir, "test_fail_1.t20")

        self.contents_cfg_test_fail_2 = "{var1 = \"val1\"}\n"
        self.cfg_test_fail_2 = path_utils.concat_path(self.test_dir, "test_fail_2.t20")

        self.contents_cfg_test_fail_3 = "{fakeopt} var1 = \"val1\"\n"
        self.cfg_test_fail_3 = path_utils.concat_path(self.test_dir, "test_fail_3.t20")

        self.contents_cfg_test_fail_4 = "var1 {opt1: \"val1} = \"val2\"\n"
        self.cfg_test_fail_4 = path_utils.concat_path(self.test_dir, "test_fail_4.t20")

        create_and_write_file.create_file_contents(self.cfg_test_ok_1, self.contents_cfg_test_ok_1)
        create_and_write_file.create_file_contents(self.cfg_test_ok_2, self.contents_cfg_test_ok_2)
        create_and_write_file.create_file_contents(self.cfg_test_ok_3, self.contents_cfg_test_ok_3)
        create_and_write_file.create_file_contents(self.cfg_test_ok_4, self.contents_cfg_test_ok_4)
        create_and_write_file.create_file_contents(self.cfg_test_ok_5, self.contents_cfg_test_ok_5)
        create_and_write_file.create_file_contents(self.cfg_test_ok_6, self.contents_cfg_test_ok_6)
        create_and_write_file.create_file_contents(self.cfg_test_ok_7, self.contents_cfg_test_ok_7)
        create_and_write_file.create_file_contents(self.cfg_test_ok_8, self.contents_cfg_test_ok_8)
        create_and_write_file.create_file_contents(self.cfg_test_ok_9, self.contents_cfg_test_ok_9)
        create_and_write_file.create_file_contents(self.cfg_test_ok_10, self.contents_cfg_test_ok_10)
        create_and_write_file.create_file_contents(self.cfg_test_ok_11, self.contents_cfg_test_ok_11)
        create_and_write_file.create_file_contents(self.cfg_test_ok_12, self.contents_cfg_test_ok_12)
        create_and_write_file.create_file_contents(self.cfg_test_ok_13, self.contents_cfg_test_ok_13)
        create_and_write_file.create_file_contents(self.cfg_test_ok_14, self.contents_cfg_test_ok_14)
        create_and_write_file.create_file_contents(self.cfg_test_ok_15, self.contents_cfg_test_ok_15)
        create_and_write_file.create_file_contents(self.cfg_test_ok_16, self.contents_cfg_test_ok_16)
        create_and_write_file.create_file_contents(self.cfg_test_ok_17, self.contents_cfg_test_ok_17)
        create_and_write_file.create_file_contents(self.cfg_test_ok_18, self.contents_cfg_test_ok_18)
        create_and_write_file.create_file_contents(self.cfg_test_ok_19, self.contents_cfg_test_ok_19)
        create_and_write_file.create_file_contents(self.cfg_test_ok_20, self.contents_cfg_test_ok_20)
        create_and_write_file.create_file_contents(self.cfg_test_ok_21, self.contents_cfg_test_ok_21)
        create_and_write_file.create_file_contents(self.cfg_test_ok_22, self.contents_cfg_test_ok_22)
        create_and_write_file.create_file_contents(self.cfg_test_ok_23, self.contents_cfg_test_ok_23)
        create_and_write_file.create_file_contents(self.cfg_test_fail_1, self.contents_cfg_test_fail_1)
        create_and_write_file.create_file_contents(self.cfg_test_fail_2, self.contents_cfg_test_fail_2)
        create_and_write_file.create_file_contents(self.cfg_test_fail_3, self.contents_cfg_test_fail_3)
        create_and_write_file.create_file_contents(self.cfg_test_fail_4, self.contents_cfg_test_fail_4)

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)
        v, r = self.mvtools_envvars_inst.restore_copy_environ()
        if not v:
            self.fail(r)

    def parse_test_aux(self, filename, _dsl_t20_opts):

        try:
            contents = getcontents.getcontents(filename)
        except mvtools_exception.mvtools_exception as ex:
            self.fail(ex.message)

        dsl = dsl_type20.DSLType20(_dsl_t20_opts)
        v, r = dsl.parse(contents)
        return v

    def testSanitizeLineSingle(self):

        v, r = dsl_type20.sanitize_line("", False)
        self.assertEqual(v, "")
        self.assertEqual(r, False)

        v, r = dsl_type20.sanitize_line("abc", False)
        self.assertEqual(v, "abc")
        self.assertEqual(r, False)

        v, r = dsl_type20.sanitize_line("#abc", False)
        self.assertEqual(v, "")
        self.assertEqual(r, False)

        v, r = dsl_type20.sanitize_line("abc//def", False)
        self.assertEqual(v, "abc")
        self.assertEqual(r, False)

        v, r = dsl_type20.sanitize_line("//abc def", False)
        self.assertEqual(v, "")
        self.assertEqual(r, False)

        v, r = dsl_type20.sanitize_line("abc#def", False)
        self.assertEqual(v, "abc")
        self.assertEqual(r, False)

        v, r = dsl_type20.sanitize_line("   abc   ", False)
        self.assertEqual(v, "abc")
        self.assertEqual(r, False)

        v, r = dsl_type20.sanitize_line(" #   abc   ", False)
        self.assertEqual(v, "")
        self.assertEqual(r, False)

        v, r = dsl_type20.sanitize_line("   abc   #", False)
        self.assertEqual(v, "abc")
        self.assertEqual(r, False)

        v, r = dsl_type20.sanitize_line("   abc   // def   # xyz", False)
        self.assertEqual(v, "abc")
        self.assertEqual(r, False)

        v, r = dsl_type20.sanitize_line("   abc   # def   // xyz", False)
        self.assertEqual(v, "abc")
        self.assertEqual(r, False)

        v, r = dsl_type20.sanitize_line("   abc   \"#\" def   // xyz", False)
        self.assertEqual(v, "abc   \"#\" def")
        self.assertEqual(r, False)

        v, r = dsl_type20.sanitize_line("   abc   \"//\" def   // xyz", False)
        self.assertEqual(v, "abc   \"//\" def")
        self.assertEqual(r, False)

    def testSanitizeLineMulti(self):

        # begin with unfinished multiline

        v, r = dsl_type20.sanitize_line("", True)
        self.assertEqual(v, "")
        self.assertEqual(r, True)

        v, r = dsl_type20.sanitize_line("abc", True)
        self.assertEqual(v, "")
        self.assertEqual(r, True)

        v, r = dsl_type20.sanitize_line("*/", True)
        self.assertEqual(v, "")
        self.assertEqual(r, False)

        v, r = dsl_type20.sanitize_line("abc*/", True)
        self.assertEqual(v, "")
        self.assertEqual(r, False)

        v, r = dsl_type20.sanitize_line("*/a", True)
        self.assertEqual(v, "a")
        self.assertEqual(r, False)

        v, r = dsl_type20.sanitize_line("abc*/ def ", True)
        self.assertEqual(v, "def")
        self.assertEqual(r, False)

        v, r = dsl_type20.sanitize_line("/*abc*/ def ", True)
        self.assertEqual(v, "def")
        self.assertEqual(r, False)

        v, r = dsl_type20.sanitize_line("//abc*/ def ", True)
        self.assertEqual(v, "def")
        self.assertEqual(r, False)

        v, r = dsl_type20.sanitize_line("#abc*/ def ", True)
        self.assertEqual(v, "def")
        self.assertEqual(r, False)

        # try apply singleline

        v, r = dsl_type20.sanitize_line("# abc", False)
        self.assertEqual(v, "")
        self.assertEqual(r, False)

        v, r = dsl_type20.sanitize_line("// abc", False)
        self.assertEqual(v, "")
        self.assertEqual(r, False)

        v, r = dsl_type20.sanitize_line("abcdef #more", False)
        self.assertEqual(v, "abcdef")
        self.assertEqual(r, False)

        v, r = dsl_type20.sanitize_line("abcdef //more", False)
        self.assertEqual(v, "abcdef")
        self.assertEqual(r, False)

        v, r = dsl_type20.sanitize_line("abcde//f #more", False)
        self.assertEqual(v, "abcde")
        self.assertEqual(r, False)

        v, r = dsl_type20.sanitize_line("abcde#f //more", False)
        self.assertEqual(v, "abcde")
        self.assertEqual(r, False)

        v, r = dsl_type20.sanitize_line("# abc /*", False)
        self.assertEqual(v, "")
        self.assertEqual(r, False)

        v, r = dsl_type20.sanitize_line("// abc /*", False)
        self.assertEqual(v, "")
        self.assertEqual(r, False)

        v, r = dsl_type20.sanitize_line(" a#bc // def /*", False)
        self.assertEqual(v, "a")
        self.assertEqual(r, False)

        v, r = dsl_type20.sanitize_line(" a//bc # def /*", False)
        self.assertEqual(v, "a")
        self.assertEqual(r, False)

        v, r = dsl_type20.sanitize_line(" \"#// /*\"a#bc // def /*", False)
        self.assertEqual(v, "\"#// /*\"a")
        self.assertEqual(r, False)

        v, r = dsl_type20.sanitize_line(" \"#// /*\"a//bc # def /*", False)
        self.assertEqual(v, "\"#// /*\"a")
        self.assertEqual(r, False)

        v, r = dsl_type20.sanitize_line("\"#\"abc", False)
        self.assertEqual(v, "\"#\"abc")
        self.assertEqual(r, False)

        v, r = dsl_type20.sanitize_line("\"#\"#abc", False)
        self.assertEqual(v, "\"#\"")
        self.assertEqual(r, False)

        v, r = dsl_type20.sanitize_line("\"#\"#abc", False)
        self.assertEqual(v, "\"#\"")
        self.assertEqual(r, False)

        v, r = dsl_type20.sanitize_line("\"#\\\"#abc", False)
        self.assertEqual(v, "\"#\\\"#abc")
        self.assertEqual(r, False)

        v, r = dsl_type20.sanitize_line("\"//\"//abc", False)
        self.assertEqual(v, "\"//\"")
        self.assertEqual(r, False)

        v, r = dsl_type20.sanitize_line("\"//\\\"//abc", False)
        self.assertEqual(v, "\"//\\\"//abc")
        self.assertEqual(r, False)

        # try apply multiline

        v, r = dsl_type20.sanitize_line("*/ /*", False)
        self.assertEqual(v, None)
        self.assertEqual(r, False)

        v, r = dsl_type20.sanitize_line("/*", False)
        self.assertEqual(v, "")
        self.assertEqual(r, True)

        v, r = dsl_type20.sanitize_line("abc /*def*/ --- /*xyz*/", False)
        self.assertEqual(v, "abc  ---")
        self.assertEqual(r, False)

        v, r = dsl_type20.sanitize_line("abc /*def", False)
        self.assertEqual(v, "abc")
        self.assertEqual(r, True)

        v, r = dsl_type20.sanitize_line("abc */def", True)
        self.assertEqual(v, "def")
        self.assertEqual(r, False)

        v, r = dsl_type20.sanitize_line("abc */ def /*xyz*/ more ", True)
        self.assertEqual(v, "def  more")
        self.assertEqual(r, False)

        v, r = dsl_type20.sanitize_line("abc */ def /*xyz*/ more /*extra", True)
        self.assertEqual(v, "def  more")
        self.assertEqual(r, True)

        v, r = dsl_type20.sanitize_line("*/", False)
        self.assertEqual(v, None)
        self.assertEqual(r, False)

        v, r = dsl_type20.sanitize_line("abc \"/*\" def /*xyz*//*", False)
        self.assertEqual(v, "abc \"/*\" def")
        self.assertEqual(r, True)

        v, r = dsl_type20.sanitize_line("\"*/ abc /*def*/", True)
        self.assertEqual(v, "abc")
        self.assertEqual(r, False)

        v, r = dsl_type20.sanitize_line("\"*/ abc /*def*/ /*xyz", True)
        self.assertEqual(v, "abc")
        self.assertEqual(r, True)

        v, r = dsl_type20.sanitize_line("\"/*\"/*abc", False)
        self.assertEqual(v, "\"/*\"")
        self.assertEqual(r, True)

        v, r = dsl_type20.sanitize_line("\"/*\\\"//abc", False)
        self.assertEqual(v, "\"/*\\\"//abc")
        self.assertEqual(r, False)

    def testValidateName(self):
        self.assertFalse(dsl_type20.validate_name(None))
        self.assertFalse(dsl_type20.validate_name([]))
        self.assertFalse(dsl_type20.validate_name(()))
        self.assertFalse(dsl_type20.validate_name("name\x0a"))
        self.assertFalse(dsl_type20.validate_name("name\x00"))
        self.assertFalse(dsl_type20.validate_name("name\x20"))
        self.assertFalse(dsl_type20.validate_name("name\x09"))
        self.assertFalse(dsl_type20.validate_name("name\x5b"))
        self.assertFalse(dsl_type20.validate_name("name\x5d"))
        self.assertFalse(dsl_type20.validate_name("name\x7b"))
        self.assertFalse(dsl_type20.validate_name("name\x7d"))
        self.assertFalse(dsl_type20.validate_name("name\x28"))
        self.assertFalse(dsl_type20.validate_name("name\x29"))
        self.assertFalse(dsl_type20.validate_name("name\x3d"))
        self.assertFalse(dsl_type20.validate_name("name\x2f"))
        self.assertFalse(dsl_type20.validate_name("name\x5c"))
        self.assertFalse(dsl_type20.validate_name("name\x24"))
        self.assertFalse(dsl_type20.validate_name("name\x7e"))
        self.assertFalse(dsl_type20.validate_name("name\x40"))
        self.assertFalse(dsl_type20.validate_name("name\x22"))
        self.assertFalse(dsl_type20.validate_name("name\x3a"))
        self.assertFalse(dsl_type20.validate_name("name\x3b"))
        self.assertFalse(dsl_type20.validate_name("name\x2a"))
        self.assertFalse(dsl_type20.validate_name("name\x2c"))
        self.assertFalse(dsl_type20.validate_name("name\x23"))
        self.assertFalse(dsl_type20.validate_name("name\x21"))
        self.assertFalse(dsl_type20.validate_name("name\x25"))
        self.assertFalse(dsl_type20.validate_name("name\x5e"))
        self.assertFalse(dsl_type20.validate_name("name\x26"))
        self.assertFalse(dsl_type20.validate_name("name\x2b"))
        self.assertFalse(dsl_type20.validate_name("name\x3c"))
        self.assertFalse(dsl_type20.validate_name("name\x3e"))
        self.assertFalse(dsl_type20.validate_name("name\x2e"))
        self.assertFalse(dsl_type20.validate_name("name\x27"))
        self.assertFalse(dsl_type20.validate_name("name\x3f"))
        self.assertFalse(dsl_type20.validate_name("name\x7c"))
        self.assertFalse(dsl_type20.validate_name("name\x60"))
        self.assertFalse(dsl_type20.validate_name(""))
        self.assertTrue(dsl_type20.validate_name("a"))
        self.assertTrue(dsl_type20.validate_name("거물사냥꾼"))

    def testValidateValue(self):
        self.assertTrue(dsl_type20.validate_value(None))
        self.assertFalse(dsl_type20.validate_value(()))
        self.assertTrue(dsl_type20.validate_value([]))
        self.assertTrue(dsl_type20.validate_value( dsl_type20.DSLType20_Value(dsl_type20.DSLType20_Config()) ))
        self.assertTrue(dsl_type20.validate_value( [dsl_type20.DSLType20_Value(dsl_type20.DSLType20_Config()), dsl_type20.DSLType20_Value(dsl_type20.DSLType20_Config())] ))
        self.assertFalse(dsl_type20.validate_value( [dsl_type20.DSLType20_Value(dsl_type20.DSLType20_Config()), "test-val2"] ))

    def testValidateOptions(self):
        self.assertTrue(dsl_type20.validate_options( None )[0])
        self.assertTrue(dsl_type20.validate_options( dsl_type20.DSLType20_Option(dsl_type20.DSLType20_Config(), "a") )[0])
        self.assertTrue(dsl_type20.validate_options( [  ] )[0])
        self.assertTrue(dsl_type20.validate_options( [dsl_type20.DSLType20_Option(dsl_type20.DSLType20_Config(), "a"), dsl_type20.DSLType20_Option(dsl_type20.DSLType20_Config(), "b")] )[0])

        self.assertFalse(dsl_type20.validate_options( [dsl_type20.DSLType20_Option(dsl_type20.DSLType20_Config(), "a"), 1] )[0])
        self.assertFalse(dsl_type20.validate_options( [1, dsl_type20.DSLType20_Option(dsl_type20.DSLType20_Config(), "b")] )[0])
        self.assertFalse(dsl_type20.validate_options( [dsl_type20.DSLType20_Option(dsl_type20.DSLType20_Config(), "a"), dsl_type20.DSLType20_Option(dsl_type20.DSLType20_Config(), "a")] )[0])

    def testMakeObjOptList1(self):
        v, r = dsl_type20.make_obj_opt_list(dsl_type20.DSLType20_Config(), [ ("a", "b"), ("a", "b") ])
        self.assertFalse(v)

    def testMakeObjOptList2(self):
        v, r = dsl_type20.make_obj_opt_list(dsl_type20.DSLType20_Config(), [ ("a", "b"), ("c", None) ])
        self.assertTrue(v)
        self.assertTrue(isinstance(r, list))
        self.assertTrue(isinstance(r[0], dsl_type20.DSLType20_Option))
        self.assertEqual(r[0].get_type(), dsl_type20.DSLTYPE20_ENTRY_TYPE_OPT)
        self.assertEqual(r[0].get_name(), "a")
        self.assertEqual(r[0].get_value(), "b")
        self.assertTrue(isinstance(r[1], dsl_type20.DSLType20_Option))
        self.assertEqual(r[1].get_type(), dsl_type20.DSLTYPE20_ENTRY_TYPE_OPT)
        self.assertEqual(r[1].get_name(), "c")
        self.assertEqual(r[1].get_value(), None)

    def testMakeObjOptList3(self):
        v, r = dsl_type20.make_obj_opt_list(dsl_type20.DSLType20_Config(), [ ("a", "b"), ("c", []) ])
        self.assertTrue(v)
        self.assertTrue(isinstance(r, list))
        self.assertTrue(isinstance(r[0], dsl_type20.DSLType20_Option))
        self.assertEqual(r[0].get_type(), dsl_type20.DSLTYPE20_ENTRY_TYPE_OPT)
        self.assertEqual(r[0].get_name(), "a")
        self.assertEqual(r[0].get_value(), "b")
        self.assertTrue(isinstance(r[1], dsl_type20.DSLType20_Option))
        self.assertEqual(r[1].get_type(), dsl_type20.DSLTYPE20_ENTRY_TYPE_OPT)
        self.assertEqual(r[1].get_name(), "c")
        self.assertEqual(r[1].get_value(), [])

    def testMakeObjOptList4(self):
        v, r = dsl_type20.make_obj_opt_list(dsl_type20.DSLType20_Config(), [ ("a", "b"), ("c", ["abc", "def"]) ])
        self.assertTrue(v)
        self.assertTrue(isinstance(r, list))
        self.assertTrue(isinstance(r[0], dsl_type20.DSLType20_Option))
        self.assertEqual(r[0].get_type(), dsl_type20.DSLTYPE20_ENTRY_TYPE_OPT)
        self.assertEqual(r[0].get_name(), "a")
        self.assertEqual(r[0].get_value(), "b")
        self.assertTrue(isinstance(r[1], dsl_type20.DSLType20_Option))
        self.assertEqual(r[1].get_type(), dsl_type20.DSLTYPE20_ENTRY_TYPE_OPT)
        self.assertEqual(r[1].get_name(), "c")
        self.assertEqual(r[1].get_value(), ["abc", "def"])

    def testMakeObjOptList5(self):
        v, r = dsl_type20.make_obj_opt_list(dsl_type20.DSLType20_Config(), [ ("a", "b"), ("c", ["abc", None]) ])
        self.assertFalse(v)

    def testOptListHas(self):
        v, r = dsl_type20.make_obj_opt_list(dsl_type20.DSLType20_Config(), [ ("a", "b"), ("c", None) ])
        self.assertTrue(v)
        options = r
        v, r = dsl_type20.opt_list_has(options, "a")
        self.assertTrue(v)
        self.assertEqual(r.get_name(), "a")
        v, r = dsl_type20.opt_list_has(options, "b")
        self.assertFalse(v)
        self.assertEqual(r, None)
        v, r = dsl_type20.opt_list_has(options, "c")
        self.assertTrue(v)
        self.assertEqual(r.get_name(), "c")

    def testInheritOptionsHelper1(self):
        v, r = dsl_type20.make_obj_opt_list(dsl_type20.DSLType20_Config(), [ ("a", "b") ])
        self.assertTrue(v)
        parent_opts = r
        v, r = dsl_type20.make_obj_opt_list(dsl_type20.DSLType20_Config(), [ ("1", "2") ])
        self.assertTrue(v)
        new_opts = r
        self.assertEqual(dsl_type20.convert_opt_obj_list_to_neutral_format(dsl_type20.inherit_options_helper(parent_opts, new_opts)), [ ("a", "b"), ("1", "2") ])

    def testInheritOptionsHelper2(self):
        v, r = dsl_type20.make_obj_opt_list(dsl_type20.DSLType20_Config(), [ ("a", "b") ])
        self.assertTrue(v)
        parent_opts = r
        v, r = dsl_type20.make_obj_opt_list(dsl_type20.DSLType20_Config(), [ ("a", "2") ])
        self.assertTrue(v)
        new_opts = r
        self.assertEqual(dsl_type20.convert_opt_obj_list_to_neutral_format(dsl_type20.inherit_options_helper(parent_opts, new_opts)), [ ("a", "2") ])

    def testInheritOptionsHelper3(self):
        v, r = dsl_type20.make_obj_opt_list(dsl_type20.DSLType20_Config(), [ ("a", None) ])
        self.assertTrue(v)
        parent_opts = r
        v, r = dsl_type20.make_obj_opt_list(dsl_type20.DSLType20_Config(), [ ("a", "2") ])
        self.assertTrue(v)
        new_opts = r
        self.assertEqual(dsl_type20.convert_opt_obj_list_to_neutral_format(dsl_type20.inherit_options_helper(parent_opts, new_opts)), [ ("a", "2") ])

    def testInheritOptionsHelper4(self):
        v, r = dsl_type20.make_obj_opt_list(dsl_type20.DSLType20_Config(), [ ("a", "b") ])
        self.assertTrue(v)
        parent_opts = r
        v, r = dsl_type20.make_obj_opt_list(dsl_type20.DSLType20_Config(), [ ("a", None) ])
        self.assertTrue(v)
        new_opts = r
        self.assertEqual(dsl_type20.convert_opt_obj_list_to_neutral_format(dsl_type20.inherit_options_helper(parent_opts, new_opts)), [ ("a", None) ])

    def testInheritOptionsHelper5(self):
        v, r = dsl_type20.make_obj_opt_list(dsl_type20.DSLType20_Config(), [ ("a", None), ("1", "2") ])
        self.assertTrue(v)
        parent_opts = r
        v, r = dsl_type20.make_obj_opt_list(dsl_type20.DSLType20_Config(), [ ("a", None) ])
        self.assertTrue(v)
        new_opts = r
        self.assertEqual(dsl_type20.convert_opt_obj_list_to_neutral_format(dsl_type20.inherit_options_helper(parent_opts, new_opts)), [ ("1", "2") ])

    def testInheritOptionsHelper6(self):
        v, r = dsl_type20.make_obj_opt_list(dsl_type20.DSLType20_Config(), [ ("a", None) ])
        self.assertTrue(v)
        parent_opts = r
        v, r = dsl_type20.make_obj_opt_list(dsl_type20.DSLType20_Config(), [ ("a", None), ("1", "2") ])
        self.assertTrue(v)
        new_opts = r
        self.assertEqual(dsl_type20.convert_opt_obj_list_to_neutral_format(dsl_type20.inherit_options_helper(parent_opts, new_opts)), [ ("1", "2") ])

    def testInheritOptionsHelper7(self):
        v, r = dsl_type20.make_obj_opt_list(dsl_type20.DSLType20_Config(), [ ("a", "") ])
        self.assertTrue(v)
        parent_opts = r
        v, r = dsl_type20.make_obj_opt_list(dsl_type20.DSLType20_Config(), [ ("a", ""), ("1", "2") ])
        self.assertTrue(v)
        new_opts = r
        self.assertEqual(dsl_type20.convert_opt_obj_list_to_neutral_format(dsl_type20.inherit_options_helper(parent_opts, new_opts)), [ ("a", ""), ("1", "2") ])

    def testInheritOptionsHelper8(self):
        v, r = dsl_type20.make_obj_opt_list(dsl_type20.DSLType20_Config(), [ ("a", "b"), ("c", "d") ])
        self.assertTrue(v)
        parent_opts = r
        v, r = dsl_type20.make_obj_opt_list(dsl_type20.DSLType20_Config(), [ ("1", "2"), ("3", "4") ])
        self.assertTrue(v)
        new_opts = r
        self.assertEqual(dsl_type20.convert_opt_obj_list_to_neutral_format(dsl_type20.inherit_options_helper(parent_opts, new_opts)), [ ("a", "b"), ("c", "d"), ("1", "2"), ("3", "4") ])

    def testInheritOptionsHelper9(self):
        v, r = dsl_type20.make_obj_opt_list(dsl_type20.DSLType20_Config(), [ ("a", "b"), ("c", "d") ])
        self.assertTrue(v)
        parent_opts = r
        v, r = dsl_type20.make_obj_opt_list(dsl_type20.DSLType20_Config(), [ ("a", "b"), ("c", "d") ])
        self.assertTrue(v)
        new_opts = r
        self.assertEqual(dsl_type20.convert_opt_obj_list_to_neutral_format(dsl_type20.inherit_options_helper(parent_opts, new_opts)), [ ("a", "b"), ("c", "d") ])

    def testInheritOptionsHelper10(self):
        v, r = dsl_type20.make_obj_opt_list(dsl_type20.DSLType20_Config(), [ ("a", "b"), ("c", "d") ])
        self.assertTrue(v)
        parent_opts = r
        v, r = dsl_type20.make_obj_opt_list(dsl_type20.DSLType20_Config(), [ ("a", []), ("c", []) ])
        self.assertTrue(v)
        new_opts = r
        self.assertEqual(dsl_type20.convert_opt_obj_list_to_neutral_format(dsl_type20.inherit_options_helper(parent_opts, new_opts)), [ ("a", []), ("c", []) ])

    def testInheritOptionsHelper11(self):
        v, r = dsl_type20.make_obj_opt_list(dsl_type20.DSLType20_Config(), [ ("a", "b"), ("c", "d") ])
        self.assertTrue(v)
        parent_opts = r
        v, r = dsl_type20.make_obj_opt_list(dsl_type20.DSLType20_Config(), [ ("a", ["b", "d"]), ("c", ["f", "g"]) ])
        self.assertTrue(v)
        new_opts = r
        self.assertEqual(dsl_type20.convert_opt_obj_list_to_neutral_format(dsl_type20.inherit_options_helper(parent_opts, new_opts)), [ ("a", ["b", "d"]), ("c", ["f", "g"]) ])

    def testDSLType20_Value1(self):

        test_cfg = dsl_type20.DSLType20_Config()
        test_val = dsl_type20.DSLType20_Value(test_cfg)
        self.assertEqual(test_val.configs, test_cfg)
        self.assertEqual(len(test_val.internal_data), 0)
        self.assertEqual(test_val.internal_data, [])

        r = test_val.get_resolved()
        self.assertEqual(r, None)

        r = test_val.get_serialized()
        self.assertEqual(r, None)

        test_val.add_immediate("abc")
        self.assertEqual(len(test_val.internal_data), 1)
        self.assertEqual(test_val.internal_data, [(dsl_type20.DSLTYPE20_ENTRY_VALUE_TYPE_IMMEDIATE, "abc")])

        r = test_val.get_resolved()
        self.assertEqual(r, "abc")

        r = test_val.get_serialized()
        self.assertEqual(r, "\"abc\"")

        test_val.add_plus()
        self.assertEqual(len(test_val.internal_data), 2)
        self.assertEqual(test_val.internal_data, [(dsl_type20.DSLTYPE20_ENTRY_VALUE_TYPE_IMMEDIATE, "abc"), (dsl_type20.DSLTYPE20_ENTRY_VALUE_TYPE_PLUS, None)])

        r = test_val.get_resolved()
        self.assertEqual(r, "abc")

        r = test_val.get_serialized()
        self.assertEqual(r, "\"abc\" + ")

        os.environ[ (self.reserved_test_env_var_1[1:]) ] = "test-value-1"
        test_val.add_envvar(self.reserved_test_env_var_1[1:])
        self.assertEqual(len(test_val.internal_data), 3)
        self.assertEqual(test_val.internal_data, [(dsl_type20.DSLTYPE20_ENTRY_VALUE_TYPE_IMMEDIATE, "abc"), (dsl_type20.DSLTYPE20_ENTRY_VALUE_TYPE_PLUS, None), (dsl_type20.DSLTYPE20_ENTRY_VALUE_TYPE_ENVVAR, self.reserved_test_env_var_1[1:])])

        r = test_val.get_resolved()
        self.assertEqual(r, "abctest-value-1")

        r = test_val.get_serialized()
        self.assertEqual(r, "\"abc\" + " + self.reserved_test_env_var_1)

    def testDSLType20_Value2(self):

        test_cfg = dsl_type20.DSLType20_Config()
        test_val = dsl_type20.DSLType20_Value(test_cfg)
        self.assertEqual(test_val.configs, test_cfg)
        self.assertEqual(len(test_val.internal_data), 0)
        self.assertEqual(test_val.internal_data, [])

        r = test_val.get_resolved()
        self.assertEqual(r, None)

        r = test_val.get_serialized()
        self.assertEqual(r, None)

        ex_flag = False
        try:
            test_val.add_immediate("abc\ndef")
        except BaseException as ex:
            ex_flag = isinstance(ex, mvtools_exception.mvtools_exception)
        self.assertTrue(ex_flag)

        self.assertEqual(len(test_val.internal_data), 0)
        self.assertEqual(test_val.internal_data, [])

        r = test_val.get_resolved()
        self.assertEqual(r, None)

        r = test_val.get_serialized()
        self.assertEqual(r, None)

    def testDSLType20_Value3(self):

        test_cfg = dsl_type20.DSLType20_Config()
        test_val = dsl_type20.DSLType20_Value(test_cfg)
        self.assertEqual(test_val.configs, test_cfg)
        self.assertEqual(len(test_val.internal_data), 0)
        self.assertEqual(test_val.internal_data, [])

        r = test_val.get_resolved()
        self.assertEqual(r, None)

        r = test_val.get_serialized()
        self.assertEqual(r, None)

        ex_flag = False
        try:
            test_val.add_immediate("abc\x00def")
        except BaseException as ex:
            ex_flag = isinstance(ex, mvtools_exception.mvtools_exception)
        self.assertTrue(ex_flag)

        self.assertEqual(len(test_val.internal_data), 0)
        self.assertEqual(test_val.internal_data, [])

        r = test_val.get_resolved()
        self.assertEqual(r, None)

        r = test_val.get_serialized()
        self.assertEqual(r, None)

    def testDSLType20_Value4(self):

        test_cfg = dsl_type20.DSLType20_Config(True)
        test_val = dsl_type20.DSLType20_Value(test_cfg)
        self.assertEqual(test_val.configs, test_cfg)
        self.assertEqual(len(test_val.internal_data), 0)
        self.assertEqual(test_val.internal_data, [])

        r = test_val.get_resolved()
        self.assertEqual(r, None)

        r = test_val.get_serialized()
        self.assertEqual(r, None)

        test_val.add_immediate("~")
        self.assertEqual(len(test_val.internal_data), 1)
        self.assertEqual(test_val.internal_data, [(dsl_type20.DSLTYPE20_ENTRY_VALUE_TYPE_IMMEDIATE, "~")])

        r = test_val.get_resolved()
        self.assertEqual(r, os.path.expanduser("~"))

        r = test_val.get_serialized()
        self.assertEqual(r, "\"~\"")

    def testDSLType20_Value5(self):

        test_cfg = dsl_type20.DSLType20_Config(False)
        test_val = dsl_type20.DSLType20_Value(test_cfg)
        self.assertEqual(test_val.configs, test_cfg)
        self.assertEqual(len(test_val.internal_data), 0)
        self.assertEqual(test_val.internal_data, [])

        r = test_val.get_resolved()
        self.assertEqual(r, None)

        r = test_val.get_serialized()
        self.assertEqual(r, None)

        test_val.add_immediate("~")
        self.assertEqual(len(test_val.internal_data), 1)
        self.assertEqual(test_val.internal_data, [(dsl_type20.DSLTYPE20_ENTRY_VALUE_TYPE_IMMEDIATE, "~")])

        r = test_val.get_resolved()
        self.assertEqual(r, "~")

        r = test_val.get_serialized()
        self.assertEqual(r, "\"~\"")

    def testDSLType20_Variable1(self):
        ex_flag = False
        try:
            var_inst = dsl_type20.DSLType20_Variable(dsl_type20.DSLType20_Config(), "", None)
        except BaseException as ex:
            ex_flag = isinstance(ex, mvtools_exception.mvtools_exception)
        self.assertTrue(ex_flag)

    def testDSLType20_Variable2(self):
        var_inst = dsl_type20.DSLType20_Variable(dsl_type20.DSLType20_Config(), "a", None)
        self.assertTrue(isinstance(var_inst, dsl_type20.DSLType20_Variable))
        self.assertTrue(isinstance(var_inst.configs, dsl_type20.DSLType20_Config))
        self.assertEqual(var_inst.get_type(), dsl_type20.DSLTYPE20_ENTRY_TYPE_VAR)
        self.assertEqual(var_inst.name, "a")
        self.assertEqual(var_inst.get_name(), "a")
        self.assertEqual(var_inst.value, None)
        self.assertEqual(var_inst.get_value_resolved(), None)
        self.assertEqual(var_inst.options, None)
        self.assertEqual(var_inst.get_options(), [])

    def testDSLType20_Variable3(self):
        opt_inst = dsl_type20.DSLType20_Option(dsl_type20.DSLType20_Config(), "b")
        var_inst = dsl_type20.DSLType20_Variable(dsl_type20.DSLType20_Config(), "a", opt_inst)
        self.assertTrue(isinstance(var_inst, dsl_type20.DSLType20_Variable))
        self.assertTrue(isinstance(var_inst.configs, dsl_type20.DSLType20_Config))
        self.assertEqual(var_inst.get_type(), dsl_type20.DSLTYPE20_ENTRY_TYPE_VAR)
        self.assertEqual(var_inst.name, "a")
        self.assertEqual(var_inst.get_name(), "a")
        self.assertEqual(var_inst.value, None)
        self.assertEqual(var_inst.get_value_resolved(), None)
        self.assertEqual(var_inst.options, opt_inst)
        self.assertEqual(var_inst.get_options(), [opt_inst])

    def testDSLType20_Variable4(self):
        opt_inst1 = dsl_type20.DSLType20_Option(dsl_type20.DSLType20_Config(), "b")
        opt_inst2 = dsl_type20.DSLType20_Option(dsl_type20.DSLType20_Config(), "c")
        var_inst = dsl_type20.DSLType20_Variable(dsl_type20.DSLType20_Config(), "a", [opt_inst1, opt_inst2])
        self.assertTrue(isinstance(var_inst, dsl_type20.DSLType20_Variable))
        self.assertTrue(isinstance(var_inst.configs, dsl_type20.DSLType20_Config))
        self.assertEqual(var_inst.get_type(), dsl_type20.DSLTYPE20_ENTRY_TYPE_VAR)
        self.assertEqual(var_inst.name, "a")
        self.assertEqual(var_inst.get_name(), "a")
        self.assertEqual(var_inst.value, None)
        self.assertEqual(var_inst.get_value_resolved(), None)
        self.assertEqual(var_inst.options, [opt_inst1, opt_inst2])
        self.assertEqual(var_inst.get_options(), [opt_inst1, opt_inst2])

    def testDSLType20_Variable5(self):
        opt_inst = dsl_type20.DSLType20_Option(dsl_type20.DSLType20_Config(), "c")
        ex_flag = False
        try:
            var_inst = dsl_type20.DSLType20_Variable(dsl_type20.DSLType20_Config(), "a", [opt_inst, 1])
        except BaseException as ex:
            ex_flag = isinstance(ex, mvtools_exception.mvtools_exception)
        self.assertTrue(ex_flag)

    def testDSLType20_Variable_NewValue1(self):
        var_inst = dsl_type20.DSLType20_Variable(dsl_type20.DSLType20_Config(), "a", [])
        self.assertEqual(var_inst.value, None)
        var_inst.new_value()
        self.assertTrue(isinstance(var_inst.value, dsl_type20.DSLType20_Value))
        var_inst.new_value()
        self.assertTrue(isinstance(var_inst.value, list))
        self.assertEqual(len(var_inst.value), 2)
        self.assertTrue(isinstance(var_inst.value[0], dsl_type20.DSLType20_Value))
        self.assertTrue(isinstance(var_inst.value[1], dsl_type20.DSLType20_Value))

    def testDSLType20_Variable_AddValueImmediate1(self):
        var_inst = dsl_type20.DSLType20_Variable(dsl_type20.DSLType20_Config(), "a", [])
        ex_flag = False
        try:
            var_inst.add_value_immediate("val")
        except BaseException as ex:
            ex_flag = isinstance(ex, mvtools_exception.mvtools_exception)
        self.assertTrue(ex_flag)

    def testDSLType20_Variable_AddValueImmediate2(self):
        var_inst = dsl_type20.DSLType20_Variable(dsl_type20.DSLType20_Config(), "a", [])
        self.assertEqual(var_inst.value, None)
        var_inst.new_value()
        self.assertTrue(isinstance(var_inst.value, dsl_type20.DSLType20_Value))
        self.assertEqual(var_inst.value.internal_data, [])
        ex_flag = False
        try:
            var_inst.add_value_immediate("val\n")
        except BaseException as ex:
            ex_flag = isinstance(ex, mvtools_exception.mvtools_exception)
        self.assertTrue(ex_flag)

    def testDSLType20_Variable_AddValueImmediate3(self):
        var_inst = dsl_type20.DSLType20_Variable(dsl_type20.DSLType20_Config(), "a", [])
        self.assertEqual(var_inst.value, None)
        var_inst.new_value()
        self.assertTrue(isinstance(var_inst.value, dsl_type20.DSLType20_Value))
        self.assertEqual(var_inst.value.internal_data, [])
        var_inst.add_value_immediate("val1")
        self.assertEqual(var_inst.value.internal_data, [(dsl_type20.DSLTYPE20_ENTRY_VALUE_TYPE_IMMEDIATE, "val1")])
        var_inst.add_value_immediate("val2")
        self.assertEqual(var_inst.value.internal_data, [(dsl_type20.DSLTYPE20_ENTRY_VALUE_TYPE_IMMEDIATE, "val1"), (dsl_type20.DSLTYPE20_ENTRY_VALUE_TYPE_PLUS, None), (dsl_type20.DSLTYPE20_ENTRY_VALUE_TYPE_IMMEDIATE, "val2")])

    def testDSLType20_Variable_AddValueImmediate4(self):
        var_inst = dsl_type20.DSLType20_Variable(dsl_type20.DSLType20_Config(), "a", [])
        self.assertEqual(var_inst.value, None)
        var_inst.new_value()
        var_inst.new_value()
        self.assertTrue(isinstance(var_inst.value, list))
        self.assertEqual(var_inst.value[0].internal_data, [])
        self.assertEqual(var_inst.value[1].internal_data, [])
        var_inst.add_value_immediate("val1")
        self.assertEqual(var_inst.value[0].internal_data, [])
        self.assertEqual(var_inst.value[1].internal_data, [(dsl_type20.DSLTYPE20_ENTRY_VALUE_TYPE_IMMEDIATE, "val1")])
        var_inst.add_value_immediate("val2")
        self.assertEqual(var_inst.value[0].internal_data, [])
        self.assertEqual(var_inst.value[1].internal_data, [(dsl_type20.DSLTYPE20_ENTRY_VALUE_TYPE_IMMEDIATE, "val1"), (dsl_type20.DSLTYPE20_ENTRY_VALUE_TYPE_PLUS, None), (dsl_type20.DSLTYPE20_ENTRY_VALUE_TYPE_IMMEDIATE, "val2")])

    def testDSLType20_Variable_AddValueEnvvar1(self):
        var_inst = dsl_type20.DSLType20_Variable(dsl_type20.DSLType20_Config(), "a", [])
        ex_flag = False
        try:
            var_inst.add_value_envvar("envvar")
        except BaseException as ex:
            ex_flag = isinstance(ex, mvtools_exception.mvtools_exception)
        self.assertTrue(ex_flag)

    def testDSLType20_Variable_AddValueEnvvar2(self):
        var_inst = dsl_type20.DSLType20_Variable(dsl_type20.DSLType20_Config(), "a", [])
        self.assertEqual(var_inst.value, None)
        var_inst.new_value()
        self.assertTrue(isinstance(var_inst.value, dsl_type20.DSLType20_Value))
        self.assertEqual(var_inst.value.internal_data, [])
        var_inst.add_value_envvar("envvar1")
        self.assertEqual(var_inst.value.internal_data, [(dsl_type20.DSLTYPE20_ENTRY_VALUE_TYPE_ENVVAR, "envvar1")])
        var_inst.add_value_envvar("envvar2")
        self.assertEqual(var_inst.value.internal_data, [(dsl_type20.DSLTYPE20_ENTRY_VALUE_TYPE_ENVVAR, "envvar1"), (dsl_type20.DSLTYPE20_ENTRY_VALUE_TYPE_PLUS, None), (dsl_type20.DSLTYPE20_ENTRY_VALUE_TYPE_ENVVAR, "envvar2")])

    def testDSLType20_Variable_AddValueEnvvar3(self):
        var_inst = dsl_type20.DSLType20_Variable(dsl_type20.DSLType20_Config(), "a", [])
        self.assertEqual(var_inst.value, None)
        var_inst.new_value()
        var_inst.new_value()
        self.assertTrue(isinstance(var_inst.value, list))
        self.assertEqual(var_inst.value[0].internal_data, [])
        self.assertEqual(var_inst.value[1].internal_data, [])
        var_inst.add_value_envvar("envvar1")
        self.assertEqual(var_inst.value[0].internal_data, [])
        self.assertEqual(var_inst.value[1].internal_data, [(dsl_type20.DSLTYPE20_ENTRY_VALUE_TYPE_ENVVAR, "envvar1")])
        var_inst.add_value_envvar("envvar2")
        self.assertEqual(var_inst.value[0].internal_data, [])
        self.assertEqual(var_inst.value[1].internal_data, [(dsl_type20.DSLTYPE20_ENTRY_VALUE_TYPE_ENVVAR, "envvar1"), (dsl_type20.DSLTYPE20_ENTRY_VALUE_TYPE_PLUS, None), (dsl_type20.DSLTYPE20_ENTRY_VALUE_TYPE_ENVVAR, "envvar2")])

    def testDSLType20_Variable_GetValueResolved1(self):
        var_inst = dsl_type20.DSLType20_Variable(dsl_type20.DSLType20_Config(), "a", [])
        self.assertEqual(var_inst.get_value_resolved(), None)

    def testDSLType20_Variable_GetValueResolved2(self):
        var_inst = dsl_type20.DSLType20_Variable(dsl_type20.DSLType20_Config(), "a", [])
        var_inst.new_value()
        self.assertEqual(var_inst.get_value_resolved(), None)

    def testDSLType20_Variable_GetValueResolved3(self):
        var_inst = dsl_type20.DSLType20_Variable(dsl_type20.DSLType20_Config(), "a", [])
        var_inst.new_value()
        var_inst.add_value_immediate("")
        self.assertEqual(var_inst.get_value_resolved(), "")

    def testDSLType20_Variable_GetValueResolved4(self):
        var_inst = dsl_type20.DSLType20_Variable(dsl_type20.DSLType20_Config(), "a", [])
        var_inst.new_value()
        var_inst.add_value_immediate("")
        var_inst.add_value_immediate("")
        self.assertEqual(var_inst.get_value_resolved(), "")

    def testDSLType20_Variable_GetValueResolved5(self):
        var_inst = dsl_type20.DSLType20_Variable(dsl_type20.DSLType20_Config(), "a", [])
        var_inst.new_value()
        var_inst.add_value_immediate("val1")
        var_inst.add_value_immediate("val2")
        self.assertEqual(var_inst.get_value_resolved(), "val1val2")

    def testDSLType20_Variable_GetValueResolved6(self):
        os.environ[ (self.reserved_test_env_var_1[1:]) ] = "-envvar-value-1-"
        var_inst = dsl_type20.DSLType20_Variable(dsl_type20.DSLType20_Config(), "a", [])
        var_inst.new_value()
        var_inst.add_value_immediate("val1")
        var_inst.add_value_envvar(self.reserved_test_env_var_1[1:])
        var_inst.add_value_immediate("val2")
        self.assertEqual(var_inst.get_value_resolved(), "val1-envvar-value-1-val2")

    def testDSLType20_Variable_GetValueResolved7(self):
        os.environ[ (self.reserved_test_env_var_1[1:]) ] = "-envvar-value-1-"
        var_inst = dsl_type20.DSLType20_Variable(dsl_type20.DSLType20_Config(), "a", [])
        var_inst.new_value()
        var_inst.add_value_immediate("val1")
        var_inst.add_value_envvar(self.reserved_test_env_var_1[1:])
        var_inst.add_value_immediate("val2")
        self.assertEqual(var_inst.get_value_resolved(), "val1-envvar-value-1-val2")
        os.environ[ (self.reserved_test_env_var_1[1:]) ] = "-envvar-value-3-"
        self.assertEqual(var_inst.get_value_resolved(), "val1-envvar-value-3-val2")

    def testDSLType20_Variable_GetValueResolved8(self):
        var_inst = dsl_type20.DSLType20_Variable(dsl_type20.DSLType20_Config(), "a", [])
        var_inst.new_value()
        var_inst.add_value_immediate("")
        var_inst.new_value()
        var_inst.add_value_immediate("")
        self.assertEqual(var_inst.get_value_resolved(), ["", ""])

    def testDSLType20_Variable_GetValueResolved9(self):
        var_inst = dsl_type20.DSLType20_Variable(dsl_type20.DSLType20_Config(), "a", [])
        var_inst.new_value()
        var_inst.add_value_immediate("val1")
        var_inst.new_value()
        var_inst.add_value_immediate("val2")
        self.assertEqual(var_inst.get_value_resolved(), ["val1", "val2"])

    def testDSLType20_Variable_GetValueResolved10(self):
        os.environ[ (self.reserved_test_env_var_1[1:]) ] = "-envvar-value-1-"
        var_inst = dsl_type20.DSLType20_Variable(dsl_type20.DSLType20_Config(), "a", [])
        var_inst.new_value()
        var_inst.add_value_immediate("val1")
        var_inst.new_value()
        var_inst.add_value_envvar(self.reserved_test_env_var_1[1:])
        var_inst.new_value()
        var_inst.add_value_immediate("val2")
        self.assertEqual(var_inst.get_value_resolved(), ["val1", "-envvar-value-1-", "val2"])

    def testDSLType20_Variable_GetValueResolved11(self):
        os.environ[ (self.reserved_test_env_var_1[1:]) ] = "-envvar-value-1-"
        var_inst = dsl_type20.DSLType20_Variable(dsl_type20.DSLType20_Config(), "a", [])
        var_inst.new_value()
        var_inst.add_value_immediate("val1")
        var_inst.new_value()
        var_inst.add_value_envvar(self.reserved_test_env_var_1[1:])
        var_inst.new_value()
        var_inst.add_value_immediate("val2")
        self.assertEqual(var_inst.get_value_resolved(), ["val1", "-envvar-value-1-", "val2"])
        os.environ[ (self.reserved_test_env_var_1[1:]) ] = "-envvar-value-3-"
        self.assertEqual(var_inst.get_value_resolved(), ["val1", "-envvar-value-3-", "val2"])

    def testDSLType20_Variable_GetValueResolved12(self):
        var_inst = dsl_type20.DSLType20_Variable(dsl_type20.DSLType20_Config(True), "a", [])
        var_inst.new_value()
        var_inst.add_value_immediate("~")
        self.assertEqual(var_inst.get_value_resolved(), os.path.expanduser("~"))

    def testDSLType20_Variable_GetValueResolved13(self):
        var_inst = dsl_type20.DSLType20_Variable(dsl_type20.DSLType20_Config(False), "a", [])
        var_inst.new_value()
        var_inst.add_value_immediate("~")
        self.assertEqual(var_inst.get_value_resolved(), "~")

    def testDSLType20_Variable_GetValueSerialized1(self):
        var_inst = dsl_type20.DSLType20_Variable(dsl_type20.DSLType20_Config(), "a", [])
        self.assertEqual(var_inst.get_value_serialized(), None)

    def testDSLType20_Variable_GetValueSerialized2(self):
        var_inst = dsl_type20.DSLType20_Variable(dsl_type20.DSLType20_Config(), "a", [])
        var_inst.new_value()
        self.assertEqual(var_inst.get_value_serialized(), None)

    def testDSLType20_Variable_GetValueSerialized3(self):
        var_inst = dsl_type20.DSLType20_Variable(dsl_type20.DSLType20_Config(), "a", [])
        var_inst.new_value()
        var_inst.add_value_immediate("")
        self.assertEqual(var_inst.get_value_serialized(), "\"\"")

    def testDSLType20_Variable_GetValueSerialized4(self):
        var_inst = dsl_type20.DSLType20_Variable(dsl_type20.DSLType20_Config(), "a", [])
        var_inst.new_value()
        var_inst.add_value_immediate("")
        var_inst.add_value_immediate("")
        self.assertEqual(var_inst.get_value_serialized(), "\"\" + \"\"")

    def testDSLType20_Variable_GetValueSerialized5(self):
        var_inst = dsl_type20.DSLType20_Variable(dsl_type20.DSLType20_Config(), "a", [])
        var_inst.new_value()
        var_inst.add_value_immediate("val1")
        var_inst.add_value_immediate("val2")
        self.assertEqual(var_inst.get_value_serialized(), "\"val1\" + \"val2\"")

    def testDSLType20_Variable_GetValueSerialized6(self):
        os.environ[ (self.reserved_test_env_var_1[1:]) ] = "-envvar-value-1-"
        var_inst = dsl_type20.DSLType20_Variable(dsl_type20.DSLType20_Config(), "a", [])
        var_inst.new_value()
        var_inst.add_value_immediate("val1")
        var_inst.add_value_envvar(self.reserved_test_env_var_1[1:])
        var_inst.add_value_immediate("val2")
        self.assertEqual(var_inst.get_value_serialized(), "\"val1\" + $%s + \"val2\"" % self.reserved_test_env_var_1[1:])

    def testDSLType20_Variable_GetValueSerialized7(self):
        var_inst = dsl_type20.DSLType20_Variable(dsl_type20.DSLType20_Config(), "a", [])
        var_inst.new_value()
        var_inst.add_value_immediate("")
        var_inst.new_value()
        var_inst.add_value_immediate("")
        self.assertEqual(var_inst.get_value_serialized(), "(\"\", \"\")")

    def testDSLType20_Variable_GetValueSerialized8(self):
        var_inst = dsl_type20.DSLType20_Variable(dsl_type20.DSLType20_Config(), "a", [])
        var_inst.new_value()
        var_inst.add_value_immediate("val1")
        var_inst.new_value()
        var_inst.add_value_immediate("val2")
        self.assertEqual(var_inst.get_value_serialized(), "(\"val1\", \"val2\")")

    def testDSLType20_Variable_GetValueSerialized9(self):
        os.environ[ (self.reserved_test_env_var_1[1:]) ] = "-envvar-value-1-"
        var_inst = dsl_type20.DSLType20_Variable(dsl_type20.DSLType20_Config(), "a", [])
        var_inst.new_value()
        var_inst.add_value_immediate("val1")
        var_inst.new_value()
        var_inst.add_value_envvar(self.reserved_test_env_var_1[1:])
        var_inst.new_value()
        var_inst.add_value_immediate("val2")
        self.assertEqual(var_inst.get_value_serialized(), "(\"val1\", $%s, \"val2\")" % self.reserved_test_env_var_1[1:])

    def testDSLType20_Variable_GetValueSerialized10(self):
        var_inst = dsl_type20.DSLType20_Variable(dsl_type20.DSLType20_Config(True), "a", [])
        var_inst.new_value()
        var_inst.add_value_immediate("~")
        self.assertEqual(var_inst.get_value_serialized(), "\"~\"")

    def testDSLType20_Variable_GetValueSerialized11(self):
        var_inst = dsl_type20.DSLType20_Variable(dsl_type20.DSLType20_Config(False), "a", [])
        var_inst.new_value()
        var_inst.add_value_immediate("~")
        self.assertEqual(var_inst.get_value_serialized(), "\"~\"")

    def testDSLType20_Option1(self):
        ex_flag = False
        try:
            obj_inst = dsl_type20.DSLType20_Option(dsl_type20.DSLType20_Config(), "")
        except BaseException as ex:
            ex_flag = isinstance(ex, mvtools_exception.mvtools_exception)
        self.assertTrue(ex_flag)

    def testDSLType20_Option2(self):
        obj_inst = dsl_type20.DSLType20_Option(dsl_type20.DSLType20_Config(), "a")
        self.assertTrue(isinstance(obj_inst, dsl_type20.DSLType20_Option))
        self.assertTrue(isinstance(obj_inst.configs, dsl_type20.DSLType20_Config))
        self.assertEqual(obj_inst.get_type(), dsl_type20.DSLTYPE20_ENTRY_TYPE_OPT)
        self.assertEqual(obj_inst.name, "a")
        self.assertEqual(obj_inst.get_name(), "a")
        self.assertEqual(obj_inst.value, None)
        self.assertEqual(obj_inst.get_value(), None)

    def testDSLType20_Option_NewValue1(self):
        obj_inst = dsl_type20.DSLType20_Option(dsl_type20.DSLType20_Config(), "a")
        self.assertEqual(obj_inst.value, None)
        obj_inst.new_value()
        self.assertTrue(isinstance(obj_inst.value, dsl_type20.DSLType20_Value))
        obj_inst.new_value()
        self.assertTrue(isinstance(obj_inst.value, list))
        self.assertEqual(len(obj_inst.value), 2)
        self.assertTrue(isinstance(obj_inst.value[0], dsl_type20.DSLType20_Value))
        self.assertTrue(isinstance(obj_inst.value[1], dsl_type20.DSLType20_Value))

    def testDSLType20_Option_AddValueImmediate1(self):
        obj_inst = dsl_type20.DSLType20_Option(dsl_type20.DSLType20_Config(), "a")
        ex_flag = False
        try:
            obj_inst.add_value_immediate("val")
        except BaseException as ex:
            ex_flag = isinstance(ex, mvtools_exception.mvtools_exception)
        self.assertTrue(ex_flag)

    def testDSLType20_Option_AddValueImmediate2(self):
        obj_inst = dsl_type20.DSLType20_Option(dsl_type20.DSLType20_Config(), "a")
        self.assertEqual(obj_inst.value, None)
        obj_inst.new_value()
        self.assertTrue(isinstance(obj_inst.value, dsl_type20.DSLType20_Value))
        self.assertEqual(obj_inst.value.internal_data, [])
        ex_flag = False
        try:
            obj_inst.add_value_immediate("val\n")
        except BaseException as ex:
            ex_flag = isinstance(ex, mvtools_exception.mvtools_exception)
        self.assertTrue(ex_flag)

    def testDSLType20_Option_AddValueImmediate3(self):
        obj_inst = dsl_type20.DSLType20_Option(dsl_type20.DSLType20_Config(), "a")
        self.assertEqual(obj_inst.value, None)
        obj_inst.new_value()
        self.assertTrue(isinstance(obj_inst.value, dsl_type20.DSLType20_Value))
        self.assertEqual(obj_inst.value.internal_data, [])
        obj_inst.add_value_immediate("val1")
        self.assertEqual(obj_inst.value.internal_data, [(dsl_type20.DSLTYPE20_ENTRY_VALUE_TYPE_IMMEDIATE, "val1")])
        obj_inst.add_value_immediate("val2")
        self.assertEqual(obj_inst.value.internal_data, [(dsl_type20.DSLTYPE20_ENTRY_VALUE_TYPE_IMMEDIATE, "val1"), (dsl_type20.DSLTYPE20_ENTRY_VALUE_TYPE_PLUS, None), (dsl_type20.DSLTYPE20_ENTRY_VALUE_TYPE_IMMEDIATE, "val2")])

    def testDSLType20_Option_AddValueImmediate4(self):
        obj_inst = dsl_type20.DSLType20_Option(dsl_type20.DSLType20_Config(), "a")
        self.assertEqual(obj_inst.value, None)
        obj_inst.new_value()
        obj_inst.new_value()
        self.assertTrue(isinstance(obj_inst.value, list))
        self.assertEqual(obj_inst.value[0].internal_data, [])
        self.assertEqual(obj_inst.value[1].internal_data, [])
        obj_inst.add_value_immediate("val1")
        self.assertEqual(obj_inst.value[0].internal_data, [])
        self.assertEqual(obj_inst.value[1].internal_data, [(dsl_type20.DSLTYPE20_ENTRY_VALUE_TYPE_IMMEDIATE, "val1")])
        obj_inst.add_value_immediate("val2")
        self.assertEqual(obj_inst.value[0].internal_data, [])
        self.assertEqual(obj_inst.value[1].internal_data, [(dsl_type20.DSLTYPE20_ENTRY_VALUE_TYPE_IMMEDIATE, "val1"), (dsl_type20.DSLTYPE20_ENTRY_VALUE_TYPE_PLUS, None), (dsl_type20.DSLTYPE20_ENTRY_VALUE_TYPE_IMMEDIATE, "val2")])

    def testDSLType20_Option_AddValueEnvvar1(self):
        obj_inst = dsl_type20.DSLType20_Option(dsl_type20.DSLType20_Config(), "a")
        ex_flag = False
        try:
            obj_inst.add_value_envvar("envvar")
        except BaseException as ex:
            ex_flag = isinstance(ex, mvtools_exception.mvtools_exception)
        self.assertTrue(ex_flag)

    def testDSLType20_Option_AddValueEnvvar2(self):
        obj_inst = dsl_type20.DSLType20_Option(dsl_type20.DSLType20_Config(), "a")
        self.assertEqual(obj_inst.value, None)
        obj_inst.new_value()
        self.assertTrue(isinstance(obj_inst.value, dsl_type20.DSLType20_Value))
        self.assertEqual(obj_inst.value.internal_data, [])
        obj_inst.add_value_envvar("envvar1")
        self.assertEqual(obj_inst.value.internal_data, [(dsl_type20.DSLTYPE20_ENTRY_VALUE_TYPE_ENVVAR, "envvar1")])
        obj_inst.add_value_envvar("envvar2")
        self.assertEqual(obj_inst.value.internal_data, [(dsl_type20.DSLTYPE20_ENTRY_VALUE_TYPE_ENVVAR, "envvar1"), (dsl_type20.DSLTYPE20_ENTRY_VALUE_TYPE_PLUS, None), (dsl_type20.DSLTYPE20_ENTRY_VALUE_TYPE_ENVVAR, "envvar2")])

    def testDSLType20_Option_AddValueEnvvar3(self):
        obj_inst = dsl_type20.DSLType20_Option(dsl_type20.DSLType20_Config(), "a")
        self.assertEqual(obj_inst.value, None)
        obj_inst.new_value()
        obj_inst.new_value()
        self.assertTrue(isinstance(obj_inst.value, list))
        self.assertEqual(obj_inst.value[0].internal_data, [])
        self.assertEqual(obj_inst.value[1].internal_data, [])
        obj_inst.add_value_envvar("envvar1")
        self.assertEqual(obj_inst.value[0].internal_data, [])
        self.assertEqual(obj_inst.value[1].internal_data, [(dsl_type20.DSLTYPE20_ENTRY_VALUE_TYPE_ENVVAR, "envvar1")])
        obj_inst.add_value_envvar("envvar2")
        self.assertEqual(obj_inst.value[0].internal_data, [])
        self.assertEqual(obj_inst.value[1].internal_data, [(dsl_type20.DSLTYPE20_ENTRY_VALUE_TYPE_ENVVAR, "envvar1"), (dsl_type20.DSLTYPE20_ENTRY_VALUE_TYPE_PLUS, None), (dsl_type20.DSLTYPE20_ENTRY_VALUE_TYPE_ENVVAR, "envvar2")])

    def testDSLType20_Option_GetValueResolved1(self):
        obj_inst = dsl_type20.DSLType20_Option(dsl_type20.DSLType20_Config(), "a")
        self.assertEqual(obj_inst.get_value_resolved(), None)

    def testDSLType20_Option_GetValueResolved2(self):
        obj_inst = dsl_type20.DSLType20_Option(dsl_type20.DSLType20_Config(), "a")
        obj_inst.new_value()
        self.assertEqual(obj_inst.get_value_resolved(), None)

    def testDSLType20_Option_GetValueResolved3(self):
        obj_inst = dsl_type20.DSLType20_Option(dsl_type20.DSLType20_Config(), "a")
        obj_inst.new_value()
        obj_inst.add_value_immediate("")
        self.assertEqual(obj_inst.get_value_resolved(), "")

    def testDSLType20_Option_GetValueResolved4(self):
        obj_inst = dsl_type20.DSLType20_Option(dsl_type20.DSLType20_Config(), "a")
        obj_inst.new_value()
        obj_inst.add_value_immediate("")
        obj_inst.add_value_immediate("")
        self.assertEqual(obj_inst.get_value_resolved(), "")

    def testDSLType20_Option_GetValueResolved5(self):
        obj_inst = dsl_type20.DSLType20_Option(dsl_type20.DSLType20_Config(), "a")
        obj_inst.new_value()
        obj_inst.add_value_immediate("val1")
        obj_inst.add_value_immediate("val2")
        self.assertEqual(obj_inst.get_value_resolved(), "val1val2")

    def testDSLType20_Option_GetValueResolved6(self):
        os.environ[ (self.reserved_test_env_var_1[1:]) ] = "-envvar-value-1-"
        obj_inst = dsl_type20.DSLType20_Option(dsl_type20.DSLType20_Config(), "a")
        obj_inst.new_value()
        obj_inst.add_value_immediate("val1")
        obj_inst.add_value_envvar(self.reserved_test_env_var_1[1:])
        obj_inst.add_value_immediate("val2")
        self.assertEqual(obj_inst.get_value_resolved(), "val1-envvar-value-1-val2")

    def testDSLType20_Option_GetValueResolved7(self):
        os.environ[ (self.reserved_test_env_var_1[1:]) ] = "-envvar-value-1-"
        obj_inst = dsl_type20.DSLType20_Option(dsl_type20.DSLType20_Config(), "a")
        obj_inst.new_value()
        obj_inst.add_value_immediate("val1")
        obj_inst.add_value_envvar(self.reserved_test_env_var_1[1:])
        obj_inst.add_value_immediate("val2")
        self.assertEqual(obj_inst.get_value_resolved(), "val1-envvar-value-1-val2")
        os.environ[ (self.reserved_test_env_var_1[1:]) ] = "-envvar-value-3-"
        self.assertEqual(obj_inst.get_value_resolved(), "val1-envvar-value-3-val2")

    def testDSLType20_Option_GetValueResolved8(self):
        obj_inst = dsl_type20.DSLType20_Option(dsl_type20.DSLType20_Config(), "a")
        obj_inst.new_value()
        obj_inst.add_value_immediate("")
        obj_inst.new_value()
        obj_inst.add_value_immediate("")
        self.assertEqual(obj_inst.get_value_resolved(), ["", ""])

    def testDSLType20_Option_GetValueResolved9(self):
        obj_inst = dsl_type20.DSLType20_Option(dsl_type20.DSLType20_Config(), "a")
        obj_inst.new_value()
        obj_inst.add_value_immediate("val1")
        obj_inst.new_value()
        obj_inst.add_value_immediate("val2")
        self.assertEqual(obj_inst.get_value_resolved(), ["val1", "val2"])

    def testDSLType20_Option_GetValueResolved10(self):
        os.environ[ (self.reserved_test_env_var_1[1:]) ] = "-envvar-value-1-"
        obj_inst = dsl_type20.DSLType20_Option(dsl_type20.DSLType20_Config(), "a")
        obj_inst.new_value()
        obj_inst.add_value_immediate("val1")
        obj_inst.new_value()
        obj_inst.add_value_envvar(self.reserved_test_env_var_1[1:])
        obj_inst.new_value()
        obj_inst.add_value_immediate("val2")
        self.assertEqual(obj_inst.get_value_resolved(), ["val1", "-envvar-value-1-", "val2"])

    def testDSLType20_Option_GetValueResolved11(self):
        os.environ[ (self.reserved_test_env_var_1[1:]) ] = "-envvar-value-1-"
        obj_inst = dsl_type20.DSLType20_Option(dsl_type20.DSLType20_Config(), "a")
        obj_inst.new_value()
        obj_inst.add_value_immediate("val1")
        obj_inst.new_value()
        obj_inst.add_value_envvar(self.reserved_test_env_var_1[1:])
        obj_inst.new_value()
        obj_inst.add_value_immediate("val2")
        self.assertEqual(obj_inst.get_value_resolved(), ["val1", "-envvar-value-1-", "val2"])
        os.environ[ (self.reserved_test_env_var_1[1:]) ] = "-envvar-value-3-"
        self.assertEqual(obj_inst.get_value_resolved(), ["val1", "-envvar-value-3-", "val2"])

    def testDSLType20_Option_GetValueResolved12(self):
        obj_inst = dsl_type20.DSLType20_Option(dsl_type20.DSLType20_Config(True), "a")
        obj_inst.new_value()
        obj_inst.add_value_immediate("~")
        self.assertEqual(obj_inst.get_value_resolved(), os.path.expanduser("~"))

    def testDSLType20_Option_GetValueResolved13(self):
        obj_inst = dsl_type20.DSLType20_Option(dsl_type20.DSLType20_Config(False), "a")
        obj_inst.new_value()
        obj_inst.add_value_immediate("~")
        self.assertEqual(obj_inst.get_value_resolved(), "~")

    def testDSLType20_Option_GetValueSerialized1(self):
        obj_inst = dsl_type20.DSLType20_Option(dsl_type20.DSLType20_Config(), "a")
        self.assertEqual(obj_inst.get_value_serialized(), None)

    def testDSLType20_Option_GetValueSerialized2(self):
        obj_inst = dsl_type20.DSLType20_Option(dsl_type20.DSLType20_Config(), "a")
        obj_inst.new_value()
        self.assertEqual(obj_inst.get_value_serialized(), None)

    def testDSLType20_Option_GetValueSerialized3(self):
        obj_inst = dsl_type20.DSLType20_Option(dsl_type20.DSLType20_Config(), "a")
        obj_inst.new_value()
        obj_inst.add_value_immediate("")
        self.assertEqual(obj_inst.get_value_serialized(), "\"\"")

    def testDSLType20_Option_GetValueSerialized4(self):
        obj_inst = dsl_type20.DSLType20_Option(dsl_type20.DSLType20_Config(), "a")
        obj_inst.new_value()
        obj_inst.add_value_immediate("")
        obj_inst.add_value_immediate("")
        self.assertEqual(obj_inst.get_value_serialized(), "\"\" + \"\"")

    def testDSLType20_Option_GetValueSerialized5(self):
        obj_inst = dsl_type20.DSLType20_Option(dsl_type20.DSLType20_Config(), "a")
        obj_inst.new_value()
        obj_inst.add_value_immediate("val1")
        obj_inst.add_value_immediate("val2")
        self.assertEqual(obj_inst.get_value_serialized(), "\"val1\" + \"val2\"")

    def testDSLType20_Option_GetValueSerialized6(self):
        os.environ[ (self.reserved_test_env_var_1[1:]) ] = "-envvar-value-1-"
        obj_inst = dsl_type20.DSLType20_Option(dsl_type20.DSLType20_Config(), "a")
        obj_inst.new_value()
        obj_inst.add_value_immediate("val1")
        obj_inst.add_value_envvar(self.reserved_test_env_var_1[1:])
        obj_inst.add_value_immediate("val2")
        self.assertEqual(obj_inst.get_value_serialized(), "\"val1\" + $%s + \"val2\"" % self.reserved_test_env_var_1[1:])

    def testDSLType20_Option_GetValueSerialized7(self):
        obj_inst = dsl_type20.DSLType20_Option(dsl_type20.DSLType20_Config(), "a")
        obj_inst.new_value()
        obj_inst.add_value_immediate("")
        obj_inst.new_value()
        obj_inst.add_value_immediate("")
        self.assertEqual(obj_inst.get_value_serialized(), "(\"\", \"\")")

    def testDSLType20_Option_GetValueSerialized8(self):
        obj_inst = dsl_type20.DSLType20_Option(dsl_type20.DSLType20_Config(), "a")
        obj_inst.new_value()
        obj_inst.add_value_immediate("val1")
        obj_inst.new_value()
        obj_inst.add_value_immediate("val2")
        self.assertEqual(obj_inst.get_value_serialized(), "(\"val1\", \"val2\")")

    def testDSLType20_Option_GetValueSerialized9(self):
        os.environ[ (self.reserved_test_env_var_1[1:]) ] = "-envvar-value-1-"
        obj_inst = dsl_type20.DSLType20_Option(dsl_type20.DSLType20_Config(), "a")
        obj_inst.new_value()
        obj_inst.add_value_immediate("val1")
        obj_inst.new_value()
        obj_inst.add_value_envvar(self.reserved_test_env_var_1[1:])
        obj_inst.new_value()
        obj_inst.add_value_immediate("val2")
        self.assertEqual(obj_inst.get_value_serialized(), "(\"val1\", $%s, \"val2\")" % self.reserved_test_env_var_1[1:])

    def testDSLType20_Option_GetValueSerialized10(self):
        obj_inst = dsl_type20.DSLType20_Option(dsl_type20.DSLType20_Config(True), "a")
        obj_inst.new_value()
        obj_inst.add_value_immediate("~")
        self.assertEqual(obj_inst.get_value_serialized(), "\"~\"")

    def testDSLType20_Option_GetValueSerialized11(self):
        obj_inst = dsl_type20.DSLType20_Option(dsl_type20.DSLType20_Config(False), "a")
        obj_inst.new_value()
        obj_inst.add_value_immediate("~")
        self.assertEqual(obj_inst.get_value_serialized(), "\"~\"")

    def testDSLType20_Context1(self):
        ctx_inst = dsl_type20.DSLType20_Context(None, "a", None)
        self.assertTrue(isinstance(ctx_inst, dsl_type20.DSLType20_Context))
        self.assertEqual(ctx_inst.get_type(), dsl_type20.DSLTYPE20_ENTRY_TYPE_CTX)
        self.assertEqual(ctx_inst.ptr_parent, None)
        self.assertEqual(ctx_inst.get_parent_ptr(), None)
        self.assertEqual(ctx_inst.name, "a")
        self.assertEqual(ctx_inst.get_name(), "a")
        self.assertEqual(ctx_inst.options, None)
        self.assertEqual(ctx_inst.get_options(), [])
        self.assertEqual(ctx_inst.entries, [])

    def testDSLType20_Context2(self):
        ex_flag = False
        try:
            ctx_inst = dsl_type20.DSLType20_Context(None, "", None)
        except BaseException as ex:
            ex_flag = isinstance(ex, mvtools_exception.mvtools_exception)
        self.assertTrue(ex_flag)

    def testDSLType20_Context3(self):
        test_opt = dsl_type20.DSLType20_Option(dsl_type20.DSLType20_Config(), "a")
        ctx_inst = dsl_type20.DSLType20_Context(None, "a", test_opt)
        self.assertTrue(isinstance(ctx_inst, dsl_type20.DSLType20_Context))
        self.assertEqual(ctx_inst.get_type(), dsl_type20.DSLTYPE20_ENTRY_TYPE_CTX)
        self.assertEqual(ctx_inst.ptr_parent, None)
        self.assertEqual(ctx_inst.get_parent_ptr(), None)
        self.assertEqual(ctx_inst.name, "a")
        self.assertEqual(ctx_inst.get_name(), "a")
        self.assertEqual(ctx_inst.options, test_opt)
        self.assertEqual(ctx_inst.get_options(), [test_opt])
        self.assertEqual(ctx_inst.entries, [])

    def testDSLType20_Context4(self):
        ctx_inst = dsl_type20.DSLType20_Context(None, "a", [])
        self.assertTrue(isinstance(ctx_inst, dsl_type20.DSLType20_Context))
        self.assertEqual(ctx_inst.get_type(), dsl_type20.DSLTYPE20_ENTRY_TYPE_CTX)
        self.assertEqual(ctx_inst.ptr_parent, None)
        self.assertEqual(ctx_inst.get_parent_ptr(), None)
        self.assertEqual(ctx_inst.name, "a")
        self.assertEqual(ctx_inst.get_name(), "a")
        self.assertEqual(ctx_inst.options, [])
        self.assertEqual(ctx_inst.get_options(), [])
        self.assertEqual(ctx_inst.entries, [])

    def testDSLType20_Context5(self):
        test_opt1 = dsl_type20.DSLType20_Option(dsl_type20.DSLType20_Config(), "a")
        test_opt2 = dsl_type20.DSLType20_Option(dsl_type20.DSLType20_Config(), "b")
        ctx_inst = dsl_type20.DSLType20_Context(None, "a", [test_opt1, test_opt2])
        self.assertTrue(isinstance(ctx_inst, dsl_type20.DSLType20_Context))
        self.assertEqual(ctx_inst.get_type(), dsl_type20.DSLTYPE20_ENTRY_TYPE_CTX)
        self.assertEqual(ctx_inst.ptr_parent, None)
        self.assertEqual(ctx_inst.get_parent_ptr(), None)
        self.assertEqual(ctx_inst.name, "a")
        self.assertEqual(ctx_inst.get_name(), "a")
        self.assertEqual(ctx_inst.options, [test_opt1, test_opt2])
        self.assertEqual(ctx_inst.get_options(), [test_opt1, test_opt2])
        self.assertEqual(ctx_inst.entries, [])

    def testDslType20_GetEntireDFS1(self):

        test_cfg = dsl_type20.DSLType20_Config()
        test_dsl = dsl_type20.DSLType20(test_cfg)

        self.assertTrue(test_dsl.add_context("ctx1", None)[0])
        self.assertTrue(test_dsl.add_context("ctx2", None)[0])
        self.assertTrue(test_dsl.add_context("ctx3", None)[0])
        self.assertTrue(test_dsl.add_context("ctx4", None, "ctx1")[0])
        self.assertTrue(test_dsl.add_context("ctx5", None, "ctx2")[0])
        self.assertTrue(test_dsl.add_context("ctx6", None, "ctx3")[0])
        self.assertTrue(test_dsl.add_context("ctx7", None, "ctx4")[0])
        self.assertTrue(test_dsl.add_context("ctx8", None, "ctx4")[0])
        self.assertTrue(test_dsl.add_context("ctx9", None, "ctx5")[0])

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "var1", None)
        test_var1.new_value()
        test_var1.add_value_immediate("val1")

        test_var2 = dsl_type20.DSLType20_Variable(test_cfg, "var2", None)
        test_var2.new_value()
        test_var2.add_value_immediate("val2")

        test_var3 = dsl_type20.DSLType20_Variable(test_cfg, "var3", None)
        test_var3.new_value()
        test_var3.add_value_immediate("val3")

        test_var4 = dsl_type20.DSLType20_Variable(test_cfg, "var4", None)
        test_var4.new_value()
        test_var4.add_value_immediate("val4")

        test_var5 = dsl_type20.DSLType20_Variable(test_cfg, "var5", None)
        test_var5.new_value()
        test_var5.add_value_immediate("val5")

        test_var6 = dsl_type20.DSLType20_Variable(test_cfg, "var6", None)
        test_var6.new_value()
        test_var6.add_value_immediate("val6")

        test_var7 = dsl_type20.DSLType20_Variable(test_cfg, "var7", None)
        test_var7.new_value()
        test_var7.add_value_immediate("val7")

        test_var8 = dsl_type20.DSLType20_Variable(test_cfg, "var8", None)
        test_var8.new_value()
        test_var8.add_value_immediate("val8")

        test_var9 = dsl_type20.DSLType20_Variable(test_cfg, "var9", None)
        test_var9.new_value()
        test_var9.add_value_immediate("val9")

        test_var10 = dsl_type20.DSLType20_Variable(test_cfg, "var10", None)
        test_var10.new_value()
        test_var10.add_value_immediate("val10")

        test_var11 = dsl_type20.DSLType20_Variable(test_cfg, "var11", None)
        test_var11.new_value()
        test_var11.add_value_immediate("val11")

        test_var12 = dsl_type20.DSLType20_Variable(test_cfg, "var12", None)
        test_var12.new_value()
        test_var12.add_value_immediate("val12")

        test_var13 = dsl_type20.DSLType20_Variable(test_cfg, "var13", None)
        test_var13.new_value()
        test_var13.add_value_immediate("val13")

        test_var14 = dsl_type20.DSLType20_Variable(test_cfg, "var14", None)
        test_var14.new_value()
        test_var14.add_value_immediate("val14")

        test_var15 = dsl_type20.DSLType20_Variable(test_cfg, "var15", None)
        test_var15.new_value()
        test_var15.add_value_immediate("val15")

        test_var16 = dsl_type20.DSLType20_Variable(test_cfg, "var16", None)
        test_var16.new_value()
        test_var16.add_value_immediate("val16")

        test_var17 = dsl_type20.DSLType20_Variable(test_cfg, "var17", None)
        test_var17.new_value()
        test_var17.add_value_immediate("val17")

        test_var18 = dsl_type20.DSLType20_Variable(test_cfg, "var18", None)
        test_var18.new_value()
        test_var18.add_value_immediate("val18")

        test_var19 = dsl_type20.DSLType20_Variable(test_cfg, "var19", None)
        test_var19.new_value()
        test_var19.add_value_immediate("val19")

        test_var20 = dsl_type20.DSLType20_Variable(test_cfg, "var20", None)
        test_var20.new_value()
        test_var20.add_value_immediate("val20")

        test_var21 = dsl_type20.DSLType20_Variable(test_cfg, "var21", None)
        test_var21.new_value()
        test_var21.add_value_immediate("val21")

        test_var22 = dsl_type20.DSLType20_Variable(test_cfg, "var22", None)
        test_var22.new_value()
        test_var22.add_value_immediate("val22")

        self.assertTrue(test_dsl.add_variable(test_var1)[0])
        self.assertTrue(test_dsl.add_variable(test_var2, "ctx1")[0])
        self.assertTrue(test_dsl.add_variable(test_var3, "ctx2")[0])
        self.assertTrue(test_dsl.add_variable(test_var4, "ctx3")[0])
        self.assertTrue(test_dsl.add_variable(test_var5, "ctx4")[0])
        self.assertTrue(test_dsl.add_variable(test_var6, "ctx5")[0])
        self.assertTrue(test_dsl.add_variable(test_var7, "ctx6")[0])
        self.assertTrue(test_dsl.add_variable(test_var8, "ctx7")[0])
        self.assertTrue(test_dsl.add_variable(test_var9, "ctx8")[0])
        self.assertTrue(test_dsl.add_variable(test_var10, "ctx9")[0])

        self.assertTrue(test_dsl.add_variable(test_var11)[0])
        self.assertTrue(test_dsl.add_variable(test_var12, "ctx1")[0])
        self.assertTrue(test_dsl.add_variable(test_var13, "ctx2")[0])
        self.assertTrue(test_dsl.add_variable(test_var14, "ctx3")[0])
        self.assertTrue(test_dsl.add_variable(test_var15)[0])
        self.assertTrue(test_dsl.add_variable(test_var16, "ctx4")[0])
        self.assertTrue(test_dsl.add_variable(test_var17, "ctx5")[0])
        self.assertTrue(test_dsl.add_variable(test_var18, "ctx6")[0])
        self.assertTrue(test_dsl.add_variable(test_var19)[0])
        self.assertTrue(test_dsl.add_variable(test_var20, "ctx7")[0])
        self.assertTrue(test_dsl.add_variable(test_var21, "ctx8")[0])
        self.assertTrue(test_dsl.add_variable(test_var22, "ctx9")[0])

        v, r = test_dsl.get_entire_dfs()
        self.assertTrue(v)
        self.assertEqual([x.get_name() for x in r], [test_dsl.root_context_id, "ctx1", "ctx4", "ctx7", "var8", "var20", "ctx8", "var9", "var21", "var5", "var16", "var2", "var12", "ctx2", "ctx5", "ctx9", "var10", "var22", "var6", "var17", "var3", "var13", "ctx3", "ctx6", "var7", "var18", "var4", "var14", "var1", "var11", "var15", "var19"])

    def testDslType20_Parse1(self):
        self.assertFalse(self.parse_test_aux(self.cfg_test_fail_1, dsl_type20.DSLType20_Config()))

    def testDslType20_Parse2(self):
        self.assertFalse(self.parse_test_aux(self.cfg_test_fail_2, dsl_type20.DSLType20_Config()))

    def testDslType20_Parse3(self):
        self.assertFalse(self.parse_test_aux(self.cfg_test_fail_3, dsl_type20.DSLType20_Config()))

    def testDslType20_Parse4(self):
        self.assertFalse(self.parse_test_aux(self.cfg_test_fail_4, dsl_type20.DSLType20_Config()))

    def testDslType20_Parse5(self):
        self.assertTrue(self.parse_test_aux(self.cfg_test_ok_1, dsl_type20.DSLType20_Config()))

    def testDslType20_Parse6(self):
        self.assertTrue(self.parse_test_aux(self.cfg_test_ok_2, dsl_type20.DSLType20_Config()))

    def testDslType20_Parse7(self):
        self.assertTrue(self.parse_test_aux(self.cfg_test_ok_3, dsl_type20.DSLType20_Config()))

    def testDslType20_Parse8(self):
        self.assertTrue(self.parse_test_aux(self.cfg_test_ok_4, dsl_type20.DSLType20_Config()))

    def testDslType20_Parse9(self):
        self.assertTrue(self.parse_test_aux(self.cfg_test_ok_5, dsl_type20.DSLType20_Config()))

    def testDslType20_Parse10(self):
        self.assertTrue(self.parse_test_aux(self.cfg_test_ok_6, dsl_type20.DSLType20_Config()))

    def testDslType20_Parse11(self):
        self.assertTrue(self.parse_test_aux(self.cfg_test_ok_7, dsl_type20.DSLType20_Config()))

    def testDslType20_Parse12(self):
        self.assertTrue(self.parse_test_aux(self.cfg_test_ok_8, dsl_type20.DSLType20_Config()))

    def testDslType20_Parse13(self):
        self.assertTrue(self.parse_test_aux(self.cfg_test_ok_9, dsl_type20.DSLType20_Config()))

    def testDslType20_Parse14(self):
        self.assertTrue(self.parse_test_aux(self.cfg_test_ok_10, dsl_type20.DSLType20_Config()))

    def testDslType20_Parse15(self):
        self.assertTrue(self.parse_test_aux(self.cfg_test_ok_11, dsl_type20.DSLType20_Config()))

    def testDslType20_Parse16(self):
        self.assertTrue(self.parse_test_aux(self.cfg_test_ok_12, dsl_type20.DSLType20_Config()))

    def testDslType20_Parse17(self):
        self.assertTrue(self.parse_test_aux(self.cfg_test_ok_13, dsl_type20.DSLType20_Config()))

    def testDslType20_Parse18(self):
        self.assertTrue(self.parse_test_aux(self.cfg_test_ok_14, dsl_type20.DSLType20_Config()))

    def testDslType20_Parse19(self):
        self.assertTrue(self.parse_test_aux(self.cfg_test_ok_15, dsl_type20.DSLType20_Config()))

    def testDslType20_Parse20(self):
        self.assertTrue(self.parse_test_aux(self.cfg_test_ok_16, dsl_type20.DSLType20_Config()))

    def testDslType20_Parse21(self):
        self.assertTrue(self.parse_test_aux(self.cfg_test_ok_17, dsl_type20.DSLType20_Config()))

    def testDslType20_Parse22(self):
        self.assertTrue(self.parse_test_aux(self.cfg_test_ok_18, dsl_type20.DSLType20_Config()))

    def testDslType20_Parse23(self):
        self.assertTrue(self.parse_test_aux(self.cfg_test_ok_19, dsl_type20.DSLType20_Config()))

    def testDslType20_Parse24(self):
        self.assertTrue(self.parse_test_aux(self.cfg_test_ok_20, dsl_type20.DSLType20_Config()))

    def testDslType20_Parse25(self):
        self.assertTrue(self.parse_test_aux(self.cfg_test_ok_21, dsl_type20.DSLType20_Config()))

    def testDslType20_Parse26(self):
        self.assertTrue(self.parse_test_aux(self.cfg_test_ok_22, dsl_type20.DSLType20_Config()))

    def testDslType20_Parse27(self):
        self.assertTrue(self.parse_test_aux(self.cfg_test_ok_23, dsl_type20.DSLType20_Config()))

    def testDslType20_Parse28(self):

        blanksub = path_utils.concat_path(self.test_dir, " ")
        self.assertFalse(os.path.exists(blanksub))
        os.mkdir(blanksub)
        self.assertTrue(os.path.exists(blanksub))

        blankfile = path_utils.concat_path(blanksub, " ")
        self.assertFalse(os.path.exists(blankfile))
        create_and_write_file.create_file_contents(blankfile, self.contents_cfg_test_ok_1)
        self.assertTrue(os.path.exists(blankfile))

        self.assertTrue(self.parse_test_aux(blankfile, dsl_type20.DSLType20_Config()))

    def testDslType20_GetAllVariablesDFS1(self):

        test_cfg = dsl_type20.DSLType20_Config()
        test_dsl = dsl_type20.DSLType20(test_cfg)

        self.assertTrue(test_dsl.add_context("ctx1", None)[0])
        self.assertTrue(test_dsl.add_context("ctx2", None)[0])
        self.assertTrue(test_dsl.add_context("ctx3", None)[0])
        self.assertTrue(test_dsl.add_context("ctx4", None, "ctx1")[0])
        self.assertTrue(test_dsl.add_context("ctx5", None, "ctx2")[0])
        self.assertTrue(test_dsl.add_context("ctx6", None, "ctx3")[0])
        self.assertTrue(test_dsl.add_context("ctx7", None, "ctx4")[0])
        self.assertTrue(test_dsl.add_context("ctx8", None, "ctx4")[0])
        self.assertTrue(test_dsl.add_context("ctx9", None, "ctx5")[0])

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "var1", None)
        test_var1.new_value()
        test_var1.add_value_immediate("val1")

        test_var2 = dsl_type20.DSLType20_Variable(test_cfg, "var2", None)
        test_var2.new_value()
        test_var2.add_value_immediate("val2")

        test_var3 = dsl_type20.DSLType20_Variable(test_cfg, "var3", None)
        test_var3.new_value()
        test_var3.add_value_immediate("val3")

        test_var4 = dsl_type20.DSLType20_Variable(test_cfg, "var4", None)
        test_var4.new_value()
        test_var4.add_value_immediate("val4")

        test_var5 = dsl_type20.DSLType20_Variable(test_cfg, "var5", None)
        test_var5.new_value()
        test_var5.add_value_immediate("val5")

        test_var6 = dsl_type20.DSLType20_Variable(test_cfg, "var6", None)
        test_var6.new_value()
        test_var6.add_value_immediate("val6")

        test_var7 = dsl_type20.DSLType20_Variable(test_cfg, "var7", None)
        test_var7.new_value()
        test_var7.add_value_immediate("val7")

        test_var8 = dsl_type20.DSLType20_Variable(test_cfg, "var8", None)
        test_var8.new_value()
        test_var8.add_value_immediate("val8")

        test_var9 = dsl_type20.DSLType20_Variable(test_cfg, "var9", None)
        test_var9.new_value()
        test_var9.add_value_immediate("val9")

        test_var10 = dsl_type20.DSLType20_Variable(test_cfg, "var10", None)
        test_var10.new_value()
        test_var10.add_value_immediate("val10")

        test_var11 = dsl_type20.DSLType20_Variable(test_cfg, "var11", None)
        test_var11.new_value()
        test_var11.add_value_immediate("val11")

        test_var12 = dsl_type20.DSLType20_Variable(test_cfg, "var12", None)
        test_var12.new_value()
        test_var12.add_value_immediate("val12")

        test_var13 = dsl_type20.DSLType20_Variable(test_cfg, "var13", None)
        test_var13.new_value()
        test_var13.add_value_immediate("val13")

        test_var14 = dsl_type20.DSLType20_Variable(test_cfg, "var14", None)
        test_var14.new_value()
        test_var14.add_value_immediate("val14")

        test_var15 = dsl_type20.DSLType20_Variable(test_cfg, "var15", None)
        test_var15.new_value()
        test_var15.add_value_immediate("val15")

        test_var16 = dsl_type20.DSLType20_Variable(test_cfg, "var16", None)
        test_var16.new_value()
        test_var16.add_value_immediate("val16")

        test_var17 = dsl_type20.DSLType20_Variable(test_cfg, "var17", None)
        test_var17.new_value()
        test_var17.add_value_immediate("val17")

        test_var18 = dsl_type20.DSLType20_Variable(test_cfg, "var18", None)
        test_var18.new_value()
        test_var18.add_value_immediate("val18")

        test_var19 = dsl_type20.DSLType20_Variable(test_cfg, "var19", None)
        test_var19.new_value()
        test_var19.add_value_immediate("val19")

        test_var20 = dsl_type20.DSLType20_Variable(test_cfg, "var20", None)
        test_var20.new_value()
        test_var20.add_value_immediate("val20")

        test_var21 = dsl_type20.DSLType20_Variable(test_cfg, "var21", None)
        test_var21.new_value()
        test_var21.add_value_immediate("val21")

        test_var22 = dsl_type20.DSLType20_Variable(test_cfg, "var22", None)
        test_var22.new_value()
        test_var22.add_value_immediate("val22")

        self.assertTrue(test_dsl.add_variable(test_var1)[0])
        self.assertTrue(test_dsl.add_variable(test_var2, "ctx1")[0])
        self.assertTrue(test_dsl.add_variable(test_var3, "ctx2")[0])
        self.assertTrue(test_dsl.add_variable(test_var4, "ctx3")[0])
        self.assertTrue(test_dsl.add_variable(test_var5, "ctx4")[0])
        self.assertTrue(test_dsl.add_variable(test_var6, "ctx5")[0])
        self.assertTrue(test_dsl.add_variable(test_var7, "ctx6")[0])
        self.assertTrue(test_dsl.add_variable(test_var8, "ctx7")[0])
        self.assertTrue(test_dsl.add_variable(test_var9, "ctx8")[0])
        self.assertTrue(test_dsl.add_variable(test_var10, "ctx9")[0])

        self.assertTrue(test_dsl.add_variable(test_var11)[0])
        self.assertTrue(test_dsl.add_variable(test_var12, "ctx1")[0])
        self.assertTrue(test_dsl.add_variable(test_var13, "ctx2")[0])
        self.assertTrue(test_dsl.add_variable(test_var14, "ctx3")[0])
        self.assertTrue(test_dsl.add_variable(test_var15)[0])
        self.assertTrue(test_dsl.add_variable(test_var16, "ctx4")[0])
        self.assertTrue(test_dsl.add_variable(test_var17, "ctx5")[0])
        self.assertTrue(test_dsl.add_variable(test_var18, "ctx6")[0])
        self.assertTrue(test_dsl.add_variable(test_var19)[0])
        self.assertTrue(test_dsl.add_variable(test_var20, "ctx7")[0])
        self.assertTrue(test_dsl.add_variable(test_var21, "ctx8")[0])
        self.assertTrue(test_dsl.add_variable(test_var22, "ctx9")[0])

        self.assertEqual(var_fmt_helper(test_dsl.get_all_variables_dfs()), [("var8", "val8", []), ("var20", "val20", []), ("var9", "val9", []), ("var21", "val21", []), ("var5", "val5", []), ("var16", "val16", []), ("var2", "val2", []), ("var12", "val12", []), ("var10", "val10", []), ("var22", "val22", []), ("var6", "val6", []), ("var17", "val17", []), ("var3", "val3", []), ("var13", "val13", []), ("var7", "val7", []), ("var18", "val18", []), ("var4", "val4", []), ("var14", "val14", []), ("var1", "val1", []), ("var11", "val11", []), ("var15", "val15", []), ("var19", "val19", [])])

    def testDslType20_GetAllVariablesDFS2(self):

        test_cfg = dsl_type20.DSLType20_Config(inherit_options = True)
        test_dsl = dsl_type20.DSLType20(test_cfg)

        test_opt1 = dsl_type20.DSLType20_Option(test_cfg, "opt1")
        test_opt1.new_value()
        test_opt1.add_value_immediate("optval1")

        test_opt2 = dsl_type20.DSLType20_Option(test_cfg, "opt2")
        test_opt2.new_value()
        test_opt2.add_value_immediate("optval2")

        test_opt3 = dsl_type20.DSLType20_Option(test_cfg, "opt3")
        test_opt3.new_value()
        test_opt3.add_value_immediate("optval3")

        self.assertTrue(test_dsl.add_context("ctx1", test_opt1)[0])
        self.assertTrue(test_dsl.add_context("ctx2", None)[0])
        self.assertTrue(test_dsl.add_context("ctx3", None)[0])
        self.assertTrue(test_dsl.add_context("ctx4", test_opt2, "ctx1")[0])
        self.assertTrue(test_dsl.add_context("ctx5", None, "ctx2")[0])
        self.assertTrue(test_dsl.add_context("ctx6", None, "ctx3")[0])
        self.assertTrue(test_dsl.add_context("ctx7", None, "ctx4")[0])
        self.assertTrue(test_dsl.add_context("ctx8", None, "ctx4")[0])
        self.assertTrue(test_dsl.add_context("ctx9", None, "ctx5")[0])

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "var1", None)
        test_var1.new_value()
        test_var1.add_value_immediate("val1")

        test_var2 = dsl_type20.DSLType20_Variable(test_cfg, "var2", None)
        test_var2.new_value()
        test_var2.add_value_immediate("val2")

        test_var3 = dsl_type20.DSLType20_Variable(test_cfg, "var3", None)
        test_var3.new_value()
        test_var3.add_value_immediate("val3")

        test_var4 = dsl_type20.DSLType20_Variable(test_cfg, "var4", None)
        test_var4.new_value()
        test_var4.add_value_immediate("val4")

        test_var5 = dsl_type20.DSLType20_Variable(test_cfg, "var5", test_opt3)
        test_var5.new_value()
        test_var5.add_value_immediate("val5")

        test_var6 = dsl_type20.DSLType20_Variable(test_cfg, "var6", None)
        test_var6.new_value()
        test_var6.add_value_immediate("val6")

        test_var7 = dsl_type20.DSLType20_Variable(test_cfg, "var7", None)
        test_var7.new_value()
        test_var7.add_value_immediate("val7")

        test_var8 = dsl_type20.DSLType20_Variable(test_cfg, "var8", None)
        test_var8.new_value()
        test_var8.add_value_immediate("val8")

        test_var9 = dsl_type20.DSLType20_Variable(test_cfg, "var9", None)
        test_var9.new_value()
        test_var9.add_value_immediate("val9")

        test_var10 = dsl_type20.DSLType20_Variable(test_cfg, "var10", None)
        test_var10.new_value()
        test_var10.add_value_immediate("val10")

        test_var11 = dsl_type20.DSLType20_Variable(test_cfg, "var11", None)
        test_var11.new_value()
        test_var11.add_value_immediate("val11")

        test_var12 = dsl_type20.DSLType20_Variable(test_cfg, "var12", None)
        test_var12.new_value()
        test_var12.add_value_immediate("val12")

        test_var13 = dsl_type20.DSLType20_Variable(test_cfg, "var13", None)
        test_var13.new_value()
        test_var13.add_value_immediate("val13")

        test_var14 = dsl_type20.DSLType20_Variable(test_cfg, "var14", None)
        test_var14.new_value()
        test_var14.add_value_immediate("val14")

        test_var15 = dsl_type20.DSLType20_Variable(test_cfg, "var15", None)
        test_var15.new_value()
        test_var15.add_value_immediate("val15")

        test_var16 = dsl_type20.DSLType20_Variable(test_cfg, "var16", None)
        test_var16.new_value()
        test_var16.add_value_immediate("val16")

        test_var17 = dsl_type20.DSLType20_Variable(test_cfg, "var17", None)
        test_var17.new_value()
        test_var17.add_value_immediate("val17")

        test_var18 = dsl_type20.DSLType20_Variable(test_cfg, "var18", None)
        test_var18.new_value()
        test_var18.add_value_immediate("val18")

        test_var19 = dsl_type20.DSLType20_Variable(test_cfg, "var19", None)
        test_var19.new_value()
        test_var19.add_value_immediate("val19")

        test_var20 = dsl_type20.DSLType20_Variable(test_cfg, "var20", None)
        test_var20.new_value()
        test_var20.add_value_immediate("val20")

        test_var21 = dsl_type20.DSLType20_Variable(test_cfg, "var21", None)
        test_var21.new_value()
        test_var21.add_value_immediate("val21")

        test_var22 = dsl_type20.DSLType20_Variable(test_cfg, "var22", None)
        test_var22.new_value()
        test_var22.add_value_immediate("val22")

        self.assertTrue(test_dsl.add_variable(test_var1)[0])
        self.assertTrue(test_dsl.add_variable(test_var2, "ctx1")[0])
        self.assertTrue(test_dsl.add_variable(test_var3, "ctx2")[0])
        self.assertTrue(test_dsl.add_variable(test_var4, "ctx3")[0])
        self.assertTrue(test_dsl.add_variable(test_var5, "ctx4")[0])
        self.assertTrue(test_dsl.add_variable(test_var6, "ctx5")[0])
        self.assertTrue(test_dsl.add_variable(test_var7, "ctx6")[0])
        self.assertTrue(test_dsl.add_variable(test_var8, "ctx7")[0])
        self.assertTrue(test_dsl.add_variable(test_var9, "ctx8")[0])
        self.assertTrue(test_dsl.add_variable(test_var10, "ctx9")[0])

        self.assertTrue(test_dsl.add_variable(test_var11)[0])
        self.assertTrue(test_dsl.add_variable(test_var12, "ctx1")[0])
        self.assertTrue(test_dsl.add_variable(test_var13, "ctx2")[0])
        self.assertTrue(test_dsl.add_variable(test_var14, "ctx3")[0])
        self.assertTrue(test_dsl.add_variable(test_var15)[0])
        self.assertTrue(test_dsl.add_variable(test_var16, "ctx4")[0])
        self.assertTrue(test_dsl.add_variable(test_var17, "ctx5")[0])
        self.assertTrue(test_dsl.add_variable(test_var18, "ctx6")[0])
        self.assertTrue(test_dsl.add_variable(test_var19)[0])
        self.assertTrue(test_dsl.add_variable(test_var20, "ctx7")[0])
        self.assertTrue(test_dsl.add_variable(test_var21, "ctx8")[0])
        self.assertTrue(test_dsl.add_variable(test_var22, "ctx9")[0])

        self.assertEqual(var_fmt_helper(test_dsl.get_all_variables_dfs()), [("var8", "val8", [("opt1", "optval1"), ("opt2", "optval2")]), ("var20", "val20", [("opt1", "optval1"), ("opt2", "optval2")]), ("var9", "val9", [("opt1", "optval1"), ("opt2", "optval2")]), ("var21", "val21", [("opt1", "optval1"), ("opt2", "optval2")]), ("var5", "val5", [("opt1", "optval1"), ("opt2", "optval2"), ("opt3", "optval3")]), ("var16", "val16", [("opt1", "optval1"), ("opt2", "optval2")]), ("var2", "val2", [("opt1", "optval1")]), ("var12", "val12", [("opt1", "optval1")]), ("var10", "val10", []), ("var22", "val22", []), ("var6", "val6", []), ("var17", "val17", []), ("var3", "val3", []), ("var13", "val13", []), ("var7", "val7", []), ("var18", "val18", []), ("var4", "val4", []), ("var14", "val14", []), ("var1", "val1", []), ("var11", "val11", []), ("var15", "val15", []), ("var19", "val19", [])])

    def testDslType20_GetVariables1(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse(self.contents_cfg_test_ok_1)
        self.assertTrue(v)

        self.assertEqual(var_fmt_helper(dsl.get_variables("var0")), [])
        self.assertEqual(var_fmt_helper(dsl.get_variables("var1")), [("var1", "val1", [])])
        self.assertEqual(var_fmt_helper(dsl.get_variables("var2")), [("var2", "val2", [("opt1", None)])])
        self.assertEqual(var_fmt_helper(dsl.get_variables("var3")), [("var3", "val4", [("opt2", "val3")])])
        self.assertEqual(var_fmt_helper(dsl.get_variables("var4")), [("var4", "val7", [("opt3", "val5"), ("opt4", "val6")])])
        self.assertEqual(var_fmt_helper(dsl.get_variables("var5")), [("var5", "val10", [("opt5", None), ("opt6", "val8"), ("opt7", "val9")])])
        self.assertEqual(var_fmt_helper(dsl.get_variables("var6")), [])

    def testDslType20_GetVariables2(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse(self.contents_cfg_test_ok_2)
        self.assertTrue(v)

        self.assertEqual(var_fmt_helper(dsl.get_variables("var0")), [])
        self.assertEqual(var_fmt_helper(dsl.get_variables("var1")), [("var1", "val1", [])])
        self.assertEqual(var_fmt_helper(dsl.get_variables("var2")), [("var2", "a/path/valid1", [])])
        self.assertEqual(var_fmt_helper(dsl.get_variables("var3")), [("var3", "a/path/valid3", [("opt1", None), ("opt2", "a/path/valid2")])])
        self.assertEqual(var_fmt_helper(dsl.get_variables("var4")), [("var4", "$SOME_ENV_VAR", [])])
        self.assertEqual(var_fmt_helper(dsl.get_variables("var5")), [("var5", "opts", [("r1", ""), ("r2", None)]), ("var5", "more-opts", [("r1", None), ("r2", None)])])
        self.assertEqual(var_fmt_helper(dsl.get_variables("var6")), [])

    def testDslType20_GetVariables3(self):

        test_cfg = dsl_type20.DSLType20_Config(inherit_options = True)
        test_dsl = dsl_type20.DSLType20(test_cfg)
        test_opt1 = dsl_type20.DSLType20_Option(test_cfg, "opt1")
        test_opt1.new_value()
        test_opt1.add_value_immediate("val1")
        v, r = test_dsl.add_context("ctx1", test_opt1, None)
        self.assertTrue(v)
        test_opt2 = dsl_type20.DSLType20_Option(test_cfg, "opt2")
        test_opt2.new_value()
        test_opt2.add_value_immediate("val2")
        test_var = dsl_type20.DSLType20_Variable(test_cfg, "var1", test_opt2)
        test_var.new_value()
        test_var.add_value_immediate("val2")
        v, r = test_dsl.add_variable(test_var, "ctx1")
        self.assertTrue(v)
        v, r = test_dsl.get_variables("var1", "ctx1")
        self.assertTrue(v)
        self.assertEqual(r[0].get_name(), test_dsl.data.entries[0].entries[0].get_name())
        self.assertNotEqual(r[0], test_dsl.data.entries[0].entries[0])
        self.assertNotEqual(r[0].options[1], test_dsl.data.entries[0].entries[0].options)

    def testDslType20_GetVariables4(self):

        test_cfg = dsl_type20.DSLType20_Config(inherit_options = True)
        test_dsl = dsl_type20.DSLType20(test_cfg)

        test_opt1 = dsl_type20.DSLType20_Option(test_cfg, "opt1")
        test_opt1.new_value()
        test_opt1.add_value_immediate("val1")

        test_opt2 = dsl_type20.DSLType20_Option(test_cfg, "opt2")
        test_opt2.new_value()
        test_opt2.add_value_immediate("val2")

        test_opt3 = dsl_type20.DSLType20_Option(test_cfg, "opt3")
        test_opt3.new_value()
        test_opt3.add_value_immediate("val3")

        test_opt4 = dsl_type20.DSLType20_Option(test_cfg, "opt4")
        test_opt4.new_value()
        test_opt4.add_value_immediate("val4")

        test_opt5 = dsl_type20.DSLType20_Option(test_cfg, "opt5")
        test_opt5.new_value()
        test_opt5.add_value_immediate("val5")

        test_opt6 = dsl_type20.DSLType20_Option(test_cfg, "opt6")
        test_opt6.new_value()
        test_opt6.add_value_immediate("val6")

        test_opt7 = dsl_type20.DSLType20_Option(test_cfg, "opt7")
        test_opt7.new_value()
        test_opt7.add_value_immediate("val7")

        test_opt8 = dsl_type20.DSLType20_Option(test_cfg, "opt8")
        test_opt8.new_value()
        test_opt8.add_value_immediate("val8")

        v, r = test_dsl.add_context("ctx1", test_opt1, None)
        self.assertTrue(v)
        v, r = test_dsl.add_context("ctx2", test_opt2, "ctx1")
        self.assertTrue(v)
        v, r = test_dsl.add_context("ctx3", test_opt3, "ctx2")
        self.assertTrue(v)

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "var1", test_opt4)
        test_var1.new_value()
        test_var1.add_value_immediate("val9")

        test_var2 = dsl_type20.DSLType20_Variable(test_cfg, "var2", test_opt5)
        test_var2.new_value()
        test_var2.add_value_immediate("val10")

        test_var3 = dsl_type20.DSLType20_Variable(test_cfg, "var3", test_opt6)
        test_var3.new_value()
        test_var3.add_value_immediate("val11")

        test_var4 = dsl_type20.DSLType20_Variable(test_cfg, "var1", test_opt7)
        test_var4.new_value()
        test_var4.add_value_immediate("val12")

        test_var5 = dsl_type20.DSLType20_Variable(test_cfg, "var1", test_opt8)
        test_var5.new_value()
        test_var5.add_value_immediate("val13")

        v, r = test_dsl.add_variable(test_var1, "ctx3")
        self.assertTrue(v)
        v, r = test_dsl.add_variable(test_var2, "ctx3")
        self.assertTrue(v)
        v, r = test_dsl.add_variable(test_var3, "ctx3")
        self.assertTrue(v)
        v, r = test_dsl.add_variable(test_var4, "ctx3")
        self.assertTrue(v)
        v, r = test_dsl.add_variable(test_var5, "ctx3")
        self.assertTrue(v)
        self.assertEqual(var_fmt_helper(test_dsl.get_variables("var1", "ctx3")), [("var1", "val9", [("opt1", "val1"), ("opt2", "val2"), ("opt3", "val3"), ("opt4", "val4")]), ("var1", "val12", [("opt1", "val1"), ("opt2", "val2"), ("opt3", "val3"), ("opt7", "val7")]), ("var1", "val13", [("opt1", "val1"), ("opt2", "val2"), ("opt3", "val3"), ("opt8", "val8")])])

    def testDslType20_GetVariables5(self):

        test_cfg = dsl_type20.DSLType20_Config()
        test_dsl = dsl_type20.DSLType20(test_cfg)

        test_opt1 = dsl_type20.DSLType20_Option(test_cfg, "opt1")
        test_opt1.new_value()
        test_opt1.add_value_immediate("val1")

        test_opt2 = dsl_type20.DSLType20_Option(test_cfg, "opt2")
        test_opt2.new_value()
        test_opt2.add_value_immediate("val2")

        test_opt3 = dsl_type20.DSLType20_Option(test_cfg, "opt3")
        test_opt3.new_value()
        test_opt3.add_value_immediate("val3")

        test_opt4 = dsl_type20.DSLType20_Option(test_cfg, "opt4")
        test_opt4.new_value()
        test_opt4.add_value_immediate("val4")

        test_opt5 = dsl_type20.DSLType20_Option(test_cfg, "opt5")
        test_opt5.new_value()
        test_opt5.add_value_immediate("val5")

        test_opt6 = dsl_type20.DSLType20_Option(test_cfg, "opt6")
        test_opt6.new_value()
        test_opt6.add_value_immediate("val6")

        test_opt7 = dsl_type20.DSLType20_Option(test_cfg, "opt7")
        test_opt7.new_value()
        test_opt7.add_value_immediate("val7")

        test_opt8 = dsl_type20.DSLType20_Option(test_cfg, "opt8")
        test_opt8.new_value()
        test_opt8.add_value_immediate("val8")

        v, r = test_dsl.add_context("ctx1", test_opt1, None)
        self.assertTrue(v)
        v, r = test_dsl.add_context("ctx2", test_opt2, "ctx1")
        self.assertTrue(v)
        v, r = test_dsl.add_context("ctx3", test_opt3, "ctx2")
        self.assertTrue(v)

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "var1", test_opt4)
        test_var1.new_value()
        test_var1.add_value_immediate("val9")

        test_var2 = dsl_type20.DSLType20_Variable(test_cfg, "var2", test_opt5)
        test_var2.new_value()
        test_var2.add_value_immediate("val10")

        test_var3 = dsl_type20.DSLType20_Variable(test_cfg, "var3", test_opt6)
        test_var3.new_value()
        test_var3.add_value_immediate("val11")

        test_var4 = dsl_type20.DSLType20_Variable(test_cfg, "var1", test_opt7)
        test_var4.new_value()
        test_var4.add_value_immediate("val12")

        test_var5 = dsl_type20.DSLType20_Variable(test_cfg, "var1", test_opt8)
        test_var5.new_value()
        test_var5.add_value_immediate("val13")

        v, r = test_dsl.add_variable(test_var1, "ctx3")
        self.assertTrue(v)
        v, r = test_dsl.add_variable(test_var2, "ctx3")
        self.assertTrue(v)
        v, r = test_dsl.add_variable(test_var3, "ctx3")
        self.assertTrue(v)
        v, r = test_dsl.add_variable(test_var4, "ctx3")
        self.assertTrue(v)
        v, r = test_dsl.add_variable(test_var5, "ctx3")
        self.assertTrue(v)

        self.assertEqual(var_fmt_helper(test_dsl.get_variables("var1", "ctx3")), [("var1", "val9", [("opt4", "val4")]), ("var1", "val12", [("opt7", "val7")]), ("var1", "val13", [("opt8", "val8")])])

    def testDslType20_GetAllVariables1(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse(self.contents_cfg_test_ok_3)
        self.assertTrue(v)

        self.assertEqual(var_fmt_helper(dsl.get_all_variables()), [("var1", "val1", []), ("var2", "val2", [])])

    def testDslType20_GetAllVariables2(self):

        # mvtodo

        os.environ[ (self.reserved_test_env_var_1[1:]) ] = "test-value-1"
        os.environ[ (self.reserved_test_env_var_2[1:]) ] = "test-value-2"

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(True, True))
        v, r = dsl.parse(self.contents_cfg_test_ok_4)

        self.assertTrue(v)
        self.assertEqual(var_fmt_helper(dsl.get_all_variables()), [("var1", "test-value-1", []), ("var2", "val1", [("opt1","test-value-2")]), ("var3", path_utils.concat_path(os.path.expanduser("/tmp/folder")), [])])

    def testDslType20_GetAllVariables3(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options = True))
        v, r = dsl.parse(self.contents_cfg_test_ok_23)

        self.assertTrue(v)
        self.assertEqual(var_fmt_helper(dsl.get_all_variables("ctx1")), [("var1", ["123", "357"], [("opt1", ["first", "second"])])])

    def testDslType20_GetAllVariables4(self):

        test_cfg = dsl_type20.DSLType20_Config()
        test_dsl = dsl_type20.DSLType20(test_cfg)

        test_opt1 = dsl_type20.DSLType20_Option(test_cfg, "opt1")
        test_opt1.new_value()
        test_opt1.add_value_immediate("val1")

        self.assertTrue(test_dsl.add_context("ctx1", test_opt1, None)[0])

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "var1", None)
        test_var1.new_value()
        test_var1.add_value_immediate("val2")

        self.assertTrue(test_dsl.add_variable(test_var1, "ctx1" )[0])

        self.assertEqual(var_fmt_helper(test_dsl.get_all_variables("ctx1")), [("var1", "val2", [])])

    def testDslType20_GetAllVariables5(self):

        test_cfg = dsl_type20.DSLType20_Config(inherit_options = True)
        test_dsl = dsl_type20.DSLType20(test_cfg)

        test_opt1 = dsl_type20.DSLType20_Option(test_cfg, "opt1")
        test_opt1.new_value()
        test_opt1.add_value_immediate("val1")

        self.assertTrue(test_dsl.add_context("ctx1", test_opt1, None)[0])

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "var1", None)
        test_var1.new_value()
        test_var1.add_value_immediate("val2")

        self.assertTrue(test_dsl.add_variable(test_var1, "ctx1" )[0])

        self.assertEqual(var_fmt_helper(test_dsl.get_all_variables("ctx1")), [("var1", "val2", [("opt1", "val1")])])

    def testDslType20_GetAllVariables6(self):

        test_cfg = dsl_type20.DSLType20_Config(inherit_options = True)
        test_dsl = dsl_type20.DSLType20(test_cfg)

        test_opt1 = dsl_type20.DSLType20_Option(test_cfg, "opt1")
        test_opt1.new_value()
        test_opt1.add_value_immediate("val1")

        test_opt2 = dsl_type20.DSLType20_Option(test_cfg, "opt2")
        test_opt2.new_value()
        test_opt2.add_value_immediate("val3")

        self.assertTrue(test_dsl.add_context("ctx1", test_opt1, None)[0])

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "var1", test_opt2)
        test_var1.new_value()
        test_var1.add_value_immediate("val2")

        self.assertTrue(test_dsl.add_variable(test_var1, "ctx1" )[0])

        self.assertEqual(var_fmt_helper(test_dsl.get_all_variables("ctx1")), [("var1", "val2", [("opt1", "val1"), ("opt2", "val3")])])

    def testDslType20_GetAllVariables7(self):

        test_cfg = dsl_type20.DSLType20_Config(inherit_options = True)
        test_dsl = dsl_type20.DSLType20(test_cfg)

        test_opt1 = dsl_type20.DSLType20_Option(test_cfg, "opt1")
        test_opt1.new_value()
        test_opt1.add_value_immediate("val1")

        test_opt2 = dsl_type20.DSLType20_Option(test_cfg, "opt2")
        test_opt2.new_value()
        test_opt2.add_value_immediate("val2")

        test_opt3 = dsl_type20.DSLType20_Option(test_cfg, "opt3")
        test_opt3.new_value()
        test_opt3.add_value_immediate("val3")

        self.assertTrue(test_dsl.add_context("ctx1", test_opt1, None)[0])
        self.assertTrue(test_dsl.add_context("ctx2", test_opt2, "ctx1")[0])

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "var1", test_opt3)
        test_var1.new_value()
        test_var1.add_value_immediate("val4")

        self.assertTrue(test_dsl.add_variable(test_var1, "ctx2" )[0])

        self.assertEqual(var_fmt_helper(test_dsl.get_all_variables("ctx2")), [("var1", "val4", [("opt1", "val1"), ("opt2", "val2"), ("opt3", "val3")])])

    def testDslType20_GetAllVariables8(self):

        test_cfg = dsl_type20.DSLType20_Config(inherit_options = True)
        test_dsl = dsl_type20.DSLType20(test_cfg)

        test_opt1 = dsl_type20.DSLType20_Option(test_cfg, "opt1")
        test_opt1.new_value()
        test_opt1.add_value_immediate("val1")

        test_opt2 = dsl_type20.DSLType20_Option(test_cfg, "opt2")
        test_opt2.new_value()
        test_opt2.add_value_immediate("val2")

        test_opt3 = dsl_type20.DSLType20_Option(test_cfg, "opt3")
        test_opt3.new_value()
        test_opt3.add_value_immediate("val3")

        test_opt4 = dsl_type20.DSLType20_Option(test_cfg, "opt4")
        test_opt4.new_value()
        test_opt4.add_value_immediate("val4")

        test_opt5 = dsl_type20.DSLType20_Option(test_cfg, "opt5")
        test_opt5.new_value()
        test_opt5.add_value_immediate("val5")

        self.assertTrue(test_dsl.add_context("ctx1", test_opt1, None)[0])
        self.assertTrue(test_dsl.add_context("ctx2", test_opt2, "ctx1")[0])
        self.assertTrue(test_dsl.add_context("ctx3", test_opt3, "ctx2")[0])
        self.assertTrue(test_dsl.add_context("ctx4", test_opt4, "ctx3")[0])

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "var1", test_opt5)
        test_var1.new_value()
        test_var1.add_value_immediate("val6")

        self.assertTrue(test_dsl.add_variable(test_var1, "ctx4" )[0])

        self.assertEqual(var_fmt_helper(test_dsl.get_all_variables("ctx4")), [("var1", "val6", [("opt1", "val1"), ("opt2", "val2"), ("opt3", "val3"), ("opt4", "val4"), ("opt5", "val5")])])

    def testDslType20_GetAllVariables9(self):

        test_cfg = dsl_type20.DSLType20_Config(inherit_options = True)
        test_dsl = dsl_type20.DSLType20(test_cfg)

        test_opt1 = dsl_type20.DSLType20_Option(test_cfg, "opt1")
        test_opt1.new_value()
        test_opt1.add_value_immediate("val1")

        test_opt2 = dsl_type20.DSLType20_Option(test_cfg, "opt2")
        test_opt2.new_value()
        test_opt2.add_value_immediate("val2")

        test_opt3 = dsl_type20.DSLType20_Option(test_cfg, "opt3")
        test_opt3.new_value()
        test_opt3.add_value_immediate("val3")

        test_opt4 = dsl_type20.DSLType20_Option(test_cfg, "opt4")
        test_opt4.new_value()
        test_opt4.add_value_immediate("val4")

        test_opt5 = dsl_type20.DSLType20_Option(test_cfg, "opt1")
        test_opt5.new_value()
        test_opt5.add_value_immediate("val5")

        self.assertTrue(test_dsl.add_context("ctx1", test_opt1, None)[0])
        self.assertTrue(test_dsl.add_context("ctx2", test_opt2, "ctx1")[0])
        self.assertTrue(test_dsl.add_context("ctx3", test_opt3, "ctx2")[0])
        self.assertTrue(test_dsl.add_context("ctx4", test_opt4, "ctx3")[0])

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "var1", test_opt5)
        test_var1.new_value()
        test_var1.add_value_immediate("val6")

        self.assertTrue(test_dsl.add_variable(test_var1, "ctx4" )[0])

        self.assertEqual(var_fmt_helper(test_dsl.get_all_variables("ctx4")), [("var1", "val6", [("opt2", "val2"), ("opt3", "val3"), ("opt4", "val4"), ("opt1", "val5")])])

    def testDslType20_GetAllVariables10(self):

        test_cfg = dsl_type20.DSLType20_Config(inherit_options = True)
        test_dsl = dsl_type20.DSLType20(test_cfg)

        test_opt1 = dsl_type20.DSLType20_Option(test_cfg, "opt1")

        test_opt2 = dsl_type20.DSLType20_Option(test_cfg, "opt2")
        test_opt2.new_value()
        test_opt2.add_value_immediate("val2")

        test_opt3 = dsl_type20.DSLType20_Option(test_cfg, "opt1")

        test_opt4 = dsl_type20.DSLType20_Option(test_cfg, "opt4")
        test_opt4.new_value()
        test_opt4.add_value_immediate("val4")

        test_opt5 = dsl_type20.DSLType20_Option(test_cfg, "opt4")

        self.assertTrue(test_dsl.add_context("ctx1", test_opt1, None)[0])
        self.assertTrue(test_dsl.add_context("ctx2", test_opt2, "ctx1")[0])
        self.assertTrue(test_dsl.add_context("ctx3", test_opt3, "ctx2")[0])
        self.assertTrue(test_dsl.add_context("ctx4", test_opt4, "ctx3")[0])

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "var1", test_opt5)
        test_var1.new_value()
        test_var1.add_value_immediate("val6")

        self.assertTrue(test_dsl.add_variable(test_var1, "ctx4" )[0])

        self.assertEqual(var_fmt_helper(test_dsl.get_all_variables("ctx4")), [("var1", "val6", [("opt2", "val2"), ("opt4", None)])])

    def testDslType20_GetAllVariables11(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options = True))
        v, r = dsl.parse(self.contents_cfg_test_ok_22)
        self.assertTrue(v)

        self.assertEqual(var_fmt_helper(dsl.get_all_variables("ctx1")), [("var1", ["123", "357"], [("opt1", ["abc", "def"]), ("opt2", ["first", "second"])])])

    def testDslType20_GetAllVariables12(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options = False))
        v, r = dsl.parse(self.contents_cfg_test_ok_22)
        self.assertTrue(v)

        self.assertEqual(var_fmt_helper(dsl.get_all_variables("ctx1")), [("var1", ["123", "357"], [("opt2", ["first", "second"])])])

    def testDslType20_TestVanilla1(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("var1 = \"val1\"")
        self.assertTrue(v)

        self.assertEqual(var_fmt_helper(dsl.get_all_variables()), [("var1", "val1", [])])

    def testDslType20_TestVanilla2(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("var1 {opt1} = \"val1\"")
        self.assertTrue(v)

        self.assertEqual(var_fmt_helper(dsl.get_all_variables()), [("var1", "val1", [("opt1", None)])])

    def testDslType20_TestVanilla3(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("var1")
        self.assertTrue(v)

        self.assertEqual(var_fmt_helper(dsl.get_all_variables()), [("var1", None, [])])

    def testDslType20_TestVanilla4(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("var1 {opt1}")
        self.assertTrue(v)

        self.assertEqual(var_fmt_helper(dsl.get_all_variables()), [("var1", None, [("opt1", None)])])

    def testDslType20_TestVanilla5(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("var1 {opt1 / opt2}")
        self.assertTrue(v)

        self.assertEqual(var_fmt_helper(dsl.get_all_variables()), [("var1", None, [("opt1", None), ("opt2", None)])])

    def testDslType20_TestVanilla6(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("var1 {opt1: \"val1\" / opt2}")
        self.assertTrue(v)

        self.assertEqual(var_fmt_helper(dsl.get_all_variables()), [("var1", None, [("opt1", "val1"), ("opt2", None)])])

    def testDslType20_TestVanilla7(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("var1 {opt1 / opt2: \"val1\"}")
        self.assertTrue(v)

        self.assertEqual(var_fmt_helper(dsl.get_all_variables()), [("var1", None, [("opt1", None), ("opt2", "val1")])])

    def testDslType20_TestVanilla8(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("[\n@ctx\nvar1\n]")
        self.assertTrue(v)

        self.assertEqual(var_fmt_helper(dsl.get_all_variables("ctx")), [("var1", None, [])])

    def testDslType20_TestVanilla9(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("[\n@ctx\nvar1 {opt1}\n]")
        self.assertTrue(v)

        self.assertEqual(var_fmt_helper(dsl.get_all_variables("ctx")), [("var1", None, [("opt1", None)])])

    def testDslType20_TestVanilla10(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("[\n@ctx\nvar1 {opt1 / opt2}\n]")
        self.assertTrue(v)

        self.assertEqual(var_fmt_helper(dsl.get_all_variables("ctx")), [("var1", None, [("opt1", None), ("opt2", None)])])

    def testDslType20_TestVanilla11(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("[\n@ctx\nvar1 {opt1: \"val1\" / opt2}\n]")
        self.assertTrue(v)

        self.assertEqual(var_fmt_helper(dsl.get_all_variables("ctx")), [("var1", None, [("opt1", "val1"), ("opt2", None)])])

    def testDslType20_TestVanilla12(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("[\n@ctx\nvar1 {opt1 / opt2: \"val1\"}\n]")
        self.assertTrue(v)

        self.assertEqual(var_fmt_helper(dsl.get_all_variables("ctx")), [("var1", None, [("opt1", None), ("opt2", "val1")])])

    def testDslType20_TestVanilla13(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("[\n@ctx {opt1: \"val1\"}\nvar1 {opt1: \"val2\"}\n]")
        self.assertTrue(v)

        self.assertEqual(var_fmt_helper(dsl.get_all_variables("ctx")), [("var1", None, [("opt1", "val2")])])

    def testDslType20_TestVanilla14(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("[\n@ctx\nvar1 {opt1: \"val2\"}\n]")
        self.assertTrue(v)

        self.assertEqual(var_fmt_helper(dsl.get_all_variables("ctx")), [("var1", None, [("opt1", "val2")])])

    def testDslType20_TestVanilla15(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("[\n@ctx {opt1: \"val1\"}\nvar1 {opt1}\n]")
        self.assertTrue(v)

        self.assertEqual(var_fmt_helper(dsl.get_all_variables("ctx")), [("var1", None, [("opt1", None)])])

    def testDslType20_TestVanilla16(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options = True))
        v, r = dsl.parse("[\n@ctx {opt1}\nvar1 {opt1}\n]")
        self.assertTrue(v)

        self.assertEqual(var_fmt_helper(dsl.get_all_variables("ctx")), [("var1", None, [])])

    def testDslType20_TestVanilla17(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("var1 = \"val1\"\r\nvar2 = \"val2\"\r\nvar3 = \"val3\"")
        self.assertTrue(v)

        self.assertEqual(var_fmt_helper(dsl.get_all_variables()), [("var1", "val1", []), ("var2", "val2", []), ("var3", "val3", [])])

    def testDslType20_TestVanilla18(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("var1")
        self.assertTrue(v)

        self.assertEqual(var_fmt_helper(dsl.get_all_variables()), [("var1", None, [])])

    def testDslType20_TestVanilla19(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("var1 = ()")
        self.assertTrue(v)

        self.assertEqual(var_fmt_helper(dsl.get_all_variables()), [("var1", [], [])])

    def testDslType20_TestVanilla20(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("var1 {}")
        self.assertTrue(v)

        self.assertEqual(var_fmt_helper(dsl.get_all_variables()), [("var1", None, [])])

    def testDslType20_TestVanilla21(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("var1 {} = ()")
        self.assertTrue(v)

        self.assertEqual(var_fmt_helper(dsl.get_all_variables()), [("var1", [], [])])

    def testDslType20_TestVanilla22(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("[\n@ctx1 {}\n]")
        self.assertTrue(v)

        v, r = dsl.get_context("ctx1")
        self.assertTrue(v)

        self.assertEqual(r.name, "ctx1")
        self.assertEqual(len(r.options), 0)

    def testDslType20_TestParseDecoratedVar1(self):

        decorated_var = "* var1 {opt1} = \"val1\""

        dsl1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl1.parse(decorated_var)
        self.assertFalse(v)

        dsl2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(var_decorator = "* "))
        v, r = dsl2.parse(decorated_var)
        self.assertTrue(v)

        self.assertEqual(var_fmt_helper(dsl2.get_all_variables()), [("var1", "val1", [("opt1", None)])])

    def testDslType20_TestParseDecoratedVar2(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(var_decorator = "**"))
        v, r = dsl.parse("** var1 {opt1} = \"val1\"")
        self.assertTrue(v)

    def testDslType20_TestParseDecoratedVarFail1(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(var_decorator = "* "))
        v, r = dsl.parse("*var1 {opt1} = \"val1\"")
        self.assertFalse(v)

    def testDslType20_TestParseDecoratedVarFail2(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(var_decorator = "* "))
        v, r = dsl.parse("* ")
        self.assertFalse(v)

    def testDslType20_TestParseDecoratedVarFail3(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(var_decorator = "**"))
        v, r = dsl.parse("* var1 {opt1} = \"val1\"")
        self.assertFalse(v)

    def testDslType20_TestNonEscapedQuoteVarVal(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("var1 = \"val \"1\"\"")
        self.assertFalse(v)

    def testDslType20_TestNonEscapedQuoteVarOptVal(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("var1 {opt1: \"val \"2\"\"} = \"val \\\"1\\\"\"")
        self.assertFalse(v)

    def testDslType20_TestSlashInsideVarOptVal1(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("var1   {  _opt-1   :    \"val \\\\  =  \\\"1/2\\\"\" / opt2  :  \"val = \\\"2/4\\\"\" }     =  \"val = \\\"1\\\"\"  ")
        self.assertTrue(v)

        self.assertEqual(var_fmt_helper(dsl.get_all_variables()), [("var1", "val = \"1\"", [("_opt-1", "val \\  =  \"1/2\""), ("opt2", "val = \"2/4\"")])])

    def testDslType20_TestCommentInsideVarOptVal1(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("var1 { remote_link : \"https://www.url.net/folder/whatever\" } = \"svn.py\"")
        self.assertTrue(v)

        self.assertEqual(var_fmt_helper(dsl.get_all_variables()), [("var1", "svn.py", [("remote_link", "https://www.url.net/folder/whatever")])])

    def testDslType20_TestBlankAndNoneOption(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("var1 {opt1: \"\" / opt2} = \"val1\"")
        self.assertTrue(v)

        self.assertEqual(var_fmt_helper(dsl.get_all_variables()), [("var1", "val1", [("opt1", ""), ("opt2", None)])])

    def testDslType20_TestSpacedOptionValueless1(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("    var1   {  the_option     }     =    \"val1\"  ")
        self.assertTrue(v)

        self.assertEqual(var_fmt_helper(dsl.get_all_variables()), [("var1", "val1", [("the_option", None)])])

    def testDslType20_TestSpacedOptionValueless2(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("    var1   {  the_option1   /   the_option2    }     =    \"val1\"  ")
        self.assertTrue(v)

        self.assertEqual(var_fmt_helper(dsl.get_all_variables()), [("var1", "val1", [("the_option1", None), ("the_option2", None)])])

    def testDslType20_TestOptionsAlternated1(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("var1 {opt1 / opt2: \"val2\" / opt3 / opt4: \"val3\"} = \"val1\"")
        self.assertTrue(v)

        self.assertEqual(var_fmt_helper(dsl.get_all_variables()), [("var1", "val1", [("opt1", None), ("opt2", "val2"), ("opt3", None), ("opt4", "val3")])])

    def testDslType20_TestOptionsAlternated2(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("var1 {opt2: \"val2\" / opt1 / opt4: \"val3\" / opt3} = \"val1\"")
        self.assertTrue(v)

        self.assertEqual(var_fmt_helper(dsl.get_all_variables()), [("var1", "val1", [("opt2", "val2"), ("opt1", None), ("opt4", "val3"), ("opt3", None)])])

    def testDslType20_TestMalformedOptName(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("var1 {opt=1: \"optval\"} = \"val1\"")
        self.assertFalse(v)

    def testDslType20_TestMalformedValueQuotesEscaped1(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("var1 = \"val1\\\"")
        self.assertFalse(v)

    def testDslType20_TestMalformedValueQuotesEscaped2(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("var1 = \\\"val1\"")
        self.assertFalse(v)

    def testDslType20_TestVarValueParsing1(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("var1 = \"   val1\"")
        self.assertTrue(v)

        self.assertEqual(var_fmt_helper(dsl.get_all_variables()), [("var1", "   val1", [])])

    def testDslType20_TestVarValueParsing2(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("var1 = \"val1   \"")
        self.assertTrue(v)

        self.assertEqual(var_fmt_helper(dsl.get_all_variables()), [("var1", "val1   ", [])])

    def testDslType20_TestVarValueParsing3(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("var1 = \"val1   val2\"")
        self.assertTrue(v)

        self.assertEqual(var_fmt_helper(dsl.get_all_variables()), [("var1", "val1   val2", [])])

    def testDslType20_TestOptValueParsing1(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("var1 {opt1: \"   val2\"} = \"val1\"")
        self.assertTrue(v)

        self.assertEqual(var_fmt_helper(dsl.get_all_variables()), [("var1", "val1", [("opt1", "   val2")])])

    def testDslType20_TestOptValueParsing2(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("var1 {opt1: \"val2   \"} = \"val1\"")
        self.assertTrue(v)

        self.assertEqual(var_fmt_helper(dsl.get_all_variables()), [("var1", "val1", [("opt1", "val2   ")])])

    def testDslType20_TestOptValueParsing3(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("var1 {opt1: \"val2   val3\"} = \"val1\"")
        self.assertTrue(v)

        self.assertEqual(var_fmt_helper(dsl.get_all_variables()), [("var1", "val1", [("opt1", "val2   val3")])])

    def testDslType20_TestUnspacing(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("var1{opt1/opt2/opt3:\"val\\\"2\"}=\"val1\"")
        self.assertTrue(v)

        self.assertEqual(var_fmt_helper(dsl.get_all_variables()), [("var1", "val1", [("opt1", None), ("opt2", None), ("opt3", "val\"2")])])

    def testDslType20_TestLeftoversFail1(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("var1 abc = \"val1\"")
        self.assertFalse(v)

    def testDslType20_TestLeftoversFail2(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("var1 = abc \"val1\"")
        self.assertFalse(v)

    def testDslType20_TestLeftoversFail3(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("var1 = \"val1\" abc")
        self.assertFalse(v)

    def testDslType20_TestLeftoversFail4(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("var1 = {opt1} \"val1\"")
        self.assertFalse(v)

    def testDslType20_TestLeftoversFail5(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("var1 {opt1 opt2} = \"val1\"")
        self.assertFalse(v)

    def testDslType20_TestLeftoversFail6(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("var1 {opt1 /} = \"val1\"")
        self.assertFalse(v)

    def testDslType20_TestLeftoversFail7(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("var1 {{opt1} = \"val1\"")
        self.assertFalse(v)

    def testDslType20_TestLeftoversFail8(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("var1 {opt1}} = \"val1\"")
        self.assertFalse(v)

    def testDslType20_TestLeftoversFail9(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("var1 {opt1} abc = \"val1\"")
        self.assertFalse(v)

    def testDslType20_TestLeftoversFail10(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("var1 == \"val1\"")
        self.assertFalse(v)

    def testDslType20_TestLeftoversFail11(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("var1 {opt1} == \"val1\"")
        self.assertFalse(v)

    def testDslType20_TestLeftoversFail12(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("var1 {opt1} = \"val1\"/*")
        self.assertFalse(v)

    def testDslType20_TestExceedMaxNumberOptionsFail(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        dsl.max_number_options = 2
        v, r = dsl.parse("var1 {opt1 / opt2 / opt3} == \"val1\"")
        self.assertFalse(v)

    def testDslType20_TestNewContextVanilla1(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("var1 = \"val1\"\n[\n@ctx1\n]")
        self.assertTrue(v)
        self.assertEqual(var_fmt_helper(dsl.get_all_variables()), [("var1", "val1", [])])

    def testDslType20_TestNewContextVanilla2(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("var1 = \"val1\"\n[\n@ctx1\nvar2 = \"val2\"\n]")
        self.assertTrue(v)
        self.assertEqual(var_fmt_helper(dsl.get_all_variables()), [("var1", "val1", [])])
        self.assertEqual(var_fmt_helper(dsl.get_all_variables("ctx1")), [("var2", "val2", [])])

    def testDslType20_TestNewContextVanilla3(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("var1 = \"val1\"\n[\n@ctx1\nvar2 {opt1 / opt2} = \"val2\"\n]\nvar3 = \"val3\"\n[\n@ctx2\nvar4 = \"val4\"\n]")
        self.assertTrue(v)
        self.assertEqual(var_fmt_helper(dsl.get_all_variables()), [("var1", "val1", []), ("var3", "val3", [])])
        self.assertEqual(var_fmt_helper(dsl.get_all_variables("ctx1")), [("var2", "val2", [("opt1", None), ("opt2", None)])])
        self.assertEqual(var_fmt_helper(dsl.get_all_variables("ctx2")), [("var4", "val4", [])])

    def testDslType20_TestNewContextVanilla4(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("var1 = \"val1\"\n[\n]")
        self.assertTrue(v)
        self.assertEqual(var_fmt_helper(dsl.get_all_variables()), [("var1", "val1", [])])

    def testDslType20_TestNewContextVanilla5(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("\n[\n]\n")
        self.assertTrue(v)
        self.assertEqual(var_fmt_helper(dsl.get_all_variables()), [])

    def testDslType20_TestNewContextVanilla6(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("\n[\nvar1 = \"val1\"\n]\n")
        self.assertTrue(v)
        self.assertEqual(var_fmt_helper(dsl.get_all_variables()), [("var1", "val1", [])])

    def testDslType20_TestNewContextWithOptions1(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options = True))
        v, r = dsl.parse("[\n@ctx1 {opt1}\nvar1 = \"val1\"\n]")
        self.assertEqual(var_fmt_helper(dsl.get_variables("var1", "ctx1")), [("var1", "val1", [("opt1", None)])])
        self.assertTrue(v)

    def testDslType20_TestNewContextWithOptions2(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options = True))
        v, r = dsl.parse("[\n@ctx1 {opt2: \"val2\"}\nvar1 = \"val1\"\n]")
        self.assertTrue(v)
        self.assertEqual(var_fmt_helper(dsl.get_variables("var1", "ctx1")), [("var1", "val1", [("opt2", "val2")])])

    def testDslType20_TestNewContextWithOptions3(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options = True))
        v, r = dsl.parse("[\n@ctx1 {opt3: \"val3\"}\nvar1 {opt4: \"val4\"} = \"val1\"\n]")
        self.assertTrue(v)
        self.assertEqual(var_fmt_helper(dsl.get_variables("var1", "ctx1")), [("var1", "val1", [("opt3", "val3"), ("opt4", "val4")])])

    def testDslType20_TestNewContextWithOptions4(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options = True))
        v, r = dsl.parse("[\n@ctx1 {opt1: \"val1\"}\nvar1 {opt1: \"val3\"} = \"val2\"\n]")
        self.assertTrue(v)
        self.assertEqual(var_fmt_helper(dsl.get_variables("var1", "ctx1")), [("var1", "val2", [("opt1", "val3")])])

    def testDslType20_TestNewContextWithOptions5(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes = False))
        v, r = dsl.parse("[\n@ctx1 {opt1: \"val1\"}\nvar1 {opt1: \"val3\"} = \"val2\"\n]")
        self.assertTrue(v)
        self.assertEqual(var_fmt_helper(dsl.get_variables("var1", "ctx1")), [("var1", "val2", [("opt1", "val3")])])

    def testDslType20_TestNewContextWithOptions6(self):

        # mvtodo

        test_envvar_value = "dsltype20-test-value"
        os.environ[ (self.reserved_test_env_var_1[1:]) ] = test_envvar_value

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options = True))
        v, r = dsl.parse("[\n@ctx1 {opt1: \"%s\"}\nvar1 = \"val2\"\n]" % self.reserved_test_env_var_1)
        self.assertEqual(var_fmt_helper(dsl.get_variables("var1", "ctx1")), [("var1", "val2", [("opt1", test_envvar_value)])])
        self.assertTrue(v)

    def testDslType20_TestNewContextWithOptions7(self):

        # mvtodo

        test_envvar_value = "dsltype20-test-value"
        os.environ[ (self.reserved_test_env_var_1[1:]) ] = test_envvar_value

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options = True))
        v, r = dsl.parse("[\n@ctx1 {opt1: \"%s\"}\nvar1 = \"val2\"\n]" % self.reserved_test_env_var_1)
        self.assertEqual(var_fmt_helper(dsl.get_variables("var1", "ctx1")), [("var1", "val2", [("opt1", self.reserved_test_env_var_1)])])
        self.assertTrue(v)

    def testDslType20_TestNewContextFail1(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("var1 = \"val1\"\n@ctx1\nvar2 = \"val2\"\n]")
        self.assertFalse(v)

    def testDslType20_TestNewContextFail2(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("var1 = \"val1\"\n[\n[\n@ctx1\n]")
        self.assertFalse(v)

    def testDslType20_TestNewContextFail3(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("var1 = \"val1\"\n[\n")
        self.assertFalse(v)

    def testDslType20_TestNewContextFail4(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("var1 = \"val1\"\n[\n@@ctx1\n]")
        self.assertFalse(v)

    def testDslType20_TestNewContextFail5(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("var1 = \"val1\"\n[\n@ctx 1\n]")
        self.assertFalse(v)

    def testDslType20_TestNewContextFail6(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("[\n@ctx1\nvar1 = \"val1\"\n")
        self.assertFalse(v)

    def testDslType20_TestContextFail1(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl._parse_variable("var1 = \"val1\"", "nonexistent context")
        self.assertFalse(v)

    def testDslType20_TestContextReopenFail(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("[\n@ctx1\nvar1 = \"val1\"\n]\nvar2 = \"val2\"\n[\n@ctx1\nvar3 = \"val3\"\n]")
        self.assertFalse(v)

    def testDslType20_TestContextGetAllVariablesFail1(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("[\n@ctx1\nvar1 = \"val1\"\n]")
        self.assertTrue(v)
        self.assertEqual(var_fmt_helper(dsl.get_all_variables("ctx1")), [("var1", "val1", [])])
        self.assertFalse(dsl.get_all_variables("nonexistent context")[0])

    def testDslType20_TestContextGetVariablesFail1(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("[\n@ctx1\nvar1 = \"val1\"\n]")

        self.assertTrue(v)
        self.assertEqual(var_fmt_helper(dsl.get_variables("var1", None)), [])
        self.assertEqual(var_fmt_helper(dsl.get_variables("var1", "ctx1")), [("var1", "val1", [])])
        self.assertFalse(dsl.get_variables("var1", "nonexistent context")[0])

    def testDslType20_TestParsingFail1(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("[\n@ctx1\nvar1 = \"val1\"\n]\n]")

        self.assertFalse(v)

    def testDslType20_TestParsingFail2(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("\n@ctx1\nvar1 = \"val1\"")

        self.assertFalse(v)

    def testDslType20_TestParsingFail3(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("\n[\nvar1 = \"val1\"\n@ctx1\n]")

        self.assertFalse(v)

    def testDslType20_TestParsingFail4(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("\n[\n@ctx1\n@ctx2\nvar1 = \"val1\"\n]")

        self.assertFalse(v)

    def testDslType20_TestParsingFail5(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("\n[\n@ctx1\n@ctx1\nvar1 = \"val1\"\n]")

        self.assertFalse(v)

    def testDslType20_TestAddContext1(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.add_context("ok", None, None)
        self.assertTrue(v)

    def testDslType20_TestAddContext2(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.add_context("ok1", None, None)
        self.assertTrue(v)

    def testDslType20_TestAddContext3(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.add_context("_ok-90", None, None)
        self.assertTrue(v)

    def testDslType20_TestAddContext4(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.add_context("ok", [("var1", "val1")], None)
        self.assertTrue(v)

    def testDslType20_TestAddContext5(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.add_context("n ok", None, None)
        self.assertFalse(v)

    def testDslType20_TestAddContext6(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.add_context("ctx1", None, None)
        self.assertTrue(v)
        v, r = dsl.add_context("ctx2", None, "ctx1")
        self.assertTrue(v)
        v, r = dsl.add_context("ctx3", None, "ctx1")
        self.assertTrue(v)
        v, r = dsl.get_all_sub_contexts(None)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0].get_name(), "ctx1")
        v, r = dsl.get_all_sub_contexts("ctx1")
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertEqual(r[0].get_name(), "ctx2")
        self.assertEqual(r[1].get_name(), "ctx3")

    def testDslType20_TestAddContext7(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.add_context("ctx1", [("a", "b")], None)
        self.assertTrue(v)
        v, r = dsl.add_context("ctx2", [("1", "2")], "ctx1")
        self.assertTrue(v)
        self.assertEqual(opt_fmt_helper(dsl.get_context_options("ctx1")), [ ("a", "b") ])
        self.assertEqual(opt_fmt_helper(dsl.get_context_options("ctx2")), [ ("1", "2") ])

    def testDslType20_TestAddContext8(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.add_context("ctx1", [("opt1", "val1")], None)
        self.assertTrue(v)
        v, r = dsl.add_context("ctx2", [("opt1", "val2")], "ctx1")
        self.assertTrue(v)
        self.assertEqual(opt_fmt_helper(dsl.get_context_options("ctx1")), [ ("opt1", "val1") ])
        self.assertEqual(opt_fmt_helper(dsl.get_context_options("ctx2")), [ ("opt1", "val2") ])

    def testDslType20_TestAddContext9(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.add_context("ctx1", [("opt1", "val1"), ("opt2", "val2")], None)
        self.assertTrue(v)
        v, r = dsl.add_context("ctx2", [("opt3", "val3"), ("opt4", "val4")], "ctx1")
        self.assertTrue(v)
        self.assertEqual(opt_fmt_helper(dsl.get_context_options("ctx1")), [ ("opt1", "val1"), ("opt2", "val2") ])
        self.assertEqual(opt_fmt_helper(dsl.get_context_options("ctx2")), [ ("opt3", "val3"), ("opt4", "val4") ])

    def testDslType20_TestAddContext10(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.add_context("ctx1", [("opt1", "val1"), ("opt2", "val2")], None)
        self.assertTrue(v)
        v, r = dsl.add_context("ctx2", [("opt3", "val3"), ("opt1", "val4")], "ctx1")
        self.assertTrue(v)
        self.assertEqual(opt_fmt_helper(dsl.get_context_options("ctx1")), [ ("opt1", "val1"), ("opt2", "val2") ])
        self.assertEqual(opt_fmt_helper(dsl.get_context_options("ctx2")), [ ("opt3", "val3"), ("opt1", "val4") ])

    def testDslType20_TestAddContext11(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.add_context("ctx1", [("opt1", None), ("opt2", "val2")], None)
        self.assertTrue(v)
        v, r = dsl.add_context("ctx2", [("opt3", "val3"), ("opt1", None)], "ctx1")
        self.assertTrue(v)
        self.assertEqual(opt_fmt_helper(dsl.get_context_options("ctx1")), [ ("opt1", None), ("opt2", "val2") ])
        self.assertEqual(opt_fmt_helper(dsl.get_context_options("ctx2")), [ ("opt3", "val3"), ("opt1", None) ])

    def testDslType20_TestAddContext12(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.add_context("ctx1", [("opt1", "val1"), ("opt2", "val2")], None)
        self.assertTrue(v)
        v, r = dsl.add_context("ctx2", [("opt3", "val3"), ("opt1", None)], "ctx1")
        self.assertTrue(v)
        self.assertEqual(opt_fmt_helper(dsl.get_context_options("ctx1")), [ ("opt1", "val1"), ("opt2", "val2") ])
        self.assertEqual(opt_fmt_helper(dsl.get_context_options("ctx2")), [ ("opt3", "val3"), ("opt1", None) ])

    def testDslType20_TestAddContext13(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.add_context("ctx1", [("opt1", None), ("opt2", "val2")], None)
        self.assertTrue(v)
        v, r = dsl.add_context("ctx2", [("opt3", "val3"), ("opt1", "val4")], "ctx1")
        self.assertTrue(v)
        self.assertEqual(opt_fmt_helper(dsl.get_context_options("ctx1")), [ ("opt1", None), ("opt2", "val2") ])
        self.assertEqual(opt_fmt_helper(dsl.get_context_options("ctx2")), [ ("opt3", "val3"), ("opt1", "val4") ])

    def testDslType20_TestAddContext14(self):

        test_cfg = dsl_type20.DSLType20_Config()
        test_dsl = dsl_type20.DSLType20(test_cfg)

        v, r = test_dsl.add_context("ctx1", None, None)
        self.assertTrue(v)
        v, r = test_dsl.add_context("ctx2", None, "ctx1")
        self.assertTrue(v)

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "var1", None)
        test_var2 = dsl_type20.DSLType20_Variable(test_cfg, "var2", None)
        test_var3 = dsl_type20.DSLType20_Variable(test_cfg, "var3", None)
        test_var4 = dsl_type20.DSLType20_Variable(test_cfg, "var4", None)

        v, r = test_dsl.add_variable(test_var1, "ctx1")
        self.assertTrue(v)
        v, r = test_dsl.add_variable(test_var2, "ctx1")
        self.assertTrue(v)
        v, r = test_dsl.add_variable(test_var3, "ctx2")
        self.assertTrue(v)
        v, r = test_dsl.add_variable(test_var4, "ctx2")
        self.assertTrue(v)

        v, r = test_dsl.get_all_variables("ctx1")
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertEqual([x.get_name() for x in r], ["var1", "var2"])

        v, r = test_dsl.get_all_variables("ctx2")
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertEqual([x.get_name() for x in r], ["var3", "var4"])

    def testDslType20_TestAddContext15(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.add_context("ctx1", None, None)
        self.assertTrue(v)
        v, r = dsl.add_context("ctx1", None, "ctx1")
        self.assertFalse(v)

    def testDslType20_TestAddContext16(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options = True))
        v, r = dsl.add_context("ctx1", [("a", "b")], None)
        self.assertTrue(v)
        v, r = dsl.add_context("ctx2", [("1", "2")], "ctx1")
        self.assertTrue(v)
        self.assertEqual(opt_fmt_helper(dsl.get_context_options("ctx1")), [ ("a", "b") ])
        self.assertEqual(opt_fmt_helper(dsl.get_context_options("ctx2")), [ ("a", "b"), ("1", "2") ])

    def testDslType20_TestAddContext17(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options = True))
        v, r = dsl.add_context("ctx1", [("opt1", "val1")], None)
        self.assertTrue(v)
        v, r = dsl.add_context("ctx2", [("opt1", "val2")], "ctx1")
        self.assertTrue(v)
        self.assertEqual(opt_fmt_helper(dsl.get_context_options("ctx1")), [ ("opt1", "val1") ])
        self.assertEqual(opt_fmt_helper(dsl.get_context_options("ctx2")), [ ("opt1", "val2") ])

    def testDslType20_TestAddContext18(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options = True))
        v, r = dsl.add_context("ctx1", [("opt1", "val1"), ("opt2", "val2")], None)
        self.assertTrue(v)
        v, r = dsl.add_context("ctx2", [("opt3", "val3"), ("opt4", "val4")], "ctx1")
        self.assertTrue(v)
        self.assertEqual(opt_fmt_helper(dsl.get_context_options("ctx1")), [ ("opt1", "val1"), ("opt2", "val2") ])
        self.assertEqual(opt_fmt_helper(dsl.get_context_options("ctx2")), [ ("opt1", "val1"), ("opt2", "val2"), ("opt3", "val3"), ("opt4", "val4") ])

    def testDslType20_TestAddContext19(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options = True))
        v, r = dsl.add_context("ctx1", [("opt1", "val1"), ("opt2", "val2")], None)
        self.assertTrue(v)
        v, r = dsl.add_context("ctx2", [("opt3", "val3"), ("opt1", "val4")], "ctx1")
        self.assertTrue(v)
        self.assertEqual(opt_fmt_helper(dsl.get_context_options("ctx1")), [ ("opt1", "val1"), ("opt2", "val2") ])
        self.assertEqual(opt_fmt_helper(dsl.get_context_options("ctx2")), [ ("opt2", "val2"), ("opt3", "val3"), ("opt1", "val4") ])

    def testDslType20_TestAddContext20(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options = True))
        v, r = dsl.add_context("ctx1", [("opt1", None), ("opt2", "val2")], None)
        self.assertTrue(v)
        v, r = dsl.add_context("ctx2", [("opt3", "val3"), ("opt1", None)], "ctx1")
        self.assertTrue(v)
        self.assertEqual(opt_fmt_helper(dsl.get_context_options("ctx1")), [ ("opt1", None), ("opt2", "val2") ])
        self.assertEqual(opt_fmt_helper(dsl.get_context_options("ctx2")), [ ("opt2", "val2"), ("opt3", "val3") ])

    def testDslType20_TestAddContext21(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options = True))
        v, r = dsl.add_context("ctx1", [("opt1", "val1"), ("opt2", "val2")], None)
        self.assertTrue(v)
        v, r = dsl.add_context("ctx2", [("opt3", "val3"), ("opt1", None)], "ctx1")
        self.assertTrue(v)
        self.assertEqual(opt_fmt_helper(dsl.get_context_options("ctx1")), [ ("opt1", "val1"), ("opt2", "val2") ])
        self.assertEqual(opt_fmt_helper(dsl.get_context_options("ctx2")), [ ("opt2", "val2"), ("opt3", "val3"), ("opt1", None) ])

    def testDslType20_TestAddContext22(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options = True))
        v, r = dsl.add_context("ctx1", [("opt1", None), ("opt2", "val2")], None)
        self.assertTrue(v)
        v, r = dsl.add_context("ctx2", [("opt3", "val3"), ("opt1", "val4")], "ctx1")
        self.assertTrue(v)
        self.assertEqual(opt_fmt_helper(dsl.get_context_options("ctx1")), [ ("opt1", None), ("opt2", "val2") ])
        self.assertEqual(opt_fmt_helper(dsl.get_context_options("ctx2")), [ ("opt2", "val2"), ("opt3", "val3"), ("opt1", "val4") ])

    def testDslType20_TestAddContext23(self):

        test_cfg = dsl_type20.DSLType20_Config(inherit_options = True)
        test_dsl = dsl_type20.DSLType20(test_cfg)

        v, r = test_dsl.add_context("ctx1", None, None)
        self.assertTrue(v)
        v, r = test_dsl.add_context("ctx2", None, "ctx1")
        self.assertTrue(v)

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "var1", None)
        test_var2 = dsl_type20.DSLType20_Variable(test_cfg, "var2", None)
        test_var3 = dsl_type20.DSLType20_Variable(test_cfg, "var3", None)
        test_var4 = dsl_type20.DSLType20_Variable(test_cfg, "var4", None)

        v, r = test_dsl.add_variable(test_var1, "ctx1")
        self.assertTrue(v)
        v, r = test_dsl.add_variable(test_var2, "ctx1")
        self.assertTrue(v)
        v, r = test_dsl.add_variable(test_var3, "ctx2")
        self.assertTrue(v)
        v, r = test_dsl.add_variable(test_var4, "ctx2")
        self.assertTrue(v)

        self.assertEqual(var_fmt_helper(test_dsl.get_all_variables("ctx1")), [("var1", None, []), ("var2", None, [])])
        self.assertEqual(var_fmt_helper(test_dsl.get_all_variables("ctx2")), [("var3", None, []), ("var4", None, [])])

    def testDslType20_TestAddContext24(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options = True))
        v, r = dsl.add_context("ctx1", None, None)
        self.assertTrue(v)
        v, r = dsl.add_context("ctx1", None, "ctx1")
        self.assertFalse(v)

    def testDslType20_TestAddContext25(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.add_context("ok", None, None)
        self.assertTrue(v)

    def testDslType20_TestAddContext26(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.add_context("ctx1", None, None)
        self.assertTrue(v)
        v, r = dsl.add_context(dsl.root_context_id, [], "ctx1")
        self.assertFalse(v)

    def testDslType20_TestAddContext27(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.add_context("ctx1", [("opt1", [])], None)
        self.assertTrue(v)
        self.assertEqual(opt_fmt_helper(dsl.get_context_options("ctx1")), [("opt1", [])])

    def testDslType20_TestAddContext28(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.add_context("ctx1", [("opt1", ["abc"])], None)
        self.assertTrue(v)
        self.assertEqual(opt_fmt_helper(dsl.get_context_options("ctx1")), [("opt1", ["abc"])])

    def testDslType20_TestGetContext1(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.add_context("ctx1", None, None)
        self.assertTrue(v)
        v, r = dsl.add_context("ctx2", None, "ctx1")
        self.assertTrue(v)
        v, r = dsl.get_context(None)
        self.assertTrue(v)
        self.assertTrue(isinstance(r, dsl_type20.DSLType20_Context))
        self.assertEqual(r.get_name(), dsl.data.get_name())
        self.assertNotEqual(r, dsl.data)
        self.assertEqual(len(r.get_entries()), 1)

    def testDslType20_TestGetContext2(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.add_context("ctx1", None, None)
        self.assertTrue(v)
        v, r = dsl.add_context("ctx2", None, "ctx1")
        self.assertTrue(v)
        v, r = dsl.get_context("ctx2")
        self.assertTrue(v)
        self.assertTrue(isinstance(r, dsl_type20.DSLType20_Context))
        self.assertEqual(r.get_name(), "ctx2")
        self.assertEqual(len(r.get_entries()), 0)

    def testDslType20_TestGetContext3(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.add_context("ctx1", None, None)
        self.assertTrue(v)
        v, r = dsl.add_context("ctx2", None, "ctx1")
        self.assertTrue(v)
        v, r = dsl.get_context("ctx3")
        self.assertFalse(v)

    def testDslType20_TestGetContext4(self):

        test_cfg = dsl_type20.DSLType20_Config()
        test_dsl = dsl_type20.DSLType20(test_cfg)

        v, r = test_dsl.add_context("ctx1", None, None)
        self.assertTrue(v)

        test_opt1 = dsl_type20.DSLType20_Option(test_cfg, "opt1")

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "var1", test_opt1)
        test_var1.new_value()
        test_var1.add_value_immediate("val1")

        v, r = test_dsl.add_variable(test_var1, "ctx1")
        self.assertTrue(v)

        v, r = test_dsl.get_context("ctx1")
        self.assertTrue(v)

        self.assertNotEqual(r.entries[0], test_dsl.data.entries[0].entries[0])
        self.assertNotEqual(r.entries[0].options[0], test_dsl.data.entries[0].entries[0].options)

    def testDslType20_TestGetContext5(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.add_context("ctx1", None, None)
        self.assertTrue(v)
        v, r = dsl.add_context("ctx2", None, "ctx1")
        self.assertTrue(v)
        v, r = dsl.get_context("ctx2")
        self.assertTrue(v)
        self.assertEqual(r.get_parent_ptr(), None)

    def testDslType20_TestGetContext6(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.add_context("ctx1", None, None)
        self.assertTrue(v)
        v, r = dsl.add_context("ctx2", None, "ctx1")
        self.assertTrue(v)
        v, r = dsl.get_context("ctx1")
        self.assertTrue(v)
        self.assertEqual(r.get_entries()[0].get_name(), "ctx2")
        self.assertNotEqual(r.get_entries()[0].get_parent_ptr(), None)
        self.assertEqual(r.get_entries()[0].get_parent_ptr().get_name(), "ctx1")

    def testDslType20_TestGetContext7(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.add_context("ctx1", None, None)
        self.assertTrue(v)
        v, r = dsl.add_context("ctx2", [("opt1", None)], "ctx1")
        self.assertTrue(v)
        v, r = dsl.get_context("ctx1")
        self.assertTrue(v)
        self.assertEqual(r.entries[0].get_name(), dsl.data.entries[0].entries[0].get_name())
        self.assertNotEqual(r.entries[0], dsl.data.entries[0].entries[0])
        self.assertNotEqual(r.entries[0].options[0], dsl.data.entries[0].entries[0].options[0])

    def testDslType20_TestGetContext8(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options = True))
        v, r = dsl.add_context("ctx1", [("opt1", None)], None)
        self.assertTrue(v)
        v, r = dsl.add_context("ctx2", [("opt2", None)], "ctx1")
        self.assertTrue(v)
        v, r = dsl.get_context("ctx2")
        self.assertTrue(v)
        self.assertEqual(r.options[1].get_name(), dsl.data.entries[0].entries[0].options[0].get_name())
        self.assertNotEqual(r.options[1], dsl.data.entries[0].entries[0].options[0])

    def testDslType20_TestGetContext9(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options = True))
        v, r = dsl.add_context("ctx1", [("opt1", "val1")], None)
        self.assertTrue(v)
        v, r = dsl.add_context("ctx2", [("opt2", "val2")], "ctx1")
        self.assertTrue(v)
        v, r = dsl.get_context("ctx2")
        self.assertTrue(v)
        self.assertEqual(dsl_type20.convert_opt_obj_list_to_neutral_format(r.get_options()), [("opt1", "val1"), ("opt2", "val2")])

    def testDslType20_TestGetContext10(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options = True))
        v, r = dsl.add_context("ctx1", [("opt1", "val1")], None)
        self.assertTrue(v)
        v, r = dsl.add_context("ctx2", [("opt1", "val2")], "ctx1")
        self.assertTrue(v)
        v, r = dsl.get_context("ctx2")
        self.assertTrue(v)
        self.assertEqual(dsl_type20.convert_opt_obj_list_to_neutral_format(r.get_options()), [("opt1", "val2")])

    def testDslType20_TestGetContext11(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options = True))
        v, r = dsl.add_context("ctx1", [("opt1", None)], None)
        self.assertTrue(v)
        v, r = dsl.add_context("ctx2", [("opt1", None)], "ctx1")
        self.assertTrue(v)
        v, r = dsl.get_context("ctx2")
        self.assertTrue(v)
        self.assertEqual(dsl_type20.convert_opt_obj_list_to_neutral_format(r.get_options()), [])

    def testDslType20_TestGetContext12(self):

        test_cfg = dsl_type20.DSLType20_Config()
        test_dsl = dsl_type20.DSLType20(test_cfg)

        v, r = test_dsl.add_context("ctx1", None, None)
        self.assertTrue(v)

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "var1", None)
        test_var1.new_value()
        test_var1.add_value_immediate("val1")

        test_var2 = dsl_type20.DSLType20_Variable(test_cfg, "var2", None)
        test_var2.new_value()
        test_var2.add_value_immediate("val2")

        self.assertTrue(test_dsl.add_variable(test_var1, None)[0])
        self.assertTrue(test_dsl.add_variable(test_var2, "ctx1")[0])

        v, r = test_dsl.get_context(None)
        self.assertTrue(v)
        self.assertEqual(len(r.get_entries()), 2)
        self.assertEqual(r.get_entries()[0].get_name(), "ctx1")
        self.assertEqual(len(r.get_entries()[0].get_entries()), 0)

    def testDslType20_TestGetContext13(self):

        test_cfg = dsl_type20.DSLType20_Config()
        test_dsl = dsl_type20.DSLType20(test_cfg)

        v, r = test_dsl.add_context("ctx1", None, None)
        self.assertTrue(v)
        v, r = test_dsl.add_context("ctx2", None, "ctx1")
        self.assertTrue(v)
        v, r = test_dsl.add_context("ctx3", None, "ctx2")
        self.assertTrue(v)

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "var1", None)
        test_var1.new_value()
        test_var1.add_value_immediate("val1")

        test_var2 = dsl_type20.DSLType20_Variable(test_cfg, "var2", None)
        test_var2.new_value()
        test_var2.add_value_immediate("val2")

        self.assertTrue(test_dsl.add_variable(test_var1, "ctx1")[0])
        self.assertTrue(test_dsl.add_variable(test_var2, "ctx2")[0])

        v, r = test_dsl.get_context("ctx1")
        self.assertTrue(v)
        self.assertEqual(len(r.get_entries()), 2)
        self.assertEqual(r.get_entries()[0].get_name(), "ctx2")
        self.assertEqual(len(r.get_entries()[0].get_entries()), 0)

    def testDslType20_TestGetContext14(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options = True))
        v, r = dsl.add_context("ctx1", [("opt1", None)], None)
        self.assertTrue(v)
        v, r = dsl.add_context("ctx2", [("opt2", None)], "ctx1")
        self.assertTrue(v)
        v, r = dsl.add_context("ctx3", [("opt3", None)], "ctx2")
        self.assertTrue(v)
        v, r = dsl.get_context("ctx2")
        self.assertTrue(v)
        self.assertEqual(r.get_entries()[0].get_name(), "ctx3")
        self.assertEqual(dsl_type20.convert_opt_obj_list_to_neutral_format(r.get_entries()[0].get_options()), [("opt1", None), ("opt2", None), ("opt3", None)])
        self.assertEqual(r.get_entries()[0].get_parent_ptr().get_name(), "ctx2")
        self.assertEqual(dsl.data.entries[0].entries[0].get_name(), "ctx2")
        self.assertNotEqual(dsl.data.entries[0].entries[0], r.get_entries()[0].get_parent_ptr())
        self.assertEqual(r.get_entries()[0].get_parent_ptr().get_parent_ptr(), None)

    def testDslType20_TestGetContext15(self):

        test_cfg = dsl_type20.DSLType20_Config(inherit_options = True)
        test_dsl = dsl_type20.DSLType20(test_cfg)

        test_opt1 = dsl_type20.DSLType20_Option(test_cfg, "opt1")
        test_opt2 = dsl_type20.DSLType20_Option(test_cfg, "opt2")
        test_opt3 = dsl_type20.DSLType20_Option(test_cfg, "opt3")
        test_opt4 = dsl_type20.DSLType20_Option(test_cfg, "opt4")

        v, r = test_dsl.add_context("ctx1", test_opt1, None)
        self.assertTrue(v)
        v, r = test_dsl.add_context("ctx2", test_opt2, "ctx1")
        self.assertTrue(v)
        v, r = test_dsl.add_context("ctx3", test_opt3, "ctx2")
        self.assertTrue(v)

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "var1", test_opt4)
        test_var1.new_value()
        test_var1.add_value_immediate("val1")

        v, r = test_dsl.add_variable(test_var1, "ctx3")
        self.assertTrue(v)

        v, r = test_dsl.get_context("ctx3")
        self.assertTrue(v)
        self.assertEqual(r.get_entries()[0].get_name(), "var1")
        self.assertEqual(dsl_type20.convert_opt_obj_list_to_neutral_format(r.get_entries()[0].get_options()), [("opt1", None), ("opt2", None), ("opt3", None), ("opt4", None)])

    def testDslType20_TestGetSubContext1(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.add_context("ctx1", None, None)
        self.assertTrue(v)
        v, r = dsl.add_context("ctx2", None, "ctx1")
        self.assertTrue(v)
        v, r = dsl.get_sub_context(None)
        self.assertTrue(v)
        self.assertTrue(isinstance(r, dsl_type20.DSLType20_Context))
        self.assertEqual(r.get_name(), dsl.data.get_name())
        self.assertNotEqual(r, dsl.data)
        self.assertEqual(len(r.get_entries()), 1)

    def testDslType20_TestGetSubContext2(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.add_context("ctx1", None, None)
        self.assertTrue(v)
        v, r = dsl.add_context("ctx2", None, "ctx1")
        self.assertTrue(v)
        v, r = dsl.get_sub_context(dsl.root_context_id)
        self.assertTrue(v)
        self.assertTrue(isinstance(r, dsl_type20.DSLType20_Context))
        self.assertEqual(r.get_name(), dsl.data.get_name())
        self.assertNotEqual(r, dsl.data)
        self.assertEqual(len(r.get_entries()), 1)

    def testDslType20_TestGetSubContext3(self):

        test_cfg = dsl_type20.DSLType20_Config()
        test_dsl = dsl_type20.DSLType20(test_cfg)

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "ctx1", None)

        v, r = test_dsl.add_variable(test_var1)
        self.assertTrue(v)

        v, r = test_dsl.add_context("ctx1", None, None)
        self.assertTrue(v)
        v, r = test_dsl.add_context("ctx2", None, "ctx1")
        self.assertTrue(v)

        v, r = test_dsl.get_sub_context("ctx1")
        self.assertTrue(v)
        self.assertTrue(isinstance(r, dsl_type20.DSLType20_Context))
        self.assertEqual(r.get_name(), test_dsl.data.entries[1].get_name())
        self.assertNotEqual(r, test_dsl.data.entries[1])
        self.assertEqual(len(r.get_entries()), 1)
        self.assertTrue("ctx2" in [x.get_name() for x in r.get_entries()] )

    def testDslType20_TestGetSubContext4(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.add_context("ctx1", None, None)
        self.assertTrue(v)
        v, r = dsl.add_context("ctx2", None, "ctx1")
        self.assertTrue(v)
        v, r = dsl.get_sub_context("ctx2", "ctx1")
        self.assertTrue(v)
        self.assertTrue(isinstance(r, dsl_type20.DSLType20_Context))
        self.assertEqual(r.get_name(), dsl.data.get_entries()[0].get_entries()[0].get_name())
        self.assertEqual(len(r.get_entries()), 0)

    def testDslType20_TestGetSubContext5(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.add_context("ctx1", None, None)
        self.assertTrue(v)
        v, r = dsl.add_context("ctx2", None, "ctx1")
        self.assertTrue(v)
        v, r = dsl.get_sub_context("ctx2")
        self.assertTrue(v)
        self.assertEqual(r, None)

    def testDslType20_TestGetSubContext6(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options = True))
        v, r = dsl.add_context("ctx1", [("opt1", "val1")], None)
        self.assertTrue(v)
        v, r = dsl.add_context("ctx2", [("opt2", "val2")], "ctx1")
        self.assertTrue(v)
        v, r = dsl.get_sub_context("ctx2", "ctx1")
        self.assertTrue(v)
        self.assertEqual(dsl_type20.convert_opt_obj_list_to_neutral_format(r.get_options()), [("opt1", "val1"), ("opt2", "val2")])

    def testDslType20_TestGetSubContext7(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options = True))
        v, r = dsl.add_context("ctx1", [("opt1", "val1")], None)
        self.assertTrue(v)
        v, r = dsl.add_context("ctx2", [("opt1", "val2")], "ctx1")
        self.assertTrue(v)
        v, r = dsl.get_sub_context("ctx2", "ctx1")
        self.assertTrue(v)
        self.assertEqual(dsl_type20.convert_opt_obj_list_to_neutral_format(r.get_options()), [("opt1", "val2")])

    def testDslType20_TestGetSubContext8(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options = True))
        v, r = dsl.add_context("ctx1", [("opt1", None)], None)
        self.assertTrue(v)
        v, r = dsl.add_context("ctx2", [("opt1", None)], "ctx1")
        self.assertTrue(v)
        v, r = dsl.get_sub_context("ctx2", "ctx1")
        self.assertTrue(v)
        self.assertEqual(dsl_type20.convert_opt_obj_list_to_neutral_format(r.get_options()), [])

    def testDslType20_TestGetSubContext9(self):

        test_cfg = dsl_type20.DSLType20_Config()
        test_dsl = dsl_type20.DSLType20(test_cfg)

        self.assertTrue(test_dsl.add_context("ctx1", None, None)[0])
        self.assertTrue(test_dsl.add_context("ctx2", None, "ctx1")[0])

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "var1", None)
        test_var1.new_value()
        test_var1.add_value_immediate("val1")

        self.assertTrue(test_dsl.add_variable(test_var1, "ctx1")[0])

        v, r = test_dsl.get_sub_context(None)
        self.assertTrue(v)
        self.assertEqual(len(r.get_entries()), 1)
        self.assertEqual(r.get_entries()[0].get_name(), "ctx1")
        self.assertEqual(len(r.get_entries()[0].get_entries()), 0)

    def testDslType20_TestGetSubContext10(self):

        test_cfg = dsl_type20.DSLType20_Config()
        test_dsl = dsl_type20.DSLType20(test_cfg)

        self.assertTrue(test_dsl.add_context("ctx1", None, None)[0])
        self.assertTrue(test_dsl.add_context("ctx2", None, "ctx1")[0])
        self.assertTrue(test_dsl.add_context("ctx3", None, "ctx2")[0])

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "var1", None)
        test_var1.new_value()
        test_var1.add_value_immediate("val1")

        test_var2 = dsl_type20.DSLType20_Variable(test_cfg, "var2", None)
        test_var2.new_value()
        test_var2.add_value_immediate("val2")

        self.assertTrue(test_dsl.add_variable(test_var1, "ctx1")[0])
        self.assertTrue(test_dsl.add_variable(test_var2, "ctx2")[0])

        v, r = test_dsl.get_sub_context("ctx1")
        self.assertTrue(v)
        self.assertEqual(len(r.get_entries()), 2)
        self.assertEqual(r.get_entries()[0].get_name(), "ctx2")
        self.assertEqual(len(r.get_entries()[0].get_entries()), 0)

    def testDslType20_GetAllContextsDFS1(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())

        self.assertTrue(dsl.add_context("ctx1", None)[0])
        self.assertTrue(dsl.add_context("ctx2", None)[0])
        self.assertTrue(dsl.add_context("ctx3", None)[0])
        self.assertTrue(dsl.add_context("ctx4", None, "ctx1")[0])
        self.assertTrue(dsl.add_context("ctx5", None, "ctx2")[0])
        self.assertTrue(dsl.add_context("ctx6", None, "ctx3")[0])
        self.assertTrue(dsl.add_context("ctx7", None, "ctx4")[0])
        self.assertTrue(dsl.add_context("ctx8", None, "ctx4")[0])
        self.assertTrue(dsl.add_context("ctx9", None, "ctx5")[0])

        v, r = dsl.get_all_contexts_dfs()
        self.assertTrue(v)
        self.assertEqual([x.get_name() for x in r], [dsl.root_context_id, "ctx1", "ctx4", "ctx7", "ctx8", "ctx2", "ctx5", "ctx9", "ctx3", "ctx6"])

    def testDslType20_TestGetSubContexts1(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl.add_context("ctx1", None, None)[0])
        self.assertTrue(dsl.add_context("ctx2", None, None)[0])
        v, r = dsl.get_all_sub_contexts(None)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertEqual([x.get_name() for x in r], ["ctx1", "ctx2"])

    def testDslType20_TestGetSubContexts2(self):

        test_cfg = dsl_type20.DSLType20_Config()
        test_dsl = dsl_type20.DSLType20(test_cfg)

        self.assertTrue(test_dsl.add_context("ctx1", None, None)[0])
        self.assertTrue(test_dsl.add_context("ctx2", None, None)[0])

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "var1", None)

        self.assertTrue(test_dsl.add_variable(test_var1)[0])

        self.assertFalse(test_dsl.add_context("ctx 3", None, None)[0])
        self.assertTrue(test_dsl.add_context("ctx4", None, None)[0])

        v, r = test_dsl.get_all_sub_contexts(None)
        self.assertTrue(v)
        self.assertEqual(len(r), 3)
        self.assertEqual([x.get_name() for x in r], ["ctx1", "ctx2", "ctx4"])

    def testDslType20_TestGetSubContexts3(self):

        test_cfg = dsl_type20.DSLType20_Config()
        test_dsl = dsl_type20.DSLType20(test_cfg)

        self.assertTrue(test_dsl.add_context("ctx1", None, None)[0])
        self.assertTrue(test_dsl.add_context("ctx2", None, "ctx1")[0])
        self.assertTrue(test_dsl.add_context("ctx3", None, "ctx2")[0])

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "var1", None)
        test_var1.new_value()
        test_var1.add_value_immediate("ctx3")

        self.assertTrue(test_dsl.add_variable(test_var1)[0])

        v, r = test_dsl.get_all_sub_contexts("ctx3")
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

    def testDslType20_TestGetSubContexts4(self):

        test_cfg = dsl_type20.DSLType20_Config()
        test_dsl = dsl_type20.DSLType20(test_cfg)

        self.assertTrue(test_dsl.add_context("ctx1", None, None)[0])
        self.assertTrue(test_dsl.add_context("ctx2", None, "ctx1")[0])
        self.assertTrue(test_dsl.add_context("ctx3", None, "ctx2")[0])

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "var1", None)
        test_var1.new_value()
        test_var1.add_value_immediate("ctx3")

        self.assertTrue(test_dsl.add_variable(test_var1)[0])

        v, r = test_dsl.get_all_sub_contexts("ctx2")
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertEqual([x.get_name() for x in r], ["ctx3"])

    def testDslType20_TestGetSubContexts5(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options = True))
        self.assertTrue(dsl.add_context("ctx1", [("opt1", "val1")], None)[0])
        self.assertTrue(dsl.add_context("ctx2", [("opt2", "val2")], "ctx1")[0])
        v, r = dsl.get_all_sub_contexts("ctx1")
        self.assertTrue(v)
        self.assertEqual(dsl_type20.convert_opt_obj_list_to_neutral_format(r[0].get_options()), [("opt1", "val1"), ("opt2", "val2")])

    def testDslType20_TestGetSubContexts6(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options = True))
        self.assertTrue(dsl.add_context("ctx1", [("opt1", "val1")], None)[0])
        self.assertTrue(dsl.add_context("ctx2", [("opt1", "val2")], "ctx1")[0])
        v, r = dsl.get_all_sub_contexts("ctx1")
        self.assertTrue(v)
        self.assertEqual(dsl_type20.convert_opt_obj_list_to_neutral_format(r[0].get_options()), [("opt1", "val2")])

    def testDslType20_TestGetSubContexts7(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options = True))
        self.assertTrue(dsl.add_context("ctx1", [("opt1", None)], None)[0])
        self.assertTrue(dsl.add_context("ctx2", [("opt1", None)], "ctx1")[0])
        v, r = dsl.get_all_sub_contexts("ctx1")
        self.assertTrue(v)
        self.assertEqual(dsl_type20.convert_opt_obj_list_to_neutral_format(r[0].get_options()), [])

    def testDslType20_TestAddContextFail1(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.add_context([], None, None)
        self.assertFalse(v)

    def testDslType20_TestAddContextFail2(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.add_context("", None, None)
        self.assertFalse(v)

    def testDslType20_TestAddContextFail5(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.add_context("ok", None, None)
        self.assertTrue(v)
        v, r = dsl.add_context("ok", None, None)
        self.assertFalse(v)

    def testDslType20_TestAddContextFail6(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.add_context("ok", "nok", None)
        self.assertFalse(v)

    def testDslType20_TestAddContextFail7(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertFalse(dsl.add_context("ok", [("var1", "first line\nsecond line")], None)[0])

    def testDslType20_TestAddContextFail8(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.add_context("@ok", None, None)
        self.assertFalse(v)

    def testDslType20_TestAddVariable1(self):

        test_cfg = dsl_type20.DSLType20_Config()
        test_dsl = dsl_type20.DSLType20(test_cfg)

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "var1", None)

        self.assertTrue(test_dsl.add_variable(test_var1)[0])

        v, r = test_dsl.get_all_variables()
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        var_obj = r[0]
        self.assertEqual(var_obj.get_name(), "var1")
        self.assertEqual(var_obj.get_value_resolved(), None)
        self.assertEqual(var_obj.get_options(), [])

    def testDslType20_TestAddVariable2(self):

        test_cfg = dsl_type20.DSLType20_Config()
        test_dsl = dsl_type20.DSLType20(test_cfg)

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "var1", None)
        test_var1.new_value()
        test_var1.add_value_immediate("")

        self.assertTrue(test_dsl.add_variable(test_var1)[0])

        v, r = test_dsl.get_all_variables()
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        var_obj = r[0]
        self.assertEqual(var_obj.get_name(), "var1")
        self.assertEqual(var_obj.get_value_resolved(), "")
        self.assertEqual(var_obj.get_options(), [])

    def testDslType20_TestAddVariable3(self):

        test_cfg = dsl_type20.DSLType20_Config()
        test_dsl = dsl_type20.DSLType20(test_cfg)

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "var1", None)
        test_var1.new_value()
        test_var1.add_value_immediate("val1")

        self.assertTrue(test_dsl.add_variable(test_var1)[0])

        v, r = test_dsl.get_all_variables()
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        var_obj = r[0]
        self.assertEqual(var_obj.get_name(), "var1")
        self.assertEqual(var_obj.get_value_resolved(), "val1")
        self.assertEqual(var_obj.get_options(), [])

    def testDslType20_TestAddVariable4(self):

        test_cfg = dsl_type20.DSLType20_Config()
        test_dsl = dsl_type20.DSLType20(test_cfg)

        test_opt1 = dsl_type20.DSLType20_Option(test_cfg, "opt1")
        test_opt1.new_value()
        test_opt1.add_value_immediate("val2")

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "var1", test_opt1)
        test_var1.new_value()
        test_var1.add_value_immediate("val1")

        self.assertTrue(test_dsl.add_variable(test_var1)[0])

        v, r = test_dsl.get_all_variables()
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        var_obj = r[0]
        self.assertEqual(var_obj.get_name(), "var1")
        self.assertEqual(var_obj.get_value_resolved(), "val1")
        self.assertEqual(dsl_type20.convert_opt_obj_list_to_neutral_format(var_obj.get_options()), [("opt1", "val2")])

    def testDslType20_TestAddVariable5(self):

        test_cfg = dsl_type20.DSLType20_Config()
        test_dsl = dsl_type20.DSLType20(test_cfg)

        test_opt1 = dsl_type20.DSLType20_Option(test_cfg, "opt1")
        test_opt1.new_value()
        test_opt1.add_value_immediate("val2")

        test_opt2 = dsl_type20.DSLType20_Option(test_cfg, "opt2")
        test_opt2.new_value()
        test_opt2.add_value_immediate("val3")

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "var1", [test_opt1, test_opt2])
        test_var1.new_value()
        test_var1.add_value_immediate("val1")

        self.assertTrue(test_dsl.add_variable(test_var1)[0])

        v, r = test_dsl.get_all_variables()
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        var_obj = r[0]
        self.assertEqual(var_obj.get_name(), "var1")
        self.assertEqual(var_obj.get_value_resolved(), "val1")
        self.assertEqual(dsl_type20.convert_opt_obj_list_to_neutral_format(var_obj.get_options()), [ ("opt1", "val2"), ("opt2", "val3") ])

    def testDslType20_TestAddVariable6(self):

        test_cfg = dsl_type20.DSLType20_Config()
        test_dsl = dsl_type20.DSLType20(test_cfg)

        test_opt1 = dsl_type20.DSLType20_Option(test_cfg, "opt1")
        test_opt1.new_value()
        test_opt1.add_value_immediate("val2")

        test_opt2 = dsl_type20.DSLType20_Option(test_cfg, "opt2")
        test_opt2.new_value()
        test_opt2.add_value_immediate("val3")

        test_opt3 = dsl_type20.DSLType20_Option(test_cfg, "opt1")
        test_opt3.new_value()
        test_opt3.add_value_immediate("val2")

        test_opt4 = dsl_type20.DSLType20_Option(test_cfg, "opt2")
        test_opt4.new_value()
        test_opt4.add_value_immediate("val3")

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "var1", [test_opt1, test_opt2])
        test_var1.new_value()
        test_var1.add_value_immediate("val1")

        test_var2 = dsl_type20.DSLType20_Variable(test_cfg, "var1", [test_opt3, test_opt4])
        test_var2.new_value()
        test_var2.add_value_immediate("val1")

        self.assertTrue(test_dsl.add_variable(test_var1)[0])
        self.assertTrue(test_dsl.add_variable(test_var2)[0])

        v, r = test_dsl.get_all_variables()
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        var_obj = r[0]
        self.assertEqual(var_obj.get_name(), "var1")
        self.assertEqual(var_obj.get_value_resolved(), "val1")
        self.assertEqual(dsl_type20.convert_opt_obj_list_to_neutral_format(var_obj.get_options()), [ ("opt1", "val2"), ("opt2", "val3") ])
        var_obj = r[1]
        self.assertEqual(var_obj.get_name(), "var1")
        self.assertEqual(var_obj.get_value_resolved(), "val1")
        self.assertEqual(dsl_type20.convert_opt_obj_list_to_neutral_format(var_obj.get_options()), [ ("opt1", "val2"), ("opt2", "val3") ])

    def testDslType20_TestAddVariable7(self):

        test_cfg = dsl_type20.DSLType20_Config(inherit_options = True)
        test_dsl = dsl_type20.DSLType20(test_cfg)

        test_opt1 = dsl_type20.DSLType20_Option(test_cfg, "opt1")
        test_opt1.new_value()
        test_opt1.add_value_immediate("val1")

        test_opt2 = dsl_type20.DSLType20_Option(test_cfg, "opt2")
        test_opt2.new_value()
        test_opt2.add_value_immediate("val3")

        self.assertTrue(test_dsl.add_context("ctx1", test_opt1, None)[0])

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "var1", test_opt2)
        test_var1.new_value()
        test_var1.add_value_immediate("val2")

        self.assertTrue(test_dsl.add_variable(test_var1, "ctx1" )[0])

        v, r = test_dsl.get_variables("var1", "ctx1")
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        var_obj = r[0]
        self.assertEqual(var_obj.get_name(), "var1")
        self.assertEqual(var_obj.get_value_resolved(), "val2")
        self.assertEqual(dsl_type20.convert_opt_obj_list_to_neutral_format(var_obj.get_options()), [("opt1", "val1"), ("opt2", "val3")])

    def testDslType20_TestAddVariable8(self):

        test_cfg = dsl_type20.DSLType20_Config(inherit_options = True)
        test_dsl = dsl_type20.DSLType20(test_cfg)

        test_opt1 = dsl_type20.DSLType20_Option(test_cfg, "opt1")
        test_opt1.new_value()
        test_opt1.add_value_immediate("val1")

        test_opt2 = dsl_type20.DSLType20_Option(test_cfg, "opt1")
        test_opt2.new_value()
        test_opt2.add_value_immediate("val3")

        self.assertTrue(test_dsl.add_context("ctx1", test_opt1, None)[0])

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "var1", test_opt2)
        test_var1.new_value()
        test_var1.add_value_immediate("val2")

        self.assertTrue(test_dsl.add_variable(test_var1, "ctx1" )[0])

        v, r = test_dsl.get_variables("var1", "ctx1")
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        var_obj = r[0]
        self.assertEqual(var_obj.get_name(), "var1")
        self.assertEqual(var_obj.get_value_resolved(), "val2")
        self.assertEqual(dsl_type20.convert_opt_obj_list_to_neutral_format(var_obj.get_options()), [("opt1", "val3")])

    def testDslType20_TestAddVariable9(self):

        test_cfg = dsl_type20.DSLType20_Config()
        test_dsl = dsl_type20.DSLType20(test_cfg)

        test_opt1 = dsl_type20.DSLType20_Option(test_cfg, "opt1")

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "var1", test_opt1)
        test_var1.new_value()
        test_var1.add_value_immediate("val1")

        self.assertTrue(test_dsl.add_variable(test_var1)[0])

        v, r = test_dsl.get_all_variables()
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertEqual(var_fmt_helper(test_dsl.get_all_variables()), [ ("var1", "val1", [("opt1", None)]) ])

    def testDslType20_TestAddVariable10(self):

        test_cfg = dsl_type20.DSLType20_Config()
        test_dsl = dsl_type20.DSLType20(test_cfg)

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "var1", None)

        self.assertTrue(test_dsl.add_variable(test_var1)[0])

    def testDslType20_TestAddVariable11(self):

        test_cfg = dsl_type20.DSLType20_Config()
        test_dsl = dsl_type20.DSLType20(test_cfg)

        test_opt1 = dsl_type20.DSLType20_Option(test_cfg, "opt1")
        test_opt1.new_value()
        test_opt1.add_value_immediate("val1")

        test_opt2 = dsl_type20.DSLType20_Option(test_cfg, "opt2")
        test_opt2.new_value()
        test_opt2.add_value_immediate("val3")

        self.assertTrue(test_dsl.add_context("ctx1", test_opt1, None)[0])

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "var1", test_opt2)
        test_var1.new_value()
        test_var1.add_value_immediate("val2")

        self.assertTrue(test_dsl.add_variable(test_var1, "ctx1" )[0])

        v, r = test_dsl.get_variables("var1", "ctx1")
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        var_obj = r[0]
        self.assertEqual(var_obj.get_name(), "var1")
        self.assertEqual(var_obj.get_value_resolved(), "val2")
        self.assertEqual(dsl_type20.convert_opt_obj_list_to_neutral_format(var_obj.get_options()), [("opt2", "val3")])

    def testDslType20_TestAddVariable12(self):

        test_cfg = dsl_type20.DSLType20_Config(inherit_options = True)
        test_dsl = dsl_type20.DSLType20(test_cfg)

        test_opt1 = dsl_type20.DSLType20_Option(test_cfg, "opt1")

        test_opt2 = dsl_type20.DSLType20_Option(test_cfg, "opt1")
        test_opt2.new_value()
        test_opt2.add_value_immediate("val3")

        self.assertTrue(test_dsl.add_context("ctx1", test_opt1, None)[0])

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "var1", test_opt2)
        test_var1.new_value()
        test_var1.add_value_immediate("val2")

        self.assertTrue(test_dsl.add_variable(test_var1, "ctx1" )[0])

        v, r = test_dsl.get_variables("var1", "ctx1")
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        var_obj = r[0]
        self.assertEqual(var_obj.get_name(), "var1")
        self.assertEqual(var_obj.get_value_resolved(), "val2")
        self.assertEqual(dsl_type20.convert_opt_obj_list_to_neutral_format(var_obj.get_options()), [("opt1", "val3")])

    def testDslType20_TestAddVariable13(self):

        test_cfg = dsl_type20.DSLType20_Config(inherit_options = True)
        test_dsl = dsl_type20.DSLType20(test_cfg)

        test_opt1 = dsl_type20.DSLType20_Option(test_cfg, "opt1")
        test_opt1.new_value()
        test_opt1.add_value_immediate("val3")

        test_opt2 = dsl_type20.DSLType20_Option(test_cfg, "opt1")

        self.assertTrue(test_dsl.add_context("ctx1", test_opt1, None)[0])

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "var1", test_opt2)
        test_var1.new_value()
        test_var1.add_value_immediate("val2")

        self.assertTrue(test_dsl.add_variable(test_var1, "ctx1" )[0])

        v, r = test_dsl.get_variables("var1", "ctx1")
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        var_obj = r[0]
        self.assertEqual(var_obj.get_name(), "var1")
        self.assertEqual(var_obj.get_value_resolved(), "val2")
        self.assertEqual(dsl_type20.convert_opt_obj_list_to_neutral_format(var_obj.get_options()), [("opt1", None)])

    def testDslType20_TestAddVariable14(self):

        test_cfg = dsl_type20.DSLType20_Config(inherit_options = True)
        test_dsl = dsl_type20.DSLType20(test_cfg)

        test_opt1 = dsl_type20.DSLType20_Option(test_cfg, "opt1")
        test_opt2 = dsl_type20.DSLType20_Option(test_cfg, "opt1")

        self.assertTrue(test_dsl.add_context("ctx1", test_opt1, None)[0])

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "var1", test_opt2)
        test_var1.new_value()
        test_var1.add_value_immediate("val2")

        self.assertTrue(test_dsl.add_variable(test_var1, "ctx1" )[0])

        v, r = test_dsl.get_variables("var1", "ctx1")
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        var_obj = r[0]
        self.assertEqual(var_obj.get_name(), "var1")
        self.assertEqual(var_obj.get_value_resolved(), "val2")
        self.assertEqual(dsl_type20.convert_opt_obj_list_to_neutral_format(var_obj.get_options()), [])

    def testDslType20_TestAddVariable15(self):

        test_cfg = dsl_type20.DSLType20_Config(inherit_options = True)
        test_dsl = dsl_type20.DSLType20(test_cfg)

        test_opt1 = dsl_type20.DSLType20_Option(test_cfg, "opt1")
        test_opt1.new_value()
        test_opt1.add_value_immediate("val2")

        test_opt2 = dsl_type20.DSLType20_Option(test_cfg, "opt2")
        test_opt2.new_value()
        test_opt2.add_value_immediate("val3")

        test_opt3 = dsl_type20.DSLType20_Option(test_cfg, "opt3")
        test_opt3.new_value()
        test_opt3.add_value_immediate("val4")

        test_opt4 = dsl_type20.DSLType20_Option(test_cfg, "opt4")
        test_opt4.new_value()
        test_opt4.add_value_immediate("val5")

        self.assertTrue(test_dsl.add_context("ctx1", test_opt1, None)[0])
        self.assertTrue(test_dsl.add_context("ctx2", test_opt2, "ctx1")[0])
        self.assertTrue(test_dsl.add_context("ctx3", test_opt3, "ctx2")[0])

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "var1", test_opt4)
        test_var1.new_value()
        test_var1.add_value_immediate("val2")

        self.assertTrue(test_dsl.add_variable(test_var1, "ctx3" )[0])

        v, r = test_dsl.get_variables("var1", "ctx3")
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        var_obj = r[0]
        self.assertEqual(var_obj.get_name(), "var1")
        self.assertEqual(var_obj.get_value_resolved(), "val2")
        self.assertEqual(dsl_type20.convert_opt_obj_list_to_neutral_format(var_obj.get_options()), [("opt1", "val2"), ("opt2", "val3"), ("opt3", "val4"), ("opt4", "val5")])

    def testDslType20_TestAddVariable16(self):

        test_cfg = dsl_type20.DSLType20_Config()
        test_dsl = dsl_type20.DSLType20(test_cfg)

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "var1", None)
        test_var1.new_value()
        test_var1.add_value_immediate("val1")

        self.assertTrue(test_dsl.add_variable(test_var1, "ctx1")[0])

        v, r = test_dsl.get_all_variables("ctx1")
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        var_obj = r[0]
        self.assertEqual(var_obj.get_name(), "var1")
        self.assertEqual(var_obj.get_value_resolved(), "val1")
        self.assertEqual(dsl_type20.convert_opt_obj_list_to_neutral_format(var_obj.get_options()), [])

    def testDslType20_TestAddVariable17(self):

        test_cfg = dsl_type20.DSLType20_Config(allow_var_dupes = False)
        test_dsl = dsl_type20.DSLType20(test_cfg)

        self.assertTrue(test_dsl.add_context("var1", None, None)[0])

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "var1", None)

        self.assertTrue(test_dsl.add_variable(test_var1)[0])

        self.assertEqual(var_fmt_helper(test_dsl.get_all_variables()), [("var1", None, [])])

    def testDslType20_TestAddVariable18(self):

        test_cfg = dsl_type20.DSLType20_Config()
        test_dsl = dsl_type20.DSLType20(test_cfg)

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "var1", None)
        test_var1.new_value()
        test_var1.add_value_immediate("one")

        self.assertTrue(test_dsl.add_variable(test_var1)[0])

        self.assertEqual(var_fmt_helper(test_dsl.get_all_variables()), [("var1", "one", [])])

    def testDslType20_TestAddVariable19(self):

        test_cfg = dsl_type20.DSLType20_Config()
        test_dsl = dsl_type20.DSLType20(test_cfg)

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "var1", None)
        test_var1.new_value()
        test_var1.add_value_immediate("one")
        test_var1.new_value()
        test_var1.add_value_immediate("two")

        self.assertTrue(test_dsl.add_variable(test_var1)[0])

        self.assertEqual(var_fmt_helper(test_dsl.get_all_variables()), [("var1", ["one", "two"], [])])

    def testDslType20_TestAddVariable20(self):

        test_cfg = dsl_type20.DSLType20_Config()
        test_dsl = dsl_type20.DSLType20(test_cfg)

        test_opt1 = dsl_type20.DSLType20_Option(test_cfg, "opt1")

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "var1", test_opt1)
        test_var1.new_value()
        test_var1.add_value_immediate("one")
        test_var1.new_value()
        test_var1.add_value_immediate("two")

        self.assertTrue(test_dsl.add_variable(test_var1)[0])

        self.assertEqual(var_fmt_helper(test_dsl.get_all_variables()), [("var1", ["one", "two"], [("opt1", None)])])

    def testDslType20_TestAddVariable21(self):

        test_cfg = dsl_type20.DSLType20_Config()
        test_dsl = dsl_type20.DSLType20(test_cfg)

        test_opt1 = dsl_type20.DSLType20_Option(test_cfg, "opt1")
        test_opt1.new_value()
        test_opt1.add_value_immediate("three")
        test_opt1.new_value()
        test_opt1.add_value_immediate("four")

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "var1", test_opt1)
        test_var1.new_value()
        test_var1.add_value_immediate("one")
        test_var1.new_value()
        test_var1.add_value_immediate("two")

        self.assertTrue(test_dsl.add_variable(test_var1)[0])

        self.assertEqual(var_fmt_helper(test_dsl.get_all_variables()), [("var1", ["one", "two"], [("opt1", ["three", "four"])])])

    def testDslType20_TestAddVariableFail1(self):

        test_cfg = dsl_type20.DSLType20_Config()
        test_dsl = dsl_type20.DSLType20(test_cfg)

        test_opt1 = dsl_type20.DSLType20_Option(test_cfg, "opt1")

        self.assertFalse(test_dsl.add_variable(test_opt1)[0])

    def testDslType20_TestDisallowDupes1(self):

        test_cfg = dsl_type20.DSLType20_Config(allow_var_dupes = False)
        test_dsl = dsl_type20.DSLType20(test_cfg)

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "var1", None)
        test_var1.new_value()
        test_var1.add_value_immediate("val1")

        test_var2 = dsl_type20.DSLType20_Variable(test_cfg, "var1", None)
        test_var2.new_value()
        test_var2.add_value_immediate("val2")

        self.assertTrue(test_dsl.add_variable(test_var1)[0])
        self.assertFalse(test_dsl.add_variable(test_var2)[0])

    def testDslType20_TestDisallowDupes2(self):

        test_cfg = dsl_type20.DSLType20_Config(allow_var_dupes = False)
        test_dsl = dsl_type20.DSLType20(test_cfg)

        test_opt1 = dsl_type20.DSLType20_Option(test_cfg, "opt1")

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "var1", test_opt1)
        test_var1.new_value()
        test_var1.add_value_immediate("val1")

        self.assertTrue(test_dsl.add_variable(test_var1)[0])

    def testDslType20_TestDisallowDupes3(self):

        test_cfg = dsl_type20.DSLType20_Config(allow_var_dupes = False)
        test_dsl = dsl_type20.DSLType20(test_cfg)

        test_opt1 = dsl_type20.DSLType20_Option(test_cfg, "opt1")
        test_opt2 = dsl_type20.DSLType20_Option(test_cfg, "opt1")

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "var1", test_opt1)
        test_var1.new_value()
        test_var1.add_value_immediate("val1")

        test_var2 = dsl_type20.DSLType20_Variable(test_cfg, "var2", test_opt2)
        test_var2.new_value()
        test_var2.add_value_immediate("val1")

        self.assertTrue(test_dsl.add_variable(test_var1)[0])
        self.assertTrue(test_dsl.add_variable(test_var2)[0])

    def testDslType20_TestDisallowDupes4(self):

        test_cfg = dsl_type20.DSLType20_Config(allow_var_dupes = False)
        test_dsl = dsl_type20.DSLType20(test_cfg)

        self.assertTrue(test_dsl.add_context("ctx1", None, None)[0])

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "var1", None)
        test_var1.new_value()
        test_var1.add_value_immediate("val1")

        test_var2 = dsl_type20.DSLType20_Variable(test_cfg, "var1", None)
        test_var2.new_value()
        test_var2.add_value_immediate("val2")

        self.assertTrue(test_dsl.add_variable(test_var1, "ctx1")[0])
        self.assertFalse(test_dsl.add_variable(test_var2, "ctx1")[0])

    def testDslType20_TestDisallowDupes5(self):

        test_cfg = dsl_type20.DSLType20_Config(allow_var_dupes = False)
        dsl = dsl_type20.DSLType20(test_cfg)

        self.assertTrue(dsl.add_context("ctx1", None, None)[0])

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "var1", None)
        test_var1.new_value()
        test_var1.add_value_immediate("val1")

        test_var2 = dsl_type20.DSLType20_Variable(test_cfg, "var1", None)
        test_var2.new_value()
        test_var2.add_value_immediate("val2")

        self.assertTrue(dsl.add_variable(test_var1, "ctx1")[0])
        self.assertTrue(dsl.add_variable(test_var2, None)[0])

    def testDslType20_TestDisallowDupesParse1(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes = False))

        contents_cfg_test_fail_dupevar = "var1 = \"val1\"\n"
        contents_cfg_test_fail_dupevar += "var1 = \"val2\"\n"

        v, r = dsl.parse(contents_cfg_test_fail_dupevar)
        self.assertFalse(v)

    def testDslType20_TestRemVariables1(self):

        test_cfg = dsl_type20.DSLType20_Config()
        test_dsl = dsl_type20.DSLType20(test_cfg)

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "var1", None)
        test_var1.new_value()
        test_var1.add_value_immediate("val1")

        self.assertTrue(test_dsl.add_variable(test_var1)[0])

        v, r = test_dsl.get_all_variables()
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        var_obj = r[0]
        self.assertEqual(var_obj.get_name(), "var1")
        self.assertEqual(var_obj.get_value_resolved(), "val1")
        self.assertEqual(var_obj.get_options(), [])

        v, r = test_dsl.rem_variables("var1")
        self.assertTrue(v)
        self.assertEqual(r, 1)

        v, r = test_dsl.get_all_variables()
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

    def testDslType20_TestRemVariables2(self):

        test_cfg = dsl_type20.DSLType20_Config()
        test_dsl = dsl_type20.DSLType20(test_cfg)

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "var1", None)
        test_var1.new_value()
        test_var1.add_value_immediate("val1")

        self.assertTrue(test_dsl.add_variable(test_var1)[0])

        v, r = test_dsl.get_all_variables()
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        var_obj = r[0]
        self.assertEqual(var_obj.get_name(), "var1")
        self.assertEqual(var_obj.get_value_resolved(), "val1")
        self.assertEqual(var_obj.get_options(), [])

        v, r = test_dsl.rem_variables("var1", "ctx1")
        self.assertFalse(v)

    def testDslType20_TestRemVariables3(self):

        test_cfg = dsl_type20.DSLType20_Config()
        test_dsl = dsl_type20.DSLType20(test_cfg)

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "var1", None)
        test_var1.new_value()
        test_var1.add_value_immediate("val1")

        test_var2 = dsl_type20.DSLType20_Variable(test_cfg, "var1", None)
        test_var2.new_value()
        test_var2.add_value_immediate("val2")

        self.assertTrue(test_dsl.add_variable(test_var1)[0])
        self.assertTrue(test_dsl.add_variable(test_var2)[0])

        v, r = test_dsl.get_all_variables()
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        var_obj = r[0]
        self.assertEqual(var_obj.get_name(), "var1")
        self.assertEqual(var_obj.get_value_resolved(), "val1")
        self.assertEqual(var_obj.get_options(), [])
        var_obj = r[1]
        self.assertEqual(var_obj.get_name(), "var1")
        self.assertEqual(var_obj.get_value_resolved(), "val2")
        self.assertEqual(var_obj.get_options(), [])

        v, r = test_dsl.rem_variables("var1")
        self.assertTrue(v)
        self.assertEqual(r, 2)

        v, r = test_dsl.get_all_variables()
        self.assertTrue(v)
        self.assertEqual(len(r), 0)
        self.assertEqual(r, [])

    def testDslType20_TestRemVariables4(self):

        test_cfg = dsl_type20.DSLType20_Config()
        test_dsl = dsl_type20.DSLType20(test_cfg)

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "var1", None)
        test_var1.new_value()
        test_var1.add_value_immediate("val1")

        self.assertTrue(test_dsl.add_variable(test_var1)[0])

        v, r = test_dsl.get_all_variables()
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        var_obj = r[0]
        self.assertEqual(var_obj.get_name(), "var1")
        self.assertEqual(var_obj.get_value_resolved(), "val1")
        self.assertEqual(var_obj.get_options(), [])

        v, r = test_dsl.rem_variables("var2")
        self.assertTrue(v)
        self.assertEqual(r, 0)

        v, r = test_dsl.get_all_variables()
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        var_obj = r[0]
        self.assertEqual(var_obj.get_name(), "var1")
        self.assertEqual(var_obj.get_value_resolved(), "val1")
        self.assertEqual(var_obj.get_options(), [])

    def testDslType20_TestRemVariables5(self):

        test_cfg = dsl_type20.DSLType20_Config()
        test_dsl = dsl_type20.DSLType20(test_cfg)

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "var1", None)
        test_var1.new_value()
        test_var1.add_value_immediate("val2")

        test_var2 = dsl_type20.DSLType20_Variable(test_cfg, "var1", None)
        test_var2.new_value()
        test_var2.add_value_immediate("val4")

        self.assertTrue(test_dsl.add_variable(test_var1)[0])
        self.assertTrue(test_dsl.add_variable(test_var2, "ctx1")[0])

        v, r = test_dsl.get_all_variables()
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        var_obj = r[0]
        self.assertEqual(var_obj.get_name(), "var1")
        self.assertEqual(var_obj.get_value_resolved(), "val2")
        self.assertEqual(var_obj.get_options(), [])

        v, r = test_dsl.get_all_variables("ctx1")
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        var_obj = r[0]
        self.assertEqual(var_obj.get_name(), "var1")
        self.assertEqual(var_obj.get_value_resolved(), "val4")
        self.assertEqual(var_obj.get_options(), [])

        v, r = test_dsl.rem_variables("var1", "ctx1")
        self.assertTrue(v)
        self.assertEqual(r, 1)

        v, r = test_dsl.get_all_variables()
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        var_obj = r[0]
        self.assertEqual(var_obj.get_name(), "var1")
        self.assertEqual(var_obj.get_value_resolved(), "val2")
        self.assertEqual(var_obj.get_options(), [])

        v, r = test_dsl.get_all_variables("ctx1")
        self.assertTrue(v)
        self.assertEqual(len(r), 0)
        self.assertEqual(r, [])

    def testDslType20_TestRemVariables6(self):

        test_cfg = dsl_type20.DSLType20_Config()
        test_dsl = dsl_type20.DSLType20(test_cfg)

        self.assertTrue(test_dsl.add_context("ctx1", None, None)[0])
        self.assertTrue(test_dsl.add_context("ctx2", None, "ctx1")[0])
        self.assertTrue(test_dsl.add_context("ctx3", None, "ctx2")[0])

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "var1", None)
        test_var1.new_value()
        test_var1.add_value_immediate("val1")

        test_var2 = dsl_type20.DSLType20_Variable(test_cfg, "var2", None)
        test_var2.new_value()
        test_var2.add_value_immediate("val2")

        test_var3 = dsl_type20.DSLType20_Variable(test_cfg, "var3", None)
        test_var3.new_value()
        test_var3.add_value_immediate("val3")

        test_var4 = dsl_type20.DSLType20_Variable(test_cfg, "var4", None)
        test_var4.new_value()
        test_var4.add_value_immediate("val4")

        test_var5 = dsl_type20.DSLType20_Variable(test_cfg, "var5", None)
        test_var5.new_value()
        test_var5.add_value_immediate("val5")

        test_var6 = dsl_type20.DSLType20_Variable(test_cfg, "var6", None)
        test_var6.new_value()
        test_var6.add_value_immediate("val6")

        test_var7 = dsl_type20.DSLType20_Variable(test_cfg, "var7", None)
        test_var7.new_value()
        test_var7.add_value_immediate("val7")

        test_var8 = dsl_type20.DSLType20_Variable(test_cfg, "var8", None)
        test_var8.new_value()
        test_var8.add_value_immediate("val8")

        test_var9 = dsl_type20.DSLType20_Variable(test_cfg, "var9", None)
        test_var9.new_value()
        test_var9.add_value_immediate("val9")

        self.assertTrue(test_dsl.add_variable(test_var1, "ctx1")[0])
        self.assertTrue(test_dsl.add_variable(test_var2, "ctx1")[0])
        self.assertTrue(test_dsl.add_variable(test_var3, "ctx1")[0])
        self.assertTrue(test_dsl.add_variable(test_var4, "ctx2")[0])
        self.assertTrue(test_dsl.add_variable(test_var5, "ctx2")[0])
        self.assertTrue(test_dsl.add_variable(test_var6, "ctx2")[0])
        self.assertTrue(test_dsl.add_variable(test_var7, "ctx3")[0])
        self.assertTrue(test_dsl.add_variable(test_var8, "ctx3")[0])
        self.assertTrue(test_dsl.add_variable(test_var9, "ctx3")[0])

        self.assertEqual(var_fmt_helper(test_dsl.get_all_variables("ctx1")), [("var1", "val1", []), ("var2", "val2", []), ("var3", "val3", [])])
        self.assertEqual(var_fmt_helper(test_dsl.get_all_variables("ctx2")), [("var4", "val4", []), ("var5", "val5", []), ("var6", "val6", [])])
        self.assertEqual(var_fmt_helper(test_dsl.get_all_variables("ctx3")), [("var7", "val7", []), ("var8", "val8", []), ("var9", "val9", [])])

        v, r = test_dsl.rem_variables("var1", "ctx1")
        self.assertTrue(v)
        self.assertEqual(r, 1)

        self.assertEqual(var_fmt_helper(test_dsl.get_all_variables("ctx1")), [("var2", "val2", []), ("var3", "val3", [])])
        self.assertEqual(var_fmt_helper(test_dsl.get_all_variables("ctx2")), [("var4", "val4", []), ("var5", "val5", []), ("var6", "val6", [])])
        self.assertEqual(var_fmt_helper(test_dsl.get_all_variables("ctx3")), [("var7", "val7", []), ("var8", "val8", []), ("var9", "val9", [])])

        v, r = test_dsl.rem_variables("var4", "ctx2")
        self.assertTrue(v)
        self.assertEqual(r, 1)

        self.assertEqual(var_fmt_helper(test_dsl.get_all_variables("ctx1")), [("var2", "val2", []), ("var3", "val3", [])])
        self.assertEqual(var_fmt_helper(test_dsl.get_all_variables("ctx2")), [("var5", "val5", []), ("var6", "val6", [])])
        self.assertEqual(var_fmt_helper(test_dsl.get_all_variables("ctx3")), [("var7", "val7", []), ("var8", "val8", []), ("var9", "val9", [])])

        v, r = test_dsl.rem_variables("var7", "ctx3")
        self.assertTrue(v)
        self.assertEqual(r, 1)

        self.assertEqual(var_fmt_helper(test_dsl.get_all_variables("ctx1")), [("var2", "val2", []), ("var3", "val3", [])])
        self.assertEqual(var_fmt_helper(test_dsl.get_all_variables("ctx2")), [("var5", "val5", []), ("var6", "val6", [])])
        self.assertEqual(var_fmt_helper(test_dsl.get_all_variables("ctx3")), [("var8", "val8", []), ("var9", "val9", [])])

    def testDslType20_TestRemVariables7(self):

        test_cfg = dsl_type20.DSLType20_Config()
        test_dsl = dsl_type20.DSLType20(test_cfg)

        self.assertTrue(test_dsl.add_context("ctx1", None, None)[0])
        self.assertTrue(test_dsl.add_context("ctx2", None, "ctx1")[0])
        self.assertTrue(test_dsl.add_context("ctx3", None, "ctx2")[0])

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "var1", None)
        test_var1.new_value()
        test_var1.add_value_immediate("val1")

        test_var2 = dsl_type20.DSLType20_Variable(test_cfg, "var1", None)
        test_var2.new_value()
        test_var2.add_value_immediate("val2")

        test_var3 = dsl_type20.DSLType20_Variable(test_cfg, "var1", None)
        test_var3.new_value()
        test_var3.add_value_immediate("val3")

        test_var4 = dsl_type20.DSLType20_Variable(test_cfg, "var2", None)
        test_var4.new_value()
        test_var4.add_value_immediate("val4")

        test_var5 = dsl_type20.DSLType20_Variable(test_cfg, "var2", None)
        test_var5.new_value()
        test_var5.add_value_immediate("val5")

        test_var6 = dsl_type20.DSLType20_Variable(test_cfg, "var2", None)
        test_var6.new_value()
        test_var6.add_value_immediate("val6")

        test_var7 = dsl_type20.DSLType20_Variable(test_cfg, "var3", None)
        test_var7.new_value()
        test_var7.add_value_immediate("val7")

        test_var8 = dsl_type20.DSLType20_Variable(test_cfg, "var3", None)
        test_var8.new_value()
        test_var8.add_value_immediate("val8")

        test_var9 = dsl_type20.DSLType20_Variable(test_cfg, "var3", None)
        test_var9.new_value()
        test_var9.add_value_immediate("val9")

        self.assertTrue(test_dsl.add_variable(test_var1, "ctx1")[0])
        self.assertTrue(test_dsl.add_variable(test_var2, "ctx1")[0])
        self.assertTrue(test_dsl.add_variable(test_var3, "ctx1")[0])
        self.assertTrue(test_dsl.add_variable(test_var4, "ctx2")[0])
        self.assertTrue(test_dsl.add_variable(test_var5, "ctx2")[0])
        self.assertTrue(test_dsl.add_variable(test_var6, "ctx2")[0])
        self.assertTrue(test_dsl.add_variable(test_var7, "ctx3")[0])
        self.assertTrue(test_dsl.add_variable(test_var8, "ctx3")[0])
        self.assertTrue(test_dsl.add_variable(test_var9, "ctx3")[0])

        self.assertEqual(var_fmt_helper(test_dsl.get_all_variables("ctx1")), [("var1", "val1", []), ("var1", "val2", []), ("var1", "val3", [])])
        self.assertEqual(var_fmt_helper(test_dsl.get_all_variables("ctx2")), [("var2", "val4", []), ("var2", "val5", []), ("var2", "val6", [])])
        self.assertEqual(var_fmt_helper(test_dsl.get_all_variables("ctx3")), [("var3", "val7", []), ("var3", "val8", []), ("var3", "val9", [])])

        v, r = test_dsl.rem_variables("var1", "ctx1")
        self.assertTrue(v)
        self.assertEqual(r, 3)

        self.assertEqual(var_fmt_helper(test_dsl.get_all_variables("ctx1")), [])
        self.assertEqual(var_fmt_helper(test_dsl.get_all_variables("ctx2")), [("var2", "val4", []), ("var2", "val5", []), ("var2", "val6", [])])
        self.assertEqual(var_fmt_helper(test_dsl.get_all_variables("ctx3")), [("var3", "val7", []), ("var3", "val8", []), ("var3", "val9", [])])

        v, r = test_dsl.rem_variables("var2", "ctx2")
        self.assertTrue(v)
        self.assertEqual(r, 3)

        self.assertEqual(var_fmt_helper(test_dsl.get_all_variables("ctx1")), [])
        self.assertEqual(var_fmt_helper(test_dsl.get_all_variables("ctx2")), [])
        self.assertEqual(var_fmt_helper(test_dsl.get_all_variables("ctx3")), [("var3", "val7", []), ("var3", "val8", []), ("var3", "val9", [])])

        v, r = test_dsl.rem_variables("var3", "ctx3")
        self.assertTrue(v)
        self.assertEqual(r, 3)

        self.assertEqual(var_fmt_helper(test_dsl.get_all_variables("ctx1")), [])
        self.assertEqual(var_fmt_helper(test_dsl.get_all_variables("ctx2")), [])
        self.assertEqual(var_fmt_helper(test_dsl.get_all_variables("ctx3")), [])

    def testDslType20_TestRemAllVariables1(self):

        test_cfg = dsl_type20.DSLType20_Config()
        test_dsl = dsl_type20.DSLType20(test_cfg)

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "var1", None)
        test_var1.new_value()
        test_var1.add_value_immediate("val1")

        self.assertTrue(test_dsl.add_variable(test_var1)[0])

        v, r = test_dsl.get_all_variables()
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        var_obj = r[0]
        self.assertEqual(var_obj.get_name(), "var1")
        self.assertEqual(var_obj.get_value_resolved(), "val1")
        self.assertEqual(var_obj.get_options(), [])

        v, r = test_dsl.rem_all_variables()
        self.assertTrue(v)
        self.assertEqual(r, ["var1"])

        v, r = test_dsl.get_all_variables()
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

    def testDslType20_TestRemAllVariables2(self):

        test_cfg = dsl_type20.DSLType20_Config()
        test_dsl = dsl_type20.DSLType20(test_cfg)

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "var1", None)
        test_var1.new_value()
        test_var1.add_value_immediate("val1")

        self.assertTrue(test_dsl.add_variable(test_var1, "ctx1")[0])

        v, r = test_dsl.get_all_variables("ctx1")
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        var_obj = r[0]
        self.assertEqual(var_obj.get_name(), "var1")
        self.assertEqual(var_obj.get_value_resolved(), "val1")
        self.assertEqual(var_obj.get_options(), [])

        v, r = test_dsl.rem_all_variables("ctx1")
        self.assertTrue(v)
        self.assertEqual(r, ["var1"])

        v, r = test_dsl.get_all_variables()
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

    def testDslType20_TestRemAllVariables3(self):

        test_cfg = dsl_type20.DSLType20_Config()
        test_dsl = dsl_type20.DSLType20(test_cfg)

        test_var1 = dsl_type20.DSLType20_Variable(test_cfg, "var1", None)
        test_var1.new_value()
        test_var1.add_value_immediate("val1")

        self.assertTrue(test_dsl.add_variable(test_var1, "ctx1")[0])

        v, r = test_dsl.get_all_variables("ctx1")
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        var_obj = r[0]
        self.assertEqual(var_obj.get_name(), "var1")
        self.assertEqual(var_obj.get_value_resolved(), "val1")
        self.assertEqual(var_obj.get_options(), [])

        v, r = test_dsl.rem_all_variables()
        self.assertTrue(v)
        self.assertEqual(r, [])

        v, r = test_dsl.get_all_variables("ctx1")
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        var_obj = r[0]
        self.assertEqual(var_obj.get_name(), "var1")
        self.assertEqual(var_obj.get_value_resolved(), "val1")
        self.assertEqual(var_obj.get_options(), [])

    def testDslType20_TestRemAllVariables4(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl.add_variable("var1", "val1", [], "ctx1")[0])
        self.assertTrue(dsl.add_variable("var2", "val2", [], "ctx1")[0])
        self.assertTrue(dsl.add_variable("var3", "val3", [], "ctx1")[0])
        self.assertTrue(dsl.add_variable("var3", "val3", [])[0])
        v, r = dsl.get_all_variables("ctx1")
        self.assertTrue(v)
        self.assertEqual(len(r), 3)
        var_obj = r[0]
        self.assertEqual(var_obj.get_name(), "var1")
        self.assertEqual(var_obj.get_value(), "val1")
        self.assertEqual(var_obj.get_options(), [])
        var_obj = r[1]
        self.assertEqual(var_obj.get_name(), "var2")
        self.assertEqual(var_obj.get_value(), "val2")
        self.assertEqual(var_obj.get_options(), [])
        var_obj = r[2]
        self.assertEqual(var_obj.get_name(), "var3")
        self.assertEqual(var_obj.get_value(), "val3")
        self.assertEqual(var_obj.get_options(), [])
        v, r = dsl.rem_all_variables("ctx1")
        self.assertTrue(v)
        self.assertEqual(r, ["var1", "var2", "var3"])
        v, r = dsl.get_all_variables("ctx1")
        self.assertTrue(v)
        self.assertEqual(len(r), 0)
        self.assertEqual(r, [])

    def testDslType20_TestRemAllVariables5(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl.add_context("ctx1", None, None)[0])
        self.assertTrue(dsl.add_context("ctx2", None, "ctx1")[0])
        self.assertTrue(dsl.add_context("ctx3", None, "ctx2")[0])
        self.assertTrue(dsl.add_variable("var1", "val1", [], "ctx1")[0])
        self.assertTrue(dsl.add_variable("var2", "val2", [], "ctx1")[0])
        self.assertTrue(dsl.add_variable("var3", "val3", [], "ctx1")[0])
        self.assertTrue(dsl.add_variable("var4", "val4", [], "ctx2")[0])
        self.assertTrue(dsl.add_variable("var5", "val5", [], "ctx2")[0])
        self.assertTrue(dsl.add_variable("var6", "val6", [], "ctx2")[0])
        self.assertTrue(dsl.add_variable("var7", "val7", [], "ctx3")[0])
        self.assertTrue(dsl.add_variable("var8", "val8", [], "ctx3")[0])
        self.assertTrue(dsl.add_variable("var9", "val9", [], "ctx3")[0])
        self.assertEqual(var_fmt_helper(dsl.get_all_variables("ctx1")), [("var1", "val1", []), ("var2", "val2", []), ("var3", "val3", [])])
        self.assertEqual(var_fmt_helper(dsl.get_all_variables("ctx2")), [("var4", "val4", []), ("var5", "val5", []), ("var6", "val6", [])])
        self.assertEqual(var_fmt_helper(dsl.get_all_variables("ctx3")), [("var7", "val7", []), ("var8", "val8", []), ("var9", "val9", [])])
        v, r = dsl.rem_all_variables("ctx1")
        self.assertTrue(v)
        self.assertEqual(r, ["var1", "var2", "var3"])
        self.assertEqual(var_fmt_helper(dsl.get_all_variables("ctx1")), [])
        self.assertEqual(var_fmt_helper(dsl.get_all_variables("ctx2")), [("var4", "val4", []), ("var5", "val5", []), ("var6", "val6", [])])
        self.assertEqual(var_fmt_helper(dsl.get_all_variables("ctx3")), [("var7", "val7", []), ("var8", "val8", []), ("var9", "val9", [])])
        v, r = dsl.rem_all_variables("ctx2")
        self.assertTrue(v)
        self.assertEqual(r, ["var4", "var5", "var6"])
        self.assertEqual(var_fmt_helper(dsl.get_all_variables("ctx1")), [])
        self.assertEqual(var_fmt_helper(dsl.get_all_variables("ctx2")), [])
        self.assertEqual(var_fmt_helper(dsl.get_all_variables("ctx3")), [("var7", "val7", []), ("var8", "val8", []), ("var9", "val9", [])])
        v, r = dsl.rem_all_variables("ctx3")
        self.assertTrue(v)
        self.assertEqual(r, ["var7", "var8", "var9"])
        self.assertEqual(var_fmt_helper(dsl.get_all_variables("ctx1")), [])
        self.assertEqual(var_fmt_helper(dsl.get_all_variables("ctx2")), [])
        self.assertEqual(var_fmt_helper(dsl.get_all_variables("ctx3")), [])

    def testDslType20_TestRemContext1(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertFalse(dsl.rem_context(None)[0])

    def testDslType20_TestRemContext2(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertFalse(dsl.rem_context(dsl.root_context_id)[0])

    def testDslType20_TestRemContext3(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertFalse(dsl.rem_context("ctx1")[0])

    def testDslType20_TestRemContext4(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl.add_context("ctx1", None, None)[0])
        v, r = dsl.get_all_sub_contexts(None)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertEqual([x.get_name() for x in r], ["ctx1"])
        self.assertTrue(dsl.rem_context("ctx1")[0])
        v, r = dsl.get_all_sub_contexts(None)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)
        self.assertEqual([x.get_name() for x in r], [])

    def testDslType20_TestRemContext5(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl.add_context("ctx1", None, None)[0])
        self.assertTrue(dsl.add_context("ctx2", None, None)[0])
        v, r = dsl.get_all_sub_contexts(None)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertEqual([x.get_name() for x in r], ["ctx1", "ctx2"])
        self.assertTrue(dsl.rem_context("ctx1")[0])
        v, r = dsl.get_all_sub_contexts(None)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertEqual([x.get_name() for x in r], ["ctx2"])

    def testDslType20_TestRemContext6(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl.add_variable("ctx1", None, [])[0])
        v, r = dsl.get_all_variables(None)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertEqual([x.get_name() for x in r], ["ctx1"])
        v, r = dsl.get_all_sub_contexts(None)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)
        self.assertEqual([x.get_name() for x in r], [])
        self.assertFalse(dsl.rem_context("ctx1")[0])
        v, r = dsl.get_all_variables(None)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertEqual([x.get_name() for x in r], ["ctx1"])

    def testDslType20_TestRemContext7(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl.add_context("ctx1", None, None)[0])
        self.assertTrue(dsl.add_context("ctx2", None, "ctx1")[0])
        v, r = dsl.get_all_sub_contexts(None)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertEqual([x.get_name() for x in r], ["ctx1"])
        v, r = dsl.get_all_sub_contexts("ctx1")
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertEqual([x.get_name() for x in r], ["ctx2"])
        self.assertTrue(dsl.rem_context("ctx2")[0])
        v, r = dsl.get_all_sub_contexts("ctx1")
        self.assertTrue(v)
        self.assertEqual(len(r), 0)
        self.assertEqual([x.get_name() for x in r], [])

    def testDslType20_TestProduce1(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl_1.add_variable("var1", "val1", [])[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), [("var1", "val1", [])])
        self.assertEqual(dsl_1.produce(), "var1 = \"val1\"")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce2(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl_1.add_variable("var1", "val1", [])[0])
        self.assertTrue(dsl_1.add_variable("var2", "val2", [])[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), [("var1", "val1", []), ("var2", "val2", [])])
        self.assertEqual(dsl_1.produce(), "var1 = \"val1\"\nvar2 = \"val2\"")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce3(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl_1.add_variable("var1", "val1", [], "ctx1")[0])
        self.assertTrue(dsl_1.add_variable("var2", "val2", [])[0])
        self.assertTrue(dsl_1.add_variable("var1", "val1", [], "ctx2")[0])
        self.assertTrue(dsl_1.add_variable("var2", "val2", [], "ctx2")[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), [("var2", "val2", [])])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables("ctx1")), [("var1", "val1", [])])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables("ctx2")), [("var1", "val1", []), ("var2", "val2", [])])
        self.assertEqual(dsl_1.produce(), "[\n@ctx1\nvar1 = \"val1\"\n]\n\nvar2 = \"val2\"\n\n[\n@ctx2\nvar1 = \"val1\"\nvar2 = \"val2\"\n]")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce4(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl_1.add_variable("var1", "val\"1\"", [], "ctx1")[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables("ctx1")), [("var1", "val\"1\"", [])])
        self.assertEqual(dsl_1.produce(), "[\n@ctx1\nvar1 = \"val\\\"1\\\"\"\n]")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce5(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl_1.add_variable("var1", "val\"1\"", [("opt1", None)], "ctx1")[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables("ctx1")), [("var1", "val\"1\"", [("opt1", None)])])
        self.assertEqual(dsl_1.produce(), "[\n@ctx1\nvar1 {opt1} = \"val\\\"1\\\"\"\n]")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce6(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl_1.add_variable("var1", "val1", [("opt1", "val2")], "ctx1")[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables("ctx1")), [("var1", "val1", [("opt1", "val2")])])
        self.assertEqual(dsl_1.produce(), "[\n@ctx1\nvar1 {opt1: \"val2\"} = \"val1\"\n]")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce7(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl_1.add_variable("var1", "val\"1\"", [("opt1", "val\"2\"")], "ctx1")[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables("ctx1")), [("var1", "val\"1\"", [("opt1", "val\"2\"")])])
        self.assertEqual(dsl_1.produce(), "[\n@ctx1\nvar1 {opt1: \"val\\\"2\\\"\"} = \"val\\\"1\\\"\"\n]")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce8(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options = True))
        self.assertTrue(dsl_1.add_context("ctx1", [("opt1", "val2")], None)[0])
        self.assertTrue(dsl_1.add_variable("var1", "val1", [], "ctx1")[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables("ctx1")), [("var1", "val1", [("opt1", "val2")])])
        self.assertEqual(dsl_1.produce(), "[\n@ctx1 {opt1: \"val2\"}\nvar1 = \"val1\"\n]")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce9(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options = True))
        self.assertTrue(dsl_1.add_context("ctx1", [("opt1", "val1")], None)[0])
        self.assertTrue(dsl_1.add_variable("var1", "val2", [("opt1", "val3")], "ctx1")[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables("ctx1")), [("var1", "val2", [("opt1", "val3")])])
        self.assertEqual(dsl_1.produce(), "[\n@ctx1 {opt1: \"val1\"}\nvar1 {opt1: \"val3\"} = \"val2\"\n]")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce10(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes = False))
        self.assertTrue(dsl_1.add_context("ctx1", [("opt1", "val1")], None)[0])
        self.assertTrue(dsl_1.add_variable("var1", "val2", [("opt1", "val3")], "ctx1")[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables("ctx1")), [("var1", "val2", [("opt1", "val3")])])
        self.assertEqual(dsl_1.produce(), "[\n@ctx1 {opt1: \"val1\"}\nvar1 {opt1: \"val3\"} = \"val2\"\n]")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes = False))
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce11(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(var_decorator="* "))
        self.assertTrue(dsl_1.add_variable("var1", "val1", [])[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), [("var1", "val1", [])])
        self.assertEqual(dsl_1.produce(), "* var1 = \"val1\"")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(var_decorator="* "))
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce12(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes = False))
        self.assertTrue(dsl_1.add_context("ctx1", [("opt1", "val1"), ("opt2", "val2")], None)[0])
        self.assertTrue(dsl_1.add_variable("var1", "val4", [("opt1", "val3")], "ctx1")[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables("ctx1")), [("var1", "val4", [("opt1", "val3")])])
        self.assertEqual(dsl_1.produce(), "[\n@ctx1 {opt1: \"val1\" / opt2: \"val2\"}\nvar1 {opt1: \"val3\"} = \"val4\"\n]")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes = False))
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce13(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes = False))
        self.assertTrue(dsl_1.add_context("ctx1", None, None)[0])
        self.assertTrue(dsl_1.add_variable("var1", "", [], "ctx1")[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables("ctx1")), [("var1", "", [])])
        self.assertEqual(dsl_1.produce(), "[\n@ctx1\nvar1 = \"\"\n]")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes = False))
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce14(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes = False))
        self.assertTrue(dsl_1.add_context("ctx1", None, None)[0])
        self.assertTrue(dsl_1.add_variable("var1", "", [("opt1", None)], "ctx1")[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables("ctx1")), [("var1", "", [("opt1", None)])])
        self.assertEqual(dsl_1.produce(), "[\n@ctx1\nvar1 {opt1} = \"\"\n]")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes = False))
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce15(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes = False))
        self.assertTrue(dsl_1.add_context("ctx1", [("opt1", None)], None)[0])
        self.assertTrue(dsl_1.add_variable("var1", "", [], "ctx1")[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables("ctx1")), [("var1", "", [])])
        self.assertEqual(dsl_1.produce(), "[\n@ctx1 {opt1}\nvar1 = \"\"\n]")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes = False))
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce16(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes = False))
        self.assertTrue(dsl_1.add_context("ctx1", None, None)[0])
        self.assertTrue(dsl_1.add_variable("var1", "", [("opt1", "")], "ctx1")[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables("ctx1")), [("var1", "", [("opt1", "")])])
        self.assertEqual(dsl_1.produce(), "[\n@ctx1\nvar1 {opt1: \"\"} = \"\"\n]")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes = False))
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce17(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes = False))
        self.assertTrue(dsl_1.add_context("ctx1", [("opt1", "")], None)[0])
        self.assertTrue(dsl_1.add_variable("var1", "", [], "ctx1")[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables("ctx1")), [("var1", "", [])])
        self.assertEqual(dsl_1.produce(), "[\n@ctx1 {opt1: \"\"}\nvar1 = \"\"\n]")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes = False))
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce18(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes = False))
        self.assertTrue(dsl_1.add_context("ctx1", None, None)[0])
        self.assertTrue(dsl_1.add_variable("var1", "", [("opt1", None), ("opt2", None)], "ctx1")[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables("ctx1")), [("var1", "", [("opt1", None), ("opt2", None)])])
        self.assertEqual(dsl_1.produce(), "[\n@ctx1\nvar1 {opt1 / opt2} = \"\"\n]")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes = False))
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce19(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes = False))
        self.assertTrue(dsl_1.add_context("ctx1", None, None)[0])
        self.assertTrue(dsl_1.add_variable("var1", "", [("opt1", ""), ("opt2", "")], "ctx1")[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables("ctx1")), [("var1", "", [("opt1", ""), ("opt2", "")])])
        self.assertEqual(dsl_1.produce(), "[\n@ctx1\nvar1 {opt1: \"\" / opt2: \"\"} = \"\"\n]")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes = False))
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce20(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes = False))
        self.assertTrue(dsl_1.add_context("ctx1", None, None)[0])
        self.assertTrue(dsl_1.add_variable("var1", "", [("opt1", "abc"), ("opt2", "def")], "ctx1")[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables("ctx1")), [("var1", "", [("opt1", "abc"), ("opt2", "def")])])
        self.assertEqual(dsl_1.produce(), "[\n@ctx1\nvar1 {opt1: \"abc\" / opt2: \"def\"} = \"\"\n]")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes = False))
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce21(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes = False))
        self.assertTrue(dsl_1.add_context("ctx1", [("opt1", None), ("opt2", None)], None)[0])
        self.assertTrue(dsl_1.add_variable("var1", "", [], "ctx1")[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables("ctx1")), [("var1", "", [])])
        self.assertEqual(dsl_1.produce(), "[\n@ctx1 {opt1 / opt2}\nvar1 = \"\"\n]")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes = False))
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce22(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes = False))
        self.assertTrue(dsl_1.add_context("ctx1", [("opt1", ""), ("opt2", "")], None)[0])
        self.assertTrue(dsl_1.add_variable("var1", "", [], "ctx1")[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables("ctx1")), [("var1", "", [])])
        self.assertEqual(dsl_1.produce(), "[\n@ctx1 {opt1: \"\" / opt2: \"\"}\nvar1 = \"\"\n]")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes = False))
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce23(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes = False))
        self.assertTrue(dsl_1.add_context("ctx1", [("opt1", "abc"), ("opt2", "def")], None)[0])
        self.assertTrue(dsl_1.add_variable("var1", "", [], "ctx1")[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables("ctx1")), [("var1", "", [])])
        self.assertEqual(dsl_1.produce(), "[\n@ctx1 {opt1: \"abc\" / opt2: \"def\"}\nvar1 = \"\"\n]")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes = False))
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce24(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl_1.add_variable("var1", "#val1", [])[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), [("var1", "#val1", [])])
        self.assertEqual(dsl_1.produce(), "var1 = \"#val1\"")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce25(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl_1.add_variable("var1", "//val1", [])[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), [("var1", "//val1", [])])
        self.assertEqual(dsl_1.produce(), "var1 = \"//val1\"")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce26(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl_1.parse("var1")[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), [("var1", None, [])])
        self.assertEqual(dsl_1.produce(), "var1")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce27(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl_1.parse("var1 {opt1}")[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), [("var1", None, [("opt1", None)])])
        self.assertEqual(dsl_1.produce(), "var1 {opt1}")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce28(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl_1.parse("var1 {opt1 / opt2}")[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), [("var1", None, [("opt1", None), ("opt2", None)])])
        self.assertEqual(dsl_1.produce(), "var1 {opt1 / opt2}")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce29(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl_1.parse("var1 {opt1: \"val1\" / opt2}")[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), [("var1", None, [("opt1", "val1"), ("opt2", None)])])
        self.assertEqual(dsl_1.produce(), "var1 {opt1: \"val1\" / opt2}")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce30(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl_1.parse("var1 {opt1 / opt2: \"val1\"}")[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), [("var1", None, [("opt1", None), ("opt2", "val1")])])
        self.assertEqual(dsl_1.produce(), "var1 {opt1 / opt2: \"val1\"}")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce31(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl_1.parse("[\n@ctx\nvar1\n]")[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables("ctx")), [("var1", None, [])])
        self.assertEqual(dsl_1.produce(), "[\n@ctx\nvar1\n]")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce32(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl_1.parse("[\n@ctx\nvar1 {opt1}\n]")[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables("ctx")), [("var1", None, [("opt1", None)])])
        self.assertEqual(dsl_1.produce(), "[\n@ctx\nvar1 {opt1}\n]")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce33(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl_1.parse("[\n@ctx\nvar1 {opt1 / opt2}\n]")[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables("ctx")), [("var1", None, [("opt1", None), ("opt2", None)])])
        self.assertEqual(dsl_1.produce(), "[\n@ctx\nvar1 {opt1 / opt2}\n]")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce34(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl_1.parse("[\n@ctx\nvar1 {opt1: \"val1\" / opt2}\n]")[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables("ctx")), [("var1", None, [("opt1", "val1"), ("opt2", None)])])
        self.assertEqual(dsl_1.produce(), "[\n@ctx\nvar1 {opt1: \"val1\" / opt2}\n]")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce35(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl_1.parse("[\n@ctx\nvar1 {opt1 / opt2: \"val1\"}\n]")[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables("ctx")), [("var1", None, [("opt1", None), ("opt2", "val1")])])
        self.assertEqual(dsl_1.produce(), "[\n@ctx\nvar1 {opt1 / opt2: \"val1\"}\n]")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce36(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl_1.parse("[\n@고래\n돌고래 {상어}\n]")[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables("고래")), [("돌고래", None, [("상어", None)])])
        self.assertEqual(dsl_1.produce(), "[\n@고래\n돌고래 {상어}\n]")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce37(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl_1.parse("[\n@ctx1\nvar1 {opt1 / opt2: \"val1\"}\n[\n@ctx2\nvar2 {opt3 / opt4: \"val2\"}\n]\n]")[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables("ctx1")), [("var1", None, [("opt1", None), ("opt2", "val1")])])
        self.assertEqual(dsl_1.produce(), "[\n@ctx1\nvar1 {opt1 / opt2: \"val1\"}\n\n[\n@ctx2\nvar2 {opt3 / opt4: \"val2\"}\n]\n\n]")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce38(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl_1.parse("[\n@ctx1\nvar1 {opt1 / opt2: \"val1\"}\n[\nvar2 {opt3 / opt4: \"val2\"}\n]\n]")[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables("ctx1")), [("var1", None, [("opt1", None), ("opt2", "val1")]), ("var2", None, [("opt3", None), ("opt4", "val2")])])
        self.assertEqual(dsl_1.produce(), "[\n@ctx1\nvar1 {opt1 / opt2: \"val1\"}\nvar2 {opt3 / opt4: \"val2\"}\n]")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce39(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl_1.parse("var1 = ()")[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), [("var1", [], [])])
        self.assertEqual(dsl_1.produce(), "var1 = ()")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce40(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl_1.parse("var1 = (\"\")")[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), [("var1", [""], [])])
        self.assertEqual(dsl_1.produce(), "var1 = (\"\")")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce41(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl_1.parse("var1 = (\"\", \"\")")[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), [("var1", ["", ""], [])])
        self.assertEqual(dsl_1.produce(), "var1 = (\"\", \"\")")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce42(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl_1.parse("var1 = (\"abc\", \"def\")")[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), [("var1", ["abc", "def"], [])])
        self.assertEqual(dsl_1.produce(), "var1 = (\"abc\", \"def\")")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce43(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl_1.parse("var1 = (\"   abc   \", \"   def   \")")[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), [("var1", ["   abc   ", "   def   "], [])])
        self.assertEqual(dsl_1.produce(), "var1 = (\"   abc   \", \"   def   \")")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce44(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options = True))
        self.assertTrue(dsl_1.parse("[\n@ctx1 {opt1: () / opt2: ()}\nvar1 {opt3: () / opt4: ()}\n]")[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables("ctx1")), [("var1", None, [("opt1", []), ("opt2", []), ("opt3", []), ("opt4", [])])])
        self.assertEqual(dsl_1.produce(), "[\n@ctx1 {opt1: () / opt2: ()}\nvar1 {opt3: () / opt4: ()}\n]")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce45(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options = True))
        self.assertTrue(dsl_1.parse("[\n@ctx1 {opt1: (\"\") / opt2: (\"\")}\nvar1 {opt3: (\"\") / opt4: (\"\")}\n]")[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables("ctx1")), [("var1", None, [("opt1", [""]), ("opt2", [""]), ("opt3", [""]), ("opt4", [""])])])
        self.assertEqual(dsl_1.produce(), "[\n@ctx1 {opt1: (\"\") / opt2: (\"\")}\nvar1 {opt3: (\"\") / opt4: (\"\")}\n]")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce46(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options = True))
        self.assertTrue(dsl_1.parse("[\n@ctx1 {opt1: (\"\", \"\") / opt2: (\"\", \"\")}\nvar1 {opt3: (\"\", \"\") / opt4: (\"\", \"\")}\n]")[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables("ctx1")), [("var1", None, [("opt1", ["", ""]), ("opt2", ["", ""]), ("opt3", ["", ""]), ("opt4", ["", ""])])])
        self.assertEqual(dsl_1.produce(), "[\n@ctx1 {opt1: (\"\", \"\") / opt2: (\"\", \"\")}\nvar1 {opt3: (\"\", \"\") / opt4: (\"\", \"\")}\n]")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce47(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options = True))
        self.assertTrue(dsl_1.parse("[\n@ctx1 {opt1: (\"abc\", \"def\") / opt2: (\"xyz\", \"123\")}\nvar1 {opt3: (\"first\", \"second\") / opt4: (\"third\", \"fourth\")}\n]")[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables("ctx1")), [("var1", None, [("opt1", ["abc", "def"]), ("opt2", ["xyz", "123"]), ("opt3", ["first", "second"]), ("opt4", ["third", "fourth"])])])
        self.assertEqual(dsl_1.produce(), "[\n@ctx1 {opt1: (\"abc\", \"def\") / opt2: (\"xyz\", \"123\")}\nvar1 {opt3: (\"first\", \"second\") / opt4: (\"third\", \"fourth\")}\n]")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce48(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options = True))
        self.assertTrue(dsl_1.parse("[\n@ctx1 {opt1: (\"   abc   \", \"   def   \") / opt2: (\"   xyz   \", \"   123   \")}\nvar1 {opt3: (\"   first   \", \"   second   \") / opt4: (\"   third   \", \"   fourth   \")}\n]")[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables("ctx1")), [("var1", None, [("opt1", ["   abc   ", "   def   "]), ("opt2", ["   xyz   ", "   123   "]), ("opt3", ["   first   ", "   second   "]), ("opt4", ["   third   ", "   fourth   "])])])
        self.assertEqual(dsl_1.produce(), "[\n@ctx1 {opt1: (\"   abc   \", \"   def   \") / opt2: (\"   xyz   \", \"   123   \")}\nvar1 {opt3: (\"   first   \", \"   second   \") / opt4: (\"   third   \", \"   fourth   \")}\n]")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestGetContextOptions1(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl.add_context("ctx1", [("opt1", "val1")], None)[0])
        self.assertEqual(opt_fmt_helper(dsl.get_context_options("ctx1")), [("opt1", "val1")])

    def testDslType20_TestGetContextOptions2(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl.add_context("ctx1", [("opt1", "val1"), ("opt2", "val2")], None)[0])
        self.assertEqual(opt_fmt_helper(dsl.get_context_options("ctx1")), [("opt1", "val1"), ("opt2", "val2")])

    def testDslType20_TestGetContextOptions3(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl.add_context("ctx1", [("opt1", "val1")], None)[0])
        v, r = dsl.get_context_options("ctx1")
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertNotEqual(r[0], dsl.data.entries[0].options[0])

    def testDslType20_TestFindContext1(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl.add_context("ctx1", [("opt1", "val1")], None)[0])
        v, r = dsl._find_context("ctx1", None, None)
        self.assertTrue(v)
        self.assertTrue(r)

    def testDslType20_TestFindContext2(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl.add_context("ctx1", [("opt1", "val1")], None)[0])
        v, r = dsl._find_context("no-ctx", None, None)
        self.assertTrue(v)
        self.assertFalse(r)

    def testDslType20_TestFindContext3(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl.add_context("ctx1", [("opt1", "val1")], None)[0])
        v, r = dsl._find_context("ctx1", find_context_callback_positive, "dummy-data")
        self.assertTrue(v)
        self.assertTrue(r)

    def testDslType20_TestFindContext4(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl.add_context("ctx1", [("opt1", "val1")], None)[0])
        v, r = dsl._find_context("ctx1", find_context_callback_negative, "dummy-data")
        self.assertFalse(v)
        self.assertEqual(r, "Test error")

    def testDslType20_TestFindContext5(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl.add_context("ctx1", None, None)[0])
        self.assertTrue(dsl.add_context("ctx2", None, None)[0])
        self.assertTrue(dsl.add_context("ctx3", None, None)[0])

        self.assertTrue(dsl.add_context("ctx4", None, "ctx1")[0])
        self.assertTrue(dsl.add_context("ctx5", None, "ctx1")[0])

        self.assertTrue(dsl.add_context("ctx6", None, "ctx2")[0])
        self.assertTrue(dsl.add_context("ctx7", None, "ctx2")[0])

        self.assertTrue(dsl.add_context("ctx8", None, "ctx3")[0])
        self.assertTrue(dsl.add_context("ctx9", None, "ctx3")[0])

        self.assertTrue(dsl.add_context("ctx10", None, "ctx4")[0])
        self.assertTrue(dsl.add_context("ctx11", None, "ctx5")[0])

        names_chain = []
        v, r = dsl._find_context("ctx10", find_context_callback_report_chain, names_chain)
        self.assertTrue(v)
        self.assertTrue(r)
        self.assertEqual(names_chain, ["ctx10", "ctx4", "ctx1", "_DSL_TYPE20_RESERVED_INTERNAL_MASTER_ROOT_CONTEXT_"])

        names_chain.clear()
        v, r = dsl._find_context("ctx11", find_context_callback_report_chain, names_chain)
        self.assertTrue(v)
        self.assertTrue(r)
        self.assertEqual(names_chain, ["ctx11", "ctx5", "ctx1", "_DSL_TYPE20_RESERVED_INTERNAL_MASTER_ROOT_CONTEXT_"])

        names_chain.clear()
        v, r = dsl._find_context("ctx9", find_context_callback_report_chain, names_chain)
        self.assertTrue(v)
        self.assertTrue(r)
        self.assertEqual(names_chain, ["ctx9", "ctx3", "_DSL_TYPE20_RESERVED_INTERNAL_MASTER_ROOT_CONTEXT_"])

        names_chain.clear()
        v, r = dsl._find_context("ctx6", find_context_callback_report_chain, names_chain)
        self.assertTrue(v)
        self.assertTrue(r)
        self.assertEqual(names_chain, ["ctx6", "ctx2", "_DSL_TYPE20_RESERVED_INTERNAL_MASTER_ROOT_CONTEXT_"])

    def testDslType20_TestProduceValues1(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertEqual(dsl._produce_values(""), "\"\"")

    def testDslType20_TestProduceValues2(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertEqual(dsl._produce_values("abc"), "\"abc\"")

    def testDslType20_TestProduceValues3(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertEqual(dsl._produce_values("a\"c"), "\"a\\\"c\"")

    def testDslType20_TestProduceValues4(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertEqual(dsl._produce_values([]), "")

    def testDslType20_TestProduceValues5(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertEqual(dsl._produce_values([""]), "\"\"")

    def testDslType20_TestProduceValues6(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertEqual(dsl._produce_values(["abc"]), "\"abc\"")

    def testDslType20_TestProduceValues7(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertEqual(dsl._produce_values(["abc", "def"]), "\"abc\", \"def\"")

    def testDslType20_TestProduceValues8(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertEqual(dsl._produce_values(["abc", "def", "xyz", "123"]), "\"abc\", \"def\", \"xyz\", \"123\"")

    def testDslType20_TestParseValueEnd1(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl._parse_value_end("var1")
        self.assertTrue(v)
        self.assertEqual(r, ("var1", None))

    def testDslType20_TestParseValueEnd2(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl._parse_value_end("var1 = \"\"")
        self.assertTrue(v)
        self.assertEqual(r, ("var1", ""))

    def testDslType20_TestParseValueEnd3(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl._parse_value_end("var1 = \"abc\"")
        self.assertTrue(v)
        self.assertEqual(r, ("var1", "abc"))

    def testDslType20_TestParseValueEnd4(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl._parse_value_end("var1 = ()")
        self.assertTrue(v)
        self.assertEqual(r, ("var1", []))

    def testDslType20_TestParseValueEnd5(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl._parse_value_end("var1 = (\"\")")
        self.assertTrue(v)
        self.assertEqual(r, ("var1", [""]))

    def testDslType20_TestParseValueEnd6(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl._parse_value_end("var1 = (\"abc\")")
        self.assertTrue(v)
        self.assertEqual(r, ("var1", ["abc"]))

    def testDslType20_TestParseValueEnd7(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl._parse_value_end("var1 = (\"a\\\"c\")")
        self.assertTrue(v)
        self.assertEqual(r, ("var1", ["a\"c"]))

    def testDslType20_TestParseValueEnd8(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl._parse_value_end("var1 = (\"\", \"\")")
        self.assertTrue(v)
        self.assertEqual(r, ("var1", ["", ""]))

    def testDslType20_TestParseValueEnd9(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl._parse_value_end("var1 = (\"abc\", \"def\")")
        self.assertTrue(v)
        self.assertEqual(r, ("var1", ["abc", "def"]))

    def testDslType20_TestParseValueEnd10(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl._parse_value_end("var1 = (\"a\\\"c\", \"d\\\"f\")")
        self.assertTrue(v)
        self.assertEqual(r, ("var1", ["a\"c", "d\"f"]))

    def testDslType20_TestParseValueEnd11(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl._parse_value_end("var1 = (\"abc\", )")
        self.assertFalse(v)

    def testDslType20_TestParseValueEnd12(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl._parse_value_end("var1 = (\"   abc  \", \"  def   \")")
        self.assertTrue(v)
        self.assertEqual(r, ("var1", ["   abc  ", "  def   "]))

    def testDslType20_TestParseValue1(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl._parse_value("opt1: \"\"}", "\"\"}")
        self.assertTrue(v)
        self.assertEqual(r[0], "}")
        self.assertEqual(r[1], "")

    def testDslType20_TestParseValue2(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl._parse_value("opt1: \"abc\"}", "\"abc\"}")
        self.assertTrue(v)
        self.assertEqual(r[0], "}")
        self.assertEqual(r[1], "abc")

    def testDslType20_TestParseValue3(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl._parse_value("opt1: \"a\\\"c\"}", "\"a\\\"c\"}")
        self.assertTrue(v)
        self.assertEqual(r[0], "}")
        self.assertEqual(r[1], "a\"c")

    def testDslType20_TestParseValue4(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl._parse_value("opt1: ()}", "()}")
        self.assertTrue(v)
        self.assertEqual(r[0], "}")
        self.assertEqual(r[1], [])

    def testDslType20_TestParseValue5(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl._parse_value("opt1: (\"\")}", "(\"\")}")
        self.assertTrue(v)
        self.assertEqual(r[0], "}")
        self.assertEqual(r[1], [""])

    def testDslType20_TestParseValue6(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl._parse_value("opt1: (\"abc\")}", "(\"abc\")}")
        self.assertTrue(v)
        self.assertEqual(r[0], "}")
        self.assertEqual(r[1], ["abc"])

    def testDslType20_TestParseValue7(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl._parse_value("opt1: (\"\", \"\")}", "(\"\", \"\")}")
        self.assertTrue(v)
        self.assertEqual(r[0], "}")
        self.assertEqual(r[1], ["", ""])

    def testDslType20_TestParseValue8(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl._parse_value("opt1: (\"abc\", \"def\")}", "(\"abc\", \"def\")}")
        self.assertTrue(v)
        self.assertEqual(r[0], "}")
        self.assertEqual(r[1], ["abc", "def"])

    def testDslType20_TestParseValue9(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl._parse_value("opt1: (\"abc\", \"def\",)}", "(\"abc\", \"def\",)}")
        self.assertFalse(v)

    def testDslType20_TestParseValue10(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl._parse_value("opt1: (\"   abc  \", \"  def   \")}", "(\"   abc  \", \"  def   \")}")
        self.assertTrue(v)
        self.assertEqual(r[0], "}")
        self.assertEqual(r[1], ["   abc  ", "  def   "])

if __name__ == "__main__":
    unittest.main()
