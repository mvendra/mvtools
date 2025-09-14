#!/usr/bin/env python

import sys
import os

import path_utils
import fsquery
import mvtools_exception

def insert_pragma(path):

    exts = ["h"]
    v, r = fsquery.makecontentlist(path, True, False, True, False, False, False, True, exts)
    if not v:
        raise mvtools_exception.mvtools_exception(r)
    ret = r

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

def puaq(selfhelp):
    print("Usage: %s folder" % path_utils.basename_filtered(__file__))
    if selfhelp:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq(False)
    else:
        insert_pragma(sys.argv[1])
