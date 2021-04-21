#!/usr/bin/env python3

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

    def testDeleteIndicesFromString1(self):
        self.assertEqual(miniparse.delete_indices_from_string(None, [1, 2]), None)

    def testDeleteIndicesFromString2(self):
        self.assertEqual(miniparse.delete_indices_from_string("", [1, 2]), None)

    def testDeleteIndicesFromString3(self):
        self.assertEqual(miniparse.delete_indices_from_string([], [1, 2]), None)

    def testDeleteIndicesFromString4(self):
        self.assertEqual(miniparse.delete_indices_from_string("aaa", None), None)

    def testDeleteIndicesFromString5(self):
        self.assertEqual(miniparse.delete_indices_from_string("aaa", ""), None)

    def testDeleteIndicesFromString6(self):
        self.assertEqual(miniparse.delete_indices_from_string("aaa", []), None)

    def testDeleteIndicesFromString7(self):
        self.assertEqual(miniparse.delete_indices_from_string("aaa", [1]), "aa")

    def testDeleteIndicesFromString8(self):
        self.assertEqual(miniparse.delete_indices_from_string("abcdef", [1, 3]), "acef")

    def testDeleteIndicesFromString9(self):
        self.assertEqual(miniparse.delete_indices_from_string("bbb", [6, 8]), None)

    def testDeleteIndicesFromString10(self):
        self.assertEqual(miniparse.delete_indices_from_string("abc", [0, 0]), "bc")

    def testDeleteIndicesFromString11(self):
        self.assertEqual(miniparse.delete_indices_from_string("abc", [-1]), None)

    def testPopSurroundingChar1(self):
        v, r = miniparse.pop_surrounding_char("!bugger@", "!", "@")
        self.assertTrue(v)
        self.assertEqual(r, "bugger")

    def testPopSurroundingChar2(self):
        v, r = miniparse.pop_surrounding_char("bugger@", "!", "@")
        self.assertFalse(v)
        self.assertEqual(r, "bugger")

    def testPopSurroundingChar3(self):
        v, r = miniparse.pop_surrounding_char("!bugger", "!", "@")
        self.assertFalse(v)
        self.assertEqual(r, "bugger")

    def testGetOpt1(self):
        p1, p2 = miniparse.opt_get(None, ":")
        self.assertEqual(p1, None)
        self.assertEqual(p2, None)

    def testGetOpt2(self):
        p1, p2 = miniparse.opt_get("", ":")
        self.assertEqual(p1, None)
        self.assertEqual(p2, None)

    def testGetOpt3(self):
        p1, p2 = miniparse.opt_get("param", ":")
        self.assertEqual(p1, "param")
        self.assertEqual(p2, "")

    def testGetOpt4(self):
        p1, p2 = miniparse.opt_get("param: value", ":")
        self.assertEqual(p1, "param")
        self.assertEqual(p2, None)

    def testGetOpt5(self):
        p1, p2 = miniparse.opt_get("param: \"value", ":")
        self.assertEqual(p1, "param")
        self.assertEqual(p2, None)

    def testGetOpt6(self):
        p1, p2 = miniparse.opt_get("   param: \"value \" ", ":")
        self.assertEqual(p1, "param")
        self.assertEqual(p2, "value ")

    def testGuardedSplit1(self):
        p = miniparse.guarded_split("var", "=", [("\"", "\"")])
        self.assertEqual(p, ["var"])

    def testGuardedSplit2(self):
        p = miniparse.guarded_split("", "=", [("\"", "\"")])
        self.assertEqual(p, [])

    def testGuardedSplit3(self):
        p = miniparse.guarded_split(None, "=", [("\"", "\"")])
        self.assertEqual(p, None)

    def testGuardedSplit4(self):
        p = miniparse.guarded_split("a=b", "=", [("\"", "\"")])
        self.assertEqual(p, ["a", "b"])

    def testGuardedSplit5(self):
        p = miniparse.guarded_split("variable = \"val=ue\"", "=", [("\"", "\"")])
        self.assertEqual(p, ["variable ", " \"val=ue\""])

    def testGuardedSplit6(self):
        p = miniparse.guarded_split("variable {param1: \"pval1\"} = \"value1\"", "=", [("\"", "\"")])
        self.assertEqual(p, ["variable {param1: \"pval1\"} ", " \"value1\""])

    def testGuardedSplit7(self):
        p = miniparse.guarded_split("variable {param1 = \"pval1\"} = \"value1\"", "=", [("\"", "\"")])
        self.assertEqual(p, ["variable {param1 ", " \"pval1\"} ", " \"value1\""])

    def testGuardedSplit8(self):
        p = miniparse.guarded_split("variable {param1 = \"pval1\"} = \"value1\"", "=", [("\"", "\""), ("{", "}")])
        self.assertEqual(p, ["variable {param1 = \"pval1\"} ", " \"value1\""])

    def testGuardedSplit9(self):
        p = miniparse.guarded_split("aaa{b]=bb}=ccc", "=", [("[", "]"), ("{", "}")])
        self.assertEqual(p, ["aaa{b]=bb}", "ccc"])

    def testGuardedSplit10(self):
        p = miniparse.guarded_split("aaa{b[=bb}=ccc", "=", [("[", "]"), ("{", "}")])
        self.assertEqual(p, ["aaa{b[=bb}", "ccc"])

    def testGuardedSplit11(self):
        p = miniparse.guarded_split("aaa{b[]=bb}=ccc", "=", [("[", "]"), ("{", "}")])
        self.assertEqual(p, ["aaa{b[]=bb}", "ccc"])

    def testGuardedSplit12(self):
        p = miniparse.guarded_split("aaa{b[]=bb}=ccc", "=", [("[", "]"), ("{", "}")])
        self.assertEqual(p, ["aaa{b[]=bb}", "ccc"])

    def testGuardedRightCut1(self):
        p = miniparse.guarded_right_cut([], ["#"], "'")
        self.assertEqual(p, None)

    def testGuardedRightCut2(self):
        p = miniparse.guarded_right_cut("", ["#"], "'")
        self.assertEqual(p, None)

    def testGuardedRightCut3(self):
        p = miniparse.guarded_right_cut("abc", (), "'")
        self.assertEqual(p, None)

    def testGuardedRightCut4(self):
        p = miniparse.guarded_right_cut("abc", [], "'")
        self.assertEqual(p, None)

    def testGuardedRightCut5(self):
        p = miniparse.guarded_right_cut("abc", ["#"], "")
        self.assertEqual(p, None)

    def testGuardedRightCut6(self):
        p = miniparse.guarded_right_cut("abc", ["#"], [])
        self.assertEqual(p, None)

    def testGuardedRightCut7(self):
        p = miniparse.guarded_right_cut("abc", ["#"], "#")
        self.assertEqual(p, None)

    def testGuardedRightCut8(self):
        p = miniparse.guarded_right_cut("abc", ["#"], "'")
        self.assertEqual(p, "abc")

    def testGuardedRightCut9(self):
        p = miniparse.guarded_right_cut("abc #def", ["#"], "'")
        self.assertEqual(p, "abc ")

    def testGuardedRightCut10(self):
        p = miniparse.guarded_right_cut("abc ##def", ["#"], "'")
        self.assertEqual(p, "abc ")

    def testGuardedRightCut11(self):
        p = miniparse.guarded_right_cut("##abc ##def", ["#"], "'")
        self.assertEqual(p, "")

    def testGuardedRightCut12(self):
        p = miniparse.guarded_right_cut("abc 'def'", ["#"], "'")
        self.assertEqual(p, "abc 'def'")

    def testGuardedRightCut13(self):
        p = miniparse.guarded_right_cut("abc 'def' #more", ["#"], "'")
        self.assertEqual(p, "abc 'def' ")

    def testGuardedRightCut14(self):
        p = miniparse.guarded_right_cut("abc 'def' //more", ["/", "/"], "'")
        self.assertEqual(p, "abc 'def' ")

    def testGuardedRightCut15(self):
        p = miniparse.guarded_right_cut("abc 'def' /more", ["/", "/"], "'")
        self.assertEqual(p, "abc 'def' /more")

    def testGuardedRightCut16(self):
        p = miniparse.guarded_right_cut("//abc 'def' /more", ["/", "/"], "'")
        self.assertEqual(p, "")

    def testGuardedRightCut17(self):
        p = miniparse.guarded_right_cut("//abc 'def' /more", ["/", "/", "/"], "'")
        self.assertEqual(p, "//abc 'def' /more")

    def testGuardedRightCut18(self):
        p = miniparse.guarded_right_cut("///abc 'def' /more", ["/", "/", "/"], "'")
        self.assertEqual(p, "")

    def testGuardedRightCut19(self):
        p = miniparse.guarded_right_cut("#abc 'def' /more", ["#"], "'")
        self.assertEqual(p, "")

    def testGuardedRightCut20(self):
        p = miniparse.guarded_right_cut("#abc 'def' ###more", ["#"], "'")
        self.assertEqual(p, "")

    def testGuardedRightCut21(self):
        p = miniparse.guarded_right_cut("#abc 'def' ###more", ["#", "#"], "'")
        self.assertEqual(p, "#abc 'def' ")

    def testGuardedRightCut22(self):
        p = miniparse.guarded_right_cut("abc 'def #xyz'", ["#"], "'")
        self.assertEqual(p, "abc 'def #xyz'")

    def testGuardedRightCut23(self):
        p = miniparse.guarded_right_cut("abc 'def ##xyz'", ["#"], "'")
        self.assertEqual(p, "abc 'def ##xyz'")

    def testGuardedRightCut24(self):
        p = miniparse.guarded_right_cut("abc 'def ##xyz' #more", ["#"], "'")
        self.assertEqual(p, "abc 'def ##xyz' ")

    def testGuardedRightCut25(self):
        p = miniparse.guarded_right_cut("abc 'def ##xyz #more", ["#"], "'")
        self.assertEqual(p, "abc 'def ##xyz #more")

    def testGuardedRightCut26(self):
        p = miniparse.guarded_right_cut("abc 'def //xyz' //more", ["/", "/"], "'")
        self.assertEqual(p, "abc 'def //xyz' ")

    def testGuardedRightCut27(self):
        p = miniparse.guarded_right_cut("abc 'def //xyz //more", ["/", "/"], "'")
        self.assertEqual(p, "abc 'def //xyz //more")

    def testGuardedRightCut28(self):
        p = miniparse.guarded_right_cut("abc 'def' '//xyz' //more", ["/", "/"], "'")
        self.assertEqual(p, "abc 'def' '//xyz' ")

    def testGuardedRightCut29(self):
        p = miniparse.guarded_right_cut("abc 'def' '//xyz //more", ["/", "/"], "'")
        self.assertEqual(p, "abc 'def' '//xyz //more")

    def testGuardedRightCut30(self):
        p = miniparse.guarded_right_cut("abc 'def' '//xyz //more", ["#", "/"], "'")
        self.assertEqual(p, "abc 'def' '//xyz //more")

    def testGuardedRightCut31(self):
        p = miniparse.guarded_right_cut("#/abc 'def' '//xyz //more", ["#", "/"], "'")
        self.assertEqual(p, "")

    def testGuardedRightCut32(self):
        p = miniparse.guarded_right_cut("abc", ["#", "/", "#", "/"], "'")
        self.assertEqual(p, "abc")

    def testGuardedRightCut33(self):
        p = miniparse.guarded_right_cut("a#/#/bc", ["#", "/", "#", "/"], "'")
        self.assertEqual(p, "a")

    def testGuardedRightCut34(self):
        p = miniparse.guarded_right_cut("'a#/#/bc", ["#", "/", "#", "/"], "'")
        self.assertEqual(p, "'a#/#/bc")

    def testGuardedRightCut35(self):
        p = miniparse.guarded_right_cut("''a#/#/bc", ["#", "/", "#", "/"], "'")
        self.assertEqual(p, "''a")

    def testGuardedRightCut36(self):
        p = miniparse.guarded_right_cut("abc'", ["#"], "'")
        self.assertEqual(p, "abc'")

    def testGuardedRightCut37(self):
        p = miniparse.guarded_right_cut("abc'#", ["#"], "'")
        self.assertEqual(p, "abc'#")

    def testGuardedRightCut38(self):
        p = miniparse.guarded_right_cut("abc''#", ["#"], "'")
        self.assertEqual(p, "abc''")

    def testSplitNext1(self):
        p = miniparse.split_next(None, None)
        self.assertEqual(p, None)

    def testSplitNext2(self):
        p = miniparse.split_next([], ["abc"])
        self.assertEqual(p, None)

    def testSplitNext3(self):
        p = miniparse.split_next("aaa =   bbb", None)
        self.assertEqual(p, None)

    def testSplitNext4(self):
        p = miniparse.split_next("aaa =   bbb", [])
        self.assertEqual(p, None)

    def testSplitNext5(self):
        p = miniparse.split_next("aaa =   bbb", ["="])
        self.assertEqual(p, ("aaa ", "=   bbb"))

    def testSplitNext6(self):
        p = miniparse.split_next("aaa =  : bbb", ["=", ":"])
        self.assertEqual(p, ("aaa ", "=  : bbb"))

    def testSplitNext7(self):
        p = miniparse.split_next("aaa :  = bbb", ["=", ":"])
        self.assertEqual(p, ("aaa ", ":  = bbb"))

    def testSplitNext8(self):
        p = miniparse.split_next("aaa =  : bbb", [":", "="])
        self.assertEqual(p, ("aaa ", "=  : bbb"))

    def testSplitNext9(self):
        p = miniparse.split_next("aaa =  : bbb", ["%", "*"])
        self.assertEqual(p, None)

    def testSplitLast1(self):
        p = miniparse.split_last(None, None)
        self.assertEqual(p, None)

    def testSplitLast2(self):
        p = miniparse.split_last([], ["abc"])
        self.assertEqual(p, None)

    def testSplitLast3(self):
        p = miniparse.split_last("aaa =   bbb", None)
        self.assertEqual(p, None)

    def testSplitLast4(self):
        p = miniparse.split_last("aaa =   bbb", [])
        self.assertEqual(p, None)

    def testSplitLast5(self):
        p = miniparse.split_last("aaa =  : bbb", ["%", "*"])
        self.assertEqual(p, None)

    def testSplitLast6(self):
        p = miniparse.split_last("aaa = bbb = ccc", ["="])
        self.assertEqual(p, ("aaa = bbb ", "= ccc"))

    def testSplitLast7(self):
        p = miniparse.split_last("aaa = bbb ! ccc", ["!", "="])
        self.assertEqual(p, ("aaa = bbb ", "! ccc"))

    def testSplitLast8(self):
        p = miniparse.split_last("aaa = bbb ! ccc = ddd", ["!", "="])
        self.assertEqual(p, ("aaa = bbb ! ccc ", "= ddd"))

    def testSplitLast9(self):
        p = miniparse.split_last("aaa = bbb ! ccc = ddd", ["=", "!"])
        self.assertEqual(p, ("aaa = bbb ! ccc ", "= ddd"))

    def testRemoveNextOf1(self):
        v, r = miniparse.remove_next_of(None, None)
        self.assertEqual(v, False)
        self.assertEqual(r, None)

    def testRemoveNextOf2(self):
        v, r = miniparse.remove_next_of("", None)
        self.assertEqual(v, False)
        self.assertEqual(r, None)

    def testRemoveNextOf3(self):
        v, r = miniparse.remove_next_of("", "")
        self.assertEqual(v, False)
        self.assertEqual(r, None)

    def testRemoveNextOf4(self):
        v, r = miniparse.remove_next_of(None, "")
        self.assertEqual(v, False)
        self.assertEqual(r, None)

    def testRemoveNextOf5(self):
        v, r = miniparse.remove_next_of([], "!")
        self.assertEqual(v, False)
        self.assertEqual(r, None)

    def testRemoveNextOf6(self):
        v, r = miniparse.remove_next_of(" abc", [])
        self.assertEqual(v, False)
        self.assertEqual(r, None)

    def testRemoveNextOf7(self):
        v, r = miniparse.remove_next_of("= abc", "=")
        self.assertEqual(v, True)
        self.assertEqual(r, " abc")

    def testRemoveNextOf8(self):
        v, r = miniparse.remove_next_of("= abc", "!")
        self.assertEqual(v, False)
        self.assertEqual(r, "= abc")

    def testRemoveNextOf9(self):
        v, r = miniparse.remove_next_of("", "!")
        self.assertEqual(v, False)
        self.assertEqual(r, None)

    def testRemoveNextOf10(self):
        v, r = miniparse.remove_next_of(" def = abc", "=")
        self.assertEqual(v, True)
        self.assertEqual(r, " abc")

    def testRemoveNextOf11(self):
        v, r = miniparse.remove_next_of(" def = abc=", "=")
        self.assertEqual(v, True)
        self.assertEqual(r, " abc=")

    def testRemoveNextOf12(self):
        v, r = miniparse.remove_next_of(" def = abc=", "!")
        self.assertEqual(v, False)
        self.assertEqual(r, " def = abc=")

    def testRemoveNextOf13(self):
        v, r = miniparse.remove_next_of(" def  abc=", "=")
        self.assertEqual(v, True)
        self.assertEqual(r, "")

    def testRemoveNextOf14(self):
        v, r = miniparse.remove_next_of("\"", "\"")
        self.assertEqual(v, True)
        self.assertEqual(r, "")

    def testRemoveLastOf1(self):
        v, r = miniparse.remove_last_of(None, None)
        self.assertEqual(v, False)
        self.assertEqual(r, None)

    def testRemoveLastOf2(self):
        v, r = miniparse.remove_last_of("", None)
        self.assertEqual(v, False)
        self.assertEqual(r, None)

    def testRemoveLastOf3(self):
        v, r = miniparse.remove_last_of("", "")
        self.assertEqual(v, False)
        self.assertEqual(r, None)

    def testRemoveLastOf4(self):
        v, r = miniparse.remove_last_of(None, "")
        self.assertEqual(v, False)
        self.assertEqual(r, None)

    def testRemoveLastOf5(self):
        v, r = miniparse.remove_last_of([], "!")
        self.assertEqual(v, False)
        self.assertEqual(r, None)

    def testRemoveLastOf6(self):
        v, r = miniparse.remove_last_of(" abc", [])
        self.assertEqual(v, False)
        self.assertEqual(r, None)

    def testRemoveLastOf7(self):
        v, r = miniparse.remove_last_of("= abc", "=")
        self.assertEqual(v, True)
        self.assertEqual(r, "")

    def testRemoveLastOf8(self):
        v, r = miniparse.remove_last_of("= abc", "!")
        self.assertEqual(v, False)
        self.assertEqual(r, "= abc")

    def testRemoveLastOf9(self):
        v, r = miniparse.remove_last_of("", "!")
        self.assertEqual(v, False)
        self.assertEqual(r, None)

    def testRemoveLastOf10(self):
        v, r = miniparse.remove_last_of(" def = abc", "=")
        self.assertEqual(v, True)
        self.assertEqual(r, " def ")

    def testRemoveLastOf11(self):
        v, r = miniparse.remove_last_of(" def = abc=", "=")
        self.assertEqual(v, True)
        self.assertEqual(r, " def = abc")

    def testRemoveLastOf12(self):
        v, r = miniparse.remove_last_of(" def = abc=", "!")
        self.assertEqual(v, False)
        self.assertEqual(r, " def = abc=")

    def testRemoveLastOf13(self):
        v, r = miniparse.remove_last_of(" def  abc=", "=")
        self.assertEqual(v, True)
        self.assertEqual(r, " def  abc")

    def testRemoveLastOf14(self):
        v, r = miniparse.remove_last_of("\"", "\"")
        self.assertEqual(v, True)
        self.assertEqual(r, "")

    def testScanAndSliceBeginning1(self):
        v, r = miniparse.scan_and_slice_beginning(None, "x")
        self.assertEqual(v, None)
        self.assertEqual(r, None)

    def testScanAndSliceBeginning2(self):
        v, r = miniparse.scan_and_slice_beginning([], "x")
        self.assertEqual(v, None)
        self.assertEqual(r, None)

    def testScanAndSliceBeginning3(self):
        v, r = miniparse.scan_and_slice_beginning("aaa: bbb", "ccc")
        self.assertFalse(v)
        self.assertEqual(r, "aaa: bbb") 

    def testScanAndSliceBeginning4(self):
        v, r = miniparse.scan_and_slice_beginning("aaa: bbb", "aaa:")
        self.assertTrue(v)
        self.assertEqual(r, ("aaa:", " bbb"))

    def testScanAndSlice1(self):
        v, r = miniparse.scan_and_slice("aaa: -yy- bbb", "(-yy-)")
        self.assertTrue(v)
        self.assertEqual(r, ("-yy-", "aaa:  bbb"))

    def testScanAndSliceEnd1(self):
        v, r = miniparse.scan_and_slice_end("aaabbb", "bbb")
        self.assertTrue(v)
        self.assertEqual(r[0], "bbb")
        self.assertEqual(r[1], "aaa")

    def testScanAndSliceEnd2(self):
        v, r = miniparse.scan_and_slice_end("aaabbbaaaccc", "aaa")
        self.assertFalse(v)
        self.assertEqual(r, "aaabbbaaaccc")

    def testNextNotEscapedSlice1(self):
        v, r = miniparse.next_not_escaped_slice(None, "b", "c")
        self.assertFalse(v)
        self.assertEqual(r, None)

    def testNextNotEscapedSlice2(self):
        v, r = miniparse.next_not_escaped_slice([], "b", "c")
        self.assertFalse(v)
        self.assertEqual(r, None)

    def testNextNotEscapedSlice3(self):
        v, r = miniparse.next_not_escaped_slice("", "b", "c")
        self.assertFalse(v)
        self.assertEqual(r, None)

    def testNextNotEscapedSlice4(self):
        v, r = miniparse.next_not_escaped_slice("a", None, "c")
        self.assertFalse(v)
        self.assertEqual(r, None)

    def testNextNotEscapedSlice5(self):
        v, r = miniparse.next_not_escaped_slice("a", [], "c")
        self.assertFalse(v)
        self.assertEqual(r, None)

    def testNextNotEscapedSlice6(self):
        v, r = miniparse.next_not_escaped_slice("a", "", "c")
        self.assertFalse(v)
        self.assertEqual(r, None)

    def testNextNotEscapedSlice7(self):
        v, r = miniparse.next_not_escaped_slice("a", "b", None)
        self.assertFalse(v)
        self.assertEqual(r, None)

    def testNextNotEscapedSlice8(self):
        v, r = miniparse.next_not_escaped_slice("a", "b", [])
        self.assertFalse(v)
        self.assertEqual(r, None)

    def testNextNotEscapedSlice9(self):
        v, r = miniparse.next_not_escaped_slice("a", "b", "")
        self.assertFalse(v)
        self.assertEqual(r, None)

    def testNextNotEscapedSlice10(self):
        v, r = miniparse.next_not_escaped_slice(" aaa \\\" bbb \\\" ccc \" ddd", "\"", "\\")
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertEqual(r[0], " aaa \\\" bbb \\\" ccc ")
        self.assertEqual(r[1], "\" ddd")

    def testNextNotEscapedSlice11(self):
        v, r = miniparse.next_not_escaped_slice("\" aaa \\\" bbb \\\" ccc \" ddd", "\"", "\\")
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertEqual(r[0], "")
        self.assertEqual(r[1], "\" aaa \\\" bbb \\\" ccc \" ddd")

    def testNextNotEscapedSlice12(self):
        v, r = miniparse.next_not_escaped_slice("\"a", "\"", "\\")
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertEqual(r[0], "")
        self.assertEqual(r[1], "\"a")

    def testNextNotEscapedSlice13(self):
        v, r = miniparse.next_not_escaped_slice("a\"", "\"", "\\")
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertEqual(r[0], "a")
        self.assertEqual(r[1], "\"")

    def testNextNotEscapedSlice14(self):
        v, r = miniparse.next_not_escaped_slice("aaa c bbb", "q", "s")
        self.assertFalse(v)
        self.assertEqual(r, None)

    def testNextNotEscapedSlice15(self):
        v, r = miniparse.next_not_escaped_slice("aaa qc bbb", "q", "s")
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertEqual(r[0], "aaa ")
        self.assertEqual(r[1], "qc bbb")

    def testNextNotEscapedSlice16(self):
        v, r = miniparse.next_not_escaped_slice("aaa qc bqbb", "q", "s")
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertEqual(r[0], "aaa ")
        self.assertEqual(r[1], "qc bqbb")

    def testNextNotEscapedSlice17(self):
        v, r = miniparse.next_not_escaped_slice("aaa sqc bqbb", "q", "s")
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertEqual(r[0], "aaa sqc b")
        self.assertEqual(r[1], "qbb")

    def testNextNotEscapedSlice18(self):
        v, r = miniparse.next_not_escaped_slice("aaa sbbqb", "q", "s")
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertEqual(r[0], "aaa sbb")
        self.assertEqual(r[1], "qb")

    def testNextNotEscapedSlice19(self):
        v, r = miniparse.next_not_escaped_slice("aaa qbbb qccc", "q", "s")
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertEqual(r[0], "aaa ")
        self.assertEqual(r[1], "qbbb qccc")

    def testNextNotEscapedSlice20(self):
        v, r = miniparse.next_not_escaped_slice("aaa sqbbb qccc", "q", "s")
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertEqual(r[0], "aaa sqbbb ")
        self.assertEqual(r[1], "qccc")

    def testNextNotEscapedSlice21(self):
        v, r = miniparse.next_not_escaped_slice("aaaq", "q", "s")
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertEqual(r[0], "aaa")
        self.assertEqual(r[1], "q")

    def testNextNotEscapedSlice22(self):
        v, r = miniparse.next_not_escaped_slice("aaasq", "q", "s")
        self.assertFalse(v)
        self.assertEqual(r, None)

    def testLastNotEscapedSlice1(self):
        v, r = miniparse.last_not_escaped_slice(None, "b", "c")
        self.assertFalse(v)
        self.assertEqual(r, None)

    def testLastNotEscapedSlice2(self):
        v, r = miniparse.last_not_escaped_slice([], "b", "c")
        self.assertFalse(v)
        self.assertEqual(r, None)

    def testLastNotEscapedSlice3(self):
        v, r = miniparse.last_not_escaped_slice("", "b", "c")
        self.assertFalse(v)
        self.assertEqual(r, None)

    def testLastNotEscapedSlice4(self):
        v, r = miniparse.last_not_escaped_slice("a", None, "c")
        self.assertFalse(v)
        self.assertEqual(r, None)

    def testLastNotEscapedSlice5(self):
        v, r = miniparse.last_not_escaped_slice("a", [], "c")
        self.assertFalse(v)
        self.assertEqual(r, None)

    def testLastNotEscapedSlice6(self):
        v, r = miniparse.last_not_escaped_slice("a", "", "c")
        self.assertFalse(v)
        self.assertEqual(r, None)

    def testLastNotEscapedSlice7(self):
        v, r = miniparse.last_not_escaped_slice("a", "b", None)
        self.assertFalse(v)
        self.assertEqual(r, None)

    def testLastNotEscapedSlice8(self):
        v, r = miniparse.last_not_escaped_slice("a", "b", [])
        self.assertFalse(v)
        self.assertEqual(r, None)

    def testLastNotEscapedSlice9(self):
        v, r = miniparse.last_not_escaped_slice("a", "b", "")
        self.assertFalse(v)
        self.assertEqual(r, None)

    def testLastNotEscapedSlice10(self):
        v, r = miniparse.last_not_escaped_slice(" aaa \\\" bbb \\\" ccc \" ddd", "\"", "\\")
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertEqual(r[0], " ddd")
        self.assertEqual(r[1], " aaa \\\" bbb \\\" ccc \"")

    def testLastNotEscapedSlice11(self):
        v, r = miniparse.last_not_escaped_slice("\" aaa \\\" bbb \\\" ccc \" ddd", "\"", "\\")
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertEqual(r[0], " ddd")
        self.assertEqual(r[1], "\" aaa \\\" bbb \\\" ccc \"")

    def testLastNotEscapedSlice12(self):
        v, r = miniparse.last_not_escaped_slice("a\"", "\"", "\\")
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertEqual(r[0], "")
        self.assertEqual(r[1], "a\"")

    def testLastNotEscapedSlice13(self):
        v, r = miniparse.last_not_escaped_slice("\"a", "\"", "\\")
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertEqual(r[0], "a")
        self.assertEqual(r[1], "\"")

    def testLastNotEscapedSlice14(self):
        v, r = miniparse.last_not_escaped_slice("aaa c bbb", "q", "s")
        self.assertFalse(v)
        self.assertEqual(r, None)

    def testLastNotEscapedSlice15(self):
        v, r = miniparse.last_not_escaped_slice("aaa qc bbb", "q", "s")
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertEqual(r[0], "c bbb")
        self.assertEqual(r[1], "aaa q")

    def testLastNotEscapedSlice16(self):
        v, r = miniparse.last_not_escaped_slice("aaa qc bqbb", "q", "s")
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertEqual(r[0], "bb")
        self.assertEqual(r[1], "aaa qc bq")

    def testLastNotEscapedSlice17(self):
        v, r = miniparse.last_not_escaped_slice("aaa sqc bqbb", "q", "s")
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertEqual(r[0], "bb")
        self.assertEqual(r[1], "aaa sqc bq")

    def testLastNotEscapedSlice18(self):
        v, r = miniparse.last_not_escaped_slice("aaa sbbqb", "q", "s")
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertEqual(r[0], "b")
        self.assertEqual(r[1], "aaa sbbq")

    def testLastNotEscapedSlice19(self):
        v, r = miniparse.last_not_escaped_slice("aaa qbbb qccc", "q", "s")
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertEqual(r[0], "ccc")
        self.assertEqual(r[1], "aaa qbbb q")

    def testLastNotEscapedSlice20(self):
        v, r = miniparse.last_not_escaped_slice("aaa qbbb sqccc", "q", "s")
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertEqual(r[0], "bbb sqccc")
        self.assertEqual(r[1], "aaa q")

    def testLastNotEscapedSlice21(self):
        v, r = miniparse.last_not_escaped_slice("aaaq", "q", "s")
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertEqual(r[0], "")
        self.assertEqual(r[1], "aaaq")

    def testLastNotEscapedSlice22(self):
        v, r = miniparse.last_not_escaped_slice("qaaa", "q", "s")
        self.assertTrue(v)
        self.assertEqual(len(r), 2)
        self.assertEqual(r[0], "aaa")
        self.assertEqual(r[1], "q")

    def testLastNotEscapedSlice23(self):
        v, r = miniparse.last_not_escaped_slice("sqaaa", "q", "s")
        self.assertFalse(v)
        self.assertEqual(r, None)

    def testSliceLeftStrip1(self):
        v, r = miniparse.slice_left_strip(None, "a")
        self.assertFalse(v)
        self.assertEqual(r, None)

    def testSliceLeftStrip2(self):
        v, r = miniparse.slice_left_strip([], "a")
        self.assertFalse(v)
        self.assertEqual(r, None)

    def testSliceLeftStrip3(self):
        v, r = miniparse.slice_left_strip("", "a")
        self.assertFalse(v)
        self.assertEqual(r, None)

    def testSliceLeftStrip4(self):
        v, r = miniparse.slice_left_strip("aaa", None)
        self.assertFalse(v)
        self.assertEqual(r, None)

    def testSliceLeftStrip5(self):
        v, r = miniparse.slice_left_strip(None, [])
        self.assertFalse(v)
        self.assertEqual(r, None)

    def testSliceLeftStrip6(self):
        v, r = miniparse.slice_left_strip(None, "")
        self.assertFalse(v)
        self.assertEqual(r, None)

    def testSliceLeftStrip7(self):
        v, r = miniparse.slice_left_strip("aaa", "b")
        self.assertFalse(v)
        self.assertEqual(r, None)

    def testSliceLeftStrip8(self):
        v, r = miniparse.slice_left_strip("aaa:bbb", ":")
        self.assertTrue(v)
        self.assertEqual(r, "aaa")

    def testSliceLeftStrip9(self):
        v, r = miniparse.slice_left_strip(":aaabbb", ":")
        self.assertTrue(v)
        self.assertEqual(r, "")

    def testSliceLeftStrip10(self):
        v, r = miniparse.slice_left_strip(":aaa:bbb", ":")
        self.assertTrue(v)
        self.assertEqual(r, "")

    def testSliceLeftStrip11(self):
        v, r = miniparse.slice_left_strip("aaabbb:    ", ":")
        self.assertTrue(v)
        self.assertEqual(r, "aaabbb")

    def testSliceLeftStrip12(self):
        v, r = miniparse.slice_left_strip("     aaabbb:    ", ":")
        self.assertTrue(v)
        self.assertEqual(r, "aaabbb")

    def testSliceLeftStrip13(self):
        v, r = miniparse.slice_left_strip("     aaabbb     :    ", ":")
        self.assertTrue(v)
        self.assertEqual(r, "aaabbb")

    def testSliceLeftStrip14(self):
        v, r = miniparse.slice_left_strip("     aaabbb  -   :    ", ":")
        self.assertTrue(v)
        self.assertEqual(r, "aaabbb  -")

    def testDescape1(self):
        v, r = miniparse.descape(None, "s")
        self.assertFalse(v)
        self.assertEqual(r, None)

    def testDescape2(self):
        v, r = miniparse.descape([], "s")
        self.assertFalse(v)
        self.assertEqual(r, None)

    def testDescape3(self):
        v, r = miniparse.descape("", "s")
        self.assertTrue(v)
        self.assertEqual(r, "")

    def testDescape4(self):
        v, r = miniparse.descape("aaa", None)
        self.assertFalse(v)
        self.assertEqual(r, None)

    def testDescape5(self):
        v, r = miniparse.descape("aaa", [])
        self.assertFalse(v)
        self.assertEqual(r, None)

    def testDescape6(self):
        v, r = miniparse.descape("aaa", "")
        self.assertFalse(v)
        self.assertEqual(r, None)

    def testDescape7(self):
        v, r = miniparse.descape("aaa", "s")
        self.assertTrue(v)
        self.assertEqual(r, "aaa")

    def testDescape8(self):
        v, r = miniparse.descape("aasa", "s")
        self.assertTrue(v)
        self.assertEqual(r, "aaa")

    def testDescape9(self):
        v, r = miniparse.descape("ssaaa", "s")
        self.assertTrue(v)
        self.assertEqual(r, "saaa")

    def testDescape10(self):
        v, r = miniparse.descape("sbsaaa", "s")
        self.assertTrue(v)
        self.assertEqual(r, "baaa")

    def testDescape11(self):
        v, r = miniparse.descape("sssaaa", "s")
        self.assertTrue(v)
        self.assertEqual(r, "saaa")

    def testDescape12(self):
        v, r = miniparse.descape("bb", "b")
        self.assertTrue(v)
        self.assertEqual(r, "b")

    def testEscape1(self):
        v, r = miniparse.escape(None, "a", ["b"])
        self.assertFalse(v)
        self.assertEqual(r, None)

    def testEscape2(self):
        v, r = miniparse.escape([], "a", ["b"])
        self.assertFalse(v)
        self.assertEqual(r, None)

    def testEscape3(self):
        v, r = miniparse.escape("", "a", ["b"])
        self.assertFalse(v)
        self.assertEqual(r, None)

    def testEscape4(self):
        v, r = miniparse.escape("aaa", None, ["b"])
        self.assertFalse(v)
        self.assertEqual(r, None)

    def testEscape5(self):
        v, r = miniparse.escape("aaa", [], ["b"])
        self.assertFalse(v)
        self.assertEqual(r, None)

    def testEscape6(self):
        v, r = miniparse.escape("aaa", "", ["b"])
        self.assertFalse(v)
        self.assertEqual(r, None)

    def testEscape7(self):
        v, r = miniparse.escape("aaa", "a", None)
        self.assertFalse(v)
        self.assertEqual(r, None)

    def testEscape8(self):
        v, r = miniparse.escape("aaa", "a", "")
        self.assertFalse(v)
        self.assertEqual(r, None)

    def testEscape9(self):
        v, r = miniparse.escape("aaa", "a", [])
        self.assertFalse(v)
        self.assertEqual(r, None)

    def testEscape10(self):
        v, r = miniparse.escape("aaaqbbb", "s", ["q"])
        self.assertTrue(v)
        self.assertEqual(r, "aaasqbbb")

    def testEscape11(self):
        v, r = miniparse.escape("aaaqbbbqccc", "s", ["q"])
        self.assertTrue(v)
        self.assertEqual(r, "aaasqbbbsqccc")

    def testEscape12(self):
        v, r = miniparse.escape("aaaqbbsbbqccc", "s", ["q"])
        self.assertTrue(v)
        self.assertEqual(r, "aaasqbbssbbsqccc")

    def testEscape13(self):
        v, r = miniparse.escape("aqqa", "s", ["q"])
        self.assertTrue(v)
        self.assertEqual(r, "asqsqa")

    def testEscape14(self):
        v, r = miniparse.escape("aqqqa", "s", ["q"])
        self.assertTrue(v)
        self.assertEqual(r, "asqsqsqa")

    def testEscape15(self):
        v, r = miniparse.escape("cssc", "s", ["q"])
        self.assertTrue(v)
        self.assertEqual(r, "cssssc")

    def testEscape16(self):
        v, r = miniparse.escape("csssc", "s", ["q"])
        self.assertTrue(v)
        self.assertEqual(r, "cssssssc")

    def testEscape17(self):
        v, r = miniparse.escape("aqaaabssbbbcccxc", "s", ["q", "x"])
        self.assertTrue(v)
        self.assertEqual(r, "asqaaabssssbbbcccsxc")

if __name__ == '__main__':
    unittest.main()
