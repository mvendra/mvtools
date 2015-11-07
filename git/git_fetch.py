#!/usr/bin/env python

import os
import subprocess

def do_fetch(repo, remotes):

    ORIGINAL_COLOR = "\033[0m" # mvtodo: would be better to try to detect the terminal's current standard color
    report = []

    remotes_line = ""
    for r in remotes:
        remotes_line += r + " "
    remotes_line = remotes_line.strip() # removes the last space

    print("\n* Fetching %s ..." % repo)
    try:
        out = subprocess.check_output(["git", "--git-dir=%s" % repo, "--work-tree=%s" % os.path.dirname(repo), "fetch", "--multiple", remotes_line])
        out = "OK."
        color = "\033[32m" # green
    except OSError as oser:
        out = "Failed."
        color = "\033[31m" # red
    except subprocess.CalledProcessError as cper:
        out = "Failed."
        color = "\033[31m" # red
    
    report.append("%s%s: %s%s" % (color, repo, out, ORIGINAL_COLOR))

    return report

