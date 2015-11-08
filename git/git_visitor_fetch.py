#!/usr/bin/env python

import git_visitor_base
import git_repo_query
import git_fetch

import sys

def visitor_fetch(repos, options):

    ORIGINAL_COLOR = "\033[0m" # mvtodo: would be better to try to detect the terminal's current standard color

    report = []
    for rp in repos:
        remotes = git_repo_query.get_remotes(rp)
        remotes = git_visitor_base.filter_remotes(remotes, options)
        if remotes is None:
            report.append("\033[31m%s: Failed filtering remotes\033[0m" % rp) # those colors are RED and WHITE, respectively. mvtodo: also change them here eventually
            continue
        report_piece = git_fetch.do_fetch(rp, remotes)
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

    git_visitor_base.do_visit(None, filters, visitor_fetch)

