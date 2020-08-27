#!/usr/bin/env python3

import sys
import os
import time
import random

import props

def retry(retry_params, func, p1):

    # retry_params is a map with retry parameters, valid uses are:
    # retry_params["retries_max"] = 0 ~ 100 
    # maximum number of retries. 0 means no retries at all. it's capped at 100.

    # retry_params["retry_sleep_random"] = 0 ~ 500 (ms)
    # maximum time to randomly sleep before retrying. if zero, the retry will take place instantaneous. otherwise,
    # a random amount between 0 and this number will be waited for before retrying. it's capped at 500ms.

    random.seed()

    retries_count = 0
    retries_max = props.setup_prop(5, 20, retry_params, "retries_max")
    retry_sleep_random = props.setup_prop(100, 500, retry_params, "retry_sleep_random")

    while retries_count < retries_max:
        retries_count += 1

        if func(p1):
            return True

        rnd_sleep = random.randrange(0, retry_sleep_random)
        time.sleep(rnd_sleep/1000)

    return False # all retries failed
