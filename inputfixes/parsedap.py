#!/usr/bin/env python3

# Parse Device Accel Profile

import sys
import os

import re
import path_utils

def parsed_accel_profile(STR):

    m = re.search("Device Accel Profile ([0-9]+):", STR)
    if m == None:
        return ""

    m = re.search("[0-9]+", m.group(0))
    if m == None:
        return ""

    return m.group(0) 

def puaq():
    print("Usage: %s search-string" % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    STR=" ".join(sys.argv[1:])
    print(parsed_accel_profile(STR))
