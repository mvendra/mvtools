#!/usr/bin/env python

import sys
import os

import getpass
from subprocess import call

def puaq():
    print("Usage: %s infile [outfile] [passphrase]" % os.path.basename(__file__))
    sys.exit(1)

if __name__ == "__main__":

    infile = ""
    outfile = ""
    passphrase = ""

    if len(sys.argv) < 2:
        puaq()

    infile = sys.argv[1] # mandatory

    if len(sys.argv) > 2:
        outfile = sys.argv[2] # optional

    if len(sys.argv) > 3:
        passphrase = sys.argv[3] # optional
 
    if (outfile == ""):
        outfile = "%s.enc" % infile

    if os.path.isfile(outfile) or os.path.isdir(outfile):
        print("%s already exists. Aborting." % outfile)
        sys.exit(1)

    if (passphrase == ""):
        passphrase = getpass.getpass("Type in...\n")

    call(["openssl", "des3", "-e", "-salt", "-in", infile, "-out", outfile, "-k", passphrase])

