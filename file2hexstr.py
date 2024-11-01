#!/usr/bin/env python3

import sys
import os

import path_utils

def file2hexstr(input_file, output_file):

    if not os.path.exists(input_file):
        return False, "[%s] does not exist" % input_file

    if not os.path.isfile(input_file):
        return False, "[%s] is not a file" % input_file

    if os.path.exists(output_file):
        return False, "[%s] already exists" % output_file

    input_contents = ""
    output_contents = "\""

    with open(input_file, "rb") as f:
        input_contents = f.read()

    for b in input_contents:
        output_contents += format(b, '02x')

    output_contents += "\""

    with open(output_file, "w") as f:
        f.write(output_contents)

    return True, None

def puaq():
    print("Usage: %s source_file target_file" % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 3:
        puaq()

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    v, r = file2hexstr(input_file, output_file)
    if not v:
        print(r)
        sys.exit(1)
