#!/usr/bin/env python3

import terminal_colors
import git_wrapper

def remote_change_url(repo, remote, operation, newpath):

    ORIGINAL_COLOR = terminal_colors.get_standard_color() 
    report = ""
    fail = False

    print("\n* Changing %s's %s remote (%s) ..." % (repo, operation, remote))

    v, r = git_wrapper.remote_change_url(repo, remote, newpath)
    if v:
        out = "OK."
        color = terminal_colors.TTY_GREEN
    else:
        print(r)
        fail = True
        out = "Failed."
        color = terminal_colors.TTY_RED

    report = "%sChanging %s's remote (%s) to %s: %s%s" % (color, repo, remote, newpath, out, ORIGINAL_COLOR)

    return fail, report
