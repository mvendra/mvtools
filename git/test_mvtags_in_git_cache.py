#!/usr/bin/env python

import sys
import os

def puaq():
    print("Usage: %s repo_path" % os.path.basename(__file__))
    sys.exit(1)

def check_mvtags(repo):

    """ check_mvtags
    searches a repo for mvtags, but only on cached (staged) files
    returns a list of staged files with mvtags, when any is found
    or returns None when no mvtags are found on the given repository
    """

    # mvtodo: implement
    return None

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    repo = sys.argv[1]

    report = check_mvtags(repo)
    if report is None:
        exit(0)
    else:
        print(report)
        exit(1)

