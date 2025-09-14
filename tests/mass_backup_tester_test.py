#!/usr/bin/env python

import sys
import os
import stat
import shutil
import unittest
from unittest import mock
from unittest.mock import patch

import create_and_write_file
import mvtools_test_fixture
import backup_processor
import path_utils

import mass_backup_tester

class MassBackupTesterTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("mass_backup_tester_test")
        if not v:
            return v, r
        self.test_base_dir = r[0]
        self.test_dir = r[1]

        self.bk_test_temp_folder = path_utils.concat_path(self.test_dir, "bktemp")
        self.bk_base_folder_test = "BackupTests"
        self.test_source_folder = path_utils.concat_path(self.test_dir, "source_test")
        os.mkdir(self.test_source_folder)
        self.test_target_path = path_utils.concat_path(self.test_dir, "target_test")
        os.mkdir(self.test_target_path)

        # create test folders
        self.folder1 = path_utils.concat_path(self.test_source_folder, "folder1")
        self.folder2 = path_utils.concat_path(self.test_source_folder, "folder2")
        os.mkdir(self.folder1)
        os.mkdir(self.folder2)

        # create files, folder1
        self.folder1_file1 = path_utils.concat_path(self.folder1, "file11.txt")
        create_and_write_file.create_file_contents(self.folder1_file1, "abc")

        # create files, folder2
        self.folder2_file1 = path_utils.concat_path(self.folder2, "file21.txt")
        create_and_write_file.create_file_contents(self.folder2_file1, "abc")

        # create config file
        cfg_file_contents = ""
        cfg_file_contents += ("BKSOURCE {descend} = \"%s\"" + os.linesep) % self.test_source_folder
        cfg_file_contents += ("BKTARGETS_ROOT {nocheckmount} = \"%s\"" + os.linesep) % self.test_target_path
        cfg_file_contents += ("BKTEMP = \"%s\"" + os.linesep) % self.bk_test_temp_folder
        cfg_file_contents += ("BKTARGETS_BASEDIR = \"%s\"" + os.linesep) % self.bk_base_folder_test
        self.test_config_file = path_utils.concat_path(self.test_dir, "test_config_file.t20")
        create_and_write_file.create_file_contents(self.test_config_file, cfg_file_contents)

        # hash file
        self.hash_file = path_utils.concat_path(self.test_dir, ".hash_file_test")
        self.passphrase = "abcdef"
        create_and_write_file.create_file_contents(self.hash_file, "e32ef19623e8ed9d267f657a81944b3d07adbb768518068e88435745564e8d4150a0a703be2a7d88b61e3d390c2bb97e2d4c311fdc69d6b1267f05f59aa920e7")

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testRunBackupOk(self):

        # basic execution
        with mock.patch("input_checked_passphrase.get_checked_passphrase", return_value=(True, self.passphrase)):
            r = backup_processor.run_backup(self.test_config_file, self.hash_file)
        self.assertTrue(r)

        tg_final = path_utils.concat_path(self.test_target_path, self.bk_base_folder_test)

        # sanity checks on the backup products themselves
        self.assertTrue( os.path.exists( path_utils.concat_path(tg_final, "bk_date.txt")) ) 
        tg_folder1_e = path_utils.concat_path(tg_final, "source_test", "folder1.tar.bz2.enc")
        tg_folder1_h = path_utils.concat_path(tg_final, "source_test", "folder1.tar.bz2.enc.sha512")
        tg_folder2_e = path_utils.concat_path(tg_final, "source_test", "folder2.tar.bz2.enc")
        tg_folder2_h = path_utils.concat_path(tg_final, "source_test", "folder2.tar.bz2.enc.sha512")
        self.assertTrue( os.path.exists( tg_folder1_e ) )
        self.assertTrue( os.path.exists( tg_folder1_h ) )
        self.assertTrue( os.path.exists( tg_folder2_e ) )
        self.assertTrue( os.path.exists( tg_folder2_h ) )

        with mock.patch("input_checked_passphrase.get_checked_passphrase", return_value=(True, self.passphrase)):
            r = mass_backup_tester.backups_mass_check(self.test_config_file, self.hash_file)
        self.assertTrue(r)

    def testRunBackupFail1(self):

        # basic execution
        with mock.patch("input_checked_passphrase.get_checked_passphrase", return_value=(True, self.passphrase)):
            r = backup_processor.run_backup(self.test_config_file, self.hash_file)
        self.assertTrue(r)

        tg_final = path_utils.concat_path(self.test_target_path, self.bk_base_folder_test)

        # sanity checks on the backup products themselves
        self.assertTrue( os.path.exists( path_utils.concat_path(tg_final, "bk_date.txt")) ) 
        tg_folder1_e = path_utils.concat_path(tg_final, "source_test", "folder1.tar.bz2.enc")
        tg_folder1_h = path_utils.concat_path(tg_final, "source_test", "folder1.tar.bz2.enc.sha512")
        tg_folder2_e = path_utils.concat_path(tg_final, "source_test", "folder2.tar.bz2.enc")
        tg_folder2_h = path_utils.concat_path(tg_final, "source_test", "folder2.tar.bz2.enc.sha512")
        self.assertTrue( os.path.exists( tg_folder1_e ) )
        self.assertTrue( os.path.exists( tg_folder1_h ) )
        self.assertTrue( os.path.exists( tg_folder2_e ) )
        self.assertTrue( os.path.exists( tg_folder2_h ) )

        with open(tg_folder2_h, "w") as f:
            f.write("tampering with folder2's hash")

        with mock.patch("input_checked_passphrase.get_checked_passphrase", return_value=(True, self.passphrase)):
            r = mass_backup_tester.backups_mass_check(self.test_config_file, self.hash_file)
        self.assertFalse(r)

    def testRunBackupFail2(self):

        # basic execution
        with mock.patch("input_checked_passphrase.get_checked_passphrase", return_value=(True, self.passphrase)):
            r = backup_processor.run_backup(self.test_config_file, self.hash_file)
        self.assertTrue(r)

        tg_final = path_utils.concat_path(self.test_target_path, self.bk_base_folder_test)

        # sanity checks on the backup products themselves
        self.assertTrue( os.path.exists( path_utils.concat_path(tg_final, "bk_date.txt")) ) 
        tg_folder1_e = path_utils.concat_path(tg_final, "source_test", "folder1.tar.bz2.enc")
        tg_folder1_h = path_utils.concat_path(tg_final, "source_test", "folder1.tar.bz2.enc.sha512")
        tg_folder2_e = path_utils.concat_path(tg_final, "source_test", "folder2.tar.bz2.enc")
        tg_folder2_h = path_utils.concat_path(tg_final, "source_test", "folder2.tar.bz2.enc.sha512")
        self.assertTrue( os.path.exists( tg_folder1_e ) )
        self.assertTrue( os.path.exists( tg_folder1_h ) )
        self.assertTrue( os.path.exists( tg_folder2_e ) )
        self.assertTrue( os.path.exists( tg_folder2_h ) )

        with mock.patch("input_checked_passphrase.get_checked_passphrase", return_value=(True, self.passphrase + "tampering")):
            r = mass_backup_tester.backups_mass_check(self.test_config_file, self.hash_file)
        self.assertFalse(r)

if __name__ == "__main__":
    unittest.main()
