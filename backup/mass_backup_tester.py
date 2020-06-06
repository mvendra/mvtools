#!/usr/bin/env python3

import sys
import os
import shutil

import path_utils
import input_checked_passphrase

import test_mass_hash_check
import test_mass_decrypt

import backup_processor

def backups_mass_check(config_file, pass_hash_file):

    r, v = backup_processor.read_config(config_file)
    if not r:
        print("Failed reading config file: [%s]" % config_file)
        return False

    path_folders = v[2]
    temp_path = v[4]
    extension = "enc"

    # test mass hash check
    for pf in path_folders:
        print("Mass hash checking [%s]..." % pf)
        r, v = test_mass_hash_check.test_mass_hash_check(pf, extension)
        if not r:
            return False
        test_mass_hash_check.print_report(v)

    # gets and checks the passphrase
    r_pp, passphrase = input_checked_passphrase.get_checked_passphrase(pass_hash_file)
    if not r_pp:
        print("Passphrase does not check")
        return False

    # avoid conflict with tmp folder used by actual backup creation
    if os.path.exists(temp_path):
        print("Temp path [%s] already exists. Aborting." % temp_path)
        return False

    # scratches the temp folder
    if not path_utils.scratchfolder(temp_path):
        print("Can't scratch the folder [%s]." % temp_path)
        return False

    # test mass decrypt
    for pf in path_folders:
        print("Mass test-decrypting [%s]..." % pf)
        r, v = test_mass_decrypt.test_mass_decrypt(pf, temp_path, extension, passphrase)
        if not r:
            return False
        test_mass_decrypt.print_report(v)

    shutil.rmtree(temp_path)

    return True

if __name__ == "__main__":

    if len(sys.argv) < 3:
        puaq()

    cfg_file_path = sys.argv[1]
    ph_file = sys.argv[2]

    if not backups_mass_check(cfg_file_path, ph_file):
        sys.exit(1)
