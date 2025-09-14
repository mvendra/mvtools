#!/usr/bin/env python

import sys
import os

from random import randrange

import path_utils
import maketimestamp
import sha256_wrapper # think twice before upgrading to sha512: some platforms have very short max path limitations

def randomfilenamegen():

    timestamp_now = maketimestamp.get_timestamp_now_compact()

    random_number = randrange(100000000)
    v, r = sha256_wrapper.hash_sha_256_app_content(str(random_number))
    if not v:
        return None
    hashed_random_number = r

    final_fn = "%s_%s.tmp" % (timestamp_now, hashed_random_number)
    return final_fn

if __name__ == "__main__":

    random_fn = randomfilenamegen()
    print(random_fn)
