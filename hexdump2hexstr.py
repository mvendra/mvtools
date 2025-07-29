#!/usr/bin/env python3

import sys
import os

import path_utils
import getcontents

def alphanumerichex_ar(ar, p):
    if p >= len(ar):
        return False
    if not ar[p].isalnum():
        return False
    try:
        u = int(ar[p], 16)
        return True
    except ValueError as vex:
        return False

def hexdump_to_hexstring(hexdump):

    result = ""

    i = 0
    while i < len(hexdump)-1:
        if alphanumerichex_ar(hexdump, i):
            si = i
            c = 0
            j = i+1
            while j < len(hexdump)+1:
                c += 1
                i += 1
                if not alphanumerichex_ar(hexdump, j):
                    if c == 2:
                        result += hexdump[si:si+2]
                    break
                else:
                    j += 1
        else:
            i += 1

    return result

def make_output_filename(filename):
    if filename is None:
        filename = "blank"
    return "%s_out.txt" % filename

def savecontents(filename, contents):
    with open(filename, "w") as f:
        f.write(contents)

def puaq(selfhelp):
    print("Usage: %s file_with_hexdump.txt" % path_utils.basename_filtered(__file__))
    if selfhelp:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq(False)

    input_filename = path_utils.basename_filtered(sys.argv[1])
    output_filename = ""
    if len(sys.argv) > 2:
        output_filename = sys.argv[2]
    else:
        output_filename = make_output_filename(input_filename)

    if not os.path.exists(input_filename):
        print("%s does not exist. Aborting." % input_filename)
        sys.exit(1)

    if os.path.exists(output_filename):
        print("%s already exists. Aborting." % output_filename)
        sys.exit(1)

    contents = getcontents.getcontents(input_filename)
    contents = hexdump_to_hexstring(contents)
    savecontents(output_filename, contents)
