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

    # gets and checks the passphrase
    r_pp, passphrase = input_checked_passphrase.get_checked_passphrase(pass_hash_file)
    if not r_pp:
        print("Passphrase does not check")
        return False

    # reads config file
    v, r = backup_processor.read_config(config_file)
    if not v:
        print("Failed reading config file: [%s]" % config_file)
        return False

    path_folders = r[2]
    temp_path = r[4]
    extension = "enc"

    # avoid conflict with tmp folder used by actual backup creation
    if os.path.exists(temp_path):
        print("Temp path [%s] already exists. Aborting." % temp_path)
        return False

    # scratches the temp folder
    if not path_utils.scratchfolder(temp_path):
        print("Can't scratch the folder [%s]." % temp_path)
        return False

    v = backups_mass_check_delegate(extension, passphrase, path_folders, temp_path)
    shutil.rmtree(temp_path)
    return v

def backups_mass_check_delegate(extension, passphrase, path_folders, temp_path):

    return_value = True

    # test mass hash check
    for pf in path_folders:
        print("Mass hash checking [%s]..." % pf)
        v, r = test_mass_hash_check.test_mass_hash_check(pf, extension)
        return_value &= v
        test_mass_hash_check.print_report(v, r)

    # test mass decrypt
    for pf in path_folders:
        print("Mass test-decrypting [%s]..." % pf)
        v, r = test_mass_decrypt.test_mass_decrypt(pf, temp_path, extension, passphrase)
        return_value &= v
        test_mass_decrypt.print_report(v, r)

    return return_value

def puaq():
    print("Usage: %s config-file passhash-file" % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 3:
        puaq()

    cfg_file_path = sys.argv[1]
    ph_file = sys.argv[2]

    if not backups_mass_check(cfg_file_path, ph_file):
        sys.exit(1)
