#!/usr/bin/env python3

import sys
import os
import fsquery

import hash_check

""" test_mass_hash_check
Tests if all files inside a given path, that match the given extension, have an accompanying valid hash file (filename + ".sha256")
"""

def puaq(): # print usage and quit
    print("Usage: %s path_to_operate files_extension" % os.path.basename(__file__))
    sys.exit(1)

def test_mass_hash_check(path_files, extension):

    if not os.path.exists(path_files):
        print("%s does not exist. Aborting." % path_files)
        return False, None

    ext_list_aux = []
    ext_list_aux.append(extension)
    filelist = fsquery.makecontentlist(path_files, True, True, False, True, False, ext_list_aux)
    report = []

    if len(filelist) == 0:
        print("WARNING: Nothing to test.")

    for f in filelist:
        hash_file = f + ".sha256"
        if not os.path.exists(hash_file):
            report.append(f + " has no corresponding hash file.")
        elif not hash_check.sha256sum_check(f, hash_file):
            report.append(f + " check FAILED.")

    return True, report

def print_report(report):
    for l in report:
        print(l)
    if len(report) == 0:
        print("All passed!")
    else:
        print("\nThere were %s errors." % len(report))

if __name__ == "__main__":

    if len(sys.argv) < 3:
        puaq()

    path_files = sys.argv[1]
    extension = sys.argv[2]

    r, v = test_mass_hash_check(path_files, extension)
    if not r:
        sys.exit(1)
    else:
        print("\nWill print the report...:")
        print_report(v)
