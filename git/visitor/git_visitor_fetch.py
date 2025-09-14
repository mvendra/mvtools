#!/usr/bin/env python

import sys

import terminal_colors

import git_visitor_base
import git_lib
import git_fetch

def visitor_fetch(repos, options):

    ORIGINAL_COLOR = terminal_colors.get_standard_color()

    report = []
    all_passed = True
    for rp in repos:
        v, r = git_lib.get_remotes(rp)
        if not v:
            all_passed = False
            report.append("visitor_fetch failed [%s]: [%s]" % (rp, r))
            continue
        remotes = r
        remotes = git_visitor_base.filter_remotes(remotes, options)
        if remotes is None:
            report.append("%s%s: Failed filtering remotes.%s" % (terminal_colors.TTY_RED, rp, ORIGINAL_COLOR)) 
            continue
        op_piece, report_piece = git_fetch.do_fetch(rp, remotes)
        all_passed = all_passed and (not op_piece)
        for ri in report_piece:
            report.append(ri)

    git_visitor_base.print_report(all_passed, report)
    return all_passed

if __name__ == "__main__":

    filters = None
    if len(sys.argv) > 1:
        filters = sys.argv[1:]

    r = git_visitor_base.do_visit(None, filters, visitor_fetch)
    if False in r:
        sys.exit(1)
