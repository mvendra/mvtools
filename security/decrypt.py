#!/usr/bin/env python3

import sys
import os

import path_utils

import getpass
from subprocess import call

def puaq():
    print("Usage: %s infile [outfile] [passphrase]" % os.path.basename(__file__))
    sys.exit(1)

def symmetric_decrypt(infile, outfile, passphrase):

    """
    symmetric_decrypt
    parameters are all mandatory here
    returns True on success, False on failures
    """

    if not os.path.isfile(infile):
        print("%s does not exist. Aborting." % infile)
        sys.exit(1)

    if outfile == "" or outfile == None:
        print("Invalid output filename. Aborting")
        sys.exit(1)

    if passphrase == "" or passphrase == None:
        print("Invalid passphrase. Aborting.")
        sys.exit(1)

    out = call(["openssl", "des3", "-d", "-pbkdf2", "-in", infile, "-out", outfile, "-k", passphrase])
    if out == 0:
        return True
    else:
        print("Openssl command failed.")
        return False

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
        outfile = path_utils.poplastextension(infile)

    if os.path.isfile(outfile) or os.path.isdir(outfile):
        print("%s already exists. Aborting." % outfile)
        sys.exit(1)

    if (passphrase == ""):
        passphrase = getpass.getpass("Type in...\n")

    if not symmetric_decrypt(infile, outfile, passphrase):
        print("Failed to decrypt - likely incorrect passphrase used")
        os.unlink(outfile)
