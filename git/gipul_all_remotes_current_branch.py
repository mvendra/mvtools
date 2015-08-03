#!/usr/bin/env python

import sys
import os
import git_repo_query
from subprocess import check_output

def puaq(): # print usage and quit
    print("Usage: %s repo_path (.git folder included)." % os.path.basename(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    repo_path = sys.argv[1]

    remotes = git_repo_query.get_remotes(repo_path)
    branches = git_repo_query.get_branches(repo_path)

    if branches is None:
        print("No branches detected in %s. Aborting." % repo_path)
        sys.exit(1)

    if remotes is None:
        print("No remotes detected in %s. Aborting." % repo_path)
        sys.exit(1)

    current_branch = branches[0]

    report = []
    for r in remotes:
        print("Pulling from %s..." % r)
        try:
            out = check_output(["git", "--git-dir=%s" % repo_path, "--work-tree=%s" % os.path.dirname(repo_path), "pull", "--ff-only", r, current_branch])
            out = "OK."
        except:
            out = "Failed."
        report.append("%s: %s" % (r, out))

    print("\nRESULTS:")
    for p in report:
        print(p)

