#!/usr/bin/env python3

import terminal_colors

from subprocess import check_output
from subprocess import CalledProcessError

def do_pull(repo, remotes, branches):

    ORIGINAL_COLOR = terminal_colors.get_standard_color() 
    report = []

    remotes_list = [i for i in remotes if "fetch" in remotes[i]]

    print("\n* Pulling on %s ..." % repo)
    hasanyfailed = False
    for rm in remotes_list:
        for bn in branches:

            try:
                out = check_output(["git", "-C", "%s" % repo, "pull", "--ff-only", rm, bn])
                out = "OK."
                color = terminal_colors.TTY_GREEN
            except:
                hasanyfailed = True
                out = "Failed."
                color = terminal_colors.TTY_RED

            report.append("%s%s (remote=%s, branch=%s): %s%s" % (color, repo, rm, bn, out, ORIGINAL_COLOR))

    return hasanyfailed, report
