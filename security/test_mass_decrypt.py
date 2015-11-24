#!/usr/bin/env python

import sys
import os
import fsquery
import path_utils
import shutil
import getpass

from subprocess import check_output

""" test_mass_decrypt
Tests if all files inside a given path, that match the given extension, have been encrypted with the same given passphrase (recursively).
A temporary path must also be provided - temporarily decrypted files will be stored there, and then this folder will be deleted.
This is like a dry-run version of a would-be mass_decrypt operation/script. Intended for validating purposes.
"""

def puaq(): # print usage and quit
    print("Usage: %s path_to_operate temporary_path files_extension [passphrase]" % os.path.basename(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 4:
        puaq()

    path_files = sys.argv[1]
    path_temp = sys.argv[2]
    extension = sys.argv[3]

    if len(sys.argv) > 4:
        # optional passphrase also specified
        passphrase = sys.argv[4]
    else:
        # optional passphrase not specified. lets read it from console interactively
        passphrase = getpass.getpass("Type in...\n")

    if not os.path.exists(path_files):
        print("%s does not exist. Aborting." % path_files)
        sys.exit(1)

    path_temp = os.path.join(path_temp, os.path.basename(__file__) + "_temp_DELETE_ME_NOW")
    path_utils.scratchfolder(path_temp)

    ext_list_aux = []
    ext_list_aux.append(extension)
    filelist = fsquery.makecontentlist(path_files, True, True, False, True, False, ext_list_aux)

    report = []
    for f in filelist:
        try:
            check_output(["decrypt.sh", f, os.path.join(path_temp, os.path.basename(f) + ".tmp"), passphrase])
        except:
            report.append(f + " FAILED")

    print("\nWill print the report...:")
    for r in report:
        print(r)
    if len(report) == 0:
        print("All passed!")
    else:
        print("\nThere were %s errors." % len(report))

    try:
        shutil.rmtree(path_temp)
    except:
        print("\nWARNING: Failed deleting %s! You should do it now manually." % path_temp)
    
