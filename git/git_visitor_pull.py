#!/usr/bin/env python

import terminal_colors

import git_visitor_base
import git_pull

import sys

def visitor_pull(repos, options):

    ORIGINAL_COLOR = terminal_colors.get_standard_color() 

    report = []
    for rp in repos:

        try:
            remotes, branches = git_visitor_base.apply_filters(rp, options)
        except git_visitor_base.gvbexcept as gvbex:
            report.append("%s%s: %s.%s" % (terminal_colors.TTY_RED, rp, gvbex.message, ORIGINAL_COLOR)) 
            continue

        report_piece = git_pull.do_pull(rp, remotes, branches)
        for ri in report_piece:
            report.append(ri)

    print("\nRESULTS:")
    for p in report:
        print(p)
    print("%s\n" % ORIGINAL_COLOR) # reset terminal color

if __name__ == "__main__":

    filters = None
    if len(sys.argv) > 1:
        filters = sys.argv[1:]

    git_visitor_base.do_visit(None, filters, visitor_pull)

