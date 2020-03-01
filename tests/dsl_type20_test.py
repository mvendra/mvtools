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
        create_and_write_file.create_file_contents(self.cfg_test_fail_1, self.contents_cfg_test_fail_1)
        create_and_write_file.create_file_contents(self.cfg_test_fail_2, self.contents_cfg_test_fail_2)
        create_and_write_file.create_file_contents(self.cfg_test_fail_3, self.contents_cfg_test_fail_3)
        create_and_write_file.create_file_contents(self.cfg_test_fail_4, self.contents_cfg_test_fail_4)

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def parse_test_aux(self, filename):
        contents = getcontents(filename)
        if contents is None:
            self.fail("Unable to open and read file [%s]" % self.cfg_test_ok_1)

        dsl = dsl_type20.DSLType20()
        v, r = dsl.parse(contents)
        return v

    def testDslType20_Parse1(self):
        self.assertTrue(self.parse_test_aux(self.cfg_test_ok_1))

    def testDslType20_Parse2(self):
        self.assertTrue(self.parse_test_aux(self.cfg_test_ok_2))

    def testDslType20_Parse3(self):
        self.assertFalse(self.parse_test_aux(self.cfg_test_fail_1))

    def testDslType20_Parse4(self):
        self.assertFalse(self.parse_test_aux(self.cfg_test_fail_2))

    def testDslType20_Parse5(self):
        self.assertFalse(self.parse_test_aux(self.cfg_test_fail_3))

    def testDslType20_Parse6(self):
        self.assertFalse(self.parse_test_aux(self.cfg_test_fail_4))

    def testDslType20_GetVar1(self):

        dsl = dsl_type20.DSLType20()
        v, r = dsl.parse(self.contents_cfg_test_ok_1)
        self.assertTrue(v)

        self.assertEqual(dsl.getvars("var0"), [])
        self.assertEqual(dsl.getvars("var1"), [("var1", "val1", [])])
        self.assertEqual(dsl.getvars("var2"), [("var2", "val2", [("opt1", "")])])
        self.assertEqual(dsl.getvars("var3"), [("var3", "val4", [("opt2", "val3")])])
        self.assertEqual(dsl.getvars("var4"), [("var4", "val7", [("opt3", "val5"), ("opt4", "val6")])])
        self.assertEqual(dsl.getvars("var5"), [("var5", "val10", [("opt5", ""), ("opt6", "val8"), ("opt7", "val9")])])
        self.assertEqual(dsl.getvars("var6"), [])

    def testDslType20_GetVar2(self):

        dsl = dsl_type20.DSLType20()
        v, r = dsl.parse(self.contents_cfg_test_ok_2)
        self.assertTrue(v)

        self.assertEqual(dsl.getvars("var0"), [])
        self.assertEqual(dsl.getvars("var1"), [("var1", "val1", [])])
        self.assertEqual(dsl.getvars("var2"), [("var2", "a/path/valid1", [])])
        self.assertEqual(dsl.getvars("var3"), [("var3", "a/path/valid3", [("opt1", ""), ("opt2", "a/path/valid2")])])
        self.assertEqual(dsl.getvars("var4"), [("var4", "$SOME_ENV_VAR", [])])
        self.assertEqual(dsl.getvars("var5"), [("var5", "repeated1", [("r1", ""), ("r1", "")]), ("var5", "repeated2", [("r2", ""), ("r2", "")])])
        self.assertEqual(dsl.getvars("var6"), [])

if __name__ == '__main__':
    unittest.main()
