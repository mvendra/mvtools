#!/usr/bin/env python3

import sys
import os
import shutil
from subprocess import call

import get_platform

class PathUtilsException(RuntimeError):
    def __init__(self, msg):
        self._set_message(msg)
    def _get_message(self): 
        return self._message
    def _set_message(self, message): 
        self._message = message
    message = property(_get_message, _set_message)

def replace_extension(source_string, ext_to_find, ext_to_replace_with):

    if source_string is None:
        return None

    n = source_string.rfind(ext_to_find)
    if n == -1:
        return None

    if source_string[n:] != ext_to_find:
        return None

    return source_string[:n] + ext_to_replace_with

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

def deletefolder_ignoreerrors(folderpath):
    try:
        shutil.rmtree(folderpath)
    except FileNotFoundError as fnfe_ex:
        pass

def backpedal_path(path):
    if path is None:
        return None
    partial = concat_path(path, os.pardir)
    parent = os.path.abspath(partial)
    if parent == path:
        return None
    return parent

def arraytopath(the_path_array):

    result = ""
    c = 0 
    for args in the_path_array:
        c += 1
        if c == len(the_path_array):
            result += args
        else:
            result += args + os.sep
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

    if path is None or path == "":
        raise PathUtilsException("%s guaranteefolder: path [%s] is invalid. This is an exception." % (basename_filtered(__file__), path))

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
            if dirname_filtered(x) == dirname_filtered(y):
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

def getpathroot(path):

    if path is None:
        return None
    if path == "":
        return None

    if len(path) > 1:
        path = filter_remove_trailing_sep(path)

    path_pieces = splitpath(path, "auto")
    if path_pieces is None:
        return None
    if len(path_pieces) == 0:
        return None
    return path_pieces[0]

def splitpath(target_path, windows_path):

    # {windows_path} valid values are {"yes" / "no" / "auto"}

    if target_path is None:
        return None
    if target_path == "":
        return None

    sep_chars = ["/"]
    treat_as_windows_path = (windows_path == "yes") or ((windows_path == "auto") and (get_platform.getplat() == get_platform.PLAT_WINDOWS))
    if treat_as_windows_path:
        sep_chars.append("\\")

    result_list = []
    current_piece = ""
    c = 0
    for current_char in target_path:
        c += 1

        if (c == 1) and (current_char == "/") and (not treat_as_windows_path):
            result_list.append("/")
            continue
        if (current_char in sep_chars):
            if current_piece != "":
                result_list.append(current_piece)
                current_piece = ""
            continue
        current_piece += current_char

    if current_piece != "":
        result_list.append(current_piece)

    if len(result_list) == 0:
        return None
    return result_list

def basename_filtered(path, windows_path = "auto"):

    # {windows_path} valid values are {"yes" / "no" / "auto"}

    # basename_filtered: will discard traling path separators, and return the last node. if there is only one node, that first node
    # will be returned alone. on linux-like platforms, if the first character is a "/", then it is considered to be a valid node (root).
    # for example: basename_filtered("/", "no") -> must return "/". on windows, None is returned on such case.

    if path is None:
        return None
    if path == "":
        return None

    path_pieces = splitpath(path, windows_path)
    if path_pieces is None:
        return None

    # just return the last node / leaf
    return path_pieces[len(path_pieces)-1]

def dirname_filtered(path, windows_path = "auto"):

    # {windows_path} valid values are {"yes" / "no" / "auto"}

    # dirname_filtered: will discard trailing path separators, and return every node except the last one. if there is only one node,
    # then None is returned. on linux-like platforms, if the first character is a "/", then it is considered to be a valid node (root).
    # partial/middle paths (without the filesystem's root, regardless of the platform) are supported. for example, the following:
    # dirname_filtered("home/user/folder", "no") -> must return "home/user".

    if path is None:
        return None
    if path == "":
        return None

    treat_as_windows_path = (windows_path == "yes") or ((windows_path == "auto") and (get_platform.getplat() == get_platform.PLAT_WINDOWS))

    path_pieces = splitpath(path, windows_path)
    if path_pieces is None:
        return None
    if len(path_pieces) == 0:
        return None
    if len(path_pieces) == 1:
        if (not treat_as_windows_path) and (path_pieces[0] == "/"):
            return path_pieces[0]
        else:
            return None

    assembled_path = ""

    # just return every node except last node / leaf
    for i in range(len(path_pieces)-1):
        if i == 0:
            assembled_path += path_pieces[i]
        else:
            if (not treat_as_windows_path) and (assembled_path == "/"):
                assembled_path += path_pieces[i]
                continue
            assembled_path += ("%s%s" % (os.sep, path_pieces[i]))

    if treat_as_windows_path and path[0] == "/": # path_pieces was produced without the leftmost slash. artificially re-introduce it.
        assembled_path = "%s%s" % (os.sep, assembled_path)

    return assembled_path

def copy_to_and_rename(source_path, target_path, new_name):

    if source_path is None:
        return False

    if os.path.isdir(source_path):
        return copy_folder_to_and_rename(source_path, target_path, new_name)
    else:
        return copy_file_to_and_rename(source_path, target_path, new_name)

def copy_file_to_and_rename(source_path, target_path, new_name):

    if source_path is None:
        return False
    if target_path is None:
        return False
    if new_name is None:
        return False

    if not os.path.exists(source_path):
        return False
    if os.path.isdir(source_path):
        return False
    if not os.path.exists(target_path):
        return False
    if not os.path.isdir(target_path):
        return False
    if source_path == target_path:
        return False

    if len(splitpath(new_name, "auto")) != 1:
        return False

    final_target_path = concat_path(target_path, new_name)
    if os.path.exists(final_target_path):
        return False

    contents = None
    with open(source_path, "rb") as f:
        contents = f.read()

    with open(final_target_path, "wb") as f:
        f.write(contents)

    return True

def copy_folder_to_and_rename(source_path, target_path, new_name):

    if source_path is None:
        return False
    if target_path is None:
        return False
    if new_name is None:
        return False

    if not os.path.exists(source_path):
        return False
    if not os.path.isdir(source_path):
        return False
    if not os.path.exists(target_path):
        return False
    if not os.path.isdir(target_path):
        return False
    if source_path == target_path:
        return False

    if len(splitpath(new_name, "auto")) != 1:
        return False

    final_target_path = concat_path(target_path, new_name)
    if os.path.exists(final_target_path):
        return False

    shutil.copytree(source_path, final_target_path, symlinks=True)
    return True

def copy_to(source, target):

    # works just like the POSIX "cp" app but does not require the "-r" for copying folders
    # does not allow simultaneous renaming/overwriting of any kind

    if os.path.isdir(source):
        return copy_folder_to(source, target)
    else:
        return copy_file_to(source, target)

def copy_file_to(source, target):

    if not os.path.exists(source):
        return False
    if not os.path.exists(target):
        return False
    if not os.path.isdir(target):
        return False
    final_filename = concat_path(target, basename_filtered(source))
    if os.path.exists(final_filename):
        return False

    contents = None
    with open(source, "rb") as f:
        contents = f.read()

    with open(final_filename, "wb") as f:
        f.write(contents)

    return True

def copy_folder_to(source, target):

    target_folder_final_path = concat_path(target, basename_filtered(source))

    if not os.path.exists(source):
        return False
    if not os.path.exists(target):
        return False
    if not os.path.isdir(target):
        return False
    if os.path.exists(target_folder_final_path):
        return False

    shutil.copytree(source, target_folder_final_path, symlinks=True)
    return True

def based_path_find_outstanding_path(source_basepath, source_fullpath):

    # given:
    # source_basepath = "/home/user/folder" and source_fullpath = "/home/user/folder/more/stuff"
    # returns "more/stuff"

    if source_basepath == "" or source_basepath is None:
        return False, "Invalid source_basepath"
    if source_fullpath == "" or source_fullpath is None:
        return False, "Invalid source_fullpath"

    source_basepath_pieces = splitpath(source_basepath, "auto")
    source_fullpath_pieces = splitpath(source_fullpath, "auto")

    if len(source_basepath_pieces) < 1:
        return False, "Invalid source_basepath"
    if len(source_fullpath_pieces) < 1:
        return False, "Invalid source_fullpath"
    if len(source_fullpath_pieces) <= len(source_basepath_pieces):
        return False, "Invalid parameters"

    for i in range(len(source_basepath_pieces)):
        if source_basepath_pieces[i] != source_fullpath_pieces[i]:
            return False, "Invalid parameters"

    outstanding_path = source_fullpath_pieces[len(source_basepath_pieces):]
    return True, arraytopath(outstanding_path)

def based_copy_to(source_basepath, source_fullpath, target):

    # a mixture of POSIX's "cp -R" and "mkdir -p"

    if source_basepath == "" or source_basepath is None or not os.path.exists(source_basepath):
        return False
    if source_fullpath == "" or source_fullpath is None or not os.path.exists(source_fullpath):
        return False
    if target == "" or target is None or not os.path.exists(target):
        return False

    v, r = based_path_find_outstanding_path(source_basepath, source_fullpath)
    if not v:
        return False
    outstanding_path_pieces = splitpath(r, "auto")

    current_assembled_path = target
    for i in range(len(outstanding_path_pieces)):
        if i == len(outstanding_path_pieces)-1:
            return copy_to(source_fullpath, current_assembled_path)
        else:
            current_assembled_path = concat_path(current_assembled_path, outstanding_path_pieces[i])
            if not os.path.exists(current_assembled_path):
                os.mkdir(current_assembled_path)
            else:
                if not os.path.isdir(current_assembled_path): # should never happen, but you never know
                    return False

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

def find_middle_path_parts(basepath, fullpath):

    # given two paths with a common base
    # for example: /home and /home/user/folder
    # return the middle parts in relation to the
    # fullpath. so in this example, that'd be "user".
    # another example: /home and /home/user/folder/second
    # the return would be "user/folder"
    # returns None on errors

    if basepath is None or fullpath is None:
        return None

    basepath_pieces = splitpath(basepath, "auto")
    fullpath_pieces = splitpath(fullpath, "auto")

    if (len(basepath_pieces) < 1) or (len(fullpath_pieces) <= len(basepath_pieces)):
        return None

    if basepath_pieces[0] != fullpath_pieces[0]:
        return None

    assembled_middle = ""
    for i in range(len(basepath_pieces)):
        if fullpath_pieces[i] != basepath_pieces[i]:
            return None

    idx_first = i+1
    idx_second = len(fullpath_pieces)-1

    if idx_second == idx_first:
        return ""
    elif not idx_second > idx_first:
        return None

    assembled_middle = fullpath_pieces[idx_first:idx_second]

    assembled_middle_string = ""
    for i in range(len(assembled_middle)):
        if i < len(assembled_middle) - 1:
            assembled_middle_string += assembled_middle[i] + os.sep
        else:
            assembled_middle_string += assembled_middle[i]

    return assembled_middle_string

def compat_windows_path(path):

    # substitute the blackwards-slash in the given path to forward slashes,
    # in order to make it compatible with linux/cygwin

    if path is None:
        return None

    if not isinstance(path, str):
        return None

    if path == "":
        return None

    local_path = path
    local_path = local_path.replace("\\", "/")
    return local_path

if __name__ == "__main__":
    print("Hello from %s" % basename_filtered(__file__))
