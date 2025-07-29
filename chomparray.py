#!/usr/bin/env python3

import sys
import os

import path_utils

def chomparray(option, inputs):

    # sample usage:
    # chomparray.py r1 aaa bbb ccc -> yields "aaa bbb"
    # chomparray.py l1 aaa bbb ccc -> yields "bbb ccc"

    bucket=[]
    for args in inputs:
        bucket.append(args)

    d=option[0]
    m=int(option[1:])

    ret=None
    if d=="l": # left
        ret=bucket[m:]
    elif d=="r": # right
        ret=bucket[:len(bucket)-m]

    toline=""
    for p in ret:
        toline+=p+" "
    toline=toline[:len(toline)-1] # removes trailing blank space
    print(toline)

def puaq(selfhelp):
    print("Usage: %s {r1|l1} [string] ..." % path_utils.basename_filtered(__file__))
    if selfhelp:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq(False)

    option = sys.argv[1]
    inputs = sys.argv[2:]

    chomparray(option, inputs)
