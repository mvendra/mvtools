#!/usr/bin/env python

import sys
import os
import subprocess

def getfromclipboards():
    contents = subprocess.check_output(["xclip", "-sel", "clip", "-o"])
    return contents

if __name__ == "__main__":
    print(getfromclipboards())

