#!/usr/bin/env python3

import sys
import os

# example of custom path navigator's interface for collect_patches.py

def visit_path(path):
    ret = []
    ret.append("/custom_stuff/%s" % path)
    return ret

if __name__ == "__main__":
    pass
