#!/usr/bin/env python3

import sys
import os
import stat
import shred_wrapper
import getpass

from subprocess import check_output
from subprocess import call

import decrypt

def puaq():
    print("Usage: %s enc_password_file" % os.path.basename(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    encpassfile = sys.argv[1]

    # tests permissions of encpassfile
    p = os.stat(encpassfile)
    if p.st_mode & stat.S_IRWXG:
        print("WARNING: This file has group permissions!")

    if p.st_mode & stat.S_IRWXO:
        print("WARNING: This file has permissions for others!")

    if not os.path.exists(encpassfile):
        print("%s does not exist. Aborting." % encpassfile)
        sys.exit(1)

    random_fn = check_output(["randomfilenamegen.sh"])
    passphrase = getpass.getpass("Type in...\n")

    if not decrypt.symmetric_decrypt(encpassfile, random_fn, passphrase):
        print("Failed decrypting file.")
        shred_wrapper.shred_target(random_fn)
        sys.exit(1)

    try:
        call(["copypass.py", random_fn])
        shred_wrapper.shred_target(random_fn)
    except:
        print("Unable to send password to clipboard.")
        shred_wrapper.shred_target(random_fn)
        sys.exit(1)

