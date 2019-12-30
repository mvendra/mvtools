#!/usr/bin/env python3

import sys
import os

from subprocess import CalledProcessError
from subprocess import run, PIPE

def puaq():
    print("Usage: %s archive-to-check [hash-file]" % os.path.basename(__file__))
    sys.exit(1)

def sha256sum_check(archive_file, hash_file):

    p = run(["sha256sum", archive_file], stdout=PIPE, encoding="ascii")
    archive_file_computed_hash = p.stdout

    hash_file_contents = ""
    with open(hash_file, "r") as f:
        hash_file_contents = f.read()

    # lets cleanup the output of sha256sum
    archive_file_computed_hash = archive_file_computed_hash[:64]
    hash_file_contents = hash_file_contents[:64]

    # and then compare
    if archive_file_computed_hash == hash_file_contents:
        return True
    else:
        return False

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    archive_file = sys.argv[1]
    hash_file = ""

    if len(sys.argv) > 2:
        hash_file = sys.argv[2]
    else:
        hash_file = archive_file + ".sha256"

    if not os.path.isfile(archive_file):
        print("%s does not exist. Aborting." % archive_file)
        sys.exit(1)

    if not os.path.isfile(hash_file):
        print("%s does not exist. Aborting." % hash_file)
        sys.exit(1)

    if sha256sum_check(archive_file, hash_file):
        print("Correct match")
    else:
        print("Check failed!")
        sys.exit(1)

