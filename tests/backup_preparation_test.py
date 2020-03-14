#!/usr/bin/env python3

import sys
import os
import stat
import shutil
import unittest
from unittest import mock
from unittest.mock import patch
import getpass

import create_and_write_file
import mvtools_test_fixture

import backup_preparation

import path_utils

class BackupPreparationTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

        # folder where to store the preparation artifacts
        self.prep_target = path_utils.concat_path(self.test_dir, "preptarget")
        path_utils.scratchfolder(self.prep_target)

        self.nonexistant = path_utils.concat_path(self.test_dir, "nonexistant")

        self.warn_size_each1 = "1024"
        self.warn_size_final1 = "8192"
        self.warn_size_each2 = "10"
        self.warn_size_final2 = "40"

        # test contents
        self.test_source_folder1 = path_utils.concat_path(self.test_dir, "source_test1")
        os.mkdir(self.test_source_folder1)
        self.file1 = path_utils.concat_path(self.test_source_folder1, "file1.txt")
        create_and_write_file.create_file_contents(self.file1, "xyz")

        self.test_source_folder2 = path_utils.concat_path(self.test_dir, "source_test2")
        os.mkdir(self.test_source_folder2)
        self.file2 = path_utils.concat_path(self.test_source_folder2, "file2.txt")
        create_and_write_file.create_file_contents(self.file2, "abc")

        cfg_file_contents1 = ""
        cfg_file_contents1 += ("SET_STORAGE_PATH {reset} = \"%s\"" + os.linesep) % (self.prep_target)
        cfg_file_contents1 += ("SET_WARN_SIZE_EACH {abort} = \"%s\"" + os.linesep) % (self.warn_size_each1)
        cfg_file_contents1 += ("SET_WARN_SIZE_FINAL {abort} = \"%s\"" + os.linesep) % (self.warn_size_final1)
        cfg_file_contents1 += ("COPY_PATH {abort} = \"%s\"" + os.linesep) % (self.test_source_folder1)
        cfg_file_contents1 += ("COPY_TREE_OUT {abort} = \"%s\"" + os.linesep) % (self.test_source_folder2)
        self.test_config_file1 = path_utils.concat_path(self.test_dir, "test_config_file1.cfg")
        create_and_write_file.create_file_contents(self.test_config_file1, cfg_file_contents1)

        cfg_file_contents2 = ""
        cfg_file_contents2 += ("SET_STORAGE_PATH = \"%s\"" + os.linesep) % (self.prep_target)
        cfg_file_contents2 += ("SET_WARN_SIZE_EACH = \"%s\"" + os.linesep) % (self.warn_size_each2)
        cfg_file_contents2 += ("SET_WARN_SIZE_FINAL = \"%s\"" + os.linesep) % (self.warn_size_final2)
        cfg_file_contents2 += ("COPY_PATH = \"%s\"" + os.linesep) % (self.test_source_folder2)
        cfg_file_contents2 += ("COPY_TREE_OUT = \"%s\"" + os.linesep) % (self.test_source_folder1)
        self.test_config_file2 = path_utils.concat_path(self.test_dir, "test_config_file2.cfg")
        create_and_write_file.create_file_contents(self.test_config_file2, cfg_file_contents2)

        cfg_file_contents3 = ""
        cfg_file_contents3 += ("SET_STORAGE_PATH = \"%s\"" + os.linesep) % (self.prep_target)
        self.test_config_file3 = path_utils.concat_path(self.test_dir, "test_config_file3.cfg")
        create_and_write_file.create_file_contents(self.test_config_file3, cfg_file_contents3)

        cfg_file_contents_fail1 = ""
        cfg_file_contents_fail1 += ("SET_STORAGE_PATH = \"%s\"" + os.linesep) % (self.nonexistant)
        self.test_config_file_fail1 = path_utils.concat_path(self.test_dir, "test_config_file_fail1.cfg")
        create_and_write_file.create_file_contents(self.test_config_file_fail1, cfg_file_contents_fail1)

        cfg_file_contents_fail2 = ""
        cfg_file_contents_fail2 += ("SET_STORAGE_PATH = %s\"" + os.linesep) % (self.prep_target)
        self.test_config_file_fail2 = path_utils.concat_path(self.test_dir, "test_config_file_fail2.cfg")
        create_and_write_file.create_file_contents(self.test_config_file_fail2, cfg_file_contents_fail2)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("backup_preparation_test")
        if not v:
            return v, r
        self.test_base_dir = r[0]
        self.test_dir = r[1]

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testConvertToByteFail(self):
        self.assertEqual(backup_preparation.convert_to_bytes("1b"), (False, None))
        self.assertEqual(backup_preparation.convert_to_bytes("50bb"), (False, None))
        self.assertEqual(backup_preparation.convert_to_bytes("abc"), (False, None))
        self.assertEqual(backup_preparation.convert_to_bytes(""), (False, None))

    def testConvertToByteSuccess(self):
        self.assertEqual(backup_preparation.convert_to_bytes("50"), (True, 50))
        self.assertEqual(backup_preparation.convert_to_bytes("1024"), (True, 1024))
        self.assertEqual(backup_preparation.convert_to_bytes("1kb"), (True, 1024))
        self.assertEqual(backup_preparation.convert_to_bytes("20kb"), (True, 20480))
        self.assertEqual(backup_preparation.convert_to_bytes("1mb"), (True, 1048576))
        self.assertEqual(backup_preparation.convert_to_bytes("20mb"), (True, 20971520))
        self.assertEqual(backup_preparation.convert_to_bytes("1gb"), (True, 1073741824))
        self.assertEqual(backup_preparation.convert_to_bytes("1tb"), (True, 1073741824*1024))

    def testDeriveFolderNameForTree(self):
        self.assertEqual(backup_preparation.derivefoldernamefortree("/home/user/folder"), "folder_tree_out.txt")

    def testDeriveFilenameForCrontab(self):
        self.assertEqual(backup_preparation.derivefilenameforcrontab(), "crontab_" + getpass.getuser() + ".txt")

    def testReadConfig1(self):
        bkprep = backup_preparation.BackupPreparation(self.test_config_file1)
        bkprep.read_config(bkprep.config_file)
        bkprep.setup_configuration()
        self.assertEqual(bkprep.storage_path, self.prep_target)
        self.assertEqual(bkprep.storage_path_reset, True)
        self.assertEqual(bkprep.warn_size_each_active, True)
        self.assertEqual(bkprep.warn_size_each, int(self.warn_size_each1))
        self.assertEqual(bkprep.warn_size_each_abort, True)
        self.assertEqual(bkprep.warn_size_final_active, True)
        self.assertEqual(bkprep.warn_size_final, int(self.warn_size_final1))
        self.assertEqual(bkprep.warn_size_final_abort, True)

    def testReadConfig2(self):
        bkprep = backup_preparation.BackupPreparation("")
        bkprep.read_config(self.test_config_file2)
        bkprep.setup_configuration()
        self.assertEqual(bkprep.storage_path, self.prep_target)
        self.assertEqual(bkprep.storage_path_reset, False)
        self.assertEqual(bkprep.warn_size_each_active, True)
        self.assertEqual(bkprep.warn_size_each, int(self.warn_size_each2))
        self.assertEqual(bkprep.warn_size_each_abort, False)
        self.assertEqual(bkprep.warn_size_final_active, True)
        self.assertEqual(bkprep.warn_size_final, int(self.warn_size_final2))
        self.assertEqual(bkprep.warn_size_final_abort, False)

    def testReadConfig3(self):
        bkprep = backup_preparation.BackupPreparation(self.test_config_file3)
        bkprep.read_config(bkprep.config_file)
        bkprep.setup_configuration()
        self.assertEqual(bkprep.storage_path, self.prep_target)
        self.assertEqual(bkprep.storage_path_reset, False)
        self.assertEqual(bkprep.warn_size_each_active, False)
        self.assertEqual(bkprep.warn_size_each, 0)
        self.assertEqual(bkprep.warn_size_each_abort, False)
        self.assertEqual(bkprep.warn_size_final_active, False)
        self.assertEqual(bkprep.warn_size_final, 0)
        self.assertEqual(bkprep.warn_size_final_abort, False)

    def testReadConfigFail1(self):
        bkprep = backup_preparation.BackupPreparation(self.test_config_file_fail1)
        bkprep.read_config(bkprep.config_file)
        ex_raised = False
        try:
            bkprep.setup_configuration()
        except backup_preparation.BackupPreparationException as bkprepbpex:
            ex_raised = True
        self.assertTrue(ex_raised)

    def testReadConfigFail2(self):
        bkprep = backup_preparation.BackupPreparation(self.test_config_file_fail2)
        ex_raised = False
        try:
            bkprep.read_config(bkprep.config_file)
        except backup_preparation.BackupPreparationException as bkprepbpex:
            ex_raised = True
        self.assertTrue(ex_raised)

    def testProcSingleConfig(self):

        bkprep = backup_preparation.BackupPreparation("")

        # set_storage_path
        self.assertTrue(bkprep.proc_single_config("SET_STORAGE_PATH", self.prep_target, [("", "")]))
        self.assertEqual(bkprep.storage_path, self.prep_target)

        # warn_size_each
        wse = "90"
        self.assertTrue(bkprep.proc_single_config("SET_WARN_SIZE_EACH", wse, [("", "")]))
        self.assertTrue(bkprep.warn_size_each_active)
        self.assertFalse(bkprep.warn_size_each_abort)
        self.assertEqual(bkprep.warn_size_each, int(wse))

        wse = "100"
        self.assertTrue(bkprep.proc_single_config("SET_WARN_SIZE_EACH", wse, [("abort", "")]))
        self.assertTrue(bkprep.warn_size_each_active)
        self.assertTrue(bkprep.warn_size_each_abort)
        self.assertEqual(bkprep.warn_size_each, int(wse))

        bad_wse = "abc"
        ex_raised = False
        try:
            self.assertTrue(bkprep.proc_single_config("SET_WARN_SIZE_EACH", bad_wse, [("abort", "")]))
        except backup_preparation.BackupPreparationException as bkprepbpex:
            ex_raised = True
        self.assertTrue(ex_raised)

        # warn_size_final
        wsf = "45"
        self.assertTrue(bkprep.proc_single_config("SET_WARN_SIZE_FINAL", wsf, [("", "")]))
        self.assertTrue(bkprep.warn_size_final_active)
        self.assertFalse(bkprep.warn_size_final_abort)
        self.assertEqual(bkprep.warn_size_final, int(wsf))

        wsf = "72"
        self.assertTrue(bkprep.proc_single_config("SET_WARN_SIZE_FINAL", wsf, [("abort", "")]))
        self.assertTrue(bkprep.warn_size_final_active)
        self.assertTrue(bkprep.warn_size_final_abort)
        self.assertEqual(bkprep.warn_size_final, int(wsf))

        bad_wsf = "xyz"
        ex_raised = False
        try:
            self.assertTrue(bkprep.proc_single_config("SET_WARN_SIZE_FINAL", bad_wsf, [("", "")]))
        except backup_preparation.BackupPreparationException as bkprepbpex:
            ex_raised = True
        self.assertTrue(ex_raised)

        # handling of valid values only
        self.assertFalse(bkprep.proc_single_config("BOGUS_VARIABLE", None, [("", "")]))

    def testDoCopyFile1(self):
        bkprep = backup_preparation.BackupPreparation("")
        self.assertTrue(bkprep.proc_single_config("SET_STORAGE_PATH", self.prep_target, [("", "")]))

        final_path = path_utils.concat_path(self.prep_target, os.path.basename(self.test_source_folder1))
        bkprep.do_copy_file(self.test_source_folder1)
        self.assertTrue(os.path.exists(final_path))

    def testDoCopyFileFail1(self):
        bkprep = backup_preparation.BackupPreparation("")
        self.assertTrue(bkprep.proc_single_config("SET_STORAGE_PATH", self.prep_target, [("", "")]))

        final_path = path_utils.concat_path(self.prep_target, os.path.basename(self.test_source_folder1))
        os.mkdir(final_path)

        ex_raised = False
        try:
            bkprep.do_copy_file(self.test_source_folder1)
        except backup_preparation.BackupPreparationException as bkprepbpex:
            ex_raised = True

        self.assertTrue(ex_raised)

    def testDoCopyFileFail2(self):
        bkprep = backup_preparation.BackupPreparation("")
        self.assertTrue(bkprep.proc_single_config("SET_STORAGE_PATH", self.prep_target, [("", "")]))
        self.assertTrue(bkprep.proc_single_config("SET_WARN_SIZE_EACH", "1", [("abort", "")]))

        final_path = path_utils.concat_path(self.prep_target, os.path.basename(self.test_source_folder1))

        ex_raised = False
        try:
            bkprep.do_copy_file(self.test_source_folder1)
        except backup_preparation.BackupPreparationException as bkprepbpex:
            ex_raised = True

        self.assertTrue(ex_raised)

    def testDoCopyFileFail3(self):
        bkprep = backup_preparation.BackupPreparation("")
        self.assertTrue(bkprep.proc_single_config("SET_STORAGE_PATH", self.prep_target, [("", "")]))
        self.assertTrue(bkprep.proc_single_config("SET_WARN_SIZE_EACH", "4099", [("abort", "")]))

        final_path = path_utils.concat_path(self.prep_target, os.path.basename(self.test_source_folder1))

        ex_raised = False
        try:
            bkprep.do_copy_file(self.test_source_folder1)
        except backup_preparation.BackupPreparationException as bkprepbpex:
            ex_raised = True

        self.assertFalse(ex_raised)

    def testDoCopyFileWarn(self):
        bkprep = backup_preparation.BackupPreparation("")
        self.assertTrue(bkprep.proc_single_config("SET_STORAGE_PATH", self.prep_target, [("", "")]))
        self.assertTrue(bkprep.proc_single_config("SET_WARN_SIZE_EACH", "1", [("", "")]))

        final_path = path_utils.concat_path(self.prep_target, os.path.basename(self.test_source_folder1))

        ex_raised = False
        try:
            bkprep.do_copy_file(self.test_source_folder1)
        except backup_preparation.BackupPreparationException as bkprepbpex:
            ex_raised = True

        self.assertFalse(ex_raised)

    def testDoCopyContent1(self):
        bkprep = backup_preparation.BackupPreparation("")
        self.assertTrue(bkprep.proc_single_config("SET_STORAGE_PATH", self.prep_target, [("", "")]))

        test_fn = "local.txt"
        test_content = "abc"
        final_path = path_utils.concat_path(self.prep_target, test_fn)

        bkprep.do_copy_content(test_content, test_fn)
        self.assertTrue(os.path.exists(final_path))

    def testDoCopyContentFail1(self):
        bkprep = backup_preparation.BackupPreparation("")
        self.assertTrue(bkprep.proc_single_config("SET_STORAGE_PATH", self.prep_target, [("", "")]))

        test_fn = "local.txt"
        test_content = "abc"
        final_path = path_utils.concat_path(self.prep_target, test_fn)

        create_and_write_file.create_file_contents(final_path, test_content)

        ex_raised = False
        try:
            bkprep.do_copy_content(test_content, test_fn)
        except backup_preparation.BackupPreparationException as bkprepbpex:
            ex_raised = True

        self.assertTrue(ex_raised)

    def testDoCopyContentFail2(self):
        bkprep = backup_preparation.BackupPreparation("")
        self.assertTrue(bkprep.proc_single_config("SET_STORAGE_PATH", self.prep_target, [("", "")]))
        self.assertTrue(bkprep.proc_single_config("SET_WARN_SIZE_EACH", "1", [("abort", "")]))

        test_fn = "local.txt"
        test_content = "abc"
        final_path = path_utils.concat_path(self.prep_target, test_fn)

        ex_raised = False
        try:
            bkprep.do_copy_content(test_content, test_fn)
        except backup_preparation.BackupPreparationException as bkprepbpex:
            ex_raised = True

        self.assertTrue(ex_raised)

    def testDoCopyContentFail3(self):
        bkprep = backup_preparation.BackupPreparation("")
        self.assertTrue(bkprep.proc_single_config("SET_STORAGE_PATH", self.prep_target, [("", "")]))
        self.assertTrue(bkprep.proc_single_config("SET_WARN_SIZE_EACH", "3", [("abort", "")]))

        test_fn = "local.txt"
        test_content = "abc"
        final_path = path_utils.concat_path(self.prep_target, test_fn)

        ex_raised = False
        try:
            bkprep.do_copy_content(test_content, test_fn)
        except backup_preparation.BackupPreparationException as bkprepbpex:
            ex_raised = True

        self.assertFalse(ex_raised)

    def testDoCopyContentWarn(self):
        bkprep = backup_preparation.BackupPreparation("")
        self.assertTrue(bkprep.proc_single_config("SET_STORAGE_PATH", self.prep_target, [("", "")]))
        self.assertTrue(bkprep.proc_single_config("SET_WARN_SIZE_EACH", "1", [("", "")]))

        test_fn = "local.txt"
        test_content = "abc"
        final_path = path_utils.concat_path(self.prep_target, test_fn)

        ex_raised = False
        try:
            bkprep.do_copy_content(test_content, test_fn)
        except backup_preparation.BackupPreparationException as bkprepbpex:
            ex_raised = True

        self.assertFalse(ex_raised)

    def testRunPreparation(self):
        pass # mvtodo: several of these full tests, with different config files

if __name__ == '__main__':
    unittest.main()
