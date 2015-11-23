#!/usr/bin/env python

import sys
import os
from subprocess import check_output

import git_repo_query

def puaq():
    print("Usage: %s repo_path" % os.path.basename(__file__))
    sys.exit(1)

def check_mvtags_in_file(repo, thefile):

    """ check_mvtags_in_file
    returns true if thefile has mvtags in it
    returns false otherwise
    returns None if thefile does not exist
    """

    if not os.path.exists(thefile):
        return None

    cmd = ["git", "-C", repo, "diff", "--no-ext-diff", "--cached", thefile]
    out = check_output(cmd)
    out = out.strip()

    # mvtodo: need to clean up out and consider only the new additions

    r = out.find("mvtodo")
    if r != -1:
        return True
    r = out.find("mvdebug")
    if r != -1:
        return True

    return False

def check_mvtags_in_repo(repo):

    """ check_mvtags_in_repo
    searches a repo for mvtags, but only on cached (staged) files
    and only in the introduced changes.
    returns a list of staged files with mvtags, when any is found.
    returns an empty list when none is found.
    """

    ret = []

    files = git_repo_query.get_staged_files(repo)
    for f in files:
        if check_mvtags_in_file(repo, f):
            ret.append(f)

    return ret

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    repo = sys.argv[1]

    if not os.path.exists(repo):
        print("%s does not exist. Aborting." % repo)
        exit(2)

    report = check_mvtags_in_repo(repo)
    if len(report) == 0:
        exit(0)
    else:
        for r in report:
            print("%s has mvtags" % r)
        exit(1)

