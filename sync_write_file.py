#!/usr/bin/env python3

import sys
import os

import trylock

def sync_write_file(filename, contents):

    with open(filename, "a") as f:

        # tries to acquire a mutex lock on this file to prevent concurrent writes
        if not trylock.try_lock_file(f):
            return False

        f.truncate(0) # clear old contents prior to updating
        f.write(contents)
        f.flush()
        trylock.try_unlock_file(f)

    return True

if __name__ == "__main__":
    print("Hello from %s" % os.path.basename(__file__))
