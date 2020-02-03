#!/usr/bin/env python3

import sys
import os
import shutil
import unittest
from unittest import mock
from unittest.mock import patch

import create_and_write_file
import mvtools_test_fixture

import backup_processor

import hash_check
import decrypt
import generic_run
import path_utils

class BackupProcessorTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("backup_processor_test")
        if not v:
            return v, r
        self.test_base_dir = r[0]
        self.test_dir = r[1]

        # will make the following path the working directory
        self.extracted_folder = os.path.join(self.test_dir, "extracted")
        os.mkdir(self.extracted_folder)
        os.chdir(self.extracted_folder)

        # nonexistent folder - for testing only
        self.nonexistent = os.path.join(self.test_dir, "nonexistent")

        # temp folder
        self.bk_test_temp_folder = os.path.join(self.test_dir, "bktemp")

        # base backup folder
        self.bk_base_folder_test = "BackupTests"

        # create folders, source and target
        self.test_source_folder = os.path.join(self.test_dir, "source_test")
        os.mkdir(self.test_source_folder)
        self.test_source_alt_folder = os.path.join(self.test_dir, "source_alt_test")
        os.mkdir(self.test_source_alt_folder)
        self.test_source_folder_another = os.path.join(self.test_dir, "source_test_another")
        os.mkdir(self.test_source_folder_another)
        self.test_target_1_folder = os.path.join(self.test_dir, "target_1_test")
        os.mkdir(self.test_target_1_folder)
        self.test_target_2_folder = os.path.join(self.test_dir, "target_2_test")
        os.mkdir(self.test_target_2_folder)

        # create test folders
        self.folder1 = os.path.join(self.test_source_folder, "folder1")
        self.folder2 = os.path.join(self.test_source_folder, "folder2")
        self.folder3 = os.path.join(self.test_source_folder, "folder3")
        self.folder4 = os.path.join(self.test_source_folder, ".folder4")
        self.alt_folder5 = os.path.join(self.test_source_alt_folder, "folder5")
        self.alt_folder6 = os.path.join(self.test_source_alt_folder, "folder6")
        self.another_folder7 = os.path.join(self.test_source_folder_another, "folder7")
        os.mkdir(self.folder1)
        os.mkdir(self.folder2)
        os.mkdir(self.folder3)
        os.mkdir(self.folder4)
        os.mkdir(self.alt_folder5)
        os.mkdir(self.alt_folder6)
        os.mkdir(self.another_folder7)

        # file "zero" - at the root of the source dir
        self.file0 = os.path.join(self.test_source_folder, ".file0.txt")
        create_and_write_file.create_file_contents(self.file0, "xyz")

        # create subfolders
        self.folder1_subfolder1 = os.path.join(self.folder1, "subfolder1")
        os.mkdir(self.folder1_subfolder1)
        self.folder1_subfolder2 = os.path.join(self.folder1, "subfolder2")
        os.mkdir(self.folder1_subfolder2)

        # create files, folder1
        self.folder1_file1 = os.path.join(self.folder1, "file1.txt")
        create_and_write_file.create_file_contents(self.folder1_file1, "abc")
        self.folder1_subfolder1_file2 = os.path.join(self.folder1_subfolder1, "file2.txt")
        create_and_write_file.create_file_contents(self.folder1_subfolder1_file2, "abc")
        self.folder1_subfolder2_file3 = os.path.join(self.folder1_subfolder2, "file3.txt")
        create_and_write_file.create_file_contents(self.folder1_subfolder2_file3, "abc")

        # create files, folder2
        self.folder2_file1 = os.path.join(self.folder2, "file1.txt")
        create_and_write_file.create_file_contents(self.folder2_file1, "abc")

        # create files, folder3
        self.folder3_file1 = os.path.join(self.folder3, "file1.txt")
        create_and_write_file.create_file_contents(self.folder3_file1, "abc")

        # create files, folder4
        self.folder4_file1 = os.path.join(self.folder4, "file1.txt")
        create_and_write_file.create_file_contents(self.folder4_file1, "abc")

        # create files alt source folders
        self.alt_folder5_file1 = os.path.join(self.alt_folder5, "file51.txt")
        create_and_write_file.create_file_contents(self.alt_folder5_file1, "abc")
        self.alt_folder6_file1 = os.path.join(self.alt_folder6, "file61.txt")
        create_and_write_file.create_file_contents(self.alt_folder6_file1, "abc")
        self.file01 = os.path.join(self.test_source_alt_folder, ".file01.txt")
        create_and_write_file.create_file_contents(self.file01, "ooo")

        # create files another source folders
        self.file_another = os.path.join(self.another_folder7, "file_another.txt")
        create_and_write_file.create_file_contents(self.file_another, "zzz")

        # create config file
        cfg_file_contents = ""
        #cfg_file_contents += "BKPREPARATION = ...\n"

        # sources
        cfg_file_contents += "BKSOURCE {descend} = \"%s\"\n" % self.test_source_folder
        cfg_file_contents += "BKSOURCE {descend / ex: \"%s\" / ex: \"%s\"} = \"%s\"\n" % (".file01.txt", "folder5", self.test_source_alt_folder)
        cfg_file_contents += "BKSOURCE = \"%s\"\n" % self.test_source_folder_another

        cfg_file_contents += "BKTARGETS_ROOT {nocheckmount} = \"%s\"\n" % self.test_target_1_folder
        cfg_file_contents += "BKTARGETS_ROOT {nocheckmount} = \"%s\"\n" % self.test_target_2_folder
        cfg_file_contents += "BKTEMP = \"%s\"\n" % self.bk_test_temp_folder
        cfg_file_contents += "BKTARGETS_BASEDIR = \"%s\"\n" % self.bk_base_folder_test

        self.test_config_file = os.path.join(self.test_dir, "test_config_file.cfg")
        create_and_write_file.create_file_contents(self.test_config_file, cfg_file_contents)

        # hash file
        self.hash_file = os.path.join(self.test_dir, ".hash_file_test")
        self.passphrase = "abcdef"
        create_and_write_file.create_file_contents(self.hash_file, "e32ef19623e8ed9d267f657a81944b3d07adbb768518068e88435745564e8d4150a0a703be2a7d88b61e3d390c2bb97e2d4c311fdc69d6b1267f05f59aa920e7")

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testArtifactBase1(self):
        artbase = backup_processor.ArtifactBase(self.test_source_folder, [self.folder2], True)
        self.assertTrue(artbase.get_path(), self.test_source_folder)
        self.assertTrue(artbase.get_list_exceptions(), [self.folder2])
        self.assertTrue(artbase.validate_exceptions(), (True, ""))

    def testArtifactBase2(self):
        artbase = backup_processor.ArtifactBase(self.test_source_folder, [self.nonexistent], True)
        self.assertTrue(artbase.get_path(), self.test_source_folder)
        self.assertTrue(artbase.get_list_exceptions(), [self.nonexistent])
        r = artbase.validate_exceptions()
        self.assertFalse(r[0])

    def testMakeBackupArtifactsList1(self):
        artbase = backup_processor.ArtifactBase(self.test_source_folder, [self.folder2], True)
        res = backup_processor.make_backup_artifacts_list([artbase])
        self.assertTrue(self.folder1 in res)
        self.assertFalse(self.folder2 in res)
        self.assertTrue(self.folder3 in res)

    def testMakeBackupArtifactsList2(self):
        artbase = backup_processor.ArtifactBase(self.test_source_folder, [], False)
        res = backup_processor.make_backup_artifacts_list([artbase])
        self.assertTrue(self.test_source_folder in res)
        self.assertFalse(self.folder1 in res)
        self.assertFalse(self.folder2 in res)
        self.assertFalse(self.folder3 in res)

    def testReadConfig(self):
        v, r = backup_processor.read_config(self.test_config_file)
        self.assertTrue(v)
        self.assertEqual(r[0], "")
        self.assertEqual(r[2], [self.test_target_1_folder, self.test_target_2_folder])
        self.assertEqual(r[3], self.bk_base_folder_test)
        self.assertEqual(r[4], self.bk_test_temp_folder)

    def testRunBackup1(self):

        # basic execution
        with mock.patch("input_checked_passphrase.get_checked_passphrase", return_value=(True, self.passphrase)):
            r = backup_processor.run_backup(self.test_config_file, self.hash_file)
        self.assertTrue(r)

        tg1_final = os.path.join(self.test_target_1_folder, self.bk_base_folder_test)
        tg2_final = os.path.join(self.test_target_2_folder, self.bk_base_folder_test)

        # check if dates were written in both targets
        self.assertTrue( os.path.exists( os.path.join(tg1_final, "bk_date.txt") ) )
        self.assertTrue( os.path.exists( os.path.join(tg2_final, "bk_date.txt") ) )

        # check if all artifacts are present on both targets

        # target 1
        tg1_folder1_e = os.path.join(tg1_final, "source_test", "folder1.tar.bz2.enc")
        tg1_folder1_z = os.path.join(tg1_final, "source_test", "folder1.tar.bz2")
        tg1_folder1_h = os.path.join(tg1_final, "source_test", "folder1.tar.bz2.enc.sha256")
        tg1_folder2_e = os.path.join(tg1_final, "source_test", "folder2.tar.bz2.enc")
        tg1_folder2_z = os.path.join(tg1_final, "source_test", "folder2.tar.bz2")
        tg1_folder2_h = os.path.join(tg1_final, "source_test", "folder2.tar.bz2.enc.sha256")
        tg1_folder3_e = os.path.join(tg1_final, "source_test", "folder3.tar.bz2.enc")
        tg1_folder3_z = os.path.join(tg1_final, "source_test", "folder3.tar.bz2")
        tg1_folder3_h = os.path.join(tg1_final, "source_test", "folder3.tar.bz2.enc.sha256")
        tg1_folder4_e = os.path.join(tg1_final, "source_test", ".folder4.tar.bz2.enc")
        tg1_folder4_z = os.path.join(tg1_final, "source_test", ".folder4.tar.bz2")
        tg1_folder4_h = os.path.join(tg1_final, "source_test", ".folder4.tar.bz2.enc.sha256")
        tg1_file0_e = os.path.join(tg1_final, "source_test", ".file0.txt.tar.bz2.enc")
        tg1_file0_z = os.path.join(tg1_final, "source_test", ".file0.txt.tar.bz2")
        tg1_file0_h = os.path.join(tg1_final, "source_test", ".file0.txt.tar.bz2.enc.sha256")

        # target 2
        tg2_folder1_e = os.path.join(tg2_final, "source_test", "folder1.tar.bz2.enc")
        tg2_folder1_z = os.path.join(tg2_final, "source_test", "folder1.tar.bz2")
        tg2_folder1_h = os.path.join(tg2_final, "source_test", "folder1.tar.bz2.enc.sha256")
        tg2_folder2_e = os.path.join(tg2_final, "source_test", "folder2.tar.bz2.enc")
        tg2_folder2_z = os.path.join(tg2_final, "source_test", "folder2.tar.bz2")
        tg2_folder2_h = os.path.join(tg2_final, "source_test", "folder2.tar.bz2.enc.sha256")
        tg2_folder3_e = os.path.join(tg2_final, "source_test", "folder3.tar.bz2.enc")
        tg2_folder3_z = os.path.join(tg2_final, "source_test", "folder3.tar.bz2")
        tg2_folder3_h = os.path.join(tg2_final, "source_test", "folder3.tar.bz2.enc.sha256")
        tg2_folder4_e = os.path.join(tg2_final, "source_test", ".folder4.tar.bz2.enc")
        tg2_folder4_z = os.path.join(tg2_final, "source_test", ".folder4.tar.bz2")
        tg2_folder4_h = os.path.join(tg2_final, "source_test", ".folder4.tar.bz2.enc.sha256")
        tg2_file0_e = os.path.join(tg2_final, "source_test", ".file0.txt.tar.bz2.enc")
        tg2_file0_z = os.path.join(tg2_final, "source_test", ".file0.txt.tar.bz2")
        tg2_file0_h = os.path.join(tg2_final, "source_test", ".file0.txt.tar.bz2.enc.sha256")

        # target1
        self.assertTrue( os.path.exists( tg1_folder1_e ) )
        self.assertTrue( os.path.exists( tg1_folder1_h ) )
        self.assertTrue( os.path.exists( tg1_folder2_e ) )
        self.assertTrue( os.path.exists( tg1_folder2_h ) )
        self.assertTrue( os.path.exists( tg1_folder3_e ) )
        self.assertTrue( os.path.exists( tg1_folder3_h ) )
        self.assertTrue( os.path.exists( tg1_folder4_e ) )
        self.assertTrue( os.path.exists( tg1_folder4_h ) )
        self.assertTrue( os.path.exists( tg1_file0_e ) )
        self.assertTrue( os.path.exists( tg1_file0_h ) )

        # target2
        self.assertTrue( os.path.exists( tg2_folder1_e ) )
        self.assertTrue( os.path.exists( tg2_folder1_h ) )
        self.assertTrue( os.path.exists( tg2_folder2_e ) )
        self.assertTrue( os.path.exists( tg2_folder2_h ) )
        self.assertTrue( os.path.exists( tg2_folder3_e ) )
        self.assertTrue( os.path.exists( tg2_folder3_h ) )
        self.assertTrue( os.path.exists( tg2_folder4_e ) )
        self.assertTrue( os.path.exists( tg2_folder4_h ) )
        self.assertTrue( os.path.exists( tg2_file0_e ) )
        self.assertTrue( os.path.exists( tg2_file0_h ) )

        # check hashes
        # target 1
        self.assertTrue(hash_check.sha256sum_check( tg1_folder1_e, tg1_folder1_h ))
        self.assertTrue(hash_check.sha256sum_check( tg1_folder2_e, tg1_folder2_h ))
        self.assertTrue(hash_check.sha256sum_check( tg1_folder3_e, tg1_folder3_h ))
        self.assertTrue(hash_check.sha256sum_check( tg1_folder4_e, tg1_folder4_h ))
        self.assertTrue(hash_check.sha256sum_check( tg1_file0_e, tg1_file0_h ))

        # target 2
        self.assertTrue(hash_check.sha256sum_check( tg2_folder1_e, tg2_folder1_h ))
        self.assertTrue(hash_check.sha256sum_check( tg2_folder2_e, tg2_folder2_h ))
        self.assertTrue(hash_check.sha256sum_check( tg2_folder3_e, tg2_folder3_h ))
        self.assertTrue(hash_check.sha256sum_check( tg2_folder4_e, tg2_folder4_h ))
        self.assertTrue(hash_check.sha256sum_check( tg2_file0_e, tg2_file0_h ))

        # decrypt files
        # target 1
        self.assertTrue(decrypt.symmetric_decrypt( tg1_folder1_e, tg1_folder1_z, self.passphrase ))
        self.assertTrue(decrypt.symmetric_decrypt( tg1_folder2_e, tg1_folder2_z, self.passphrase ))
        self.assertTrue(decrypt.symmetric_decrypt( tg1_folder3_e, tg1_folder3_z, self.passphrase ))
        self.assertTrue(decrypt.symmetric_decrypt( tg1_folder4_e, tg1_folder4_z, self.passphrase ))
        self.assertTrue(decrypt.symmetric_decrypt( tg1_file0_e, tg1_file0_z, self.passphrase ))

        # target 2
        self.assertTrue(decrypt.symmetric_decrypt( tg2_folder1_e, tg2_folder1_z, self.passphrase ))
        self.assertTrue(decrypt.symmetric_decrypt( tg2_folder2_e, tg2_folder2_z, self.passphrase ))
        self.assertTrue(decrypt.symmetric_decrypt( tg2_folder3_e, tg2_folder3_z, self.passphrase ))
        self.assertTrue(decrypt.symmetric_decrypt( tg2_folder4_e, tg2_folder4_z, self.passphrase ))
        self.assertTrue(decrypt.symmetric_decrypt( tg2_file0_e, tg2_file0_z, self.passphrase ))

        # extract files and check contents
        # target 1
        generic_run.run_cmd("tar -xf %s" % tg1_folder1_z )
        generic_run.run_cmd("tar -xf %s" % tg1_folder2_z )
        generic_run.run_cmd("tar -xf %s" % tg1_folder3_z )
        generic_run.run_cmd("tar -xf %s" % tg1_folder4_z )
        generic_run.run_cmd("tar -xf %s" % tg1_file0_z )

        self.assertTrue( os.path.exists( os.path.join( self.extracted_folder, self.folder1_file1) ) )
        self.assertTrue( os.path.exists( os.path.join( self.extracted_folder, self.folder1_subfolder1_file2) ) )
        self.assertTrue( os.path.exists( os.path.join( self.extracted_folder, self.folder1_subfolder2_file3) ) )
        self.assertTrue( os.path.exists( os.path.join( self.extracted_folder, self.folder2_file1) ) )
        self.assertTrue( os.path.exists( os.path.join( self.extracted_folder, self.folder3_file1) ) )
        self.assertTrue( os.path.exists( os.path.join( self.extracted_folder, self.folder4_file1) ) )
        self.assertTrue( os.path.exists( os.path.join( self.extracted_folder, self.file0) ) )

        # reset extracted folder
        homedir = os.path.expanduser("~/")
        os.chdir(homedir)
        path_utils.scratchfolder(self.extracted_folder)
        os.chdir(self.extracted_folder)

        # target 2
        generic_run.run_cmd("tar -xf %s" % tg2_folder1_z )
        generic_run.run_cmd("tar -xf %s" % tg2_folder2_z )
        generic_run.run_cmd("tar -xf %s" % tg2_folder3_z )
        generic_run.run_cmd("tar -xf %s" % tg2_folder4_z )
        generic_run.run_cmd("tar -xf %s" % tg2_file0_z )

        self.assertTrue( os.path.exists( os.path.join( self.extracted_folder, self.folder1_file1) ) )
        self.assertTrue( os.path.exists( os.path.join( self.extracted_folder, self.folder1_subfolder1_file2) ) )
        self.assertTrue( os.path.exists( os.path.join( self.extracted_folder, self.folder1_subfolder2_file3) ) )
        self.assertTrue( os.path.exists( os.path.join( self.extracted_folder, self.folder2_file1) ) )
        self.assertTrue( os.path.exists( os.path.join( self.extracted_folder, self.folder3_file1) ) )
        self.assertTrue( os.path.exists( os.path.join( self.extracted_folder, self.folder4_file1) ) )
        self.assertTrue( os.path.exists( os.path.join( self.extracted_folder, self.file0) ) )

    def testRunBackup2(self):

        # basic execution
        with mock.patch("input_checked_passphrase.get_checked_passphrase", return_value=(True, self.passphrase)):
            r = backup_processor.run_backup(self.test_config_file, self.hash_file)
        self.assertTrue(r)

        tg1_final = os.path.join(self.test_target_1_folder, self.bk_base_folder_test)
        tg2_final = os.path.join(self.test_target_2_folder, self.bk_base_folder_test)

        # check if dates were written in both targets
        self.assertTrue( os.path.exists( os.path.join(tg1_final, "bk_date.txt") ) )
        self.assertTrue( os.path.exists( os.path.join(tg2_final, "bk_date.txt") ) )

        # target 1
        # alt source
        tg1_folder5 = os.path.join(tg1_final, "source_alt_test", "folder5.tar.bz2.enc")
        tg1_folder6 = os.path.join(tg1_final, "source_alt_test", "folder6.tar.bz2.enc")
        tg1_file01 = os.path.join(tg1_final, "source_alt_test", ".file01.txt.tar.bz2.enc")

        # another source
        tg1_folder_another_e = os.path.join(tg1_final, "backup_processor_test", "source_test_another.tar.bz2.enc")
        tg1_folder_another_z = os.path.join(tg1_final, "backup_processor_test", "source_test_another.tar.bz2")
        tg1_folder_another_h = os.path.join(tg1_final, "backup_processor_test", "source_test_another.tar.bz2.enc.sha256")
        tg1_folder7_e = os.path.join(tg1_final, "backup_processor_test", "source_test_another", "folder7.tar.bz2.enc")
        tg1_folder7_z = os.path.join(tg1_final, "backup_processor_test", "source_test_another", "folder7.tar.bz2")
        tg1_folder7_h = os.path.join(tg1_final, "backup_processor_test", "source_test_another", "folder7.tar.bz2.enc.sha256")

        # target 2
        # alt source
        tg2_folder5 = os.path.join(tg2_final, "source_alt_test", "folder5.tar.bz2.enc")
        tg2_folder6 = os.path.join(tg2_final, "source_alt_test", "folder6.tar.bz2.enc")
        tg2_file01 = os.path.join(tg2_final, "source_alt_test", ".file01.txt.tar.bz2.enc")

        # another source
        tg2_folder_another_e = os.path.join(tg2_final, "backup_processor_test", "source_test_another.tar.bz2.enc")
        tg2_folder_another_z = os.path.join(tg2_final, "backup_processor_test", "source_test_another.tar.bz2")
        tg2_folder_another_h = os.path.join(tg2_final, "backup_processor_test", "source_test_another.tar.bz2.enc.sha256")
        tg2_folder7_e = os.path.join(tg2_final, "backup_processor_test", "source_test_another", "folder7.tar.bz2.enc")
        tg2_folder7_z = os.path.join(tg2_final, "backup_processor_test", "source_test_another", "folder7.tar.bz2")
        tg2_folder7_h = os.path.join(tg2_final, "backup_processor_test", "source_test_another", "folder7.tar.bz2.enc.sha256")

        # target 1
        self.assertFalse( os.path.exists( tg1_folder5 ) )
        self.assertTrue( os.path.exists( tg1_folder6 ) )
        self.assertFalse( os.path.exists( tg1_file01 ) )
        self.assertTrue( os.path.exists( tg1_folder_another_e ) )
        self.assertTrue( os.path.exists( tg1_folder_another_h ) )
        self.assertFalse( os.path.exists( tg1_folder7_e ) )
        self.assertFalse( os.path.exists( tg1_folder7_h ) )

        self.assertTrue(hash_check.sha256sum_check( tg1_folder_another_e, tg1_folder_another_h ))

        self.assertTrue(decrypt.symmetric_decrypt( tg1_folder_another_e, tg1_folder_another_z, self.passphrase ))

        generic_run.run_cmd("tar -xf %s" % tg1_folder_another_z )

        self.assertTrue( os.path.exists( os.path.join( self.extracted_folder, self.another_folder7 ) ) )
        self.assertTrue( os.path.exists( os.path.join( self.extracted_folder, self.file_another ) ) )

        # reset extracted folder
        homedir = os.path.expanduser("~/")
        os.chdir(homedir)
        path_utils.scratchfolder(self.extracted_folder)
        os.chdir(self.extracted_folder)

        # target 2
        self.assertFalse( os.path.exists( tg2_folder5 ) )
        self.assertTrue( os.path.exists( tg2_folder6 ) )
        self.assertFalse( os.path.exists( tg2_file01 ) )
        self.assertTrue( os.path.exists( tg2_folder_another_e ) )
        self.assertTrue( os.path.exists( tg2_folder_another_h ) )
        self.assertFalse( os.path.exists( tg2_folder7_e ) )
        self.assertFalse( os.path.exists( tg2_folder7_h ) )

        self.assertTrue(hash_check.sha256sum_check( tg2_folder_another_e, tg2_folder_another_h ))

        self.assertTrue(decrypt.symmetric_decrypt( tg2_folder_another_e, tg2_folder_another_z, self.passphrase ))

        generic_run.run_cmd("tar -xf %s" % tg2_folder_another_z )

        self.assertTrue( os.path.exists( os.path.join( self.extracted_folder, self.another_folder7 ) ) )
        self.assertTrue( os.path.exists( os.path.join( self.extracted_folder, self.file_another ) ) )

if __name__ == '__main__':
    unittest.main()
