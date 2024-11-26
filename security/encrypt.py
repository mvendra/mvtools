#!/usr/bin/env python3

import sys
import os

import openssl_wrapper
import getpass

import path_utils

def puaq():
    print("Usage: %s infile [outfile] [passphrase]" % path_utils.basename_filtered(__file__))
    sys.exit(1)

def symmetric_encrypt(infile, outfile, passphrase):

    v, r = openssl_wrapper.encrypt_des3_pbkdf2(infile, outfile, passphrase)
    return v, r

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
        print("Failed to encrypt: [%s]" % r)
        sys.exit(1)
