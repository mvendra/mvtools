#!/usr/bin/env python3

import os
import sys
import fsquery
import terminal_colors

import git_pull
import git_lib
import path_utils

def filter_sub_files(sub_candidates):

    ret = []
    for i in sub_candidates:
        if path_utils.basename_filtered(i) == ".git":
            ret.append(path_utils.dirname_filtered(i))

    return ret

def pull_subs(path):

    subs = fsquery.makecontentlist(path, True, False, False, False, True, False, True, None)
    subs = filter_sub_files(subs)

    report = []
    anyfailed = False

    for s in subs:

        v, r = git_lib.get_remotes(s)
        if not v:
            anyfailed = True
            report.append("pull_subs failed [%s]: [%s]" % (s, r))
            continue
        rs = r
        v, r = git_lib.get_branches(s)
        if not v:
            anyfailed = True
            report.append("pull_subs failed [%s]: [%s]" % (s, r))
            continue
        bs = r

        af, r = git_pull.do_pull(s, rs, bs)
        anyfailed |= af
        report += r

    print(os.linesep)
    for rp in report:
        print(rp)
    print(os.linesep)

    if anyfailed:
        print("%sErrors detected, see above.%s" % (terminal_colors.TTY_RED, terminal_colors.TTY_WHITE))
    else:
        print("%sAll succeeded.%s" % (terminal_colors.TTY_GREEN, terminal_colors.TTY_WHITE))

if __name__ == "__main__":

    path = ""
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = os.getcwd()

    pull_subs(path)
