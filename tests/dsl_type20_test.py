#!/usr/bin/env python3

import os
import shutil
import unittest

import create_and_write_file
import mvtools_test_fixture
import path_utils
import mvtools_envvars

import dsl_type20

def getcontents(filename):
    if not os.path.exists(filename):
        return None
    contents = ""
    with open(filename) as f:
        contents = f.read()
    return contents

class DSLType20Test(unittest.TestCase):

    def setUp(self):
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

        self.contents_cfg_test_ok_1 = "var1 = \"val1\"" + os.linesep
        self.contents_cfg_test_ok_1 += "var2 {opt1} = \"val2\"" + os.linesep
        self.contents_cfg_test_ok_1 += "var3 {opt2: \"val3\"} = \"val4\"" + os.linesep
        self.contents_cfg_test_ok_1 += "var4 {opt3: \"val5\" / opt4: \"val6\"} = \"val7\"" + os.linesep
        self.contents_cfg_test_ok_1 += "var5 {opt5 / opt6: \"val8\" / opt7: \"val9\"} = \"val10\"" + os.linesep
        self.cfg_test_ok_1 = path_utils.concat_path(self.test_dir, "test_ok_1.t20")

        self.contents_cfg_test_ok_2 = "var1 = \"val1\"" + os.linesep
        self.contents_cfg_test_ok_2 += "var2 = \"a/path/valid1\"" + os.linesep
        self.contents_cfg_test_ok_2 += "var3 {opt1 / opt2: \"a/path/valid2\"} = \"a/path/valid3\"" + os.linesep
        self.contents_cfg_test_ok_2 += "var4 = \"$SOME_ENV_VAR\"" + os.linesep
        self.contents_cfg_test_ok_2 += "var5 {r1: \"\" / r1} = \"repeated1\"" + os.linesep
        self.contents_cfg_test_ok_2 += "var5 {r2 / r2} = \"repeated2\"" + os.linesep
        self.cfg_test_ok_2 = path_utils.concat_path(self.test_dir, "test_ok_2.t20")

        self.contents_cfg_test_ok_3 = "var1 = \"val1\"" + os.linesep
        self.contents_cfg_test_ok_3 += "var2 = \"val2\"" + os.linesep
        self.cfg_test_ok_3 = path_utils.concat_path(self.test_dir, "test_ok_3.t20")

        self.contents_cfg_test_ok_4 = ("var1 = \"%s\"" + os.linesep) % self.reserved_test_env_var_1
        self.contents_cfg_test_ok_4 += ("var2 {opt1: \"%s\"} = \"val1\"" + os.linesep) % self.reserved_test_env_var_2
        self.contents_cfg_test_ok_4 += ("var3 = \"%s\"" + os.linesep) % self.reserved_path_with_user_1
        self.cfg_test_ok_4 = path_utils.concat_path(self.test_dir, "test_ok_4.t20")

        self.contents_cfg_test_ok_5 = "var1 = \"val1\" # comment" + os.linesep
        self.cfg_test_ok_5 = path_utils.concat_path(self.test_dir, "test_ok_5.t20")

        self.contents_cfg_test_fail_1 = "var1 = val1" + os.linesep
        self.cfg_test_fail_1 = path_utils.concat_path(self.test_dir, "test_fail_1.t20")

        self.contents_cfg_test_fail_2 = "var1" + os.linesep
        self.cfg_test_fail_2 = path_utils.concat_path(self.test_dir, "test_fail_2.t20")

        self.contents_cfg_test_fail_3 = "{var1 = \"val1\"}" + os.linesep
        self.cfg_test_fail_3 = path_utils.concat_path(self.test_dir, "test_fail_3.t20")

        self.contents_cfg_test_fail_4 = "{fakeopt} var1 = \"val1\"" + os.linesep
        self.cfg_test_fail_4 = path_utils.concat_path(self.test_dir, "test_fail_4.t20")

        self.contents_cfg_test_fail_5 = "var1 {opt1: \"val1} = \"val2\"" + os.linesep
        self.cfg_test_fail_5 = path_utils.concat_path(self.test_dir, "test_fail_5.t20")

        create_and_write_file.create_file_contents(self.cfg_test_ok_1, self.contents_cfg_test_ok_1)
        create_and_write_file.create_file_contents(self.cfg_test_ok_2, self.contents_cfg_test_ok_2)
        create_and_write_file.create_file_contents(self.cfg_test_ok_3, self.contents_cfg_test_ok_3)
        create_and_write_file.create_file_contents(self.cfg_test_ok_4, self.contents_cfg_test_ok_4)
        create_and_write_file.create_file_contents(self.cfg_test_ok_5, self.contents_cfg_test_ok_5)
        create_and_write_file.create_file_contents(self.cfg_test_fail_1, self.contents_cfg_test_fail_1)
        create_and_write_file.create_file_contents(self.cfg_test_fail_2, self.contents_cfg_test_fail_2)
        create_and_write_file.create_file_contents(self.cfg_test_fail_3, self.contents_cfg_test_fail_3)
        create_and_write_file.create_file_contents(self.cfg_test_fail_4, self.contents_cfg_test_fail_4)
        create_and_write_file.create_file_contents(self.cfg_test_fail_5, self.contents_cfg_test_fail_5)

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def parse_test_aux(self, filename, _dsl_t20_opts):
        contents = getcontents(filename)
        if contents is None:
            self.fail("Unable to open and read file [%s]" % self.cfg_test_ok_1)

        dsl = dsl_type20.DSLType20(_dsl_t20_opts)
        v, r = dsl.parse(contents)
        return v

    def testDslType20_SanitizeLine(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        self.assertEqual(dsl.sanitize_line(""), "")
        self.assertEqual(dsl.sanitize_line("abc"), "abc")
        self.assertEqual(dsl.sanitize_line("#abc"), "")
        self.assertEqual(dsl.sanitize_line("abc#def"), "abc")
        self.assertEqual(dsl.sanitize_line("   abc   "), "abc")
        self.assertEqual(dsl.sanitize_line(" #   abc   "), "")
        self.assertEqual(dsl.sanitize_line("   abc   #"), "abc")
        self.assertEqual(dsl.sanitize_line("   abc   // def"), "abc")
        self.assertEqual(dsl.sanitize_line("//   abc   // def"), "")
        self.assertEqual(dsl.sanitize_line("   abc   // def   # xyz"), "abc")
        self.assertEqual(dsl.sanitize_line("   abc   # def   // xyz"), "abc")
        self.assertEqual(dsl.sanitize_line(" abc \"xyz # def \" # more"), "abc \"xyz # def \"")
        self.assertEqual(dsl.sanitize_line(" abc \"xyz // def \" // more"), "abc \"xyz // def \"")

    def testDslType20_Parse1(self):
        self.assertTrue(self.parse_test_aux(self.cfg_test_ok_1, dsl_type20.DSLType20_Options()))

    def testDslType20_Parse2(self):
        self.assertTrue(self.parse_test_aux(self.cfg_test_ok_2, dsl_type20.DSLType20_Options()))

    def testDslType20_Parse3(self):
        self.assertFalse(self.parse_test_aux(self.cfg_test_fail_1, dsl_type20.DSLType20_Options()))

    def testDslType20_Parse4(self):
        self.assertFalse(self.parse_test_aux(self.cfg_test_fail_2, dsl_type20.DSLType20_Options()))

    def testDslType20_Parse5(self):
        self.assertFalse(self.parse_test_aux(self.cfg_test_fail_3, dsl_type20.DSLType20_Options()))

    def testDslType20_Parse6(self):
        self.assertFalse(self.parse_test_aux(self.cfg_test_fail_4, dsl_type20.DSLType20_Options()))

    def testDslType20_Parse7(self):
        self.assertFalse(self.parse_test_aux(self.cfg_test_fail_5, dsl_type20.DSLType20_Options()))

    def testDslType20_Parse8(self):
        self.assertTrue(self.parse_test_aux(self.cfg_test_ok_5, dsl_type20.DSLType20_Options()))

    def testDslType20_GetVars1(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl.parse(self.contents_cfg_test_ok_1)
        self.assertTrue(v)

        self.assertEqual(dsl.get_vars("var0"), [])
        self.assertEqual(dsl.get_vars("var1"), [("var1", "val1", [])])
        self.assertEqual(dsl.get_vars("var2"), [("var2", "val2", [("opt1", None)])])
        self.assertEqual(dsl.get_vars("var3"), [("var3", "val4", [("opt2", "val3")])])
        self.assertEqual(dsl.get_vars("var4"), [("var4", "val7", [("opt3", "val5"), ("opt4", "val6")])])
        self.assertEqual(dsl.get_vars("var5"), [("var5", "val10", [("opt5", None), ("opt6", "val8"), ("opt7", "val9")])])
        self.assertEqual(dsl.get_vars("var6"), [])

        self.assertTrue(dsl_type20.hasopt_var(dsl.get_vars("var2")[0], "opt1"))
        self.assertTrue(dsl_type20.hasopt_var(dsl.get_vars("var3")[0], "opt2"))
        self.assertFalse(dsl_type20.hasopt_var(dsl.get_vars("var3")[0], "opt3"))

        self.assertTrue(dsl_type20.hasopt_opts(dsl.get_vars("var2")[0][2], "opt1"))
        self.assertTrue(dsl_type20.hasopt_opts(dsl.get_vars("var3")[0][2], "opt2"))

        self.assertEqual(dsl_type20.getopts(dsl.get_vars("var2")[0], "opt1"), [("opt1", None)])

    def testDslType20_GetVars2(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl.parse(self.contents_cfg_test_ok_2)
        self.assertTrue(v)

        self.assertEqual(dsl.get_vars("var0"), [])
        self.assertEqual(dsl.get_vars("var1"), [("var1", "val1", [])])
        self.assertEqual(dsl.get_vars("var2"), [("var2", "a/path/valid1", [])])
        self.assertEqual(dsl.get_vars("var3"), [("var3", "a/path/valid3", [("opt1", None), ("opt2", "a/path/valid2")])])
        self.assertEqual(dsl.get_vars("var4"), [("var4", "$SOME_ENV_VAR", [])])
        self.assertEqual(dsl.get_vars("var5"), [("var5", "repeated1", [("r1", ""), ("r1", None)]), ("var5", "repeated2", [("r2", None), ("r2", None)])])
        self.assertEqual(dsl.get_vars("var6"), [])

        self.assertEqual(dsl_type20.getopts(dsl.get_vars("var5")[0], "r1"), [("r1", ""), ("r1", None)])
        self.assertEqual(dsl_type20.getopts(dsl.get_vars("var5")[1], "r1"), [])
        self.assertEqual(dsl_type20.getopts(dsl.get_vars("var5")[1], "r2"), [("r2", None), ("r2", None)])

    def testDslType20_GetVars3(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl.parse(self.contents_cfg_test_ok_3)
        self.assertTrue(v)

        self.assertEqual(dsl.get_all_vars(), [("var1", "val1", []), ("var2", "val2", [])])

    def testDslType20_GetVars4(self):
        #credit: https://stackoverflow.com/questions/2059482/python-temporarily-modify-the-current-processs-environment/34333710
        _environ = os.environ.copy()
        try:
            os.environ[ (self.reserved_test_env_var_1[1:]) ] = "test-value-1"
            os.environ[ (self.reserved_test_env_var_2[1:]) ] = "test-value-2"

            dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options(True, True))
            v, r = dsl.parse(self.contents_cfg_test_ok_4)

            self.assertTrue(v)
            self.assertEqual(dsl.get_all_vars(), [("var1", "test-value-1", []), ("var2", "val1", [("opt1","test-value-2")]), ("var3", path_utils.concat_path(os.path.expanduser("/tmp/folder")), [])])
        finally:
            os.environ.clear()
            os.environ.update(_environ)

    def testDslType20_GetVars5(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        self.assertTrue(dsl.add_context("ctx1", [("opt1", "val1")]))
        self.assertTrue(dsl.add_var("var1", "val2", [ ], "ctx1" ))
        self.assertEqual(dsl.get_all_vars("ctx1"), [("var1", "val2", [])])

    def testDslType20_GetVars6(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options(vars_auto_ctx_options=True))
        self.assertTrue(dsl.add_context("ctx1", [("opt1", "val1")]))
        self.assertTrue(dsl.add_var("var1", "val2", [ ], "ctx1" ))
        self.assertEqual(dsl.get_all_vars("ctx1"), [("var1", "val2", [("opt1", "val1")])])

    def testDslType20_TestVanilla1(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl.parse("var1 = \"val1\"")
        self.assertTrue(v)

        self.assertEqual(dsl.get_all_vars(), [("var1", "val1", [])])

    def testDslType20_TestVanilla2(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl.parse("var1 {opt1} = \"val1\"")
        self.assertTrue(v)

        self.assertEqual(dsl.get_all_vars(), [("var1", "val1", [("opt1", None)])])

    def testDslType20_TestParseDecoratedVar1(self):

        decorated_var = "* var1 {opt1} = \"val1\""

        dsl1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl1.parse(decorated_var)
        self.assertFalse(v)

        dsl2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Options(variable_decorator = "* "))
        v, r = dsl2.parse(decorated_var)
        self.assertTrue(v)

        self.assertEqual(dsl2.get_all_vars(), [("var1", "val1", [("opt1", None)])])

    def testDslType20_TestParseDecoratedVar2(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options(variable_decorator = "**"))
        v, r = dsl.parse("** var1 {opt1} = \"val1\"")
        self.assertTrue(v)

    def testDslType20_TestParseDecoratedVarFail1(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options(variable_decorator = "* "))
        v, r = dsl.parse("*var1 {opt1} = \"val1\"")
        self.assertFalse(v)

    def testDslType20_TestParseDecoratedVarFail2(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options(variable_decorator = "* "))
        v, r = dsl.parse("* ")
        self.assertFalse(v)

    def testDslType20_TestParseDecoratedVarFail3(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options(variable_decorator = "**"))
        v, r = dsl.parse("* var1 {opt1} = \"val1\"")
        self.assertFalse(v)

    def testDslType20_TestNonEscapedQuoteVarVal(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl.parse("var1 = \"val \"1\"\"")
        self.assertFalse(v)

    def testDslType20_TestNonEscapedQuoteVarOptVal(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl.parse("var1 {opt1: \"val \"2\"\"} = \"val \\\"1\\\"\"")
        self.assertFalse(v)

    def testDslType20_TestSlashInsideVarOptVal1(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl.parse("var1   {  _opt-1   :    \"val \\\\  =  \\\"1/2\\\"\" / opt2  :  \"val = \\\"2/4\\\"\" }     =  \"val = \\\"1\\\"\"  ")
        self.assertTrue(v)

        self.assertEqual(dsl.get_all_vars(), [("var1", "val = \"1\"", [("_opt-1", "val \\  =  \"1/2\""), ("opt2", "val = \"2/4\"")])])

    def testDslType20_TestCommentInsideVarOptVal1(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl.parse("var1 { remote_link : \"https://www.url.net/folder/whatever\" } = \"svn.py\"")
        self.assertTrue(v)

        self.assertEqual(dsl.get_all_vars(), [("var1", "svn.py", [("remote_link", "https://www.url.net/folder/whatever")])])

    def testDslType20_TestBlankAndNoneOption(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl.parse("var1 {opt1: \"\" / opt2} = \"val1\"")
        self.assertTrue(v)

        self.assertEqual(dsl.get_all_vars(), [("var1", "val1", [("opt1", ""), ("opt2", None)])])

    def testDslType20_TestSpacedOptionValueless1(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl.parse("    var1   {  the_option     }     =    \"val1\"  ")
        self.assertTrue(v)

        self.assertEqual(dsl.get_all_vars(), [("var1", "val1", [("the_option", None)])])

    def testDslType20_TestSpacedOptionValueless2(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl.parse("    var1   {  the_option1   /   the_option2    }     =    \"val1\"  ")
        self.assertTrue(v)

        self.assertEqual(dsl.get_all_vars(), [("var1", "val1", [("the_option1", None), ("the_option2", None)])])

    def testDslType20_TestOptionsAlternated1(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl.parse("var1 {opt1 / opt2: \"val2\" / opt3 / opt4: \"val3\"} = \"val1\"")
        self.assertTrue(v)

        self.assertEqual(dsl.get_all_vars(), [("var1", "val1", [("opt1", None), ("opt2", "val2"), ("opt3", None), ("opt4", "val3")])])

    def testDslType20_TestOptionsAlternated2(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl.parse("var1 {opt2: \"val2\" / opt1 / opt4: \"val3\" / opt3} = \"val1\"")
        self.assertTrue(v)

        self.assertEqual(dsl.get_all_vars(), [("var1", "val1", [("opt2", "val2"), ("opt1", None), ("opt4", "val3"), ("opt3", None)])])

    def testDslType20_TestMalformedOptName(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl.parse("var1 {opt=1: \"optval\"} = \"val1\"")
        self.assertFalse(v)

    def testDslType20_TestMalformedValueQuotesEscaped1(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl.parse("var1 = \"val1\\\"")
        self.assertFalse(v)

    def testDslType20_TestMalformedValueQuotesEscaped2(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl.parse("var1 = \\\"val1\"")
        self.assertFalse(v)

    def testDslType20_TestVarValueParsing1(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl.parse("var1 = \"   val1\"")
        self.assertTrue(v)

        self.assertEqual(dsl.get_all_vars(), [("var1", "   val1", [])])

    def testDslType20_TestVarValueParsing2(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl.parse("var1 = \"val1   \"")
        self.assertTrue(v)

        self.assertEqual(dsl.get_all_vars(), [("var1", "val1   ", [])])

    def testDslType20_TestVarValueParsing3(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl.parse("var1 = \"val1   val2\"")
        self.assertTrue(v)

        self.assertEqual(dsl.get_all_vars(), [("var1", "val1   val2", [])])

    def testDslType20_TestOptValueParsing1(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl.parse("var1 {opt1: \"   val2\"} = \"val1\"")
        self.assertTrue(v)

        self.assertEqual(dsl.get_all_vars(), [("var1", "val1", [("opt1", "   val2")])])

    def testDslType20_TestOptValueParsing2(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl.parse("var1 {opt1: \"val2   \"} = \"val1\"")
        self.assertTrue(v)

        self.assertEqual(dsl.get_all_vars(), [("var1", "val1", [("opt1", "val2   ")])])

    def testDslType20_TestOptValueParsing3(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl.parse("var1 {opt1: \"val2   val3\"} = \"val1\"")
        self.assertTrue(v)

        self.assertEqual(dsl.get_all_vars(), [("var1", "val1", [("opt1", "val2   val3")])])

    def testDslType20_TestUnspacing(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl.parse("var1{opt1/opt2/opt3:\"val\\\"2\"}=\"val1\"")
        self.assertTrue(v)

        self.assertEqual(dsl.get_all_vars(), [("var1", "val1", [("opt1", None), ("opt2", None), ("opt3", "val\"2")])])

    def testDslType20_TestLeftoversFail1(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl.parse("var1 abc = \"val1\"")
        self.assertFalse(v)

    def testDslType20_TestLeftoversFail2(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl.parse("var1 = abc \"val1\"")
        self.assertFalse(v)

    def testDslType20_TestLeftoversFail3(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl.parse("var1 = \"val1\" abc")
        self.assertFalse(v)

    def testDslType20_TestLeftoversFail4(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl.parse("var1 = {opt1} \"val1\"")
        self.assertFalse(v)

    def testDslType20_TestLeftoversFail5(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl.parse("var1 {opt1 opt2} = \"val1\"")
        self.assertFalse(v)

    def testDslType20_TestLeftoversFail6(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl.parse("var1 {opt1 /} = \"val1\"")
        self.assertFalse(v)

    def testDslType20_TestLeftoversFail7(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl.parse("var1 {{opt1} = \"val1\"")
        self.assertFalse(v)

    def testDslType20_TestLeftoversFail8(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl.parse("var1 {opt1}} = \"val1\"")
        self.assertFalse(v)

    def testDslType20_TestLeftoversFail9(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl.parse("var1 {opt1} abc = \"val1\"")
        self.assertFalse(v)

    def testDslType20_TestLeftoversFail10(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl.parse("var1 == \"val1\"")
        self.assertFalse(v)

    def testDslType20_TestLeftoversFail11(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl.parse("var1 {opt1} == \"val1\"")
        self.assertFalse(v)

    def testDslType20_TestExceedMaxNumberOptionsFail(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        dsl.max_number_options = 2
        v, r = dsl.parse("var1 {opt1 / opt2 / opt3} == \"val1\"")
        self.assertFalse(v)

    def testDslType20_TestNewContextVanilla1(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl.parse("var1 = \"val1\"\n[\n@ctx1\n]")
        self.assertTrue(v)
        self.assertEqual(dsl.get_all_vars(), [("var1", "val1", [])])

    def testDslType20_TestNewContextVanilla2(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl.parse("var1 = \"val1\"\n[\n@ctx1\nvar2 = \"val2\"\n]")
        self.assertTrue(v)
        self.assertEqual(dsl.get_all_vars(), [("var1", "val1", [])])
        self.assertEqual(dsl.get_all_vars("ctx1"), [("var2", "val2", [])])

    def testDslType20_TestNewContextVanilla3(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl.parse("var1 = \"val1\"\n[\n@ctx1\nvar2 {opt1 / opt2} = \"val2\"\n]\nvar3 = \"val3\"\n[\n@ctx2\nvar4 = \"val4\"\n]")
        self.assertTrue(v)
        self.assertEqual(dsl.get_all_vars(), [("var1", "val1", []), ("var3", "val3", [])])
        self.assertEqual(dsl.get_all_vars("ctx1"), [("var2", "val2", [("opt1", None), ("opt2", None)])])
        self.assertEqual(dsl.get_all_vars("ctx2"), [("var4", "val4", [])])

    def testDslType20_TestNewContextWithOptions1(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options(vars_auto_ctx_options=True))
        v, r = dsl.parse("[\n@ctx1 {opt1}\nvar1 = \"val1\"\n]")
        self.assertEqual(dsl.get_vars("var1", "ctx1"), [("var1", "val1", [("opt1", None)])])
        self.assertTrue(v)

    def testDslType20_TestNewContextWithOptions2(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options(vars_auto_ctx_options=True))
        v, r = dsl.parse("[\n@ctx1 {opt2: \"val2\"}\nvar1 = \"val1\"\n]")
        self.assertTrue(v)
        self.assertEqual(dsl.get_vars("var1", "ctx1"), [("var1", "val1", [("opt2", "val2")])])

    def testDslType20_TestNewContextWithOptions3(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options(vars_auto_ctx_options=True))
        v, r = dsl.parse("[\n@ctx1 {opt3: \"val3\"}\nvar1 {opt4: \"val4\"} = \"val1\"\n]")
        self.assertTrue(v)
        self.assertEqual(dsl.get_vars("var1", "ctx1"), [("var1", "val1", [("opt3", "val3"), ("opt4", "val4")])])

    def testDslType20_TestNewContextWithOptions4(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options(vars_auto_ctx_options=True))
        v, r = dsl.parse("[\n@ctx1 {opt1: \"val1\"}\nvar1 {opt1: \"val3\"} = \"val2\"\n]")
        self.assertTrue(v)
        self.assertEqual(dsl.get_vars("var1", "ctx1"), [("var1", "val2", [("opt1", "val1"), ("opt1", "val3")])])

    def testDslType20_TestNewContextWithOptions5(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options(allow_dupes=False))
        v, r = dsl.parse("[\n@ctx1 {opt1: \"val1\"}\nvar1 {opt1: \"val3\"} = \"val2\"\n]")
        self.assertTrue(v)
        self.assertEqual(dsl.get_vars("var1", "ctx1"), [("var1", "val2", [("opt1", "val3")])])

    def testDslType20_TestNewContextFail1(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl.parse("var1 = \"val1\"\n@ctx1\nvar2 = \"val2\"\n]")
        self.assertFalse(v)

    def testDslType20_TestNewContextFail2(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl.parse("var1 = \"val1\"\n[\n[\n@ctx1\n]")
        self.assertFalse(v)

    def testDslType20_TestNewContextFail3(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl.parse("var1 = \"val1\"\n[\n]")
        self.assertFalse(v)

    def testDslType20_TestNewContextFail4(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl.parse("var1 = \"val1\"\n[\n")
        self.assertFalse(v)

    def testDslType20_TestNewContextFail5(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl.parse("var1 = \"val1\"\n[\n@@ctx1\n]")
        self.assertFalse(v)

    def testDslType20_TestNewContextFail6(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl.parse("var1 = \"val1\"\n[\n@ctx 1\n]")
        self.assertFalse(v)

    def testDslType20_TestNewContextFail7(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl.parse("[\n@ctx1\nvar1 = \"val1\"\n")
        self.assertFalse(v)

    def testDslType20_TestNewContextFail8(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl.parse("\n[\nvar1 = \"val1\"\n]\n")
        self.assertFalse(v)

    def testDslType20_TestNewContextFail9(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl.parse("\n[\n]\n")
        self.assertFalse(v)

    def testDslType20_TestContextFail1(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl._parse_variable("var1 = \"val1\"", "nonexistent context")
        self.assertFalse(v)

    def testDslType20_TestContextReopenFail(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl.parse("[\n@ctx1\nvar1 = \"val1\"\n]\nvar2 = \"val2\"\n[\n@ctx1\nvar3 = \"val3\"\n]")
        self.assertFalse(v)

    def testDslType20_TestContextGetAllVarsFail1(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl.parse("[\n@ctx1\nvar1 = \"val1\"\n]")
        self.assertTrue(v)
        self.assertEqual(dsl.get_all_vars("ctx1"), [("var1", "val1", [])])
        self.assertEqual(dsl.get_all_vars("nonexistent context"), None)

    def testDslType20_TestContextGetVarsFail1(self):

        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl.parse("[\n@ctx1\nvar1 = \"val1\"\n]")

        self.assertTrue(v)
        self.assertEqual(dsl.get_vars("var1", None), [])
        self.assertEqual(dsl.get_vars("var1", "ctx1"), [("var1", "val1", [])])
        self.assertEqual(dsl.get_vars("var1", "nonexistent context"), None)

    def testDslType20_TestAddContext1(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        self.assertTrue(dsl.add_context("ok", []))

    def testDslType20_TestAddContext2(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        self.assertTrue(dsl.add_context("ok1", []))

    def testDslType20_TestAddContext3(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        self.assertTrue(dsl.add_context("_ok-90", []))

    def testDslType20_TestAddContext4(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        self.assertTrue(dsl.add_context("ok", [("var1", "val1")]))

    def testDslType20_TestGetAllContexts1(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        self.assertTrue(dsl.add_context("ctx1", []))
        self.assertTrue(dsl.add_context("ctx2", []))
        self.assertEqual(dsl.get_all_contexts(), ["ctx1", "ctx2"])

    def testDslType20_TestGetAllContexts2(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        self.assertTrue(dsl.add_context("ctx1", []))
        self.assertTrue(dsl.add_context("ctx2", []))
        v, r = dsl.add_context("ctx 3", [])
        self.assertFalse(v)
        self.assertTrue(dsl.add_context("ctx4", []))
        self.assertEqual(dsl.get_all_contexts(), ["ctx1", "ctx2", "ctx4"])

    def testDslType20_TestAddContextFail1(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl.add_context([], [])
        self.assertFalse(v)

    def testDslType20_TestAddContextFail2(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl.add_context("", [])
        self.assertFalse(v)

    def testDslType20_TestAddContextFail3(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl.add_context("ok!", [])
        self.assertFalse(v)

    def testDslType20_TestAddContextFail4(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl.add_context("@ok", [])
        self.assertFalse(v)

    def testDslType20_TestAddContextFail5(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl.add_context("ok", [])
        self.assertTrue(v)
        v, r = dsl.add_context("ok", [])
        self.assertFalse(v)

    def testDslType20_TestAddContextFail6(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl.add_context("ok", "nok")
        self.assertFalse(v)

    def testDslType20_TestAddVar1(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        self.assertTrue(dsl.add_var("var1", "", [ ] ))
        self.assertEqual(dsl.get_all_vars(), [ ("var1", "", [ ]) ] )

    def testDslType20_TestAddVar2(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        self.assertTrue(dsl.add_var("var1", "val1", [ ] ))
        self.assertEqual(dsl.get_all_vars(), [ ("var1", "val1", [ ]) ] )

    def testDslType20_TestAddVar3(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        self.assertTrue(dsl.add_var("var1", "val1", [ ("opt1", "val2") ] ))
        self.assertEqual(dsl.get_all_vars(), [ ("var1", "val1", [ ("opt1", "val2") ]) ] )

    def testDslType20_TestAddVar4(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        self.assertTrue(dsl.add_var("var1", "val1", [ ("opt1", "val2"), ("opt1", "val2") ] ))
        self.assertEqual(dsl.get_all_vars(), [ ("var1", "val1", [ ("opt1", "val2"), ("opt1", "val2") ]) ] )

    def testDslType20_TestAddVar5(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        self.assertTrue(dsl.add_var("var1", "val1", [ ("opt1", "val2"), ("opt1", "val2") ] ))
        self.assertTrue(dsl.add_var("var1", "val1", [ ("opt1", "val2"), ("opt1", "val2") ] ))
        self.assertEqual(dsl.get_all_vars(), [ ("var1", "val1", [ ("opt1", "val2"), ("opt1", "val2") ]), ("var1", "val1", [ ("opt1", "val2"), ("opt1", "val2") ]) ] )

    def testDslType20_TestAddVar6(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options(vars_auto_ctx_options=True))
        self.assertTrue(dsl.add_context("ctx1", [("opt1", "val1")]))
        self.assertTrue(dsl.add_var("var1", "val2", [ ("opt2", "val3") ], "ctx1" ))
        self.assertEqual(dsl.get_vars("var1", "ctx1"), [("var1", "val2", [("opt1", "val1"), ("opt2", "val3")] )])
        self.assertEqual(dsl.get_all_vars("ctx1"), [ ("var1", "val2", [("opt1", "val1"), ("opt2", "val3")] ) ] )

    def testDslType20_TestAddVar7(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options(vars_auto_ctx_options=True))
        self.assertTrue(dsl.add_context("ctx1", [("opt1", "val1")]))
        self.assertTrue(dsl.add_var("var1", "val2", [ ("opt1", "val3") ], "ctx1" ))
        self.assertEqual(dsl.get_vars("var1", "ctx1"), [("var1", "val2", [("opt1", "val1"), ("opt1", "val3")] )])
        self.assertEqual(dsl.get_all_vars("ctx1"), [ ("var1", "val2", [("opt1", "val1"), ("opt1", "val3")] ) ] )

    def testDslType20_TestAddVar8(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options(allow_dupes=False))
        self.assertTrue(dsl.add_context("ctx1", [("opt1", "val1")]))
        self.assertTrue(dsl.add_var("var1", "val2", [ ("opt1", "val3") ], "ctx1" ))
        self.assertEqual(dsl.get_vars("var1", "ctx1"), [("var1", "val2", [("opt1", "val3")] )])
        self.assertEqual(dsl.get_all_vars("ctx1"), [ ("var1", "val2", [("opt1", "val3")] ) ] )

    def testDslType20_TestAddVarFail1(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        self.assertFalse(dsl.add_var("var1", None, [ ] ))

    def testDslType20_TestAddVarFail2(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        self.assertFalse(dsl.add_var("var1", [], [ ] ))

    def testDslType20_TestAddVarFail3(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        self.assertFalse(dsl.add_var("var1", "val1", [ ("opt") ] ))

    def testDslType20_TestAddVarFail4(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        self.assertFalse(dsl.add_var("var1", "val1", [ ("opt", 1) ] ))

    def testDslType20_TestAddVarFail5(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        self.assertFalse(dsl.add_var("var1", "val1", [ ("opt", "val", "again") ] ))

    def testDslType20_TestAddVarFail6(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        self.assertFalse(dsl.add_var("var1", "val1", [ ["opt", "val"] ] ))

    def testDslType20_TestAddVarFail7(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        self.assertFalse(dsl.add_var("var1", "val1", [ None ] ))

    def testDslType20_TestAddVarFail8(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        self.assertFalse(dsl.add_var("var1", "val1", None ))

    def testDslType20_TestAddVarFail9(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        self.assertFalse(dsl.add_var(1, "val1", [ ("opt", "val") ] ))

    def testDslType20_TestAddVarFail10(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        self.assertFalse(dsl.add_var(None, "val1", [ ("opt", "val") ] ))

    def testDslType20_TestCountOccurrenceFirstOfPair1(self):
        self.assertEqual(dsl_type20.count_occurrence_first_of_pair( [ ("b", None) ], "a" ), 0)

    def testDslType20_TestCountOccurrenceFirstOfPair2(self):
        self.assertEqual(dsl_type20.count_occurrence_first_of_pair( [ ("b", None) ], "b" ), 1)

    def testDslType20_TestCountOccurrenceFirstOfPair3(self):
        self.assertEqual(dsl_type20.count_occurrence_first_of_pair( [ ("b", None), ("b", None) ], "b" ), 2)

    def testDslType20_TestDisallowDupes1(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options(allow_dupes=False))
        self.assertTrue(dsl.add_var("var1", "val1", []))
        self.assertFalse(dsl.add_var("var1", "val2", []))

    def testDslType20_TestDisallowDupes2(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options(allow_dupes=False))
        self.assertTrue(dsl.add_var("var1", "val1", [ ("opt1", None) ] ))

    def testDslType20_TestDisallowDupes3(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options(allow_dupes=False))
        self.assertFalse(dsl.add_var("var1", "val1", [ ("opt1", None), ("opt1", None) ] ))

    def testDslType20_TestDisallowDupes4(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options(allow_dupes=False))
        self.assertTrue(dsl.add_var("var1", "val1", [ ("opt1", None) ] ))
        self.assertTrue(dsl.add_var("var2", "val1", [ ("opt1", None) ] ))

    def testDslType20_TestDisallowDupesParse1(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options(allow_dupes=False))

        contents_cfg_test_fail_dupevar = "var1 = \"val1\"" + os.linesep
        contents_cfg_test_fail_dupevar += "var1 = \"val2\"" + os.linesep

        v, r = dsl.parse(contents_cfg_test_fail_dupevar)
        self.assertFalse(v)

    def testDslType20_TestRemVar1(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        self.assertTrue(dsl.add_var("var1", "val1", []))
        self.assertEqual(dsl.get_all_vars(), [ ("var1", "val1", []) ] )
        self.assertTrue(dsl.rem_var("var1"))
        self.assertEqual(dsl.get_all_vars(), [] )

    def testDslType20_TestRemVar2(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        self.assertTrue(dsl.add_var("var1", "val1", []))
        self.assertEqual(dsl.get_all_vars(), [ ("var1", "val1", []) ] )
        self.assertTrue(dsl.rem_var("var1", 0))
        self.assertEqual(dsl.get_all_vars(), [] )

    def testDslType20_TestRemVar3(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        self.assertTrue(dsl.add_var("var1", "val1", []))
        self.assertEqual(dsl.get_all_vars(), [ ("var1", "val1", []) ] )
        self.assertFalse(dsl.rem_var("var1", 1))
        self.assertEqual(dsl.get_all_vars(), [ ("var1", "val1", []) ] )

    def testDslType20_TestRemVar4(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        self.assertTrue(dsl.add_var("var1", "val1", []))
        self.assertTrue(dsl.add_var("var1", "val2", []))
        self.assertEqual(dsl.get_all_vars(), [ ("var1", "val1", []), ("var1", "val2", []) ] )
        self.assertTrue(dsl.rem_var("var1", 1))
        self.assertEqual(dsl.get_all_vars(), [("var1", "val1", [])] )

    def testDslType20_TestRemVar5(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        self.assertTrue(dsl.add_var("var1", "val1", []))
        self.assertEqual(dsl.get_all_vars(), [ ("var1", "val1", []) ] )
        self.assertFalse(dsl.rem_var("var2"))
        self.assertEqual(dsl.get_all_vars(), [ ("var1", "val1", []) ] )

    def testDslType20_TestRemVar6(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        self.assertTrue(dsl.add_var("var1", "val2", []))
        self.assertTrue(dsl.add_var("var1", "val4", [], "ctx1"))
        self.assertEqual(dsl.get_all_vars(), [ ("var1", "val2", []) ] )
        self.assertEqual(dsl.get_all_vars("ctx1"), [ ("var1", "val4", []) ] )

        self.assertTrue(dsl.rem_var("var1", None, "ctx1"))
        self.assertEqual(dsl.get_all_vars(), [ ("var1", "val2", []) ] )
        self.assertEqual(dsl.get_all_vars("ctx1"), [] )

    def testDslType20_TestRemCtx1(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        self.assertFalse(dsl.rem_ctx(None))

    def testDslType20_TestRemCtx2(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        self.assertFalse(dsl.rem_ctx(dsl.default_context_id))

    def testDslType20_TestRemCtx3(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        self.assertFalse(dsl.rem_ctx("ctx1"))

    def testDslType20_TestRemCtx4(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        self.assertTrue(dsl.add_context("ctx1", []))
        self.assertTrue("ctx1" in dsl.get_all_contexts() )
        self.assertTrue(dsl.rem_ctx("ctx1"))
        self.assertFalse("ctx1" in dsl.get_all_contexts() )

    def testDslType20_TestRemCtx5(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        self.assertTrue(dsl.add_context("ctx1", []))
        self.assertTrue(dsl.add_context("ctx2", []))
        self.assertTrue("ctx1" in dsl.get_all_contexts() )
        self.assertTrue("ctx2" in dsl.get_all_contexts() )
        self.assertTrue(dsl.rem_ctx("ctx1"))
        self.assertFalse("ctx1" in dsl.get_all_contexts() )
        self.assertTrue("ctx2" in dsl.get_all_contexts() )

    def testDslType20_TestProduce1(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        self.assertTrue(dsl_1.add_var("var1", "val1", []))
        self.assertEqual(dsl_1.get_all_vars(), [("var1", "val1", [])])
        self.assertEqual(dsl_1.produce(), "var1 = \"val1\"")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(dsl_1.get_all_vars(), dsl_2.get_all_vars())
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce2(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        self.assertTrue(dsl_1.add_var("var1", "val1", []))
        self.assertTrue(dsl_1.add_var("var2", "val2", []))
        self.assertEqual(dsl_1.get_all_vars(), [("var1", "val1", []), ("var2", "val2", [])])
        self.assertEqual(dsl_1.produce(), "var1 = \"val1\"\nvar2 = \"val2\"")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(dsl_1.get_all_vars(), dsl_2.get_all_vars())
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce3(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        self.assertTrue(dsl_1.add_var("var1", "val1", [], "ctx1"))
        self.assertTrue(dsl_1.add_var("var2", "val2", []))
        self.assertTrue(dsl_1.add_var("var1", "val1", [], "ctx2"))
        self.assertTrue(dsl_1.add_var("var2", "val2", [], "ctx2"))
        self.assertEqual(dsl_1.get_all_vars(), [("var2", "val2", [])])
        self.assertEqual(dsl_1.get_all_vars("ctx1"), [("var1", "val1", [])])
        self.assertEqual(dsl_1.get_all_vars("ctx2"), [("var1", "val1", []), ("var2", "val2", [])])
        self.assertEqual(dsl_1.produce(), "var2 = \"val2\"\n[\n@ctx1\nvar1 = \"val1\"\n]\n\n[\n@ctx2\nvar1 = \"val1\"\nvar2 = \"val2\"\n]")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(dsl_1.get_all_vars(), dsl_2.get_all_vars())
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce4(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        self.assertTrue(dsl_1.add_var("var1", "val\"1\"", [], "ctx1"))
        self.assertEqual(dsl_1.get_all_vars("ctx1"), [("var1", "val\"1\"", [])])
        self.assertEqual(dsl_1.produce(), "[\n@ctx1\nvar1 = \"val\\\"1\\\"\"\n]")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(dsl_1.get_all_vars(), dsl_2.get_all_vars())
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce5(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        self.assertTrue(dsl_1.add_var("var1", "val\"1\"", [("opt1", None)], "ctx1"))
        self.assertEqual(dsl_1.get_all_vars("ctx1"), [("var1", "val\"1\"", [("opt1", None)])])
        self.assertEqual(dsl_1.produce(), "[\n@ctx1\nvar1 {opt1} = \"val\\\"1\\\"\"\n]")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(dsl_1.get_all_vars(), dsl_2.get_all_vars())
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce6(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        self.assertTrue(dsl_1.add_var("var1", "val1", [("opt1", "val2")], "ctx1"))
        self.assertEqual(dsl_1.get_all_vars("ctx1"), [("var1", "val1", [("opt1", "val2")])])
        self.assertEqual(dsl_1.produce(), "[\n@ctx1\nvar1 {opt1: \"val2\"} = \"val1\"\n]")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(dsl_1.get_all_vars(), dsl_2.get_all_vars())
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce7(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        self.assertTrue(dsl_1.add_var("var1", "val\"1\"", [("opt1", "val\"2\"")], "ctx1"))
        self.assertEqual(dsl_1.get_all_vars("ctx1"), [("var1", "val\"1\"", [("opt1", "val\"2\"")])])
        self.assertEqual(dsl_1.produce(), "[\n@ctx1\nvar1 {opt1: \"val\\\"2\\\"\"} = \"val\\\"1\\\"\"\n]")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(dsl_1.get_all_vars(), dsl_2.get_all_vars())
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce8(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Options(vars_auto_ctx_options=True))
        self.assertTrue(dsl_1.add_context("ctx1", [("opt1", "val2")]))
        self.assertTrue(dsl_1.add_var("var1", "val1", [], "ctx1"))
        self.assertEqual(dsl_1.get_all_vars("ctx1"), [("var1", "val1", [("opt1", "val2")])])
        self.assertEqual(dsl_1.produce(), "[\n@ctx1 {opt1: \"val2\"}\nvar1 = \"val1\"\n]")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(dsl_1.get_all_vars(), dsl_2.get_all_vars())
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce9(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Options(vars_auto_ctx_options=True))
        self.assertTrue(dsl_1.add_context("ctx1", [("opt1", "val1")]))
        self.assertTrue(dsl_1.add_var("var1", "val2", [("opt1", "val3")], "ctx1"))
        self.assertEqual(dsl_1.get_all_vars("ctx1"), [("var1", "val2", [("opt1", "val1"), ("opt1", "val3")])])
        self.assertEqual(dsl_1.produce(), "[\n@ctx1 {opt1: \"val1\"}\nvar1 {opt1: \"val3\"} = \"val2\"\n]")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(dsl_1.get_all_vars(), dsl_2.get_all_vars())
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce10(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Options(allow_dupes=False))
        self.assertTrue(dsl_1.add_context("ctx1", [("opt1", "val1")]))
        self.assertTrue(dsl_1.add_var("var1", "val2", [("opt1", "val3")], "ctx1"))
        self.assertEqual(dsl_1.get_all_vars("ctx1"), [("var1", "val2", [("opt1", "val3")])])
        self.assertEqual(dsl_1.produce(), "[\n@ctx1 {opt1: \"val1\"}\nvar1 {opt1: \"val3\"} = \"val2\"\n]")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Options(allow_dupes=False))
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(dsl_1.get_all_vars(), dsl_2.get_all_vars())
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestProduce11(self):
        dsl_1 = dsl_type20.DSLType20(dsl_type20.DSLType20_Options(variable_decorator="* "))
        self.assertTrue(dsl_1.add_var("var1", "val1", []))
        self.assertEqual(dsl_1.get_all_vars(), [("var1", "val1", [])])
        self.assertEqual(dsl_1.produce(), "* var1 = \"val1\"")

        dsl_2 = dsl_type20.DSLType20(dsl_type20.DSLType20_Options(variable_decorator="* "))
        v, r = dsl_2.parse(dsl_1.produce())
        self.assertTrue(v)
        self.assertEqual(r, None)
        self.assertEqual(dsl_1.get_all_vars(), dsl_2.get_all_vars())
        self.assertEqual(dsl_1.produce(), dsl_2.produce())

    def testDslType20_TestGetContextOptions1(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        self.assertTrue(dsl.add_context("ctx1", [("var1", "val1")]))
        self.assertEqual(dsl.get_context_options("ctx1"), [("var1", "val1")])

    def testDslType20_TestGetContextOptions2(self):
        dsl = dsl_type20.DSLType20(dsl_type20.DSLType20_Options())
        self.assertTrue(dsl.add_context("ctx1", [("var1", "val1"), ("var2", "val2")]))
        self.assertEqual(dsl.get_context_options("ctx1"), [("var1", "val1"), ("var2", "val2")])

if __name__ == '__main__':
    unittest.main()
