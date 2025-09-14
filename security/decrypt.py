#!/usr/bin/env python

import sys
import os

import openssl_wrapper
import getpass

import path_utils

def symmetric_decrypt(infile, outfile, passphrase):

    v, r = openssl_wrapper.decrypt_des3_pbkdf2(infile, outfile, passphrase)
    return v, r

def puaq(selfhelp):
    print("Usage: %s infile [outfile] [passphrase]" % path_utils.basename_filtered(__file__))
    if selfhelp:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":

    infile = ""
    outfile = None
    passphrase = None

    if len(sys.argv) < 2:
        puaq(False)

    infile = sys.argv[1] # mandatory

    if len(sys.argv) > 2:
        outfile = sys.argv[2] # optional

    if outfile is None:
        outfile = path_utils.poplastextension(infile)

    if len(sys.argv) > 3:
        passphrase = sys.argv[3] # optional

    if passphrase is None:
        passphrase = getpass.getpass("Type in...\n")

    v, r = symmetric_decrypt(infile, outfile, passphrase)
    if not v:
        print("Failed to decrypt: [%s]" % r)
        os.unlink(outfile)
        sys.exit(1)
