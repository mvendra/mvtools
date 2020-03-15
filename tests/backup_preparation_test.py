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

        self.warn_size_each1 = "102400"
        self.warn_size_final1 = "409600"
        self.warn_size_each2 = "5000"
        self.warn_size_final2 = "12000"

        # test contents
        self.test_source_folder1 = path_utils.concat_path(self.test_dir, "source_test1")
        os.mkdir(self.test_source_folder1)
        self.file1 = path_utils.concat_path(self.test_source_folder1, "file1.txt")
        create_and_write_file.create_file_contents(self.file1, "xyz")

        self.test_source_folder2 = path_utils.concat_path(self.test_dir, "source_test2")
        os.mkdir(self.test_source_folder2)
        self.file2 = path_utils.concat_path(self.test_source_folder2, "file2.txt")
        create_and_write_file.create_file_contents(self.file2, "abc")

        self.test_source_folder3 = path_utils.concat_path(self.test_dir, "source_test3")
        os.mkdir(self.test_source_folder3)
        self.file5 = path_utils.concat_path(self.test_source_folder3, "file5.txt")
        create_and_write_file.create_file_contents(self.file5, "def")

        self.file3 = path_utils.concat_path(self.test_dir, "   file3  .txt  ")
        create_and_write_file.create_file_contents(self.file3, "abc")

        self.file4 = path_utils.concat_path(self.test_dir, "heavyfile4.txt")
        create_and_write_file.create_file_contents(self.file4, "12345678" * 15000)

        cfg_file_contents1 = ""
        cfg_file_contents1 += ("SET_STORAGE_PATH {reset} = \"%s\"" + os.linesep) % (self.prep_target)
        cfg_file_contents1 += ("SET_WARN_SIZE_EACH {abort} = \"%s\"" + os.linesep) % (self.warn_size_each1)
        cfg_file_contents1 += ("SET_WARN_SIZE_FINAL {abort} = \"%s\"" + os.linesep) % (self.warn_size_final1)
        cfg_file_contents1 += ("COPY_PATH {abort} = \"%s\"" + os.linesep) % (self.test_source_folder1)
        cfg_file_contents1 += ("COPY_PATH {abort} = \"%s\"" + os.linesep) % (self.file3)
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

        cfg_file_contents4 = ""
        cfg_file_contents4 += ("SET_STORAGE_PATH = \"%s\"" + os.linesep) % (self.prep_target)
        cfg_file_contents4 += ("COPY_PATH = \"%s%s\"" + os.linesep) % (self.test_source_folder3, os.sep)
        self.test_config_file4 = path_utils.concat_path(self.test_dir, "test_config_file4.cfg")
        create_and_write_file.create_file_contents(self.test_config_file4, cfg_file_contents4)

        cfg_file_contents_fail1 = ""
        cfg_file_contents_fail1 += ("SET_STORAGE_PATH = \"%s\"" + os.linesep) % (self.nonexistant)
        self.test_config_file_fail1 = path_utils.concat_path(self.test_dir, "test_config_file_fail1.cfg")
        create_and_write_file.create_file_contents(self.test_config_file_fail1, cfg_file_contents_fail1)

        cfg_file_contents_fail2 = ""
        cfg_file_contents_fail2 += ("SET_STORAGE_PATH = %s\"" + os.linesep) % (self.prep_target)
        self.test_config_file_fail2 = path_utils.concat_path(self.test_dir, "test_config_file_fail2.cfg")
        create_and_write_file.create_file_contents(self.test_config_file_fail2, cfg_file_contents_fail2)

        cfg_file_contents_fail3 = ""
        cfg_file_contents_fail3 += ("SET_STORAGE_PATH = \"%s\"" + os.linesep) % (self.prep_target)
        cfg_file_contents_fail3 += ("SET_WARN_SIZE_EACH {abort} = \"%s\"" + os.linesep) % (self.warn_size_each2)
        cfg_file_contents_fail3 += ("COPY_PATH = \"%s\"" + os.linesep) % (self.test_source_folder1)
        cfg_file_contents_fail3 += ("COPY_PATH = \"%s\"" + os.linesep) % (self.file4)
        self.test_config_file_fail3 = path_utils.concat_path(self.test_dir, "test_config_file_fail3.cfg")
        create_and_write_file.create_file_contents(self.test_config_file_fail3, cfg_file_contents_fail3)

        cfg_file_contents_fail4 = ""
        cfg_file_contents_fail4 += ("SET_STORAGE_PATH = \"%s\"" + os.linesep) % (self.prep_target)
        cfg_file_contents_fail4 += ("SET_WARN_SIZE_FINAL {abort} = \"%s\"" + os.linesep) % (self.warn_size_final2)
        cfg_file_contents_fail4 += ("COPY_PATH = \"%s\"" + os.linesep) % (self.file4)
        self.test_config_file_fail4 = path_utils.concat_path(self.test_dir, "test_config_file_fail4.cfg")
        create_and_write_file.create_file_contents(self.test_config_file_fail4, cfg_file_contents_fail4)

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

    def testReadConfig4(self):
        bkprep = backup_preparation.BackupPreparation(self.test_config_file4)
        bkprep.read_config(bkprep.config_file)
        bkprep.setup_configuration()
        self.assertEqual( (self.test_source_folder3 + os.sep), bkprep.instructions[0][1])

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
        self.assertTrue(bkprep.proc_single_config("SET_STORAGE_PATH", self.prep_target, []))
        self.assertEqual(bkprep.storage_path, self.prep_target)

        # warn_size_each
        wse = "90"
        self.assertTrue(bkprep.proc_single_config("SET_WARN_SIZE_EACH", wse, []))
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
        self.assertTrue(bkprep.proc_single_config("SET_WARN_SIZE_FINAL", wsf, []))
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
            self.assertTrue(bkprep.proc_single_config("SET_WARN_SIZE_FINAL", bad_wsf, []))
        except backup_preparation.BackupPreparationException as bkprepbpex:
            ex_raised = True
        self.assertTrue(ex_raised)

        # handling of valid values only
        self.assertFalse(bkprep.proc_single_config("BOGUS_VARIABLE", None, []))

    def testDoCopyFile1(self):
        bkprep = backup_preparation.BackupPreparation("")
        self.assertTrue(bkprep.proc_single_config("SET_STORAGE_PATH", self.prep_target, []))

        final_path = path_utils.concat_path(self.prep_target, os.path.basename(self.test_source_folder1))
        bkprep.do_copy_file(self.test_source_folder1, None, None)
        self.assertTrue(os.path.exists(final_path))

    def testDoCopyFileFail1(self):
        bkprep = backup_preparation.BackupPreparation("")
        self.assertTrue(bkprep.proc_single_config("SET_STORAGE_PATH", self.prep_target, []))

        final_path = path_utils.concat_path(self.prep_target, os.path.basename(self.test_source_folder1))
        os.mkdir(final_path)

        ex_raised = False
        try:
            bkprep.do_copy_file(self.test_source_folder1, None, None)
        except backup_preparation.BackupPreparationException as bkprepbpex:
            ex_raised = True

        self.assertTrue(ex_raised)

    def testDoCopyFileFail2(self):
        bkprep = backup_preparation.BackupPreparation("")
        self.assertTrue(bkprep.proc_single_config("SET_STORAGE_PATH", self.prep_target, []))
        self.assertTrue(bkprep.proc_single_config("SET_WARN_SIZE_EACH", "1", [("abort", "")]))

        final_path = path_utils.concat_path(self.prep_target, os.path.basename(self.test_source_folder1))

        ex_raised = False
        try:
            bkprep.do_copy_file(self.test_source_folder1, None, None)
        except backup_preparation.BackupPreparationException as bkprepbpex:
            ex_raised = True

        self.assertTrue(ex_raised)

    def testDoCopyFileFail3(self):
        bkprep = backup_preparation.BackupPreparation("")
        self.assertTrue(bkprep.proc_single_config("SET_STORAGE_PATH", self.prep_target, []))
        self.assertTrue(bkprep.proc_single_config("SET_WARN_SIZE_EACH", "4099", [("abort", "")]))

        final_path = path_utils.concat_path(self.prep_target, os.path.basename(self.test_source_folder1))

        ex_raised = False
        try:
            bkprep.do_copy_file(self.test_source_folder1, None, None)
        except backup_preparation.BackupPreparationException as bkprepbpex:
            ex_raised = True

        self.assertFalse(ex_raised)

    def testDoCopyFileWarnSize1(self):
        bkprep = backup_preparation.BackupPreparation("")
        self.assertTrue(bkprep.proc_single_config("SET_STORAGE_PATH", self.prep_target, []))
        self.assertTrue(bkprep.proc_single_config("SET_WARN_SIZE_EACH", "1", []))

        final_path = path_utils.concat_path(self.prep_target, os.path.basename(self.test_source_folder1))

        ex_raised = False
        try:
            bkprep.do_copy_file(self.test_source_folder1, None, None)
        except backup_preparation.BackupPreparationException as bkprepbpex:
            ex_raised = True

        self.assertFalse(ex_raised)

    def testDoCopyFileWarnSize2(self):
        bkprep = backup_preparation.BackupPreparation("")
        self.assertTrue(bkprep.proc_single_config("SET_STORAGE_PATH", self.prep_target, []))
        self.assertTrue(bkprep.proc_single_config("SET_WARN_SIZE_EACH", "1Gb", []))

        final_path = path_utils.concat_path(self.prep_target, os.path.basename(self.test_source_folder1))

        ex_raised = False
        try:
            bkprep.do_copy_file(self.test_source_folder1, None, None)
        except backup_preparation.BackupPreparationException as bkprepbpex:
            ex_raised = True

        self.assertFalse(ex_raised)

        shutil.rmtree(final_path)

        ex_raised = False
        try:
            bkprep.do_copy_file(self.test_source_folder1, 1, True)
        except backup_preparation.BackupPreparationException as bkprepbpex:
            ex_raised = True

        self.assertTrue(ex_raised)

    def testDoCopyContent1(self):
        bkprep = backup_preparation.BackupPreparation("")
        self.assertTrue(bkprep.proc_single_config("SET_STORAGE_PATH", self.prep_target, []))

        test_fn = "local.txt"
        test_content = "abc"
        final_path = path_utils.concat_path(self.prep_target, test_fn)

        bkprep.do_copy_content(test_content, test_fn)
        self.assertTrue(os.path.exists(final_path))

    def testDoCopyContentFail1(self):
        bkprep = backup_preparation.BackupPreparation("")
        self.assertTrue(bkprep.proc_single_config("SET_STORAGE_PATH", self.prep_target, []))

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
        self.assertTrue(bkprep.proc_single_config("SET_STORAGE_PATH", self.prep_target, []))
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
        self.assertTrue(bkprep.proc_single_config("SET_STORAGE_PATH", self.prep_target, []))
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

    def testDoCopyContentWarnSize(self):
        bkprep = backup_preparation.BackupPreparation("")
        self.assertTrue(bkprep.proc_single_config("SET_STORAGE_PATH", self.prep_target, []))
        self.assertTrue(bkprep.proc_single_config("SET_WARN_SIZE_EACH", "1", []))

        test_fn = "local.txt"
        test_content = "abc"
        final_path = path_utils.concat_path(self.prep_target, test_fn)

        ex_raised = False
        try:
            bkprep.do_copy_content(test_content, test_fn)
        except backup_preparation.BackupPreparationException as bkprepbpex:
            ex_raised = True

        self.assertFalse(ex_raised)

    def testProcessInstructions1(self):
        bkprep = backup_preparation.BackupPreparation("")
        self.assertTrue(bkprep.proc_single_config("SET_STORAGE_PATH", self.prep_target, []))
        self.assertTrue(bkprep.proc_single_config("SET_WARN_SIZE_FINAL", "100Mb", []))
        bkprep.instructions = []
        bkprep.instructions.append( ("COPY_PATH", self.file3, [("","")]) )

        ex_raised = False
        try:
            bkprep.process_instructions()
        except backup_preparation.BackupPreparationException as bkprepbpex:
            ex_raised = True

        self.assertFalse(ex_raised)
        self.assertTrue(os.path.exists(path_utils.concat_path(self.prep_target, os.path.basename(self.file3))))

    def testProcessInstructions2(self):
        bkprep = backup_preparation.BackupPreparation("")
        self.assertTrue(bkprep.proc_single_config("SET_STORAGE_PATH", self.prep_target, []))
        self.assertTrue(bkprep.proc_single_config("SET_WARN_SIZE_FINAL", "1", []))
        bkprep.instructions = []
        bkprep.instructions.append( ("COPY_PATH", self.file3, [("","")]) )

        ex_raised = False
        try:
            bkprep.process_instructions()
        except backup_preparation.BackupPreparationException as bkprepbpex:
            ex_raised = True

        self.assertFalse(ex_raised)
        self.assertTrue(os.path.exists(path_utils.concat_path(self.prep_target, os.path.basename(self.file3))))

    def testProcessInstructions3(self):
        bkprep = backup_preparation.BackupPreparation("")
        self.assertTrue(bkprep.proc_single_config("SET_STORAGE_PATH", self.prep_target, []))
        self.assertTrue(bkprep.proc_single_config("SET_WARN_SIZE_FINAL", "1", [("abort", "")]))
        bkprep.instructions = []
        bkprep.instructions.append( ("COPY_PATH", self.file3, [("","")]) )

        ex_raised = False
        try:
            bkprep.process_instructions()
        except backup_preparation.BackupPreparationException as bkprepbpex:
            ex_raised = True

        self.assertTrue(ex_raised)
        self.assertTrue(os.path.exists(path_utils.concat_path(self.prep_target, os.path.basename(self.file3))))

    def testProcessInstructionsFail1(self):
        bkprep = backup_preparation.BackupPreparation("")
        self.assertTrue(bkprep.proc_single_config("SET_STORAGE_PATH", self.prep_target, []))
        self.assertTrue(bkprep.proc_single_config("SET_WARN_SIZE_FINAL", "1", [("abort", "")]))
        bkprep.instructions = []
        bkprep.instructions.append( ("COPY_PATH", self.nonexistant, []) )

        ex_raised = False
        try:
            bkprep.process_instructions()
        except backup_preparation.BackupPreparationException as bkprepbpex:
            ex_raised = True

        self.assertTrue(ex_raised)
        self.assertFalse(os.path.exists(path_utils.concat_path(self.prep_target, os.path.basename(self.nonexistant))))

    def testProcessInstructionsFail2(self):
        bkprep = backup_preparation.BackupPreparation("")
        self.assertTrue(bkprep.proc_single_config("SET_STORAGE_PATH", self.prep_target, []))
        bkprep.instructions = []
        bkprep.instructions.append( ("COPY_PATH", self.file3, []) )

        create_and_write_file.create_file_contents(path_utils.concat_path(self.prep_target, os.path.basename(self.file3)), "testcontents")

        ex_raised = False
        try:
            bkprep.process_instructions()
        except backup_preparation.BackupPreparationException as bkprepbpex:
            ex_raised = True

        self.assertTrue(ex_raised)

    def testProcessInstructionsFail3(self):
        bkprep = backup_preparation.BackupPreparation("")
        self.assertTrue(bkprep.proc_single_config("SET_STORAGE_PATH", self.prep_target, []))
        bkprep.instructions = []
        bkprep.instructions.append( ("BOGUS_INSTRUCTION", self.file3, []) )

        ex_raised = False
        try:
            bkprep.process_instructions()
        except backup_preparation.BackupPreparationException as bkprepbpex:
            ex_raised = True

        self.assertTrue(ex_raised)

    def testProcessInstructionsOverrideWarns(self):
        bkprep = backup_preparation.BackupPreparation("")
        self.assertTrue(bkprep.proc_single_config("SET_STORAGE_PATH", self.prep_target, []))

        final_path = path_utils.concat_path(self.prep_target, os.path.basename(self.file3))

        bkprep.instructions = []
        bkprep.instructions.append( ("COPY_PATH", self.file3, []) )
        ex_raised = False
        try:
            bkprep.process_instructions()
        except backup_preparation.BackupPreparationException as bkprepbpex:
            ex_raised = True

        self.assertFalse(ex_raised)
        self.assertTrue(os.path.exists(final_path))
        os.unlink(final_path)
        self.assertFalse(os.path.exists(final_path))

        bkprep.instructions = []
        bkprep.instructions.append( ("COPY_PATH", self.file3, [("warn_size", "1"), ("warn_abort", "")] ) )
        ex_raised = False
        try:
            bkprep.process_instructions()
        except backup_preparation.BackupPreparationException as bkprepbpex:
            ex_raised = True

        self.assertTrue(ex_raised)
        self.assertFalse(os.path.exists(final_path))

    def testProcSingleInst(self):
        bkprep = backup_preparation.BackupPreparation("")

        ex_raised = False
        try:
            bkprep.proc_single_inst("NONEXISTANT_INSTRUCTION", None, None)
        except backup_preparation.BackupPreparationException as bkprepbpex:
            ex_raised = True

        self.assertTrue(ex_raised)

    def testProcCopyPath(self):
        bkprep = backup_preparation.BackupPreparation("")
        self.assertTrue(bkprep.proc_single_config("SET_STORAGE_PATH", self.prep_target, []))

        bkprep.proc_copy_path(self.test_source_folder1, [])
        self.assertTrue(os.path.exists(path_utils.concat_path(self.prep_target, os.path.basename(self.test_source_folder1))))

        bkprep.proc_copy_path(self.nonexistant, [])
        self.assertFalse(os.path.exists(path_utils.concat_path(self.prep_target, os.path.basename(self.nonexistant))))

        ex_raised = False
        try:
            bkprep.proc_copy_path(self.nonexistant, [("abort", "")])
        except backup_preparation.BackupPreparationException as bkprepbpex:
            ex_raised = True

        self.assertTrue(ex_raised)
        self.assertFalse(os.path.exists(path_utils.concat_path(self.prep_target, os.path.basename(self.nonexistant))))

    def testProcCopyTreeOut(self):
        bkprep = backup_preparation.BackupPreparation("")
        self.assertTrue(bkprep.proc_single_config("SET_STORAGE_PATH", self.prep_target, []))

        final_path = path_utils.concat_path(self.prep_target, backup_preparation.derivefoldernamefortree(self.test_source_folder2))
        bkprep.proc_copy_tree_out(self.test_source_folder2, [])
        self.assertTrue(os.path.exists(final_path))
        cmp_str = self.test_source_folder2 + os.linesep + "└── file2.txt" + os.linesep + os.linesep + "0 directories, 1 file" + os.linesep

        str_read = ""
        with open(final_path) as f:
            str_read = f.read()

        self.assertEqual(cmp_str, str_read)

        ex_raised = False
        try:
            bkprep.proc_copy_tree_out(self.nonexistant, [])
        except backup_preparation.BackupPreparationException as bkprepbpex:
            ex_raised = True

        self.assertFalse(ex_raised)

        ex_raised = False
        try:
            bkprep.proc_copy_tree_out(self.nonexistant, [("abort", "")])
        except backup_preparation.BackupPreparationException as bkprepbpex:
            ex_raised = True

        self.assertTrue(ex_raised)

    def testBackupPreparation1(self):
        self.assertTrue(backup_preparation.backup_preparation(self.test_config_file1))
        self.assertTrue(os.path.exists(path_utils.concat_path(self.prep_target)))
        self.assertTrue(os.path.exists(path_utils.concat_path(self.prep_target, os.path.basename(self.test_source_folder1))))
        self.assertTrue(os.path.exists(path_utils.concat_path(self.prep_target, os.path.basename(self.file3))))
        self.assertTrue(os.path.exists(path_utils.concat_path(self.prep_target, backup_preparation.derivefoldernamefortree(self.test_source_folder2))))

    def testBackupPreparation2(self):
        self.assertTrue(backup_preparation.backup_preparation(self.test_config_file2))
        self.assertTrue(os.path.exists(path_utils.concat_path(self.prep_target)))
        self.assertTrue(os.path.exists(path_utils.concat_path(self.prep_target, os.path.basename(self.test_source_folder2))))
        self.assertFalse(os.path.exists(path_utils.concat_path(self.prep_target, os.path.basename(self.file3))))
        self.assertTrue(os.path.exists(path_utils.concat_path(self.prep_target, backup_preparation.derivefoldernamefortree(self.test_source_folder1))))

    def testBackupPreparation3(self):
        self.assertTrue(backup_preparation.backup_preparation(self.test_config_file4))
        self.assertTrue(os.path.exists(path_utils.concat_path(self.prep_target)))
        self.assertTrue(os.path.exists(path_utils.concat_path(self.prep_target, os.path.basename(self.test_source_folder3))))

    def testBackupPreparationFail1(self):
        self.assertFalse(backup_preparation.backup_preparation(self.test_config_file_fail1))

    def testBackupPreparationFail2(self):
        self.assertFalse(backup_preparation.backup_preparation(self.test_config_file_fail3))

    def testBackupPreparationFail3(self):
        self.assertFalse(backup_preparation.backup_preparation(self.test_config_file_fail4))

if __name__ == '__main__':
    unittest.main()
