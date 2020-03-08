#!/usr/bin/python3

import os
import shutil
import unittest

import create_and_write_file
import mvtools_test_fixture

import path_utils
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

        self.reserved_test_env_var_1 = "$MVTOOLS_TEST_DSLTYPE20_ENVVAR_RESERVED_1"
        if self.reserved_test_env_var_1[1:] in os.environ:
            return False, "Environment variable [%s] is in use. This test requires it to be undefined." % (self.reserved_test_env_var_1[1:])
        self.reserved_test_env_var_2 = "$MVTOOLS_TEST_DSLTYPE20_ENVVAR_RESERVED_2"
        if self.reserved_test_env_var_2[1:] in os.environ:
            return False, "Environment variable [%s] is in use. This test requires it to be undefined." % (self.reserved_test_env_var_2[1:])

        self.contents_cfg_test_ok_1 = "var1 = \"val1\"" + os.linesep
        self.contents_cfg_test_ok_1 += "var2 {opt1} = \"val2\"" + os.linesep
        self.contents_cfg_test_ok_1 += "var3 {opt2: \"val3\"} = \"val4\"" + os.linesep
        self.contents_cfg_test_ok_1 += "var4 {opt3: \"val5\" / opt4: \"val6\"} = \"val7\"" + os.linesep
        self.contents_cfg_test_ok_1 += "var5 {opt5 / opt6: \"val8\" / opt7: \"val9\"} = \"val10\"" + os.linesep
        self.cfg_test_ok_1 = path_utils.concat_path(self.test_dir, "test_ok_1.cfg")

        self.contents_cfg_test_ok_2 = "var1 = \"val1\"" + os.linesep
        self.contents_cfg_test_ok_2 += "var2 = \"a/path/valid1\"" + os.linesep
        self.contents_cfg_test_ok_2 += "var3 {opt1 / opt2: \"a/path/valid2\"} = \"a/path/valid3\"" + os.linesep
        self.contents_cfg_test_ok_2 += "var4 = \"$SOME_ENV_VAR\"" + os.linesep
        self.contents_cfg_test_ok_2 += "var5 {r1 / r1} = \"repeated1\"" + os.linesep
        self.contents_cfg_test_ok_2 += "var5 {r2 / r2} = \"repeated2\"" + os.linesep
        self.cfg_test_ok_2 = path_utils.concat_path(self.test_dir, "test_ok_2.cfg")

        self.contents_cfg_test_ok_3 = "var1 = \"val1\"" + os.linesep
        self.contents_cfg_test_ok_3 += "var2 = \"val2\"" + os.linesep
        self.cfg_test_ok_3 = path_utils.concat_path(self.test_dir, "test_ok_3.cfg")

        self.contents_cfg_test_ok_4 = ("var1 = \"%s\"" + os.linesep) % self.reserved_test_env_var_1
        self.contents_cfg_test_ok_4 += ("var2 {opt1: \"%s\"} = \"val1\"" + os.linesep) % self.reserved_test_env_var_2
        self.cfg_test_ok_4 = path_utils.concat_path(self.test_dir, "test_ok_4.cfg")

        self.contents_cfg_test_fail_1 = "var1 = val1" + os.linesep
        self.cfg_test_fail_1 = path_utils.concat_path(self.test_dir, "test_fail_1.cfg")

        self.contents_cfg_test_fail_2 = "var1" + os.linesep
        self.cfg_test_fail_2 = path_utils.concat_path(self.test_dir, "test_fail_2.cfg")

        self.contents_cfg_test_fail_3 = "{var1 = \"val1\"}" + os.linesep
        self.cfg_test_fail_3 = path_utils.concat_path(self.test_dir, "test_fail_3.cfg")

        self.contents_cfg_test_fail_4 = "{fakeopt} var1 = \"val1\"" + os.linesep
        self.cfg_test_fail_4 = path_utils.concat_path(self.test_dir, "test_fail_4.cfg")

        create_and_write_file.create_file_contents(self.cfg_test_ok_1, self.contents_cfg_test_ok_1)
        create_and_write_file.create_file_contents(self.cfg_test_ok_2, self.contents_cfg_test_ok_2)
        create_and_write_file.create_file_contents(self.cfg_test_ok_3, self.contents_cfg_test_ok_3)
        create_and_write_file.create_file_contents(self.cfg_test_ok_4, self.contents_cfg_test_ok_4)
        create_and_write_file.create_file_contents(self.cfg_test_fail_1, self.contents_cfg_test_fail_1)
        create_and_write_file.create_file_contents(self.cfg_test_fail_2, self.contents_cfg_test_fail_2)
        create_and_write_file.create_file_contents(self.cfg_test_fail_3, self.contents_cfg_test_fail_3)
        create_and_write_file.create_file_contents(self.cfg_test_fail_4, self.contents_cfg_test_fail_4)

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def parse_test_aux(self, filename, _expand_envvars):
        contents = getcontents(filename)
        if contents is None:
            self.fail("Unable to open and read file [%s]" % self.cfg_test_ok_1)

        dsl = dsl_type20.DSLType20(_expand_envvars)
        v, r = dsl.parse(contents)
        return v

    def testDslType20_Parse1(self):
        self.assertTrue(self.parse_test_aux(self.cfg_test_ok_1, False))

    def testDslType20_Parse2(self):
        self.assertTrue(self.parse_test_aux(self.cfg_test_ok_2, False))

    def testDslType20_Parse3(self):
        self.assertFalse(self.parse_test_aux(self.cfg_test_fail_1, False))

    def testDslType20_Parse4(self):
        self.assertFalse(self.parse_test_aux(self.cfg_test_fail_2, False))

    def testDslType20_Parse5(self):
        self.assertFalse(self.parse_test_aux(self.cfg_test_fail_3, False))

    def testDslType20_Parse6(self):
        self.assertFalse(self.parse_test_aux(self.cfg_test_fail_4, False))

    def testDslType20_GetVars1(self):

        dsl = dsl_type20.DSLType20(False)
        v, r = dsl.parse(self.contents_cfg_test_ok_1)
        self.assertTrue(v)

        self.assertEqual(dsl.getvars("var0"), [])
        self.assertEqual(dsl.getvars("var1"), [("var1", "val1", [])])
        self.assertEqual(dsl.getvars("var2"), [("var2", "val2", [("opt1", "")])])
        self.assertEqual(dsl.getvars("var3"), [("var3", "val4", [("opt2", "val3")])])
        self.assertEqual(dsl.getvars("var4"), [("var4", "val7", [("opt3", "val5"), ("opt4", "val6")])])
        self.assertEqual(dsl.getvars("var5"), [("var5", "val10", [("opt5", ""), ("opt6", "val8"), ("opt7", "val9")])])
        self.assertEqual(dsl.getvars("var6"), [])

        self.assertTrue(dsl_type20.hasopt_var(dsl.getvars("var2")[0], "opt1"))
        self.assertTrue(dsl_type20.hasopt_var(dsl.getvars("var3")[0], "opt2"))
        self.assertFalse(dsl_type20.hasopt_var(dsl.getvars("var3")[0], "opt3"))

        self.assertTrue(dsl_type20.hasopt_opts(dsl.getvars("var2")[0][2], "opt1"))
        self.assertTrue(dsl_type20.hasopt_opts(dsl.getvars("var3")[0][2], "opt2"))

        self.assertEqual(dsl_type20.getopts(dsl.getvars("var2")[0], "opt1"), [("opt1", "")])

    def testDslType20_GetVars2(self):

        dsl = dsl_type20.DSLType20(False)
        v, r = dsl.parse(self.contents_cfg_test_ok_2)
        self.assertTrue(v)

        self.assertEqual(dsl.getvars("var0"), [])
        self.assertEqual(dsl.getvars("var1"), [("var1", "val1", [])])
        self.assertEqual(dsl.getvars("var2"), [("var2", "a/path/valid1", [])])
        self.assertEqual(dsl.getvars("var3"), [("var3", "a/path/valid3", [("opt1", ""), ("opt2", "a/path/valid2")])])
        self.assertEqual(dsl.getvars("var4"), [("var4", "$SOME_ENV_VAR", [])])
        self.assertEqual(dsl.getvars("var5"), [("var5", "repeated1", [("r1", ""), ("r1", "")]), ("var5", "repeated2", [("r2", ""), ("r2", "")])])
        self.assertEqual(dsl.getvars("var6"), [])

        self.assertEqual(dsl_type20.getopts(dsl.getvars("var5")[0], "r1"), [("r1", ""), ("r1", "")])
        self.assertEqual(dsl_type20.getopts(dsl.getvars("var5")[1], "r1"), [])
        self.assertEqual(dsl_type20.getopts(dsl.getvars("var5")[1], "r2"), [("r2", ""), ("r2", "")])

    def testDslType20_GetVars3(self):

        dsl = dsl_type20.DSLType20(False)
        v, r = dsl.parse(self.contents_cfg_test_ok_3)
        self.assertTrue(v)

        self.assertEqual(dsl.getallvars(), [("var1", "val1", []), ("var2", "val2", [])])

    def testDslType20_GetVars4(self):
        #credit: https://stackoverflow.com/questions/2059482/python-temporarily-modify-the-current-processs-environment/34333710
        _environ = os.environ.copy()
        try:
            os.environ[ (self.reserved_test_env_var_1[1:]) ] = "test-value-1"
            os.environ[ (self.reserved_test_env_var_2[1:]) ] = "test-value-2"

            dsl = dsl_type20.DSLType20(True)
            v, r = dsl.parse(self.contents_cfg_test_ok_4)

            self.assertTrue(v)
            self.assertEqual(dsl.getallvars(), [("var1", "test-value-1", []), ("var2", "val1", [("opt1","test-value-2")])])
        finally:
            os.environ.clear()
            os.environ.update(_environ)

if __name__ == '__main__':
    unittest.main()
