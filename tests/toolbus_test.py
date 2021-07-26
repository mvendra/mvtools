#!/usr/bin/env python3

import os
import shutil
import unittest

import mvtools_test_fixture
import create_and_write_file
import path_utils
import mvtools_envvars

import toolbus

class ToolbusTest(unittest.TestCase):

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

        v, r = mvtools_test_fixture.makeAndGetTestFolder("toolbus_test")
        if not v:
            return v, r
        self.test_base_dir = r[0]
        self.test_dir = r[1]

        v, r = mvtools_envvars.mvtools_envvar_write_toolbus_base(self.test_dir)
        if not v:
            return False, "Failed setting up toolbus envvar for testing."

        self.nonexistent_folder = path_utils.concat_path(self.test_dir, "nonexistent_folder")
        self.nonexistent_file = path_utils.concat_path(self.test_dir, "nonexistent_file")

        self.db_test_empty = "test_db_empty"
        self.db_test_empty_full = path_utils.concat_path(self.test_dir, "%s.%s" % (self.db_test_empty, toolbus.DB_EXTENSION))

        self.contents_db_test_ok_1 = "var1 = \"val1\"" + os.linesep
        self.db_test_ok_1 = "test_db_ok_1"
        self.db_test_ok_1_full = path_utils.concat_path(self.test_dir, "%s.%s" % (self.db_test_ok_1, toolbus.DB_EXTENSION))

        self.contents_db_test_ok_2 = "var1 = \"val1\"" + os.linesep
        self.contents_db_test_ok_2 += "[" + os.linesep
        self.contents_db_test_ok_2 += "@ctx1" + os.linesep
        self.contents_db_test_ok_2 += "var2 = \"val2\"" + os.linesep
        self.contents_db_test_ok_2 += "]" + os.linesep
        self.db_test_ok_2 = "test_db_ok_2"
        self.db_test_ok_2_full = path_utils.concat_path(self.test_dir, "%s.%s" % (self.db_test_ok_2, toolbus.DB_EXTENSION))

        self.contents_db_test_fail_1 = "var1 ! \"val1\"" + os.linesep
        self.db_test_fail_1 = path_utils.concat_path(self.test_dir, "test_db_fail_1.%s" % (toolbus.DB_EXTENSION))

        self.contents_db_test_fail_2 = "var1 = \"val1\"" + os.linesep
        self.contents_db_test_fail_2 += "var1 = \"val1\"" + os.linesep
        self.db_test_fail_2 = path_utils.concat_path(self.test_dir, "test_db_fail_2.%s" % (toolbus.DB_EXTENSION))

        self.db_test_internal_database = path_utils.concat_path(self.test_dir, "%s.%s" % (toolbus.INTERNAL_DB_FILENAME, toolbus.DB_EXTENSION))
        self.db_test_custom_database = path_utils.concat_path(self.test_dir, "%s.%s" % ("custom-test-db", toolbus.DB_EXTENSION))

        create_and_write_file.create_file_contents(self.db_test_ok_1_full, self.contents_db_test_ok_1)
        create_and_write_file.create_file_contents(self.db_test_ok_2_full, self.contents_db_test_ok_2)
        create_and_write_file.create_file_contents(self.db_test_fail_1, self.contents_db_test_fail_1)
        create_and_write_file.create_file_contents(self.db_test_fail_2, self.contents_db_test_fail_2)
        create_and_write_file.create_file_contents(self.db_test_empty_full, "")

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)
        v, r = self.mvtools_envvars_inst.restore_copy_environ()
        if not v:
            self.fail(r)

    def testBootstrapCustomToolbusDb(self):
        v, r = toolbus.bootstrap_custom_toolbus_db(path_utils.poplastextension(path_utils.basename_filtered(self.db_test_custom_database)))
        self.assertTrue(v)
        self.assertTrue(os.path.exists(self.db_test_custom_database))
        v, r = toolbus.bootstrap_custom_toolbus_db(path_utils.poplastextension(path_utils.basename_filtered(self.db_test_custom_database)))
        self.assertFalse(v)

    def testGetDbHandle1(self):

        v, r, ext = toolbus.get_db_handle(None)
        self.assertFalse(v)

    def testGetDbHandle2(self):

        v, r, ext = toolbus.get_db_handle( path_utils.basename_filtered(self.db_test_ok_1_full) )
        self.assertTrue(v)

    def testGetDbHandle3(self):

        v, r = mvtools_envvars.mvtools_envvar_write_toolbus_base(self.nonexistent_folder)
        if not v:
            self.fail("Failed setting toolbus envvar with value: [%s]" % (self.nonexistent_folder))

        v, r, ext = toolbus.get_db_handle( path_utils.basename_filtered(self.db_test_ok_1_full) )
        self.assertFalse(v)

    def testGetDbHandle4(self):

        self.assertFalse( os.path.exists( self.db_test_internal_database ) )
        v, r, ext = toolbus.get_db_handle( ("%s.%s" % (toolbus.INTERNAL_DB_FILENAME, toolbus.DB_EXTENSION)), True )
        self.assertTrue(v)
        self.assertTrue( os.path.exists( self.db_test_internal_database ) )

    def testGetDbHandle5(self):

        self.assertFalse(os.path.exists( self.db_test_internal_database ))

        contents_internal_db  = "[" + os.linesep
        contents_internal_db += ("@%s" + os.linesep ) % toolbus.TOOLBUS_SIGNAL_CONTEXT
        contents_internal_db += "]"

        create_and_write_file.create_file_contents(self.db_test_internal_database, contents_internal_db)
        self.assertTrue(os.path.exists( self.db_test_internal_database ))

        v, r, ext = toolbus.get_db_handle( path_utils.basename_filtered(self.db_test_internal_database), True )
        self.assertTrue(v)

        read_contents = ""
        with open(self.db_test_internal_database) as f:
            read_contents = f.read()
        self.assertEqual(contents_internal_db, read_contents)

    def testGetDbHandle6(self):

        v, r, ext = toolbus.get_db_handle( path_utils.basename_filtered(self.nonexistent_file) )
        self.assertFalse(v)

    def testGetDbHandle7(self):

        v, r, ext = toolbus.get_db_handle( path_utils.basename_filtered(self.db_test_fail_1) )
        self.assertFalse(v)

    def testGetDbHandle8(self):

        v, r, ext = toolbus.get_db_handle( path_utils.basename_filtered(self.db_test_fail_2) )
        self.assertFalse(v)

    def testGetHandleCustomDb1(self):
        v, r, ext = toolbus.get_handle_custom_db( toolbus.INTERNAL_DB_FILENAME )
        self.assertFalse(v)

    def testGetHandleCustomDb2(self):
        v, r, ext = toolbus.get_handle_custom_db( self.db_test_ok_1 )
        self.assertTrue(v)

    def testGetField1(self):

        v, r = toolbus.get_field(self.db_test_ok_1, None, "var3")
        self.assertTrue(v)
        self.assertEqual(r, None)

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
        self.assertTrue(v)
        self.assertEqual(r, None)

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
        self.assertTrue(v)
        self.assertEqual(r, None)

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
        self.assertTrue(v)
        self.assertEqual(r, None)

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
        self.assertTrue(v)
        self.assertEqual(r, None)

        v, r = toolbus.set_field(self.db_test_ok_1, "new-ctx", "var5", "val5", [("a", "1")])
        self.assertTrue(v)

        v, r = toolbus.get_field(self.db_test_ok_1, "new-ctx", "var5")
        self.assertTrue(v)
        self.assertEqual(r, ("var5", "val5", [("a", "1")]))

    def testGetSignal1(self):
        self.assertFalse(os.path.exists( self.db_test_internal_database ))
        v, r = toolbus.get_signal("novar")
        self.assertTrue(os.path.exists( self.db_test_internal_database ))

    def testGetSignal2(self):

        self.assertFalse(os.path.exists( self.db_test_internal_database ))

        contents_internal_db  = "[" + os.linesep
        contents_internal_db += ("@%s" + os.linesep ) % toolbus.TOOLBUS_SIGNAL_CONTEXT
        contents_internal_db += "var7 = \"val7\"" + os.linesep
        contents_internal_db += "]"
        create_and_write_file.create_file_contents(self.db_test_internal_database, contents_internal_db)
        self.assertTrue(os.path.exists( self.db_test_internal_database ))

        v, r = toolbus.get_signal("var7")
        self.assertTrue(v)
        self.assertEqual(r, "val7")

        v, r = toolbus.get_signal("var8")
        self.assertTrue(v)
        self.assertEqual(r, None)

    def testGetSignal3(self):

        self.assertFalse(os.path.exists( self.db_test_internal_database ))
        v, r = toolbus.set_signal("var14", "val14")
        self.assertTrue(v)
        self.assertTrue(os.path.exists( self.db_test_internal_database ))

        v, r = toolbus.get_signal("var14", True)
        self.assertTrue(v)
        self.assertEqual(r, "val14")

        v, r = toolbus.get_signal("var14")
        self.assertTrue(v)
        self.assertEqual(r, "val14")

        v, r = toolbus.get_signal("var14")
        self.assertTrue(v)
        self.assertEqual(r, None)

    def testSetSignal1(self):

        self.assertFalse(os.path.exists( self.db_test_internal_database ))
        v, r = toolbus.set_signal("var10", "val10")
        self.assertTrue(os.path.exists( self.db_test_internal_database ))
        self.assertTrue(v)

    def testSetSignal2(self):

        v, r = toolbus.get_signal("var11")
        self.assertTrue(v)
        self.assertEqual(r, None)

        v, r = toolbus.set_signal("var11", "val11")
        self.assertTrue(v)

        v, r = toolbus.get_signal("var11")
        self.assertTrue(v)
        self.assertEqual(r, "val11")

    def testSetSignal3(self):

        v, r = toolbus.get_signal("var13")
        self.assertTrue(v)
        self.assertEqual(r, None)

        v, r = toolbus.set_signal("var13", "val13")
        self.assertTrue(v)

        v, r = toolbus.set_signal("var13", "val13")
        self.assertFalse(v)

    def testSetAndGetSignal1(self):

        v, r = toolbus.get_signal("var12")
        self.assertTrue(v)
        self.assertEqual(r, None)

        v, r = toolbus.set_signal("var12", "val12")
        self.assertTrue(v)

        v, r = toolbus.get_signal("var12")
        self.assertTrue(v)
        self.assertEqual(r, "val12")

        v, r = toolbus.get_signal("var12")
        self.assertTrue(v)
        self.assertEqual(r, None)

    def testRemoveField1(self):

        v, r = toolbus.set_field(self.db_test_empty, None, "var1", "val2", [])
        self.assertTrue(v)

        v, r = toolbus.get_field(self.db_test_empty, None, "var1")
        self.assertTrue(v)

        v, r = toolbus.remove_field(self.db_test_empty, None, "var1")
        self.assertTrue(v)

        v, r = toolbus.get_field(self.db_test_empty, None, "var1")
        self.assertTrue(v)
        self.assertEqual(r, None)

    def testRemoveField2(self):

        v, r = toolbus.set_field(self.db_test_empty, None, "var1", "val2", [])
        self.assertTrue(v)

        v, r = toolbus.get_field(self.db_test_empty, None, "var1")
        self.assertTrue(v)

        v, r = toolbus.remove_field(self.db_test_empty, None, "var2")
        self.assertFalse(v)

        v, r = toolbus.get_field(self.db_test_empty, None, "var1")
        self.assertTrue(v)

    def testRemoveField3(self):

        v, r = toolbus.set_field(self.db_test_empty, "ctx1", "var1", "val2", [])
        self.assertTrue(v)

        v, r = toolbus.get_field(self.db_test_empty, "ctx1", "var1")
        self.assertTrue(v)

        v, r = toolbus.remove_field(self.db_test_empty, "ctx1", "var2")
        self.assertFalse(v)

        v, r = toolbus.get_field(self.db_test_empty, "ctx1", "var1")
        self.assertTrue(v)

    def testRemoveTable1(self):

        v, r = toolbus.set_field(self.db_test_empty, "ctx1", "var1", "val1", [])
        self.assertTrue(v)

        v, r = toolbus.get_field(self.db_test_empty, "ctx1", "var1")
        self.assertTrue(v)

        v, r = toolbus.remove_table(self.db_test_empty, "ctx1")
        self.assertTrue(v)

        v, r = toolbus.get_field(self.db_test_empty, "ctx1", "var1")
        self.assertTrue(v)
        self.assertEqual(r, None)

    def testRemoveTable2(self):

        v, r = toolbus.set_field(self.db_test_empty, "ctx1", "var1", "val1", [])
        self.assertTrue(v)

        v, r = toolbus.set_field(self.db_test_empty, "ctx2", "var2", "val2", [])
        self.assertTrue(v)

        v, r = toolbus.get_field(self.db_test_empty, "ctx1", "var1")
        self.assertTrue(v)

        v, r = toolbus.get_field(self.db_test_empty, "ctx2", "var2")
        self.assertTrue(v)

        v, r = toolbus.remove_table(self.db_test_empty, "ctx1")
        self.assertTrue(v)

        v, r = toolbus.get_field(self.db_test_empty, "ctx1", "var1")
        self.assertTrue(v)
        self.assertEqual(r, None)

        v, r = toolbus.get_field(self.db_test_empty, "ctx2", "var2")
        self.assertTrue(v)

    def testGetAllTables1(self):

        v, r = toolbus.set_field(self.db_test_empty, "ctx1", "var1", "val1", [])
        self.assertTrue(v)

        v, r = toolbus.get_all_tables(self.db_test_empty)
        self.assertTrue(v)
        self.assertEqual(r, ["ctx1"])

    def testGetAllTables2(self):

        v, r = toolbus.set_field(self.db_test_empty, "ctx1", "var1", "val1", [])
        self.assertTrue(v)

        v, r = toolbus.set_field(self.db_test_empty, "ctx2", "var2", "val2", [])
        self.assertTrue(v)

        v, r = toolbus.get_all_tables(self.db_test_empty)
        self.assertTrue(v)
        self.assertEqual(r, ["ctx1", "ctx2"])

    def testGetAllTables3(self):

        v, r = toolbus.set_field(self.db_test_empty, "ctx1", "var1", "val1", [])
        self.assertTrue(v)

        v, r = toolbus.set_field(self.db_test_empty, "ctx2", "var2", "val2", [])
        self.assertTrue(v)

        v, r = toolbus.remove_table(self.db_test_empty, "ctx1")
        self.assertTrue(v)

        v, r = toolbus.get_all_tables(self.db_test_empty)
        self.assertTrue(v)
        self.assertEqual(r, ["ctx2"])

    def testGetAllFields1(self):

        v, r = toolbus.set_field(self.db_test_empty, "ctx1", "var1", "val1", [])
        self.assertTrue(v)

        v, r = toolbus.get_all_fields(self.db_test_empty, "ctx1")
        self.assertTrue(v)
        self.assertEqual(r, [("var1", "val1", [])])

    def testGetAllFields2(self):

        v, r = toolbus.set_field(self.db_test_empty, "ctx1", "var1", "val1", [])
        self.assertTrue(v)

        v, r = toolbus.set_field(self.db_test_empty, "ctx2", "var2", "val2", [])
        self.assertTrue(v)

        v, r = toolbus.get_all_fields(self.db_test_empty, "ctx2")
        self.assertTrue(v)
        self.assertEqual(r, [("var2", "val2", [])])

    def testGetAllFields3(self):

        v, r = toolbus.set_field(self.db_test_empty, "ctx1", "var1", "val1", [])
        self.assertTrue(v)

        v, r = toolbus.set_field(self.db_test_empty, "ctx2", "var2", "val2", [])
        self.assertTrue(v)

        v, r = toolbus.remove_field(self.db_test_empty, "ctx1", "var1")
        self.assertTrue(v)

        v, r = toolbus.get_all_fields(self.db_test_empty, "ctx2")
        self.assertTrue(v)
        self.assertEqual(r, [("var2", "val2", [])])

    def testGetAllFields4(self):

        v, r = toolbus.set_field(self.db_test_empty, "ctx1", "var1", "val1", [])
        self.assertTrue(v)

        v, r = toolbus.set_field(self.db_test_empty, "ctx2", "var2", "val2", [])
        self.assertTrue(v)

        v, r = toolbus.remove_table(self.db_test_empty, "ctx1")
        self.assertTrue(v)

        v, r = toolbus.get_all_fields(self.db_test_empty, "ctx1")
        self.assertTrue(v)
        self.assertEqual(r, None)

        v, r = toolbus.get_all_fields(self.db_test_empty, "ctx2")
        self.assertTrue(v)
        self.assertEqual(r, [("var2", "val2", [])])

if __name__ == '__main__':
    unittest.main()
