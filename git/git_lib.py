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

def is_char_status_staged(the_char):
    return the_char in ["A", "M", "R", "C", "U"]

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
        return None
    path = os.path.abspath(path)
    if path is None:
        return False
    if not os.path.exists(path):
        return False
    if path_utils.basename_filtered(path).endswith(".git"):
        return True
    return False

def discover_repo_root(repo):

    if repo is None:
        return None

    repo = os.path.abspath(repo)

    curpath = repo
    while not is_repo_root(path_utils.concat_path(curpath, ".git")):
        curpath = path_utils.backpedal_path(curpath)
        if curpath is None:
            return None
    return curpath

def is_head_clear(repo):

    if repo is None:
        return False, "No repo specified"

    repo = os.path.abspath(repo)

    v, r = git_wrapper.status_simple(repo)
    if not v:
        return False, r

    return True, (r.strip() == "")

def get_remotes(repo):

    if repo is None:
        return False, "No repo specified"

    repo = os.path.abspath(repo)

    """ get_remotes
    returns a 3-level dictionary containing remotes information
    example:
    { 'offline': {'push': 'local/path1', 'fetch': 'local/path2'},
      'private': {'push': 'git@remote/path.git', 'fetch': 'git@remote/path.git'} }
    returns False,error-msg_str on failures
    """

    t1 = is_repo_working_tree(repo)
    if t1 is None:
        return False, "%s does not exist." % repo
    elif t1 is False:
        return False, "%s is not a git work tree." % repo

    v, r = git_wrapper.remote_list(repo)
    if not v:
        return False, "get_remotes failed: %s" % r
    filtered_list = r.split() # removes the trailing newline

    # has to return multiples of 3 (name_remote, remote_path, (fetch/push))
    if len(filtered_list) == 0:
        return True, {} # no remotes
    elif len(filtered_list) % 3 != 0:
        return False, "could not detect remotes"
    elif (len(filtered_list) / 3) % 2 != 0:
        return False, "could not detect remotes"

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

    return True, ret_dict

def get_branches(repo):

    if repo is None:
        return False, "No repo specified"

    repo = os.path.abspath(repo)

    t1 = is_repo_working_tree(repo)
    if t1 is None:
        return False, "%s does not exist." % repo
    elif t1 is False:
        return False, "%s is not a git work tree." % repo

    v, r = git_wrapper.branch(repo)
    if not v:
        return False, "get_branches failed: %s" % r
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

    return True, ret_list

def get_current_branch(repo):

    if repo is None:
        return False, "No repo specified"

    repo = os.path.abspath(repo)

    t1 = is_repo_working_tree(repo)
    if t1 is None:
        return False, "%s does not exist." % repo
    elif t1 is False:
        return False, "%s is not a git work tree." % repo

    v, r = get_branches(repo)
    if not v:
        return False, "get_current_branch failed: [%s]" % r
    current_branch = r

    if len(current_branch) == 0:
        return True, None
    return True, current_branch[0]

def get_modified_files(repo):

    if repo is None:
        return False, "No repo specified"

    repo = os.path.abspath(repo)

    t1 = is_repo_working_tree(repo)
    if t1 is None:
        return False, "%s does not exist." % repo
    elif t1 is False:
        return False, "%s is not a git work tree." % repo

    v, r = git_wrapper.status(repo)
    if not v:
        return False, "get_modified_files failed: %s" % r
    out = r.rstrip() # removes the trailing newline
    if len(out) == 0:
        return True, []

    ret = []
    for l in out.split("\n"):
        cl = l.rstrip()
        if len(cl) < 2:
            continue
        if cl[0:2] == " M":
            lf = cl[3:]
            fp = path_utils.concat_path(repo, lf)
            ret.append(os.path.abspath(fp))
    return True, ret

def get_staged_files(repo):

    if repo is None:
        return False, "No repo specified"

    repo = os.path.abspath(repo)

    t1 = is_repo_working_tree(repo)
    if t1 is None:
        return False, "%s does not exist." % repo
    elif t1 is False:
        return False, "%s is not a git work tree." % repo

    v, r = git_wrapper.status(repo)
    if not v:
        return False, "get_staged_files failed: %s" % r
    out = r.rstrip() # removes the trailing newline
    if len(out) == 0:
        return True, []

    ret = []
    for l in out.split("\n"):
        cl = l.rstrip()
        if len(cl) < 2:
            continue
        if is_char_status_staged(cl[0]):
            lf = cl[3:]
            fp = path_utils.concat_path(repo, lf)
            ret.append(os.path.abspath(fp))
    return True, ret

def get_unversioned_files(repo):

    if repo is None:
        return False, "No repo specified"

    repo = os.path.abspath(repo)

    v, r = git_wrapper.ls_files(repo)
    if not v:
        return False, r
    unversioned_files = [path_utils.concat_path(repo, x) for x in r.split(os.linesep) if x != ""]
    return True, unversioned_files

def get_stash_list(repo):

    if repo is None:
        return False, "No repo specified"

    repo = os.path.abspath(repo)

    v, r = git_wrapper.stash_list(repo)
    if not v:
        return False, r
    stash_list = [get_stash_name(x) for x in r.split(os.linesep) if x != ""]
    return True, stash_list

def get_previous_hash_list(repo, num_previous):

    if repo is None:
        return False, "No repo specified"

    repo = os.path.abspath(repo)

    v, r = git_wrapper.log_oneline(repo)
    if not v:
        return False, r
    prev_list = [get_prev_hash(x) for x in r.split(os.linesep) if x != ""]
    return True, prev_list

def is_repo_working_tree(repo):

    if repo is None:
        return False, "No repo specified"

    repo = os.path.abspath(repo)

    v, r = git_wrapper.rev_parse_is_inside_work_tree(repo)
    if not v:
        if "not a git repository" in r:
            return True, False
        else:
            return False, "git_lib.is_repo_working_tree failed: %s" % r
    return True, "true" in r

def is_repo_bare(repo):

    if repo is None:
        return False, "No repo specified"

    repo = os.path.abspath(repo)

    v, r = git_wrapper.rev_parse_is_bare_repo(repo)
    if not v:
        return False, "git_lib.is_repo_bare failed: %s" % r
    bare_query_result = "true" in r

    if not bare_query_result:
        return True, False

    v, r = git_wrapper.rev_parse_absolute_git_dir(repo)
    if not v:
        return False, "git_lib.is_repo_bare failed: %s" % r
    abs_path_found = r

    if abs_path_found != repo:
        # is a subdirectory of a bare repo
        return True, False

    return True, True

def is_repo_standard(repo):

    if repo is None:
        return False, "No repo specified"

    repo = os.path.abspath(repo)

    v, r = is_repo_working_tree(repo)
    if not v:
        return False, "git_lib.is_repo_standard failed: %s" % r

    the_git_obj = path_utils.concat_path(repo, ".git")
    if os.path.isdir(the_git_obj):
        return True, True
    return True, False

def is_repo_submodule(repo):

    if repo is None:
        return False, "No repo specified"

    repo = os.path.abspath(repo)

    v, r = is_repo_working_tree(repo)
    if not v:
        return False, "git_lib.is_repo_submodule failed: %s" % r

    the_git_obj = path_utils.concat_path(repo, ".git")
    if not os.path.exists( the_git_obj ):
        return True, False

    if not os.path.isdir(the_git_obj):
        return True, True
    return True, False

def patch_as_head(repo, patch_file, override_head_check):

    if repo is None:
        return False, "No repo specified"

    if patch_file is None:
        return False, "No patch file specified"

    repo = os.path.abspath(repo)
    patch_file = os.path.abspath(patch_file)

    if not override_head_check:
        v, r = is_head_clear(repo)
        if not v:
            return False, r
        if not r:
            return False, "Cannot patch - head is not clear"

    v, r = git_wrapper.apply(repo, patch_file)
    if not v:
        return False, r

    return True, None

def patch_as_staged(repo, patch_file, override_head_check):

    if repo is None:
        return False, "No repo specified"

    if patch_file is None:
        return False, "No patch file specified"

    repo = os.path.abspath(repo)
    patch_file = os.path.abspath(patch_file)

    v, r = patch_as_head(repo, patch_file, override_head_check)
    if not v:
        return False, r

    v, r = git_wrapper.stage(repo)
    if not v:
        return False, r

    return True, None

def patch_as_stash(repo, patch_file, override_head_check, override_stash_check):

    if repo is None:
        return False, "No repo specified"

    if patch_file is None:
        return False, "No patch file specified"

    repo = os.path.abspath(repo)
    patch_file = os.path.abspath(patch_file)

    if not override_stash_check:
        v, r = get_stash_list(repo)
        if not v:
            return False, r
        if len(r) != 0:
            return False, "Cannot patch - stash is not empty"

    v, r = patch_as_head(repo, patch_file, override_head_check)
    if not v:
        return False, r

    v, r = git_wrapper.stash(repo)
    if not v:
        return False, r

    return True, None

def unstage(repo, file_list=None):

    if repo is None:
        return False, "No repo specified"

    repo = os.path.abspath(repo)
    file_list_final = []

    if file_list is not None:

        v, r = get_staged_files(repo)
        if not v:
            return False, "Can't unstage - unable to fetch staged files first: [%s]" % r
        staged_files = r

        for f in file_list:
            f_abs = os.path.abspath(f)
            if not f_abs in staged_files:
                return False, "File [%s] is not staged" % f_abs
            file_list_final.append(f_abs)

    return git_wrapper.reset_head(repo, file_list_final)

if __name__ == "__main__":
    print("Hello from %s" % path_utils.basename_filtered(__file__))
