#!/usr/bin/env python

import sys
import os
import shutil
import unittest

import git_test_fixture
import git_wrapper
import git_visitor_base
import path_utils
import mvtools_test_fixture

class GitVisitorBaseTest(unittest.TestCase):

    def makeFilename(self):
        self.internal_counter += 1
        filename = "testfile_%s.txt" % self.internal_counter
        return filename

    def makeContent(self):
        self.internal_counter += 1
        content = "rubbish_content_%s" % self.internal_counter
        return content

    def setUp(self):
        v, r = self.delegate_setUp()
        if not v:
            self.tearDown()
            self.fail(r)

    def delegate_setUp(self):

        self.internal_counter = 0

        v, r = mvtools_test_fixture.makeAndGetTestFolder("git_visitor_backends_test")
        if not v:
            return v, r
        self.test_base_dir = r[0] # base test folder. shared amongst other test cases
        self.test_dir = r[1] # test folder, specific for each test case (i.e. one level above self.test_base_dir)

        # test repos paths
        self.first_repo = path_utils.concat_path(self.test_dir, "first")
        self.second_repo = path_utils.concat_path(self.test_dir, "second")
        self.third_repo = path_utils.concat_path(self.test_dir, "third")

        # creates test repos
        v, r = git_wrapper.init(self.test_dir, "first", False)
        if not v:
            return v, r

        v, r = git_wrapper.init(self.test_dir, "second", False)
        if not v:
            return v, r

        v, r = git_wrapper.init(self.test_dir, "third", False)
        if not v:
            return v, r

        return True, ""

    def tearDown(self):
        shutil.rmtree(self.test_base_dir)

    def testFilterGitOnly(self):

        repos = ["/home/user/nuke/first/.git", "/home/user/nuke", "/made/up/path", "/home/user/nuke/second/_.git"]

        r = git_visitor_base.filter_git_only(repos)
        self.assertEqual( len(r), 1)
        self.assertEqual( r[0], "/home/user/nuke/first/.git" )

    def testPrintReport(self):
        pass

    def testMakeRepoList(self):

        r = git_visitor_base.make_repo_list(self.test_dir)

        self.assertEqual( len(r), 3 )
        self.assertTrue( path_utils.concat_path(self.test_dir, "first") in r )
        self.assertTrue( path_utils.concat_path(self.test_dir, "second") in r )
        self.assertTrue( path_utils.concat_path(self.test_dir, "third") in r )

    def testMakePathList(self):

        r = git_visitor_base.make_path_list([self.test_dir])
        self.assertEqual( len(r), 1 )
        self.assertEqual( self.test_dir, r[0] )

    def testPluckDotGit(self):

        paths = [path_utils.concat_path(self.test_dir, "first/.git"), path_utils.concat_path(self.test_dir, "second/.git"), self.test_dir ]
        r = git_visitor_base.pluck_dotgit(paths)
        self.assertEqual( len(r), 3 )

    def testAssemblePickList(self):

        xor_opt = "xor-remotename"
        not_opt = ""

        options = {}
        options["xor-remotename"] = "offline"

        remote_names = ["public", "offline", "private"]

        r = git_visitor_base.assemble_pick_list(xor_opt, not_opt, options, remote_names)
        self.assertEqual( len(r), 1 )
        self.assertEqual( r[0], "offline" )

        xor_opt = ""
        not_opt = "not-remotename"

        options = {}
        options["not-remotename"] = "offline"

        remote_names = ["public", "offline", "private"]

        r = git_visitor_base.assemble_pick_list(xor_opt, not_opt, options, remote_names)
        self.assertEqual( len(r), 2 )
        self.assertTrue( "public" in r )
        self.assertTrue( "private" in r )

    def testFilterBranches(self):

        branches = ["master", "feature", "bug"]
        options = {}
        options["xor-branch"] = "master"

        r = git_visitor_base.filter_branches(branches, options)
        self.assertEqual( len(r), 1 )
        self.assertEqual(r[0], "master")

        branches = ["master", "feature", "bug"]
        options = {}
        options["not-branch"] = "master"

        r = git_visitor_base.filter_branches(branches, options)
        self.assertEqual( len(r), 2 )
        self.assertTrue("feature" in r)
        self.assertTrue("bug" in r)

    def testFilterRemotes(self):

        remotes = {}
        remotes["origin"] = { "push": self.second_repo, "fetch": self.second_repo }
        remotes["extra_endpoint"] = { "push": self.third_repo, "fetch": self.third_repo }

        options  = {}
        options["xor-remotename"] = "origin"

        r = git_visitor_base.filter_remotes(remotes, options)
        self.assertEqual( len(r), 1 )
        self.assertTrue( "origin" in r )

        options  = {}
        options["not-remotename"] = "origin"

        r = git_visitor_base.filter_remotes(remotes, options)
        self.assertEqual( len(r), 1 )
        self.assertTrue( "extra_endpoint" in r )

    def testApplyFilters(self):

        v, r = git_wrapper.remote_add(self.first_repo, "origin", self.second_repo)
        if not v:
            self.fail(r)

        v, r = git_wrapper.remote_add(self.first_repo, "third_remote", self.third_repo)
        if not v:
            self.fail(r)

        v, r = git_test_fixture.git_createAndCommit(self.first_repo, self.makeFilename(), self.makeContent(), "commit_msg")
        if not v:
            self.fail(r)

        options = {}
        options["xor-remotename"] = "origin"
        options["xor-branch"] = "master"

        r = git_visitor_base.apply_filters(self.first_repo, options)
        self.assertEqual( len(r), 2 )
        self.assertTrue( "origin" in r[0] )

    def testProcessFilters(self):

        query = ["--not-remotename", "origin"]
        r = git_visitor_base.process_filters(query)
        self.assertEqual( len(r), 1 )
        self.assertTrue( "not-remotename" in r )

        query = ["--xor-remotename", "offline"]
        r = git_visitor_base.process_filters(query)
        self.assertEqual( len(r), 1 )
        self.assertTrue( "xor-remotename" in r )

    def testDoVisitOpt1(self):

        repos = [self.first_repo]
        query = ["--not-remotename", "extra"]

        called_flag = False

        def test_func(p1, p2):
            nonlocal called_flag
            called_flag = True
            return p2

        r = git_visitor_base.do_visit(repos, query, test_func)
        self.assertTrue(called_flag)
        self.assertEqual( len(r), 1 )
        self.assertTrue( "not-remotename" in r[0] )
        self.assertEqual( r[0]["not-remotename"][0], "extra" )

    def testDoVisitOpt2(self):

        repos = [self.first_repo]
        query = ["--xor-remotename", "origin"]

        called_flag = False

        def test_func(p1, p2):
            nonlocal called_flag
            called_flag = True
            return p2

        r = git_visitor_base.do_visit(repos, query, test_func)
        self.assertTrue(called_flag)
        self.assertEqual( len(r), 1 )
        self.assertTrue( "xor-remotename" in r[0] )
        self.assertEqual( r[0]["xor-remotename"], "origin" )

if __name__ == "__main__":
    unittest.main()
