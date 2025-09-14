#!/usr/bin/env python

import os
import unittest

import props

class PropsTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):
        return True, ""

    def tearDown(self):
        pass

    def testMaxOf1(self):
        self.assertEqual(props.max_of(5, 7), 5)

    def testMaxOf2(self):
        self.assertEqual(props.max_of(7, 5), 5)

    def testGetFromMapIfPresent1(self):
        self.assertEqual(props.get_from_map_if_present({"a": 1}, "a"), (True, 1))

    def testGetFromMapIfPresent2(self):
        self.assertEqual(props.get_from_map_if_present({"b": 2}, "a"), (False, None))

    def testGetFromMapIfPresent3(self):
        self.assertEqual(props.get_from_map_if_present(["b", 2], "b"), (False, None))

    def testGetFromMapIfPresent4(self):
        self.assertEqual(props.get_from_map_if_present(None, "b"), (False, None))

    def testSetupProp1(self):
        self.assertEqual(props.setup_prop(0, 5, {"a": 1}, "a"), 1)

    def testSetupProp2(self):
        self.assertEqual(props.setup_prop(0, 5, {"a": 1}, "b"), 0)

    def testSetupProp3(self):
        self.assertEqual(props.setup_prop(0, 5, {"a": 6}, "a"), 5)

if __name__ == "__main__":
    unittest.main()
