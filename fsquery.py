#!/usr/bin/env python3

import sys
import os

import path_utils

class graph_aux:

    def __init__(self, root_node_key):
        self.data = {}
        self.root = root_node_key
        self.data[root_node_key] = []
        self.cycle_detection_record = None

    def add_node(self, node_key):
        if node_key in self.data:
            return False # not added
        self.data[node_key] = []
        return True # node was added

    def add_connection(self, node_key_source, node_key_target):
        if not node_key_source in self.data:
            return False
        if not node_key_target in self.data:
            return False
        if node_key_target in self.data[node_key_source]:
            return False
        self.data[node_key_source].append(node_key_target)
        return True

    def get_cycle_error_report(self):
        return self.cycle_detection_record

    def detect_cycle(self):
        self.cycle_detection_record = None
        return self._visit(self.root, [])

    def _visit(self, node_key, node_chain_list):

        if node_key in node_chain_list:
            self.cycle_detection_record = "%s -> [%s]" % (node_key, node_chain_list)
            return True # cycle detected
        node_chain_list.append(node_key)

        for leaf in self.data[node_key]:
            ret = self._visit(leaf, node_chain_list)
            node_chain_list.pop()
            if ret is True:
                return True

        return False

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

    if not os.path.exists(path):
        return False, "Path [%s] does not exist" % path

    ret_list = []

    if recursive:

        if follow_symlinks:
            g = graph_aux(os.path.realpath(path))

        for dirpath, dirnames, filenames in os.walk(path, followlinks=follow_symlinks):

            if follow_symlinks:
                dirpath_resolved = os.path.realpath(dirpath)
                g.add_node(dirpath_resolved)
                for leaf in dirnames:
                    leaf_real = os.path.realpath(path_utils.concat_path(dirpath, leaf))
                    g.add_node(leaf_real)
                    g.add_connection(dirpath_resolved, leaf_real)
                if g.detect_cycle():
                    return False, "Cycle detected at [%s]" % (g.get_cycle_error_report())

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
            elif os.path.isfile(current_element) or path_utils.is_path_broken_symlink(current_element):
                filenames.append(item)

        ret_list += __makecontentlist_delegate(dirpath, dirnames, filenames, include_regular_files, include_regular_dirs, include_hidden_files, include_hidden_dirs, extensions_include, extensions)

    return True, ret_list

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

    v, r = makecontentlist(path, rec, follow_symlinks, inc_reg_files, inc_reg_dirs, inc_hidden_files, inc_hidden_dirs, exts_incl, exts)
    if not v:
        print("Path [%s] failed: [%s]" % (path, r))
        sys.exit(1)
    for x in r:
        print(x)
