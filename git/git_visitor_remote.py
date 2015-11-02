#!/usr/bin/env python

import sys
import os

import git_visitor_base
import git_repo_query

def visitor_remote(repos):

    for rp in repos:
        print("\n* Listing remotes of %s ..." % rp)
        remotes = git_repo_query.get_remotes(rp)
        for rm in remotes:
            print("%s: %s" % (os.path.basename(os.path.dirname(rp)), rm))

if __name__ == "__main__":
    git_visitor_base.do_visit(sys.argv, visitor_remote)

