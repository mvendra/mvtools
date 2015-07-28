#!/usr/bin/env python

import sys
import os

def makecontentlist_delegate(dirpath, dirnames, filenames, include_files, include_dirs, include_hidden_files, include_hidden_dirs, extensions):

    ret_list_deleg = []

    if include_dirs:
        for d in dirnames:
            if d.startswith(".") and not include_hidden_dirs:
                continue
            ret_list_deleg.append(os.path.join(dirpath, d))

    if include_files:
        for f in filenames:
            if f.startswith(".") and not include_hidden_files:
                continue
            if len(extensions) == 0:
                # no extensions specified. add everything indiscriminately
                ret_list_deleg.append(os.path.join(dirpath, f))
            else:
                _, fext = os.path.splitext(f)
                fext = fext[1:] # removes the '.'
                if len(fext) > 0 and fext in extensions:
                    ret_list_deleg.append(os.path.join(dirpath, f))

    return ret_list_deleg

def makecontentlist(path, recursive, include_files, include_dirs, include_hidden_files, include_hidden_dirs, extensions):

    ret_list = []

    if recursive:

        for dirpath, dirnames, filenames in os.walk(path):
            ret_list += makecontentlist_delegate(dirpath, dirnames, filenames, include_files, include_dirs, include_hidden_files, include_hidden_dirs, extensions)

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

        ret_list += makecontentlist_delegate(dirpath, dirnames, filenames, include_files, include_dirs, include_hidden_files, include_hidden_dirs, extensions)

    return ret_list

if __name__ == "__main__":
    
    if len(sys.argv) < 6:
        print("Usage: %s [-R] path include_files include_dirs include_hidden_files include_hidden_dirs extensions" % os.path.basename(__file__))
        exit(1)

    # declarations, defaults
    path = os.getcwd()
    rec = False
    inc_files = True
    inc_dirs = False
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

    # include files - mandatory
    if sys.argv[next_index] == "yes":
        inc_files = True
    elif sys.argv[next_index] == "no":
        inc_files = False
    next_index += 1

    # include dirs - mandatory
    if sys.argv[next_index] == "yes":
        inc_dirs = True
    elif sys.argv[next_index] == "no":
        inc_dirs = False
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

    ret = makecontentlist(path, rec, inc_files, inc_dirs, inc_hidden_files, inc_hidden_dirs, exts)
    for r in ret:
        print(r)

