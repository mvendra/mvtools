#!/usr/bin/env python

import terminal_colors

import subprocess

def do_fetch(repo, remotes):

    ORIGINAL_COLOR = terminal_colors.get_standard_color() 
    report = []

    print("\n* Fetching on %s ..." % repo)
    hasanyfailed = False
    try:
        out = subprocess.check_output(["git", "-C", repo, "fetch", "--multiple"] + remotes)
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
    
    report.append("%s%s: %s%s" % (color, repo, out, ORIGINAL_COLOR))

    return hasanyfailed, report

