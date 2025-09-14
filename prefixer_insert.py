#!/usr/bin/env python

import os
import sys

import path_utils
import fsquery
import mvtools_exception
import prjrenamer

def pad_with_zeroes_left(num_in_str, amount):
    if len(num_in_str) > amount:
        return num_in_str
    while amount - len(num_in_str) != 0:
        num_in_str = "0" + num_in_str
    return num_in_str

def is_std_cpp_autobooted_proj(path):
    full = path_utils.concat_path(path, "proj")
    full = path_utils.concat_path(full, "codelite")
    if os.path.exists(full):
        return True
    return False

def basic_refactor(original, new):
    os.rename(original, new)

def autobooted_refactor(original, new):
    td = path_utils.dirname_filtered(original)
    po = path_utils.basename_filtered(original)
    pn = path_utils.basename_filtered(new)
    prjrenamer.prjrename(td, po, pn)

def prefixer_insert(target_dir, prefix_to_reserve):

    print("This script is broken and disabled")
    sys.exit(1)

    PREFIX_SIZE = 3
    v, r = fsquery.makecontentlist(target_dir, False, False, False, True, False, False, True, None)
    if not v:
        raise mvtools_exception.mvtools_exception(r)
    dirs = r
    dirs.sort()
    for d in dirs:
        base = path_utils.dirname_filtered(d)
        subject = path_utils.basename_filtered(d)
        pref = subject[0:PREFIX_SIZE]
        if int(pref) >= int(prefix_to_reserve):
            new_pref = int(pref) + 1
            new_pref_str = str(new_pref)
            new_subject = pad_with_zeroes_left(new_pref_str, PREFIX_SIZE) + subject[PREFIX_SIZE:]
            new_full = path_utils.concat_path(base, new_subject)
            if is_std_cpp_autobooted_proj(d):
                autobooted_refactor(d, new_full)
            else:
                basic_refactor(d, new_full)

def puaq(selfhelp):
    print("Usage: %s prefix-to-reserve [target-dir]" % path_utils.basename_filtered(__file__))
    if selfhelp:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":

    print("mvtodo: this script is broken and disabled")
    sys.exit(1)

    """
    given:
    /somepath/001_whatever
    /somepath/002_whatever
    /somepath/003_whatever
    where all "00*_whatever" are folders

    this tool:
    prefixer_insert 002 /somepath

    results in:
    /somepath/001_whatever
    /somepath/003_whatever
    /somepath/004_whatever

    explanation:
    002_whatever will be renamed to 003_whatever, so as to reserve the prefix 002
    """

    td = os.getcwd()
    ptr = ""

    if len(sys.argv) < 2:
        puaq(False)

    ptr = sys.argv[1]

    if len(sys.argv) > 2:
        td = sys.argv[2]

    prefixer_insert(td, ptr)
