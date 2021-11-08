#!/usr/bin/env python3

import os

import path_utils
import fsquery
import mvtools_exception
import git_lib

import terminal_colors
import mvtools_envvars

class gvbexcept(RuntimeError):
    def __init__(self, msg):
        self._set_message(msg)
    def _get_message(self):
        return self._message
    def _set_message(self, message):
        self._message = message
    message = property(_get_message, _set_message)

def filter_git_only(path_list):

    """ filter_git_only
    given path_list, will filter elements if they point to a git repository (.git folder)
    returns a subset of path_list that do point to a git repository's git folder
    """

    ret = []
    for d in path_list:
        if path_utils.filter_remove_trailing_sep(d).endswith(".git"):
            ret.append(d)
    return ret

def pluck_dotgit(path_list):

    """ pluck_dotgit
    on success, returns a list that is a copy of the given list, with the trailing ".git" removed off the items
    returns None on failures
    """

    if path_list is None:
        return None

    ret_list = []
    for it in path_list:
        local_it = path_utils.filter_remove_trailing_sep(it)
        if local_it.endswith(".git"):
            local_it = path_utils.backpedal_path(local_it)
        ret_list.append(local_it)

    return ret_list

def filter_remotes(remotes, options):

    if remotes is None or options is None:
        return None

    """ filter_remotes
    on success, returns a 3-level dict of filtered remotes,
    according to passed |options|
    on failure, returns None

    valid options are:
    xor-remotename
    not-remotename

    xor-remoteop
    not-remoteop

    xor-remotepath
    not-remotepath

    possibly for the future:
    include xor-partial-match and not-partial-match
    (so it would be possible to more feasibly filter out certain paths)
    """

    remote_names = []
    remote_ops = []
    remote_paths = []

    for x in remotes:
        remote_names.append(x)
        for y in remotes[x]:
            if not y in remote_ops:
                remote_ops.append(y)
            if not remotes[x][y] in remote_paths:
                remote_paths.append(remotes[x][y])

    names_to_pick = []
    ops_to_pick = []
    paths_to_pick = []

    # FILTER REMOTE NAMES
    names_to_pick = assemble_pick_list("xor-remotename", "not-remotename", options, remote_names)

    # FILTER REMOTE OPERATIONS (fetch or push)
    ops_to_pick = assemble_pick_list("xor-remoteop", "not-remoteop", options, remote_ops)

    # FILTER REMOTE PATHS
    paths_to_pick = assemble_pick_list("xor-remotepath", "not-remotepath", options, remote_paths)

    ret_dict = {}
    for x in remotes:
        for y in remotes[x]:

            if (x in names_to_pick) and (y in ops_to_pick) and (remotes[x][y] in paths_to_pick):
                
                if x in ret_dict:
                    ret_dict[x][y] = remotes[x][y]
                else:
                    ret_dict[x] = {y: remotes[x][y]}

    return ret_dict

def assemble_pick_list(xor_opt, not_opt, options, candidate_list):

    """ assemble_pick_list
    applies xor and not operations, based on their presence (or lack thereof) inside |options|,
    onto candidate_list and return another list accordingly
    returns empty list on misparameterisation (passing a xor but not specifying it)
    """

    pick_list = []

    if xor_opt in options:
        if not options[xor_opt] in candidate_list:
            return [] # the xor'ed name must be available to begin with
        pick_list.append(options[xor_opt])
    else: # its either a xor-opt or a not-opt. cant have both.
        if not_opt in options:
            for it in candidate_list:
                if not it in options[not_opt]:
                    pick_list += [it]
        else:
            pick_list = candidate_list

    return pick_list

def apply_filters(repo, options):

    """ apply_filters
    on success, returns filtered remotes and branches
    on failure, raises gvbexcept with detail msg
    """

    v, r = git_lib.get_remotes(repo)
    if not v:
        raise gvbexcept("Unable to detect remotes for repo [%s]: [%s]" % (repo, r))
    elif v and r == {}:
        raise gvbexcept("No remotes detected for repo: [%s]" % repo)
    remotes = r

    remotes = filter_remotes(remotes, options)
    if remotes is None:
        raise gvbexcept("Failed filtering remotes")

    v, r = git_lib.get_branches(repo)
    if not v:
        raise gvbexcept("Unable to detect branches for repo [%s]: [%s]" % (repo, r))
    elif v and r == []:
        raise gvbexcept("No branches detected: [%s]" % repo)
    branches = r

    branches = filter_branches(branches, options)
    if branches is None:
        raise gvbexcept("Failed filtering branches")

    return remotes, branches

def filter_branches(branches, options):

    """ filter_branches
    on success, returns list of branches filtered by the provided |options|
    on failure, returns None
    """

    ret = assemble_pick_list("xor-branch", "not-branch", options, branches)
    if len(ret) == 0:
        return None
    return ret

def make_path_list(paths_to_consider):

    """ make_path_list
    assembles a list of valid paths, based on function parameter and envvar
    returns None if no paths are put together
    """

    paths = []

    if paths_to_consider is not None:
        for pc in paths_to_consider:
            paths.append(pc)
    else:
        path_env = get_path_from_env()
        if path_env is not None:
            paths.append(path_env)
        paths = path_utils.filter_path_list_no_same_branch(paths) # sanitises paths list

    if len(paths) == 0:
        return None

    return paths

def get_path_from_env():

    """ get_path_from_env
    will return the path defined by the environment. returns None if its undefined.
    """

    v, r = mvtools_envvars.mvtools_envvar_read_git_visitor_base()
    if not v:
        return None
    return r

def make_repo_list(path):

    """ make_repo_list
    returns a list of git repositories found in the given base path
    """

    if path is None:
        return None

    v, r = fsquery.makecontentlist(path, True, False, False, True, False, True, True, [])
    if not v:
        raise mvtools_exception.mvtools_exception(r)
    ret_list = r
    ret_list = filter_git_only(ret_list)
    ret_list = pluck_dotgit(ret_list)
    if len(ret_list) > 0:
        return ret_list
    else:
        return None

def process_filters(query):

    """ process_filters
    on success, returns a dict with a list of options, based off of a processed
    filter query
    on error, returns None
    """

    options_ret = {}
    if query is None:
        return options_ret

    idx = 0
    for it in query:
        idx += 1

        # NOT REMOTENAME
        if it == "--not-remotename":
            if idx == len(query): # error: this option requires a parameter, but none was given
                return None
            if not "not-remotename" in options_ret: # adds this option if not preexistent
                options_ret["not-remotename"] = []
            options_ret["not-remotename"] += [query[idx]] # inserts options

        # XOR REMOTENAME
        if it == "--xor-remotename":
            if idx == len(query): # error: this option requires a parameter, but none was given
                return None
            options_ret["xor-remotename"] = query[idx] # inserts option

    return options_ret

def print_report(has_all_passed, report_list):

    print("\nRESULTS:")
    for p in report_list:
        print(p)

    if has_all_passed:
        print("\n%sAll operations successful." % terminal_colors.TTY_GREEN)
    else:
        print("\n%sNot all operations succeeded." % terminal_colors.TTY_RED)

    print("%s" % terminal_colors.get_standard_color()) # reset terminal color

def do_visit(path_list, filters_query, func):

    paths = make_path_list(path_list)
    if paths is None:
        print("No paths to visit.")
        return None

    options = process_filters(filters_query)
    if options is None:
        print("Failed processing options")
        return None

    r = []
    for p in paths:
        repos = make_repo_list(p)
        if repos is None:
            print("Warning: %s has no repositories." % p)
            continue
        r.append(func(repos, options))

    return r
