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

    random_fn = subprocess.check_output(["randomfilenamegen.sh"])
    passphrase = getpass.getpass("Type in...\n")
    contents=""

    try:
        subprocess.check_output(["decrypt.sh", passfile, random_fn, passphrase])
        with open(random_fn) as f:
            contents=f.read()
    except:
        print("Failed decrypting file.")
        path_utils.deletefile_ignoreerrors(random_fn)
        sys.exit(1)

    password = getpasswordfromcontents(contents)
    if password == None:
        print("Unable to extract password from file - cant find the password text pattern.")
        path_utils.deletefile_ignoreerrors(random_fn)
        sys.exit(1)

    try:
        subprocess.call(["inline_echo_xclip_wrapper.sh", password])
        path_utils.deletefile_ignoreerrors(random_fn)
    except:
        print("Unable to send password to clipboard.")
        path_utils.deletefile_ignoreerrors(random_fn)
        sys.exit(1)

