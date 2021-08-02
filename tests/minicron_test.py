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

    def testConvertDurationSinglePartFail(self):
        self.assertEqual(minicron.convert_time_string([]), None)
        self.assertEqual(minicron.convert_time_string(""), None)
        self.assertEqual(minicron.convert_time_string("1"), None)
        self.assertEqual(minicron.convert_time_string(None), None)
        self.assertEqual(minicron.convert_time_string("1f"), None)

    def testConvertDurationSinglePartOk(self):
        self.assertEqual(minicron.convert_single_part("7h"), 25200)
        self.assertEqual(minicron.convert_single_part("30m"), 1800)
        self.assertEqual(minicron.convert_single_part("15s"), 15)

    def testConvertDurationTimeStringFail(self):
        self.assertEqual(minicron.convert_time_string("7h67m15s4"), None)
        self.assertEqual(minicron.convert_time_string("00000"), None)

    def testConvertDurationTimeStringOk(self):
        self.assertEqual(minicron.convert_time_string("1m1s"), 61)
        self.assertEqual(minicron.convert_time_string("18s"), 18)
        self.assertEqual(minicron.convert_time_string("08m02s"), 482)
        self.assertEqual(minicron.convert_time_string("2h5m12s"), 7512)

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
