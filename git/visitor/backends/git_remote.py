#!/usr/bin/env python

import terminal_colors

from subprocess import check_output
from subprocess import CalledProcessError

def remote_change_url(repo, remote, operation, newpath):

    ORIGINAL_COLOR = terminal_colors.get_standard_color() 
    report = ""
    fail = False

    print("\n* Changing %s's %s remote (%s) ..." % (repo, operation, remote))

    try:
        # currently (september 2016), there is no support on git's side for specifying fetch operations.
        # so, for now, the operation is ignored
        #out = check_output(["git", "-C", "%s" % repo, "remote", "set-url", "--%s" % operation, remote, newpath])
        out = check_output(["git", "-C", "%s" % repo, "remote", "set-url", remote, newpath])
        out = "OK."
        color = terminal_colors.TTY_GREEN
    except OSError as oser:
        fail = True
        out = "Failed."
        color = terminal_colors.TTY_RED
    except CalledProcessError as cper:
        fail = True
        out = "Failed."
        color = terminal_colors.TTY_RED
    
    #report = "%sChanging %s's %s remote (%s) to %s: %s%s" % (color, repo, operation, remote, newpath, out, ORIGINAL_COLOR)
    report = "%sChanging %s's remote (%s) to %s: %s%s" % (color, repo, remote, newpath, out, ORIGINAL_COLOR)

    return fail, report

