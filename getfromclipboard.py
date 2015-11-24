#!/usr/bin/env python

import sys
import os
from subprocess import check_output

def getfromclipboards():
    try:
        contents = check_output(["xclip", "-sel", "clip", "-o"])
    except OSError as oe:
        print("Failed to call xclip. Make sure it is installed.")
        exit(1)
    return contents

if __name__ == "__main__":
    print(getfromclipboards())

