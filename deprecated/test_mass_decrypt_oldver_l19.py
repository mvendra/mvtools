#!/usr/bin/env python

import sys
import os
import fsquery
import path_utils
import shutil
import getpass

from subprocess import check_output

import decrypt

""" test_mass_decrypt
Tests if all files inside a given path, that match the given extension, have been encrypted with the same given passphrase (recursively).
A temporary path must also be provided - temporarily decrypted files will be stored there. This temporary folder is cleared after the operation
is complete, but it is not removed.
This is like a dry-run version of a would-be mass_decrypt operation/script. Intended for validating purposes.
"""

def puaq(): # print usage and quit
    print("Usage: %s path_to_operate temporary_path files_extension [passphrase]" % os.path.basename(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 4:
        puaq()

    path_files = sys.argv[1]
    path_temp_base = sys.argv[2]
    extension = sys.argv[3]

    if not os.path.exists(path_files):
        print("%s does not exist. Aborting." % path_files)
        sys.exit(1)

    if not os.path.isdir(path_temp_base):
        print("%s does not exist or is not a directory. You have to create a directory manually - and get rid of it too, after the test is complete. This is by design. Aborting." % path_temp_base)
        sys.exit(2)
 
    if len(sys.argv) > 4:
        # optional passphrase also specified
        passphrase = sys.argv[4]
    else:
        # optional passphrase not specified. lets read it from console interactively
        passphrase = getpass.getpass("Type in...\n")

   
    path_temp_used = os.path.join(path_temp_base, os.path.basename(__file__) + "_temp_DELETE_ME_NOW")
    path_utils.scratchfolder(path_temp_used)

    ext_list_aux = []
    ext_list_aux.append(extension)
    filelist = fsquery.makecontentlist(path_files, True, True, False, True, False, ext_list_aux)

    report = []
    for f in filelist:
        if not decrypt.symmetric_decrypt(f, os.path.join(path_temp_used, os.path.basename(f) + ".tmp"), passphrase):
            report.append(f + " FAILED")

    print("\nWill print the report...:")
    for r in report:
        print(r)
    if len(report) == 0:
        print("All passed!")
    else:
        print("\nThere were %s errors." % len(report))

    try:
        shutil.rmtree(path_temp_used)
    except:
        print("\nWARNING: Failed deleting %s! You should do it now manually." % path_temp_used)
    
