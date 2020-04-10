#!/usr/bin/env python3

import os
import sys
from pathlib import PurePath

import fsquery
import path_utils

"""
# python2
# from http://stackoverflow.com/questions/4579908/cross-platform-splitting-of-path-in-python
def os_path_split_asunder(path, debug=False):
    parts = []
    while True:
        newpath, tail = os.path.split(path)
        if debug: print repr(path), (newpath, tail)
        if newpath == path:
            assert not tail
            if path: parts.append(path)
            break
        parts.append(tail)
        path = newpath
    parts.reverse()
    return parts
"""

# python3
def os_path_split_asunder(path):
    return list(PurePath(path).parts)

def remove_root(files, roots):

    ret = []

    for f in files:
    
        parts = os_path_split_asunder(f)
        add = True
        for r in roots:
            if r in parts:
                add = False

        if add:
            ret.append(f)

    return ret

def remove_extensions(files, extensions):

    ret = []

    for f in files:

        fname = path_utils.basename_filtered(f)

        if fname.find(".") == -1: # no extension. we cant decide what to do
            ret.append(f)
            continue

        s = fname.rfind(".")
        if len(fname) - 1 == s: # the dot is the last character. let it be
            ret.append(f)
            continue

        ext = fname[s+1:]
        if not ext in extensions:
            ret.append(f)

    return ret

def remove_files(files_in, files_exclude):

    ret = []

    for f in files_in:
        if not f in files_exclude:
            ret.append(f)

    return ret

def detect_crlf(file):

    with open(file, "rb") as f:
        contents = f.read()
        s = contents.find(b"\x0d\x0a")
        if s != -1:
            return True
        else:
            return False

def detect_tabs(file):

    with open(file, "rb") as f:
        contents = f.read()
        s = contents.find(b"\x09")
        if s != -1:
            return True
        else:
            return False

def filter_generic(candidates, rem_exts, rem_roots, rem_files):

    ret = []

    ret = remove_extensions(candidates, rem_exts)
    ret = remove_root(ret, rem_roots)
    ret = remove_files(ret, rem_files)

    return ret

def check_crlf(path, rem_exts, rem_roots, rem_files):

    files = fsquery.makecontentlist(path, True, True, False, False, False, True, None)
    files = filter_generic(files, rem_exts, rem_roots, rem_files)

    bad_files = []

    for f in files:
        if detect_crlf(f):
            bad_files.append(f)

    if len(bad_files) > 0:
        print("BAD FILES - CRLF:")
        for f in bad_files:
            print(f)

def check_tabs(path, rem_exts, rem_roots, rem_files):

    files = fsquery.makecontentlist(path, True, True, False, False, False, True, None)
    files = filter_generic(files, rem_exts, rem_roots, rem_files)

    bad_files = []

    for f in files:
        if detect_tabs(f):
            bad_files.append(f)

    if len(bad_files) > 0:
        print("BAD FILES - TABS:")
        for f in bad_files:
            print(f)

if __name__ == "__main__":

    path = ""
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = ".."

    path = os.path.abspath(path)

    rem_exts = ["pyc", "o", "lib", "dll", "so", "mk", "sln"]
    rem_roots = [".git"]
    rem_files = []

    check_crlf(path, rem_exts, rem_roots, rem_files)
    check_tabs(path, rem_exts, rem_roots, rem_files)
