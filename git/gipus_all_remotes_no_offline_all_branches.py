#!/usr/bin/env python

import sys
import os
import git_repo_query
import git_push

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

    # removes the offline remote
    aux = remotes
    remotes = []
    for r in aux:
        if r != "offline":
            remotes.append(r)

    ORIGINAL_COLOR = "\033[0m" # mvtodo: would be better to try to detect the terminal's current standard color
    report = git_push.do_push(repo_path, remotes, branches)

    print("\nRESULTS:")
    for p in report:
        print(p)
    print("%s" % ORIGINAL_COLOR) # reset terminal color

