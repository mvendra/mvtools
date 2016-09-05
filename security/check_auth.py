#!/usr/bin/env python

import sys
import os
import stat

import terminal_colors

import fsquery

def print_success(msg):
    print("%s%s%s" % (terminal_colors.TTY_GREEN, msg, terminal_colors.get_standard_color()))

def print_error(msg):
    print("%s%s%s" % (terminal_colors.TTY_RED, msg, terminal_colors.get_standard_color()))

def check_permission(path):

    p = os.stat(path)
    if p.st_mode & stat.S_IRWXG:
        return False # has group permissions
    if p.st_mode & stat.S_IRWXO:
        return False # has permissions for others

    return True

def check_auth_envvar():

    MVAUTH = ""
    try:
        MVAUTH = os.environ['MVAUTH']
    except KeyError:
        print_error("MVAUTH is not defined. Aborting.")
        return False

    if not os.path.exists(MVAUTH):
        print_error("MVAUTH points to nonexistent path.")
        return False

    files_probe = fsquery.makecontentlist(MVAUTH, True, True, True, True, True, "")

    result = True
    for f in files_probe:
        if not check_permission(f):
            print_error("%s has bad permissions." % f)
            result = False

    return result

def check_auth():
    r = check_auth_envvar()
    if r:
        print_success("check_auth: All good.")
        return True
    else:
        print_error("check_auth: Incorrect permissions detected")
        return False

if __name__ == "__main__":
    check_auth()

