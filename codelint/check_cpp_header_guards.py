#!/usr/bin/env python3

import sys
import os

import path_utils

def getcontents(filename):
    contents = ""
    with open(filename) as f:
        contents = f.read()
    return contents

def check_cpp_header_guards(filename):

    """
    this will check if a given cpp header file is
    in the following format:

    #ifndef GUARD
    #define GUARD
    #endif // GUARD
    """

    contents = getcontents(filename)
    lines = contents.split("\n")

    guardname = ""
    i = 0
    for l in lines:
        l = l.strip()
        if l == "":
            i += 1
            continue
        if l[0:8] == "#ifndef ":
            guardname = l[8:]
            if i+1 >= len(lines): # guard not defined below ifndef
                return False
            if guardname != lines[i+1][8:]: # ifndef GUARD and define GUARD do not match
                return False
            else:
                break
        i += 1

    for l in reversed(lines):
        if l == "":
            continue
        if l[0:6] == "#endif":
            if guardname != l[10:]: # guard and endif // guard do not match
                return False
            else:
                break

    return True

def puaq():
    print("Usage: %s file.h" % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()
    if not check_cpp_header_guards(sys.argv[1]):
        print("%s has faulty header guards" % sys.argv[1])
        sys.exit(1)
    sys.exit(0)
