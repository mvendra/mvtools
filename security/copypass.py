#!/usr/bin/env python

import sys
import os
import subprocess
import path_utils
import getpass

def puaq():
    print("Usage: %s password_file" % os.path.basename(__file__))
    sys.exit(1)

def getpasswordfromcontents(contents):

    ID_PATTERN_S="pw=["
    ID_PATTERN_E="]"

    of_s = contents.find(ID_PATTERN_S)

    if of_s == -1:
        return None

    of_s += len(ID_PATTERN_S)
    of_e = contents.find(ID_PATTERN_E, of_s)

    if of_e == -1:
        return None

    return contents[of_s:of_e]

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    passfile = sys.argv[1]
    if not os.path.exists(passfile):
        print("%s does not exist. Aborting." % passfile)
        sys.exit(1)

    contents=""
    with open(passfile) as f:
        contents=f.read()

    password = getpasswordfromcontents(contents)
    content_to_copy = password
    if password == None:
        opt = raw_input("Unable to find predefined text pattern. Press enter and I will copy entire file. This is your chance to abort.")
        content_to_copy = contents

    try:
        subprocess.call(["sendtoclipboard.py", content_to_copy])
    except:
        print("Unable to send password to clipboard.")
        sys.exit(1)

