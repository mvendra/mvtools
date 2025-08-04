#!/usr/bin/env python3

import sys
import os
import shutil

import fsquery
import path_utils
import decrypt
import input_checked_passphrase
import terminal_colors

""" test_mass_decrypt
Tests if all files inside a given path, that match the given extension, have been encrypted with the same given passphrase (recursively).
A temporary path must also be provided - temporarily decrypted files will be stored there. This temporary folder is cleared after the operation
is complete, but it is not removed.
This is like a dry-run version of a would-be mass_decrypt operation/script. Intended for validating purposes.
"""

def print_report(v, r):

    errcode = 0
    if v:
        print("%sAll passed!%s" % (terminal_colors.TTY_GREEN, terminal_colors.get_standard_color()))
    else:
        print("%s\nThere were %s errors:%s" % (terminal_colors.TTY_RED, len(r), terminal_colors.get_standard_color()))
        errcode = 5

    for x in r:
        print(x)
    return errcode

def test_mass_decrypt(path_files, path_temp_base, extension, passphrase):

    path_temp_used = path_utils.concat_path(path_temp_base, path_utils.basename_filtered(__file__) + "_temp_DELETE_ME_NOW")
    path_utils.scratchfolder(path_temp_used)

    ext_list_aux = []
    ext_list_aux.append(extension)
    v, r = fsquery.makecontentlist(path_files, True, False, True, False, True, False, True, ext_list_aux)
    if not v:
        return False, [r]
    filelist = r
    report = []

    if len(filelist) == 0:
        print("WARNING: Nothing to test.")

    for f in filelist:
        if not decrypt.symmetric_decrypt(f, path_utils.concat_path(path_temp_used, path_utils.basename_filtered(f) + ".tmp"), passphrase)[0]:
            report.append(f + " FAILED")

    try:
        shutil.rmtree(path_temp_used)
    except:
        print("\nWARNING: Failed deleting %s! You should do it now manually." % path_temp_used)

    return (len(report) == 0), report

def puaq(selfhelp): # print usage and quit
    print("Usage: %s path_to_operate temporary_path files_extension passphrase_hash_file" % path_utils.basename_filtered(__file__))
    if selfhelp:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 5:
        puaq(False)

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

    v, r = test_mass_decrypt(path_files, path_temp_base, extension, passphrase)
    print("\nWill print the report...:")
    sys.exit(print_report(v, r))
