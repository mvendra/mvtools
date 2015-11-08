#!/usr/bin/env python

import sys
import os
from subprocess import check_output

def puaq(): # print usage and quit
    print("Usage: %s repo_path (.git folder included)." % os.path.basename(__file__))
    sys.exit(1)

def get_remotes(repo):

    """ get_remotes
    returns a list with a repo's remotes.
    """

    if not os.path.exists(repo):
        print("%s does not exist." % repo)
        return None
    if not (repo.endswith(".git") or repo.endswith(".git" + os.sep)):
        print("%s does not point to a .git repository." % repo)
        return None

    out = check_output(["git", "--git-dir=%s" % repo, "--work-tree=%s" % os.path.dirname(repo), "remote"])
    ret_list = out.split()
    if len(ret_list) > 0:
        return ret_list
    else:
        return None

def get_branches(repo):

    """ get branches
    on sucess, returns a list with a repo's branches. the first item in the list is the checked out branch
    on failure, returns None
    """

    if not os.path.exists(repo):
        print("%s does not exist." % repo)
        return None
    if not (repo.endswith(".git") or repo.endswith(".git" + os.sep)):
        print("%s does not point to a .git repository." % repo)
        return None

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

def get_current_branch(repo):

    """ get_current_branch
    on success, returns the name of the checked out branch
    on failure, returns None
    """

    current_branch = get_branches(repo)
    if current_branch is None:
        print("Failed querying the current branch of %s." % repo)
        return None

    return current_branch[0]

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    repopath = sys.argv[1]
    if not os.path.exists(repopath):
        print("%s does not exist. Aborting." % repopath)
        sys.exit(1)

    print("branches: %s" % get_branches(repopath))
    print("remotes: %s" % get_remotes(repopath))

