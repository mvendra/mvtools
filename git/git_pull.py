#!/usr/bin/env python

import sys
import os
import subprocess

import git_visitor_base
import git_repo_query

def do_pull(repo, remotes, branches):

    ORIGINAL_COLOR = "\033[0m" # mvtodo: would be better to try to detect the terminal's current standard color
    report = []

    print("\n* Pulling from %s ..." % repo)
    for rm in remotes:
        for bn in branches:

            try:
                out = subprocess.check_output(["git", "--git-dir=%s" % repo, "--work-tree=%s" % os.path.dirname(repo), "pull", "--ff-only", rm, bn])
                out = "OK."
                color = "\033[32m" # green
            except OSError as oser:
                out = "Failed."
                color = "\033[31m" # red
            except subprocess.CalledProcessError as cper:
                out = "Failed."
                color = "\033[31m" # red
            
            report.append("%s%s (remote=%s, branch=%s): %s%s" % (color, repo, rm, bn, out, ORIGINAL_COLOR))

    return report

