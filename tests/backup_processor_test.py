#!/usr/bin/env python3

import sys
import os
import shutil
import unittest

import create_and_write_file
import mvtools_test_fixture

import backup_processor

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

        # nonexistent folder - for testing only
        self.nonexistent = os.path.join(self.test_dir, "nonexistent")

        # create folders, source and target
        self.test_source_folder = os.path.join(self.test_dir, "source_test")
        os.mkdir(self.test_source_folder)
        self.test_target_folder = os.path.join(self.test_dir, "target_test")
        os.mkdir(self.test_target_folder)

        # create test folders
        self.folder1 = os.path.join(self.test_source_folder, "folder1")
        self.folder2 = os.path.join(self.test_source_folder, "folder2")
        self.folder3 = os.path.join(self.test_source_folder, "folder3")
        os.mkdir(self.folder1)
        os.mkdir(self.folder2)
        os.mkdir(self.folder3)

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

        # create config file
        cfg_file_contents = ""
        #cfg_file_contents += "BKPREPARATION = ...\n"
        cfg_file_contents += "BKARTIFACTS_BASE = %s\n" % self.test_source_folder
        cfg_file_contents += "BKTARGETS_ROOT = %s - nocheckmount\n" % self.test_target_folder
        cfg_file_contents += "BKTEMP = %s\n" % self.test_dir
        cfg_file_contents += "BKTARGETS_BASEDIR = BackupTests\n"

        self.test_config_file = os.path.join(self.test_dir, "test_config_file.cfg")
        create_and_write_file.create_file_contents(self.test_config_file, cfg_file_contents)

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testArtifactBase1(self):
        artbase = backup_processor.ArtifactBase(self.test_source_folder, [self.folder2])
        self.assertTrue(artbase.get_path(), self.test_source_folder)
        self.assertTrue(artbase.get_list_exceptions(), [self.folder2])
        self.assertTrue(artbase.validate_exceptions(), (True, ""))

    def testArtifactBase2(self):
        artbase = backup_processor.ArtifactBase(self.test_source_folder, [self.nonexistent])
        self.assertTrue(artbase.get_path(), self.test_source_folder)
        self.assertTrue(artbase.get_list_exceptions(), [self.nonexistent])
        r = artbase.validate_exceptions()
        self.assertFalse(r[0])

    def testMakeBackupArtifactsList(self):
        artbase = backup_processor.ArtifactBase(self.test_source_folder, [self.folder2])
        res = backup_processor.make_backup_artifacts_list([artbase])
        self.assertTrue(self.folder1 in res)
        self.assertFalse(self.folder2 in res)
        self.assertTrue(self.folder3 in res)

    def testReadConfig(self):
        v, r = backup_processor.read_config(self.test_config_file)
        self.assertTrue(v)
        self.assertEqual(r[0], "")
        self.assertEqual(r[2], [self.test_target_folder])
        self.assertEqual(r[3], "BackupTests")
        self.assertEqual(r[4], self.test_dir)

if __name__ == '__main__':
    unittest.main()
