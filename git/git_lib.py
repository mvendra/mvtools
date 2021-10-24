#!/usr/bin/env python3

import sys
import os

import git_wrapper
import path_utils
import string_utils

def change_stash_index(stash_name, index):
    if stash_name is None or index is None:
        return None
    idx_begin = stash_name.rfind("{")
    idx_end = stash_name.rfind("}")
    if idx_begin == -1 or idx_end == -1:
        return None
    if idx_begin == 0 or idx_end == 0:
        return None
    if idx_begin > idx_end:
        return None
    new_stash_name = "%s%d%s" % (stash_name[:idx_begin+1], index, stash_name[idx_end:])
    return new_stash_name

def get_stash_name(str_line):
    return string_utils.generic_parse(str_line, ":")

def get_prev_hash(str_line):
    return string_utils.generic_parse(str_line, " ")

def get_renamed_details(renamed_msg):

    if renamed_msg is None:
        return None

    filename_original = None
    filename_renamed = None

    n = renamed_msg.find("->")
    if n == -1 or n == 0:
        return None

    filename_original = renamed_msg[:n-1]
    filename_renamed = (renamed_msg[n+2:]).lstrip()

    return (filename_original, filename_renamed)

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

def remove_gitstatus_simple_decorations(statusmsg_singleline):
    if statusmsg_singleline is None:
        return None
    if len(statusmsg_singleline) < 4:
        return None
    if statusmsg_singleline[2] != " ":
        return None
    return statusmsg_singleline[3:]

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

    # is_head_clear is a misnomer, because this will also take into consideration staged, unversioned, etc.

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

def get_head_files(repo):

    total_entries = []

    funcs = [get_head_modified_files, get_head_deleted_files, get_head_updated_files]

    for f in funcs:
        v, r = f(repo)
        if not v:
            return False, r
        total_entries += r

    return True, total_entries

def get_head_modified_files(repo):
    return get_head_files_delegate(repo, " M", "modified")

def get_head_deleted_files(repo):
    return get_head_files_delegate(repo, " D", "deleted")

def get_head_updated_files(repo):
    return get_head_files_delegate(repo, "UU", "updated")

def get_head_updated_deleted_files(repo):
    return get_head_files_delegate(repo, "UD", "updated_deleted")

def get_head_files_delegate(repo, status_detect, info_variation):

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
        return False, "get_head_%s_files failed: %s" % (info_variation, r)
    out = r.rstrip() # removes the trailing newline
    if len(out) == 0:
        return True, []

    ret = []
    for l in out.split("\n"):
        cl = l.rstrip()
        if len(cl) < 2:
            continue
        if cl[0:2] == status_detect:
            lf = cl[3:]
            fp = path_utils.concat_path(repo, lf)
            ret.append(os.path.abspath(fp))
    return True, ret

def get_staged_files(repo):

    all_staged_files = []

    v, r = get_staged_delegate(repo, ["M", "A", "D", "C", "U"])
    if not v:
        return False, r
    all_staged_files += r

    v, r = get_staged_renamed_files(repo)
    if not v:
        return False, r
    for x in r:
        all_staged_files.append(x[1])

    return True, all_staged_files

def get_staged_deleted_files(repo):
    return get_staged_delegate(repo, ["D"])

def get_staged_renamed_files(repo):

    v, r = get_staged_delegate(repo, ["R"])
    if not v:
        return False, r
    renamed_list = r

    repo_local = os.path.abspath(repo)

    renamed_list_filtered = []
    for rl in renamed_list:

        r = get_renamed_details(rl)
        if r is None:
            return False, "Unable to read out and parse staged, renamed files from repo [%s]" % repo_local
        original_fn = r[0]
        renamed_fn  = r[1]

        renamed_list_filtered.append( (original_fn, path_utils.concat_path(repo_local, renamed_fn)) )

    return True, renamed_list_filtered

def get_staged_delegate(repo, check_chars):

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
        if cl[0] in check_chars:
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

def get_unversioned_files_and_folders(repo):

    # this version of "get_unversioned_files" will return a folder, if that entire folder
    # contains unversioned files only. empty folders, alone, will not be returned (as per Git's design).

    if repo is None:
        return False, "No repo specified"
    repo = os.path.abspath(repo)

    v, r = git_wrapper.status_simple(repo)
    if not v:
        return False, r
    saved_st_msg = r
    status_items = [x for x in r.split(os.linesep) if x != ""]

    unversioned_files = []
    for si in status_items:
        if len(si) < 4:
            return False, "Invalid status message returned. Repo: [%s]. Status msg: [%s]" % (repo, saved_st_msg)
        if si[0:2] == "??":
            si_filtered = remove_gitstatus_simple_decorations(si)
            if si_filtered is None:
                return False, "Invalid status message returned (detected while filtering). Repo: [%s]. Status msg: [%s]" % (repo, saved_st_msg)
            unversioned_files.append(path_utils.concat_path(repo, si_filtered))

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

def get_previous_hash_list(repo, num_previous = None):

    if repo is None:
        return False, "No repo specified"

    repo = os.path.abspath(repo)

    v, r = git_wrapper.log_oneline(repo, num_previous)
    if not v:
        return False, r
    prev_list = [get_prev_hash(x) for x in r.split(os.linesep) if x != ""]
    return True, prev_list

def get_head_hash(repo):

    if repo is None:
        return False, "No repo specified"

    repo = os.path.abspath(repo)

    v, r = get_previous_hash_list(repo, 1)
    if not v:
        return False, "git_lib.get_head_hash failed: [%s]" % r

    return True, r[0]

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

def clone_bare(repo_source, repo_target):
    if repo_source is None:
        return False, "No source repo specified"
    if repo_target is None:
        return False, "No target repo specified"
    repo_source = os.path.abspath(repo_source)
    repo_target = os.path.abspath(repo_target)
    return git_wrapper.clone_bare(repo_source, repo_target)

def clone(repo_source, repo_target, remotename=None):
    if repo_source is None:
        return False, "No source repo specified"
    if repo_target is None:
        return False, "No target repo specified"
    repo_source = os.path.abspath(repo_source)
    repo_target = os.path.abspath(repo_target)
    return git_wrapper.clone(repo_source, repo_target, remotename)

def clone_ext(repo_source, repo_target, remotename=None):
    if repo_source is None:
        return False, "No source repo specified"
    if repo_target is None:
        return False, "No target repo specified"
    repo_source = os.path.abspath(repo_source)
    repo_target = os.path.abspath(repo_target)
    return git_wrapper.clone_ext(repo_source, repo_target, remotename)

def pull_default(repo):
    if repo is None:
        return False, "No repo specified"
    repo = os.path.abspath(repo)
    return git_wrapper.pull_default(repo)

def pull(repo, remote, branch):
    if repo is None:
        return False, "No repo specified"
    repo = os.path.abspath(repo)
    return git_wrapper.pull(repo, remote, branch)

def push(repo, remote, branch):
    if repo is None:
        return False, "No repo specified"
    repo = os.path.abspath(repo)
    return git_wrapper.push(repo, remote, branch)

def log(repo, limit=None):
    if repo is None:
        return False, "No repo specified"
    repo = os.path.abspath(repo)
    return git_wrapper.log(repo, limit)

def fetch_multiple(repo, remotes):
    if repo is None:
        return False, "No repo specified"
    repo = os.path.abspath(repo)
    return git_wrapper.fetch_multiple(repo, remotes)

def fetch_all(repo):
    if repo is None:
        return False, "No repo specified"
    repo = os.path.abspath(repo)
    return git_wrapper.fetch_all(repo)

def diff(repo, file_list=None):
    if repo is None:
        return False, "No repo specified"
    repo = os.path.abspath(repo)
    final_file_list = []
    if file_list is None:
        final_file_list = None
    elif isinstance(file_list, str):
        final_file_list.append(os.path.abspath(file_list))
    elif isinstance(file_list, list):
        for fl in file_list:
            final_file_list.append(os.path.abspath(fl))
    else:
        return False, "file_list is invalid: [%s]" % file_list
    return git_wrapper.diff(repo, final_file_list)

def diff_cached(repo, file_list=None):
    if repo is None:
        return False, "No repo specified"
    repo = os.path.abspath(repo)
    final_file_list = []
    if file_list is None:
        final_file_list = None
    elif isinstance(file_list, str):
        final_file_list.append(os.path.abspath(file_list))
    elif isinstance(file_list, list):
        for fl in file_list:
            final_file_list.append(os.path.abspath(fl))
    else:
        return False, "file_list is invalid: [%s]" % file_list
    return git_wrapper.diff_cached(repo, final_file_list)

def rev_parse_head(repo):
    if repo is None:
        return False, "No repo specified"
    repo = os.path.abspath(repo)
    return git_wrapper.rev_parse_head(repo)

def stash_show(repo, stash_name):
    if repo is None:
        return False, "No repo specified"
    repo = os.path.abspath(repo)
    return git_wrapper.stash_show(repo, stash_name)

def stash_clear(repo):
    if repo is None:
        return False, "No repo specified"
    repo = os.path.abspath(repo)
    return git_wrapper.stash_clear(repo)

def stash_drop(repo, stash_name = None):
    if repo is None:
        return False, "No repo specified"
    repo = os.path.abspath(repo)
    return git_wrapper.stash_drop(repo, stash_name)

def stash_pop(repo):
    if repo is None:
        return False, "No repo specified"
    repo = os.path.abspath(repo)
    return git_wrapper.stash_pop(repo)

def show(repo, commit_id):
    if repo is None:
        return False, "No repo specified"
    repo = os.path.abspath(repo)
    return git_wrapper.show(repo, commit_id)

def checkout(repo, file_list=None):
    if repo is None:
        return False, "No repo specified"
    repo = os.path.abspath(repo)
    final_file_list = []
    if file_list is None:
        final_file_list = None
    elif isinstance(file_list, str):
        final_file_list.append(os.path.abspath(file_list))
    elif isinstance(file_list, list):
        for fl in file_list:
            final_file_list.append(os.path.abspath(fl))
    else:
        return False, "file_list is invalid: [%s]" % file_list
    return git_wrapper.checkout(repo, final_file_list)

def config(key, value, global_cfg=True):
    if key is None:
        return False, "key unspecified"
    return git_wrapper.config(key, value, global_cfg)

def commit_editor(repo):
    if repo is None:
        return False, "No repo specified"
    repo = os.path.abspath(repo)
    return git_wrapper.commit_editor(repo)

def commit_direct(repo, params):
    if repo is None:
        return False, "No repo specified"
    repo = os.path.abspath(repo)
    return git_wrapper.commit_direct(repo, params)

def remote_change_url(repo, remote, new_url):
    if repo is None:
        return False, "No repo specified"
    repo = os.path.abspath(repo)
    return git_wrapper.remote_change_url(repo, remote, new_url)

def status_simple(repo):
    if repo is None:
        return False, "No repo specified"
    repo = os.path.abspath(repo)
    return git_wrapper.status_simple(repo)

def kill_previous(repo, num_previous):
    if repo is None:
        return False, "No repo specified"
    if num_previous is None:
        return False, "previous quantity unspecified"
    repo = os.path.abspath(repo)
    return git_wrapper.reset_hard_head(repo, num_previous)

if __name__ == "__main__":
    print("Hello from %s" % path_utils.basename_filtered(__file__))
