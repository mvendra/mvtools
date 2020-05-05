#!/usr/bin/env python3

import sys
import os
import shutil
import unittest

import create_and_write_file
import mvtools_test_fixture
import path_utils
import git_wrapper

def is_hex_string(the_string):
    try:
        f = int(the_string, 16)
        return True
    except:
        return False

class GitWrapperTest(unittest.TestCase):

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        v, r = mvtools_test_fixture.makeAndGetTestFolder("git_wrapper_test_base")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # first repo
        self.first_repo = path_utils.concat_path(self.test_dir, "first")
        v, r = git_wrapper.init(self.test_dir, "first", False)
        if not v:
            return v, r

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testInitStandard(self):

        second_repo = path_utils.concat_path(self.test_dir, "second")
        v, r = git_wrapper.init(self.test_dir, "second", False)
        self.assertTrue(v)
        self.assertTrue( os.path.exists(second_repo) )

    def testInitBare(self):

        second_repo = path_utils.concat_path(self.test_dir, "second")
        v, r = git_wrapper.init(self.test_dir, "second", True)
        self.assertTrue(v)
        self.assertTrue( os.path.exists(second_repo) )

    def testStage1(self):

        test_file = path_utils.concat_path(self.first_repo, "test_file.txt")
        if not create_and_write_file.create_file_contents(test_file, "test-contents"):
            self.fail("Failed creating test file %s" % test_file)

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.status(self.first_repo)
        self.assertTrue("A  test_file.txt" in r)

    def testStage2(self):

        test_file = path_utils.concat_path(self.first_repo, "test_file.txt")
        if not create_and_write_file.create_file_contents(test_file, "test-contents"):
            self.fail("Failed creating test file %s" % test_file)

        v, r = git_wrapper.stage(self.first_repo, [path_utils.basename_filtered(test_file)])
        self.assertTrue(v)

        v, r = git_wrapper.status(self.first_repo)
        self.assertTrue("A  test_file.txt" in r)

    def testStage3(self):

        test_file = path_utils.concat_path(self.first_repo, "test_file.txt")
        if not create_and_write_file.create_file_contents(test_file, "test-contents"):
            self.fail("Failed creating test file %s" % test_file)

        v, r = git_wrapper.stage(self.first_repo, [test_file])
        self.assertTrue(v)

        v, r = git_wrapper.status(self.first_repo)
        self.assertTrue("A  test_file.txt" in r)

    def testStageFail(self):

        test_file = path_utils.concat_path(self.first_repo, "test_file.txt")
        if not create_and_write_file.create_file_contents(test_file, "test-contents"):
            self.fail("Failed creating test file %s" % test_file)

        v, r = git_wrapper.stage(self.first_repo, test_file)
        self.assertFalse(v)
        self.assertEqual(r, "git_wrapper.stage: file_list must be a list")

    def testCommitDirectFail1(self):

        test_file = path_utils.concat_path(self.first_repo, "test_file.txt")
        if not create_and_write_file.create_file_contents(test_file, "test-contents"):
            self.fail("Failed creating test file %s" % test_file)

        v, r = git_wrapper.commit_direct(self.first_repo, 123)
        self.assertFalse(v)
        self.assertEqual(r, "git_wrapper.commit_direct: params must be a list")

    def testCommitDirectFail2(self):

        test_file = path_utils.concat_path(self.first_repo, "test_file.txt")
        if not create_and_write_file.create_file_contents(test_file, "test-contents"):
            self.fail("Failed creating test file %s" % test_file)

        v, r = git_wrapper.commit_direct(self.first_repo, [])
        self.assertFalse(v)
        self.assertEqual(r, "git_wrapper.commit_direct: nothing to do")

    def testCommitDirect(self):

        test_file = path_utils.concat_path(self.first_repo, "test_file.txt")
        if not create_and_write_file.create_file_contents(test_file, "test-contents"):
            self.fail("Failed creating test file %s" % test_file)

        v, r = git_wrapper.git_wrapper_standard_command(["git", "-C", self.first_repo, "add", "."])
        if not v:
            self.fail(r)

        v, r = git_wrapper.commit_direct(self.first_repo, ["-m", "test commit msg1"])
        self.assertTrue(v)

        with open(test_file, "a") as f:
            f.write("extrastuff")

        v, r = git_wrapper.commit_direct(self.first_repo, ["-a", "-m", "test commit msg2"])
        self.assertTrue(v)

        v, r = git_wrapper.status(self.first_repo)
        self.assertFalse("A  test_file.txt" in r)

    def testCommit(self):

        test_file1 = path_utils.concat_path(self.first_repo, "test_file1.txt")
        if not create_and_write_file.create_file_contents(test_file1, "test-contents1"):
            self.fail("Failed creating test file %s" % test_file1)

        v, r = git_wrapper.git_wrapper_standard_command(["git", "-C", self.first_repo, "add", "."])
        if not v:
            self.fail(r)

        v, r = git_wrapper.commit(self.first_repo, "test commit msg1")
        self.assertTrue(v)

        test_file2 = path_utils.concat_path(self.first_repo, "test_file2.txt")
        if not create_and_write_file.create_file_contents(test_file2, "test-contents2"):
            self.fail("Failed creating test file %s" % test_file2)

        v, r = git_wrapper.status(self.first_repo)
        self.assertTrue("?? test_file2.txt" in r)

        v, r = git_wrapper.git_wrapper_standard_command(["git", "-C", self.first_repo, "add", "."])
        if not v:
            self.fail(r)

        v, r = git_wrapper.commit(self.first_repo, "test commit msg2")
        self.assertTrue(v)

        v, r = git_wrapper.status(self.first_repo)
        self.assertFalse("?? test_file2.txt" in r)

    def testClone1(self):

        test_file = path_utils.concat_path(self.first_repo, "test_file.txt")
        if not create_and_write_file.create_file_contents(test_file, "test-contents"):
            self.fail("Failed creating test file %s" % test_file)

        v, r = git_wrapper.stage(self.first_repo, [test_file])
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.first_repo, "test commit msg")
        self.assertTrue(v)

        second_repo = path_utils.concat_path(self.test_dir, "second")
        v, r = git_wrapper.clone(self.first_repo, second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.remote_list(second_repo)
        self.assertTrue(v)
        self.assertTrue("origin" in r)

    def testClone2(self):

        test_file = path_utils.concat_path(self.first_repo, "test_file.txt")
        if not create_and_write_file.create_file_contents(test_file, "test-contents"):
            self.fail("Failed creating test file %s" % test_file)

        v, r = git_wrapper.stage(self.first_repo, [test_file])
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.first_repo, "test commit msg")
        self.assertTrue(v)

        second_repo = path_utils.concat_path(self.test_dir, "second")
        v, r = git_wrapper.clone(self.first_repo, second_repo, "not-origin")
        self.assertTrue(v)

        v, r = git_wrapper.remote_list(second_repo)
        self.assertTrue(v)
        self.assertTrue("not-origin" in r)

    def testDiff1(self):

        test_file1 = path_utils.concat_path(self.first_repo, "test_file1.txt")
        if not create_and_write_file.create_file_contents(test_file1, "test-contents1"):
            self.fail("Failed creating test file %s" % test_file1)

        test_file2 = path_utils.concat_path(self.first_repo, "test_file2.txt")
        if not create_and_write_file.create_file_contents(test_file2, "test-contents2"):
            self.fail("Failed creating test file %s" % test_file2)

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.first_repo, "test commit msg")
        self.assertTrue(v)

        with open(test_file1, "a") as f:
            f.write("latest content1")

        with open(test_file2, "a") as f:
            f.write("latest content2")

        v, r = git_wrapper.diff(self.first_repo)
        self.assertTrue(v)
        self.assertTrue("+test-contents1latest content1" in r)
        self.assertTrue("+test-contents2latest content2" in r)

    def testDiff2(self):

        test_file1 = path_utils.concat_path(self.first_repo, "test_file1.txt")
        if not create_and_write_file.create_file_contents(test_file1, "test-contents1"):
            self.fail("Failed creating test file %s" % test_file1)

        test_file2 = path_utils.concat_path(self.first_repo, "test_file2.txt")
        if not create_and_write_file.create_file_contents(test_file2, "test-contents2"):
            self.fail("Failed creating test file %s" % test_file2)

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.first_repo, "test commit msg")
        self.assertTrue(v)

        with open(test_file1, "a") as f:
            f.write("latest content1")

        with open(test_file2, "a") as f:
            f.write("latest content2")

        v, r = git_wrapper.diff(self.first_repo, [test_file1])
        self.assertTrue(v)
        self.assertTrue("+test-contents1latest content1" in r)
        self.assertFalse("+test-contents2latest content2" in r)

    def testDiff3(self):

        test_file1 = path_utils.concat_path(self.first_repo, "test_file1.txt")
        if not create_and_write_file.create_file_contents(test_file1, "test-contents1"):
            self.fail("Failed creating test file %s" % test_file1)

        test_file2 = path_utils.concat_path(self.first_repo, "test_file2.txt")
        if not create_and_write_file.create_file_contents(test_file2, "test-contents2"):
            self.fail("Failed creating test file %s" % test_file2)

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.first_repo, "test commit msg")
        self.assertTrue(v)

        with open(test_file1, "a") as f:
            f.write("latest content1")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        with open(test_file2, "a") as f:
            f.write("latest content2")

        v, r = git_wrapper.diff(self.first_repo)
        self.assertTrue(v)
        self.assertFalse("+test-contents1latest content1" in r)
        self.assertTrue("+test-contents2latest content2" in r)

    def testDiffFail1(self):
        v, r = git_wrapper.diff(self.first_repo, "string")
        self.assertFalse(v)
        self.assertEqual(r, "git_wrapper.diff: file_list must be a list")

    def testDiffFail2(self):
        v, r = git_wrapper.diff(self.first_repo, 123)
        self.assertFalse(v)
        self.assertEqual(r, "git_wrapper.diff: file_list must be a list")

    def testDiffCached1(self):

        test_file1 = path_utils.concat_path(self.first_repo, "test_file1.txt")
        if not create_and_write_file.create_file_contents(test_file1, "test-contents1"):
            self.fail("Failed creating test file %s" % test_file1)

        test_file2 = path_utils.concat_path(self.first_repo, "test_file2.txt")
        if not create_and_write_file.create_file_contents(test_file2, "test-contents2"):
            self.fail("Failed creating test file %s" % test_file2)

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.first_repo, "test commit msg")
        self.assertTrue(v)

        with open(test_file1, "a") as f:
            f.write("latest content1")

        with open(test_file2, "a") as f:
            f.write("latest content2")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.diff_cached(self.first_repo)
        self.assertTrue(v)
        self.assertTrue("+test-contents1latest content1" in r)
        self.assertTrue("+test-contents2latest content2" in r)

    def testDiffCached2(self):

        test_file1 = path_utils.concat_path(self.first_repo, "test_file1.txt")
        if not create_and_write_file.create_file_contents(test_file1, "test-contents1"):
            self.fail("Failed creating test file %s" % test_file1)

        test_file2 = path_utils.concat_path(self.first_repo, "test_file2.txt")
        if not create_and_write_file.create_file_contents(test_file2, "test-contents2"):
            self.fail("Failed creating test file %s" % test_file2)

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.first_repo, "test commit msg")
        self.assertTrue(v)

        with open(test_file1, "a") as f:
            f.write("latest content1")

        with open(test_file2, "a") as f:
            f.write("latest content2")

        v, r = git_wrapper.diff_cached(self.first_repo)
        self.assertTrue(v)
        self.assertFalse("+test-contents1latest content1" in r)
        self.assertFalse("+test-contents2latest content2" in r)

    def testDiffCached3(self):

        test_file1 = path_utils.concat_path(self.first_repo, "test_file1.txt")
        if not create_and_write_file.create_file_contents(test_file1, "test-contents1"):
            self.fail("Failed creating test file %s" % test_file1)

        test_file2 = path_utils.concat_path(self.first_repo, "test_file2.txt")
        if not create_and_write_file.create_file_contents(test_file2, "test-contents2"):
            self.fail("Failed creating test file %s" % test_file2)

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.first_repo, "test commit msg")
        self.assertTrue(v)

        with open(test_file1, "a") as f:
            f.write("latest content1")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        with open(test_file2, "a") as f:
            f.write("latest content2")

        v, r = git_wrapper.diff_cached(self.first_repo)
        self.assertTrue(v)
        self.assertTrue("+test-contents1latest content1" in r)
        self.assertFalse("+test-contents2latest content2" in r)

    def testDiffCachedFail1(self):
        v, r = git_wrapper.diff_cached(self.first_repo, "string")
        self.assertFalse(v)
        self.assertEqual(r, "git_wrapper.diff_cached: file_list must be a list")

    def testDiffCachedFail2(self):
        v, r = git_wrapper.diff_cached(self.first_repo, 123)
        self.assertFalse(v)
        self.assertEqual(r, "git_wrapper.diff_cached: file_list must be a list")

    def testRevParse(self):

        test_file = path_utils.concat_path(self.first_repo, "test_file.txt")
        if not create_and_write_file.create_file_contents(test_file, "test-contents"):
            self.fail("Failed creating test file %s" % test_file)

        v, r = git_wrapper.stage(self.first_repo, [test_file])
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.first_repo, "test commit msg")
        self.assertTrue(v)

        v, r = git_wrapper.rev_parse(self.first_repo)
        self.assertTrue(v)
        self.assertTrue( (len(r) >= (40 + len(os.linesep))) and is_hex_string(r))

    def testLsFiles1(self):

        test_file1 = path_utils.concat_path(self.first_repo, "test_file1.txt")
        if not create_and_write_file.create_file_contents(test_file1, "test-contents1"):
            self.fail("Failed creating test file %s" % test_file1)

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.first_repo, "test commit msg")
        self.assertTrue(v)

        test_file2 = path_utils.concat_path(self.first_repo, "test_file2.txt")
        if not create_and_write_file.create_file_contents(test_file2, "test-contents2"):
            self.fail("Failed creating test file %s" % test_file2)

        test_file3 = path_utils.concat_path(self.first_repo, "test_file3.txt")
        if not create_and_write_file.create_file_contents(test_file3, "test-contents3"):
            self.fail("Failed creating test file %s" % test_file3)

        v, r = git_wrapper.ls_files(self.first_repo)
        self.assertTrue(v)
        self.assertFalse( path_utils.basename_filtered(test_file1) in r)
        self.assertTrue( path_utils.basename_filtered(test_file2) in r)
        self.assertTrue( path_utils.basename_filtered(test_file3) in r)

        v, r = git_wrapper.stage(self.first_repo, [test_file3])
        self.assertTrue(v)

        v, r = git_wrapper.ls_files(self.first_repo)
        self.assertTrue(v)
        self.assertFalse( path_utils.basename_filtered(test_file1) in r)
        self.assertTrue( path_utils.basename_filtered(test_file2) in r)
        self.assertFalse( path_utils.basename_filtered(test_file3) in r)

    def testLsFiles2(self):

        test_file = path_utils.concat_path(self.first_repo, "test_file.txt")
        if not create_and_write_file.create_file_contents(test_file, "test-contents"):
            self.fail("Failed creating test file %s" % test_file)

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.ls_files(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(r, "")

    def testStash_and_StashList(self):

        test_file = path_utils.concat_path(self.first_repo, "test_file.txt")
        if not create_and_write_file.create_file_contents(test_file, "test-contents"):
            self.fail("Failed creating test file %s" % test_file)

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.first_repo, "stash-list test commit msg")
        self.assertTrue(v)

        with open(test_file, "a") as f:
            f.write("latest content")

        v, r = git_wrapper.stash(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.stash_list(self.first_repo)
        self.assertTrue(v)
        self.assertEqual( len(r.strip().split(os.linesep)), 1 )
        self.assertTrue( "stash@{0}: WIP on master:" in r)
        self.assertTrue( "stash-list test commit msg" in r)

        with open(test_file, "a") as f:
            f.write("yet more stuff")

        v, r = git_wrapper.stash(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.stash_list(self.first_repo)
        self.assertTrue(v)
        self.assertEqual( len(r.strip().split(os.linesep)), 2 )
        self.assertTrue( "stash@{0}: WIP on master:" in r)
        self.assertTrue( "stash@{1}: WIP on master:" in r)
        self.assertTrue( "stash-list test commit msg" in r)

    def testStash_and_StashShow(self):

        test_file = path_utils.concat_path(self.first_repo, "test_file.txt")
        if not create_and_write_file.create_file_contents(test_file, "test-contents"):
            self.fail("Failed creating test file %s" % test_file)

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.first_repo, "stash-list test commit msg")
        self.assertTrue(v)

        v, r = git_wrapper.stash_show(self.first_repo, "stash@{0}")
        self.assertFalse(v)

        with open(test_file, "a") as f:
            f.write("latest content, stash show 1")

        v, r = git_wrapper.stash(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.stash_show(self.first_repo, "stash@{0}")
        self.assertTrue(v)
        self.assertTrue("+test-contentslatest content, stash show 1" in r)

        with open(test_file, "a") as f:
            f.write("latest content, stash show 2")

        v, r = git_wrapper.stash(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.stash_show(self.first_repo, "stash@{0}")
        self.assertTrue(v)
        self.assertTrue("+test-contentslatest content, stash show 2" in r)
        self.assertFalse("+test-contentslatest content, stash show 1" in r)

        v, r = git_wrapper.stash_show(self.first_repo, "stash@{1}")
        self.assertTrue(v)
        self.assertFalse("+test-contentslatest content, stash show 2" in r)
        self.assertTrue("+test-contentslatest content, stash show 1" in r)

    def testLogOneline(self):

        test_file = path_utils.concat_path(self.first_repo, "test_file.txt")
        if not create_and_write_file.create_file_contents(test_file, "test-contents"):
            self.fail("Failed creating test file %s" % test_file)

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.first_repo, "log-oneline test commit msg 1")
        self.assertTrue(v)

        v, r = git_wrapper.log_oneline(self.first_repo)
        self.assertTrue(v)
        self.assertEqual( len(r.strip().split(os.linesep)), 1 )
        self.assertTrue("log-oneline test commit msg 1" in r)

        with open(test_file, "a") as f:
            f.write("latest content, log-oneline")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.first_repo, "log-oneline test commit msg 2")
        self.assertTrue(v)

        v, r = git_wrapper.log_oneline(self.first_repo)
        self.assertTrue(v)
        self.assertEqual( len(r.strip().split(os.linesep)), 2 )
        self.assertTrue("log-oneline test commit msg 1" in r)
        self.assertTrue("log-oneline test commit msg 2" in r)

    def testLog(self):

        test_file = path_utils.concat_path(self.first_repo, "test_file.txt")
        if not create_and_write_file.create_file_contents(test_file, "test-contents"):
            self.fail("Failed creating test file %s" % test_file)

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.first_repo, "log-oneline test commit msg 1")
        self.assertTrue(v)

        v, r = git_wrapper.log(self.first_repo)

        self.assertTrue(v)
        self.assertEqual( len(r.strip().split(os.linesep)), 5 )
        self.assertTrue("log-oneline test commit msg 1" in r)

        with open(test_file, "a") as f:
            f.write("latest content, log-oneline")

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.first_repo, "log-oneline test commit msg 2")
        self.assertTrue(v)

        v, r = git_wrapper.log(self.first_repo)

        self.assertTrue(v)
        self.assertEqual( len(r.strip().split(os.linesep)), 11 )
        self.assertTrue("log-oneline test commit msg 1" in r)
        self.assertTrue("log-oneline test commit msg 2" in r)

    def testShow(self):

        test_file = path_utils.concat_path(self.first_repo, "test_file.txt")
        if not create_and_write_file.create_file_contents(test_file, "test-show, test contents"):
            self.fail("Failed creating test file %s" % test_file)

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.first_repo, "test-show, test commit msg")
        self.assertTrue(v)

        v, r = git_wrapper.log_oneline(self.first_repo)
        self.assertTrue(v)
        p = r.find(" ")
        if p == -1:
            self.fail("Failed retrieving commit id, testShow")
        commit_id = r[:p]

        v, r = git_wrapper.show(self.first_repo, commit_id)
        self.assertTrue(v)
        self.assertTrue("test-show, test contents" in r)

    def testStatus(self):

        test_file1 = path_utils.concat_path(self.first_repo, "test_file1.txt")
        if not create_and_write_file.create_file_contents(test_file1, "test-show, test contents"):
            self.fail("Failed creating test file %s" % test_file1)

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.first_repo, "test-show, test commit msg")
        self.assertTrue(v)

        v, r = git_wrapper.status(self.first_repo)
        self.assertTrue(v)
        self.assertEqual("", r)

        test_file2 = path_utils.concat_path(self.first_repo, "test_file2.txt")
        if not create_and_write_file.create_file_contents(test_file2, "test-contents2"):
            self.fail("Failed creating test file %s" % test_file2)

        v, r = git_wrapper.status(self.first_repo)
        self.assertTrue(v)
        self.assertTrue("?? test_file2.txt" in r)

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.status(self.first_repo)
        self.assertTrue(v)
        self.assertTrue("A  test_file2.txt" in r)

    def testStatusSimple(self):

        test_file1 = path_utils.concat_path(self.first_repo, "test_file1.txt")
        if not create_and_write_file.create_file_contents(test_file1, "test-show, test contents"):
            self.fail("Failed creating test file %s" % test_file1)

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.first_repo, "test-show, test commit msg")
        self.assertTrue(v)

        v, r = git_wrapper.status_simple(self.first_repo)
        self.assertTrue(v)
        self.assertEqual("", r)

        test_file2 = path_utils.concat_path(self.first_repo, "test_file2.txt")
        if not create_and_write_file.create_file_contents(test_file2, "test-contents2"):
            self.fail("Failed creating test file %s" % test_file2)

        v, r = git_wrapper.status_simple(self.first_repo)
        self.assertTrue(v)
        self.assertTrue("?? test_file2.txt" in r)

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.status_simple(self.first_repo)
        self.assertTrue(v)
        self.assertTrue("A  test_file2.txt" in r)

    def testRemoteList_and_RemoteAdd_and_ChangeUrl(self):

        test_file = path_utils.concat_path(self.first_repo, "test_file.txt")
        if not create_and_write_file.create_file_contents(test_file, "test-show, test contents"):
            self.fail("Failed creating test file %s" % test_file)

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.first_repo, "test-show, test commit msg")
        self.assertTrue(v)

        v, r = git_wrapper.remote_list(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(r, "")

        second_repo = path_utils.concat_path(self.test_dir, "second")
        v, r = git_wrapper.remote_add(self.first_repo, "new-remote", second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.remote_list(self.first_repo)
        self.assertTrue(v)
        self.assertTrue( ("new-remote\t%s (fetch)" % second_repo) in r )
        self.assertTrue( ("new-remote\t%s (push)" % second_repo) in r )

        third_repo = path_utils.concat_path(self.test_dir, "third")
        v, r = git_wrapper.remote_change_url(self.first_repo, "nonexistant-remote", third_repo)
        self.assertFalse(v)

        v, r = git_wrapper.remote_change_url(self.first_repo, "new-remote", third_repo)
        self.assertTrue(v)

        v, r = git_wrapper.remote_list(self.first_repo)
        self.assertTrue(v)
        self.assertTrue( ("new-remote\t%s (fetch)" % third_repo) in r )
        self.assertTrue( ("new-remote\t%s (push)" % third_repo) in r )

    def testBranch(self):

        v, r = git_wrapper.branch(self.first_repo)
        self.assertTrue(v)
        self.assertEqual("", r.strip())

        test_file = path_utils.concat_path(self.first_repo, "test_file.txt")
        if not create_and_write_file.create_file_contents(test_file, "test-show, test contents"):
            self.fail("Failed creating test file %s" % test_file)

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.first_repo, "test-show, test commit msg")
        self.assertTrue(v)

        v, r = git_wrapper.branch(self.first_repo)
        self.assertTrue(v)
        self.assertTrue("* master" in r)

    def testBranchCreateAndSwitch(self):

        v, r = git_wrapper.branch(self.first_repo)
        self.assertTrue(v)
        self.assertEqual("", r.strip())

        test_file = path_utils.concat_path(self.first_repo, "test_file.txt")
        if not create_and_write_file.create_file_contents(test_file, "test-show, test contents"):
            self.fail("Failed creating test file %s" % test_file)

        v, r = git_wrapper.stage(self.first_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.first_repo, "test-show, test commit msg")
        self.assertTrue(v)

        v, r = git_wrapper.branch_create_and_switch(self.first_repo, "offline")
        self.assertTrue(v)

        v, r = git_wrapper.branch(self.first_repo)
        self.assertTrue(v)
        self.assertTrue("* offline" in r)

if __name__ == '__main__':
    unittest.main()
