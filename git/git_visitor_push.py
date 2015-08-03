#!/usr/bin/env python

import sys
import os
import subprocess

import git_visitor_base
import git_repo_query

def visitor_push(repos):

    report = []
    for rp in repos:
        print("\n* Pushing to %s ..." % rp)
        remotes = git_repo_query.get_remotes(rp)
        for rm in remotes:

            try:
                out = subprocess.check_output(["git", "--git-dir=%s" % rp, "--work-tree=%s" % os.path.dirname(rp), "push", rm])
                out = "OK."
            except OSError as oser:
                out = "Failed."
            except subprocess.CalledProcessError as cper:
                out = "Failed."
            
            bn = "mvtodo"
            report.append("%s (remote=%s, branch=%s): %s" % (rp, rm, bn, out))

    print("RESULTS:\n")
    for p in report:
        print(p)

if __name__ == "__main__":
    git_visitor_base.do_visit(sys.argv, visitor_push)

