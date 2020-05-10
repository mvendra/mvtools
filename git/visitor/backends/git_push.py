#!/usr/bin/env python3

import terminal_colors
import git_wrapper

def do_push(repo, remotes, branches):

    ORIGINAL_COLOR = terminal_colors.get_standard_color()
    report = []

    remotes_list = [i for i in remotes if "push" in remotes[i]]

    print("\n* Pushing on %s ..." % repo)
    hasanyfailed = False
    for rm in remotes_list:
        for bn in branches:

            v, r = git_wrapper.push(repo, rm, bn)
            if v:
                out = "OK."
                color = terminal_colors.TTY_GREEN
            else:
                print(r)
                hasanyfailed = True
                out = "Failed."
                color = terminal_colors.TTY_RED

            report.append("%s%s (remote=%s, branch=%s): %s%s" % (color, repo, rm, bn, out, ORIGINAL_COLOR))

    return hasanyfailed, report
