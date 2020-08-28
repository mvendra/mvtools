#!/usr/bin/env python3

import os
import shutil
import unittest

import mvtools_test_fixture
import create_and_write_file
import path_utils

import toolbus

class ToolbusTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        self.environ_copy = os.environ.copy()

        v, r = mvtools_test_fixture.makeAndGetTestFolder("toolbus_test")
        if not v:
            return v, r
        self.test_base_dir = r[0]
        self.test_dir = r[1]

        if not self._setenv(toolbus.TOOLBUS_ENVVAR, self.test_dir):
            return False, "Failed setting up the %s env var for testing." % toolbus.TOOLBUS_ENVVAR

        self.reserved_test_env_var = "$MVTOOLS_TOOLBUS_TEST_RESERVED_1"
        if self.reserved_test_env_var[1:] in os.environ:
            return False, "Environment variable [%s] is in use. This test requires it to be undefined." % (self.reserved_test_env_var[1:])

        self.nonexistent_folder = path_utils.concat_path(self.test_dir, "nonexistent_folder")
        self.nonexistent_file = path_utils.concat_path(self.test_dir, "nonexistent_file")

        self.contents_db_test_ok_1 = "var1 = \"val1\"" + os.linesep
        self.db_test_ok_1 = "test_db_ok_1"
        self.db_test_ok_1_full = path_utils.concat_path(self.test_dir, "%s.txt" % self.db_test_ok_1)

        self.contents_db_test_ok_2 = "var1 = \"val1\"" + os.linesep
        self.contents_db_test_ok_2 += "[" + os.linesep
        self.contents_db_test_ok_2 += "@ctx1" + os.linesep
        self.contents_db_test_ok_2 += "var2 = \"val2\"" + os.linesep
        self.contents_db_test_ok_2 += "]" + os.linesep
        self.db_test_ok_2 = "test_db_ok_2"
        self.db_test_ok_2_full = path_utils.concat_path(self.test_dir, "%s.txt" % self.db_test_ok_2)

        self.contents_db_test_fail_1 = "var1 ! \"val1\"" + os.linesep
        self.db_test_fail_1 = path_utils.concat_path(self.test_dir, "test_db_fail_1.txt")

        self.contents_db_test_fail_2 = "var1 = \"val1\"" + os.linesep
        self.contents_db_test_fail_2 += "var1 = \"val1\"" + os.linesep
        self.db_test_fail_2 = path_utils.concat_path(self.test_dir, "test_db_fail_2.txt")

        create_and_write_file.create_file_contents(self.db_test_ok_1_full, self.contents_db_test_ok_1)
        create_and_write_file.create_file_contents(self.db_test_ok_2_full, self.contents_db_test_ok_2)
        create_and_write_file.create_file_contents(self.db_test_fail_1, self.contents_db_test_fail_1)
        create_and_write_file.create_file_contents(self.db_test_fail_2, self.contents_db_test_fail_2)

        return True, ""

    def _setenv(self, _var, _val):
        try:
            os.environ[ _var ] = _val
        except:
            return False
        return True

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.environ_copy)
        shutil.rmtree(self.test_base_dir)

    def testGetDbHandle1(self):

        v, r, ext = toolbus.get_db_handle(None)
        self.assertFalse(v)

    def testGetDbHandle2(self):

        v, r, ext = toolbus.get_db_handle( os.path.basename(self.db_test_ok_1_full) )
        self.assertTrue(v)

    def testGetDbHandle3(self):

        local_environ_copy = os.environ.copy()
        try:
            if not self._setenv(toolbus.TOOLBUS_ENVVAR, self.nonexistent_folder):
                self.fail("Failed setting envvar: [%s] with value: [%s]" % (toolbus.TOOLBUS_ENVVAR, self.nonexistent_folder))

            v, r, ext = toolbus.get_db_handle( os.path.basename(self.db_test_ok_1_full) )
            self.assertFalse(v)

        finally:
            os.environ.clear()
            os.environ.update(local_environ_copy)

    def testGetDbHandle4(self):
        pass # mvtodo: test get_db_handle for internal (signalling?)

    def testGetDbHandle5(self):

        v, r, ext = toolbus.get_db_handle( os.path.basename(self.nonexistent_file) )
        self.assertFalse(v)

    def testGetDbHandle6(self):

        v, r, ext = toolbus.get_db_handle( os.path.basename(self.db_test_fail_1) )
        self.assertFalse(v)

    def testGetDbHandle7(self):

        v, r, ext = toolbus.get_db_handle( os.path.basename(self.db_test_fail_2) )
        self.assertFalse(v)

    def testGetHandleCustomDb1(self):
        v, r, ext = toolbus.get_handle_custom_db( toolbus.INTERNAL_DB_FILENAME )
        self.assertFalse(v)

    def testGetHandleCustomDb2(self):
        v, r, ext = toolbus.get_handle_custom_db( self.db_test_ok_1 )
        self.assertTrue(v)

    # mvtodo: get_signal
    # mvtodo: set_signal

    def testGetField1(self):

        v, r = toolbus.get_field(self.db_test_ok_1, None, "var3")
        self.assertFalse(v)

    def testGetField2(self):

        v, r = toolbus.get_field(self.db_test_ok_1, None, "var1")
        self.assertTrue(v)
        self.assertEqual(len(r), 3)
        self.assertEqual(r[0], "var1")
        self.assertEqual(r[1], "val1")
        self.assertEqual(r[2], [])

    def testGetField3(self):

        v, r = toolbus.get_field(self.db_test_ok_2, None, "var1")
        self.assertTrue(v)
        self.assertEqual(len(r), 3)
        self.assertEqual(r[0], "var1")
        self.assertEqual(r[1], "val1")
        self.assertEqual(r[2], [])

    def testGetField4(self):

        v, r = toolbus.get_field(self.db_test_ok_2, "ctx2", "var2")
        self.assertFalse(v)

    def testGetField5(self):

        v, r = toolbus.get_field(self.db_test_ok_2, "ctx1", "var2")
        self.assertTrue(v)
        self.assertEqual(len(r), 3)
        self.assertEqual(r[0], "var2")
        self.assertEqual(r[1], "val2")
        self.assertEqual(r[2], [])

    def testGetField6(self):

        v, r = toolbus.get_field(self.nonexistent_file, None, "var1")
        self.assertFalse(v)

    def testSetField1(self):

        v, r = toolbus.get_field(self.db_test_ok_1, None, "var1")
        self.assertTrue(v)
        self.assertEqual(r, ("var1", "val1", []))

        v, r = toolbus.set_field(self.db_test_ok_1, None, "var1", "val2", [])
        self.assertTrue(v)

        v, r = toolbus.get_field(self.db_test_ok_1, None, "var1")
        self.assertTrue(v)
        self.assertEqual(r, ("var1", "val2", []))

    def testSetField2(self):

        v, r = toolbus.get_field(self.db_test_ok_1, None, "var1")
        self.assertTrue(v)
        self.assertEqual(r, ("var1", "val1", []))

        v, r = toolbus.set_field(self.db_test_ok_1, None, "var1", "val3", [("a", "1")])
        self.assertTrue(v)

        v, r = toolbus.get_field(self.db_test_ok_1, None, "var1")
        self.assertTrue(v)
        self.assertEqual(r, ("var1", "val3", [("a", "1")]))

    def testSetField3(self):

        v, r = toolbus.get_field(self.db_test_ok_1, None, "var2")
        self.assertFalse(v)

        v, r = toolbus.set_field(self.db_test_ok_1, None, "var2", "val2", [("b", "2")])
        self.assertTrue(v)

        v, r = toolbus.get_field(self.db_test_ok_1, None, "var2")
        self.assertTrue(v)
        self.assertEqual(r, ("var2", "val2", [("b", "2")]))

    def testSetField4(self):

        v, r = toolbus.get_field(self.db_test_ok_2, "ctx1", "var2")
        self.assertTrue(v)
        self.assertEqual(r, ("var2", "val2", []))

        v, r = toolbus.set_field(self.db_test_ok_2, "ctx1", "var2", "val2", [("c", "3")])
        self.assertTrue(v)

        v, r = toolbus.get_field(self.db_test_ok_2, "ctx1", "var2")
        self.assertTrue(v)
        self.assertEqual(r, ("var2", "val2", [("c", "3")]))

    def testSetField5(self):

        v, r = toolbus.get_field(self.db_test_ok_2, "ctx1", "var3")
        self.assertFalse(v)

        v, r = toolbus.set_field(self.db_test_ok_2, "ctx1", "var3", "val3", [])
        self.assertTrue(v)

        v, r = toolbus.get_field(self.db_test_ok_2, "ctx1", "var3")
        self.assertTrue(v)
        self.assertEqual(r, ("var3", "val3", []))

    def testSetField6(self):

        v, r = toolbus.set_field(self.nonexistent_file, None, "var1", "val1", [])
        self.assertFalse(v)

    def testSetField7(self):

        v, r = toolbus.get_field(self.db_test_ok_1, "new-ctx", "var5")
        self.assertFalse(v)

        v, r = toolbus.set_field(self.db_test_ok_1, "new-ctx", "var5", "val5", [("a", "1")])
        self.assertTrue(v)

        v, r = toolbus.get_field(self.db_test_ok_1, "new-ctx", "var5")
        self.assertTrue(v)
        self.assertEqual(r, ("var5", "val5", [("a", "1")]))

if __name__ == '__main__':
    unittest.main()
