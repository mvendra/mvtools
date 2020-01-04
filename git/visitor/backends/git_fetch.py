#!/usr/bin/env python3

import terminal_colors

from subprocess import check_output
from subprocess import CalledProcessError

def do_fetch(repo, remotes):

    ORIGINAL_COLOR = terminal_colors.get_standard_color() 
    report = []

    remotes_list = [i for i in remotes if "fetch" in remotes[i]]

    print("\n* Fetching on %s ..." % repo)
    hasanyfailed = False
    try:
        out = check_output(["git", "-C", repo, "fetch", "--multiple"] + remotes_list)
        out = "OK."
        color = terminal_colors.TTY_GREEN
    except:
        hasanyfailed = True
        out = "Failed."
        color = terminal_colors.TTY_RED

    report.append("%s%s: %s%s" % (color, repo, out, ORIGINAL_COLOR))

    return hasanyfailed, report
