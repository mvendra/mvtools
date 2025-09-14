#!/usr/bin/env python

import sys
import os

import path_utils
import generic_run

def encrypt_des3_pbkdf2(infile, outfile, passphrase):

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

    full_cmd = ["openssl", "des3", "-e", "-pbkdf2", "-in", infile, "-out", outfile, "-k", passphrase]
    v, r = generic_run.run_cmd_simple(full_cmd)
    if not v:
        return False, "Failed running openssl encrypt-des3-pbkdf2 command: [%s]" % r

    return True, None

def decrypt_des3_pbkdf2(infile, outfile, passphrase):

    if not os.path.exists(infile):
        return False, "%s does not exist." % infile

    if outfile == "" or outfile is None:
        return False, "Invalid output filename."

    if os.path.exists(outfile):
        return False, "%s already exists." % outfile

    if passphrase == "" or passphrase is None:
        return False, "Invalid passphrase."

    full_cmd = ["openssl", "des3", "-d", "-pbkdf2", "-in", infile, "-out", outfile, "-k", passphrase]
    v, r = generic_run.run_cmd_simple(full_cmd)
    if not v:
        return False, "Failed running openssl decrypt-des3-pbkdf2 command: [%s]" % r

    return True, None

def puaq(selfhelp):
    print("Hello from %s" % path_utils.basename_filtered(__file__))
    if selfhelp:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    puaq(False)
