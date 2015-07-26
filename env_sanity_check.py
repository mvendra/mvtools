#!/usr/bin/env python

""" Attempts to check the sanity of your environment """

import os

#VARS_EXCEPTIONS = ["MANDATORY_PATH", "GPG_AGENT_INFO", "XDG_CONFIG_DIRS", "DEFAULTS_PATH", "XDG_DATA_DIRS"] # my mint 17 had these undefined in mid-2015 (mv)
VARS_EXCEPTIONS = []

def is_sane(var, val):

    if var in VARS_EXCEPTIONS:
        return True

    if val == "":
        return True

    if var == "PATH": # special case
        paths_in_path = val.split(":")
        for p in paths_in_path:
            if not os.path.exists(p):
                print("%s inside PATH does not exist")
                return False

    elif val[0] == '/': # generic case
        return os.path.exists(val)

    return True

if __name__ == "__main__":
    for i in os.environ.keys():
        thevar = i
        theval = os.environ[i]
        if not is_sane(thevar, theval):
            print("WARNING: %s has a suspicious value" % thevar)

