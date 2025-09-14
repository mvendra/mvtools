#!/usr/bin/env python

import sys
import os

import path_utils

def puaq():
    print("Usage: %s file" % path_utils.basename_filtered(__file__))
    sys.exit(1)

def to_urho_mdl(inputfile):

    if not os.path.exists(inputfile):
        print("%s does not exist. Aborting." % inputfile)
        return False

    fr = inputfile.rfind(".")
    ifnameonly = ""
    if (fr > 0):
        ifnameonly = inputfile[:fr]
    else:
        ifnameonly = inputfile

    outputfile = "%s.mdl" % ifnameonly
    if os.path.exists(outputfile):
        print("%s already exists. Aborting." % outputfile)
        sys.exit(1)

    fullcmd = "AssetImporter model %s %s" % (inputfile, outputfile)

    os.system(fullcmd)

    return True

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    inputfile = sys.argv[1]
    to_urho_mdl(inputfile)
