#!/usr/bin/env python3

import fsquery

import sys
import os

def puaq():
    print("Usage: %s folder" % os.path.basename(__file__))
    sys.exit(1)

def insert_pragma(path):

    exts = ["h"]
    ret = fsquery.makecontentlist(path, True, True, False, False, False, True, exts)

    pragma_str = "\n#ifdef __GNUC__\n#pragma GCC system_header\n#endif\n"

    failed_bucket = [] #currently unused

    for r in ret:
        contents = pragma_str
        with open(r) as f:
            contents += f.read()
        with open(r, "w") as f:
            f.write(contents)

    if len(failed_bucket) > 0:
        print("There were failures!")
        for fb in failed_bucket:
            print("%s failed." % fb)
    else:
        print("All done - no errors detected")

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()
    else:
        insert_pragma(sys.argv[1])
