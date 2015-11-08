#!/usr/bin/env python

import git_visitor_base
import git_pull

import sys

def visitor_pull(repos, options):

    ORIGINAL_COLOR = "\033[0m" # mvtodo: would be better to try to detect the terminal's current standard color

    report = []
    for rp in repos:

        try:
            remotes, branches = git_visitor_base.apply_filters(rp, options)
        except git_visitor_base.gvbexcept as gvbex:
            report.append("\033[31m%s: %s.\033[0m" % (gvbex.message, rp)) # those colors are RED and WHITE, respectively. mvtodo: also change them here eventually
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

