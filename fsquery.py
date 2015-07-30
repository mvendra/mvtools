#!/usr/bin/env python

import sys
import os

def filename_qualifies_extension_list(filename, extensions):

    if len(extensions) == 0: # no extensions specified. add everything indiscriminately
        return True

    _, fext = os.path.splitext(filename)
    fext = fext[1:] # removes the '.'
    if len(fext) > 0 and fext in extensions:
        return True
    else:
        return False

def __makecontentlist_delegate(dirpath, dirnames, filenames, include_regular_files, include_regular_dirs, include_hidden_files, include_hidden_dirs, extensions):

    ret_list_deleg = []

    # filter directories
    if include_regular_dirs or include_regular_dirs: # premature optimisation? hmm...
        for d in dirnames:
            if d.startswith("."): # is a hidden directory
                if include_hidden_dirs:
                    ret_list_deleg.append(os.path.join(dirpath, d))
            else: # is not a hidden directory
                if include_regular_dirs: 
                    ret_list_deleg.append(os.path.join(dirpath, d))

    # filter files
    if include_regular_files or include_hidden_files: # again, premature optimisation.
        for f in filenames:
            if f.startswith("."): # is a hidden file
                if include_hidden_files and filename_qualifies_extension_list(f, extensions):
                    ret_list_deleg.append(os.path.join(dirpath, f))
            else: # is a regular file
                if include_regular_files and filename_qualifies_extension_list(f, extensions):
                    ret_list_deleg.append(os.path.join(dirpath, f))


    return ret_list_deleg

def makecontentlist(path, recursive, include_regular_files, include_regular_dirs, include_hidden_files, include_hidden_dirs, extensions):

    ret_list = []

    if recursive:

        for dirpath, dirnames, filenames in os.walk(path):
            ret_list += __makecontentlist_delegate(dirpath, dirnames, filenames, include_regular_files, include_regular_dirs, include_hidden_files, include_hidden_dirs, extensions)

    else:

        dirpath = path
        dirnames = []
        filenames = []

        folder_contents = os.listdir(path)
        for item in folder_contents:
            if os.path.isdir(os.path.join(path, item)):
                dirnames.append(item)
            elif os.path.isfile(os.path.join(path, item)):
                filenames.append(item)

        ret_list += __makecontentlist_delegate(dirpath, dirnames, filenames, include_regular_files, include_regular_dirs, include_hidden_files, include_hidden_dirs, extensions)

    return ret_list

if __name__ == "__main__":
    
    if len(sys.argv) < 6:
        print("Usage: %s [-R] path include_regular_files include_regular_dirs include_hidden_files include_hidden_dirs extensions" % os.path.basename(__file__))
        exit(1)

    # declarations, defaults
    path = os.getcwd()
    rec = False
    inc_reg_files = True
    inc_reg_dirs = False
    inc_hidden_files = False
    inc_hidden_dirs = False
    exts = [] # empty means "any"

    # recursive - optional
    next_index = 1
    if '-R' in sys.argv or '-r' in sys.argv:
        rec = True
        next_index = 2

    # path - mandatory
    path = sys.argv[next_index]
    if not os.path.exists(path):
        print("%s does not exist." % path)
        sys.exit(1)
    next_index += 1

    # include regular files - mandatory
    if sys.argv[next_index] == "yes":
        inc_reg_files = True
    elif sys.argv[next_index] == "no":
        inc_reg_files = False
    next_index += 1

    # include regular dirs - mandatory
    if sys.argv[next_index] == "yes":
        inc_reg_dirs = True
    elif sys.argv[next_index] == "no":
        inc_reg_dirs = False
    next_index += 1

    # include hidden files - mandatory
    if sys.argv[next_index] == "yes":
        inc_hidden_files = True
    elif sys.argv[next_index] == "no":
        inc_hidden_files = False
    next_index += 1

    # include hidden dirs - mandatory
    if sys.argv[next_index] == "yes":
        inc_hidden_dirs = True
    elif sys.argv[next_index] == "no":
        inc_hidden_dirs = False
    next_index += 1

    # extensions - optional
    exts = sys.argv[next_index:]

    ret = makecontentlist(path, rec, inc_reg_files, inc_reg_dirs, inc_hidden_files, inc_hidden_dirs, exts)
    for r in ret:
        print(r)

