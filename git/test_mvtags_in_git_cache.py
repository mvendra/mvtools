#!/usr/bin/env python3

import sys
import os

import git_wrapper
import git_repo_query

def puaq():
    print("Usage: %s repo_path" % os.path.basename(__file__))
    sys.exit(1)

def check_mvtags_in_file(repo, thefile):

    """ check_mvtags_in_file
    returns true if thefile has mvtags in it
    returns false otherwise
    returns None upon errors
    """

    if not os.path.exists(thefile):
        return None

    v, r = git_wrapper.diff(repo, True, thefile)
    if not v:
        print("Check mvtags failed: %s" % r)
        return None
    contents = r.strip().lower()

    # remove first 5 lines
    nl = -1
    for x in range(5):
        nl = contents.find("\n", nl+1)
        if nl == -1:
            return None
    contents = contents[nl+1:]

    for l in contents.split("\n"):
        if l[0] == "+":
            r = l.find("mvtodo")
            if r != -1:
                return True
            r = l.find("mvdebug")
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
    if files is None:
        print("Failed querying %s. Aborting." % repo)
        return None

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
            print("%s introduces mvtags" % r)
        exit(1)

