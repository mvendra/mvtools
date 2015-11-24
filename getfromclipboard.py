#!/usr/bin/env python

import sys
import os
from subprocess import check_output
from subprocess import CalledProcessError

def getfromclipboards():
    try:
        contents = check_output(["xclip", "-sel", "clip", "-o"])
    except CalledProcessError as cpe:
        print("Failed to call xclip. Make sure it is installed.")
        exit(1)
    return contents

if __name__ == "__main__":
    print(getfromclipboards())

