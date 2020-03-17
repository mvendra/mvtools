#!/usr/bin/env python3

import sys
import os

import getpass
from subprocess import call

def puaq():
    print("Usage: %s infile [outfile] [passphrase]" % os.path.basename(__file__))
    sys.exit(1)

def symmetric_encrypt(infile, outfile, passphrase):

    """
    symmetric_encrypt
    parameters are all mandatory here
    """

    if not os.path.exists(infile):
        print("%s does not exist. Aborting." % infile)
        sys.exit(1)

    if not os.path.isfile(infile):
        print("%s is not a file. Aborting." % infile)
        sys.exit(1)

    if outfile == "" or outfile is None:
        print("Invalid output filename. Aborting.")
        sys.exit(1)

    if os.path.exists(outfile):
        print("%s already exists. Aborting." % outfile)
        sys.exit(1)

    if passphrase == "" or passphrase is None:
        print("Invalid passphrase. Aborting.")
        sys.exit(1)

    call(["openssl", "des3", "-e", "-pbkdf2", "-in", infile, "-out", outfile, "-k", passphrase])

if __name__ == "__main__":

    infile = ""
    outfile = None
    passphrase = None

    if len(sys.argv) < 2:
        puaq()

    infile = sys.argv[1] # mandatory

    if len(sys.argv) > 2:
        outfile = sys.argv[2] # optional

    if outfile is None:
        outfile = "%s.enc" % infile

    if len(sys.argv) > 3:
        passphrase = sys.argv[3] # optional

    if passphrase is None:
        passphrase = getpass.getpass("Type in...\n")

    symmetric_encrypt(infile, outfile, passphrase)
