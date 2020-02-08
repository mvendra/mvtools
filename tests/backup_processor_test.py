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
import tar_wrapper
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

        # folder where extracted stuff will be stored at
        self.extracted_folder = os.path.join(self.test_dir, path_utils.filter_join_abs("extracted"))
        path_utils.scratchfolder(self.extracted_folder)

        # nonexistent folder - for testing only
        self.nonexistent = os.path.join(self.test_dir, path_utils.filter_join_abs("nonexistent"))

        # temp folder
        self.bk_test_temp_folder = os.path.join(self.test_dir, path_utils.filter_join_abs("bktemp"))

        # base backup folder
        self.bk_base_folder_test = "BackupTests"

        # create folders, source and target
        self.test_source_folder = os.path.join(self.test_dir, path_utils.filter_join_abs("source_test"))
        os.mkdir(self.test_source_folder)
        self.test_source_alt_folder = os.path.join(self.test_dir, path_utils.filter_join_abs("source_alt_test"))
        os.mkdir(self.test_source_alt_folder)
        self.test_source_folder_another = os.path.join(self.test_dir, path_utils.filter_join_abs("source_test_another"))
        os.mkdir(self.test_source_folder_another)
        self.test_target_1_folder = os.path.join(self.test_dir, path_utils.filter_join_abs("target_1_test"))
        os.mkdir(self.test_target_1_folder)
        self.test_target_2_folder = os.path.join(self.test_dir, path_utils.filter_join_abs("target_2_test"))
        os.mkdir(self.test_target_2_folder)

        # create test folders
        self.folder1 = os.path.join(self.test_source_folder, path_utils.filter_join_abs("folder1"))
        self.folder2 = os.path.join(self.test_source_folder, path_utils.filter_join_abs("folder2"))
        self.folder3 = os.path.join(self.test_source_folder, path_utils.filter_join_abs("folder3"))
        self.folder4 = os.path.join(self.test_source_folder, path_utils.filter_join_abs(".folder4"))
        self.alt_folder5 = os.path.join(self.test_source_alt_folder, path_utils.filter_join_abs("folder5"))
        self.alt_folder6 = os.path.join(self.test_source_alt_folder, path_utils.filter_join_abs("folder6"))
        self.another_folder7 = os.path.join(self.test_source_folder_another, path_utils.filter_join_abs("folder7"))
        os.mkdir(self.folder1)
        os.mkdir(self.folder2)
        os.mkdir(self.folder3)
        os.mkdir(self.folder4)
        os.mkdir(self.alt_folder5)
        os.mkdir(self.alt_folder6)
        os.mkdir(self.another_folder7)

        # file "zero" - at the root of the source dir
        self.file0 = os.path.join(self.test_source_folder, path_utils.filter_join_abs(".file0.txt"))
        create_and_write_file.create_file_contents(self.file0, "xyz")

        # create subfolders
        self.folder1_subfolder1 = os.path.join(self.folder1, path_utils.filter_join_abs("subfolder1"))
        os.mkdir(self.folder1_subfolder1)
        self.folder1_subfolder2 = os.path.join(self.folder1, path_utils.filter_join_abs("subfolder2"))
        os.mkdir(self.folder1_subfolder2)

        # create files, folder1
        self.folder1_file1 = os.path.join(self.folder1, path_utils.filter_join_abs("file1.txt"))
        create_and_write_file.create_file_contents(self.folder1_file1, "abc")
        self.folder1_subfolder1_file2 = os.path.join(self.folder1_subfolder1, path_utils.filter_join_abs("file2.txt"))
        create_and_write_file.create_file_contents(self.folder1_subfolder1_file2, "abc")
        self.folder1_subfolder2_file3 = os.path.join(self.folder1_subfolder2, path_utils.filter_join_abs("file3.txt"))
        create_and_write_file.create_file_contents(self.folder1_subfolder2_file3, "abc")

        # create files, folder2
        self.folder2_file1 = os.path.join(self.folder2, path_utils.filter_join_abs("file1.txt"))
        create_and_write_file.create_file_contents(self.folder2_file1, "abc")

        # create files, folder3
        self.folder3_file1 = os.path.join(self.folder3, path_utils.filter_join_abs("file1.txt"))
        create_and_write_file.create_file_contents(self.folder3_file1, "abc")

        # create files, folder4
        self.folder4_file1 = os.path.join(self.folder4, path_utils.filter_join_abs("file1.txt"))
        create_and_write_file.create_file_contents(self.folder4_file1, "abc")

        # create files alt source folders
        self.alt_folder5_file1 = os.path.join(self.alt_folder5, path_utils.filter_join_abs("file51.txt"))
        create_and_write_file.create_file_contents(self.alt_folder5_file1, "abc")
        self.alt_folder6_file1 = os.path.join(self.alt_folder6, path_utils.filter_join_abs("file61.txt"))
        create_and_write_file.create_file_contents(self.alt_folder6_file1, "abc")
        self.file01 = os.path.join(self.test_source_alt_folder, path_utils.filter_join_abs(".file01.txt"))
        create_and_write_file.create_file_contents(self.file01, "ooo")

        # create files another source folders
        self.file_another = os.path.join(self.another_folder7, path_utils.filter_join_abs("file_another.txt"))
        create_and_write_file.create_file_contents(self.file_another, "zzz")

        # sources with spaces
        self.special_folder = os.path.join(self.test_source_folder, path_utils.filter_join_abs("special_folder"))
        os.mkdir(self.special_folder)

        self.space_file1 = os.path.join(self.special_folder, path_utils.filter_join_abs("   sp_file1.txt"))
        self.space_file2 = os.path.join(self.special_folder, path_utils.filter_join_abs("sp_fi  le2.txt"))
        self.space_file3 = os.path.join(self.special_folder, path_utils.filter_join_abs("sp_file3.txt  "))
        create_and_write_file.create_file_contents(self.space_file1, "eee1")
        create_and_write_file.create_file_contents(self.space_file2, "eee2")
        create_and_write_file.create_file_contents(self.space_file3, "eee3")

        self.space_folder1 = os.path.join(self.special_folder, path_utils.filter_join_abs("   sp_folder1"))
        self.space_folder2 = os.path.join(self.special_folder, path_utils.filter_join_abs("sp_fol   der2"))
        self.space_folder3 = os.path.join(self.special_folder, path_utils.filter_join_abs("sp_folder3   "))
        os.mkdir(self.space_folder1)
        os.mkdir(self.space_folder2)
        os.mkdir(self.space_folder3)

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

        self.test_config_file = os.path.join(self.test_dir, path_utils.filter_join_abs("test_config_file.cfg"))
        create_and_write_file.create_file_contents(self.test_config_file, cfg_file_contents)

        # hash file
        self.hash_file = os.path.join(self.test_dir, path_utils.filter_join_abs(".hash_file_test"))
        self.passphrase = "abcdef"
        create_and_write_file.create_file_contents(self.hash_file, "e32ef19623e8ed9d267f657a81944b3d07adbb768518068e88435745564e8d4150a0a703be2a7d88b61e3d390c2bb97e2d4c311fdc69d6b1267f05f59aa920e7")

        # special source
        special_cfg_file_contents1 = ""
        special_cfg_file_contents1 += "BKSOURCE = \"%s\"\n" % self.space_file1
        special_cfg_file_contents1 += "BKSOURCE = \"%s\"\n" % self.space_file2
        special_cfg_file_contents1 += "BKSOURCE = \"%s\"\n" % self.space_file3

        special_cfg_file_contents1 += "BKSOURCE = \"%s\"\n" % self.space_folder1
        special_cfg_file_contents1 += "BKSOURCE = \"%s\"\n" % self.space_folder2
        special_cfg_file_contents1 += "BKSOURCE = \"%s\"\n" % self.space_folder3

        special_cfg_file_contents1 += "BKTARGETS_ROOT {nocheckmount} = \"%s\"\n" % self.test_target_1_folder
        special_cfg_file_contents1 += "BKTARGETS_ROOT {nocheckmount} = \"%s\"\n" % self.test_target_2_folder

        special_cfg_file_contents1 += "BKTEMP = \"%s\"\n" % self.bk_test_temp_folder
        special_cfg_file_contents1 += "BKTARGETS_BASEDIR = \"%s\"\n" % self.bk_base_folder_test

        self.test_special_config_file = os.path.join(self.test_dir, path_utils.filter_join_abs("test_special_config_file.cfg"))
        create_and_write_file.create_file_contents(self.test_special_config_file, special_cfg_file_contents1)

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

        tg1_final = os.path.join(self.test_target_1_folder, path_utils.filter_join_abs(self.bk_base_folder_test))
        tg2_final = os.path.join(self.test_target_2_folder, path_utils.filter_join_abs(self.bk_base_folder_test))

        # check if dates were written in both targets
        self.assertTrue( os.path.exists( os.path.join(tg1_final, path_utils.filter_join_abs("bk_date.txt")) ) )
        self.assertTrue( os.path.exists( os.path.join(tg2_final, path_utils.filter_join_abs("bk_date.txt")) ) )

        # check if all artifacts are present on both targets

        # target 1
        tg1_folder1_e = os.path.join(tg1_final, path_utils.filter_join_abs("source_test"), path_utils.filter_join_abs("folder1.tar.bz2.enc"))
        tg1_folder1_z = os.path.join(tg1_final, path_utils.filter_join_abs("source_test"), path_utils.filter_join_abs("folder1.tar.bz2"))
        tg1_folder1_h = os.path.join(tg1_final, path_utils.filter_join_abs("source_test"), path_utils.filter_join_abs("folder1.tar.bz2.enc.sha256"))
        tg1_folder2_e = os.path.join(tg1_final, path_utils.filter_join_abs("source_test"), path_utils.filter_join_abs("folder2.tar.bz2.enc"))
        tg1_folder2_z = os.path.join(tg1_final, path_utils.filter_join_abs("source_test"), path_utils.filter_join_abs("folder2.tar.bz2"))
        tg1_folder2_h = os.path.join(tg1_final, path_utils.filter_join_abs("source_test"), path_utils.filter_join_abs("folder2.tar.bz2.enc.sha256"))
        tg1_folder3_e = os.path.join(tg1_final, path_utils.filter_join_abs("source_test"), path_utils.filter_join_abs("folder3.tar.bz2.enc"))
        tg1_folder3_z = os.path.join(tg1_final, path_utils.filter_join_abs("source_test"), path_utils.filter_join_abs("folder3.tar.bz2"))
        tg1_folder3_h = os.path.join(tg1_final, path_utils.filter_join_abs("source_test"), path_utils.filter_join_abs("folder3.tar.bz2.enc.sha256"))
        tg1_folder4_e = os.path.join(tg1_final, path_utils.filter_join_abs("source_test"), path_utils.filter_join_abs(".folder4.tar.bz2.enc"))
        tg1_folder4_z = os.path.join(tg1_final, path_utils.filter_join_abs("source_test"), path_utils.filter_join_abs(".folder4.tar.bz2"))
        tg1_folder4_h = os.path.join(tg1_final, path_utils.filter_join_abs("source_test"), path_utils.filter_join_abs(".folder4.tar.bz2.enc.sha256"))
        tg1_file0_e = os.path.join(tg1_final, path_utils.filter_join_abs("source_test"), path_utils.filter_join_abs(".file0.txt.tar.bz2.enc"))
        tg1_file0_z = os.path.join(tg1_final, path_utils.filter_join_abs("source_test"), path_utils.filter_join_abs(".file0.txt.tar.bz2"))
        tg1_file0_h = os.path.join(tg1_final, path_utils.filter_join_abs("source_test"), path_utils.filter_join_abs(".file0.txt.tar.bz2.enc.sha256"))

        # target 2
        tg2_folder1_e = os.path.join(tg2_final, path_utils.filter_join_abs("source_test"), path_utils.filter_join_abs("folder1.tar.bz2.enc"))
        tg2_folder1_z = os.path.join(tg2_final, path_utils.filter_join_abs("source_test"), path_utils.filter_join_abs("folder1.tar.bz2"))
        tg2_folder1_h = os.path.join(tg2_final, path_utils.filter_join_abs("source_test"), path_utils.filter_join_abs("folder1.tar.bz2.enc.sha256"))
        tg2_folder2_e = os.path.join(tg2_final, path_utils.filter_join_abs("source_test"), path_utils.filter_join_abs("folder2.tar.bz2.enc"))
        tg2_folder2_z = os.path.join(tg2_final, path_utils.filter_join_abs("source_test"), path_utils.filter_join_abs("folder2.tar.bz2"))
        tg2_folder2_h = os.path.join(tg2_final, path_utils.filter_join_abs("source_test"), path_utils.filter_join_abs("folder2.tar.bz2.enc.sha256"))
        tg2_folder3_e = os.path.join(tg2_final, path_utils.filter_join_abs("source_test"), path_utils.filter_join_abs("folder3.tar.bz2.enc"))
        tg2_folder3_z = os.path.join(tg2_final, path_utils.filter_join_abs("source_test"), path_utils.filter_join_abs("folder3.tar.bz2"))
        tg2_folder3_h = os.path.join(tg2_final, path_utils.filter_join_abs("source_test"), path_utils.filter_join_abs("folder3.tar.bz2.enc.sha256"))
        tg2_folder4_e = os.path.join(tg2_final, path_utils.filter_join_abs("source_test"), path_utils.filter_join_abs(".folder4.tar.bz2.enc"))
        tg2_folder4_z = os.path.join(tg2_final, path_utils.filter_join_abs("source_test"), path_utils.filter_join_abs(".folder4.tar.bz2"))
        tg2_folder4_h = os.path.join(tg2_final, path_utils.filter_join_abs("source_test"), path_utils.filter_join_abs(".folder4.tar.bz2.enc.sha256"))
        tg2_file0_e = os.path.join(tg2_final, path_utils.filter_join_abs("source_test"), path_utils.filter_join_abs(".file0.txt.tar.bz2.enc"))
        tg2_file0_z = os.path.join(tg2_final, path_utils.filter_join_abs("source_test"), path_utils.filter_join_abs(".file0.txt.tar.bz2"))
        tg2_file0_h = os.path.join(tg2_final, path_utils.filter_join_abs("source_test"), path_utils.filter_join_abs(".file0.txt.tar.bz2.enc.sha256"))

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
        v, r = tar_wrapper.extract(tg1_folder1_z, self.extracted_folder)
        self.assertTrue(v)
        v, r = tar_wrapper.extract(tg1_folder2_z, self.extracted_folder)
        self.assertTrue(v)
        v, r = tar_wrapper.extract(tg1_folder3_z, self.extracted_folder)
        self.assertTrue(v)
        v, r = tar_wrapper.extract(tg1_folder4_z, self.extracted_folder)
        self.assertTrue(v)
        v, r = tar_wrapper.extract(tg1_file0_z, self.extracted_folder)
        self.assertTrue(v)

        self.assertTrue( os.path.exists( os.path.join( self.extracted_folder, path_utils.filter_join_abs(self.folder1_file1) ) ) )
        self.assertTrue( os.path.exists( os.path.join( self.extracted_folder, path_utils.filter_join_abs(self.folder1_subfolder1_file2) ) ) )
        self.assertTrue( os.path.exists( os.path.join( self.extracted_folder, path_utils.filter_join_abs(self.folder1_subfolder2_file3) ) ) )
        self.assertTrue( os.path.exists( os.path.join( self.extracted_folder, path_utils.filter_join_abs(self.folder2_file1) ) ) )
        self.assertTrue( os.path.exists( os.path.join( self.extracted_folder, path_utils.filter_join_abs(self.folder3_file1) ) ) )
        self.assertTrue( os.path.exists( os.path.join( self.extracted_folder, path_utils.filter_join_abs(self.folder4_file1) ) ) )
        self.assertTrue( os.path.exists( os.path.join( self.extracted_folder, path_utils.filter_join_abs(self.file0) ) ) )

        # reset extracted folder
        path_utils.scratchfolder(self.extracted_folder)

        # target 2
        v, r = tar_wrapper.extract(tg2_folder1_z, self.extracted_folder)
        self.assertTrue(v)
        v, r = tar_wrapper.extract(tg2_folder2_z, self.extracted_folder)
        self.assertTrue(v)
        v, r = tar_wrapper.extract(tg2_folder3_z, self.extracted_folder)
        self.assertTrue(v)
        v, r = tar_wrapper.extract(tg2_folder4_z, self.extracted_folder)
        self.assertTrue(v)
        v, r = tar_wrapper.extract(tg2_file0_z, self.extracted_folder)
        self.assertTrue(v)

        self.assertTrue( os.path.exists( os.path.join( self.extracted_folder, path_utils.filter_join_abs(self.folder1_file1) ) ) )
        self.assertTrue( os.path.exists( os.path.join( self.extracted_folder, path_utils.filter_join_abs(self.folder1_subfolder1_file2) ) ) )
        self.assertTrue( os.path.exists( os.path.join( self.extracted_folder, path_utils.filter_join_abs(self.folder2_file1) ) ) )
        self.assertTrue( os.path.exists( os.path.join( self.extracted_folder, path_utils.filter_join_abs(self.folder1_subfolder2_file3) ) ) )
        self.assertTrue( os.path.exists( os.path.join( self.extracted_folder, path_utils.filter_join_abs(self.folder3_file1) ) ) )
        self.assertTrue( os.path.exists( os.path.join( self.extracted_folder, path_utils.filter_join_abs(self.folder4_file1) ) ) )
        self.assertTrue( os.path.exists( os.path.join( self.extracted_folder, path_utils.filter_join_abs(self.file0) ) ) )

    def testRunBackup2(self):

        # basic execution
        with mock.patch("input_checked_passphrase.get_checked_passphrase", return_value=(True, self.passphrase)):
            r = backup_processor.run_backup(self.test_config_file, self.hash_file)
        self.assertTrue(r)

        tg1_final = os.path.join(self.test_target_1_folder, path_utils.filter_join_abs(self.bk_base_folder_test) )
        tg2_final = os.path.join(self.test_target_2_folder, path_utils.filter_join_abs(self.bk_base_folder_test) )

        # check if dates were written in both targets
        self.assertTrue( os.path.exists( os.path.join(tg1_final, path_utils.filter_join_abs("bk_date.txt") ) ) )
        self.assertTrue( os.path.exists( os.path.join(tg2_final, path_utils.filter_join_abs("bk_date.txt") ) ) )

        # target 1
        # alt source
        tg1_folder5 = os.path.join(tg1_final, path_utils.filter_join_abs("source_alt_test"), path_utils.filter_join_abs("folder5.tar.bz2.enc") )
        tg1_folder6 = os.path.join(tg1_final, path_utils.filter_join_abs("source_alt_test"), path_utils.filter_join_abs("folder6.tar.bz2.enc") )
        tg1_file01 = os.path.join(tg1_final, path_utils.filter_join_abs("source_alt_test"), path_utils.filter_join_abs(".file01.txt.tar.bz2.enc") )

        # another source
        tg1_folder_another_e = os.path.join(tg1_final, path_utils.filter_join_abs("backup_processor_test"), path_utils.filter_join_abs("source_test_another.tar.bz2.enc") )
        tg1_folder_another_z = os.path.join(tg1_final, path_utils.filter_join_abs("backup_processor_test"), path_utils.filter_join_abs("source_test_another.tar.bz2") )
        tg1_folder_another_h = os.path.join(tg1_final, path_utils.filter_join_abs("backup_processor_test"), path_utils.filter_join_abs("source_test_another.tar.bz2.enc.sha256") )
        tg1_folder7_e = os.path.join(tg1_final, path_utils.filter_join_abs("backup_processor_test"), path_utils.filter_join_abs("source_test_another"), path_utils.filter_join_abs("folder7.tar.bz2.enc") )
        tg1_folder7_z = os.path.join(tg1_final, path_utils.filter_join_abs("backup_processor_test"), path_utils.filter_join_abs("source_test_another"), path_utils.filter_join_abs("folder7.tar.bz2") )
        tg1_folder7_h = os.path.join(tg1_final, path_utils.filter_join_abs("backup_processor_test"), path_utils.filter_join_abs("source_test_another"), path_utils.filter_join_abs("folder7.tar.bz2.enc.sha256") )

        # target 2
        # alt source
        tg2_folder5 = os.path.join(tg2_final, path_utils.filter_join_abs("source_alt_test"), path_utils.filter_join_abs("folder5.tar.bz2.enc") )
        tg2_folder6 = os.path.join(tg2_final, path_utils.filter_join_abs("source_alt_test"), path_utils.filter_join_abs("folder6.tar.bz2.enc") )
        tg2_file01 = os.path.join(tg2_final, path_utils.filter_join_abs("source_alt_test"), path_utils.filter_join_abs(".file01.txt.tar.bz2.enc") )

        # another source
        tg2_folder_another_e = os.path.join(tg2_final, path_utils.filter_join_abs("backup_processor_test"), path_utils.filter_join_abs("source_test_another.tar.bz2.enc") )
        tg2_folder_another_z = os.path.join(tg2_final, path_utils.filter_join_abs("backup_processor_test"), path_utils.filter_join_abs("source_test_another.tar.bz2") )
        tg2_folder_another_h = os.path.join(tg2_final, path_utils.filter_join_abs("backup_processor_test"), path_utils.filter_join_abs("source_test_another.tar.bz2.enc.sha256") )
        tg2_folder7_e = os.path.join(tg2_final, path_utils.filter_join_abs("backup_processor_test"), path_utils.filter_join_abs("source_test_another"), path_utils.filter_join_abs("folder7.tar.bz2.enc") )
        tg2_folder7_z = os.path.join(tg2_final, path_utils.filter_join_abs("backup_processor_test"), path_utils.filter_join_abs("source_test_another"), path_utils.filter_join_abs("folder7.tar.bz2") )
        tg2_folder7_h = os.path.join(tg2_final, path_utils.filter_join_abs("backup_processor_test"), path_utils.filter_join_abs("source_test_another"), path_utils.filter_join_abs("folder7.tar.bz2.enc.sha256") )

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

        v, r = tar_wrapper.extract(tg1_folder_another_z, self.extracted_folder)
        self.assertTrue(v)

        self.assertTrue( os.path.exists( os.path.join( self.extracted_folder, path_utils.filter_join_abs(self.another_folder7) ) ) )
        self.assertTrue( os.path.exists( os.path.join( self.extracted_folder, path_utils.filter_join_abs(self.file_another) ) ) )

        # reset extracted folder
        path_utils.scratchfolder(self.extracted_folder)

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

        v, r = tar_wrapper.extract(tg2_folder_another_z, self.extracted_folder)
        self.assertTrue(v)

        self.assertTrue( os.path.exists( os.path.join( self.extracted_folder, path_utils.filter_join_abs(self.another_folder7) ) ) )
        self.assertTrue( os.path.exists( os.path.join( self.extracted_folder, path_utils.filter_join_abs(self.file_another) ) ) )

    def testRunBackup3(self):

        # basic execution
        with mock.patch("input_checked_passphrase.get_checked_passphrase", return_value=(True, self.passphrase)):
            r = backup_processor.run_backup(self.test_special_config_file, self.hash_file)
        self.assertTrue(r)

        tg1_final = os.path.join(self.test_target_1_folder, path_utils.filter_join_abs(self.bk_base_folder_test) )
        tg2_final = os.path.join(self.test_target_2_folder, path_utils.filter_join_abs(self.bk_base_folder_test) )

        # check if dates were written in both targets
        self.assertTrue( os.path.exists( os.path.join(tg1_final, path_utils.filter_join_abs("bk_date.txt") ) ) )
        self.assertTrue( os.path.exists( os.path.join(tg2_final, path_utils.filter_join_abs("bk_date.txt") ) ) )

        # target 1
        tg1_space_file1_e = os.path.join(tg1_final, path_utils.filter_join_abs("special_folder"), path_utils.filter_join_abs("   sp_file1.txt.tar.bz2.enc"))
        tg1_space_file1_z = os.path.join(tg1_final, path_utils.filter_join_abs("special_folder"), path_utils.filter_join_abs("   sp_file1.txt.tar.bz2"))
        tg1_space_file1_h = os.path.join(tg1_final, path_utils.filter_join_abs("special_folder"), path_utils.filter_join_abs("   sp_file1.txt.tar.bz2.enc.sha256"))
        tg1_space_file2_e = os.path.join(tg1_final, path_utils.filter_join_abs("special_folder"), path_utils.filter_join_abs("sp_fi  le2.txt.tar.bz2.enc"))
        tg1_space_file2_z = os.path.join(tg1_final, path_utils.filter_join_abs("special_folder"), path_utils.filter_join_abs("sp_fi  le2.txt.tar.bz2"))
        tg1_space_file2_h = os.path.join(tg1_final, path_utils.filter_join_abs("special_folder"), path_utils.filter_join_abs("sp_fi  le2.txt.tar.bz2.enc.sha256"))
        tg1_space_file3_e = os.path.join(tg1_final, path_utils.filter_join_abs("special_folder"), path_utils.filter_join_abs("sp_file3.txt  .tar.bz2.enc"))
        tg1_space_file3_z = os.path.join(tg1_final, path_utils.filter_join_abs("special_folder"), path_utils.filter_join_abs("sp_file3.txt  .tar.bz2"))
        tg1_space_file3_h = os.path.join(tg1_final, path_utils.filter_join_abs("special_folder"), path_utils.filter_join_abs("sp_file3.txt  .tar.bz2.enc.sha256"))

        tg1_space_folder1_e = os.path.join(tg1_final, path_utils.filter_join_abs("special_folder"), path_utils.filter_join_abs("   sp_folder1.tar.bz2.enc"))
        tg1_space_folder1_z = os.path.join(tg1_final, path_utils.filter_join_abs("special_folder"), path_utils.filter_join_abs("   sp_folder1.tar.bz2"))
        tg1_space_folder1_h = os.path.join(tg1_final, path_utils.filter_join_abs("special_folder"), path_utils.filter_join_abs("   sp_folder1.tar.bz2.enc.sha256"))
        tg1_space_folder2_e = os.path.join(tg1_final, path_utils.filter_join_abs("special_folder"), path_utils.filter_join_abs("sp_fol   der2.tar.bz2.enc"))
        tg1_space_folder2_z = os.path.join(tg1_final, path_utils.filter_join_abs("special_folder"), path_utils.filter_join_abs("sp_fol   der2.tar.bz2"))
        tg1_space_folder2_h = os.path.join(tg1_final, path_utils.filter_join_abs("special_folder"), path_utils.filter_join_abs("sp_fol   der2.tar.bz2.enc.sha256"))
        tg1_space_folder3_e = os.path.join(tg1_final, path_utils.filter_join_abs("special_folder"), path_utils.filter_join_abs("sp_folder3   .tar.bz2.enc"))
        tg1_space_folder3_z = os.path.join(tg1_final, path_utils.filter_join_abs("special_folder"), path_utils.filter_join_abs("sp_folder3   .tar.bz2"))
        tg1_space_folder3_h = os.path.join(tg1_final, path_utils.filter_join_abs("special_folder"), path_utils.filter_join_abs("sp_folder3   .tar.bz2.enc.sha256"))

        # target 2
        tg2_space_file1_e = os.path.join(tg2_final, path_utils.filter_join_abs("special_folder"), path_utils.filter_join_abs("   sp_file1.txt.tar.bz2.enc"))
        tg2_space_file1_z = os.path.join(tg2_final, path_utils.filter_join_abs("special_folder"), path_utils.filter_join_abs("   sp_file1.txt.tar.bz2"))
        tg2_space_file1_h = os.path.join(tg2_final, path_utils.filter_join_abs("special_folder"), path_utils.filter_join_abs("   sp_file1.txt.tar.bz2.enc.sha256"))
        tg2_space_file2_e = os.path.join(tg2_final, path_utils.filter_join_abs("special_folder"), path_utils.filter_join_abs("sp_fi  le2.txt.tar.bz2.enc"))
        tg2_space_file2_z = os.path.join(tg2_final, path_utils.filter_join_abs("special_folder"), path_utils.filter_join_abs("sp_fi  le2.txt.tar.bz2"))
        tg2_space_file2_h = os.path.join(tg2_final, path_utils.filter_join_abs("special_folder"), path_utils.filter_join_abs("sp_fi  le2.txt.tar.bz2.enc.sha256"))
        tg2_space_file3_e = os.path.join(tg2_final, path_utils.filter_join_abs("special_folder"), path_utils.filter_join_abs("sp_file3.txt  .tar.bz2.enc"))
        tg2_space_file3_z = os.path.join(tg2_final, path_utils.filter_join_abs("special_folder"), path_utils.filter_join_abs("sp_file3.txt  .tar.bz2"))
        tg2_space_file3_h = os.path.join(tg2_final, path_utils.filter_join_abs("special_folder"), path_utils.filter_join_abs("sp_file3.txt  .tar.bz2.enc.sha256"))

        tg2_space_folder1_e = os.path.join(tg2_final, path_utils.filter_join_abs("special_folder"), path_utils.filter_join_abs("   sp_folder1.tar.bz2.enc"))
        tg2_space_folder1_z = os.path.join(tg2_final, path_utils.filter_join_abs("special_folder"), path_utils.filter_join_abs("   sp_folder1.tar.bz2"))
        tg2_space_folder1_h = os.path.join(tg2_final, path_utils.filter_join_abs("special_folder"), path_utils.filter_join_abs("   sp_folder1.tar.bz2.enc.sha256"))
        tg2_space_folder2_e = os.path.join(tg2_final, path_utils.filter_join_abs("special_folder"), path_utils.filter_join_abs("sp_fol   der2.tar.bz2.enc"))
        tg2_space_folder2_z = os.path.join(tg2_final, path_utils.filter_join_abs("special_folder"), path_utils.filter_join_abs("sp_fol   der2.tar.bz2"))
        tg2_space_folder2_h = os.path.join(tg2_final, path_utils.filter_join_abs("special_folder"), path_utils.filter_join_abs("sp_fol   der2.tar.bz2.enc.sha256"))
        tg2_space_folder3_e = os.path.join(tg2_final, path_utils.filter_join_abs("special_folder"), path_utils.filter_join_abs("sp_folder3   .tar.bz2.enc"))
        tg2_space_folder3_z = os.path.join(tg2_final, path_utils.filter_join_abs("special_folder"), path_utils.filter_join_abs("sp_folder3   .tar.bz2"))
        tg2_space_folder3_h = os.path.join(tg2_final, path_utils.filter_join_abs("special_folder"), path_utils.filter_join_abs("sp_folder3   .tar.bz2.enc.sha256"))

        # check existence
        self.assertTrue( os.path.exists( tg1_space_file1_e ) )
        self.assertTrue( os.path.exists( tg1_space_file1_h ) )
        self.assertTrue( os.path.exists( tg1_space_file2_e ) )
        self.assertTrue( os.path.exists( tg1_space_file2_h ) )
        self.assertTrue( os.path.exists( tg1_space_file3_e ) )
        self.assertTrue( os.path.exists( tg1_space_file3_h ) )

        self.assertTrue( os.path.exists( tg1_space_folder1_e ) )
        self.assertTrue( os.path.exists( tg1_space_folder1_h ) )
        self.assertTrue( os.path.exists( tg1_space_folder2_e ) )
        self.assertTrue( os.path.exists( tg1_space_folder2_h ) )
        self.assertTrue( os.path.exists( tg1_space_folder3_e ) )
        self.assertTrue( os.path.exists( tg1_space_folder3_h ) )

        # check hashes
        self.assertTrue(hash_check.sha256sum_check( tg1_space_file1_e, tg1_space_file1_h ))
        self.assertTrue(hash_check.sha256sum_check( tg1_space_file2_e, tg1_space_file2_h ))
        self.assertTrue(hash_check.sha256sum_check( tg1_space_file3_e, tg1_space_file3_h ))

        self.assertTrue(hash_check.sha256sum_check( tg1_space_folder1_e, tg1_space_folder1_h ))
        self.assertTrue(hash_check.sha256sum_check( tg1_space_folder2_e, tg1_space_folder2_h ))
        self.assertTrue(hash_check.sha256sum_check( tg1_space_folder3_e, tg1_space_folder3_h ))

        # decrypt generated packages
        self.assertTrue(decrypt.symmetric_decrypt( tg1_space_file1_e, tg1_space_file1_z, self.passphrase ))
        self.assertTrue(decrypt.symmetric_decrypt( tg1_space_file2_e, tg1_space_file2_z, self.passphrase ))
        self.assertTrue(decrypt.symmetric_decrypt( tg1_space_file3_e, tg1_space_file3_z, self.passphrase ))
        self.assertTrue(decrypt.symmetric_decrypt( tg1_space_folder1_e, tg1_space_folder1_z, self.passphrase ))
        self.assertTrue(decrypt.symmetric_decrypt( tg1_space_folder2_e, tg1_space_folder2_z, self.passphrase ))
        self.assertTrue(decrypt.symmetric_decrypt( tg1_space_folder3_e, tg1_space_folder3_z, self.passphrase ))

        # extract packages
        v, r = tar_wrapper.extract(tg1_space_file1_z, self.extracted_folder)
        self.assertTrue(v)
        v, r = tar_wrapper.extract(tg1_space_file2_z, self.extracted_folder)
        self.assertTrue(v)
        v, r = tar_wrapper.extract(tg1_space_file3_z, self.extracted_folder)
        self.assertTrue(v)
        v, r = tar_wrapper.extract(tg1_space_folder1_z, self.extracted_folder)
        self.assertTrue(v)
        v, r = tar_wrapper.extract(tg1_space_folder2_z, self.extracted_folder)
        self.assertTrue(v)
        v, r = tar_wrapper.extract(tg1_space_folder3_z, self.extracted_folder)
        self.assertTrue(v)

        # check result
        self.assertTrue( os.path.exists( os.path.join( self.extracted_folder, path_utils.filter_join_abs(self.space_file1) ) ) )
        self.assertTrue( os.path.exists( os.path.join( self.extracted_folder, path_utils.filter_join_abs(self.space_file2) ) ) )
        self.assertTrue( os.path.exists( os.path.join( self.extracted_folder, path_utils.filter_join_abs(self.space_file3) ) ) )
        self.assertTrue( os.path.exists( os.path.join( self.extracted_folder, path_utils.filter_join_abs(self.space_folder1) ) ) )
        self.assertTrue( os.path.exists( os.path.join( self.extracted_folder, path_utils.filter_join_abs(self.space_folder2) ) ) )
        self.assertTrue( os.path.exists( os.path.join( self.extracted_folder, path_utils.filter_join_abs(self.space_folder3) ) ) )

        # reset extracted folder
        path_utils.scratchfolder(self.extracted_folder)

        # check existence
        self.assertTrue( os.path.exists( tg2_space_file1_e ) )
        self.assertTrue( os.path.exists( tg2_space_file1_h ) )
        self.assertTrue( os.path.exists( tg2_space_file2_e ) )
        self.assertTrue( os.path.exists( tg2_space_file2_h ) )
        self.assertTrue( os.path.exists( tg2_space_file3_e ) )
        self.assertTrue( os.path.exists( tg2_space_file3_h ) )

        self.assertTrue( os.path.exists( tg2_space_folder1_e ) )
        self.assertTrue( os.path.exists( tg2_space_folder1_h ) )
        self.assertTrue( os.path.exists( tg2_space_folder2_e ) )
        self.assertTrue( os.path.exists( tg2_space_folder2_h ) )
        self.assertTrue( os.path.exists( tg2_space_folder3_e ) )
        self.assertTrue( os.path.exists( tg2_space_folder3_h ) )

        # check hashes
        self.assertTrue(hash_check.sha256sum_check( tg2_space_file1_e, tg2_space_file1_h ))
        self.assertTrue(hash_check.sha256sum_check( tg2_space_file2_e, tg2_space_file2_h ))
        self.assertTrue(hash_check.sha256sum_check( tg2_space_file3_e, tg2_space_file3_h ))

        self.assertTrue(hash_check.sha256sum_check( tg2_space_folder1_e, tg2_space_folder1_h ))
        self.assertTrue(hash_check.sha256sum_check( tg2_space_folder2_e, tg2_space_folder2_h ))
        self.assertTrue(hash_check.sha256sum_check( tg2_space_folder3_e, tg2_space_folder3_h ))

        # decrypt generated packages
        self.assertTrue(decrypt.symmetric_decrypt( tg2_space_file1_e, tg2_space_file1_z, self.passphrase ))
        self.assertTrue(decrypt.symmetric_decrypt( tg2_space_file2_e, tg2_space_file2_z, self.passphrase ))
        self.assertTrue(decrypt.symmetric_decrypt( tg2_space_file3_e, tg2_space_file3_z, self.passphrase ))
        self.assertTrue(decrypt.symmetric_decrypt( tg2_space_folder1_e, tg2_space_folder1_z, self.passphrase ))
        self.assertTrue(decrypt.symmetric_decrypt( tg2_space_folder2_e, tg2_space_folder2_z, self.passphrase ))
        self.assertTrue(decrypt.symmetric_decrypt( tg2_space_folder3_e, tg2_space_folder3_z, self.passphrase ))

        # extract packages
        v, r = tar_wrapper.extract(tg2_space_file1_z, self.extracted_folder)
        self.assertTrue(v)
        v, r = tar_wrapper.extract(tg2_space_file2_z, self.extracted_folder)
        self.assertTrue(v)
        v, r = tar_wrapper.extract(tg2_space_file3_z, self.extracted_folder)
        self.assertTrue(v)
        v, r = tar_wrapper.extract(tg2_space_folder1_z, self.extracted_folder)
        self.assertTrue(v)
        v, r = tar_wrapper.extract(tg2_space_folder2_z, self.extracted_folder)
        self.assertTrue(v)
        v, r = tar_wrapper.extract(tg2_space_folder3_z, self.extracted_folder)
        self.assertTrue(v)

        # check result
        self.assertTrue( os.path.exists( os.path.join( self.extracted_folder, path_utils.filter_join_abs(self.space_file1) ) ) )
        self.assertTrue( os.path.exists( os.path.join( self.extracted_folder, path_utils.filter_join_abs(self.space_file2) ) ) )
        self.assertTrue( os.path.exists( os.path.join( self.extracted_folder, path_utils.filter_join_abs(self.space_file3) ) ) )
        self.assertTrue( os.path.exists( os.path.join( self.extracted_folder, path_utils.filter_join_abs(self.space_folder1) ) ) )
        self.assertTrue( os.path.exists( os.path.join( self.extracted_folder, path_utils.filter_join_abs(self.space_folder2) ) ) )
        self.assertTrue( os.path.exists( os.path.join( self.extracted_folder, path_utils.filter_join_abs(self.space_folder3) ) ) )

if __name__ == '__main__':
    unittest.main()
