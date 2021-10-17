#!/usr/bin/env python3

import sys
import os
import shutil
import unittest

import create_and_write_file
import mvtools_test_fixture
import path_utils
import git_wrapper
import collect_git_patch

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

        v, r = mvtools_test_fixture.makeAndGetTestFolder("git_wrapper_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # first repo
        self.first_repo = path_utils.concat_path(self.test_dir, "first")
        v, r = git_wrapper.init(self.test_dir, "first", True)
        if not v:
            return v, r

        # second repo
        self.second_repo = path_utils.concat_path(self.test_dir, "second")
        v, r = git_wrapper.clone(self.first_repo, self.second_repo)
        if not v:
            return v, r

        # third repo
        self.third_repo = path_utils.concat_path(self.test_dir, "   third   ")
        v, r = git_wrapper.init(self.test_dir, "   third   ", True)
        if not v:
            return v, r

        # patch files storage path
        self.storage_path = path_utils.concat_path(self.test_dir, "storage_path")
        os.mkdir(self.storage_path)

        # nonexistent_repo
        self.nonexistent_repo = path_utils.concat_path(self.test_dir, "nonexistent")

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testInitStandard(self):

        third_repo = path_utils.concat_path(self.test_dir, "third")
        v, r = git_wrapper.init(self.test_dir, "third", False)
        self.assertTrue(v)
        self.assertTrue( os.path.exists(third_repo) )

    def testInitBare(self):

        third_repo = path_utils.concat_path(self.test_dir, "third")
        v, r = git_wrapper.init(self.test_dir, "third", True)
        self.assertTrue(v)
        self.assertTrue( os.path.exists(third_repo) )

    def testStage1(self):

        test_file = path_utils.concat_path(self.second_repo, "test_file.txt")
        if not create_and_write_file.create_file_contents(test_file, "test-contents"):
            self.fail("Failed creating test file %s" % test_file)

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.status(self.second_repo)
        self.assertTrue("A  test_file.txt" in r)

    def testStage2(self):

        test_file = path_utils.concat_path(self.second_repo, "test_file.txt")
        if not create_and_write_file.create_file_contents(test_file, "test-contents"):
            self.fail("Failed creating test file %s" % test_file)

        v, r = git_wrapper.stage(self.second_repo, [path_utils.basename_filtered(test_file)])
        self.assertTrue(v)

        v, r = git_wrapper.status(self.second_repo)
        self.assertTrue("A  test_file.txt" in r)

    def testStage3(self):

        test_file = path_utils.concat_path(self.second_repo, "test_file.txt")
        if not create_and_write_file.create_file_contents(test_file, "test-contents"):
            self.fail("Failed creating test file %s" % test_file)

        v, r = git_wrapper.stage(self.second_repo, [test_file])
        self.assertTrue(v)

        v, r = git_wrapper.status(self.second_repo)
        self.assertTrue("A  test_file.txt" in r)

    def testStageFail(self):

        test_file = path_utils.concat_path(self.second_repo, "test_file.txt")
        if not create_and_write_file.create_file_contents(test_file, "test-contents"):
            self.fail("Failed creating test file %s" % test_file)

        v, r = git_wrapper.stage(self.second_repo, test_file)
        self.assertFalse(v)
        self.assertEqual(r, "git_wrapper.stage: file_list must be a list")

    def testCommitDirectFail1(self):

        test_file = path_utils.concat_path(self.second_repo, "test_file.txt")
        if not create_and_write_file.create_file_contents(test_file, "test-contents"):
            self.fail("Failed creating test file %s" % test_file)

        v, r = git_wrapper.commit_direct(self.second_repo, 123)
        self.assertFalse(v)
        self.assertEqual(r, "git_wrapper.commit_direct: params must be a list")

    def testCommitDirectFail2(self):

        test_file = path_utils.concat_path(self.second_repo, "test_file.txt")
        if not create_and_write_file.create_file_contents(test_file, "test-contents"):
            self.fail("Failed creating test file %s" % test_file)

        v, r = git_wrapper.commit_direct(self.second_repo, [])
        self.assertFalse(v)
        self.assertEqual(r, "git_wrapper.commit_direct: nothing to do")

    def testCommitDirect(self):

        test_file = path_utils.concat_path(self.second_repo, "test_file.txt")
        if not create_and_write_file.create_file_contents(test_file, "test-contents"):
            self.fail("Failed creating test file %s" % test_file)

        v, r = git_wrapper.git_wrapper_standard_command(["git", "-C", self.second_repo, "add", "."])
        if not v:
            self.fail(r)

        v, r = git_wrapper.commit_direct(self.second_repo, ["-m", "test commit msg1"])
        self.assertTrue(v)

        with open(test_file, "a") as f:
            f.write("extrastuff")

        v, r = git_wrapper.commit_direct(self.second_repo, ["-a", "-m", "test commit msg2"])
        self.assertTrue(v)

        v, r = git_wrapper.status(self.second_repo)
        self.assertFalse("A  test_file.txt" in r)

    def testCommit(self):

        test_file1 = path_utils.concat_path(self.second_repo, "test_file1.txt")
        if not create_and_write_file.create_file_contents(test_file1, "test-contents1"):
            self.fail("Failed creating test file %s" % test_file1)

        v, r = git_wrapper.git_wrapper_standard_command(["git", "-C", self.second_repo, "add", "."])
        if not v:
            self.fail(r)

        v, r = git_wrapper.commit(self.second_repo, "test commit msg1")
        self.assertTrue(v)

        test_file2 = path_utils.concat_path(self.second_repo, "test_file2.txt")
        if not create_and_write_file.create_file_contents(test_file2, "test-contents2"):
            self.fail("Failed creating test file %s" % test_file2)

        v, r = git_wrapper.status(self.second_repo)
        self.assertTrue("?? test_file2.txt" in r)

        v, r = git_wrapper.git_wrapper_standard_command(["git", "-C", self.second_repo, "add", "."])
        if not v:
            self.fail(r)

        v, r = git_wrapper.commit(self.second_repo, "test commit msg2")
        self.assertTrue(v)

        v, r = git_wrapper.status(self.second_repo)
        self.assertFalse("?? test_file2.txt" in r)

    def testClone1(self):

        test_file = path_utils.concat_path(self.second_repo, "test_file.txt")
        if not create_and_write_file.create_file_contents(test_file, "test-contents"):
            self.fail("Failed creating test file %s" % test_file)

        v, r = git_wrapper.stage(self.second_repo, [test_file])
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test commit msg")
        self.assertTrue(v)

        third_repo = path_utils.concat_path(self.test_dir, "third")
        v, r = git_wrapper.clone(self.second_repo, third_repo)
        self.assertTrue(v)

        v, r = git_wrapper.remote_list(third_repo)
        self.assertTrue(v)
        self.assertTrue("origin" in r)

    def testClone2(self):

        test_file = path_utils.concat_path(self.second_repo, "test_file.txt")
        if not create_and_write_file.create_file_contents(test_file, "test-contents"):
            self.fail("Failed creating test file %s" % test_file)

        v, r = git_wrapper.stage(self.second_repo, [test_file])
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test commit msg")
        self.assertTrue(v)

        third_repo = path_utils.concat_path(self.test_dir, "third")
        v, r = git_wrapper.clone(self.second_repo, third_repo, "not-origin")
        self.assertTrue(v)

        v, r = git_wrapper.remote_list(third_repo)
        self.assertTrue(v)
        self.assertTrue("not-origin" in r)

    def testClone3(self):

        test_file = path_utils.concat_path(self.second_repo, "test_file.txt")
        if not create_and_write_file.create_file_contents(test_file, "test-contents"):
            self.fail("Failed creating test file %s" % test_file)

        v, r = git_wrapper.stage(self.second_repo, [test_file])
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test commit msg")
        self.assertTrue(v)

        third_repo = path_utils.concat_path(self.test_dir, "third")
        v, r = git_wrapper.clone(self.nonexistent_repo, third_repo)
        self.assertFalse(v)

    def testCloneExt1(self):

        test_file = path_utils.concat_path(self.second_repo, "test_file.txt")
        if not create_and_write_file.create_file_contents(test_file, "test-contents"):
            self.fail("Failed creating test file %s" % test_file)

        v, r = git_wrapper.stage(self.second_repo, [test_file])
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test commit msg")
        self.assertTrue(v)

        third_repo = path_utils.concat_path(self.test_dir, "third")
        v, r = git_wrapper.clone_ext(self.second_repo, third_repo)
        self.assertTrue(v)
        self.assertTrue(r[0])

        v, r = git_wrapper.remote_list(third_repo)
        self.assertTrue(v)
        self.assertTrue("origin" in r)

    def testCloneExt2(self):

        test_file = path_utils.concat_path(self.second_repo, "test_file.txt")
        if not create_and_write_file.create_file_contents(test_file, "test-contents"):
            self.fail("Failed creating test file %s" % test_file)

        v, r = git_wrapper.stage(self.second_repo, [test_file])
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test commit msg")
        self.assertTrue(v)

        third_repo = path_utils.concat_path(self.test_dir, "third")
        v, r = git_wrapper.clone_ext(self.second_repo, third_repo, "not-origin")
        self.assertTrue(v)
        self.assertTrue(r[0])

        v, r = git_wrapper.remote_list(third_repo)
        self.assertTrue(v)
        self.assertTrue("not-origin" in r)

    def testCloneExt3(self):

        test_file = path_utils.concat_path(self.second_repo, "test_file.txt")
        if not create_and_write_file.create_file_contents(test_file, "test-contents"):
            self.fail("Failed creating test file %s" % test_file)

        v, r = git_wrapper.stage(self.second_repo, [test_file])
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test commit msg")
        self.assertTrue(v)

        third_repo = path_utils.concat_path(self.test_dir, "third")
        v, r = git_wrapper.clone_ext(self.nonexistent_repo, third_repo)
        self.assertTrue(v)
        self.assertFalse(r[0])

    def testCloneBare1(self):

        test_file = path_utils.concat_path(self.second_repo, "test_file.txt")
        if not create_and_write_file.create_file_contents(test_file, "test-contents"):
            self.fail("Failed creating test file %s" % test_file)

        v, r = git_wrapper.stage(self.second_repo, [test_file])
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test commit msg")
        self.assertTrue(v)

        bare_cloned_repo = path_utils.concat_path(self.test_dir, "bare_cloned_repo")
        v, r = git_wrapper.clone_bare(self.second_repo, bare_cloned_repo)
        self.assertTrue(v)
        self.assertTrue( os.path.exists(bare_cloned_repo) )
        bare_cloned_repo_objects = path_utils.concat_path(bare_cloned_repo, "objects")
        self.assertTrue( os.path.exists(bare_cloned_repo_objects) )

        third_cloned_from_bare = path_utils.concat_path(self.test_dir, "third_cloned_from_bare")
        v, r = git_wrapper.clone(bare_cloned_repo, third_cloned_from_bare)
        self.assertTrue(third_cloned_from_bare)
        third_cloned_from_bare_test_file = path_utils.concat_path(third_cloned_from_bare, path_utils.basename_filtered(test_file))
        self.assertTrue(os.path.exists(third_cloned_from_bare_test_file))

    def testDiff1(self):

        test_file1 = path_utils.concat_path(self.second_repo, "test_file1.txt")
        if not create_and_write_file.create_file_contents(test_file1, "test-contents1"):
            self.fail("Failed creating test file %s" % test_file1)

        test_file2 = path_utils.concat_path(self.second_repo, "test_file2.txt")
        if not create_and_write_file.create_file_contents(test_file2, "test-contents2"):
            self.fail("Failed creating test file %s" % test_file2)

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test commit msg")
        self.assertTrue(v)

        with open(test_file1, "a") as f:
            f.write("latest content1")

        with open(test_file2, "a") as f:
            f.write("latest content2")

        v, r = git_wrapper.diff(self.second_repo)
        self.assertTrue(v)
        self.assertTrue("+test-contents1latest content1" in r)
        self.assertTrue("+test-contents2latest content2" in r)

    def testDiff2(self):

        test_file1 = path_utils.concat_path(self.second_repo, "test_file1.txt")
        if not create_and_write_file.create_file_contents(test_file1, "test-contents1"):
            self.fail("Failed creating test file %s" % test_file1)

        test_file2 = path_utils.concat_path(self.second_repo, "test_file2.txt")
        if not create_and_write_file.create_file_contents(test_file2, "test-contents2"):
            self.fail("Failed creating test file %s" % test_file2)

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test commit msg")
        self.assertTrue(v)

        with open(test_file1, "a") as f:
            f.write("latest content1")

        with open(test_file2, "a") as f:
            f.write("latest content2")

        v, r = git_wrapper.diff(self.second_repo, [test_file1])
        self.assertTrue(v)
        self.assertTrue("+test-contents1latest content1" in r)
        self.assertFalse("+test-contents2latest content2" in r)

    def testDiff3(self):

        test_file1 = path_utils.concat_path(self.second_repo, "test_file1.txt")
        if not create_and_write_file.create_file_contents(test_file1, "test-contents1"):
            self.fail("Failed creating test file %s" % test_file1)

        test_file2 = path_utils.concat_path(self.second_repo, "test_file2.txt")
        if not create_and_write_file.create_file_contents(test_file2, "test-contents2"):
            self.fail("Failed creating test file %s" % test_file2)

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test commit msg")
        self.assertTrue(v)

        with open(test_file1, "a") as f:
            f.write("latest content1")

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        with open(test_file2, "a") as f:
            f.write("latest content2")

        v, r = git_wrapper.diff(self.second_repo)
        self.assertTrue(v)
        self.assertFalse("+test-contents1latest content1" in r)
        self.assertTrue("+test-contents2latest content2" in r)

    def testDiffFail1(self):
        v, r = git_wrapper.diff(self.second_repo, "string")
        self.assertFalse(v)
        self.assertEqual(r, "git_wrapper.diff: file_list must be a list")

    def testDiffFail2(self):
        v, r = git_wrapper.diff(self.second_repo, 123)
        self.assertFalse(v)
        self.assertEqual(r, "git_wrapper.diff: file_list must be a list")

    def testDiffCached1(self):

        test_file1 = path_utils.concat_path(self.second_repo, "test_file1.txt")
        if not create_and_write_file.create_file_contents(test_file1, "test-contents1"):
            self.fail("Failed creating test file %s" % test_file1)

        test_file2 = path_utils.concat_path(self.second_repo, "test_file2.txt")
        if not create_and_write_file.create_file_contents(test_file2, "test-contents2"):
            self.fail("Failed creating test file %s" % test_file2)

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test commit msg")
        self.assertTrue(v)

        with open(test_file1, "a") as f:
            f.write("latest content1")

        with open(test_file2, "a") as f:
            f.write("latest content2")

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.diff_cached(self.second_repo)
        self.assertTrue(v)
        self.assertTrue("+test-contents1latest content1" in r)
        self.assertTrue("+test-contents2latest content2" in r)

    def testDiffCached2(self):

        test_file1 = path_utils.concat_path(self.second_repo, "test_file1.txt")
        if not create_and_write_file.create_file_contents(test_file1, "test-contents1"):
            self.fail("Failed creating test file %s" % test_file1)

        test_file2 = path_utils.concat_path(self.second_repo, "test_file2.txt")
        if not create_and_write_file.create_file_contents(test_file2, "test-contents2"):
            self.fail("Failed creating test file %s" % test_file2)

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test commit msg")
        self.assertTrue(v)

        with open(test_file1, "a") as f:
            f.write("latest content1")

        with open(test_file2, "a") as f:
            f.write("latest content2")

        v, r = git_wrapper.diff_cached(self.second_repo)
        self.assertTrue(v)
        self.assertFalse("+test-contents1latest content1" in r)
        self.assertFalse("+test-contents2latest content2" in r)

    def testDiffCached3(self):

        test_file1 = path_utils.concat_path(self.second_repo, "test_file1.txt")
        if not create_and_write_file.create_file_contents(test_file1, "test-contents1"):
            self.fail("Failed creating test file %s" % test_file1)

        test_file2 = path_utils.concat_path(self.second_repo, "test_file2.txt")
        if not create_and_write_file.create_file_contents(test_file2, "test-contents2"):
            self.fail("Failed creating test file %s" % test_file2)

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test commit msg")
        self.assertTrue(v)

        with open(test_file1, "a") as f:
            f.write("latest content1")

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        with open(test_file2, "a") as f:
            f.write("latest content2")

        v, r = git_wrapper.diff_cached(self.second_repo)
        self.assertTrue(v)
        self.assertTrue("+test-contents1latest content1" in r)
        self.assertFalse("+test-contents2latest content2" in r)

    def testDiffCachedFail1(self):
        v, r = git_wrapper.diff_cached(self.second_repo, "string")
        self.assertFalse(v)
        self.assertEqual(r, "git_wrapper.diff_cached: file_list must be a list")

    def testDiffCachedFail2(self):
        v, r = git_wrapper.diff_cached(self.second_repo, 123)
        self.assertFalse(v)
        self.assertEqual(r, "git_wrapper.diff_cached: file_list must be a list")

    def testRevParseHead(self):

        test_file = path_utils.concat_path(self.second_repo, "test_file.txt")
        if not create_and_write_file.create_file_contents(test_file, "test-contents"):
            self.fail("Failed creating test file %s" % test_file)

        v, r = git_wrapper.stage(self.second_repo, [test_file])
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test commit msg")
        self.assertTrue(v)

        v, r = git_wrapper.rev_parse_head(self.second_repo)
        self.assertTrue(v)
        self.assertTrue( (len(r) >= (40 + len(os.linesep))) and is_hex_string(r))

    def testRevParseIsBareRepo(self):

        v, r = git_wrapper.rev_parse_is_bare_repo(self.first_repo)
        self.assertTrue(v)
        self.assertTrue("true" in r)
        v, r = git_wrapper.rev_parse_is_bare_repo(self.second_repo)
        self.assertTrue(v)
        self.assertTrue("false" in r)

    def testRevParseIsInsideWorkTree(self):

        v, r = git_wrapper.rev_parse_is_inside_work_tree(self.first_repo)
        self.assertTrue(v)
        self.assertTrue("false" in r)

        v, r = git_wrapper.rev_parse_is_inside_work_tree(self.second_repo)
        self.assertTrue(v)
        self.assertTrue("true" in r)

    def testRevParseAbsoluteGitDir(self):

        v, r = git_wrapper.rev_parse_absolute_git_dir(self.first_repo)
        self.assertTrue(v)
        self.assertEqual(self.first_repo, r)

        first_objects = path_utils.concat_path(self.first_repo, "objects")
        self.assertTrue(os.path.exists(first_objects))
        v, r = git_wrapper.rev_parse_absolute_git_dir(first_objects)
        self.assertTrue(v)
        self.assertEqual(self.first_repo, r)

        v, r = git_wrapper.rev_parse_absolute_git_dir(self.second_repo)
        self.assertTrue(v)
        self.assertNotEqual(self.second_repo, r)

        v, r = git_wrapper.rev_parse_absolute_git_dir(self.third_repo)
        self.assertTrue(v)
        self.assertEqual(self.third_repo, r)

    def testLsFiles1(self):

        test_file1 = path_utils.concat_path(self.second_repo, "test_file1.txt")
        if not create_and_write_file.create_file_contents(test_file1, "test-contents1"):
            self.fail("Failed creating test file %s" % test_file1)

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test commit msg")
        self.assertTrue(v)

        test_file2 = path_utils.concat_path(self.second_repo, "test_file2.txt")
        if not create_and_write_file.create_file_contents(test_file2, "test-contents2"):
            self.fail("Failed creating test file %s" % test_file2)

        test_file3 = path_utils.concat_path(self.second_repo, "test_file3.txt")
        if not create_and_write_file.create_file_contents(test_file3, "test-contents3"):
            self.fail("Failed creating test file %s" % test_file3)

        v, r = git_wrapper.ls_files(self.second_repo)
        self.assertTrue(v)
        self.assertFalse( path_utils.basename_filtered(test_file1) in r)
        self.assertTrue( path_utils.basename_filtered(test_file2) in r)
        self.assertTrue( path_utils.basename_filtered(test_file3) in r)

        v, r = git_wrapper.stage(self.second_repo, [test_file3])
        self.assertTrue(v)

        v, r = git_wrapper.ls_files(self.second_repo)
        self.assertTrue(v)
        self.assertFalse( path_utils.basename_filtered(test_file1) in r)
        self.assertTrue( path_utils.basename_filtered(test_file2) in r)
        self.assertFalse( path_utils.basename_filtered(test_file3) in r)

    def testLsFiles2(self):

        test_file = path_utils.concat_path(self.second_repo, "test_file.txt")
        if not create_and_write_file.create_file_contents(test_file, "test-contents"):
            self.fail("Failed creating test file %s" % test_file)

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.ls_files(self.second_repo)
        self.assertTrue(v)
        self.assertEqual(r, "")

    def testStash_and_StashList(self):

        test_file = path_utils.concat_path(self.second_repo, "test_file.txt")
        if not create_and_write_file.create_file_contents(test_file, "test-contents"):
            self.fail("Failed creating test file %s" % test_file)

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "stash-list test commit msg")
        self.assertTrue(v)

        with open(test_file, "a") as f:
            f.write("latest content")

        v, r = git_wrapper.stash(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.stash_list(self.second_repo)
        self.assertTrue(v)
        self.assertEqual( len(r.strip().split(os.linesep)), 1 )
        self.assertTrue( "stash@{0}: WIP on master:" in r)
        self.assertTrue( "stash-list test commit msg" in r)

        with open(test_file, "a") as f:
            f.write("yet more stuff")

        v, r = git_wrapper.stash(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.stash_list(self.second_repo)
        self.assertTrue(v)
        self.assertEqual( len(r.strip().split(os.linesep)), 2 )
        self.assertTrue( "stash@{0}: WIP on master:" in r)
        self.assertTrue( "stash@{1}: WIP on master:" in r)
        self.assertTrue( "stash-list test commit msg" in r)

    def testStash_and_StashShow(self):

        test_file = path_utils.concat_path(self.second_repo, "test_file.txt")
        if not create_and_write_file.create_file_contents(test_file, "test-contents"):
            self.fail("Failed creating test file %s" % test_file)

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "stash test commit msg")
        self.assertTrue(v)

        v, r = git_wrapper.stash_show(self.second_repo, "stash@{0}")
        self.assertFalse(v)

        with open(test_file, "a") as f:
            f.write("latest content, stash show 1")

        v, r = git_wrapper.stash(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.stash_show(self.second_repo, "stash@{0}")
        self.assertTrue(v)
        self.assertTrue("+test-contentslatest content, stash show 1" in r)

        with open(test_file, "a") as f:
            f.write("latest content, stash show 2")

        v, r = git_wrapper.stash(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.stash_show(self.second_repo, "stash@{0}")
        self.assertTrue(v)
        self.assertTrue("+test-contentslatest content, stash show 2" in r)
        self.assertFalse("+test-contentslatest content, stash show 1" in r)

        v, r = git_wrapper.stash_show(self.second_repo, "stash@{1}")
        self.assertTrue(v)
        self.assertFalse("+test-contentslatest content, stash show 2" in r)
        self.assertTrue("+test-contentslatest content, stash show 1" in r)

    def testStash_and_StashClear(self):

        test_file = path_utils.concat_path(self.second_repo, "test_file.txt")
        if not create_and_write_file.create_file_contents(test_file, "test-contents"):
            self.fail("Failed creating test file %s" % test_file)

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "stash test commit msg")
        self.assertTrue(v)

        v, r = git_wrapper.stash_show(self.second_repo, "stash@{0}")
        self.assertFalse(v)

        with open(test_file, "a") as f:
            f.write("latest content, stash show 1")

        v, r = git_wrapper.stash(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.stash_show(self.second_repo, "stash@{0}")
        self.assertTrue(v)
        self.assertTrue("+test-contentslatest content, stash show 1" in r)

        with open(test_file, "a") as f:
            f.write("latest content, stash show 2")

        v, r = git_wrapper.stash(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.stash_list(self.second_repo)
        self.assertTrue(v)
        self.assertEqual( len(r.strip().split(os.linesep)), 2 )

        v, r = git_wrapper.stash_show(self.second_repo, "stash@{0}")
        self.assertTrue(v)
        self.assertTrue("+test-contentslatest content, stash show 2" in r)
        self.assertFalse("+test-contentslatest content, stash show 1" in r)

        v, r = git_wrapper.stash_show(self.second_repo, "stash@{1}")
        self.assertTrue(v)
        self.assertFalse("+test-contentslatest content, stash show 2" in r)
        self.assertTrue("+test-contentslatest content, stash show 1" in r)

        v, r = git_wrapper.stash_clear(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.stash_list(self.second_repo)
        self.assertTrue(v)
        self.assertEqual(len(r), 0)

    def testStash_and_StashDrop(self):

        test_file = path_utils.concat_path(self.second_repo, "test_file.txt")
        if not create_and_write_file.create_file_contents(test_file, "test-contents"):
            self.fail("Failed creating test file %s" % test_file)

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "stash test commit msg")
        self.assertTrue(v)

        v, r = git_wrapper.stash_show(self.second_repo, "stash@{0}")
        self.assertFalse(v)

        with open(test_file, "a") as f:
            f.write("latest content, stash show 1")

        v, r = git_wrapper.stash(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.stash_show(self.second_repo, "stash@{0}")
        self.assertTrue(v)
        self.assertTrue("+test-contentslatest content, stash show 1" in r)

        with open(test_file, "a") as f:
            f.write("latest content, stash show 2")

        v, r = git_wrapper.stash(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.stash_list(self.second_repo)
        self.assertTrue(v)
        self.assertEqual( len(r.strip().split(os.linesep)), 2 )

        v, r = git_wrapper.stash_show(self.second_repo, "stash@{0}")
        self.assertTrue(v)
        self.assertTrue("+test-contentslatest content, stash show 2" in r)
        self.assertFalse("+test-contentslatest content, stash show 1" in r)

        v, r = git_wrapper.stash_show(self.second_repo, "stash@{1}")
        self.assertTrue(v)
        self.assertFalse("+test-contentslatest content, stash show 2" in r)
        self.assertTrue("+test-contentslatest content, stash show 1" in r)

        v, r = git_wrapper.stash_drop(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.stash_list(self.second_repo)
        self.assertTrue(v)
        self.assertEqual( len(r.strip().split(os.linesep)), 1 )

        v, r = git_wrapper.stash_show(self.second_repo, "stash@{0}")
        self.assertTrue(v)
        self.assertTrue("+test-contentslatest content, stash show 1" in r)

        v, r = git_wrapper.stash_drop(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.stash_list(self.second_repo)
        self.assertTrue(v)
        self.assertEqual( len(r), 0)

    def testLogOneline(self):

        test_file = path_utils.concat_path(self.second_repo, "test_file.txt")
        if not create_and_write_file.create_file_contents(test_file, "test-contents"):
            self.fail("Failed creating test file %s" % test_file)

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "log-oneline test commit msg 1")
        self.assertTrue(v)

        v, r = git_wrapper.log_oneline(self.second_repo)
        self.assertTrue(v)
        self.assertEqual( len(r.strip().split(os.linesep)), 1 )
        self.assertTrue("log-oneline test commit msg 1" in r)

        with open(test_file, "a") as f:
            f.write("latest content, log-oneline")

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "log-oneline test commit msg 2")
        self.assertTrue(v)

        v, r = git_wrapper.log_oneline(self.second_repo)
        self.assertTrue(v)
        self.assertEqual( len(r.strip().split(os.linesep)), 2 )
        self.assertTrue("log-oneline test commit msg 1" in r)
        self.assertTrue("log-oneline test commit msg 2" in r)

        v, r = git_wrapper.log_oneline(self.second_repo, 1)
        self.assertTrue(v)
        self.assertEqual( len(r.strip().split(os.linesep)), 1 )
        self.assertFalse("log-oneline test commit msg 1" in r)
        self.assertTrue("log-oneline test commit msg 2" in r)

    def testLog(self):

        test_file = path_utils.concat_path(self.second_repo, "test_file.txt")
        if not create_and_write_file.create_file_contents(test_file, "test-contents"):
            self.fail("Failed creating test file %s" % test_file)

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "log test commit msg 1")
        self.assertTrue(v)

        v, r = git_wrapper.log(self.second_repo)

        self.assertTrue(v)
        self.assertEqual( len(r.strip().split(os.linesep)), 5 )
        self.assertTrue("log test commit msg 1" in r)

        with open(test_file, "a") as f:
            f.write("latest content, log")

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "log test commit msg 2")
        self.assertTrue(v)

        v, r = git_wrapper.log(self.second_repo)
        self.assertTrue(v)
        self.assertEqual( len(r.strip().split(os.linesep)), 11 )
        self.assertTrue("log test commit msg 1" in r)
        self.assertTrue("log test commit msg 2" in r)

        v, r = git_wrapper.log(self.second_repo, 1)
        self.assertTrue(v)
        self.assertEqual( len(r.strip().split(os.linesep)), 5 )
        self.assertFalse("log test commit msg 1" in r)
        self.assertTrue("log test commit msg 2" in r)

    def testShow(self):

        test_file = path_utils.concat_path(self.second_repo, "test_file.txt")
        if not create_and_write_file.create_file_contents(test_file, "test-show, test contents"):
            self.fail("Failed creating test file %s" % test_file)

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test-show, test commit msg")
        self.assertTrue(v)

        v, r = git_wrapper.log_oneline(self.second_repo)
        self.assertTrue(v)
        p = r.find(" ")
        if p == -1:
            self.fail("Failed retrieving commit id, testShow")
        commit_id = r[:p]

        v, r = git_wrapper.show(self.second_repo, commit_id)
        self.assertTrue(v)
        contents_first_call = r
        self.assertTrue("test-show, test contents" in contents_first_call)

        v, r = git_wrapper.show(self.second_repo)
        self.assertTrue(v)
        contents_second_call = r
        self.assertEqual(contents_first_call, contents_second_call)

    def testStatus(self):

        test_file1 = path_utils.concat_path(self.second_repo, "test_file1.txt")
        if not create_and_write_file.create_file_contents(test_file1, "test-status, test contents"):
            self.fail("Failed creating test file %s" % test_file1)

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test-status, test commit msg")
        self.assertTrue(v)

        v, r = git_wrapper.status(self.second_repo)
        self.assertTrue(v)
        self.assertEqual("", r)

        test_file2 = path_utils.concat_path(self.second_repo, "test_file2.txt")
        if not create_and_write_file.create_file_contents(test_file2, "test-contents2"):
            self.fail("Failed creating test file %s" % test_file2)

        v, r = git_wrapper.status(self.second_repo)
        self.assertTrue(v)
        self.assertTrue("?? test_file2.txt" in r)

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.status(self.second_repo)
        self.assertTrue(v)
        self.assertTrue("A  test_file2.txt" in r)

    def testStatusSimple(self):

        test_file1 = path_utils.concat_path(self.second_repo, "test_file1.txt")
        if not create_and_write_file.create_file_contents(test_file1, "test-status-simple, test contents"):
            self.fail("Failed creating test file %s" % test_file1)

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test-status-simple, test commit msg")
        self.assertTrue(v)

        v, r = git_wrapper.status_simple(self.second_repo)
        self.assertTrue(v)
        self.assertEqual("", r)

        test_file2 = path_utils.concat_path(self.second_repo, "test_file2.txt")
        if not create_and_write_file.create_file_contents(test_file2, "test-contents2"):
            self.fail("Failed creating test file %s" % test_file2)

        v, r = git_wrapper.status_simple(self.second_repo)
        self.assertTrue(v)
        self.assertTrue("?? test_file2.txt" in r)

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.status_simple(self.second_repo)
        self.assertTrue(v)
        self.assertTrue("A  test_file2.txt" in r)

    def testRemoteList_and_RemoteAdd_and_ChangeUrl(self):

        test_file = path_utils.concat_path(self.second_repo, "test_file.txt")
        if not create_and_write_file.create_file_contents(test_file, "test-remote, test contents"):
            self.fail("Failed creating test file %s" % test_file)

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test-remote, test commit msg")
        self.assertTrue(v)

        v, r = git_wrapper.remote_list(self.second_repo)
        self.assertTrue(v)
        self.assertTrue( ("origin\t%s (fetch)" % self.first_repo) in r )
        self.assertTrue( ("origin\t%s (push)" % self.first_repo) in r )

        third_repo = path_utils.concat_path(self.test_dir, "third")
        v, r = git_wrapper.remote_add(self.second_repo, "new-remote", third_repo)
        self.assertTrue(v)

        v, r = git_wrapper.remote_list(self.second_repo)
        self.assertTrue(v)
        self.assertTrue( ("new-remote\t%s (fetch)" % third_repo) in r )
        self.assertTrue( ("new-remote\t%s (push)" % third_repo) in r )

        fourth_repo = path_utils.concat_path(self.test_dir, "fourth")
        v, r = git_wrapper.remote_change_url(self.second_repo, "nonexistent-remote", fourth_repo)
        self.assertFalse(v)

        v, r = git_wrapper.remote_change_url(self.second_repo, "new-remote", fourth_repo)
        self.assertTrue(v)

        v, r = git_wrapper.remote_list(self.second_repo)
        self.assertTrue(v)
        self.assertTrue( ("new-remote\t%s (fetch)" % fourth_repo) in r )
        self.assertTrue( ("new-remote\t%s (push)" % fourth_repo) in r )

    def testBranch(self):

        v, r = git_wrapper.branch(self.second_repo)
        self.assertTrue(v)
        self.assertEqual("", r.strip())

        test_file = path_utils.concat_path(self.second_repo, "test_file.txt")
        if not create_and_write_file.create_file_contents(test_file, "test-branch, test contents"):
            self.fail("Failed creating test file %s" % test_file)

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test-branch, test commit msg")
        self.assertTrue(v)

        v, r = git_wrapper.branch(self.second_repo)
        self.assertTrue(v)
        self.assertTrue("* master" in r)

    def testBranchCreateAndSwitch(self):

        v, r = git_wrapper.branch(self.second_repo)
        self.assertTrue(v)
        self.assertEqual("", r.strip())

        test_file = path_utils.concat_path(self.second_repo, "test_file.txt")
        if not create_and_write_file.create_file_contents(test_file, "test-branch-create-and-switch, test contents"):
            self.fail("Failed creating test file %s" % test_file)

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test-branch-create-and-switch, test commit msg")
        self.assertTrue(v)

        v, r = git_wrapper.branch_create_and_switch(self.second_repo, "offline")
        self.assertTrue(v)

        v, r = git_wrapper.branch(self.second_repo)
        self.assertTrue(v)
        self.assertTrue("* offline" in r)

    def testPull_and_PullDefault(self):

        test_file1 = path_utils.concat_path(self.second_repo, "test_file1.txt")
        if not create_and_write_file.create_file_contents(test_file1, "test-pull, test contents"):
            self.fail("Failed creating test file %s" % test_file1)

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test-pull, test commit msg 1")
        self.assertTrue(v)

        third_repo = path_utils.concat_path(self.test_dir, "third")
        v, r = git_wrapper.clone(self.second_repo, third_repo)
        self.assertTrue(v)

        test_file2 = path_utils.concat_path(self.second_repo, "test_file2.txt")
        if not create_and_write_file.create_file_contents(test_file2, "test-pull, test contents"):
            self.fail("Failed creating test file %s" % test_file2)

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test-pull, test commit msg 2")
        self.assertTrue(v)

        file2_third_repo = path_utils.concat_path(third_repo, path_utils.basename_filtered(test_file2))
        v, r = git_wrapper.pull(third_repo, "origin", "master")
        self.assertTrue(v)
        self.assertTrue(os.path.exists(file2_third_repo))

        test_file3 = path_utils.concat_path(self.second_repo, "test_file3.txt")
        if not create_and_write_file.create_file_contents(test_file3, "test-pull, test contents"):
            self.fail("Failed creating test file %s" % test_file3)

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test-pull, test commit msg 3")
        self.assertTrue(v)

        file3_third_repo = path_utils.concat_path(third_repo, path_utils.basename_filtered(test_file3))
        v, r = git_wrapper.pull_default(third_repo)
        self.assertTrue(v)
        self.assertTrue(os.path.exists(file3_third_repo))

    def testPush(self):

        test_file1_secondrepo = path_utils.concat_path(self.second_repo, "test_file1.txt")
        if not create_and_write_file.create_file_contents(test_file1_secondrepo, "test-push, test contents 1"):
            self.fail("Failed creating test file %s" % test_file1_secondrepo)

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test-push, test commit msg 1")
        self.assertTrue(v)

        v, r = git_wrapper.push(self.second_repo, "origin", "master")
        self.assertTrue(v)

        third_repo = path_utils.concat_path(self.test_dir, "third")
        test_file1_thirdrepo = path_utils.concat_path(third_repo, "test_file1.txt")
        v, r = git_wrapper.clone(self.first_repo, third_repo)
        self.assertTrue(v)
        self.assertTrue( os.path.exists(test_file1_thirdrepo) )

    def testPushDefault(self):

        test_file1_secondrepo = path_utils.concat_path(self.second_repo, "test_file1.txt")
        if not create_and_write_file.create_file_contents(test_file1_secondrepo, "test-push-default, test contents 1"):
            self.fail("Failed creating test file %s" % test_file1_secondrepo)

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test-push-default, test commit msg 1")
        self.assertTrue(v)

        v, r = git_wrapper.push_default(self.second_repo)
        self.assertTrue(v)

        third_repo = path_utils.concat_path(self.test_dir, "third")
        test_file1_thirdrepo = path_utils.concat_path(third_repo, "test_file1.txt")
        v, r = git_wrapper.clone(self.first_repo, third_repo)
        self.assertTrue(v)
        self.assertTrue( os.path.exists(test_file1_thirdrepo) )

    def testFetchAll_and_Merge(self):

        test_file1_secondrepo = path_utils.concat_path(self.second_repo, "test_file1.txt")
        if not create_and_write_file.create_file_contents(test_file1_secondrepo, "test-fetch-all, test contents 1"):
            self.fail("Failed creating test file %s" % test_file1_secondrepo)

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test-fetch-all, test commit msg 1")
        self.assertTrue(v)

        v, r = git_wrapper.push(self.second_repo, "origin", "master")
        self.assertTrue(v)

        # clone third as a sibling to second
        third_repo = path_utils.concat_path(self.test_dir, "third")
        v, r = git_wrapper.clone(self.first_repo, third_repo)
        self.assertTrue(v)

        # clone fourth as a child of second and third
        fourth_repo = path_utils.concat_path(self.test_dir, "fourth")
        v, r = git_wrapper.clone(third_repo, fourth_repo)
        self.assertTrue(v)

        v, r = git_wrapper.remote_add(fourth_repo, "second-remote", self.second_repo)
        self.assertTrue(v)

        # add some extra content into second
        test_file2_secondrepo = path_utils.concat_path(self.second_repo, "test_file2.txt")
        if not create_and_write_file.create_file_contents(test_file2_secondrepo, "test-fetch-all, test contents 2"):
            self.fail("Failed creating test file %s" % test_file2_secondrepo)

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test-fetch-all, test commit msg 2")
        self.assertTrue(v)

        # add some extra content into third
        test_file3_thirdrepo = path_utils.concat_path(third_repo, "test_file3.txt")
        if not create_and_write_file.create_file_contents(test_file3_thirdrepo, "test-fetch-all, test contents 3"):
            self.fail("Failed creating test file %s" % test_file3_thirdrepo)

        v, r = git_wrapper.stage(third_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(third_repo, "test-fetch-all, test commit msg 3")
        self.assertTrue(v)

        # fetch second's and third's changes into fourth
        v, r = git_wrapper.fetch_all(fourth_repo)
        self.assertTrue(v)

        test_file2_fourthrepo = path_utils.concat_path(fourth_repo, "test_file2.txt")
        test_file3_fourthrepo = path_utils.concat_path(fourth_repo, "test_file3.txt")

        # merge second onto fourth
        v, r = git_wrapper.merge(fourth_repo, "second-remote", "master")
        self.assertTrue(v)
        self.assertTrue( os.path.exists( test_file2_fourthrepo ) )
        self.assertFalse( os.path.exists( test_file3_fourthrepo ) )

        # merge third onto fourth
        v, r = git_wrapper.merge(fourth_repo, "origin", "master")
        self.assertTrue(v)
        self.assertTrue( os.path.exists( test_file2_fourthrepo ) )
        self.assertTrue( os.path.exists( test_file3_fourthrepo ) )

    def testFetchMultipleFail1(self):

        v, r = git_wrapper.fetch_multiple(self.second_repo, "a-string")
        self.assertFalse(v)
        self.assertEqual(r, "git_wrapper.fetch_multiple: remotes must be a list")

    def testFetchMultipleFail2(self):

        v, r = git_wrapper.fetch_multiple(self.second_repo, None)
        self.assertFalse(v)
        self.assertEqual(r, "git_wrapper.fetch_multiple: remotes can't be None")

    def testFetchMultiple_and_Merge(self):

        test_file1_secondrepo = path_utils.concat_path(self.second_repo, "test_file1.txt")
        if not create_and_write_file.create_file_contents(test_file1_secondrepo, "test-fetch-all, test contents 1"):
            self.fail("Failed creating test file %s" % test_file1_secondrepo)

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test-fetch-all, test commit msg 1")
        self.assertTrue(v)

        v, r = git_wrapper.push(self.second_repo, "origin", "master")
        self.assertTrue(v)

        # clone third as a sibling to second
        third_repo = path_utils.concat_path(self.test_dir, "third")
        v, r = git_wrapper.clone(self.first_repo, third_repo)
        self.assertTrue(v)

        # clone fourth as a sibling to second and third
        fourth_repo = path_utils.concat_path(self.test_dir, "fourth")
        v, r = git_wrapper.clone(self.first_repo, fourth_repo)
        self.assertTrue(v)

        # clone fifth as a child of second and third and fourth
        fifth_repo = path_utils.concat_path(self.test_dir, "fifth")
        v, r = git_wrapper.clone(fourth_repo, fifth_repo)
        self.assertTrue(v)

        v, r = git_wrapper.remote_add(fifth_repo, "second-remote", self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.remote_add(fifth_repo, "third-remote", third_repo)
        self.assertTrue(v)

        # add some extra content into second
        test_file2_secondrepo = path_utils.concat_path(self.second_repo, "test_file2.txt")
        if not create_and_write_file.create_file_contents(test_file2_secondrepo, "test-fetch-all, test contents 2"):
            self.fail("Failed creating test file %s" % test_file2_secondrepo)

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test-fetch-all, test commit msg 2")
        self.assertTrue(v)

        # add some extra content into third
        test_file3_thirdrepo = path_utils.concat_path(third_repo, "test_file3.txt")
        if not create_and_write_file.create_file_contents(test_file3_thirdrepo, "test-fetch-all, test contents 3"):
            self.fail("Failed creating test file %s" % test_file3_thirdrepo)

        v, r = git_wrapper.stage(third_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(third_repo, "test-fetch-all, test commit msg 3")
        self.assertTrue(v)

        # add some extra content into fourth
        test_file4_fourthrepo = path_utils.concat_path(fourth_repo, "test_file4.txt")
        if not create_and_write_file.create_file_contents(test_file4_fourthrepo, "test-fetch-all, test contents 4"):
            self.fail("Failed creating test file %s" % test_file4_fourthrepo)

        v, r = git_wrapper.stage(fourth_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(fourth_repo, "test-fetch-all, test commit msg 4")
        self.assertTrue(v)

        # fetch second's and third's and fourth's changes into fifth
        v, r = git_wrapper.fetch_multiple(fifth_repo, ["second-remote", "third-remote"])
        self.assertTrue(v)

        test_file2_fifthrepo = path_utils.concat_path(fifth_repo, "test_file2.txt")
        test_file3_fifthrepo = path_utils.concat_path(fifth_repo, "test_file3.txt")
        test_file4_fifthrepo = path_utils.concat_path(fifth_repo, "test_file4.txt")

        # merge second onto fourth
        v, r = git_wrapper.merge(fifth_repo, "second-remote", "master")
        self.assertTrue(v)
        self.assertTrue( os.path.exists( test_file2_fifthrepo ) )
        self.assertFalse( os.path.exists( test_file3_fifthrepo ) )
        self.assertFalse( os.path.exists( test_file4_fifthrepo ) )

        v, r = git_wrapper.merge(fifth_repo, "third-remote", "master")
        self.assertTrue(v)
        self.assertTrue( os.path.exists( test_file2_fifthrepo ) )
        self.assertTrue( os.path.exists( test_file3_fifthrepo ) )
        self.assertFalse( os.path.exists( test_file4_fifthrepo ) )

        v, r = git_wrapper.merge(fifth_repo, "origin", "master")
        self.assertTrue(v)
        self.assertTrue( os.path.exists( test_file2_fifthrepo ) )
        self.assertTrue( os.path.exists( test_file3_fifthrepo ) )
        self.assertFalse( os.path.exists( test_file4_fifthrepo ) )

        v, r = git_wrapper.fetch_multiple(fifth_repo, ["origin"])
        self.assertTrue(v)

        v, r = git_wrapper.merge(fifth_repo, "origin", "master")
        self.assertTrue(v)
        self.assertTrue( os.path.exists( test_file2_fifthrepo ) )
        self.assertTrue( os.path.exists( test_file3_fifthrepo ) )
        self.assertTrue( os.path.exists( test_file4_fifthrepo ) )

    def testSubmoduleAdd(self):

        test_file1_secondrepo = path_utils.concat_path(self.second_repo, "test_file1.txt")
        if not create_and_write_file.create_file_contents(test_file1_secondrepo, "test-submodule-add, test contents 1"):
            self.fail("Failed creating test file %s" % test_file1_secondrepo)

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test-submodule-add, test commit msg 1")
        self.assertTrue(v)

        # init third repo as an independent
        third_repo = path_utils.concat_path(self.test_dir, "third")
        v, r = git_wrapper.init(self.test_dir, "third", False)
        self.assertTrue(v)

        test_file2_thirdrepo = path_utils.concat_path(third_repo, "test_file2.txt")
        if not create_and_write_file.create_file_contents(test_file2_thirdrepo, "test-submodule-add, test contents 2"):
            self.fail("Failed creating test file %s" % test_file2_thirdrepo)

        v, r = git_wrapper.stage(third_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(third_repo, "test-submodule-add, test commit msg 2")
        self.assertTrue(v)

        # add third as a submodule of second
        v, r = git_wrapper.submodule_add(third_repo, self.second_repo)
        self.assertTrue(v)

        third_inside_second = path_utils.concat_path(self.second_repo,  path_utils.basename_filtered(third_repo) )
        self.assertTrue( os.path.exists(third_inside_second) )
        test_file2_thirdrepo_inside_second = path_utils.concat_path(third_inside_second, path_utils.basename_filtered(test_file2_thirdrepo))
        self.assertTrue( os.path.exists(test_file2_thirdrepo_inside_second) )

        # add some stuff to third, the standalone copy
        test_file3_thirdrepo = path_utils.concat_path(third_repo, "test_file3.txt")
        if not create_and_write_file.create_file_contents(test_file3_thirdrepo, "test-submodule-add, test contents 3"):
            self.fail("Failed creating test file %s" % test_file3_thirdrepo)

        v, r = git_wrapper.stage(third_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(third_repo, "test-submodule-add, test commit msg 3")
        self.assertTrue(v)

        # then pull on third, the submodule copy
        v, r = git_wrapper.pull_default(third_inside_second)
        self.assertTrue(v)
        test_file3_thirdrepo_inside_second = path_utils.concat_path(third_inside_second, path_utils.basename_filtered(test_file3_thirdrepo))
        self.assertTrue( os.path.exists(test_file3_thirdrepo_inside_second) )

    def testApplyPatchFromHead(self):

        test_file1 = path_utils.concat_path(self.second_repo, "test_file1.txt")
        if not create_and_write_file.create_file_contents(test_file1, "test-contents1"):
            self.fail("Failed creating test file %s" % test_file1)

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test commit msg1")
        self.assertTrue(v)

        test_file2 = path_utils.concat_path(self.second_repo, "test_file2.txt")
        if not create_and_write_file.create_file_contents(test_file2, "test-contents2"):
            self.fail("Failed creating test file %s" % test_file2)

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test commit msg2")
        self.assertTrue(v)

        fourth_repo = path_utils.concat_path(self.test_dir, "fourth")
        v, r = git_wrapper.clone(self.second_repo, fourth_repo)
        self.assertTrue(v)

        test_file2_fourthrepo = path_utils.concat_path(fourth_repo, "test_file2.txt")

        with open(test_file2_fourthrepo, "a") as f:
            f.write("latest content2")

        v, r = collect_git_patch.collect_git_patch_head(fourth_repo, self.storage_path)
        self.assertTrue(v)
        generated_patch_file = r
        self.assertTrue( os.path.exists(generated_patch_file) )

        v, r = git_wrapper.status_simple(self.second_repo)
        self.assertTrue(v)
        self.assertEqual(r.strip(), "")

        v, r = git_wrapper.apply(self.second_repo, generated_patch_file)
        self.assertTrue(v)

        v, r = git_wrapper.status_simple(self.second_repo)
        self.assertTrue(v)
        self.assertTrue("test_file2.txt" in r.strip())

    def testApplyPatchFromHeadStaged(self):

        test_file1 = path_utils.concat_path(self.second_repo, "test_file1.txt")
        if not create_and_write_file.create_file_contents(test_file1, "test-contents1"):
            self.fail("Failed creating test file %s" % test_file1)

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test commit msg1")
        self.assertTrue(v)

        test_file2 = path_utils.concat_path(self.second_repo, "test_file2.txt")
        if not create_and_write_file.create_file_contents(test_file2, "test-contents2"):
            self.fail("Failed creating test file %s" % test_file2)

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test commit msg2")
        self.assertTrue(v)

        fourth_repo = path_utils.concat_path(self.test_dir, "fourth")
        v, r = git_wrapper.clone(self.second_repo, fourth_repo)
        self.assertTrue(v)

        test_file2_fourthrepo = path_utils.concat_path(fourth_repo, "test_file2.txt")

        with open(test_file2_fourthrepo, "a") as f:
            f.write("latest content2")

        v, r = git_wrapper.stage(fourth_repo)
        self.assertTrue(v)

        v, r = collect_git_patch.collect_git_patch_staged(fourth_repo, self.storage_path)
        self.assertTrue(v)
        generated_patch_file = r
        self.assertTrue( os.path.exists(generated_patch_file) )

        v, r = git_wrapper.status_simple(self.second_repo)
        self.assertTrue(v)
        self.assertEqual(r.strip(), "")

        v, r = git_wrapper.apply(self.second_repo, generated_patch_file)
        self.assertTrue(v)

        v, r = git_wrapper.status_simple(self.second_repo)
        self.assertTrue(v)
        self.assertTrue("test_file2.txt" in r.strip())

    def testApplyPatchFromStash(self):

        test_file1 = path_utils.concat_path(self.second_repo, "test_file1.txt")
        if not create_and_write_file.create_file_contents(test_file1, "test-contents1"):
            self.fail("Failed creating test file %s" % test_file1)

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test commit msg1")
        self.assertTrue(v)

        test_file2 = path_utils.concat_path(self.second_repo, "test_file2.txt")
        if not create_and_write_file.create_file_contents(test_file2, "test-contents2"):
            self.fail("Failed creating test file %s" % test_file2)

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test commit msg2")
        self.assertTrue(v)

        fourth_repo = path_utils.concat_path(self.test_dir, "fourth")
        v, r = git_wrapper.clone(self.second_repo, fourth_repo)
        self.assertTrue(v)

        test_file2_fourthrepo = path_utils.concat_path(fourth_repo, "test_file2.txt")

        with open(test_file2_fourthrepo, "a") as f:
            f.write("latest content2")

        v, r = git_wrapper.stash(fourth_repo)
        self.assertTrue(v)

        v, r = collect_git_patch.collect_git_patch_stash(fourth_repo, self.storage_path)
        self.assertTrue(v)
        generated_patch_file = r[0]
        self.assertTrue( os.path.exists(generated_patch_file) )

        v, r = git_wrapper.status_simple(self.second_repo)
        self.assertTrue(v)
        self.assertEqual(r.strip(), "")

        v, r = git_wrapper.apply(self.second_repo, generated_patch_file)
        self.assertTrue(v)

        v, r = git_wrapper.status_simple(self.second_repo)
        self.assertTrue(v)
        self.assertTrue("test_file2.txt" in r.strip())

    def testApplyPatchFromPrevious(self):

        test_file1 = path_utils.concat_path(self.second_repo, "test_file1.txt")
        if not create_and_write_file.create_file_contents(test_file1, "test-contents1"):
            self.fail("Failed creating test file %s" % test_file1)

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test commit msg1")
        self.assertTrue(v)

        test_file2 = path_utils.concat_path(self.second_repo, "test_file2.txt")
        if not create_and_write_file.create_file_contents(test_file2, "test-contents2"):
            self.fail("Failed creating test file %s" % test_file2)

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test commit msg2")
        self.assertTrue(v)

        fourth_repo = path_utils.concat_path(self.test_dir, "fourth")
        v, r = git_wrapper.clone(self.second_repo, fourth_repo)
        self.assertTrue(v)

        test_file3_fourthrepo = path_utils.concat_path(fourth_repo, "test_file3.txt")

        with open(test_file3_fourthrepo, "a") as f:
            f.write("latest content3")

        v, r = git_wrapper.stage(fourth_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(fourth_repo, "test commit msg2")
        self.assertTrue(v)

        v, r = collect_git_patch.collect_git_patch_previous(fourth_repo, self.storage_path, 1)
        self.assertTrue(v)
        generated_patch_file = r[0]
        self.assertTrue( os.path.exists(generated_patch_file) )

        v, r = git_wrapper.status_simple(self.second_repo)
        self.assertTrue(v)
        self.assertEqual(r.strip(), "")

        v, r = git_wrapper.apply(self.second_repo, generated_patch_file)
        self.assertTrue(v)

        v, r = git_wrapper.status_simple(self.second_repo)
        self.assertTrue(v)
        self.assertTrue("test_file3.txt" in r.strip())

    def testCheckoutFail1(self):

        test_file1 = path_utils.concat_path(self.second_repo, "test_file1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(test_file1, "test-contents1"))

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test commit msg1")
        self.assertTrue(v)

        test_file2_nonexistent = path_utils.concat_path(self.second_repo, "test_file2_nonexistent.txt")

        v, r = git_wrapper.checkout(self.second_repo, [test_file2_nonexistent])
        self.assertFalse(v)

    def testCheckoutFail2(self):

        test_file1 = path_utils.concat_path(self.second_repo, "test_file1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(test_file1, "test-contents1"))

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test commit msg1")
        self.assertTrue(v)

        test_file2_notrepoed = path_utils.concat_path(self.second_repo, "test_file2_notrepoed.txt")
        self.assertTrue(create_and_write_file.create_file_contents(test_file2_notrepoed, "test-contents2"))

        v, r = git_wrapper.checkout(self.second_repo, [test_file2_notrepoed])
        self.assertFalse(v)

    def testCheckoutFail3(self):

        test_file1 = path_utils.concat_path(self.second_repo, "test_file1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(test_file1, "test-contents1"))

        test_file2 = path_utils.concat_path(self.second_repo, "test_file2.txt")
        self.assertTrue(create_and_write_file.create_file_contents(test_file2, "test-contents2"))

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test commit msg1")
        self.assertTrue(v)

        v, r = git_wrapper.status_simple(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(len(r.strip()) == 0)

        with open(test_file1, "a") as f:
            f.write("smore")

        with open(test_file2, "a") as f:
            f.write("smore")

        test_file2_nonexistent = path_utils.concat_path(self.second_repo, "test_file2_nonexistent.txt")

        v, r = git_wrapper.status_simple(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(len(r.strip()) != 0)

        v, r = git_wrapper.checkout(self.second_repo, [test_file2, test_file2_nonexistent])
        self.assertFalse(v)

        v, r = git_wrapper.status_simple(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(len(r.strip()) != 0)
        self.assertTrue(path_utils.basename_filtered(test_file1) in r)
        self.assertTrue(path_utils.basename_filtered(test_file2) in r)

    def testCheckoutFail4(self):

        test_file1 = path_utils.concat_path(self.second_repo, "test_file1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(test_file1, "test-contents1"))

        test_file2 = path_utils.concat_path(self.second_repo, "test_file2.txt")
        self.assertTrue(create_and_write_file.create_file_contents(test_file2, "test-contents2"))

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test commit msg1")
        self.assertTrue(v)

        v, r = git_wrapper.status_simple(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(len(r.strip()) == 0)

        with open(test_file1, "a") as f:
            f.write("smore")

        with open(test_file2, "a") as f:
            f.write("smore")

        test_file2_notrepoed = path_utils.concat_path(self.second_repo, "test_file2_notrepoed.txt")
        self.assertTrue(create_and_write_file.create_file_contents(test_file2_notrepoed, "test-contents2"))

        v, r = git_wrapper.status_simple(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(len(r.strip()) != 0)

        v, r = git_wrapper.checkout(self.second_repo, [test_file2, test_file2_notrepoed])
        self.assertFalse(v)

        v, r = git_wrapper.status_simple(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(len(r.strip()) != 0)
        self.assertTrue(path_utils.basename_filtered(test_file1) in r)
        self.assertTrue(path_utils.basename_filtered(test_file2) in r)

    def testCheckout1(self):

        test_file1 = path_utils.concat_path(self.second_repo, "test_file1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(test_file1, "test-contents1"))

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test commit msg1")
        self.assertTrue(v)

        v, r = git_wrapper.checkout(self.second_repo, [test_file1])
        self.assertTrue(v)

    def testCheckout2(self):

        test_file1 = path_utils.concat_path(self.second_repo, "test_file1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(test_file1, "test-contents1"))

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test commit msg1")
        self.assertTrue(v)

        v, r = git_wrapper.status_simple(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(len(r.strip()) == 0)

        with open(test_file1, "a") as f:
            f.write("smore")

        v, r = git_wrapper.status_simple(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(len(r.strip()) != 0)

        v, r = git_wrapper.checkout(self.second_repo, [test_file1])
        self.assertTrue(v)

        v, r = git_wrapper.status_simple(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(len(r.strip()) == 0)

    def testCheckout3(self):

        test_file1 = path_utils.concat_path(self.second_repo, "test_file1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(test_file1, "test-contents1"))

        test_file2 = path_utils.concat_path(self.second_repo, "test_file2.txt")
        self.assertTrue(create_and_write_file.create_file_contents(test_file2, "test-contents2"))

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test commit msg2")
        self.assertTrue(v)

        v, r = git_wrapper.status_simple(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(len(r.strip()) == 0)

        with open(test_file1, "a") as f:
            f.write("smore")

        with open(test_file2, "a") as f:
            f.write("smore")

        v, r = git_wrapper.status_simple(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(len(r.strip()) != 0)

        v, r = git_wrapper.checkout(self.second_repo, [test_file1])
        self.assertTrue(v)

        v, r = git_wrapper.status_simple(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(len(r.strip()) != 0)
        self.assertFalse(path_utils.basename_filtered(test_file1) in r)
        self.assertTrue(path_utils.basename_filtered(test_file2) in r)

    def testCheckout4(self):

        test_file1 = path_utils.concat_path(self.second_repo, "test_file1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(test_file1, "test-contents1"))

        test_sub = path_utils.concat_path(self.second_repo, "sub")
        os.mkdir(test_sub)
        test_sub_file2 = path_utils.concat_path(test_sub, "test_file2.txt")
        self.assertTrue(create_and_write_file.create_file_contents(test_sub_file2, "test-contents2"))

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test commit msg2")
        self.assertTrue(v)

        v, r = git_wrapper.status_simple(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(len(r.strip()) == 0)

        with open(test_file1, "a") as f:
            f.write("smore")

        with open(test_sub_file2, "a") as f:
            f.write("smore")

        v, r = git_wrapper.status_simple(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(len(r.strip()) != 0)

        v, r = git_wrapper.checkout(self.second_repo, [test_file1])
        self.assertTrue(v)

        v, r = git_wrapper.status_simple(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(len(r.strip()) != 0)
        self.assertFalse(path_utils.basename_filtered(test_file1) in r)
        self.assertTrue(path_utils.basename_filtered(test_sub_file2) in r)

    def testCheckout5(self):

        test_file1 = path_utils.concat_path(self.second_repo, "test_file1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(test_file1, "test-contents1"))

        test_sub = path_utils.concat_path(self.second_repo, "sub")
        os.mkdir(test_sub)
        test_sub_file2 = path_utils.concat_path(test_sub, "test_file2.txt")
        self.assertTrue(create_and_write_file.create_file_contents(test_sub_file2, "test-contents2"))

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test commit msg2")
        self.assertTrue(v)

        v, r = git_wrapper.status_simple(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(len(r.strip()) == 0)

        with open(test_file1, "a") as f:
            f.write("smore")

        with open(test_sub_file2, "a") as f:
            f.write("smore")

        v, r = git_wrapper.status_simple(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(len(r.strip()) != 0)

        v, r = git_wrapper.checkout(self.second_repo, [test_sub_file2])
        self.assertTrue(v)

        v, r = git_wrapper.status_simple(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(len(r.strip()) != 0)
        self.assertTrue(path_utils.basename_filtered(test_file1) in r)
        self.assertFalse(path_utils.basename_filtered(test_sub_file2) in r)

    def testCheckout6(self):

        test_file1 = path_utils.concat_path(self.second_repo, "test_file1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(test_file1, "test-contents1"))

        test_file2 = path_utils.concat_path(self.second_repo, "test_file2.txt")
        self.assertTrue(create_and_write_file.create_file_contents(test_file2, "test-contents2"))

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test commit msg1")
        self.assertTrue(v)

        v, r = git_wrapper.status_simple(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(len(r.strip()) == 0)

        with open(test_file1, "a") as f:
            f.write("smore")

        with open(test_file2, "a") as f:
            f.write("smore")

        v, r = git_wrapper.status_simple(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(len(r.strip()) != 0)

        v, r = git_wrapper.checkout(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.status_simple(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(len(r.strip()) == 0)

    def testCheckout7(self):

        test_file1 = path_utils.concat_path(self.second_repo, "test_file1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(test_file1, "test-contents1"))

        test_sub = path_utils.concat_path(self.second_repo, "sub")
        os.mkdir(test_sub)
        test_sub_file2 = path_utils.concat_path(test_sub, "test_file2.txt")
        self.assertTrue(create_and_write_file.create_file_contents(test_sub_file2, "test-contents2"))

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test commit msg1")
        self.assertTrue(v)

        v, r = git_wrapper.status_simple(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(len(r.strip()) == 0)

        with open(test_file1, "a") as f:
            f.write("smore")

        with open(test_sub_file2, "a") as f:
            f.write("smore")

        v, r = git_wrapper.status_simple(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(len(r.strip()) != 0)

        v, r = git_wrapper.checkout(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.status_simple(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(len(r.strip()) == 0)

    def testCheckout8(self):

        test_file1 = path_utils.concat_path(self.second_repo, "test_file1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(test_file1, "test-contents1"))

        test_file2 = path_utils.concat_path(self.second_repo, "test_file2.txt")
        self.assertTrue(create_and_write_file.create_file_contents(test_file2, "test-contents2"))

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test commit msg1")
        self.assertTrue(v)

        v, r = git_wrapper.status_simple(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(len(r.strip()) == 0)

        with open(test_file1, "a") as f:
            f.write("smore")

        with open(test_file2, "a") as f:
            f.write("smore")

        v, r = git_wrapper.status_simple(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(len(r.strip()) != 0)

        v, r = git_wrapper.checkout(self.second_repo, [test_file1, test_file2])
        self.assertTrue(v)

        v, r = git_wrapper.status_simple(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(len(r.strip()) == 0)

    def testCheckout9(self):

        test_file1 = path_utils.concat_path(self.second_repo, "test_file1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(test_file1, "test-contents1"))

        test_file2 = path_utils.concat_path(self.second_repo, "test_file2.txt")
        self.assertTrue(create_and_write_file.create_file_contents(test_file2, "test-contents2"))

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test commit msg1")
        self.assertTrue(v)

        v, r = git_wrapper.status_simple(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(len(r.strip()) == 0)

        with open(test_file1, "a") as f:
            f.write("smore")

        with open(test_file2, "a") as f:
            f.write("smore")

        v, r = git_wrapper.status_simple(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(len(r.strip()) != 0)

        v, r = git_wrapper.checkout(self.second_repo, [test_file2])
        self.assertTrue(v)

        v, r = git_wrapper.status_simple(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(len(r.strip()) != 0)
        self.assertTrue(path_utils.basename_filtered(test_file1) in r)
        self.assertFalse(path_utils.basename_filtered(test_file2) in r)

    def testResetHeadFail1(self):

        v, r = git_wrapper.reset_head(self.second_repo)
        self.assertFalse(v)

    def testResetHeadFail2(self):

        test_file1 = path_utils.concat_path(self.second_repo, "test_file1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(test_file1, "test-contents1"))

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test commit msg1")
        self.assertTrue(v)

        v, r = git_wrapper.status_simple(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(len(r.strip()) == 0)

        with open(test_file1, "a") as f:
            f.write("smore")

        v, r = git_wrapper.status_simple(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(len(r.strip()) != 0)

        v, r = git_wrapper.status(self.second_repo)
        self.assertTrue(" M test_file1.txt" in r)

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.status(self.second_repo)
        self.assertTrue("M  test_file1.txt" in r)

        v, r = git_wrapper.reset_head(self.second_repo, test_file1)
        self.assertFalse(v)

        v, r = git_wrapper.status(self.second_repo)
        self.assertTrue("M  test_file1.txt" in r)
        self.assertFalse(" M test_file1.txt" in r)

    def testResetHead1(self):

        test_file1 = path_utils.concat_path(self.second_repo, "test_file1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(test_file1, "test-contents1"))

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test commit msg1")
        self.assertTrue(v)

        v, r = git_wrapper.status_simple(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(len(r.strip()) == 0)

        with open(test_file1, "a") as f:
            f.write("smore")

        v, r = git_wrapper.status_simple(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(len(r.strip()) != 0)

        v, r = git_wrapper.status(self.second_repo)
        self.assertTrue(" M test_file1.txt" in r)

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.status(self.second_repo)
        self.assertTrue("M  test_file1.txt" in r)

        v, r = git_wrapper.reset_head(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.status(self.second_repo)
        self.assertTrue(" M test_file1.txt" in r)

    def testResetHead2(self):

        test_file1 = path_utils.concat_path(self.second_repo, "test_file1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(test_file1, "test-contents1"))

        test_file2 = path_utils.concat_path(self.second_repo, "test_file2.txt")
        self.assertTrue(create_and_write_file.create_file_contents(test_file2, "test-contents2"))

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test commit msg1")
        self.assertTrue(v)

        v, r = git_wrapper.status_simple(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(len(r.strip()) == 0)

        with open(test_file1, "a") as f:
            f.write("smore")

        with open(test_file2, "a") as f:
            f.write("smore")

        v, r = git_wrapper.status_simple(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(len(r.strip()) != 0)

        v, r = git_wrapper.status(self.second_repo)
        self.assertTrue(" M test_file1.txt" in r)

        v, r = git_wrapper.status(self.second_repo)
        self.assertTrue(" M test_file2.txt" in r)

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.status(self.second_repo)
        self.assertTrue("M  test_file1.txt" in r)

        v, r = git_wrapper.status(self.second_repo)
        self.assertTrue("M  test_file2.txt" in r)

        v, r = git_wrapper.reset_head(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.status(self.second_repo)
        self.assertTrue(" M test_file1.txt" in r)

        v, r = git_wrapper.status(self.second_repo)
        self.assertTrue(" M test_file2.txt" in r)

    def testResetHead3(self):

        test_file1 = path_utils.concat_path(self.second_repo, "test_file1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(test_file1, "test-contents1"))

        test_file2 = path_utils.concat_path(self.second_repo, "test_file2.txt")
        self.assertTrue(create_and_write_file.create_file_contents(test_file2, "test-contents2"))

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test commit msg1")
        self.assertTrue(v)

        v, r = git_wrapper.status_simple(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(len(r.strip()) == 0)

        with open(test_file1, "a") as f:
            f.write("smore")

        with open(test_file2, "a") as f:
            f.write("smore")

        v, r = git_wrapper.status_simple(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(len(r.strip()) != 0)

        v, r = git_wrapper.status(self.second_repo)
        self.assertTrue(" M test_file1.txt" in r)

        v, r = git_wrapper.status(self.second_repo)
        self.assertTrue(" M test_file2.txt" in r)

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.status(self.second_repo)
        self.assertTrue("M  test_file1.txt" in r)

        v, r = git_wrapper.status(self.second_repo)
        self.assertTrue("M  test_file2.txt" in r)

        v, r = git_wrapper.reset_head(self.second_repo, [test_file1])
        self.assertTrue(v)

        v, r = git_wrapper.status(self.second_repo)
        self.assertTrue(" M test_file1.txt" in r)

        v, r = git_wrapper.status(self.second_repo)
        self.assertTrue("M  test_file2.txt" in r)

    def testResetHardHeadFail1(self):

        test_file1 = path_utils.concat_path(self.second_repo, "test_file1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(test_file1, "test-contents1"))

        test_file2 = path_utils.concat_path(self.second_repo, "test_file2.txt")
        self.assertTrue(create_and_write_file.create_file_contents(test_file2, "test-contents2"))

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test commit msg1")
        self.assertTrue(v)

        v, r = git_wrapper.status_simple(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(len(r.strip()) == 0)

        v, r = git_wrapper.show(self.second_repo)
        self.assertTrue(v)
        self.assertTrue("test-contents1" in r)
        self.assertTrue("test-contents2" in r)

        v, r = git_wrapper.reset_hard_head(self.second_repo, 1)
        self.assertFalse(v) # cant reset the very first commit

    def testResetHardHead1(self):

        test_file1 = path_utils.concat_path(self.second_repo, "test_file1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(test_file1, "test-contents1"))

        test_file2 = path_utils.concat_path(self.second_repo, "test_file2.txt")
        self.assertTrue(create_and_write_file.create_file_contents(test_file2, "test-contents2"))

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test commit msg1")
        self.assertTrue(v)

        v, r = git_wrapper.status_simple(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(len(r.strip()) == 0)

        with open(test_file1, "a") as f:
            f.write("smore1")

        with open(test_file2, "a") as f:
            f.write("smore2")

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test commit msg2")
        self.assertTrue(v)

        with open(test_file1, "a") as f:
            f.write("yetmore1")

        with open(test_file2, "a") as f:
            f.write("yetmore2")

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test commit msg3")
        self.assertTrue(v)

        v, r = git_wrapper.status_simple(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(len(r.strip()) == 0)

        v, r = git_wrapper.show(self.second_repo)
        self.assertTrue(v)
        self.assertTrue("yetmore1" in r)
        self.assertTrue("yetmore2" in r)

        v, r = git_wrapper.reset_hard_head(self.second_repo, 1)
        self.assertTrue(v)

        v, r = git_wrapper.show(self.second_repo)
        self.assertTrue(v)
        self.assertFalse("yetmore1" in r)
        self.assertFalse("yetmore2" in r)
        self.assertTrue("smore1" in r)
        self.assertTrue("smore2" in r)

    def testResetHardHead2(self):

        test_file1 = path_utils.concat_path(self.second_repo, "test_file1.txt")
        self.assertTrue(create_and_write_file.create_file_contents(test_file1, "test-contents1"))

        test_file2 = path_utils.concat_path(self.second_repo, "test_file2.txt")
        self.assertTrue(create_and_write_file.create_file_contents(test_file2, "test-contents2"))

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test commit msg1")
        self.assertTrue(v)

        v, r = git_wrapper.status_simple(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(len(r.strip()) == 0)

        with open(test_file1, "a") as f:
            f.write("smore1")

        with open(test_file2, "a") as f:
            f.write("smore2")

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test commit msg2")
        self.assertTrue(v)

        with open(test_file1, "a") as f:
            f.write("yetmore1")

        with open(test_file2, "a") as f:
            f.write("yetmore2")

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test commit msg3")
        self.assertTrue(v)

        with open(test_file1, "a") as f:
            f.write("againmorestuff1")

        with open(test_file2, "a") as f:
            f.write("againmorestuff2")

        v, r = git_wrapper.stage(self.second_repo)
        self.assertTrue(v)

        v, r = git_wrapper.commit(self.second_repo, "test commit msg4")
        self.assertTrue(v)

        v, r = git_wrapper.status_simple(self.second_repo)
        self.assertTrue(v)
        self.assertTrue(len(r.strip()) == 0)

        v, r = git_wrapper.show(self.second_repo)
        self.assertTrue(v)
        self.assertTrue("againmorestuff1" in r)
        self.assertTrue("againmorestuff2" in r)

        v, r = git_wrapper.reset_hard_head(self.second_repo, 3)
        self.assertTrue(v)

        v, r = git_wrapper.show(self.second_repo)
        self.assertTrue(v)
        self.assertTrue("test-contents1" in r)
        self.assertTrue("test-contents2" in r)

if __name__ == '__main__':
    unittest.main()
