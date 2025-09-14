#!/usr/bin/env python

import sys
import os

import path_utils

def convert_to_bytes(size_string):

    try:
        s_number = ""
        s_unit = ""
        multiplier = 1

        if len(size_string) < 3:
            return (True, int(size_string))

        s_number = size_string[0:len(size_string)-2]
        s_unit = size_string[len(size_string)-2:]
        s_unit = s_unit.lower()

        if s_unit == "kb":
            multiplier = 1024
        elif s_unit == "mb":
            multiplier = 1024*1024
        elif s_unit == "gb":
            multiplier = 1024*1024*1024
        elif s_unit == "tb":
            multiplier = 1024*1024*1024*1024
        else:
            s_number = size_string

        final_num = int(s_number) * multiplier
        return (True, final_num)
    except:
        return (False, None)

def puaq(selfhelp):
    print("Usage: %s size_string" % path_utils.basename_filtered(__file__))
    if selfhelp:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq(False)
    size_string = sys.argv[1]

    v, r = convert_to_bytes(size_string)
    if not v:
        print("Failed converting %s" % size_string)
        sys.exit(1)
    print(r)
