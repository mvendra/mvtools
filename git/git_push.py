#!/usr/bin/env python

import os
import subprocess

def do_push(repo, remotes, branches):

    ORIGINAL_COLOR = "\033[0m" # mvtodo: would be better to try to detect the terminal's current standard color
    report = []

    print("\n* Pushing to %s ..." % repo)
    for rm in remotes:
        for bn in branches:

            try:
                out = subprocess.check_output(["git", "--git-dir=%s" % repo, "--work-tree=%s" % os.path.dirname(repo), "push", rm, bn])
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

