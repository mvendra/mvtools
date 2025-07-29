#!/usr/bin/env python3

import sys
import os

import path_utils
import getcontents

def hexstring_to_hexdump(hexstring):

    result = ""

    hexstring = hexstring.replace("\n", " ")
    hexstring = hexstring.replace(" ", "")

    if (len(hexstring) % 2 != 0):
        print("Invalid hex string")
        return ""

    c = 0
    offs = 0
    result += "%04X   " % offs
    for i in range(0, len(hexstring), 2):
        if c == 16:
            result += "\n"
            offs += 16
            result += "%04X   " % offs
            c = 0

        result += hexstring[i]
        result += hexstring[i+1]
        result += " "
        c += 1
    result += "\n"

    return result

def make_output_filename(filename):
    r = filename.find(".")
    if (r == -1):
        return "%s_out" % filename
    f, e = filename.split(".")
    return "%s_out.%s" % (f, e)

def savecontents(filename, contents):
    with open(filename, "w") as f:
        f.write(contents)

def puaq(selfhelp):
    print("Usage: %s file_with_hexstring.txt" % path_utils.basename_filtered(__file__))
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
    contents = hexstring_to_hexdump(contents)
    savecontents(output_filename, contents)
