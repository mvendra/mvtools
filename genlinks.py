#!/usr/bin/env python3

import sys
import os
import shutil

import fsquery
import path_utils

def has_mvtools_envvar():
    e = ""
    try:
        e = os.environ["MVTOOLS"]
    except:
        return False, None
    return True, e

def detect_duplicates(item_list):

    items_bn = []
    for i in item_list:
        bn = path_utils.basename_filtered(i)
        if bn in items_bn:
            print("Duplicate detected: [%s]" % i)
            return True # duplicate detected
        items_bn.append(bn)

    return False # no duplicates detected

def scratch_folder(path):
    try:
        shutil.rmtree(path)
    except:
        pass
    os.mkdir(path)

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

    # detect if path is mvtools
    path = os.getcwd()
    v, r = has_mvtools_envvar()

    if not v:
        print("MVTOOLS envvar is not defined. Aborting.")
        return False

    if path != r:
        print("This script should be run inside mvtools")
        return False

    path_links = path_utils.concat_path(path, "links")
    #if not os.path.exists(path_links):
        #print("[%s] does not exist. Aborting." % path_links)
        #return False

    # run fsquery and collect contents inside mvtools
    items = fsquery.makecontentlist(path, True, True, False, False, False, True, None)

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
    scratch_folder(path_links)

    # and finally create the links
    os.chdir(path_links)
    for i in items_filtered:
        item_name = path_utils.basename_filtered(i)
        if os.path.exists(item_name):
            continue
        os.symlink(i, item_name)

    return True

if __name__ == "__main__":
    if not genlinks():
        print("Failed generating links.")
