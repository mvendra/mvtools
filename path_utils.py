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

def getextension(filename):
    if filename is None:
        return None
    _, fext = os.path.splitext(filename)
    return fext[1:]

def deletefile_ignoreerrors(filepath):
    if not os.path.exists(filepath):
        return
    try:
        os.unlink(filepath)
    except:
        pass

def backpedal_path(path):
    if path is None:
        return None
    partial = os.path.join(path, os.pardir)
    parent = os.path.abspath(partial)
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

def splitpath(apath):
    from pathlib import PurePath
    path_parts = list(PurePath(apath).parts)
    return_path_list = []
    for pp in path_parts:
        if pp != os.sep or pp != "/":
            return_path_list.append(pp)
    return return_path_list

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
        raise PathUtilsException("%s guaranteefolder: %s exists and is not a folder. This is an exception." % (basename_filtered(__file__), path))
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
    if target[len(target)-1] == "/" or target[len(target)-1] == "\\":
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

    if path is None:
        return None

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
    if result_path is None:
        return None
    if len(ps) < 2:
        return result_path
    for p in ps[1:]:
        if p is None:
            return None
        result_path = os.path.join(result_path, filter_join_abs(p))
    return result_path

def basename_filtered(path):

    # vanilla os.path.basename returns empty string when given a path
    # that ends with a path separator. this one first filters out the
    # trailing path separator

    return os.path.basename( filter_remove_trailing_sep ( path ) )

def dirname_filtered(path):

    # vanilla os.path.dirname does not work well with a path that ends
    # in a separator character. this function removes the trailing
    # separator when present before doing dirname.

    return os.path.dirname( filter_remove_trailing_sep ( path ) )

def copy_to(origin, target):

    # works just like the POSIX "cp" app but does not require the "-r" for copying folders

    if not os.path.exists(origin):
        return False

    if os.path.isdir(origin):
        target_fix = concat_path(target, basename_filtered(origin))
        shutil.copytree(origin, target_fix, symlinks=True)
    else:
        shutil.copy(origin, target)

    return True

def check_if_paths_exist_stop_first(list_paths):
    for n in list_paths:
        if os.path.exists(n):
            return False, "Path [%s] already exists." % n
    return True, None

def check_if_paths_not_exist_stop_first(list_paths):
    for n in list_paths:
        if not os.path.exists(n):
            return False, "Path [%s] does not exist." % n
    return True, None

if __name__ == "__main__":
    print("Hello from %s" % basename_filtered(__file__))
