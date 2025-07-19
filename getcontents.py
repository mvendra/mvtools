#!/usr/bin/env python3

import sys
import os

def getcontents(filename):
    if not os.path.exists(filename):
        return None
    contents = ""
    with open(filename) as f:
        contents = f.read()
    return contents
