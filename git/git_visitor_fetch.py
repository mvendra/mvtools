#!/usr/bin/env python

import git_visitor_base
import git_repo_query
import git_fetch

def visitor_fetch(repos):

    ORIGINAL_COLOR = "\033[0m" # mvtodo: would be better to try to detect the terminal's current standard color

    report = []
    for rp in repos:
        remotes = git_repo_query.get_remotes(rp)
        report_piece = git_fetch.do_fetch(rp, remotes)
        for ri in report_piece:
            report.append(ri)

    print("\nRESULTS:")
    for p in report:
        print(p)
    print("%s\n" % ORIGINAL_COLOR) # reset terminal color

if __name__ == "__main__":
    git_visitor_base.do_visit(None, visitor_fetch)

