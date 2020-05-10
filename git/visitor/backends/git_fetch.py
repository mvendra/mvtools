#!/usr/bin/env python3

import terminal_colors
import git_wrapper

def do_fetch(repo, remotes):

    ORIGINAL_COLOR = terminal_colors.get_standard_color() 
    report = []

    remotes_list = [i for i in remotes if "fetch" in remotes[i]]

    print("\n* Fetching on %s ..." % repo)
    hasanyfailed = False
    v, r = git_wrapper.fetch_multiple(repo, remotes_list)
    if v:
        out = "OK."
        color = terminal_colors.TTY_GREEN
    else:
        print(r)
        hasanyfailed = True
        out = "Failed."
        color = terminal_colors.TTY_RED

    report.append("%s%s: %s%s" % (color, repo, out, ORIGINAL_COLOR))

    return hasanyfailed, report
