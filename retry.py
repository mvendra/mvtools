#!/usr/bin/env python3

import sys
import os
import time
import random

import props

DEFAULT_RETRY=3
MAX_RETRY=800000

DEFAULT_SLEEP=200
MAX_SLEEP=2000

def retry(retry_params, func, p1):

    # retry_params is a map with retry parameters, valid uses are:
    # retry_params["retries_max"] = 0 ~ 100 
    # maximum number of retries. 0 means no retries at all. it's capped at 800000.

    # retry_params["retry_sleep_random"] = 0 ~ 500 (ms)
    # maximum time to randomly sleep before retrying. if zero, the retry will take place instantaneous. otherwise,
    # a random amount between 0 and this number will be waited for before retrying. it's capped at 2000ms (2 seconds).

    random.seed()

    retries_count = 0
    retries_max = props.setup_prop(DEFAULT_RETRY, MAX_RETRY, retry_params, "retries_max")
    retry_sleep_random = props.setup_prop(DEFAULT_SLEEP, MAX_SLEEP, retry_params, "retry_sleep_random")

    while retries_count < retries_max:
        retries_count += 1

        if func(p1):
            return True

        rnd_sleep = random.randrange(0, retry_sleep_random)
        time.sleep(rnd_sleep/1000)

    return False # all retries failed
