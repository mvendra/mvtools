#!/usr/bin/env python

import sys
import os

import fcntl

def try_lock_file(file_handle):

    try:
        fcntl.lockf(file_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        return False
    return True

def try_unlock_file(file_handle):

    try:
        fcntl.lockf(file_handle, fcntl.LOCK_UN)
    except IOError:
        return False
    return True
