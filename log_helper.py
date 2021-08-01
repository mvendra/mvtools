#!/usr/bin/env python3

import sys
import os

import path_utils

def add_to_warnings(warnings, latest_msg):
    if latest_msg is None:
        return warnings
    if warnings is None:
        return latest_msg
    return "%s%s%s" % (warnings, os.linesep, latest_msg)
