#!/usr/bin/env python3

import sys
import os

import generic_run
import create_and_write_file
import hash_algos

def puaq():
    print("Usage: %s [--hash] file_or_folder" % os.path.basename(__file__))
    sys.exit(1)

def pakgen(files):

    DO_HASH=False
    TARGET=""

    if files[0] == "--hash":
        DO_HASH=True
        TARGET=files[1]
    else:
        TARGET=files[0]

    if not os.path.exists(TARGET):
        print("Does %s even exist?" % TARGET)
        sys.exit(1)

    if TARGET[len(TARGET)-1] == os.sep:
        TARGET=TARGET[0:len(TARGET)-1]

    FILENAME = os.path.basename(TARGET)
    TARGET = TARGET.replace(" ", "\\ ")
    FILENAME = FILENAME.replace(" ", "\\ ")
    FILENAME_TAR = "%s.tar" % FILENAME
    FILENAME_TAR_BZ2 = "%s.bz2" % FILENAME_TAR
    HASH_FILENAME = "%s.sha256"  % FILENAME_TAR_BZ2

    generic_run.run_cmd("tar -cf %s %s" % (FILENAME_TAR, TARGET))
    generic_run.run_cmd("bzip2 %s" % FILENAME_TAR)

    if DO_HASH:
        v, r = hash_algos.hash_sha_256_app_file(FILENAME_TAR_BZ2)
        if v:
            create_and_write_file.create_file_contents(HASH_FILENAME, r)
        else:
            print("Failed generating hash for %s" % FILENAME_TAR_BZ2)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()
    pakgen(sys.argv[1:])
