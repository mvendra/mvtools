#!/usr/bin/env python3

import sys
import os

import git_wrapper
import path_utils

def generic_parse(str_line, separator):
    if str_line is None:
        return None
    n = str_line.find(separator)
    if n == -1:
        return None
    return str_line[:n]

def get_stash_name(str_line):
    return generic_parse(str_line, ":")

def get_prev_hash(str_line):
    return generic_parse(str_line, " ")

def is_git_work_tree(path):

    """ is_git_repo
    returns true if path exists and points to a git work tree ("/path/to/repo", instead of "/path/to/repo/.git")
    returns false otherwise
    returns None if path does not exist
    """

    if not os.path.exists(path):
        return None

    if os.path.exists(path_utils.concat_path(path, ".git")):
        return True
    else:
        return False

def get_remotes(repo):

    """ get_remotes
    returns a 3-level dictionary containing remotes information
    example:
    { 'offline': {'push': 'local/path1', 'fetch': 'local/path2'},
      'private': {'push': 'git@remote/path.git', 'fetch': 'git@remote/path.git'} }
    returns None on failures
    """

    t1 = is_git_work_tree(repo)
    if t1 is None:
        print("%s does not exist." % repo)
        return None
    elif t1 is False:
        print("%s is not a git work tree." % repo)
        return None

    v, r = git_wrapper.remote_list(repo)
    if not v:
        print("get_remotes failed: %s" % r)
        return None
    filtered_list = r.split() # removes the trailing newline

    # has to return multiples of 3 (name_remote, remote_path, (fetch/push))
    if len(filtered_list) == 0:
        return None
    elif len(filtered_list) % 3 != 0:
        return None
    elif (len(filtered_list) / 3) % 2 != 0:
        return None

    ret_dict = {}

    for i in range(0, len(filtered_list), 3):
        remote_name = filtered_list[i]
        remote_path = filtered_list[i+1]
        remote_operation = filtered_list[i+2]
        remote_operation = remote_operation[1:len(remote_operation)-1] # removes the encasing parenthesis

        if remote_name in ret_dict:
            ret_dict[remote_name][remote_operation] = remote_path
        else:
            ret_dict[remote_name] = {remote_operation: remote_path}

    return ret_dict

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

    v, r = git_wrapper.branch(repo)
    if not v:
        print("get_branches failed: %s" % r)
        return None
    branch_list = r.split("\n")

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

    v, r = git_wrapper.status(repo)
    if not v:
        print("get_staged_files failed: %s" % r)
        return None
    out = r.strip() # removes the trailing newline

    if len(out) == 0:
        return ""
    for l in out.split("\n"):
        cl = l.strip()
        if len(cl) == 0:
            continue
        if cl[0] == "A":
            lf = cl[3:]
            fp = path_utils.concat_path(repo, lf)
            ret.append(fp)

    if len(ret) == 0:
        return ""
    return ret

def get_unstaged_files(repo):

    """ get_unstaged_files
    on success, returns a list of unstaged files on the given repo
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

    v, r = git_wrapper.status(repo)
    if not v:
        print("get_unstaged_files failed: %s" % r)
        return None
    out = r.strip() # removes the trailing newline

    if len(out) == 0:
        return ""
    for l in out.split("\n"):
        cl = l.strip()
        if len(cl) == 0:
            continue
        if cl[0] == "?":
            lf = cl[3:]
            fp = path_utils.concat_path(repo, lf)
            ret.append(fp)

    if len(ret) == 0:
        return ""
    return ret

def get_stash_list(repo):

    v, r = git_wrapper.stash_list(repo)
    if not v:
        return False, r
    stash_list = [get_stash_name(x) for x in r.split(os.linesep) if x != ""]
    return True, stash_list

def get_previous_hash_list(repo, num_previous):

    v, r = git_wrapper.log_oneline(repo)
    if not v:
        return False, r
    prev_list = [get_prev_hash(x) for x in r.split(os.linesep) if x != ""]
    return True, prev_list

def get_list_unversioned_files(repo):

    v, r = git_wrapper.ls_files(repo)
    if not v:
        return False, r
    unversioned_files = [x for x in r.split(os.linesep) if x != ""]
    return True, unversioned_files

def puaq(): # print usage and quit
    print("Usage: %s repo_path." % os.path.basename(__file__))
    sys.exit(1)

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
