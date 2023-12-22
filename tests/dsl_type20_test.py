#!/usr/bin/env python3

import os
import shutil
import unittest

import create_and_write_file
import mvtools_test_fixture
import path_utils
import mvtools_envvars

import dsl_type20
import mvtools_exception

def getcontents(filename):
    if not os.path.exists(filename):
        return None
    contents = ""
    with open(filename) as f:
        contents = f.read()
    return contents

def var_fmt_helper(var_list):
    v, r = var_list
    if not v:
        raise mvtools_exception.mvtools_exception("Failed test")
    return [(x.get_name(), x.get_value(), [(y.get_name(), y.get_value()) for y in x.get_options()]) for x in r]

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
        self.contents_cfg_test_ok_2 += "var5 {r1: \"\" / r1} = \"repeated1\"\n"
        self.contents_cfg_test_ok_2 += "var5 {r2 / r2} = \"repeated2\"\n"
        self.cfg_test_ok_2 = path_utils.concat_path(self.test_dir, "test_ok_2.t20")

        self.contents_cfg_test_ok_3 = "var1 = \"val1\"\n"
        self.contents_cfg_test_ok_3 += "var2 = \"val2\"\n"
        self.cfg_test_ok_3 = path_utils.concat_path(self.test_dir, "test_ok_3.t20")

        self.contents_cfg_test_ok_4 = ("var1 = \"%s\"\n") % self.reserved_test_env_var_1
        self.contents_cfg_test_ok_4 += ("var2 {opt1: \"%s\"} = \"val1\"\n") % self.reserved_test_env_var_2
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
        contents = getcontents(filename)
        if contents is None:
            self.fail("Unable to open and read file [%s]" % filename)

        dsl = dsl_type20.DSLType20(_dsl_t20_opts)
        v, r = dsl.parse(contents)
        return v

    def testSanitizeLine(self):
        self.assertEqual(dsl_type20.sanitize_line(""), "")
        self.assertEqual(dsl_type20.sanitize_line("abc"), "abc")
        self.assertEqual(dsl_type20.sanitize_line("#abc"), "")
        self.assertEqual(dsl_type20.sanitize_line("abc//def"), "abc")
        self.assertEqual(dsl_type20.sanitize_line("//abc def"), "")
        self.assertEqual(dsl_type20.sanitize_line("abc#def"), "abc")
        self.assertEqual(dsl_type20.sanitize_line("   abc   "), "abc")
        self.assertEqual(dsl_type20.sanitize_line(" #   abc   "), "")
        self.assertEqual(dsl_type20.sanitize_line("   abc   #"), "abc")
        self.assertEqual(dsl_type20.sanitize_line("   abc   // def   # xyz"), "abc")
        self.assertEqual(dsl_type20.sanitize_line("   abc   # def   // xyz"), "abc")
        self.assertEqual(dsl_type20.sanitize_line("   abc   \"#\" def   // xyz"), "abc   \"#\" def")
        self.assertEqual(dsl_type20.sanitize_line("   abc   \"//\" def   // xyz"), "abc   \"//\" def")

    def testValidateName(self):
        self.assertFalse(dsl_type20.validate_name(None))
        self.assertFalse(dsl_type20.validate_name([]))
        self.assertFalse(dsl_type20.validate_name(()))
        self.assertFalse(dsl_type20.validate_name("name\x0a"))
        self.assertFalse(dsl_type20.validate_name("name\x00"))
        self.assertFalse(dsl_type20.validate_name("name\x20"))
        self.assertFalse(dsl_type20.validate_name("name\x09"))
        self.assertFalse(dsl_type20.validate_name(""))
        self.assertTrue(dsl_type20.validate_name("a"))
        self.assertTrue(dsl_type20.validate_name("거물사냥꾼"))

    def testValidateValue(self):
        self.assertTrue(dsl_type20.validate_value(None))
        self.assertFalse(dsl_type20.validate_value([]))
        self.assertFalse(dsl_type20.validate_value(()))
        self.assertFalse(dsl_type20.validate_value("value\x0a"))
        self.assertFalse(dsl_type20.validate_value("value\x00"))
        self.assertTrue(dsl_type20.validate_value("name\x20"))
        self.assertTrue(dsl_type20.validate_value("name\x09"))
        self.assertTrue(dsl_type20.validate_value("a"))
        self.assertTrue(dsl_type20.validate_value("거물사냥꾼"))

    def testValidateVariable(self):
        self.assertTrue(dsl_type20.validate_variable("a", "a")[0])
        self.assertTrue(dsl_type20.validate_variable("거물사냥꾼", "거물사냥꾼")[0])
        self.assertFalse(dsl_type20.validate_variable("", "a")[0])
        self.assertFalse(dsl_type20.validate_variable(None, "a")[0])
        self.assertFalse(dsl_type20.validate_variable([], "a")[0])
        self.assertFalse(dsl_type20.validate_variable((), "a")[0])
        self.assertTrue(dsl_type20.validate_variable("a", None)[0])
        self.assertTrue(dsl_type20.validate_variable("a", "")[0])
        self.assertFalse(dsl_type20.validate_variable("a", [])[0])
        self.assertFalse(dsl_type20.validate_variable("a", ())[0])

    def testValidateOption(self):
        self.assertTrue(dsl_type20.validate_option("a", "a")[0])
        self.assertTrue(dsl_type20.validate_option("거물사냥꾼", "거물사냥꾼")[0])
        self.assertFalse(dsl_type20.validate_option("", "a")[0])
        self.assertFalse(dsl_type20.validate_option(None, "a")[0])
        self.assertFalse(dsl_type20.validate_option([], "a")[0])
        self.assertFalse(dsl_type20.validate_option((), "a")[0])
        self.assertTrue(dsl_type20.validate_option("a", None)[0])
        self.assertTrue(dsl_type20.validate_option("a", "")[0])
        self.assertFalse(dsl_type20.validate_option("a", [])[0])
        self.assertFalse(dsl_type20.validate_option("a", ())[0])

    def testValidateOptionsList(self):
        self.assertTrue(dsl_type20.validate_options_list( [  ] )[0])
        self.assertFalse(dsl_type20.validate_options_list( [ [1] ] )[0])
        self.assertFalse(dsl_type20.validate_options_list( [ [1, 2] ] )[0])
        self.assertFalse(dsl_type20.validate_options_list( [ (1) ] )[0])
        self.assertFalse(dsl_type20.validate_options_list( [ (1, 2) ] )[0])
        self.assertFalse(dsl_type20.validate_options_list( [ ("a", 1) ] )[0])
        self.assertFalse(dsl_type20.validate_options_list( [ ("", "a") ] )[0])
        self.assertFalse(dsl_type20.validate_options_list( [ (None, "a") ] )[0])
        self.assertTrue(dsl_type20.validate_options_list( [ ("a", "a") ] )[0])
        self.assertFalse(dsl_type20.validate_options_list( [ ("a", "a"), ("a") ] )[0])
        self.assertTrue(dsl_type20.validate_options_list( [ ("a", "a"), ("b", "b") ] )[0])
        self.assertFalse(dsl_type20.validate_options_list( [ ("a", "a"), (dsl_type20.NEWLINE, "b") ] )[0])
        self.assertFalse(dsl_type20.validate_options_list( [ ("a", "a"), (dsl_type20.NULL, "b") ] )[0])
        self.assertFalse(dsl_type20.validate_options_list( [ ("a", "a"), (dsl_type20.SPACE, "b") ] )[0])
        self.assertFalse(dsl_type20.validate_options_list( [ ("a", "a"), (dsl_type20.HTAB, "b") ] )[0])
        self.assertTrue(dsl_type20.validate_options_list( [ ("a", None) ] )[0])
        self.assertFalse(dsl_type20.validate_options_list( [ ("a", "a"), ("a", "b") ] )[0])

    def testValidateContext(self):
        self.assertFalse(dsl_type20.validate_context(None)[0])
        self.assertFalse(dsl_type20.validate_context([])[0])
        self.assertFalse(dsl_type20.validate_context(())[0])
        self.assertFalse(dsl_type20.validate_context("name\x0a")[0])
        self.assertFalse(dsl_type20.validate_context("name\x00")[0])
        self.assertFalse(dsl_type20.validate_context("name\x20")[0])
        self.assertFalse(dsl_type20.validate_context("name\x09")[0])
        self.assertFalse(dsl_type20.validate_context("")[0])
        self.assertTrue(dsl_type20.validate_context("a")[0])
        self.assertTrue(dsl_type20.validate_context("거물사냥꾼")[0])

    def testMakeObjOptList1(self):
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

    def testMakeObjOptList2(self):
        v, r = dsl_type20.make_obj_opt_list(dsl_type20.DSLType20_Config(), [ ("a", "b"), ("a", "b") ])
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

    def testInheritOptions1(self):
        v, r = dsl_type20.make_obj_opt_list(dsl_type20.DSLType20_Config(), [ ("a", "b") ])
        self.assertTrue(v)
        parent_opts = r
        v, r = dsl_type20.make_obj_opt_list(dsl_type20.DSLType20_Config(), [ ("1", "2") ])
        self.assertTrue(v)
        new_opts = r
        final_opts = dsl_type20.inherit_options(parent_opts, new_opts)
        self.assertEqual( [ (x.get_name(), x.get_value()) for x in final_opts ], [ ("a", "b"), ("1", "2") ] )

    def testInheritOptions2(self):
        v, r = dsl_type20.make_obj_opt_list(dsl_type20.DSLType20_Config(), [ ("a", "b") ])
        self.assertTrue(v)
        parent_opts = r
        v, r = dsl_type20.make_obj_opt_list(dsl_type20.DSLType20_Config(), [ ("a", "2") ])
        self.assertTrue(v)
        new_opts = r
        final_opts = dsl_type20.inherit_options(parent_opts, new_opts)
        self.assertEqual( [ (x.get_name(), x.get_value()) for x in final_opts ], [ ("a", "2") ] )

    def testInheritOptions3(self):
        v, r = dsl_type20.make_obj_opt_list(dsl_type20.DSLType20_Config(), [ ("a", None) ])
        self.assertTrue(v)
        parent_opts = r
        v, r = dsl_type20.make_obj_opt_list(dsl_type20.DSLType20_Config(), [ ("a", "2") ])
        self.assertTrue(v)
        new_opts = r
        final_opts = dsl_type20.inherit_options(parent_opts, new_opts)
        self.assertEqual( [ (x.get_name(), x.get_value()) for x in final_opts ], [ ("a", "2") ] )

    def testInheritOptions4(self):
        v, r = dsl_type20.make_obj_opt_list(dsl_type20.DSLType20_Config(), [ ("a", "b") ])
        self.assertTrue(v)
        parent_opts = r
        v, r = dsl_type20.make_obj_opt_list(dsl_type20.DSLType20_Config(), [ ("a", None) ])
        self.assertTrue(v)
        new_opts = r
        final_opts = dsl_type20.inherit_options(parent_opts, new_opts)
        self.assertEqual( [ (x.get_name(), x.get_value()) for x in final_opts ], [ ("a", None) ] )

    def testInheritOptions5(self):
        v, r = dsl_type20.make_obj_opt_list(dsl_type20.DSLType20_Config(), [ ("a", None), ("1", "2") ])
        self.assertTrue(v)
        parent_opts = r
        v, r = dsl_type20.make_obj_opt_list(dsl_type20.DSLType20_Config(), [ ("a", None) ])
        self.assertTrue(v)
        new_opts = r
        final_opts = dsl_type20.inherit_options(parent_opts, new_opts)
        self.assertEqual( [ (x.get_name(), x.get_value()) for x in final_opts ], [ ("1", "2") ] )

    def testInheritOptions6(self):
        v, r = dsl_type20.make_obj_opt_list(dsl_type20.DSLType20_Config(), [ ("a", None) ])
        self.assertTrue(v)
        parent_opts = r
        v, r = dsl_type20.make_obj_opt_list(dsl_type20.DSLType20_Config(), [ ("a", None), ("1", "2") ])
        self.assertTrue(v)
        new_opts = r
        final_opts = dsl_type20.inherit_options(parent_opts, new_opts)
        self.assertEqual( [ (x.get_name(), x.get_value()) for x in final_opts ], [ ("1", "2") ] )

    def testInheritOptions7(self):
        v, r = dsl_type20.make_obj_opt_list(dsl_type20.DSLType20_Config(), [ ("a", "") ])
        self.assertTrue(v)
        parent_opts = r
        v, r = dsl_type20.make_obj_opt_list(dsl_type20.DSLType20_Config(), [ ("a", ""), ("1", "2") ])
        self.assertTrue(v)
        new_opts = r
        final_opts = dsl_type20.inherit_options(parent_opts, new_opts)
        self.assertEqual( [ (x.get_name(), x.get_value()) for x in final_opts ], [ ("a", ""), ("1", "2") ] )

    def testInheritOptions8(self):
        v, r = dsl_type20.make_obj_opt_list(dsl_type20.DSLType20_Config(), [ ("a", "b"), ("c", "d") ])
        self.assertTrue(v)
        parent_opts = r
        v, r = dsl_type20.make_obj_opt_list(dsl_type20.DSLType20_Config(), [ ("1", "2"), ("3", "4") ])
        self.assertTrue(v)
        new_opts = r
        final_opts = dsl_type20.inherit_options(parent_opts, new_opts)
        self.assertEqual( [ (x.get_name(), x.get_value()) for x in final_opts ], [ ("a", "b"), ("c", "d"), ("1", "2"), ("3", "4") ] )

    def testInheritOptions9(self):
        v, r = dsl_type20.make_obj_opt_list(dsl_type20.DSLType20_Config(), [ ("a", "b"), ("c", "d") ])
        self.assertTrue(v)
        parent_opts = r
        v, r = dsl_type20.make_obj_opt_list(dsl_type20.DSLType20_Config(), [ ("a", "b"), ("c", "d") ])
        self.assertTrue(v)
        new_opts = r
        final_opts = dsl_type20.inherit_options(parent_opts, new_opts)
        self.assertEqual( [ (x.get_name(), x.get_value()) for x in final_opts ], [ ("a", "b"), ("c", "d") ] )

    def testDSLType20_Variable1(self):
        var_inst = dsl_type20.DSLType20_Variable(dsl_type20.DSLType20_Config(), "a", None, [])
        self.assertTrue(isinstance(var_inst, dsl_type20.DSLType20_Variable))
        self.assertTrue(isinstance(var_inst.configs, dsl_type20.DSLType20_Config))
        self.assertEqual(var_inst.get_type(), dsl_type20.DSLTYPE20_ENTRY_TYPE_VAR)
        self.assertEqual(var_inst.name, "a")
        self.assertEqual(var_inst.get_name(), "a")
        self.assertEqual(var_inst.value, None)
        self.assertEqual(var_inst.get_value(), None)
        self.assertEqual(var_inst.options, [])
        self.assertEqual(var_inst.get_options(), [])

    def testDSLType20_Variable2(self):
        ex_flag = False
        try:
            var_inst = dsl_type20.DSLType20_Variable(dsl_type20.DSLType20_Config(), "", None, [])
        except BaseException as ex:
            ex_flag = isinstance(ex, mvtools_exception.mvtools_exception)
        self.assertTrue(ex_flag)

    def testDSLType20_Option1(self):
        obj_inst = dsl_type20.DSLType20_Option(dsl_type20.DSLType20_Config(), "a", None)
        self.assertTrue(isinstance(obj_inst, dsl_type20.DSLType20_Option))
        self.assertTrue(isinstance(obj_inst.configs, dsl_type20.DSLType20_Config))
        self.assertEqual(obj_inst.get_type(), dsl_type20.DSLTYPE20_ENTRY_TYPE_OPT)
        self.assertEqual(obj_inst.name, "a")
        self.assertEqual(obj_inst.get_name(), "a")
        self.assertEqual(obj_inst.value, None)
        self.assertEqual(obj_inst.get_value(), None)

    def testDSLType20_Option2(self):
        ex_flag = False
        try:
            obj_inst = dsl_type20.DSLType20_Option(dsl_type20.DSLType20_Config(), "", None)
        except BaseException as ex:
            ex_flag = isinstance(ex, mvtools_exception.mvtools_exception)
        self.assertTrue(ex_flag)

    def testDSLType20_Context1(self):
        ctx_inst = dsl_type20.DSLType20_Context(None, "a", [])
        self.assertTrue(isinstance(ctx_inst, dsl_type20.DSLType20_Context))
        self.assertEqual(ctx_inst.get_type(), dsl_type20.DSLTYPE20_ENTRY_TYPE_CTX)
        self.assertEqual(ctx_inst.ptr_parent, None)
        self.assertEqual(ctx_inst.get_ptr_parent(), None)
        self.assertEqual(ctx_inst.name, "a")
        self.assertEqual(ctx_inst.get_name(), "a")
        self.assertEqual(ctx_inst.options, [])
        self.assertEqual(ctx_inst.get_options(), [])
        self.assertEqual(ctx_inst.entries, [])

    def testDSLType20_Context2(self):
        ex_flag = False
        try:
            ctx_inst = dsl_type20.DSLType20_Context(None, "", [])
        except BaseException as ex:
            ex_flag = isinstance(ex, mvtools_exception.mvtools_exception)
        self.assertTrue(ex_flag)

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

        blanksub = path_utils.concat_path(self.test_dir, " ")
        self.assertFalse(os.path.exists(blanksub))
        os.mkdir(blanksub)
        self.assertTrue(os.path.exists(blanksub))

        blankfile = path_utils.concat_path(blanksub, " ")
        self.assertFalse(os.path.exists(blankfile))
        create_and_write_file.create_file_contents(blankfile, self.contents_cfg_test_ok_1)
        self.assertTrue(os.path.exists(blankfile))

        self.assertTrue(self.parse_test_aux(blankfile, dsl_type20.DSLType20_Config()))

    def testDslType20_GetVariables1(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse(self.contents_cfg_test_ok_1)
        self.assertTrue(v)

        self.assertEqual(var_fmt_helper(dsl.get_variables("var0")), [])
        self.assertEqual(dsl.get_variables("var1"), [("var1", "val1", [])])
        self.assertEqual(dsl.get_variables("var2"), [("var2", "val2", [("opt1", None)])])
        self.assertEqual(dsl.get_variables("var3"), [("var3", "val4", [("opt2", "val3")])])
        self.assertEqual(dsl.get_variables("var4"), [("var4", "val7", [("opt3", "val5"), ("opt4", "val6")])])
        self.assertEqual(dsl.get_variables("var5"), [("var5", "val10", [("opt5", None), ("opt6", "val8"), ("opt7", "val9")])])
        self.assertEqual(dsl.get_variables("var6"), [])

        self.assertTrue(dsl_type20.hasopt_var(dsl.get_variables("var2")[0], "opt1"))
        self.assertTrue(dsl_type20.hasopt_var(dsl.get_variables("var3")[0], "opt2"))
        self.assertFalse(dsl_type20.hasopt_var(dsl.get_variables("var3")[0], "opt3"))

        self.assertTrue(dsl_type20.hasopt_opts(dsl.get_variables("var2")[0][2], "opt1"))
        self.assertTrue(dsl_type20.hasopt_opts(dsl.get_variables("var3")[0][2], "opt2"))

        #self.assertEqual(dsl_type20.getopts(dsl.get_variables("var2")[0], "opt1"), [("opt1", None)]) # mvtodo

    def testDslType20_GetVariables2(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse(self.contents_cfg_test_ok_2)
        self.assertTrue(v)

        self.assertEqual(dsl.get_variables("var0"), [])
        self.assertEqual(dsl.get_variables("var1"), [("var1", "val1", [])])
        self.assertEqual(dsl.get_variables("var2"), [("var2", "a/path/valid1", [])])
        self.assertEqual(dsl.get_variables("var3"), [("var3", "a/path/valid3", [("opt1", None), ("opt2", "a/path/valid2")])])
        self.assertEqual(dsl.get_variables("var4"), [("var4", "$SOME_ENV_VAR", [])])
        self.assertEqual(dsl.get_variables("var5"), [("var5", "repeated1", [("r1", ""), ("r1", None)]), ("var5", "repeated2", [("r2", None), ("r2", None)])])
        self.assertEqual(dsl.get_variables("var6"), [])

        #self.assertEqual(dsl_type20.getopts(dsl.get_variables("var5")[0], "r1"), [("r1", ""), ("r1", None)]) # mvtodo
        #self.assertEqual(dsl_type20.getopts(dsl.get_variables("var5")[1], "r1"), []) # mvtodo
        #self.assertEqual(dsl_type20.getopts(dsl.get_variables("var5")[1], "r2"), [("r2", None), ("r2", None)]) # mvtodo

    def testDslType20_GetVariables3(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse(self.contents_cfg_test_ok_3)
        self.assertTrue(v)

        self.assertEqual(dsl.get_all_variables(), [("var1", "val1", []), ("var2", "val2", [])])

    def testDslType20_GetVariables4(self):

        os.environ[ (self.reserved_test_env_var_1[1:]) ] = "test-value-1"
        os.environ[ (self.reserved_test_env_var_2[1:]) ] = "test-value-2"

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(True, True))
        v, r = dsl.parse(self.contents_cfg_test_ok_4)

        self.assertTrue(v)
        self.assertEqual(dsl.get_all_variables(), [("var1", "test-value-1", []), ("var2", "val1", [("opt1","test-value-2")]), ("var3", path_utils.concat_path(os.path.expanduser("/tmp/folder")), [])])

    def testDslType20_GetVariables5(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl.add_context(None, "ctx1", [("opt1", "val1")])[0])
        self.assertTrue(dsl.add_variable("var1", "val2", [ ], "ctx1" )[0])
        self.assertEqual(dsl.get_all_variables("ctx1"), [("var1", "val2", [])])

    def testDslType20_GetVariables6(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options=True))
        self.assertTrue(dsl.add_context(None, "ctx1", [("opt1", "val1")])[0])
        self.assertTrue(dsl.add_variable("var1", "val2", [ ], "ctx1" )[0])
        self.assertEqual(dsl.get_all_variables("ctx1"), [("var1", "val2", [("opt1", "val1")])])

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

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options=True))
        v, r = dsl.parse("[\n@ctx {opt1}\nvar1 {opt1}\n]")
        self.assertTrue(v)

        self.assertEqual(var_fmt_helper(dsl.get_all_variables("ctx")), [("var1", None, [])])

    def testDslType20_TestParseDecoratedVar1(self):

        decorated_var = "* var1 {opt1} = \"val1\""

        dsl1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl1.parse(decorated_var)
        self.assertFalse(v)

        dsl2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(variable_decorator = "* "))
        v, r = dsl2.parse(decorated_var)
        self.assertTrue(v)

        self.assertEqual(var_fmt_helper(dsl2.get_all_variables()), [("var1", "val1", [("opt1", None)])])

    def testDslType20_TestParseDecoratedVar2(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(variable_decorator = "**"))
        v, r = dsl.parse("** var1 {opt1} = \"val1\"")
        self.assertTrue(v)

    def testDslType20_TestParseDecoratedVarFail1(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(variable_decorator = "* "))
        v, r = dsl.parse("*var1 {opt1} = \"val1\"")
        self.assertFalse(v)

    def testDslType20_TestParseDecoratedVarFail2(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(variable_decorator = "* "))
        v, r = dsl.parse("* ")
        self.assertFalse(v)

    def testDslType20_TestParseDecoratedVarFail3(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(variable_decorator = "**"))
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
        self.assertEqual(var_fmt_helper(dsl.get_all_variables("ctx2")[1]), [("var4", "val4", [])])

    def testDslType20_TestNewContextWithOptions1(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options=True))
        v, r = dsl.parse("[\n@ctx1 {opt1}\nvar1 = \"val1\"\n]")
        self.assertEqual(var_fmt_helper(dsl.get_variables("var1", "ctx1")[1]), [("var1", "val1", [("opt1", None)])])
        self.assertTrue(v)

    def testDslType20_TestNewContextWithOptions2(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options=True))
        v, r = dsl.parse("[\n@ctx1 {opt2: \"val2\"}\nvar1 = \"val1\"\n]")
        self.assertTrue(v)
        self.assertEqual(var_fmt_helper(dsl.get_variables("var1", "ctx1")[1]), [("var1", "val1", [("opt2", "val2")])])

    def testDslType20_TestNewContextWithOptions3(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options=True))
        v, r = dsl.parse("[\n@ctx1 {opt3: \"val3\"}\nvar1 {opt4: \"val4\"} = \"val1\"\n]")
        self.assertTrue(v)
        self.assertEqual(var_fmt_helper(dsl.get_variables("var1", "ctx1")[1]), [("var1", "val1", [("opt3", "val3"), ("opt4", "val4")])])

    def testDslType20_TestNewContextWithOptions4(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options=True))
        v, r = dsl.parse("[\n@ctx1 {opt1: \"val1\"}\nvar1 {opt1: \"val3\"} = \"val2\"\n]")
        self.assertTrue(v)
        self.assertEqual(var_fmt_helper(dsl.get_variables("var1", "ctx1")[1]), [("var1", "val2", [("opt1", "val3")])])

    def testDslType20_TestNewContextWithOptions5(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes=False))
        v, r = dsl.parse("[\n@ctx1 {opt1: \"val1\"}\nvar1 {opt1: \"val3\"} = \"val2\"\n]")
        self.assertTrue(v)
        self.assertEqual(var_fmt_helper(dsl.get_variables("var1", "ctx1")[1]), [("var1", "val2", [("opt1", "val3")])])

    def testDslType20_TestNewContextWithOptions6(self):

        test_envvar_value = "dsltype20-test-value"
        os.environ[ (self.reserved_test_env_var_1[1:]) ] = test_envvar_value

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options=True, expand_envvars=True))
        v, r = dsl.parse("[\n@ctx1 {opt1: \"%s\"}\nvar1 = \"val2\"\n]" % self.reserved_test_env_var_1)
        self.assertEqual(var_fmt_helper(dsl.get_variables("var1", "ctx1")[1]), [("var1", "val2", [("opt1", test_envvar_value)])])
        self.assertTrue(v)

    def testDslType20_TestNewContextWithOptions7(self):

        test_envvar_value = "dsltype20-test-value"
        os.environ[ (self.reserved_test_env_var_1[1:]) ] = test_envvar_value

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options=True, expand_envvars=False))
        v, r = dsl.parse("[\n@ctx1 {opt1: \"%s\"}\nvar1 = \"val2\"\n]" % self.reserved_test_env_var_1)
        self.assertEqual(var_fmt_helper(dsl.get_variables("var1", "ctx1")[1]), [("var1", "val2", [("opt1", self.reserved_test_env_var_1)])])
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
        v, r = dsl.parse("var1 = \"val1\"\n[\n]")
        self.assertFalse(v)

    def testDslType20_TestNewContextFail4(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("var1 = \"val1\"\n[\n")
        self.assertFalse(v)

    def testDslType20_TestNewContextFail5(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("var1 = \"val1\"\n[\n@@ctx1\n]")
        self.assertFalse(v)

    def testDslType20_TestNewContextFail6(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("var1 = \"val1\"\n[\n@ctx 1\n]")
        self.assertFalse(v)

    def testDslType20_TestNewContextFail7(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("[\n@ctx1\nvar1 = \"val1\"\n")
        self.assertFalse(v)

    def testDslType20_TestNewContextFail8(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("\n[\nvar1 = \"val1\"\n]\n")
        self.assertFalse(v)

    def testDslType20_TestNewContextFail9(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.parse("\n[\n]\n")
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

    def testDslType20_TestAddContext1(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.add_context(None, "ok", [])
        self.assertTrue(v)

    def testDslType20_TestAddContext2(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.add_context(None, "ok1", [])
        self.assertTrue(v)

    def testDslType20_TestAddContext3(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.add_context(None, "_ok-90", [])
        self.assertTrue(v)

    def testDslType20_TestAddContext4(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.add_context(None, "ok", [("var1", "val1")])
        self.assertTrue(v)

    def testDslType20_TestAddContext5(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.add_context(None, "n ok", [])
        self.assertFalse(v)

    def testDslType20_TestAddContext6(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.add_context(None, "ctx1", [])
        self.assertTrue(v)
        v, r = dsl.add_context("ctx1", "ctx2", [])
        self.assertTrue(v)
        v, r = dsl.add_context("ctx1", "ctx3", [])
        self.assertTrue(v)
        v, r = dsl.get_sub_contexts(None)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0].get_name(), "ctx1")
        v, r = dsl.get_sub_contexts("ctx1")
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertEqual(r[0].get_name(), "ctx2")
        self.assertEqual(r[1].get_name(), "ctx3")

    def testDslType20_TestAddContext7(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.add_context(None, "ctx1", [("a", "b")])
        self.assertTrue(v)
        v, r = dsl.add_context("ctx1", "ctx2", [("1", "2")])
        self.assertTrue(v)
        v, r = dsl.get_context_options("ctx1")
        self.assertTrue(v)
        self.assertEqual([ (x.get_name(), x.get_value()) for x in r], [ ("a", "b") ])
        v, r = dsl.get_context_options("ctx2")
        self.assertTrue(v)
        self.assertEqual([ (x.get_name(), x.get_value()) for x in r], [ ("1", "2") ])

    def testDslType20_TestAddContext8(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.add_context(None, "ctx1", [("opt1", "val1")])
        self.assertTrue(v)
        v, r = dsl.add_context("ctx1", "ctx2", [("opt1", "val2")])
        self.assertTrue(v)
        v, r = dsl.get_context_options("ctx1")
        self.assertTrue(v)
        self.assertEqual([ (x.get_name(), x.get_value()) for x in r], [ ("opt1", "val1") ])
        v, r = dsl.get_context_options("ctx2")
        self.assertTrue(v)
        self.assertEqual([ (x.get_name(), x.get_value()) for x in r], [ ("opt1", "val2") ])

    def testDslType20_TestAddContext9(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.add_context(None, "ctx1", [("opt1", "val1"), ("opt2", "val2")])
        self.assertTrue(v)
        v, r = dsl.add_context("ctx1", "ctx2", [("opt3", "val3"), ("opt4", "val4")])
        self.assertTrue(v)
        v, r = dsl.get_context_options("ctx1")
        self.assertTrue(v)
        self.assertEqual([ (x.get_name(), x.get_value()) for x in r], [ ("opt1", "val1"), ("opt2", "val2") ])
        v, r = dsl.get_context_options("ctx2")
        self.assertTrue(v)
        self.assertEqual([ (x.get_name(), x.get_value()) for x in r], [ ("opt3", "val3"), ("opt4", "val4") ])

    def testDslType20_TestAddContext10(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.add_context(None, "ctx1", [("opt1", "val1"), ("opt2", "val2")])
        self.assertTrue(v)
        v, r = dsl.add_context("ctx1", "ctx2", [("opt3", "val3"), ("opt1", "val4")])
        self.assertTrue(v)
        v, r = dsl.get_context_options("ctx1")
        self.assertTrue(v)
        self.assertEqual([ (x.get_name(), x.get_value()) for x in r], [ ("opt1", "val1"), ("opt2", "val2") ])
        v, r = dsl.get_context_options("ctx2")
        self.assertTrue(v)
        self.assertEqual([ (x.get_name(), x.get_value()) for x in r], [ ("opt3", "val3"), ("opt1", "val4") ])

    def testDslType20_TestAddContext11(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.add_context(None, "ctx1", [("opt1", None), ("opt2", "val2")])
        self.assertTrue(v)
        v, r = dsl.add_context("ctx1", "ctx2", [("opt3", "val3"), ("opt1", None)])
        self.assertTrue(v)
        v, r = dsl.get_context_options("ctx1")
        self.assertTrue(v)
        self.assertEqual([ (x.get_name(), x.get_value()) for x in r], [ ("opt1", None), ("opt2", "val2") ])
        v, r = dsl.get_context_options("ctx2")
        self.assertTrue(v)
        self.assertEqual([ (x.get_name(), x.get_value()) for x in r], [ ("opt3", "val3"), ("opt1", None) ])

    def testDslType20_TestAddContext12(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.add_context(None, "ctx1", [("opt1", "val1"), ("opt2", "val2")])
        self.assertTrue(v)
        v, r = dsl.add_context("ctx1", "ctx2", [("opt3", "val3"), ("opt1", None)])
        self.assertTrue(v)
        v, r = dsl.get_context_options("ctx1")
        self.assertTrue(v)
        self.assertEqual([ (x.get_name(), x.get_value()) for x in r], [ ("opt1", "val1"), ("opt2", "val2") ])
        v, r = dsl.get_context_options("ctx2")
        self.assertTrue(v)
        self.assertEqual([ (x.get_name(), x.get_value()) for x in r], [ ("opt3", "val3"), ("opt1", None) ])

    def testDslType20_TestAddContext13(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.add_context(None, "ctx1", [("opt1", None), ("opt2", "val2")])
        self.assertTrue(v)
        v, r = dsl.add_context("ctx1", "ctx2", [("opt3", "val3"), ("opt1", "val4")])
        self.assertTrue(v)
        v, r = dsl.get_context_options("ctx1")
        self.assertTrue(v)
        self.assertEqual([ (x.get_name(), x.get_value()) for x in r], [ ("opt1", None), ("opt2", "val2") ])
        v, r = dsl.get_context_options("ctx2")
        self.assertTrue(v)
        self.assertEqual([ (x.get_name(), x.get_value()) for x in r], [ ("opt3", "val3"), ("opt1", "val4") ])

    def testDslType20_TestAddContext14(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.add_context(None, "ctx1", [])
        self.assertTrue(v)
        v, r = dsl.add_context("ctx1", "ctx2", [])
        self.assertTrue(v)
        v, r = dsl.add_variable("var1", None, [], "ctx1")
        self.assertTrue(v)
        v, r = dsl.add_variable("var2", None, [], "ctx1")
        self.assertTrue(v)
        v, r = dsl.add_variable("var3", None, [], "ctx2")
        self.assertTrue(v)
        v, r = dsl.add_variable("var4", None, [], "ctx2")
        self.assertTrue(v)
        v, r = dsl.get_all_variables("ctx1")
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertEqual([x.get_name() for x in r], ["var1", "var2"])
        v, r = dsl.get_all_variables("ctx2")
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertEqual([x.get_name() for x in r], ["var3", "var4"])

    def testDslType20_TestAddContext15(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.add_context(None, "ctx1", [])
        self.assertTrue(v)
        v, r = dsl.add_context("ctx1", "ctx1", [])
        self.assertFalse(v)

    def testDslType20_TestAddContext16(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options = True))
        v, r = dsl.add_context(None, "ctx1", [("a", "b")])
        self.assertTrue(v)
        v, r = dsl.add_context("ctx1", "ctx2", [("1", "2")])
        self.assertTrue(v)
        v, r = dsl.get_context_options("ctx1")
        self.assertTrue(v)
        self.assertEqual([ (x.get_name(), x.get_value()) for x in r], [ ("a", "b") ])
        v, r = dsl.get_context_options("ctx2")
        self.assertTrue(v)
        self.assertEqual([ (x.get_name(), x.get_value()) for x in r], [ ("a", "b"), ("1", "2") ])

    def testDslType20_TestAddContext17(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options = True))
        v, r = dsl.add_context(None, "ctx1", [("opt1", "val1")])
        self.assertTrue(v)
        v, r = dsl.add_context("ctx1", "ctx2", [("opt1", "val2")])
        self.assertTrue(v)
        v, r = dsl.get_context_options("ctx1")
        self.assertTrue(v)
        self.assertEqual([ (x.get_name(), x.get_value()) for x in r], [ ("opt1", "val1") ])
        v, r = dsl.get_context_options("ctx2")
        self.assertTrue(v)
        self.assertEqual([ (x.get_name(), x.get_value()) for x in r], [ ("opt1", "val2") ])

    def testDslType20_TestAddContext18(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options = True))
        v, r = dsl.add_context(None, "ctx1", [("opt1", "val1"), ("opt2", "val2")])
        self.assertTrue(v)
        v, r = dsl.add_context("ctx1", "ctx2", [("opt3", "val3"), ("opt4", "val4")])
        self.assertTrue(v)
        v, r = dsl.get_context_options("ctx1")
        self.assertTrue(v)
        self.assertEqual([ (x.get_name(), x.get_value()) for x in r], [ ("opt1", "val1"), ("opt2", "val2") ])
        v, r = dsl.get_context_options("ctx2")
        self.assertTrue(v)
        self.assertEqual([ (x.get_name(), x.get_value()) for x in r], [ ("opt1", "val1"), ("opt2", "val2"), ("opt3", "val3"), ("opt4", "val4") ])

    def testDslType20_TestAddContext19(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options = True))
        v, r = dsl.add_context(None, "ctx1", [("opt1", "val1"), ("opt2", "val2")])
        self.assertTrue(v)
        v, r = dsl.add_context("ctx1", "ctx2", [("opt3", "val3"), ("opt1", "val4")])
        self.assertTrue(v)
        v, r = dsl.get_context_options("ctx1")
        self.assertTrue(v)
        self.assertEqual([ (x.get_name(), x.get_value()) for x in r], [ ("opt1", "val1"), ("opt2", "val2") ])
        v, r = dsl.get_context_options("ctx2")
        self.assertTrue(v)
        self.assertEqual([ (x.get_name(), x.get_value()) for x in r], [ ("opt2", "val2"), ("opt3", "val3"), ("opt1", "val4") ])

    def testDslType20_TestAddContext20(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options = True))
        v, r = dsl.add_context(None, "ctx1", [("opt1", None), ("opt2", "val2")])
        self.assertTrue(v)
        v, r = dsl.add_context("ctx1", "ctx2", [("opt3", "val3"), ("opt1", None)])
        self.assertTrue(v)
        v, r = dsl.get_context_options("ctx1")
        self.assertTrue(v)
        self.assertEqual([ (x.get_name(), x.get_value()) for x in r], [ ("opt1", None), ("opt2", "val2") ])
        v, r = dsl.get_context_options("ctx2")
        self.assertTrue(v)
        self.assertEqual([ (x.get_name(), x.get_value()) for x in r], [ ("opt2", "val2"), ("opt3", "val3") ])

    def testDslType20_TestAddContext21(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options = True))
        v, r = dsl.add_context(None, "ctx1", [("opt1", "val1"), ("opt2", "val2")])
        self.assertTrue(v)
        v, r = dsl.add_context("ctx1", "ctx2", [("opt3", "val3"), ("opt1", None)])
        self.assertTrue(v)
        v, r = dsl.get_context_options("ctx1")
        self.assertTrue(v)
        self.assertEqual([ (x.get_name(), x.get_value()) for x in r], [ ("opt1", "val1"), ("opt2", "val2") ])
        v, r = dsl.get_context_options("ctx2")
        self.assertTrue(v)
        self.assertEqual([ (x.get_name(), x.get_value()) for x in r], [ ("opt2", "val2"), ("opt3", "val3"), ("opt1", None) ])

    def testDslType20_TestAddContext22(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options = True))
        v, r = dsl.add_context(None, "ctx1", [("opt1", None), ("opt2", "val2")])
        self.assertTrue(v)
        v, r = dsl.add_context("ctx1", "ctx2", [("opt3", "val3"), ("opt1", "val4")])
        self.assertTrue(v)
        v, r = dsl.get_context_options("ctx1")
        self.assertTrue(v)
        self.assertEqual([ (x.get_name(), x.get_value()) for x in r], [ ("opt1", None), ("opt2", "val2") ])
        v, r = dsl.get_context_options("ctx2")
        self.assertTrue(v)
        self.assertEqual([ (x.get_name(), x.get_value()) for x in r], [ ("opt2", "val2"), ("opt3", "val3"), ("opt1", "val4") ])

    def testDslType20_TestAddContext23(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options = True))
        v, r = dsl.add_context(None, "ctx1", [])
        self.assertTrue(v)
        v, r = dsl.add_context("ctx1", "ctx2", [])
        self.assertTrue(v)
        v, r = dsl.add_variable("var1", None, [], "ctx1")
        self.assertTrue(v)
        v, r = dsl.add_variable("var2", None, [], "ctx1")
        self.assertTrue(v)
        v, r = dsl.add_variable("var3", None, [], "ctx2")
        self.assertTrue(v)
        v, r = dsl.add_variable("var4", None, [], "ctx2")
        self.assertTrue(v)
        v, r = dsl.get_all_variables("ctx1")
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertEqual([x.get_name() for x in r], ["var1", "var2"])
        v, r = dsl.get_all_variables("ctx2")
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertEqual([x.get_name() for x in r], ["var3", "var4"])

    def testDslType20_TestAddContext24(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options = True))
        v, r = dsl.add_context(None, "ctx1", [])
        self.assertTrue(v)
        v, r = dsl.add_context("ctx1", "ctx1", [])
        self.assertFalse(v)

    def testDslType20_TestGetContext1(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.add_context(None, "ctx1", [])
        self.assertTrue(v)
        v, r = dsl.add_context("ctx1", "ctx2", [])
        self.assertTrue(v)
        v, r = dsl.get_context(None)
        self.assertTrue(v)
        self.assertTrue(isinstance(r, dsl_type20.DSLType20_Context))
        self.assertEqual(r, dsl.data)
        self.assertEqual(len(r.get_entries()), 1)

    def testDslType20_TestGetContext2(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.add_context(None, "ctx1", [])
        self.assertTrue(v)
        v, r = dsl.add_context("ctx1", "ctx2", [])
        self.assertTrue(v)
        v, r = dsl.get_context("default-context")
        self.assertTrue(v)
        self.assertTrue(isinstance(r, dsl_type20.DSLType20_Context))
        self.assertEqual(r, dsl.data)
        self.assertEqual(len(r.get_entries()), 1)

    def testDslType20_TestGetContext3(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.add_variable("ctx1", None, [])
        self.assertTrue(v)
        v, r = dsl.add_context(None, "ctx1", [])
        self.assertTrue(v)
        v, r = dsl.add_context("ctx1", "ctx2", [])
        self.assertTrue(v)
        v, r = dsl.get_context("ctx1")
        self.assertTrue(v)
        self.assertTrue(isinstance(r, dsl_type20.DSLType20_Context))
        self.assertEqual(r, dsl.data.get_entries()[1])
        self.assertEqual(len(r.get_entries()), 1)
        self.assertTrue("ctx2" in [x.get_name() for x in r.get_entries()] )

    def testDslType20_TestGetContext4(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.add_context(None, "ctx1", [])
        self.assertTrue(v)
        v, r = dsl.add_context("ctx1", "ctx2", [])
        self.assertTrue(v)
        v, r = dsl.get_context("ctx2", "ctx1")
        self.assertTrue(v)
        self.assertTrue(isinstance(r, dsl_type20.DSLType20_Context))
        self.assertEqual(r, dsl.data.get_entries()[0].get_entries()[0])
        self.assertEqual(len(r.get_entries()), 0)

    def testDslType20_TestGetContext5(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.add_context(None, "ctx1", [])
        self.assertTrue(v)
        v, r = dsl.add_context("ctx1", "ctx2", [])
        self.assertTrue(v)
        v, r = dsl.get_context("ctx2")
        self.assertTrue(v)
        self.assertEqual(r, None)

    def testDslType20_TestGetSubContexts1(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl.add_context(None, "ctx1", [])[0])
        self.assertTrue(dsl.add_context(None, "ctx2", [])[0])
        v, r = dsl.get_sub_contexts(None)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertEqual([x.get_name() for x in r], ["ctx1", "ctx2"])

    def testDslType20_TestGetSubContexts2(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl.add_context(None, "ctx1", [])[0])
        self.assertTrue(dsl.add_context(None, "ctx2", [])[0])
        self.assertTrue(dsl.add_variable("var1", None, [])[0])
        self.assertFalse(dsl.add_context(None, "ctx 3", [])[0])
        self.assertTrue(dsl.add_context(None, "ctx4", [])[0])
        v, r = dsl.get_sub_contexts(None)
        self.assertTrue(v)
        self.assertEqual(len(r), 3)
        self.assertEqual([x.get_name() for x in r], ["ctx1", "ctx2", "ctx4"])

    def testDslType20_TestGetSubContexts3(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl.add_context(None, "ctx1", [])[0])
        self.assertTrue(dsl.add_context("ctx1", "ctx2", [])[0])
        self.assertTrue(dsl.add_context("ctx2", "ctx3", [])[0])
        self.assertTrue(dsl.add_variable("var1", "ctx3", [])[0])
        v, r = dsl.get_sub_contexts("ctx3")
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

    def testDslType20_TestGetSubContexts4(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl.add_context(None, "ctx1", [])[0])
        self.assertTrue(dsl.add_context("ctx1", "ctx2", [])[0])
        self.assertTrue(dsl.add_context("ctx2", "ctx3", [])[0])
        self.assertTrue(dsl.add_variable("var1", "ctx3", [])[0])
        v, r = dsl.get_sub_contexts("ctx2")
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertEqual([x.get_name() for x in r], ["ctx3"])

    def testDslType20_TestAddContextFail1(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.add_context(None, [], [])
        self.assertFalse(v)

    def testDslType20_TestAddContextFail2(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.add_context(None, "", [])
        self.assertFalse(v)

    def testDslType20_TestAddContextFail3(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.add_context(None, "ok!", [])
        self.assertFalse(v)

    def testDslType20_TestAddContextFail4(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.add_context(None, "@ok", [])
        self.assertFalse(v)

    def testDslType20_TestAddContextFail5(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.add_context(None, "ok", [])
        self.assertTrue(v)
        v, r = dsl.add_context(None, "ok", [])
        self.assertFalse(v)

    def testDslType20_TestAddContextFail6(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl.add_context(None, "ok", "nok")
        self.assertFalse(v)

    def testDslType20_TestAddContextFail7(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertFalse(dsl.add_context(None, "ok", [("var1", "first line\nsecond line")])[0])

    def testDslType20_TestAddVariable1(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl.add_variable("var1", None, [ ] )[0])
        v, r = dsl.get_all_variables()
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        var_obj = r[0]
        self.assertEqual(var_obj.get_name(), "var1")
        self.assertEqual(var_obj.get_value(), None)
        self.assertEqual(var_obj.get_options(), [])

    def testDslType20_TestAddVariable2(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl.add_variable("var1", "", [ ] )[0])
        v, r = dsl.get_all_variables()
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        var_obj = r[0]
        self.assertEqual(var_obj.get_name(), "var1")
        self.assertEqual(var_obj.get_value(), "")
        self.assertEqual(var_obj.get_options(), [])

    def testDslType20_TestAddVariable3(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl.add_variable("var1", "val1", [ ] )[0])
        v, r = dsl.get_all_variables()
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        var_obj = r[0]
        self.assertEqual(var_obj.get_name(), "var1")
        self.assertEqual(var_obj.get_value(), "val1")
        self.assertEqual(var_obj.get_options(), [])

    def testDslType20_TestAddVariable4(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl.add_variable("var1", "val1", [ ("opt1", "val2") ] )[0])
        v, r = dsl.get_all_variables()
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        var_obj = r[0]
        self.assertEqual(var_obj.get_name(), "var1")
        self.assertEqual(var_obj.get_value(), "val1")
        self.assertEqual([(x.get_name(), x.get_value()) for x in var_obj.get_options()], [("opt1", "val2")])

    def testDslType20_TestAddVariable5(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl.add_variable("var1", "val1", [ ("opt1", "val2"), ("opt2", "val3") ] )[0])
        v, r = dsl.get_all_variables()
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        var_obj = r[0]
        self.assertEqual(var_obj.get_name(), "var1")
        self.assertEqual(var_obj.get_value(), "val1")
        self.assertEqual([(x.get_name(), x.get_value()) for x in var_obj.get_options()], [ ("opt1", "val2"), ("opt2", "val3") ])

    def testDslType20_TestAddVariable6(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl.add_variable("var1", "val1", [ ("opt1", "val2"), ("opt2", "val3") ] )[0])
        self.assertTrue(dsl.add_variable("var1", "val1", [ ("opt1", "val2"), ("opt2", "val3") ] )[0])
        v, r = dsl.get_all_variables()
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        var_obj = r[0]
        self.assertEqual(var_obj.get_name(), "var1")
        self.assertEqual(var_obj.get_value(), "val1")
        self.assertEqual([(x.get_name(), x.get_value()) for x in var_obj.get_options()], [ ("opt1", "val2"), ("opt2", "val3") ])
        var_obj = r[1]
        self.assertEqual(var_obj.get_name(), "var1")
        self.assertEqual(var_obj.get_value(), "val1")
        self.assertEqual([(x.get_name(), x.get_value()) for x in var_obj.get_options()], [ ("opt1", "val2"), ("opt2", "val3") ])

    def testDslType20_TestAddVariable7(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options=True))
        self.assertTrue(dsl.add_context(None, "ctx1", [("opt1", "val1")])[0])
        self.assertTrue(dsl.add_variable("var1", "val2", [ ("opt2", "val3") ], "ctx1" )[0])
        v, r = dsl.get_variables("var1", "ctx1")
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        var_obj = r[0]
        self.assertEqual(var_obj.get_name(), "var1")
        self.assertEqual(var_obj.get_value(), "val2")
        self.assertEqual([(x.get_name(), x.get_value()) for x in var_obj.get_options()], [("opt1", "val1"), ("opt2", "val3")])

    def testDslType20_TestAddVariable8(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options=True))
        self.assertTrue(dsl.add_context(None, "ctx1", [("opt1", "val1")])[0])
        self.assertTrue(dsl.add_variable("var1", "val2", [ ("opt1", "val3") ], "ctx1" )[0])
        v, r = dsl.get_variables("var1", "ctx1")
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        var_obj = r[0]
        self.assertEqual(var_obj.get_name(), "var1")
        self.assertEqual(var_obj.get_value(), "val2")
        self.assertEqual([(x.get_name(), x.get_value()) for x in var_obj.get_options()], [("opt1", "val3")])

    def testDslType20_TestAddVariable9(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl.add_variable("var1", "val1", [ ("opt1", None) ] )[0])
        v, r = dsl.get_all_variables()
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertEqual([ ((x.get_name(), x.get_value(), [(y.get_name(), y.get_value()) for y in x.get_options()]) ) for x in r], [ ("var1", "val1", [("opt1", None)]) ])

    def testDslType20_TestAddVariable10(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl.add_variable("var1", None, [ ] )[0])

    def testDslType20_TestAddVariable11(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl.add_context(None, "ctx1", [("opt1", "val1")])[0])
        self.assertTrue(dsl.add_variable("var1", "val2", [ ("opt2", "val3") ], "ctx1" )[0])
        v, r = dsl.get_variables("var1", "ctx1")
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        var_obj = r[0]
        self.assertEqual(var_obj.get_name(), "var1")
        self.assertEqual(var_obj.get_value(), "val2")
        self.assertEqual([(x.get_name(), x.get_value()) for x in var_obj.get_options()], [("opt2", "val3")])

    def testDslType20_TestAddVariable12(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options=True))
        self.assertTrue(dsl.add_context(None, "ctx1", [("opt1", None)])[0])
        self.assertTrue(dsl.add_variable("var1", "val2", [ ("opt1", "val3") ], "ctx1" )[0])
        v, r = dsl.get_variables("var1", "ctx1")
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        var_obj = r[0]
        self.assertEqual(var_obj.get_name(), "var1")
        self.assertEqual(var_obj.get_value(), "val2")
        self.assertEqual([(x.get_name(), x.get_value()) for x in var_obj.get_options()], [("opt1", "val3")])

    def testDslType20_TestAddVariable13(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options=True))
        self.assertTrue(dsl.add_context(None, "ctx1", [("opt1", "val3")])[0])
        self.assertTrue(dsl.add_variable("var1", "val2", [ ("opt1", None) ], "ctx1" )[0])
        v, r = dsl.get_variables("var1", "ctx1")
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        var_obj = r[0]
        self.assertEqual(var_obj.get_name(), "var1")
        self.assertEqual(var_obj.get_value(), "val2")
        self.assertEqual([(x.get_name(), x.get_value()) for x in var_obj.get_options()], [("opt1", None)])

    def testDslType20_TestAddVariable14(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options=True))
        self.assertTrue(dsl.add_context(None, "ctx1", [("opt1", None)])[0])
        self.assertTrue(dsl.add_variable("var1", "val2", [ ("opt1", None) ], "ctx1" )[0])
        v, r = dsl.get_variables("var1", "ctx1")
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        var_obj = r[0]
        self.assertEqual(var_obj.get_name(), "var1")
        self.assertEqual(var_obj.get_value(), "val2")
        self.assertEqual([(x.get_name(), x.get_value()) for x in var_obj.get_options()], [])

    def testDslType20_TestAddVariable15(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options=True))
        self.assertTrue(dsl.add_context(None, "ctx1", [("opt1", "val2")])[0])
        self.assertTrue(dsl.add_context("ctx1", "ctx2", [("opt2", "val3")])[0])
        self.assertTrue(dsl.add_context("ctx2", "ctx3", [("opt3", "val4")])[0])
        self.assertTrue(dsl.add_variable("var1", "val2", [ ("opt4", "val5") ], "ctx3" )[0])
        v, r = dsl.get_variables("var1", "ctx3")
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        var_obj = r[0]
        self.assertEqual(var_obj.get_name(), "var1")
        self.assertEqual(var_obj.get_value(), "val2")
        self.assertEqual([(x.get_name(), x.get_value()) for x in var_obj.get_options()], [("opt1", "val2"), ("opt2", "val3"), ("opt3", "val4"), ("opt4", "val5")])

    def testDslType20_TestAddVariable16(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl.add_variable("var1", "val1", [], "ctx1")[0])
        v, r = dsl.get_all_variables("ctx1")
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        var_obj = r[0]
        self.assertEqual(var_obj.get_name(), "var1")
        self.assertEqual(var_obj.get_value(), "val1")
        self.assertEqual([(x.get_name(), x.get_value()) for x in var_obj.get_options()], [])

    def testDslType20_TestAddVariableFail1(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertFalse(dsl.add_variable("var1", [], [ ] )[0])

    def testDslType20_TestAddVariableFail2(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertFalse(dsl.add_variable("var1", "val1", [ ("opt") ] )[0])

    def testDslType20_TestAddVariableFail3(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertFalse(dsl.add_variable("var1", "val1", [ ("opt", 1) ] )[0])

    def testDslType20_TestAddVariableFail4(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertFalse(dsl.add_variable("var1", "val1", [ ("opt", "val", "again") ] )[0])

    def testDslType20_TestAddVariableFail5(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertFalse(dsl.add_variable("var1", "val1", [ ["opt", "val"] ] )[0])

    def testDslType20_TestAddVariableFail6(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertFalse(dsl.add_variable("var1", "val1", [ None ] )[0])

    def testDslType20_TestAddVariableFail7(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertFalse(dsl.add_variable("var1", "val1", None )[0])

    def testDslType20_TestAddVariableFail8(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertFalse(dsl.add_variable(1, "val1", [ ("opt", "val") ] )[0])

    def testDslType20_TestAddVariableFail9(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertFalse(dsl.add_variable(None, "val1", [ ("opt", "val") ] )[0])

    def testDslType20_TestAddVariableFail10(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertFalse(dsl.add_variable("var1", "first line\nsecond line", [ ] )[0])

    def testDslType20_TestAddVariableFail11(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertFalse(dsl.add_variable("var1", "val1", [ ("opt1", "first line\nsecond line") ] )[0])

    def testDslType20_TestCountOccurrenceFirstOfPair1(self):
        self.assertEqual(dsl_type20.count_occurrence_first_of_pair( [ ("b", None) ], "a" ), 0)

    def testDslType20_TestCountOccurrenceFirstOfPair2(self):
        self.assertEqual(dsl_type20.count_occurrence_first_of_pair( [ ("b", None) ], "b" ), 1)

    def testDslType20_TestCountOccurrenceFirstOfPair3(self):
        self.assertEqual(dsl_type20.count_occurrence_first_of_pair( [ ("b", None), ("b", None) ], "b" ), 2)

    def testDslType20_TestDisallowDupes1(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes=False))
        self.assertTrue(dsl.add_variable("var1", "val1", [])[0])
        self.assertFalse(dsl.add_variable("var1", "val2", [])[0])

    def testDslType20_TestDisallowDupes2(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes=False))
        self.assertTrue(dsl.add_variable("var1", "val1", [ ("opt1", None) ] )[0])

    def testDslType20_TestDisallowDupes3(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes=False))
        self.assertFalse(dsl.add_variable("var1", "val1", [ ("opt1", None), ("opt1", None) ] )[0])

    def testDslType20_TestDisallowDupes4(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes=False))
        self.assertTrue(dsl.add_variable("var1", "val1", [ ("opt1", None) ] )[0])
        self.assertTrue(dsl.add_variable("var2", "val1", [ ("opt1", None) ] )[0])

    def testDslType20_TestDisallowDupes5(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes=False))
        self.assertTrue(dsl.add_context(None, "ctx1", [])[0])
        self.assertTrue(dsl.add_variable("var1", "val1", [], "ctx1")[0])
        self.assertFalse(dsl.add_variable("var1", "val2", [], "ctx1")[0])

    def testDslType20_TestDisallowDupes6(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes=False))
        self.assertTrue(dsl.add_context(None, "ctx1", [])[0])
        self.assertTrue(dsl.add_variable("var1", "val1", [], "ctx1")[0])
        self.assertTrue(dsl.add_variable("var1", "val2", [], None)[0])

    def testDslType20_TestDisallowDupesParse1(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes=False))

        contents_cfg_test_fail_dupevar = "var1 = \"val1\"\n"
        contents_cfg_test_fail_dupevar += "var1 = \"val2\"\n"

        v, r = dsl.parse(contents_cfg_test_fail_dupevar)
        self.assertFalse(v)

    def testDslType20_TestRemVariable1(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl.add_variable("var1", "val1", [])[0])
        v, r = dsl.get_all_variables()
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        var_obj = r[0]
        self.assertEqual(var_obj.get_name(), "var1")
        self.assertEqual(var_obj.get_value(), "val1")
        self.assertEqual(var_obj.get_options(), [])
        v, r = dsl.rem_variable("var1")
        self.assertTrue(v)
        self.assertEqual(r, 1)
        v, r = dsl.get_all_variables()
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

    def testDslType20_TestRemVariable2(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl.add_variable("var1", "val1", [])[0])
        v, r = dsl.get_all_variables()
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        var_obj = r[0]
        self.assertEqual(var_obj.get_name(), "var1")
        self.assertEqual(var_obj.get_value(), "val1")
        self.assertEqual(var_obj.get_options(), [])
        v, r = dsl.rem_variable("var1", "ctx1")
        self.assertFalse(v)

    def testDslType20_TestRemVariable3(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl.add_variable("var1", "val1", [])[0])
        self.assertTrue(dsl.add_variable("var1", "val2", [])[0])
        v, r = dsl.get_all_variables()
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        var_obj = r[0]
        self.assertEqual(var_obj.get_name(), "var1")
        self.assertEqual(var_obj.get_value(), "val1")
        self.assertEqual(var_obj.get_options(), [])
        var_obj = r[1]
        self.assertEqual(var_obj.get_name(), "var1")
        self.assertEqual(var_obj.get_value(), "val2")
        self.assertEqual(var_obj.get_options(), [])
        v, r = dsl.rem_variable("var1")
        self.assertTrue(v)
        self.assertEqual(r, 2)
        v, r = dsl.get_all_variables()
        self.assertTrue(v)
        self.assertEqual(len(r), 0)
        self.assertEqual(r, [])

    def testDslType20_TestRemVariable4(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl.add_variable("var1", "val1", [])[0])
        v, r = dsl.get_all_variables()
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        var_obj = r[0]
        self.assertEqual(var_obj.get_name(), "var1")
        self.assertEqual(var_obj.get_value(), "val1")
        self.assertEqual(var_obj.get_options(), [])
        v, r = dsl.rem_variable("var2")
        self.assertTrue(v)
        self.assertEqual(r, 0)
        v, r = dsl.get_all_variables()
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        var_obj = r[0]
        self.assertEqual(var_obj.get_name(), "var1")
        self.assertEqual(var_obj.get_value(), "val1")
        self.assertEqual(var_obj.get_options(), [])

    def testDslType20_TestRemVariable5(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl.add_variable("var1", "val2", [])[0])
        self.assertTrue(dsl.add_variable("var1", "val4", [], "ctx1")[0])
        v, r = dsl.get_all_variables()
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        var_obj = r[0]
        self.assertEqual(var_obj.get_name(), "var1")
        self.assertEqual(var_obj.get_value(), "val2")
        self.assertEqual(var_obj.get_options(), [])
        v, r = dsl.get_all_variables("ctx1")
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        var_obj = r[0]
        self.assertEqual(var_obj.get_name(), "var1")
        self.assertEqual(var_obj.get_value(), "val4")
        self.assertEqual(var_obj.get_options(), [])
        v, r = dsl.rem_variable("var1", "ctx1")
        self.assertTrue(v)
        self.assertEqual(r, 1)
        v, r = dsl.get_all_variables()
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        var_obj = r[0]
        self.assertEqual(var_obj.get_name(), "var1")
        self.assertEqual(var_obj.get_value(), "val2")
        self.assertEqual(var_obj.get_options(), [])
        v, r = dsl.get_all_variables("ctx1")
        self.assertTrue(v)
        self.assertEqual(len(r), 0)
        self.assertEqual(r, [])

    def testDslType20_TestRemAllVariables1(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl.add_variable("var1", "val1", [])[0])
        v, r = dsl.get_all_variables()
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        var_obj = r[0]
        self.assertEqual(var_obj.get_name(), "var1")
        self.assertEqual(var_obj.get_value(), "val1")
        self.assertEqual(var_obj.get_options(), [])
        v, r = dsl.rem_all_variables()
        self.assertTrue(v)
        self.assertEqual(r, ["var1"])
        v, r = dsl.get_all_variables()
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

    def testDslType20_TestRemAllVariables2(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl.add_variable("var1", "val1", [], "ctx1")[0])
        v, r = dsl.get_all_variables("ctx1")
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        var_obj = r[0]
        self.assertEqual(var_obj.get_name(), "var1")
        self.assertEqual(var_obj.get_value(), "val1")
        self.assertEqual(var_obj.get_options(), [])
        v, r = dsl.rem_all_variables("ctx1")
        self.assertTrue(v)
        self.assertEqual(r, ["var1"])
        v, r = dsl.get_all_variables()
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

    def testDslType20_TestRemAllVariables3(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl.add_variable("var1", "val1", [], "ctx1")[0])
        v, r = dsl.get_all_variables("ctx1")
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        var_obj = r[0]
        self.assertEqual(var_obj.get_name(), "var1")
        self.assertEqual(var_obj.get_value(), "val1")
        self.assertEqual(var_obj.get_options(), [])
        v, r = dsl.rem_all_variables()
        self.assertTrue(v)
        self.assertEqual(r, [])
        v, r = dsl.get_all_variables("ctx1")
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        var_obj = r[0]
        self.assertEqual(var_obj.get_name(), "var1")
        self.assertEqual(var_obj.get_value(), "val1")
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

    def testDslType20_TestRemContext1(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertFalse(dsl.rem_context(None)[0])

    def testDslType20_TestRemContext2(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertFalse(dsl.rem_context(dsl.default_context_id)[0])

    def testDslType20_TestRemContext3(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertFalse(dsl.rem_context("ctx1")[0])

    def testDslType20_TestRemContext4(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl.add_context(None, "ctx1", [])[0])
        v, r = dsl.get_sub_contexts(None)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertEqual([x.get_name() for x in r], ["ctx1"])
        self.assertTrue(dsl.rem_context("ctx1")[0])
        v, r = dsl.get_sub_contexts(None)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)
        self.assertEqual([x.get_name() for x in r], [])

    def testDslType20_TestRemContext5(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl.add_context(None, "ctx1", [])[0])
        self.assertTrue(dsl.add_context(None, "ctx2", [])[0])
        v, r = dsl.get_sub_contexts(None)
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertEqual([x.get_name() for x in r], ["ctx1", "ctx2"])
        self.assertTrue(dsl.rem_context("ctx1")[0])
        v, r = dsl.get_sub_contexts(None)
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
        v, r = dsl.get_sub_contexts(None)
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
        self.assertTrue(dsl.add_context(None, "ctx1", [])[0])
        self.assertTrue(dsl.add_context("ctx1", "ctx2", [])[0])
        v, r = dsl.get_sub_contexts(None)
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertEqual([x.get_name() for x in r], ["ctx1"])
        v, r = dsl.get_sub_contexts("ctx1")
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertEqual([x.get_name() for x in r], ["ctx2"])
        self.assertTrue(dsl.rem_context("ctx2")[0])
        v, r = dsl.get_sub_contexts("ctx1")
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
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables("ctx1")[1]), [("var1", "val1", [])])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables("ctx2")[1]), [("var1", "val1", []), ("var2", "val2", [])])
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
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables("ctx1")[1]), [("var1", "val\"1\"", [])])
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
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables("ctx1")[1]), [("var1", "val\"1\"", [("opt1", None)])])
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
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables("ctx1")[1]), [("var1", "val1", [("opt1", "val2")])])
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
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables("ctx1")[1]), [("var1", "val\"1\"", [("opt1", "val\"2\"")])])
        self.assertEqual(dsl_1.produce(), "[\n@ctx1\nvar1 {opt1: \"val\\\"2\\\"\"} = \"val\\\"1\\\"\"\n]")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce8(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options=True))
        self.assertTrue(dsl_1.add_context(None, "ctx1", [("opt1", "val2")])[0])
        self.assertTrue(dsl_1.add_variable("var1", "val1", [], "ctx1")[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables("ctx1")[1]), [("var1", "val1", [("opt1", "val2")])])
        self.assertEqual(dsl_1.produce(), "[\n@ctx1 {opt1: \"val2\"}\nvar1 = \"val1\"\n]")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce9(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(inherit_options=True))
        self.assertTrue(dsl_1.add_context(None, "ctx1", [("opt1", "val1")])[0])
        self.assertTrue(dsl_1.add_variable("var1", "val2", [("opt1", "val3")], "ctx1")[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables("ctx1")[1]), [("var1", "val2", [("opt1", "val1"), ("opt1", "val3")])])
        self.assertEqual(dsl_1.produce(), "[\n@ctx1 {opt1: \"val1\"}\nvar1 {opt1: \"val3\"} = \"val2\"\n]")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce10(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes=False))
        self.assertTrue(dsl_1.add_context(None, "ctx1", [("opt1", "val1")])[0])
        self.assertTrue(dsl_1.add_variable("var1", "val2", [("opt1", "val3")], "ctx1")[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables("ctx1")[1]), [("var1", "val2", [("opt1", "val3")])])
        self.assertEqual(dsl_1.produce(), "[\n@ctx1 {opt1: \"val1\"}\nvar1 {opt1: \"val3\"} = \"val2\"\n]")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes=False))
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce11(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(variable_decorator="* "))
        self.assertTrue(dsl_1.add_variable("var1", "val1", [])[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), [("var1", "val1", [])])
        self.assertEqual(dsl_1.produce(), "* var1 = \"val1\"")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(variable_decorator="* "))
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce12(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes=False))
        self.assertTrue(dsl_1.add_context(None, "ctx1", [("opt1", "val1"), ("opt2", "val2")])[0])
        self.assertTrue(dsl_1.add_variable("var1", "val4", [("opt1", "val3")], "ctx1")[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables("ctx1")[1]), [("var1", "val4", [("opt1", "val3")])])
        self.assertEqual(dsl_1.produce(), "[\n@ctx1 {opt1: \"val1\" / opt2: \"val2\"}\nvar1 {opt1: \"val3\"} = \"val4\"\n]")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes=False))
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce13(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes=False))
        self.assertTrue(dsl_1.add_context(None, "ctx1", [])[0])
        self.assertTrue(dsl_1.add_variable("var1", "", [], "ctx1")[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables("ctx1")[1]), [("var1", "", [])])
        self.assertEqual(dsl_1.produce(), "[\n@ctx1\nvar1 = \"\"\n]")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes=False))
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce14(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes=False))
        self.assertTrue(dsl_1.add_context(None, "ctx1", [])[0])
        self.assertTrue(dsl_1.add_variable("var1", "", [("opt1", None)], "ctx1")[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables("ctx1")[1]), [("var1", "", [("opt1", None)])])
        self.assertEqual(dsl_1.produce(), "[\n@ctx1\nvar1 {opt1} = \"\"\n]")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes=False))
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce15(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes=False))
        self.assertTrue(dsl_1.add_context(None, "ctx1", [("opt1", None)])[0])
        self.assertTrue(dsl_1.add_variable("var1", "", [], "ctx1")[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables("ctx1")[1]), [("var1", "", [])])
        self.assertEqual(dsl_1.produce(), "[\n@ctx1 {opt1}\nvar1 = \"\"\n]")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes=False))
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce16(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes=False))
        self.assertTrue(dsl_1.add_context(None, "ctx1", [])[0])
        self.assertTrue(dsl_1.add_variable("var1", "", [("opt1", "")], "ctx1")[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables("ctx1")[1]), [("var1", "", [("opt1", "")])])
        self.assertEqual(dsl_1.produce(), "[\n@ctx1\nvar1 {opt1: \"\"} = \"\"\n]")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes=False))
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce17(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes=False))
        self.assertTrue(dsl_1.add_context(None, "ctx1", [("opt1", "")])[0])
        self.assertTrue(dsl_1.add_variable("var1", "", [], "ctx1")[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables("ctx1")[1]), [("var1", "", [])])
        self.assertEqual(dsl_1.produce(), "[\n@ctx1 {opt1: \"\"}\nvar1 = \"\"\n]")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes=False))
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce18(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes=False))
        self.assertTrue(dsl_1.add_context(None, "ctx1", [])[0])
        self.assertTrue(dsl_1.add_variable("var1", "", [("opt1", None), ("opt2", None)], "ctx1")[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables("ctx1")[1]), [("var1", "", [("opt1", None), ("opt2", None)])])
        self.assertEqual(dsl_1.produce(), "[\n@ctx1\nvar1 {opt1 / opt2} = \"\"\n]")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes=False))
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce19(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes=False))
        self.assertTrue(dsl_1.add_context(None, "ctx1", [])[0])
        self.assertTrue(dsl_1.add_variable("var1", "", [("opt1", ""), ("opt2", "")], "ctx1")[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables("ctx1")[1]), [("var1", "", [("opt1", ""), ("opt2", "")])])
        self.assertEqual(dsl_1.produce(), "[\n@ctx1\nvar1 {opt1: \"\" / opt2: \"\"} = \"\"\n]")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes=False))
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce20(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes=False))
        self.assertTrue(dsl_1.add_context(None, "ctx1", [])[0])
        self.assertTrue(dsl_1.add_variable("var1", "", [("opt1", "abc"), ("opt2", "def")], "ctx1")[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables("ctx1")[1]), [("var1", "", [("opt1", "abc"), ("opt2", "def")])])
        self.assertEqual(dsl_1.produce(), "[\n@ctx1\nvar1 {opt1: \"abc\" / opt2: \"def\"} = \"\"\n]")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes=False))
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce21(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes=False))
        self.assertTrue(dsl_1.add_context(None, "ctx1", [("opt1", None), ("opt2", None)])[0])
        self.assertTrue(dsl_1.add_variable("var1", "", [], "ctx1")[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables("ctx1")[1]), [("var1", "", [])])
        self.assertEqual(dsl_1.produce(), "[\n@ctx1 {opt1 / opt2}\nvar1 = \"\"\n]")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes=False))
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce22(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes=False))
        self.assertTrue(dsl_1.add_context(None, "ctx1", [("opt1", ""), ("opt2", "")])[0])
        self.assertTrue(dsl_1.add_variable("var1", "", [], "ctx1")[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables("ctx1")[1]), [("var1", "", [])])
        self.assertEqual(dsl_1.produce(), "[\n@ctx1 {opt1: \"\" / opt2: \"\"}\nvar1 = \"\"\n]")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes=False))
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables()), var_fmt_helper(dsl_2.get_all_variables()))
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce23(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes=False))
        self.assertTrue(dsl_1.add_context(None, "ctx1", [("opt1", "abc"), ("opt2", "def")])[0])
        self.assertTrue(dsl_1.add_variable("var1", "", [], "ctx1")[0])
        self.assertEqual(var_fmt_helper(dsl_1.get_all_variables("ctx1")[1]), [("var1", "", [])])
        self.assertEqual(dsl_1.produce(), "[\n@ctx1 {opt1: \"abc\" / opt2: \"def\"}\nvar1 = \"\"\n]")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Config(allow_var_dupes=False))
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

    def testDslType20_TestGetContextOptions1(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl.add_context(None, "ctx1", [("opt1", "val1")])[0])
        v, r = dsl.get_context_options("ctx1")
        self.assertTrue(v)
        self.assertEqual(len(r), 1)
        self.assertEqual([(x.get_name(), x.get_value()) for x in r], [("opt1", "val1")])

    def testDslType20_TestGetContextOptions2(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Config())
        self.assertTrue(dsl.add_context(None, "ctx1", [("opt1", "val1"), ("opt2", "val2")])[0])
        v, r = dsl.get_context_options("ctx1")
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertEqual([(x.get_name(), x.get_value()) for x in r], [("opt1", "val1"), ("opt2", "val2")])

if __name__ == '__main__':
    unittest.main()
