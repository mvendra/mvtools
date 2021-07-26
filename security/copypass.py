#!/usr/bin/env python3

import sys
import os
import subprocess
import getpass

import sendtoclipboard
import path_utils

def puaq():
    print("Usage: %s password_file" % path_utils.basename_filtered(__file__))
    sys.exit(1)

def getpasswordfromcontents(contents):

    local_contents = contents

    ID_PATTERN_S="pw=["
    ID_PATTERN_E="]"

    of_s = local_contents.find(ID_PATTERN_S)

    if of_s == -1:
        return None

    local_contents = local_contents[of_s+len(ID_PATTERN_S):]
    local_contents = local_contents.split("\n")[0].strip()

    of_e = local_contents.rfind(ID_PATTERN_E)

    if of_e == -1:
        return None

    return local_contents[:of_e]

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
        opt = input("Unable to find predefined text pattern. Press enter and I will copy entire file. This is your chance to abort.")
        content_to_copy = contents

    try:
        sendtoclipboard.sendtoclipboard(content_to_copy)
        print("Ok, you're up...")
        subprocess.call(["sleep", "5"])
        sendtoclipboard.sendtoclipboard("clear")
        print("Expired.")
    except:
        print("Unable to send password to clipboard.")
        sys.exit(1)

