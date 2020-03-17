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
        return False, "%s does not exist." % infile

    if not os.path.isfile(infile):
        return False, "%s is not a file." % infile

    if outfile == "" or outfile is None:
        return False, "Invalid output filename."

    if os.path.exists(outfile):
        return False, "%s already exists." % outfile

    if passphrase == "" or passphrase is None:
        return False, "Invalid passphrase."

    out = call(["openssl", "des3", "-e", "-pbkdf2", "-in", infile, "-out", outfile, "-k", passphrase])
    if out != 0:
        return False, "Openssl command failed."

    return True, None

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

    v, r = symmetric_encrypt(infile, outfile, passphrase)
    if not v:
        print(r)
        sys.exit(1)
