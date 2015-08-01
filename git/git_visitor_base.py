#!/usr/bin/env python

import sys
import os
import fsquery
from subprocess import check_output

def puaq():
    print("Usage: %s base_path." % os.path.basename(__file__))
    sys.exit(1)

def __filter_git_only(thelist):
    ret = []
    for d in thelist:
        if os.path.basename(d) == ".git":
            ret.append(d)
    return ret

def make_repo_list(path):

    """ make_repo_list
    returns a list of git repositories found in the given base path
    """

    ret_list = fsquery.makecontentlist(path, True, False, True, False, True, [])
    ret_list = __filter_git_only(ret_list)
    if len(ret_list) > 0:
        return ret_list
    else:
        return None

def get_remotes(repo):

    """ get_remotes
    returns a list with a repo's remotes.
    """

    out = check_output(["git", "--git-dir=%s" % repo, "--work-tree=%s" % os.path.dirname(repo), "remote"])
    ret_list = out.split()
    if len(ret_list) > 0:
        return ret_list
    else:
        return None

def get_branches(repo):

    """ get branches
    returns a list with a repo's branches. the first item in the list is the checked out branch
    """

    out = check_output(["git", "--git-dir=%s" % repo, "--work-tree=%s" % os.path.dirname(repo), "branch"])
    branch_list = out.split("\n")

    # move the checked out branch to the front
    for i in branch_list:
        if i.startswith("*"):
            branch_list.remove(i)
            branch_list = [i[2:]] + branch_list
            break;

    # remove blank spaces
    if "" in branch_list:
        branch_list.remove("")

    # trim branch strings
    ret_list = []
    for i in branch_list:
        ret_list.append(i.strip())

    if len(ret_list) > 0:
        return ret_list
    else:
        return None

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    basepath = sys.argv[1]
    if not os.path.exists(basepath):
        print("%s does not exist. Aborting." % basepath)
        sys.exit(1)

    for r in make_repo_list(basepath):
        print("repo: %s" % r)
        print("branches: %s" % get_branches(r))
        print("remotes: %s" % get_remotes(r))

