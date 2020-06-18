#!/usr/bin/env python3

import sys
import os
import shutil

import fsquery
import path_utils

def has_and_get_envvar(the_envvar):
    e = ""
    try:
        e = os.environ[the_envvar]
    except:
        return False, None
    return True, e

def has_mvtools_envvar():
    return has_and_get_envvar("MVTOOLS")

def has_mvtools_links_path_envvar():
    return has_and_get_envvar("MVTOOLS_LINKS_PATH")

def get_mvtools_links_path():

    # detect if path is mvtools
    path = os.getcwd()
    v, r = has_mvtools_envvar()

    if not v:
        print("MVTOOLS envvar is not defined.")
        return None, None

    mvtools_path = r
    mvtools_links_path = None

    if path != mvtools_path:
        print("This script should be run inside mvtools")
        return None, None

    # MVTOOLS_LINKS_PATH is optional
    v, r = has_mvtools_links_path_envvar()
    if not v:
        mvtools_links_path = path_utils.concat_path(path, "links")
    else:
        mvtools_links_path = r

    return mvtools_path, mvtools_links_path

def detect_duplicates(item_list):

    items_bn = []
    for i in item_list:
        bn = path_utils.basename_filtered(i)
        if bn in items_bn:
            print("Duplicate detected: [%s]" % i)
            return True # duplicate detected
        items_bn.append(bn)

    return False # no duplicates detected

def filter_mvtools_item(item):

    if item is None:
        return False

    if len(item) == 0:
        return False

    path_pieces = item.split(os.path.sep)
    filename = path_utils.basename_filtered(item)
    fn_ext = os.path.splitext(filename)[1]

    # exclude some folders
    ex_folders = ["__pycache__", ".git", "links", "kbase", "nbproject", "deprecated", "tests", "compat"]
    for e in ex_folders:
        if e in path_pieces:
            return False

    # exclude some extra files
    ex_files = ["LICENSE", "README.md", "README.TXT", "built-jar.properties", "manifest.mf", "build.xml"]
    for e in ex_files:
        if e == filename:
            return False

    # exclude some extensions
    ex_exceptions = [".pyc"]
    for e in ex_exceptions:
        if e == fn_ext:
            return False

    return True

def genlinks():

    # resolve necessary paths
    path_mvtools, path_mvtools_links = get_mvtools_links_path()
    if path_mvtools is None or path_mvtools_links is None:
        print("Resolving paths failed. Aborting.")
        return False

    # run fsquery and collect contents inside mvtools
    items = fsquery.makecontentlist(path_mvtools, True, True, False, False, False, True, None)

    # filter out what should not be included
    items_filtered = []
    for i in items:
        if filter_mvtools_item(i):
            items_filtered.append(i)

    # check for duplicates
    if detect_duplicates(items_filtered):
        print("Detected duplicates. Aborting.")
        return False

    # wipe out old links folder and recreate it
    path_utils.scratchfolder(path_mvtools_links)

    # and finally create the links
    os.chdir(path_mvtools_links)
    for i in items_filtered:
        item_name = path_utils.basename_filtered(i)
        if os.path.exists(item_name):
            continue
        os.symlink(i, item_name)

    return True

if __name__ == "__main__":
    if not genlinks():
        print("Failed generating links.")
