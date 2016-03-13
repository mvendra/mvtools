#!/usr/bin/env python

import sys
import os
import path_utils
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
    if not os.path.exists(encpassfile):
        print("%s does not exist. Aborting." % encpassfile)
        sys.exit(1)

    random_fn = check_output(["randomfilenamegen.sh"])
    passphrase = getpass.getpass("Type in...\n")

    if not decrypt.symmetric_decrypt(encpassfile, random_fn, passphrase):
        print("Failed decrypting file.")
        path_utils.deletefile_ignoreerrors(random_fn)
        sys.exit(1)

    try:
        call(["copypass.py", random_fn])
        path_utils.deletefile_ignoreerrors(random_fn)
    except:
        print("Unable to send password to clipboard.")
        path_utils.deletefile_ignoreerrors(random_fn)
        sys.exit(1)

