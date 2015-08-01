#!/usr/bin/env python

import sys
import os

def arraytopath(ar):

    result=os.sep
    for args in ar:
        result+=args+os.sep
    return result

def explodepath(apath):

    tokens = apath.split("/")
    result=""
    for tk in tokens:
        if tk == "":
            continue
        else:
            result+=tk+" "

    result=result[:len(result)-1] # removes trailing blank space
    return result

def scratchfolder(_self, path):

    """ scratch_folder
    Makes sure the given path is/becomes an empty folder. If not preexistent, path is created.
    If it pre-exists, being either a file or a valid tree, it is deleted and re-created and an empty folder.
    """

    if os.path.exists(path):
        if os.path.isfile(path):
            os.unlink(path)
        else:
            shutil.rmtree(path)
    call(["mkdir", path])

def filter_path_list_no_same_branch(pathlist):

    """ filter_path_list_no_same_branch
    Checks a given path list for duplicate paths, filesystem-branch-wise. 
    for example: /mnt/home and /mnt/etc are not in the same branch.
    but /mnt/home and /mnt/home/user are.
    this function filters out by unique branches (discards out dupes)
    """

    pathlist_sorted = pathlist
    pathlist_sorted.sort(lambda x,y: cmp(len(x), len(y))) # sorts list by string length
    blacklist = []
    result = []

    for x in pathlist_sorted:
        for y in pathlist_sorted:
            if x == y: 
                continue
            if y.startswith(x):
                blacklist.append(y)

    for w in pathlist_sorted:
        if w not in blacklist:
            result.append(w)

    return result

if __name__ == "__main__":
    print(filter_path_list_no_same_branch(["/home", "/home/user/nuke", "/bug", "/home/ooser", "/shome", "/home/bork/nuke/bark",]))

