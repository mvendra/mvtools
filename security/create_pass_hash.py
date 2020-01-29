#!/usr/bin/env python3

import sys
import os
import stat

import getpass

import sha512_wrapper

def create_pass_hash(filename):

    if os.path.exists(hash_fn_full):
        print("[%s] already exists. Aborting." % hash_fn_full)
        return False

    # ask passphrase
    passphrase = getpass.getpass("Type in...\n")

    # generate hash
    v, r = sha512_wrapper.hash_sha_512_app_content(passphrase)
    if not v:
        return False

    # write out to file
    with open(filename, "w") as f:
        f.write(r)

    # set user-read-only permissions
    os.chmod(filename, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)

    return True

if __name__ == "__main__":

    filename_base = os.path.expanduser("~/")
    hash_filename = ".private_passphrase_hash"

    if len(sys.argv) == 2:
        filename_base = os.getcwd()
        hash_filename = sys.argv[1]

    hash_fn_full = os.path.join(filename_base, hash_filename)
    if not create_pass_hash(hash_fn_full):
        print("Failed creating pass hash file")
        sys.exit(1)
    else:
        print("Successfuly created hash file [%s]." % hash_fn_full)
