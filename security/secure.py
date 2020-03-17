#!/usr/bin/env python3

import sys
import os
import stat

import getpass
from subprocess import call

import terminal_colors
import encrypt
import shred_wrapper
import input_checked_passphrase

def secure_file(target_file, pass_hash_file):

    # gets and checks the passphrase
    r_pp, passphrase = input_checked_passphrase.get_checked_passphrase(pass_hash_file)
    if not r_pp:
        print("%sHash doesn't check. Aborting...%s" % (terminal_colors.TTY_RED, terminal_colors.TTY_WHITE))
        return False

    target_file_out = target_file + ".enc"

    # creates the new encrypted file
    v, r = encrypt.symmetric_encrypt(target_file, target_file_out, passphrase)
    if not v:
        print("%sEncryption failed (%s). Aborting...%s" % (terminal_colors.TTY_RED, r, terminal_colors.TTY_WHITE))
        return False

    # shreds the original plain file
    v, r = shred_wrapper.shred_target(target_file)
    if not v:
        print("%sShred failed (%s). Aborting...%s" % (terminal_colors.TTY_RED, r, terminal_colors.TTY_WHITE))
        return False

    # changes the permission of the new file
    os.chmod(target_file_out, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)

    return True

def puaq():
    print("Usage: %s target_file pass_hash_file" % os.path.basename(__file__))
    sys.exit(1)

if __name__ == "__main__":

    target_file = ""

    if len(sys.argv) < 3:
        puaq()

    target_file = sys.argv[1]
    pass_hash_file = sys.argv[2]

    if not os.path.exists(target_file):
        print("Target file [%s] does not exist. Aborting." % target_file)
        sys.exit(1)

    if not os.path.exists(pass_hash_file):
        print("Pass hash file [%s] does not exist. Aborting." % pass_hash_file)
        sys.exit(2)

    if not secure_file(target_file, pass_hash_file):
        print("Failed attempting to secure [%s]." % target_file)
        sys.exit(3)
