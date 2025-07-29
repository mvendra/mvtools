#!/usr/bin/env python3

import sys
import os
import re

import path_utils

valid_modes = ["--in-to-out", "--in-to-err", "--in-to-both"]

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def streamfilter(input_text, pattern, replacement, mode):

    output_text = re.sub(pattern, replacement, input_text)

    if mode == "--in-to-out":
        sys.stdout.write(output_text)
    elif mode == "--in-to-err":
        sys.stderr.write(output_text)
    elif mode == "--in-to-both":
        sys.stdout.write(output_text)
        sys.stderr.write(output_text)

def cmdline_prettyprint(_valid_modes):
    local_output_str = "["
    for vm in _valid_modes:
        local_output_str += vm + " | "
    local_output_str = local_output_str[:len(local_output_str)-3]
    local_output_str += "]"
    return local_output_str

def puaq(selfhelp):
    print("Usage: %s pattern replacement %s" % (path_utils.basename_filtered(__file__), cmdline_prettyprint(valid_modes)))
    if selfhelp:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":

    params = sys.argv[1:]

    if len(params) < 3:
        puaq(False)

    input_text = sys.stdin.read()
    pattern = params[0]
    replacement = params[1]
    mode = params[2]

    if mode not in valid_modes:
        print("%s is not a valid mode" % mode)
        sys.exit(1)

    streamfilter(input_text, pattern, replacement, mode)
