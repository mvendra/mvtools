#!/usr/bin/env python

import sys
import os
import stat

import terminal_colors
import fsquery
import fsquery_adv_filter
import path_utils
import mvtools_exception

def print_success(msg):
    print("%s: %s%s%s" % (path_utils.basename_filtered(__file__), terminal_colors.TTY_GREEN, msg, terminal_colors.get_standard_color()))

def print_error(msg):
    print("%s: %s%s%s" % (path_utils.basename_filtered(__file__), terminal_colors.TTY_RED, msg, terminal_colors.get_standard_color()))

def check_permission(path):
    p = os.stat(path)
    if p.st_mode & stat.S_IRWXG:
        return False # has group permissions
    if p.st_mode & stat.S_IRWXO:
        return False # has permissions for others
    return True

def check_auth_folder(path):

    v, r = fsquery.makecontentlist(path, True, False, True, True, True, True, True, "")
    if not v:
        raise mvtools_exception.mvtools_exception(r)
    files_probe = r

    exclude_list = ["*/.git/*"]
    filters = []
    filters.append( (fsquery_adv_filter.filter_all_positive, "not-used") )
    for ei in exclude_list:
        filters.append( (fsquery_adv_filter.filter_has_not_middle_pieces, path_utils.splitpath(ei, "auto")) )

    items_filtered = fsquery_adv_filter.filter_path_list_and(files_probe, filters)

    result = True
    for f in items_filtered:
        if not check_permission(f):
            print_error("%s has bad permissions." % f)
            result = False

    return result

def check_auth(paths):

    for p in paths:
        if not os.path.exists(p):
            print_error("Path [%s] does not exist." % p)
            return

    any_errors = False
    for p in paths:
        if not check_auth_folder(p):
            any_errors = True
            print_error("Path [%s]: Incorrect permissions detected." % p)

    if not any_errors:
        print_success("All good.")
    else:
        print_error("Errors detected.")

def puaq(selfhelp):
    print("Usage: %s [path1 | path2]" % path_utils.basename_filtered(__file__))
    if selfhelp:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq(False)
    paths = sys.argv[1:]

    check_auth(paths)
