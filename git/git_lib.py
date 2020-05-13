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

def remove_gitlog_decorations(commitmsg):

    res = commitmsg

    # cut out first four lines (commit, author, date, \n)
    nl = -1
    for x in range(4):
        nl = res.find("\n", nl+1)
        if nl == -1:
            return None
    res = res[nl+1:]

    # remove the remaining commits
    remaining = res.find("\ncommit")
    if remaining != -1: # this could be the only commit. so we will only try to cut if there's more
        res = res[:remaining] 

    # remove the trailing last newline
    nl = res.rfind("\n")
    if nl == -1:
        return None
    res = res[:nl]

    # remove the indentation before each line
    res_lines = res.split("\n")
    res = ""
    for line in res_lines:
        line = line[4:]
        res += line + "\n"
    res = res[:len(res)-1] # the above code will always add a newline at the end of each line. this renders the last line "incorrect". lets fix it.

    return res

def is_repo_root(path):
    if path is None:
        return False
    if not os.path.exists(path):
        return False
    if path_utils.basename_filtered(path).endswith(".git"):
        return True
    return False

def git_discover_repo_root(repo_path):
    curpath = repo_path
    while not is_repo_root(path_utils.concat_path(curpath, ".git")):
        curpath = path_utils.backpedal_path(curpath)
        if curpath is None:
            return None
    return curpath

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

def is_repo_bare(repo):

    v, r = git_wrapper.rev_parse_is_bare_repo(repo)
    if not v:
        return False, "git_lib.is_repo_bare failed: %s" % r
    return True, "true" in r

def is_repo_working_tree(repo):

    v, r = git_wrapper.rev_parse_is_inside_work_tree(repo)
    if not v:
        return False, "git_lib.is_repo_working_tree failed: %s" % r
    return True, "true" in r

def is_repo_standard(repo):

    v, r = is_repo_working_tree(repo)
    if not v:
        return False, "git_lib.is_repo_standard failed: %s" % r

    the_git_obj = path_utils.concat_path(repo, ".git")
    if not os.path.exists( the_git_obj ):
        return False, "git_lib.is_repo_standard failed: %s does not exist" % the_git_obj

    if os.path.isdir(the_git_obj):
        return True, True
    return True, False

def is_repo_submodule(repo):

    v, r = is_repo_working_tree(repo)
    if not v:
        return False, "git_lib.is_repo_submodule failed: %s" % r

    the_git_obj = path_utils.concat_path(path, ".git")
    if not os.path.exists( the_git_obj ):
        return False, "git_lib.is_repo_submodule failed: %s does not exist" % the_git_obj

    if not os.path.isdir(the_git_obj):
        return True, True
    return True, False

if __name__ == "__main__":
    print("Hello from %s" % os.path.basename(__file__))
