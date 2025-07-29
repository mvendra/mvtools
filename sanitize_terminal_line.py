#!/usr/bin/env python3

import sys
import os

import path_utils

def sanitize_next(input_line):

    input_line_local = input_line

    p = input_line_local.find("\x1b")
    if p == -1:
        return False, None

    n = input_line_local.find("m", p)
    if n == -1:
        return False, None

    input_line_local = input_line_local[0:p] + input_line_local[n+1:]
    return True, input_line_local

def sanitize_terminal_line(input_line):

    input_line_local = input_line
    while True:
        v, r = sanitize_next(input_line_local)
        if not v:
            break
        else:
            input_line_local = r

    return input_line_local

def puaq(selfhelp):
    print("Usage: %s input_line" % path_utils.basename_filtered(__file__))
    if selfhelp:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq(False)
    input_lines = sys.argv[1:]
    for i in input_lines:
        print(sanitize_terminal_line(i))
