#!/usr/bin/env python3

import sys
import os

import getpass

from subprocess import check_output
from subprocess import CalledProcessError
from subprocess import run, PIPE

def check_hash(passphrase, pass_hash_file):

    pp_hash = ""
    with open(pass_hash_file) as f:
        pp_hash = f.read()

    pp_hash_calc = ""

    p = run(['sha512sum'], stdout=PIPE, input=passphrase, encoding='ascii')
    pp_hash_calc = p.stdout[0:128]

    if (pp_hash_calc == pp_hash):
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
    print("Usage: %s passphrase_hash_file" % os.path.basename(__file__))
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
