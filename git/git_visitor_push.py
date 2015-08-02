#!/usr/bin/env python

import sys
import os
import git_visitor_base
import git_repo_query
from subprocess import check_output

def visitor_push(repos):
    for rp in repos:
        print("* Pushing to %s ..." % rp)
        remotes = git_repo_query.get_remotes(rp)
        for rm in remotes:
            out = check_output(["git", "--git-dir=%s" % rp, "--work-tree=%s" % os.path.dirname(rp), "push", rm])
            # mvtodo: I could parse out and print more informative stuff
    print("\n\n")

if __name__ == "__main__":
    git_visitor_base.do_visit(sys.argv, visitor_push)

