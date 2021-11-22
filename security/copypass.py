#!/usr/bin/env python3

import sys
import os
import time
import getpass

import path_utils
import sendtoclipboard

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

def copypass(passfile):

    if not os.path.exists(passfile):
        print("%s does not exist. Aborting." % passfile)
        return False

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
        time.sleep(5)
        sendtoclipboard.sendtoclipboard("clear")
        print("Expired.")
    except:
        print("Unable to send password to clipboard.")
        return False

    return True

def puaq():
    print("Usage: %s password_file" % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    if not copypass(sys.argv[1]):
        sys.exit(1)
