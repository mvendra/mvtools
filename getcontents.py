#!/usr/bin/env python3

import sys
import os

import mvtools_exception

def getcontents(filename):
    if not os.path.exists(filename):
        raise mvtools_exception.mvtools_exception("filename [%s] does not exist" % filename)
    contents = ""
    with open(filename) as f:
        contents = f.read()
    return contents
