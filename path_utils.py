#!/usr/bin/env python3

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
    Makes sure the given path is/becomes an empty folder. If not preexistent, path is created as an empty folder.
    If it pre-exists, being either a file or a valid tree, it is deleted and re-created as an empty folder.
    Returns true/false depending on whether the operation succeeded or not.
    """

    """
    # old version
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
    """

    # newer, more compatible version
    try:
        if os.path.exists(path):
            if os.path.isfile(path):
                os.unlink(path)
            else:
                shutil.rmtree(path)
        os.mkdir(path)
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
    pathlist_sorted.sort(key = lambda x: len(x)) # sorts list by string length
    blacklist = []
    result = []

    for x in pathlist_sorted:
        for y in pathlist_sorted:
            if x == y: 
                continue
            if os.path.dirname(x) == os.path.dirname(y):
                continue
            if y.startswith(x):
                # this was an immensely foolish solution.
                # this prevents repos with the common same prefix
                # to be considered (for example: repo and repo_bk)
                # caught this in 09/2016 - mv.
                blacklist.append(y)

    for w in pathlist_sorted:
        if w not in blacklist:
            result.append(w)

    return result

def filter_remove_trailing_sep(target):
    if target[len(target)-1] == os.sep:
        if len(target) > 1:
            return target[:len(target)-1]
        else:
            return ""
    return target

def filter_join_abs(path):

    # because os.path.join does not allow for joining
    # absolute paths ("/tmp/some/path", "/some/other/path"),
    # this little crutch cleans up paths after the first
    # position to alow for adding them all in absolute terms

    if len(path) == 0:
        return ""

    if path[0] == os.path.sep:
        return path[1:]

    return path

def concat_path(*ps):

    # vanilla os.path.join does not join absolute paths 
    # for example: ("/tmp/folder", "/tmp/folder/sub") -> will not
    # become "/tmp/folder/tmp/folder/sub". that would result in "/tmp/folder/sub" actually.
    # so this function is a complement to os.path.join that actually adds absolute paths

    if len(ps) < 1:
        return ""
    result_path = ps[0]
    if len(ps) < 2:
        return result_path
    for p in ps[1:]:
        result_path = os.path.join(result_path, filter_join_abs(p))
    return result_path

if __name__ == "__main__":
    print("Hello from %s" % os.path.basename(__file__))
