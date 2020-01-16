#!/usr/bin/env python3

import sys
import os
import fsquery
import path_utils
import shutil

from subprocess import check_output

import decrypt
import input_checked_passphrase

""" test_mass_decrypt
Tests if all files inside a given path, that match the given extension, have been encrypted with the same given passphrase (recursively).
A temporary path must also be provided - temporarily decrypted files will be stored there. This temporary folder is cleared after the operation
is complete, but it is not removed.
This is like a dry-run version of a would-be mass_decrypt operation/script. Intended for validating purposes.
"""

def puaq(): # print usage and quit
    print("Usage: %s path_to_operate temporary_path files_extension passphrase_hash_file" % os.path.basename(__file__))
    sys.exit(1)


def print_report(report):
    for r in report:
        print(r)
    if len(report) == 0:
        print("All passed!")
    else:
        print("\nThere were %s errors." % len(report))

def test_mass_decrypt(path_files, path_temp_base, extension, passphrase):

    path_temp_used = os.path.join(path_temp_base, os.path.basename(__file__) + "_temp_DELETE_ME_NOW")
    path_utils.scratchfolder(path_temp_used)

    ext_list_aux = []
    ext_list_aux.append(extension)
    filelist = fsquery.makecontentlist(path_files, True, True, False, True, False, True, ext_list_aux)
    report = []

    if len(filelist) == 0:
        print("WARNING: Nothing to test.")

    for f in filelist:
        if not decrypt.symmetric_decrypt(f, os.path.join(path_temp_used, os.path.basename(f) + ".tmp"), passphrase):
            report.append(f + " FAILED")

    try:
        shutil.rmtree(path_temp_used)
    except:
        print("\nWARNING: Failed deleting %s! You should do it now manually." % path_temp_used)

    return True, report

if __name__ == "__main__":

    if len(sys.argv) < 5:
        puaq()

    path_files = sys.argv[1]
    path_temp_base = sys.argv[2]
    extension = sys.argv[3]
    passphrase_hash_file = sys.argv[4]

    if not os.path.exists(path_files):
        print("%s does not exist. Aborting." % path_files)
        sys.exit(1)

    if not os.path.isdir(path_temp_base):
        print("%s does not exist or is not a directory. You have to create a directory manually - and get rid of it too, after the test is complete. This is by design. Aborting." % path_temp_base)
        sys.exit(2)

    if not os.path.exists(passphrase_hash_file):
        print("%s does not exist. Aborting." % passphrase_hash_file)
        sys.exit(3)

    r_pp, passphrase = input_checked_passphrase.get_checked_passphrase(passphrase_hash_file)
    if not r_pp:
        print("Passphrase does not check")
        sys.exit(4)

    r, v = test_mass_decrypt(path_files, path_temp_base, extension, passphrase)
    if not r:
        sys.exit(1)
    else:
        print("\nWill print the report...:")
        print_report(v)
