#!/usr/bin/env python3

import os
import shutil
import unittest

import mvtools_test_fixture

import minicron

class MinicronTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("minicron_test")
        if not v:
            return v, r
        self.test_base_dir = r[0]
        self.test_dir = r[1]

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testConvertDurationFail(self):
        self.assertEqual(minicron.convert_time_string([]), None)
        self.assertEqual(minicron.convert_time_string(""), None)
        self.assertEqual(minicron.convert_time_string("1"), None)
        self.assertEqual(minicron.convert_time_string(None), None)
        self.assertEqual(minicron.convert_time_string("1f"), None)

    def testConvertDurationOk(self):
        self.assertEqual(minicron.convert_time_string("7h"), 25200)
        self.assertEqual(minicron.convert_time_string("30m"), 1800)
        self.assertEqual(minicron.convert_time_string("15s"), 15)

    def testBusyWaitFail(self):
        self.assertEqual(minicron.busy_wait(None), None)
        self.assertEqual(minicron.busy_wait(""), None)
        self.assertEqual(minicron.busy_wait([]), None)
        self.assertEqual(minicron.busy_wait(0), None)
        self.assertEqual(minicron.busy_wait(2.5), None)

    def testBusyWaitOk(self):
        self.assertEqual(minicron.busy_wait(2), True)

if __name__ == '__main__':
    unittest.main()
