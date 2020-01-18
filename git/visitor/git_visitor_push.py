#!/usr/bin/env python3

import terminal_colors

import git_visitor_base
import git_push

import sys

def visitor_push(repos, options):

    ORIGINAL_COLOR = terminal_colors.get_standard_color() 

    report = []
    all_passed = True
    for rp in repos:

        try:
            remotes, branches = git_visitor_base.apply_filters(rp, options)
        except git_visitor_base.gvbexcept as gvbex:
            all_passed = False
            report.append("%s%s: %s.%s" % (terminal_colors.TTY_RED, rp, gvbex.message, ORIGINAL_COLOR)) 
            continue

        op_piece, report_piece = git_push.do_push(rp, remotes, branches)
        all_passed = all_passed and (not op_piece)
        for ri in report_piece:
            report.append(ri)

    git_visitor_base.print_report(all_passed, report)    
    return all_passed

if __name__ == "__main__":

    repos = []

    c=0
    for n in sys.argv[1:]:
        c+=1
        if n == "--repo-base":
            if len(sys.argv) > c:
                repos.append(sys.argv[c+1])

    if len(repos) == 0:
        repos = None

    filters = None
    if len(sys.argv) > 1:
        filters = sys.argv[1:]

    r = git_visitor_base.do_visit(repos, filters, visitor_push)
    if False in r:
        sys.exit(1)

