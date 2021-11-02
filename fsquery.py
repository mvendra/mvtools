#!/usr/bin/env python3

import sys
import os

import path_utils

def filename_qualifies_extension_list(filename, extensions_include, extensions):

    # no extensions specified. add everything indiscriminately
    if extensions == None:
        return extensions_include
    if len(extensions) == 0: 
        return extensions_include

    _, fext = os.path.splitext(filename)
    fext = fext[1:] # removes the '.'
    if len(fext) > 0 and fext in extensions:
        return extensions_include
    else:
        return not extensions_include

def __makecontentlist_delegate(dirpath, dirnames, filenames, include_regular_files, include_regular_dirs, include_hidden_files, include_hidden_dirs, extensions_include, extensions):

    ret_list_deleg = []

    # filter directories
    if include_regular_dirs or include_hidden_dirs: # premature optimisation? hmm...
        for d in dirnames:
            if d.startswith("."): # is a hidden directory
                if include_hidden_dirs:
                    ret_list_deleg.append(path_utils.concat_path(dirpath, d))
            else: # is not a hidden directory
                if include_regular_dirs: 
                    ret_list_deleg.append(path_utils.concat_path(dirpath, d))

    # filter files
    if include_regular_files or include_hidden_files: # again, premature optimisation.
        for f in filenames:
            if f.startswith("."): # is a hidden file
                if include_hidden_files and filename_qualifies_extension_list(f, extensions_include, extensions):
                    ret_list_deleg.append(path_utils.concat_path(dirpath, f))
            else: # is a regular file
                if include_regular_files and filename_qualifies_extension_list(f, extensions_include, extensions):
                    ret_list_deleg.append(path_utils.concat_path(dirpath, f))


    return ret_list_deleg

def makecontentlist(path, recursive, follow_symlinks, include_regular_files, include_regular_dirs, include_hidden_files, include_hidden_dirs, extensions_include, extensions):

    # path: path to query
    # recursive: search path and subfolders
    # follow_symlinks: also traverse into symlinked dirs
    # include_regular_files: include regular files - will be filtered by extension
    # include_regular_dirs: no further filtering
    # include_hidden_files: include files that start with "."
    # include_hidden_dirs: include folders that start with "."
    # extensions_include: whether to include the extensions listed in the next parameter, or exclude them
    # extensions: a list of extensions, to include or exclude. None means catch-all. can be a single string or a list of strings

    ret_list = []
    circular_dict = {}

    if recursive:

        for dirpath, dirnames, filenames in os.walk(path, followlinks=follow_symlinks):
            dirpath_resolved = os.path.realpath(dirpath)
            if dirpath_resolved in circular_dict:
                # circular inclusion detected
                return None
            else:
                circular_dict[dirpath_resolved] = True
            ret_list += __makecontentlist_delegate(dirpath, dirnames, filenames, include_regular_files, include_regular_dirs, include_hidden_files, include_hidden_dirs, extensions_include, extensions)

    else:

        dirpath = path
        dirnames = []
        filenames = []

        folder_contents = os.listdir(path)
        for item in folder_contents:
            current_element = path_utils.concat_path(path, item)
            if (os.path.isdir(current_element)):
                dirnames.append(item)
            elif os.path.isfile(current_element):
                filenames.append(item)

        ret_list += __makecontentlist_delegate(dirpath, dirnames, filenames, include_regular_files, include_regular_dirs, include_hidden_files, include_hidden_dirs, extensions_include, extensions)

    return ret_list

def puaq():
    print("Usage: %s path [-R|-r] follow_symlinks, include_regular_files include_regular_dirs include_hidden_files include_hidden_dirs extensions_include [extensions]" % path_utils.basename_filtered(__file__))
    exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 8:
        puaq()

    # parameters
    path = sys.argv[1]
    if not os.path.exists(path):
        print("%s does not exist." % path)
        sys.exit(1)
    param_index = 2

    # defaults
    rec = False
    follow_symlinks = False
    inc_reg_files = True
    inc_reg_dirs = False
    inc_hidden_files = False
    inc_hidden_dirs = False
    exts_incl = True # include OR exclude extensions passed in the next parameter
    exts = [] # empty or None means "all"

    # recursive - optional
    if sys.argv[param_index].upper() == "-R":
        rec = True
        param_index += 1

    # follow symlinks - mandatory
    if sys.argv[param_index] == "yes":
        follow_symlinks = True
    elif sys.argv[param_index] == "no":
        follow_symlinks = False
    param_index += 1

    # include regular files - mandatory
    if sys.argv[param_index] == "yes":
        inc_reg_files = True
    elif sys.argv[param_index] == "no":
        inc_reg_files = False
    param_index += 1

    # include regular dirs - mandatory
    if sys.argv[param_index] == "yes":
        inc_reg_dirs = True
    elif sys.argv[param_index] == "no":
        inc_reg_dirs = False
    param_index += 1

    # include hidden files - mandatory
    if sys.argv[param_index] == "yes":
        inc_hidden_files = True
    elif sys.argv[param_index] == "no":
        inc_hidden_files = False
    param_index += 1

    # include hidden dirs - mandatory
    if sys.argv[param_index] == "yes":
        inc_hidden_dirs = True
    elif sys.argv[param_index] == "no":
        inc_hidden_dirs = False
    param_index += 1

    # include extensions - mandatory
    if sys.argv[param_index] == "yes":
        exts_incl = True
    elif sys.argv[param_index] == "no":
        exts_incl = False
    param_index += 1

    # extensions - optional
    exts = sys.argv[param_index:]

    ret = makecontentlist(path, rec, follow_symlinks, inc_reg_files, inc_reg_dirs, inc_hidden_files, inc_hidden_dirs, exts_incl, exts)
    for r in ret:
        print(r)
