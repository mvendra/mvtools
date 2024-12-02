#!/usr/bin/env python3

import sys
import os

import path_utils
import iat_wrapper

def convert_to_iso(input_file, output_file):

    v, r = iat_wrapper.convert_to_iso(input_file, output_file)
    return v, r

def puaq():
    print("Usage: %s [input.bin | input.mdf] output.iso" % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 3:
        puaq()

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    v, r = convert_to_iso(input_file, output_file)
    if not v:
        print(r)
        sys.exit(1)

    print("Generated [%s] successfully" % output_file)
