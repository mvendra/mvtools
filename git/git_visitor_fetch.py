#!/usr/bin/env python

import sys
import os
import subprocess

import git_visitor_base

def visitor_fetch(repos):

    ORIGINAL_COLOR = "\033[0m" # mvtodo: would be better to try to detect the terminal's current standard color

    report = []
    for rp in repos:
        print("\n* Fetching %s ..." % rp)

        try:
            out = subprocess.check_output(["git", "--git-dir=%s" % rp, "--work-tree=%s" % os.path.dirname(rp), "fetch", "--all"])
            out = "OK."
            color = "\033[32m" # green
        except OSError as oser:
            out = "Failed."
            color = "\033[31m" # red
        except subprocess.CalledProcessError as cper:
            out = "Failed."
            color = "\033[31m" # red
        
        report.append("%s%s: %s%s" % (color, rp, out, ORIGINAL_COLOR))

    print("\nRESULTS:")
    for p in report:
        print(p)
    print("%s\n" % ORIGINAL_COLOR) # reset terminal color

if __name__ == "__main__":
    git_visitor_base.do_visit(sys.argv, visitor_fetch)

