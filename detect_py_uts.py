#!/usr/bin/env python3

import sys
import os

import path_utils
import fsquery

def puaq():
    print("Usage: %s target_path" % path_utils.basename_filtered(__file__))
    sys.exit(1)

def get_content(file):
    content = ""
    with open(file) as f:
        content = f.read()
    return content

def is_file_py_ut(path):

    content = get_content(path)
    if "unittest.TestCase" in content and "unittest.main()" in content:
        return True
    return False

def detect_py_uts(path):

    ret = []
    qr = fsquery.makecontentlist(path, True, False, True, False, False, False, True, "py")

    for f in qr:
        if is_file_py_ut(f):
            ret.append(f)

    return ret

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    path = sys.argv[1]
    r = detect_py_uts(path)
    for e in r:
        print(e)
