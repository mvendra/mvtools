#!/usr/bin/env python3

import sys
import os

def puaq():
    print("Usage: %s file" % os.path.basename(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    inputfile = sys.argv[1]
    if not os.path.exists(inputfile):
        print("%s does not exist. Aborting." % inputfile)
        sys.exit(1)

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
