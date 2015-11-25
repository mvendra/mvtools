#!/usr/bin/env python

import sys
import os
from subprocess import check_output

def puaq(): # print usage and quit
    print("Usage: %s repo_path." % os.path.basename(__file__))
    sys.exit(1)

def is_git_work_tree(path):

    """ is_git_repo
    returns true if path exists and points to a git work tree ("/path/to/repo", instead of "/path/to/repo/.git")
    returns false otherwise
    returns None if path does not exist
    """

    if not os.path.exists(path):
        return None

    if os.path.exists(os.path.join(path, ".git")):
        return True
    else:
        return False

def get_remotes(repo):

    """ get_remotes
    returns a list with a repo's remotes.
    """

    t1 = is_git_work_tree(repo)
    if t1 is None:
        print("%s does not exist." % repo)
        return None
    elif t1 is False:
        print("%s is not a git work tree." % repo)
        return None

    try:
        out = check_output(["git", "-C", repo, "remote"])
    except OSError as oe:
        print("Unable to call git. Make sure it is installed.")
        exit(1)

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

    t1 = is_git_work_tree(repo)
    if t1 is None:
        print("%s does not exist." % repo)
        return None
    elif t1 is False:
        print("%s is not a git work tree." % repo)
        return None

    try:
        out = check_output(["git", "-C", repo, "branch"])
    except OSError as oe:
        print("Unable to call git. Make sure it is installed.")
        exit(1)

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

    t1 = is_git_work_tree(repo)
    if t1 is None:
        print("%s does not exist." % repo)
        return None
    elif t1 is False:
        print("%s is not a git work tree." % repo)
        return None

    current_branch = get_branches(repo)
    if current_branch is None:
        print("Failed querying the current branch of %s." % repo)
        return None

    return current_branch[0]

def get_staged_files(repo):

    """ get_staged_files
    on success, returns a list of staged files on the given repo
    on failure, returns None
    """

    t1 = is_git_work_tree(repo)
    if t1 is None:
        print("%s does not exist." % repo)
        return None
    elif t1 is False:
        print("%s is not a git work tree." % repo)
        return None

    ret = []

    try:
        out = check_output(["git", "-C", repo, "status", "--porcelain"])
    except OSError as oe:
        print("Unable to call git. Make sure it is installed.")
        exit(1)

    out = out.strip() # removes the trailing newline
    for l in out.split("\n"):
          lf = l[3:]
          fp = os.path.join(repo, lf)
          ret.append(fp)

    return ret

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    repopath = sys.argv[1]
    t1 = is_git_work_tree(repopath)
    if t1 is None:
        print("%s does not exist." % repopath)
        sys.exit(1)
    elif t1 is False:
        print("%s is not a git work tree." % repopath)
        sys.exit(1)

    print("branches: %s" % get_branches(repopath))
    print("remotes: %s" % get_remotes(repopath))

