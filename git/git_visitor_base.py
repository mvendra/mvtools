#!/usr/bin/env python

import os
import fsquery
import path_utils

def filter_git_only(path_list):

    """ filter_git_only
    given path_list, will filter elements if they point to a git repository (.git folder)
    returns a subset of path_list that do point to a git repository's git folder
    """

    ret = []
    for d in path_list:
        if d.endswith(".git") or d.endswith(".git" + os.sep):
            ret.append(d)
    return ret

def filter_remotes(remotes, options):

    """ filter_remotes
    on success, returns list of remotes filtered by provided options
    on failure, returns None
    """

    retlist = remotes

    if "xor-remote" in options:
        if not options["xor-remote"] in remotes:
            return None # the xor'ed remote must be available to begin with
        return [options["xor-remote"]] # early return: xor remote does not play along with any other option.

    if "not-remote" in options:
        retlist = [] # lets reset the return list, then only add the ones that are not blacklisted
        for it in remotes:
            if not it in options["not-remote"]:
                retlist += [it]

    return retlist

def filter_branches(branches, options):

    """ filter_branches
    on success, returns list of branches filtered by provided options
    on failure, returns None
    """

    retlist = branches

    if "xor-branch" in options:
        if not options["xor-branch"] in branches:
            return None # the xor'ed branch must be available to begin with
        return [options["xor-branch"]] # early return: xor branch does not play along with any other option.

    if "not-branch" in options:
        retlist = [] # lets reset the return list, then only add the ones that are not blacklisted
        for it in branches:
            if not it in options["not-branch"]:
                retlist += [it]

    return retlist

def make_path_list(paths_to_consider):

    """ make_path_list
    assembles a list of valid paths, based on function parameter and envvar
    """

    paths = []

    if paths_to_consider is not None:
        for pc in paths_to_consider:
            paths.append(pc)

    path_env = get_path_from_env()
    if path_env is not None:
        paths.append(path_env)
    paths = path_utils.filter_path_list_no_same_branch(paths) # sanitises paths list
    return paths

def get_path_from_env():

    """ get_path_from_env
    will return the path defined by the environment. returns None if its undefined.
    """

    path = None
    try:
        path = os.environ["MVBASE"]
    except KeyError:
        pass
    return path

def make_repo_list(path):

    """ make_repo_list
    returns a list of git repositories found in the given base path
    """

    if path is None:
        return None

    ret_list = fsquery.makecontentlist(path, True, False, True, False, True, [])
    ret_list = filter_git_only(ret_list)
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

        # NOT REMOTE
        if it == "--not-remote":
            if idx == len(query): # error: this option requires a parameter, but none was given
                return None
            if not "not-remote" in options_ret: # adds this option if not preexistant
                options_ret["not-remote"] = []
            options_ret["not-remote"] += [query[idx]] # inserts options

        # XOR REMOTE
        if it == "--xor-remote":
            if idx == len(query): # error: this option requires a parameter, but none was given
                return None
            options_ret["xor-remote"] = query[idx] # inserts option

    return options_ret

def do_visit(path_list, filters_query, func):

    paths = make_path_list(path_list)
    if paths is None:
        print("No paths to visit.")
        return

    options = process_filters(filters_query)
    if options is None:
        print("Failed processing options")
        return

    for p in paths:
        repos = make_repo_list(p)
        if repos is None:
            print("Warning: %s has no repositories." % p)
            continue
        func(repos, options)

