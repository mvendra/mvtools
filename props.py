#!/usr/bin/env python

import sys
import os

def max_of(val, themax):
    if val > themax:
        return themax
    return val

def get_from_map_if_present(themap, thekey):
    if themap is None:
        return False, None
    if not isinstance(themap, dict):
        return False, None
    if thekey in themap:
        return True, themap[thekey]
    return False, None

def setup_prop(default, themax, themap, thekey):
    v, r = get_from_map_if_present(themap, thekey)
    if v:
        return max_of(r, themax)
    return max_of(default, themax)
