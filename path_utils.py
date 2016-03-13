#!/usr/bin/env python

import sys
import os
import shutil
from subprocess import call

class PathUtilsException(RuntimeError):
    def __init__(self, msg):
        self._set_message(msg)
    def _get_message(self): 
        return self._message
    def _set_message(self, message): 
        self._message = message
    message = property(_get_message, _set_message)

def poplastextension(filename):
    result = "you_found_a_bug"
    idx = filename.rfind(".")
    if idx == -1:
        # no extensions found at all.
        result = filename + "_sub"
    else:
        result = filename[:idx]
    return result

def deletefile_ignoreerrors(filepath):
    if not os.path.exists(filepath):
        return
    try:
        os.unlink(filepath)
    except:
        pass

def backpedal_path(path):
    if not os.path.exists(path):
        return None
    parent = os.path.abspath(os.path.join(path, os.pardir))
    if parent == path:
        return None
    return parent

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

def scratchfolder(path):

    """ scratch_folder
    Makes sure the given path is/becomes an empty folder. If not preexistent, path is created.
    If it pre-exists, being either a file or a valid tree, it is deleted and re-created and an empty folder.
    Returns true/false depending on whether the operation succeeded or not.
    """

    try:
        if os.path.exists(path):
            if os.path.isfile(path):
                os.unlink(path)
            else:
                shutil.rmtree(path)
        ret = call(["mkdir", path])
        if ret != 0:
            return False
    except:
        return False
    return True

def guaranteefolder(path):

    """ guaranteefolder
    Makes sure the given path is a folder.

    If path already exists and is not a folder, throws exception
    if it already exists and is a folder, does nothing.
    If path does not exist, create it as a folder
    """

    if os.path.isdir(path):
        return # OK ! thats what we wanted

    if os.path.exists(path):
        # exists and is not a folder. raise hell.
        raise PathUtilsException("%s guaranteefolder: %s exists and is not a folder. This is an exception." % (os.path.basename(__file__), path))
    else:
        # just create the new folder
        call(["mkdir", "-p", path])

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
    print("Hello from %s" % os.path.basename(__file__))

