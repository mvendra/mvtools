#!/usr/bin/env python3

import sys
import os
import stat
import getpass

import mvtools_envvars
import path_utils
import decrypt
import copypass
import shred_wrapper
import randomfilenamegen

def puaq():
    print("Usage: %s enc_password_file" % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    encpassfile = sys.argv[1]

    if not os.path.exists(encpassfile):
        print("[%s] does not exist. Aborting." % encpassfile)
        sys.exit(1)

    # tests permissions of encpassfile
    p = os.stat(encpassfile)
    if p.st_mode & stat.S_IRWXG:
        print("WARNING: This file has group permissions!")

    if p.st_mode & stat.S_IRWXO:
        print("WARNING: This file has permissions for others!")

    if not os.path.exists(encpassfile):
        print("%s does not exist. Aborting." % encpassfile)
        sys.exit(1)

    v, r = mvtools_envvars.mvtools_envvar_read_temp_path()
    if not v:
        print("Unable to retrieve mvtool's temp path: [%s]" % r)
        sys.exit(1)
    temp_base_path = r

    random_fn = path_utils.concat_path(temp_base_path, randomfilenamegen.randomfilenamegen())
    if os.path.exists(random_fn):
        print("Random file name [%s] already exists. Aborting." % random_fn)
        sys.exit(1)
    passphrase = getpass.getpass("Type in...\n")

    v, r = decrypt.symmetric_decrypt(encpassfile, random_fn, passphrase)
    if not v:
        print("Failed decrypting file: [%s]." % r)
        shred_wrapper.shred_target(random_fn)
        sys.exit(1)

    try:
        copypass.copypass(random_fn)
        shred_wrapper.shred_target(random_fn)
    except:
        print("Unable to send password to clipboard.")
        shred_wrapper.shred_target(random_fn)
        sys.exit(1)
