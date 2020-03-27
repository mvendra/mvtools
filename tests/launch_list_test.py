#!/usr/bin/env python3

import sys
import os
import stat
import shutil
import unittest

import mvtools_test_fixture
import create_and_write_file
import path_utils

import launch_list
import fsquery

class LaunchListTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("launch_list_test_base")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        self.test_allgood = path_utils.concat_path(self.test_dir, "allgood")
        os.mkdir(self.test_allgood)

        self.test_allbad = path_utils.concat_path(self.test_dir, "allbad")
        os.mkdir(self.test_allbad)

        self.test_mixedbag = path_utils.concat_path(self.test_dir, "mixedbag")
        os.mkdir(self.test_mixedbag)

        # setup allgood

        self.cmd1 = path_utils.concat_path(self.test_allgood, "cmd1.sh")
        cmd1_contents = "#!/bin/bash" + os.linesep + "exit 0"
        create_and_write_file.create_file_contents(self.cmd1, cmd1_contents)
        os.chmod(self.cmd1, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)

        self.cmd2 = path_utils.concat_path(self.test_allgood, "cmd2.sh")
        cmd2_contents = "#!/bin/bash" + os.linesep + "exit 0"
        create_and_write_file.create_file_contents(self.cmd2, cmd2_contents)
        os.chmod(self.cmd2, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)

        self.cmd3 = path_utils.concat_path(self.test_allgood, "cmd3.sh")
        cmd3_contents = "#!/bin/bash" + os.linesep + "exit 0"
        create_and_write_file.create_file_contents(self.cmd3, cmd3_contents)
        os.chmod(self.cmd3, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)

        # setup allbad

        self.cmd4 = path_utils.concat_path(self.test_allbad, "cmd4.sh")
        cmd4_contents = "#!/bin/bash" + os.linesep + "exit 1"
        create_and_write_file.create_file_contents(self.cmd4, cmd4_contents)
        os.chmod(self.cmd4, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)

        self.cmd5 = path_utils.concat_path(self.test_allbad, "cmd5.sh")
        cmd5_contents = "#!/bin/bash" + os.linesep + "exit 1"
        create_and_write_file.create_file_contents(self.cmd5, cmd5_contents)
        os.chmod(self.cmd5, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)

        self.cmd6 = path_utils.concat_path(self.test_allbad, "cmd6.sh")
        cmd6_contents = "#!/bin/bash" + os.linesep + "exit 1"
        create_and_write_file.create_file_contents(self.cmd6, cmd6_contents)
        os.chmod(self.cmd6, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)

        # setup mixedbag

        self.cmd7 = path_utils.concat_path(self.test_mixedbag, "cmd7.sh")
        cmd7_contents = "#!/bin/bash" + os.linesep + "exit 0"
        create_and_write_file.create_file_contents(self.cmd7, cmd7_contents)
        os.chmod(self.cmd7, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)

        self.cmd8 = path_utils.concat_path(self.test_mixedbag, "cmd8.sh")
        cmd8_contents = "#!/bin/bash" + os.linesep + "exit 1"
        create_and_write_file.create_file_contents(self.cmd8, cmd8_contents)
        os.chmod(self.cmd8, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)

        self.cmd9 = path_utils.concat_path(self.test_mixedbag, "cmd9.sh")
        cmd9_contents = "#!/bin/bash" + os.linesep + "exit 0"
        create_and_write_file.create_file_contents(self.cmd9, cmd9_contents)
        os.chmod(self.cmd9, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testListAllGood(self):
        l = fsquery.makecontentlist(self.test_allgood, False, True, False, True, False, True, None)
        v, r = launch_list.run_list(l, None)
        self.assertTrue(v)

    def testListAllBad(self):
        l = fsquery.makecontentlist(self.test_allbad, False, True, False, True, False, True, None)
        v, r = launch_list.run_list(l, None)
        self.assertFalse(v)
        for i in r:
            self.assertFalse(i[0])

    def testListMixedBag(self):
        l = fsquery.makecontentlist(self.test_mixedbag, False, True, False, True, False, True, None)
        v, r = launch_list.run_list(l, None)
        self.assertFalse(v)

        for i in r:
            if os.path.basename(i[1]) == os.path.basename(self.cmd7):
                self.assertTrue(i[0])
            elif os.path.basename(i[1]) == os.path.basename(self.cmd8):
                self.assertFalse(i[0])
            elif os.path.basename(i[1]) == os.path.basename(self.cmd9):
                self.assertTrue(i[0])

    def testListDebased(self):
        l = [os.path.basename(self.cmd1), os.path.basename(self.cmd2), os.path.basename(self.cmd3)]
        v, r = launch_list.run_list(l, self.test_allgood)
        self.assertTrue(v)

if __name__ == '__main__':
    unittest.main()
