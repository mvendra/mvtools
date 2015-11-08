#!/usr/bin/env python

import git_visitor_base
import git_repo_query
import git_push

def visitor_push(repos, options):

    ORIGINAL_COLOR = "\033[0m" # mvtodo: would be better to try to detect the terminal's current standard color

    report = []
    for rp in repos:
        remotes = git_repo_query.get_remotes(rp)
        branches = git_repo_query.get_branches(rp)
        report_piece = git_push.do_push(rp, remotes, branches)
        for ri in report_piece:
            report.append(ri)

    print("\nRESULTS:")
    for p in report:
        print(p)
    print("%s\n" % ORIGINAL_COLOR) # reset terminal color

if __name__ == "__main__":
    git_visitor_base.do_visit(None, None, visitor_push)

