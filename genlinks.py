#!/usr/bin/env python3

import sys
import os
import shutil

import fsquery
import fsquery_adv_filter
import path_utils
import mvtools_envvars

def get_mvtools_links_path():

    # detect if path is mvtools
    path = os.getcwd()
    v, r = mvtools_envvars.mvtools_envvar_read_main()
    if not v:
        print("MVTOOLS envvar is not defined.")
        return None, None

    mvtools_path = r
    mvtools_links_path = None

    if path != mvtools_path:
        print("This script should be run inside mvtools")
        return None, None

    # MVTOOLS_LINKS_PATH is optional
    v, r = mvtools_envvars.mvtools_envvar_read_links_path()
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

def apply_links_filters(items):

    items_filtered = []

    # prefiltering
    for i in items:
        if i is not None:
            if not len(i) == 0:
                items_filtered.append(i)
    items = items_filtered
    items_filtered = []

    # setup filters
    exclude_list = ["*/__pycache__/*", "*/.git/*", "*/hexascconv/src/hexascconv/*", "*/hexascconv/build/classes/*", "*/nbproject/*", "*/links/*", "*/kbase/*", "*/deprecated/*", "*/tests/*", "*/compat/*", "*/codegen/templates/*"]
    exclude_list += ["*/LICENSE", "*/README.md", "*/hexascconv/dist/README.TXT", "*/built-jar.properties", "*/hexascconv/manifest.mf", "*/hexascconv/build.xml"]
    exclude_list_ext = ["pyc", "cfg", "png"]

    filters = []
    filters.append( (fsquery_adv_filter.filter_all_positive, "not-used") )
    for ei in exclude_list:
        filters.append( (fsquery_adv_filter.filter_has_not_middle_pieces, path_utils.splitpath(ei)) )
    filters.append( (fsquery_adv_filter.filter_extension_is_not, exclude_list_ext) )

    # filter out exceptions
    items_filtered = fsquery_adv_filter.filter_path_list_and(items, filters)

    return items_filtered

def genlinks():

    # resolve necessary paths
    path_mvtools, path_mvtools_links = get_mvtools_links_path()
    if path_mvtools is None or path_mvtools_links is None:
        print("Resolving paths failed. Aborting.")
        return False

    # run fsquery and collect contents inside mvtools
    items = fsquery.makecontentlist(path_mvtools, True, True, False, False, False, True, None)

    # filter out exceptions
    items_filtered = apply_links_filters(items)

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
