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

def do_visit(path_list, func):

    paths = make_path_list(path_list)
    if paths is None:
        print("No paths to visit.")
        return

    for p in paths:
        repos = make_repo_list(p)
        if repos is None:
            print("Warning: %s has no repositories." % p)
            continue
        func(repos)

