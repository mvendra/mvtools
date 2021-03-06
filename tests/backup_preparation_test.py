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
import git_test_fixture
import git_wrapper
import path_utils
import git_lib

class BackupPreparationTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

        # folder where to store the preparation artifacts
        self.prep_target = path_utils.concat_path(self.test_dir, "preptarget")
        path_utils.scratchfolder(self.prep_target)

        # test repo bases
        self.repo_src_folder = path_utils.concat_path(self.test_dir, "repo_src_test")
        os.mkdir(self.repo_src_folder)

        # test repos paths
        self.first_repo = path_utils.concat_path(self.repo_src_folder, "first")
        self.second_repo = path_utils.concat_path(self.repo_src_folder, "second")
        self.third_repo = path_utils.concat_path(self.repo_src_folder, "third")

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

        file_cnav1_contents = ""
        file_cnav1_contents += "#!/usr/bin/env python3" + os.linesep
        file_cnav1_contents += "import sys" + os.linesep
        file_cnav1_contents += "import os" + os.linesep
        file_cnav1_contents += "def visit_path(path):" + os.linesep
        file_cnav1_contents += "    ret = []" + os.linesep
        file_cnav1_contents += ("    ret.append(\"%s\")" + os.linesep) % self.first_repo
        file_cnav1_contents += ("    ret.append(\"%s\")" + os.linesep) % self.third_repo
        file_cnav1_contents += "    return ret" + os.linesep
        self.test_cnav1_file = path_utils.concat_path(self.test_dir, "test_cnav1_file.py")
        create_and_write_file.create_file_contents(self.test_cnav1_file, file_cnav1_contents)
        cfg_file_contents5 = ""
        cfg_file_contents5 += ("SET_STORAGE_PATH = \"%s\"" + os.linesep) % (self.prep_target)
        cfg_file_contents5 += ("RUN_COLLECT_PATCHES {custom-path-navigator: \"%s\" / storage-base: \"collected_patches\" / default-exclude / include: \"*/second\" / head-id} = \"%s\"" + os.linesep) % (self.test_cnav1_file, self.repo_src_folder)
        self.test_config_file5 = path_utils.concat_path(self.test_dir, "test_config_file5.cfg")
        create_and_write_file.create_file_contents(self.test_config_file5, cfg_file_contents5)

        file_cnav2_contents = ""
        file_cnav2_contents += "#!/usr/bin/env python3" + os.linesep
        file_cnav2_contents += "def invalid_interface(path):" + os.linesep
        file_cnav2_contents += "    return []" + os.linesep
        self.test_cnav2_file = path_utils.concat_path(self.test_dir, "test_cnav2_file.py")
        create_and_write_file.create_file_contents(self.test_cnav2_file, file_cnav2_contents)

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

    def testDeriveFolderNameForTree(self):
        self.assertEqual(backup_preparation.derivefoldernamefortree("/home/user/folder"), "folder_tree_out.txt")

    def testDeriveFilenameForCrontab(self):
        self.assertEqual(backup_preparation.derivefilenameforcrontab(), "crontab_" + getpass.getuser() + ".txt")

    def testReadConfig1(self):
        bkprep = backup_preparation.BackupPreparation(self.test_config_file1)
        bkprep.read_config(bkprep.config_file)
        bkprep.setup_configuration()
        self.assertEqual(bkprep.storage_path, self.prep_target)
        self.assertTrue(bkprep.storage_path_reset)
        self.assertTrue(bkprep.warn_size_each_active)
        self.assertEqual(bkprep.warn_size_each, int(self.warn_size_each1))
        self.assertTrue(bkprep.warn_size_each_abort)
        self.assertTrue(bkprep.warn_size_final_active)
        self.assertEqual(bkprep.warn_size_final, int(self.warn_size_final1))
        self.assertTrue(bkprep.warn_size_final_abort)

    def testReadConfig2(self):
        bkprep = backup_preparation.BackupPreparation("")
        bkprep.read_config(self.test_config_file2)
        bkprep.setup_configuration()
        self.assertEqual(bkprep.storage_path, self.prep_target)
        self.assertFalse(bkprep.storage_path_reset)
        self.assertTrue(bkprep.warn_size_each_active)
        self.assertEqual(bkprep.warn_size_each, int(self.warn_size_each2))
        self.assertFalse(bkprep.warn_size_each_abort)
        self.assertTrue(bkprep.warn_size_final_active)
        self.assertEqual(bkprep.warn_size_final, int(self.warn_size_final2))
        self.assertFalse(bkprep.warn_size_final_abort)

    def testReadConfig3(self):
        bkprep = backup_preparation.BackupPreparation(self.test_config_file3)
        bkprep.read_config(bkprep.config_file)
        bkprep.setup_configuration()
        self.assertEqual(bkprep.storage_path, self.prep_target)
        self.assertFalse(bkprep.storage_path_reset)
        self.assertFalse(bkprep.warn_size_each_active)
        self.assertEqual(bkprep.warn_size_each, 0)
        self.assertFalse(bkprep.warn_size_each_abort)
        self.assertFalse(bkprep.warn_size_final_active)
        self.assertEqual(bkprep.warn_size_final, 0)
        self.assertFalse(bkprep.warn_size_final_abort)

    def testReadConfig4(self):
        bkprep = backup_preparation.BackupPreparation(self.test_config_file4)
        bkprep.read_config(bkprep.config_file)
        bkprep.setup_configuration()
        self.assertEqual( (self.test_source_folder3 + os.sep), bkprep.instructions[0][1])

    def testReadConfig5(self):
        bkprep = backup_preparation.BackupPreparation(self.test_config_file5)
        bkprep.read_config(bkprep.config_file)
        bkprep.setup_configuration()
        self.assertEqual( "RUN_COLLECT_PATCHES", bkprep.instructions[0][0])
        self.assertEqual( self.repo_src_folder, bkprep.instructions[0][1])
        self.assertEqual( "custom-path-navigator", bkprep.instructions[0][2][0][0])
        self.assertEqual( self.test_cnav1_file, bkprep.instructions[0][2][0][1])
        self.assertEqual( "storage-base", bkprep.instructions[0][2][1][0])
        self.assertEqual( "collected_patches", bkprep.instructions[0][2][1][1])
        self.assertEqual( "default-exclude", bkprep.instructions[0][2][2][0])
        self.assertEqual( "include", bkprep.instructions[0][2][3][0])
        self.assertEqual( "*/second", bkprep.instructions[0][2][3][1])
        self.assertEqual( "head-id", bkprep.instructions[0][2][4][0])

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

        final_path = path_utils.concat_path(self.prep_target, path_utils.basename_filtered(self.test_source_folder1))
        bkprep.do_copy_file(self.test_source_folder1, None, None)
        self.assertTrue(os.path.exists(final_path))

    def testDoCopyFileFail1(self):
        bkprep = backup_preparation.BackupPreparation("")
        self.assertTrue(bkprep.proc_single_config("SET_STORAGE_PATH", self.prep_target, []))

        final_path = path_utils.concat_path(self.prep_target, path_utils.basename_filtered(self.test_source_folder1))
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

        final_path = path_utils.concat_path(self.prep_target, path_utils.basename_filtered(self.test_source_folder1))

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

        final_path = path_utils.concat_path(self.prep_target, path_utils.basename_filtered(self.test_source_folder1))

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

        final_path = path_utils.concat_path(self.prep_target, path_utils.basename_filtered(self.test_source_folder1))

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

        final_path = path_utils.concat_path(self.prep_target, path_utils.basename_filtered(self.test_source_folder1))

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
        self.assertTrue(os.path.exists(path_utils.concat_path(self.prep_target, path_utils.basename_filtered(self.file3))))

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
        self.assertTrue(os.path.exists(path_utils.concat_path(self.prep_target, path_utils.basename_filtered(self.file3))))

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
        self.assertTrue(os.path.exists(path_utils.concat_path(self.prep_target, path_utils.basename_filtered(self.file3))))

    def testProcessInstructionsFail1(self):
        bkprep = backup_preparation.BackupPreparation("")
        self.assertTrue(bkprep.proc_single_config("SET_STORAGE_PATH", self.prep_target, []))
        bkprep.instructions = []
        bkprep.instructions.append( ("COPY_PATH", self.nonexistant, []) )

        ex_raised = False
        try:
            bkprep.process_instructions()
        except backup_preparation.BackupPreparationException as bkprepbpex:
            ex_raised = True

        self.assertFalse(ex_raised)
        self.assertFalse(os.path.exists(path_utils.concat_path(self.prep_target, path_utils.basename_filtered(self.nonexistant))))

    def testProcessInstructionsFail2(self):
        bkprep = backup_preparation.BackupPreparation("")
        self.assertTrue(bkprep.proc_single_config("SET_STORAGE_PATH", self.prep_target, []))
        bkprep.instructions = []
        bkprep.instructions.append( ("COPY_PATH {abort}", self.nonexistant, []) )

        ex_raised = False
        try:
            bkprep.process_instructions()
        except backup_preparation.BackupPreparationException as bkprepbpex:
            ex_raised = True

        self.assertTrue(ex_raised)
        self.assertFalse(os.path.exists(path_utils.concat_path(self.prep_target, path_utils.basename_filtered(self.nonexistant))))

    def testProcessInstructionsFail3(self):
        bkprep = backup_preparation.BackupPreparation("")
        self.assertTrue(bkprep.proc_single_config("SET_STORAGE_PATH", self.prep_target, []))
        bkprep.instructions = []
        bkprep.instructions.append( ("COPY_PATH", self.file3, []) )

        create_and_write_file.create_file_contents(path_utils.concat_path(self.prep_target, path_utils.basename_filtered(self.file3)), "testcontents")

        ex_raised = False
        try:
            bkprep.process_instructions()
        except backup_preparation.BackupPreparationException as bkprepbpex:
            ex_raised = True

        self.assertTrue(ex_raised)

    def testProcessInstructionsFail4(self):
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

        final_path = path_utils.concat_path(self.prep_target, path_utils.basename_filtered(self.file3))

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
        self.assertTrue(os.path.exists(path_utils.concat_path(self.prep_target, path_utils.basename_filtered(self.test_source_folder1))))

        bkprep.proc_copy_path(self.nonexistant, [])
        self.assertFalse(os.path.exists(path_utils.concat_path(self.prep_target, path_utils.basename_filtered(self.nonexistant))))

        ex_raised = False
        try:
            bkprep.proc_copy_path(self.nonexistant, [("abort", "")])
        except backup_preparation.BackupPreparationException as bkprepbpex:
            ex_raised = True

        self.assertTrue(ex_raised)
        self.assertFalse(os.path.exists(path_utils.concat_path(self.prep_target, path_utils.basename_filtered(self.nonexistant))))

    def testProcCopyTreeOut(self):
        bkprep = backup_preparation.BackupPreparation("")
        self.assertTrue(bkprep.proc_single_config("SET_STORAGE_PATH", self.prep_target, []))

        final_path = path_utils.concat_path(self.prep_target, backup_preparation.derivefoldernamefortree(self.test_source_folder2))
        bkprep.proc_copy_tree_out(self.test_source_folder2, [])
        self.assertTrue(os.path.exists(final_path))

        str_read = ""
        with open(final_path) as f:
            str_read = f.read()

        self.assertTrue( path_utils.basename_filtered(self.file2) in str_read)
        self.assertFalse( path_utils.basename_filtered(self.file3) in str_read)

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

    def testProcRunCollectPatches1(self):

        # first repo
        v, r = git_wrapper.init(self.repo_src_folder, "first", False)
        if not v:
            self.fail(r)
        first_repo_file1 = path_utils.concat_path(self.first_repo, "file1.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, path_utils.basename_filtered(first_repo_file1), "r1-file1-content1", "r1-commit_msg_file1")
        if not v:
            self.fail(r)
        with open(first_repo_file1, "a") as f:
            f.write("additional contents, r1-f1")

        # second repo
        v, r = git_wrapper.init(self.repo_src_folder, "second", False)
        if not v:
            self.fail(r)
        second_repo_file1 = path_utils.concat_path(self.second_repo, "file1.txt")
        v, r = git_test_fixture.git_createAndCommit(self.second_repo, path_utils.basename_filtered(second_repo_file1), "r2-file1-content1", "r2-commit_msg_file1")
        if not v:
            self.fail(r)
        with open(second_repo_file1, "a") as f:
            f.write("additional contents, r2-f1")

        bkprep = backup_preparation.BackupPreparation("")
        self.assertTrue(bkprep.proc_single_config("SET_STORAGE_PATH", self.prep_target, []))

        bkprep.proc_run_collect_patches(self.repo_src_folder, [("storage-base", "collected_patches"), ("git", ""), ("default-include", ""), ("head", ""), ("head-id", ""), ("head-staged", ""), ("head-unversioned", ""), ("stash", ""), ("previous", "1")])

        collected_first_repo = path_utils.concat_path(self.prep_target, "collected_patches", self.first_repo)
        collected_first_repo_head_patch = path_utils.concat_path(collected_first_repo, "head.patch")
        collected_first_repo_head_patch_contents = ""
        with open(collected_first_repo_head_patch) as f:
            collected_first_repo_head_patch_contents = f.read()
        collected_first_repo_head_staged_patch = path_utils.concat_path(collected_first_repo, "head_staged.patch")
        collected_first_repo_head_id_patch = path_utils.concat_path(collected_first_repo, "head_id.txt")
        v, r = git_lib.get_previous_hash_list(self.first_repo, 1)
        if not v:
            self.fail(r)
        collected_first_repo_previous_1 = path_utils.concat_path(collected_first_repo, "previous_1_%s.patch" % r[0])
        collected_first_repo_previous_1_contents = ""
        with open(collected_first_repo_previous_1) as f:
            collected_first_repo_previous_1_contents = f.read()

        collected_second_repo = path_utils.concat_path(self.prep_target, "collected_patches", self.second_repo)
        collected_second_repo_head_patch = path_utils.concat_path(collected_second_repo, "head.patch")
        collected_second_repo_head_patch_contents = ""
        with open(collected_second_repo_head_patch) as f:
            collected_second_repo_head_patch_contents = f.read()
        collected_second_repo_head_staged_patch = path_utils.concat_path(collected_second_repo, "head_staged.patch")
        collected_second_repo_head_id_patch = path_utils.concat_path(collected_second_repo, "head_id.txt")
        v, r = git_lib.get_previous_hash_list(self.second_repo, 1)
        if not v:
            self.fail(r)
        collected_second_repo_previous_1 = path_utils.concat_path(collected_second_repo, "previous_1_%s.patch" % r[0])
        collected_second_repo_previous_1_contents = ""
        with open(collected_second_repo_previous_1) as f:
            collected_second_repo_previous_1_contents = f.read()

        self.assertTrue(os.path.exists(collected_first_repo))
        self.assertTrue(os.path.exists(collected_first_repo_head_patch))
        self.assertTrue( "additional contents, r1-f1" in collected_first_repo_head_patch_contents )
        self.assertTrue(os.path.exists(collected_first_repo_head_staged_patch))
        self.assertTrue(os.path.exists(collected_first_repo_head_id_patch))
        self.assertTrue(os.path.exists(collected_first_repo_previous_1))
        self.assertTrue( "r1-file1-content1" in collected_first_repo_previous_1_contents )

        self.assertTrue(os.path.exists(collected_second_repo))
        self.assertTrue(os.path.exists(collected_second_repo_head_patch))
        self.assertTrue( "additional contents, r2-f1" in collected_second_repo_head_patch_contents )
        self.assertTrue(os.path.exists(collected_second_repo_head_staged_patch))
        self.assertTrue(os.path.exists(collected_second_repo_head_id_patch))
        self.assertTrue(os.path.exists(collected_second_repo_previous_1))
        self.assertTrue( "r2-file1-content1" in collected_second_repo_previous_1_contents )

    def testProcRunCollectPatches_ExcludeAll(self):

        # first repo
        v, r = git_wrapper.init(self.repo_src_folder, "first", False)
        if not v:
            self.fail(r)
        first_repo_file1 = path_utils.concat_path(self.first_repo, "file1.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, path_utils.basename_filtered(first_repo_file1), "r1-file1-content1", "r1-commit_msg_file1")
        if not v:
            self.fail(r)
        with open(first_repo_file1, "a") as f:
            f.write("additional contents, r1-f1")

        # second repo
        v, r = git_wrapper.init(self.repo_src_folder, "second", False)
        if not v:
            self.fail(r)
        second_repo_file1 = path_utils.concat_path(self.second_repo, "file1.txt")
        v, r = git_test_fixture.git_createAndCommit(self.second_repo, path_utils.basename_filtered(second_repo_file1), "r2-file1-content1", "r2-commit_msg_file1")
        if not v:
            self.fail(r)
        with open(second_repo_file1, "a") as f:
            f.write("additional contents, r2-f1")

        bkprep = backup_preparation.BackupPreparation("")
        self.assertTrue(bkprep.proc_single_config("SET_STORAGE_PATH", self.prep_target, []))

        bkprep.proc_run_collect_patches(self.repo_src_folder, [("storage-base", "collected_patches"), ("git", ""), ("default-exclude", ""), ("head", ""), ("head-id", ""), ("head-staged", ""), ("head-unversioned", ""), ("stash", ""), ("previous", "1")])

        collected_first_repo = path_utils.concat_path(self.prep_target, "collected_patches", self.first_repo)
        collected_second_repo = path_utils.concat_path(self.prep_target, "collected_patches", self.second_repo)

        self.assertFalse(os.path.exists(collected_first_repo))
        self.assertFalse(os.path.exists(collected_second_repo))

    def testProcRunCollectPatches_DefaultExclude_IncludeSecondOnly(self):

        # first repo
        v, r = git_wrapper.init(self.repo_src_folder, "first", False)
        if not v:
            self.fail(r)
        first_repo_file1 = path_utils.concat_path(self.first_repo, "file1.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, path_utils.basename_filtered(first_repo_file1), "r1-file1-content1", "r1-commit_msg_file1")
        if not v:
            self.fail(r)

        # second repo
        v, r = git_wrapper.init(self.repo_src_folder, "second", False)
        if not v:
            self.fail(r)
        second_repo_file1 = path_utils.concat_path(self.second_repo, "file1.txt")
        v, r = git_test_fixture.git_createAndCommit(self.second_repo, path_utils.basename_filtered(second_repo_file1), "r2-file1-content1", "r2-commit_msg_file1")
        if not v:
            self.fail(r)

        # third repo
        v, r = git_wrapper.init(self.repo_src_folder, "third", False)
        if not v:
            self.fail(r)
        third_repo_file1 = path_utils.concat_path(self.third_repo, "file1.txt")
        v, r = git_test_fixture.git_createAndCommit(self.third_repo, path_utils.basename_filtered(third_repo_file1), "r3-file1-content1", "r3-commit_msg_file1")
        if not v:
            self.fail(r)

        bkprep = backup_preparation.BackupPreparation("")
        self.assertTrue(bkprep.proc_single_config("SET_STORAGE_PATH", self.prep_target, []))

        bkprep.proc_run_collect_patches(self.repo_src_folder, [("storage-base", "collected_patches"), ("git", ""), ("default-exclude", ""), ("include", "*/second"), ("head", ""), ("head-id", ""), ("head-staged", ""), ("head-unversioned", ""), ("stash", ""), ("previous", "1")])

        collected_first_repo = path_utils.concat_path(self.prep_target, "collected_patches", self.first_repo)
        collected_second_repo = path_utils.concat_path(self.prep_target, "collected_patches", self.second_repo)
        collected_third_repo = path_utils.concat_path(self.prep_target, "collected_patches", self.third_repo)

        self.assertFalse(os.path.exists(collected_first_repo))
        self.assertTrue(os.path.exists(collected_second_repo))
        self.assertFalse(os.path.exists(collected_third_repo))

    def testProcRunCollectPatches_CustomPathNav_DefaultInclude_ExcludeSecondByCnav_ExcludeThirdByFilter(self):

        # first repo
        v, r = git_wrapper.init(self.repo_src_folder, "first", False)
        if not v:
            self.fail(r)
        first_repo_file1 = path_utils.concat_path(self.first_repo, "file1.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, path_utils.basename_filtered(first_repo_file1), "r1-file1-content1", "r1-commit_msg_file1")
        if not v:
            self.fail(r)

        # second repo
        v, r = git_wrapper.init(self.repo_src_folder, "second", False)
        if not v:
            self.fail(r)
        second_repo_file1 = path_utils.concat_path(self.second_repo, "file1.txt")
        v, r = git_test_fixture.git_createAndCommit(self.second_repo, path_utils.basename_filtered(second_repo_file1), "r2-file1-content1", "r2-commit_msg_file1")
        if not v:
            self.fail(r)

        # third repo
        v, r = git_wrapper.init(self.repo_src_folder, "third", False)
        if not v:
            self.fail(r)
        third_repo_file1 = path_utils.concat_path(self.third_repo, "file1.txt")
        v, r = git_test_fixture.git_createAndCommit(self.third_repo, path_utils.basename_filtered(third_repo_file1), "r3-file1-content1", "r3-commit_msg_file1")
        if not v:
            self.fail(r)

        bkprep = backup_preparation.BackupPreparation("")
        self.assertTrue(bkprep.proc_single_config("SET_STORAGE_PATH", self.prep_target, []))

        bkprep.proc_run_collect_patches(self.repo_src_folder, [("custom-path-navigator", self.test_cnav1_file), ("storage-base", "collected_patches"), ("git", ""), ("default-include", ""), ("exclude", "*/third"), ("head-id", "")])

        collected_first_repo = path_utils.concat_path(self.prep_target, "collected_patches", self.first_repo)
        collected_second_repo = path_utils.concat_path(self.prep_target, "collected_patches", self.second_repo)
        collected_third_repo = path_utils.concat_path(self.prep_target, "collected_patches", self.third_repo)

        self.assertTrue(os.path.exists(collected_first_repo))
        self.assertFalse(os.path.exists(collected_second_repo))
        self.assertFalse(os.path.exists(collected_third_repo))

    def testProcRunCollectPatches_CustomPathNavFail(self):

        # first repo
        v, r = git_wrapper.init(self.repo_src_folder, "first", False)
        if not v:
            self.fail(r)
        first_repo_file1 = path_utils.concat_path(self.first_repo, "file1.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, path_utils.basename_filtered(first_repo_file1), "r1-file1-content1", "r1-commit_msg_file1")
        if not v:
            self.fail(r)

        bkprep = backup_preparation.BackupPreparation("")
        self.assertTrue(bkprep.proc_single_config("SET_STORAGE_PATH", self.prep_target, []))

        ex_raised = False
        try:
            bkprep.proc_run_collect_patches(self.repo_src_folder, [("custom-path-navigator", self.test_cnav2_file), ("storage-base", "collected_patches"), ("head-id", "")])
        except backup_preparation.BackupPreparationException as bkprepbpex:
            ex_raised = True

        self.assertTrue(ex_raised)

    def testProcRunCollectPatches_DefaultInclude_ExcludeThirdOnly(self):

        # first repo
        v, r = git_wrapper.init(self.repo_src_folder, "first", False)
        if not v:
            self.fail(r)
        first_repo_file1 = path_utils.concat_path(self.first_repo, "file1.txt")
        v, r = git_test_fixture.git_createAndCommit(self.first_repo, path_utils.basename_filtered(first_repo_file1), "r1-file1-content1", "r1-commit_msg_file1")
        if not v:
            self.fail(r)

        # second repo
        v, r = git_wrapper.init(self.repo_src_folder, "second", False)
        if not v:
            self.fail(r)
        second_repo_file1 = path_utils.concat_path(self.second_repo, "file1.txt")
        v, r = git_test_fixture.git_createAndCommit(self.second_repo, path_utils.basename_filtered(second_repo_file1), "r2-file1-content1", "r2-commit_msg_file1")
        if not v:
            self.fail(r)

        # third repo
        v, r = git_wrapper.init(self.repo_src_folder, "third", False)
        if not v:
            self.fail(r)
        third_repo_file1 = path_utils.concat_path(self.third_repo, "file1.txt")
        v, r = git_test_fixture.git_createAndCommit(self.third_repo, path_utils.basename_filtered(third_repo_file1), "r3-file1-content1", "r3-commit_msg_file1")
        if not v:
            self.fail(r)

        bkprep = backup_preparation.BackupPreparation("")
        self.assertTrue(bkprep.proc_single_config("SET_STORAGE_PATH", self.prep_target, []))

        bkprep.proc_run_collect_patches(self.repo_src_folder, [("storage-base", "collected_patches"), ("git", ""), ("default-include", ""), ("exclude", "*/third"), ("head", ""), ("head-id", ""), ("head-staged", ""), ("head-unversioned", ""), ("stash", ""), ("previous", "1")])

        collected_first_repo = path_utils.concat_path(self.prep_target, "collected_patches", self.first_repo)
        collected_second_repo = path_utils.concat_path(self.prep_target, "collected_patches", self.second_repo)
        collected_third_repo = path_utils.concat_path(self.prep_target, "collected_patches", self.third_repo)

        self.assertTrue(os.path.exists(collected_first_repo))
        self.assertTrue(os.path.exists(collected_second_repo))
        self.assertFalse(os.path.exists(collected_third_repo))

    def testBackupPreparation1(self):
        self.assertTrue(backup_preparation.backup_preparation(self.test_config_file1))
        self.assertTrue(os.path.exists(path_utils.concat_path(self.prep_target)))
        self.assertTrue(os.path.exists(path_utils.concat_path(self.prep_target, path_utils.basename_filtered(self.test_source_folder1))))
        self.assertTrue(os.path.exists(path_utils.concat_path(self.prep_target, path_utils.basename_filtered(self.file3))))
        self.assertTrue(os.path.exists(path_utils.concat_path(self.prep_target, backup_preparation.derivefoldernamefortree(self.test_source_folder2))))

    def testBackupPreparation2(self):
        self.assertTrue(backup_preparation.backup_preparation(self.test_config_file2))
        self.assertTrue(os.path.exists(path_utils.concat_path(self.prep_target)))
        self.assertTrue(os.path.exists(path_utils.concat_path(self.prep_target, path_utils.basename_filtered(self.test_source_folder2))))
        self.assertFalse(os.path.exists(path_utils.concat_path(self.prep_target, path_utils.basename_filtered(self.file3))))
        self.assertTrue(os.path.exists(path_utils.concat_path(self.prep_target, backup_preparation.derivefoldernamefortree(self.test_source_folder1))))

    def testBackupPreparation3(self):
        self.assertTrue(backup_preparation.backup_preparation(self.test_config_file4))
        self.assertTrue(os.path.exists(path_utils.concat_path(self.prep_target)))
        self.assertTrue(os.path.exists(path_utils.concat_path(self.prep_target, path_utils.basename_filtered(self.test_source_folder3))))

    def testBackupPreparationFail1(self):
        self.assertFalse(backup_preparation.backup_preparation(self.test_config_file_fail1))

    def testBackupPreparationFail2(self):
        self.assertFalse(backup_preparation.backup_preparation(self.test_config_file_fail3))

    def testBackupPreparationFail3(self):
        self.assertFalse(backup_preparation.backup_preparation(self.test_config_file_fail4))

if __name__ == '__main__':
    unittest.main()
