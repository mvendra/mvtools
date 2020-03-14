#!/usr/bin/python3

import os
import shutil
import unittest

import miniparse

class MiniparseTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):
        return True, ""

    def tearDown(self):
        pass

    def testPopSurroundingChar(self):
        v, r = miniparse.pop_surrounding_char("!bugger@", "!", "@")
        self.assertTrue(v)
        self.assertEqual(r, "bugger")

        v, r = miniparse.pop_surrounding_char("bugger@", "!", "@")
        self.assertFalse(v)
        self.assertEqual(r, "bugger")

        v, r = miniparse.pop_surrounding_char("!bugger", "!", "@")
        self.assertFalse(v)
        self.assertEqual(r, "bugger")

    def testGetOpt(self):
        p1, p2 = miniparse.opt_get(None, ":")
        self.assertEqual(p1, None)
        self.assertEqual(p2, None)

        p1, p2 = miniparse.opt_get("", ":")
        self.assertEqual(p1, None)
        self.assertEqual(p2, None)

        p1, p2 = miniparse.opt_get("param", ":")
        self.assertEqual(p1, "param")
        self.assertEqual(p2, "")

        p1, p2 = miniparse.opt_get("param: value", ":")
        self.assertEqual(p1, "param")
        self.assertEqual(p2, None)

        p1, p2 = miniparse.opt_get("param: \"value", ":")
        self.assertEqual(p1, "param")
        self.assertEqual(p2, None)

        p1, p2 = miniparse.opt_get("   param: \"value \" ", ":")
        self.assertEqual(p1, "param")
        self.assertEqual(p2, "value ")

    def testGuardedSplit(self):

        p = miniparse.guarded_split("var", "=", [("\"", "\"")])
        self.assertEqual(p, ["var"])

        p = miniparse.guarded_split("", "=", [("\"", "\"")])
        self.assertEqual(p, [])

        p = miniparse.guarded_split(None, "=", [("\"", "\"")])
        self.assertEqual(p, None)

        p = miniparse.guarded_split("a=b", "=", [("\"", "\"")])
        self.assertEqual(p, ["a", "b"])

        p = miniparse.guarded_split("variable = \"val=ue\"", "=", [("\"", "\"")])
        self.assertEqual(p, ["variable ", " \"val=ue\""])

        p = miniparse.guarded_split("variable {param1: \"pval1\"} = \"value1\"", "=", [("\"", "\"")])
        self.assertEqual(p, ["variable {param1: \"pval1\"} ", " \"value1\""])

        p = miniparse.guarded_split("variable {param1 = \"pval1\"} = \"value1\"", "=", [("\"", "\"")])
        self.assertEqual(p, ["variable {param1 ", " \"pval1\"} ", " \"value1\""])

        p = miniparse.guarded_split("variable {param1 = \"pval1\"} = \"value1\"", "=", [("\"", "\""), ("{", "}")])
        self.assertEqual(p, ["variable {param1 = \"pval1\"} ", " \"value1\""])

        p = miniparse.guarded_split("aaa{b]=bb}=ccc", "=", [("[", "]"), ("{", "}")])
        self.assertEqual(p, ["aaa{b]=bb}", "ccc"])

        p = miniparse.guarded_split("aaa{b[=bb}=ccc", "=", [("[", "]"), ("{", "}")])
        self.assertEqual(p, ["aaa{b[=bb}", "ccc"])

        p = miniparse.guarded_split("aaa{b[]=bb}=ccc", "=", [("[", "]"), ("{", "}")])
        self.assertEqual(p, ["aaa{b[]=bb}", "ccc"])

if __name__ == '__main__':
    unittest.main()
