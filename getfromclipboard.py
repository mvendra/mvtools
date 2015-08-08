#!/usr/bin/env python

import sys
import os
import subprocess

if __name__ == "__main__":

    contents = subprocess.check_output(["xclip", "-sel", "clip", "-o"])
    print(contents)

