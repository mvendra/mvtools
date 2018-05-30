#!/usr/bin/env python3

import sys
import os

def alphanumeric_ar(ar, p):
    if p >= len(ar):
        return False
    return ar[p].isalnum()

def hexdump_to_hexstring(hexdump):

    result = ""

    i = 0
    while i < len(hexdump)-1:
        if alphanumeric_ar(hexdump, i):
            si = i
            c = 0
            j = i+1
            while j < len(hexdump)+1:
                c += 1
                i += 1
                if not alphanumeric_ar(hexdump, j):
                    if c == 2:
                        result += hexdump[si:si+2]
                    break
                else:
                    j += 1
        else:
            i += 1

    return result

def puaq():
    print("Usage: %s file_with_hexdump.txt" % os.path.basename(__file__))
    sys.exit(1)

def make_output_filename(filename):
    r = filename.find(".")
    if (r == -1):
        return "%s_out" % filename
    f, e = filename.split(".")
    return "%s_out.%s" % (f, e)

def getcontents(filename):
    cnt = ""
    with open(filename) as f:
        cnt = f.read()
    return cnt

def savecontents(filename, contents):
    with open(filename, "w") as f:
        f.write(contents)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    input_filename = os.path.basename(sys.argv[1])
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

    contents = getcontents(input_filename)
    contents = hexdump_to_hexstring(contents)
    savecontents(output_filename, contents)
