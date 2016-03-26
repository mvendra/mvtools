#!/usr/bin/env python

import sys
import os
import fsquery

import hashcheck

""" test_mass_hash_check
Tests if all files inside a given path, that match the given extension, have an accompanying valid hash file (filename + ".sha256")
"""

def puaq(): # print usage and quit
    print("Usage: %s path_to_operate files_extension" % os.path.basename(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 3:
        puaq()

    path_files = sys.argv[1]
    extension = sys.argv[2]

    if not os.path.exists(path_files):
        print("%s does not exist. Aborting." % path_files)
        sys.exit(1)

    ext_list_aux = []
    ext_list_aux.append(extension)
    filelist = fsquery.makecontentlist(path_files, True, True, False, True, False, ext_list_aux)

    report = []
    for f in filelist:
        hash_file = f + ".sha256"
        if not os.path.exists(hash_file):
            report.append(f + " has no corresponding hash file.")
        elif not hashcheck.sha256sum_check(f, hash_file):
            report.append(f + " check FAILED.")

    print("\nWill print the report...:")
    for r in report:
        print(r)
    if len(report) == 0:
        print("All passed!")
    else:
        print("\nThere were %s errors." % len(report))

