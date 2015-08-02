#!/usr/bin/env python

import sys
import os
import git_visitor_base
import git_repo_query
from subprocess import check_output

def visitor_pull(repos):
    for rp in repos:
        print("\n* Pulling from %s ..." % rp)
        remotes = git_repo_query.get_remotes(rp)
        for rm in remotes:
            out = check_output(["git", "--git-dir=%s" % rp, "--work-tree=%s" % os.path.dirname(rp), "pull", rm])
            # mvtodo: if any of these calls fail, the show is stopped. this is obviously wrong. dont stop when any repo fails because local and remote are out of sync
            # mvtodo: I could parse out and print more informative stuff
    # mvtodo: should also print a shorter report in the end (no failures vs. this and that failed, instead of wanting the user to read thru all the pull messages)

if __name__ == "__main__":
    git_visitor_base.do_visit(sys.argv, visitor_pull)

