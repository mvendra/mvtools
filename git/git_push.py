#!/usr/bin/env python

import terminal_colors

import subprocess

def do_push(repo, remotes, branches):

    ORIGINAL_COLOR = terminal_colors.get_standard_color()
    report = []

    print("\n* Pushing on %s ..." % repo)
    for rm in remotes:
        for bn in branches:

            try:
                out = subprocess.check_output(["git", "-C", repo, "push", rm, bn])
                out = "OK."
                color = terminal_colors.TTY_GREEN
            except OSError as oser:
                out = "Failed."
                color = terminal_colors.TTY_RED
            except subprocess.CalledProcessError as cper:
                out = "Failed."
                color = terminal_colors.TTY_RED
            
            report.append("%s%s (remote=%s, branch=%s): %s%s" % (color, repo, rm, bn, out, ORIGINAL_COLOR))

    return report

