#!/usr/bin/env python3

import sys
import os

import getpass
import path_utils
import sha512_wrapper

def check_hash(passphrase, pass_hash_file):

    pp_hash = ""
    with open(pass_hash_file) as f:
        pp_hash = f.read()

    v, r = sha512_wrapper.hash_sha_512_app_content(passphrase)
    if not v:
        print("Failed generating hash.")
        sys.exit(1)

    if (r == pp_hash):
        return True
    else:
        return False

def get_checked_passphrase(passphrase_hash_file):

    # ask passphrase
    passphrase = getpass.getpass("Type in...\n")

    # check passphrase
    if check_hash(passphrase, passphrase_hash_file):
        return True, passphrase
    else:
        return False, None

def puaq():
    print("Usage: %s passphrase_hash_file" % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    passphrase_hash_file = sys.argv[1]

    if not os.path.exists(passphrase_hash_file):
        print("Passphrase hash file [%s] does not exist." % passphrase_hash_file)
        sys.exit(1)

    r, v = get_checked_passphrase(passphrase_hash_file)
    if (r):
        print("Passphrase checks")
    else:
        print("Passphrase does not check")
