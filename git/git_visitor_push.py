#!/usr/bin/env python

import sys
import os
import git_visitor_base
import git_repo_query
import subprocess

def derive_result(out_str):
    print("mvdebug [%s]" % out_str)
    return "mvtodo"

def visitor_push(repos):

    report = []
    for rp in repos:
        print("\n* Pushing to %s ..." % rp)
        remotes = git_repo_query.get_remotes(rp)
        for rm in remotes:

            try:
                out = subprocess.check_output(["git", "--git-dir=%s" % rp, "--work-tree=%s" % os.path.dirname(rp), "push", rm])
            except OSError as oser:
                out = oser.strerror
            except subprocess.CalledProcessError as cper:
                out = cper.strerror
            
            res = derive_result(out)
            bn = "mvtodo"
            report.append("%s (remote=%s, branch=%s): %s" % (rp, rm, bn, res))

    for p in report:
        print(p)

if __name__ == "__main__":
    git_visitor_base.do_visit(sys.argv, visitor_push)

