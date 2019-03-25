#!/usr/bin/env python3

import sys
import os

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
    FILENAME = FILENAME.replace(" ", "\\ ")
    FILENAME += ".tar"
    TARGET = TARGET.replace(" ", "\\ ")

    os.system("tar -cf %s %s" % (FILENAME, TARGET))
    os.system("bzip2 %s" % FILENAME)
    if DO_HASH:
        os.system("sha256sum %s.bz2 > %s.bz2.sha256sum" % (FILENAME, FILENAME))

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()
    pakgen(sys.argv[1:])
