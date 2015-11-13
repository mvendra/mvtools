#!/usr/bin/env python

import terminal_colors

import subprocess

def do_pull(repo, remotes, branches):

    ORIGINAL_COLOR = terminal_colors.get_standard_color() 
    report = []

    print("\n* Pulling on %s ..." % repo)
    hasanyfailed = False
    for rm in remotes:
        for bn in branches:

            try:
                out = subprocess.check_output(["git", "-C", "%s" % repo, "pull", "--ff-only", rm, bn])
                out = "OK."
                color = terminal_colors.TTY_GREEN
            except OSError as oser:
                hasanyfailed = True
                out = "Failed."
                color = terminal_colors.TTY_RED
            except subprocess.CalledProcessError as cper:
                hasanyfailed = True
                out = "Failed."
                color = terminal_colors.TTY_RED
            
            report.append("%s%s (remote=%s, branch=%s): %s%s" % (color, repo, rm, bn, out, ORIGINAL_COLOR))

    return hasanyfailed, report

