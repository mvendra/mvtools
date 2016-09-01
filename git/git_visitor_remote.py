#!/usr/bin/env python

import os

import git_visitor_base
import git_repo_query

def visitor_remote(repos, options):

    for rp in repos:
        print("\n* Listing remotes of %s ..." % rp)
        remotes = git_repo_query.get_remotes(rp)
        for rm in remotes:
            # mvtodo: print all returned
            print("%s: %s" % (os.path.basename(rp), rm))

if __name__ == "__main__":
    git_visitor_base.do_visit(None, None, visitor_remote)

