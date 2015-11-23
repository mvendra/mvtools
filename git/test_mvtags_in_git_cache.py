#!/usr/bin/env python

import sys
import os

import git_repo_query

def puaq():
    print("Usage: %s repo_path" % os.path.basename(__file__))
    sys.exit(1)

def check_mvtags_in_file(thefile):

    """ check_mvtags_in_file
    returns true if thefile has mvtags in it
    returns false otherwise
    returns None if thefile does not exist
    """

    if not os.path.exists(thefile):
        return None

    # mvtodo: get the diff of thefile and check it for mvtags
    # mvtodo: if present, return True
    
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
        if check_mvtags_in_file(f):
            ret.append(f)

    return ret

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    repo = sys.argv[1]

    report = check_mvtags_in_repo(repo)
    if report is None:
        exit(0)
    else:
        print(report)
        exit(1)

