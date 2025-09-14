#!/usr/bin/env python

import os
import sys

import git_visitor_base
import git_lib
import git_remote

def change_path(local_path, remote_name, remote_operation, remote_path):
    # here's your chance to evaluate what comes in, and change it
    # accordingly - by returning True to indicate a "go ahead and change"
    # plus the new remote url/path
    return False, remote_path

def visitor_remote_refactor(repos, options):

    report = []
    all_passed = True

    for rp in repos:
        v, r = git_lib.get_remotes(rp)
        if not v:
            all_passed = False
            report.append("visitor_remote_refactor failed [%s]: [%s]" % (rp, r))
            continue
        remotes = r
        if remotes == {}:
            continue
        for rmn in remotes:
            for rmop in remotes[rmn]:

                diff, new_url = change_path(rp, rmn, rmop, remotes[rmn][rmop])
                if diff:
                    op_piece, report_piece = git_remote.remote_change_url(rp, rmn, rmop, new_url)
                    all_passed = all_passed and (not op_piece)
                    report.append(report_piece)

    git_visitor_base.print_report(all_passed, report)
    return all_passed

if __name__ == "__main__":
    r = git_visitor_base.do_visit(None, None, visitor_remote_refactor)
    if False in r:
        sys.exit(1)
