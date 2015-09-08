#!/usr/bin/env python

import sys
import os
import subprocess

import git_visitor_base
import git_repo_query

def visitor_push(repos):

    ORIGINAL_COLOR = "\033[0m" # mvtodo: would be better to try to detect the terminal's current standard color

    report = []
    for rp in repos:
        print("\n* Pushing to %s ..." % rp)
        remotes = git_repo_query.get_remotes(rp)
        for rm in remotes:
            branches = git_repo_query.get_branches(rp)
            for bn in branches:

                try:
                    out = subprocess.check_output(["git", "--git-dir=%s" % rp, "--work-tree=%s" % os.path.dirname(rp), "push", rm, bn])
                    out = "OK."
                    color = "\033[32m" # green
                except OSError as oser:
                    out = "Failed."
                    color = "\033[31m" # red
                except subprocess.CalledProcessError as cper:
                    out = "Failed."
                    color = "\033[31m" # red
                
                report.append("%s%s (remote=%s, branch=%s): %s%s" % (color, rp, rm, bn, out, ORIGINAL_COLOR))

    print("\nRESULTS:")
    for p in report:
        print(p)
    print("%s\n" % ORIGINAL_COLOR) # reset terminal color

if __name__ == "__main__":
    # mvtodo: get the remotes by param here, then pass to visitor_push. inside visitor_push, only use all remotes if this parameter is None
    git_visitor_base.do_visit(sys.argv, visitor_push)

