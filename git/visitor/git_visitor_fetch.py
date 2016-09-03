#!/usr/bin/env python

import terminal_colors

import git_visitor_base
import git_repo_query
import git_fetch

import sys

def visitor_fetch(repos, options):

    ORIGINAL_COLOR = terminal_colors.get_standard_color()

    report = []
    all_passed = True
    for rp in repos:
        remotes = git_repo_query.get_remotes(rp)
        remotes = git_visitor_base.filter_remotes(remotes, options)
        if remotes is None:
            report.append("%s%s: Failed filtering remotes.%s" % (terminal_colors.TTY_RED, rp, ORIGINAL_COLOR)) 
            continue
        op_piece, report_piece = git_fetch.do_fetch(rp, remotes)
        all_passed = all_passed and (not op_piece)
        for ri in report_piece:
            report.append(ri)

    git_visitor_base.print_report(all_passed, report)

if __name__ == "__main__":

    filters = None
    if len(sys.argv) > 1:
        filters = sys.argv[1:]

    git_visitor_base.do_visit(None, filters, visitor_fetch)

